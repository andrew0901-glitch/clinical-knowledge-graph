"""Lane 5: final paper numbers from the v0.2.1 files.

 A. Major-topic evidence maps (D001943, D000544, D006333; tree-number full expansion) with an independent
    NOT-EXISTS check that cited + not cited = primary studies.
 B. Trial-landscape results Articles, recomputed from the release files (not the tool cache): rows vs
    distinct Articles, with/without stubs, and distinct Articles cited by a guideline or systematic review
    under the tool's own citing rule (Guideline / Practice Guideline / Systematic Review; self-links
    included as the tool does) and with self-links removed.
 C. Every property key on ClinicalTrial nodes with its fill rate, streamed from the 54 manifest node shards.

python lane5_paper_numbers.py   (after build.py; needs the same 107 verified files)
"""
import csv, gzip
from collections import Counter
from multiprocessing import Pool

from lane_common import *
from lane3_evidence_maps import DESIGN_SQL, GUIDELINE, SRMA, RCT, OTHER_TRIAL, OBSERVATIONAL

CONDITIONS = ['D001943', 'D000544', 'D006333']
TOOL_GSR = ['Guideline', 'Practice Guideline', 'Systematic Review']   # trial_landscape.py is_guideline OR is_systematic_review


def trial_props(path):
    present, filled, n = Counter(), Counter(), 0
    with gzip.open(path, 'rt') as fh:
        for line in fh:
            if '"ClinicalTrial"' not in line:
                continue
            r = json.loads(line)
            if (r.get('lunasai_labels') or [None])[0] != 'ClinicalTrial':
                continue
            n += 1
            for k, v in r.items():
                present[k] += 1
                if v is not None and v != '' and v != [] and v != {}:
                    filled[k] += 1
    return n, present, filled


def main():
    c = connect(read_only=True)
    r = Registry(c, 'lane5_paper_numbers')
    c.execute(f"CREATE OR REPLACE TEMP TABLE art AS SELECT id, year, stub, pub_types, {DESIGN_SQL} AS design, "
              f"list_has_any(pub_types, {GUIDELINE + SRMA}) AS review, "
              f"list_has_any(pub_types, {TOOL_GSR}) AS tool_gsr FROM article")

    # A. major-topic evidence maps
    for d in CONDITIONS:
        c.execute(f"CREATE OR REPLACE TEMP TABLE exp AS {full_expansion_sql()}", ['MESH:' + d])
        c.execute("""CREATE OR REPLACE TEMP TABLE mapa AS SELECT DISTINCT p.population, a.*
            FROM am JOIN exp x ON x.descriptor = am.descriptor JOIN art a ON a.id = am.article
            CROSS JOIN populations p WHERE am.major AND NOT (p.exclude_stubs AND a.stub)""")
        r.run(f'A_{d}_major_map', f"""
            SELECT '{d}' AS condition, m.population, count(*) AS articles,
              count(*) FILTER (WHERE design='guideline') AS guideline,
              count(*) FILTER (WHERE design='sr_or_ma') AS sr_or_ma,
              count(*) FILTER (WHERE design='rct') AS rct,
              count(*) FILTER (WHERE design='other_trial') AS other_trial,
              count(*) FILTER (WHERE design='observational') AS observational,
              count(*) FILTER (WHERE design='other') AS other,
              count(*) FILTER (WHERE design IN ('rct','other_trial')) AS primary_studies,
              count(*) FILTER (WHERE design IN ('rct','other_trial') AND EXISTS (
                  SELECT 1 FROM cites ci JOIN art g ON g.id = ci.citer
                  WHERE ci.cited = m.id AND g.review AND NOT (m.population = 'without_stubs' AND g.stub))) AS primary_cited,
              count(*) FILTER (WHERE design IN ('rct','other_trial') AND NOT EXISTS (
                  SELECT 1 FROM cites ci JOIN art g ON g.id = ci.citer
                  WHERE ci.cited = m.id AND g.review AND NOT (m.population = 'without_stubs' AND g.stub))) AS primary_not_cited,
              count(*) FILTER (WHERE design = 'rct' AND EXISTS (
                  SELECT 1 FROM cites ci JOIN art g ON g.id = ci.citer
                  WHERE ci.cited = m.id AND g.review AND NOT (m.population = 'without_stubs' AND g.stub))) AS rct_cited,
              (SELECT count(DISTINCT ci.citer) FROM mapa p JOIN cites ci ON ci.cited = p.id JOIN art g ON g.id = ci.citer
                 WHERE p.population = m.population AND p.design IN ('rct','other_trial') AND g.review
                   AND NOT (m.population = 'without_stubs' AND g.stub)) AS distinct_citing_reviews,
              count(*) FILTER (WHERE design='sr_or_ma' AND year BETWEEN 2022 AND 2026) AS sr_or_ma_2022_2026,
              count(*) FILTER (WHERE design='guideline' AND year BETWEEN 2022 AND 2026) AS guideline_2022_2026,
              count(*) FILTER (WHERE year IS NULL) AS articles_without_year,
              (SELECT min(year) FROM mapa p WHERE p.population = m.population) AS min_year,
              (SELECT max(year) FROM mapa p WHERE p.population = m.population) AS max_year
            FROM mapa m GROUP BY m.population ORDER BY m.population""",
              'Major-topic HAS_MESH to the tree-number full expansion; exclusive design; citing set = any in-graph '
              'guideline/SR/MA (self-links removed in build). cited and not cited computed independently by EXISTS / NOT EXISTS.',
              csv=f'lane5_{d}_major_map.csv')
    # B. trial-landscape results Articles from the release files
    c.execute("""CREATE OR REPLACE TEMP TABLE vb AS SELECT subject AS article, object AS trial FROM e WHERE type = 'VALIDATED_BY'""")
    for d in CONDITIONS:
        tree = tree_precise_expansion(c, 'MESH:' + d)
        c.execute("CREATE OR REPLACE TEMP TABLE texp AS SELECT unnest(?::VARCHAR[]) AS descriptor", [sorted(tree)])
        c.execute("CREATE OR REPLACE TEMP TABLE tr AS SELECT DISTINCT trial FROM trial_mesh JOIN texp USING (descriptor)")
        c.execute("CREATE OR REPLACE TEMP TABLE rows_ AS SELECT vb.trial, vb.article FROM vb JOIN tr USING (trial)")
        r.run(f'B_{d}_results_articles', """
            WITH a AS (SELECT r.trial, r.article, coalesce(x.stub, false) AS stub FROM rows_ r LEFT JOIN art x ON x.id = r.article),
                 g_tool2 AS (SELECT DISTINCT object AS cited FROM e ci JOIN art g ON g.id = ci.subject AND g.tool_gsr
                            WHERE ci.type = 'CITES' AND ci.object IN (SELECT article FROM rows_)),
                 g_nonself AS (SELECT DISTINCT ci.cited FROM cites ci JOIN art g ON g.id = ci.citer AND g.tool_gsr
                            WHERE ci.cited IN (SELECT article FROM rows_))
            SELECT (SELECT count(*) FROM tr) AS trials,
              count(*) AS results_article_rows,
              count(DISTINCT article) AS distinct_results_articles_with_stubs,
              count(DISTINCT article) FILTER (WHERE NOT stub) AS distinct_results_articles_without_stubs,
              count(DISTINCT article) FILTER (WHERE stub) AS distinct_stub_results_articles,
              count(*) FILTER (WHERE article IN (SELECT cited FROM g_tool2)) AS cited_gsr_rows_tool_rule,
              count(DISTINCT article) FILTER (WHERE article IN (SELECT cited FROM g_tool2)) AS cited_gsr_distinct_with_stubs_tool_rule,
              count(DISTINCT article) FILTER (WHERE article IN (SELECT cited FROM g_tool2) AND NOT stub) AS cited_gsr_distinct_without_stubs_tool_rule,
              count(DISTINCT article) FILTER (WHERE article IN (SELECT cited FROM g_nonself)) AS cited_gsr_distinct_with_stubs_nonself,
              count(DISTINCT article) FILTER (WHERE article IN (SELECT cited FROM g_nonself) AND NOT stub) AS cited_gsr_distinct_without_stubs_nonself,
              count(DISTINCT trial) AS trials_with_results_article_with_stubs,
              count(DISTINCT trial) FILTER (WHERE NOT stub) AS trials_with_results_article_without_stubs
            FROM a""",
              'Tool rule: trials = condition mesh-list HAS_MESH to the tree-precise explode; results = VALIDATED_BY '
              'Article->ClinicalTrial; guideline_or_sr = Guideline/Practice Guideline/Systematic Review citer (no MA). '
              '"tool_rule" keeps CITES self-links as the tool does; "nonself" removes them.',
              csv=f'lane5_{d}_results_articles.csv')
    # C. ClinicalTrial node properties (raw shards)
    m = json.loads(MANIFEST.read_text())
    with Pool(12) as pool:
        parts = pool.map(trial_props, [str(INPUT / e['path']) for e in m['nodes']])
    n = sum(p[0] for p in parts)
    present, filled = Counter(), Counter()
    for _, p, f in parts:
        present.update(p)
        filled.update(f)
    expected_n = m['counts']['nodes_by_label']['ClinicalTrial']
    assert n == expected_n, (n, expected_n)
    full = c.execute("SELECT count(*) FROM nodes WHERE label='ClinicalTrial' AND name IS NOT NULL").fetchone()[0]
    rows = [dict(key=k, present=present[k], filled=filled[k], fill_rate_all=round(100 * filled[k] / n, 2),
                 fill_rate_registry_records=round(100 * filled[k] / full, 2)) for k in sorted(present, key=lambda k: (-filled[k], k))]
    T.mkdir(parents=True, exist_ok=True)
    with open(T / 'lane5_clinicaltrial_properties.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    r.results['C_clinicaltrial_properties'] = dict(trial_nodes=n, registry_records_with_title=full, keys=rows)
    r.queries['C_clinicaltrial_properties'] = dict(
        sql=None, parameters=[], note='Python stream over the 54 manifest node shards: every ClinicalTrial record, every '
        'top-level key; filled = not null / empty string / empty list / empty object. Denominators: all trial nodes, and '
        'trial nodes with a title (registry records).')
    r.results['rules'] = dict(design_order=['guideline', 'sr_or_ma', 'rct', 'other_trial', 'observational', 'other'],
                              guideline=GUIDELINE, sr_or_ma=SRMA, rct=RCT, other_trial=OTHER_TRIAL,
                              observational=OBSERVATIONAL, primary_studies=['rct', 'other_trial'],
                              citing_set='any in-graph Article whose pub_types include Guideline, Practice Guideline, '
                                         'Systematic Review, Meta-Analysis or Network Meta-Analysis; not restricted to '
                                         'the condition; CITES self-links removed',
                              year_window='Article.year BETWEEN 2022 AND 2026 inclusive (integer publication year)',
                              trial_tool_gsr=TOOL_GSR)
    r.results['code_commit'] = commit()
    r.save()


if __name__ == '__main__':
    main()
