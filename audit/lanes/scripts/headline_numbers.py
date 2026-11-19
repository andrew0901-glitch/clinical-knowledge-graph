"""Every headline number of the medRxiv preprint, computed directly from the 107 v0.2.1 release files.

 * node / edge totals: an independent row count over the 107 files (not the manifest's claim)
 * identity-only Articles: Article nodes with lunasai_layer = 'ctgov_identity_only'
 * trials with results / results Articles / results Articles cited by a guideline or systematic review:
   native VALIDATED_BY links (the RESULT role); citing Article's publication types include Guideline,
   Practice Guideline or Systematic Review; CITES self-links removed (build.py); with and without the
   identity-only stubs, exactly as the exact SQL in release_audit/results/strict_chains_queries.json ('v02')
 * English MedlinePlus topics reaching a guideline/review and a condition trial through the same matched
   MeSH descriptor under full downward expansion: read from lane 2's table (lane2_topic_table_english.csv)

Each value is compared with the number printed in the preprint; the script exits non-zero on any mismatch.

python audit/lanes/scripts/headline_numbers.py     (after build.py and lane2_medlineplus_english.py)
"""
import csv, sys

from lane_common import *

PAPER = {  # value as printed in the preprint
    'nodes': 12067108, 'edges': 105758066, 'identity_only_articles': 578177,
    'trials_with_results_without_stubs': 22793, 'results_articles_cited_by_guideline_or_sr': 23460,
    'english_topics': 1017, 'english_topics_both_same_descriptor_full': 743,
}


def count_rows(files):
    c = duckdb.connect()
    c.execute("SET threads=8; SET memory_limit='20GB'; SET preserve_insertion_order=false")
    sql = "SELECT count(*) FROM read_json(?, format='newline_delimited', columns={'id': 'VARCHAR'})"
    return c.execute(sql, [files]).fetchone()[0], sql


def main():
    m = json.loads(MANIFEST.read_text())
    out, checks = {}, []

    nodes, nsql = count_rows([str(INPUT / e['path']) for e in m['nodes']])
    edges, esql = count_rows([str(INPUT / e['path']) for e in m['edges']])
    out['totals'] = dict(nodes=nodes, edges=edges, sql_nodes=nsql, sql_edges=esql, files_nodes=len(m['nodes']),
                         files_edges=len(m['edges']), manifest_totals=m['totals'])
    checks += [('nodes', nodes, PAPER['nodes']), ('edges', edges, PAPER['edges'])]

    c = connect(read_only=True)
    r = Registry(c, 'headline_numbers')
    r.results['totals'] = [out['totals']]
    r.queries['totals'] = dict(sql=[nsql, esql], parameters='<node files>, <edge files>',
                               note='independent row count over the manifest-listed node and edge files')
    stubs = r.run('identity_only_articles', f"""
        SELECT count(*) AS articles, count(*) FILTER (WHERE stub) AS identity_only,
               count(*) FILTER (WHERE NOT stub) AS without_stubs FROM article""",
                  "Article nodes; identity-only = lunasai_layer 'ctgov_identity_only' (build.py column stub)")[0]
    checks.append(('identity_only_articles', stubs['identity_only'], PAPER['identity_only_articles']))

    rows = r.run('trial_results_chain', """
        WITH links AS (SELECT subject AS article, object AS trial FROM e WHERE type = 'VALIDATED_BY'),
        hit AS (SELECT DISTINCT ci.cited AS article, p.population
                FROM cites ci JOIN article g ON g.id = ci.citer CROSS JOIN populations p
                WHERE list_has_any(g.pub_types, ['Guideline', 'Practice Guideline', 'Systematic Review'])
                  AND (NOT p.exclude_stubs OR NOT g.stub))
        SELECT p.population,
               (SELECT count(*) FROM nodes WHERE label = 'ClinicalTrial') AS trials,
               count(DISTINCT l.trial) AS trials_with_results,
               count(DISTINCT l.article) AS result_articles,
               count(DISTINCT l.article) FILTER (WHERE h.article IS NOT NULL) AS result_articles_cited_by_guideline_or_sr,
               count(DISTINCT l.trial) FILTER (WHERE h.article IS NOT NULL) AS trials_with_results_cited_by_guideline_or_sr
        FROM links l JOIN article a ON a.id = l.article CROSS JOIN populations p
        LEFT JOIN hit h ON h.article = l.article AND h.population = p.population
        WHERE NOT p.exclude_stubs OR NOT a.stub
        GROUP BY p.population ORDER BY p.population DESC""",
                 "Native VALIDATED_BY (RESULT role) Article->ClinicalTrial links; guideline/SR citers, CITES self-links "
                 "removed; stubs removed as results Articles and as citers in the without_stubs population.",
                 csv='headline_trial_results_chain.csv')
    by = {x['population']: x for x in rows}
    checks += [('trials_with_results_without_stubs', by['without_stubs']['trials_with_results'],
                PAPER['trials_with_results_without_stubs']),
               ('results_articles_cited_by_guideline_or_sr (with stubs)',
                by['with_stubs']['result_articles_cited_by_guideline_or_sr'], PAPER['results_articles_cited_by_guideline_or_sr']),
               ('results_articles_cited_by_guideline_or_sr (without stubs)',
                by['without_stubs']['result_articles_cited_by_guideline_or_sr'], PAPER['results_articles_cited_by_guideline_or_sr'])]

    with open(T / 'lane2_topic_table_english.csv') as fh:
        eng = list(csv.DictReader(fh))
    full = [x for x in eng if x['mode'] == 'full' and x['topic_set'] == 'english']
    assert {x['population'] for x in full} == {'with_stubs', 'without_stubs'}
    assert len({(x['topics'], x['reaching_both_same_descriptor']) for x in full}) == 1   # identical with / without stubs
    full = full[0]
    r.results['medlineplus_english_full_expansion'] = [full]
    r.queries['medlineplus_english_full_expansion'] = dict(
        sql=None, parameters=[], note="rows mode='full', topic_set='english' of tables/lane2_topic_table_english.csv "
        "(SQL: lane2_medlineplus_queries.json); identical with and without stubs")
    checks += [('english_topics', int(full['topics']), PAPER['english_topics']),
               ('english_topics_both_same_descriptor_full', int(full['reaching_both_same_descriptor']),
                PAPER['english_topics_both_same_descriptor_full'])]

    res = [dict(item=k, computed=a, paper=b, match=a == b) for k, a, b in checks]
    r.results['paper_check'] = res
    r.queries['paper_check'] = dict(sql=None, parameters=[], note='computed value vs the number printed in the preprint')
    r.results['code_commit'] = commit()
    r.save()
    with open(T / 'headline_numbers.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['item', 'computed', 'paper', 'match'])
        w.writeheader()
        w.writerows(res)
    for x in res:
        print(('OK  ' if x['match'] else 'FAIL'), x['item'], x['computed'], 'paper', x['paper'])
    sys.exit(0 if all(x['match'] for x in res) else 1)


if __name__ == '__main__':
    main()
