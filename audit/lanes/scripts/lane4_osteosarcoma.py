"""Lane 4: Osteosarcoma (D012516) hierarchy example, full downward expansion.

Expansion = D012516 + HAS_BROADER_ANCESTOR descendants (tree-precise, check tags removed).
Ewing branch = Sarcoma, Ewing (D012512) + its own descendants within the expansion.
Narrower branch = each direct HAS_BROADER child of D012516 plus its descendants.
Trials = ClinicalTrial HAS_MESH study_aspect='condition', mesh_type='mesh-list'.
Articles = HAS_MESH (any, and major-topic) for both Article populations.
"Only through X" = every matched descriptor of the trial/article lies in X.
"""
from lane_common import *

ROOT, EWING = 'MESH:D012516', 'MESH:D012512'


def main():
    c = connect(read_only=True)
    r = Registry(c, 'lane4_osteosarcoma')
    c.execute(f"CREATE OR REPLACE TEMP TABLE exp AS {full_expansion_sql()}", [ROOT])
    c.execute("""CREATE OR REPLACE TEMP TABLE branch AS
        SELECT h.child AS branch, h.child AS descriptor FROM hierarchy h WHERE h.type = 'HAS_BROADER' AND h.parent = $1
          AND h.child IN (SELECT descriptor FROM exp)
        UNION SELECT b.child, d.child FROM hierarchy b JOIN hierarchy d ON d.parent = b.child AND d.type = 'HAS_BROADER_ANCESTOR'
        WHERE b.type = 'HAS_BROADER' AND b.parent = $1 AND d.child IN (SELECT descriptor FROM exp)""", [ROOT])
    c.execute("CREATE OR REPLACE TEMP TABLE ewing AS SELECT descriptor FROM branch WHERE branch = $1", [EWING])
    r.run('expansion', """SELECT x.descriptor, m.mesh_id, m.name, x.depth, x.descriptor IN (SELECT descriptor FROM ewing) AS ewing_branch,
            (SELECT list(DISTINCT b.branch) FROM branch b WHERE b.descriptor = x.descriptor) AS branches,
            (SELECT list(DISTINCT tn) FROM (SELECT unnest(child_tree_numbers) tn FROM hierarchy h
                WHERE h.child = x.descriptor AND h.type = 'HAS_BROADER')) AS tree_numbers
        FROM exp x JOIN mesh m ON m.id = x.descriptor ORDER BY x.depth, m.name""",
          'Full expansion of D012516 with Ewing-branch flag and tree numbers.', csv='lane4_expansion.csv')
    c.execute("""CREATE OR REPLACE TEMP TABLE tmatch AS SELECT DISTINCT t.trial, t.descriptor FROM trial_mesh t
        JOIN exp USING (descriptor)""")
    r.run('trials', """WITH per AS (SELECT trial, bool_and(descriptor IN (SELECT descriptor FROM ewing)) AS only_ewing,
                bool_or(descriptor IN (SELECT descriptor FROM ewing)) AS any_ewing, bool_or(descriptor = $1) AS direct
            FROM tmatch GROUP BY 1)
        SELECT count(*) AS trials_full_expansion, count(*) FILTER (WHERE direct) AS trials_direct_on_osteosarcoma,
               count(*) FILTER (WHERE only_ewing) AS trials_only_through_ewing,
               count(*) FILTER (WHERE any_ewing) AS trials_matching_ewing_branch,
               count(*) FILTER (WHERE NOT only_ewing) AS trials_without_ewing_branch,
               round(100.0 * count(*) FILTER (WHERE only_ewing) / count(*), 2) AS pct_only_through_ewing
        FROM per""", 'Condition mesh-list trials.', [ROOT], csv='lane4_trials.csv')
    c.execute("""CREATE OR REPLACE TEMP TABLE amatch AS SELECT DISTINCT p.population, i.indexing, am.article, am.descriptor
        FROM am JOIN exp USING (descriptor) JOIN article a ON a.id = am.article
        CROSS JOIN populations p CROSS JOIN (VALUES ('any'), ('major')) i(indexing)
        WHERE NOT (p.exclude_stubs AND a.stub) AND (i.indexing = 'any' OR am.major)""")
    r.run('articles', """WITH per AS (SELECT population, indexing, article,
                bool_and(descriptor IN (SELECT descriptor FROM ewing)) AS only_ewing,
                bool_or(descriptor IN (SELECT descriptor FROM ewing)) AS any_ewing, bool_or(descriptor = $1) AS direct
            FROM amatch GROUP BY 1, 2, 3)
        SELECT population, indexing, count(*) AS articles_with_ewing_branch,
               count(*) FILTER (WHERE NOT only_ewing) AS articles_without_ewing_branch,
               count(*) FILTER (WHERE only_ewing) AS articles_only_through_ewing,
               count(*) FILTER (WHERE any_ewing) AS articles_indexed_to_ewing_branch,
               count(*) FILTER (WHERE direct) AS articles_direct_on_osteosarcoma,
               round(100.0 * count(*) FILTER (WHERE only_ewing) / count(*), 2) AS pct_only_through_ewing
        FROM per GROUP BY 1, 2 ORDER BY indexing, population""", 'Both Article populations; any and major indexing.',
          [ROOT], csv='lane4_articles.csv')
    r.run('branches', """WITH tb AS (SELECT b.branch, t.trial FROM branch b JOIN tmatch t USING (descriptor)),
             ab AS (SELECT b.branch, a.population, a.indexing, a.article FROM branch b JOIN amatch a USING (descriptor))
        SELECT m.mesh_id AS branch_mesh_id, m.name AS branch,
               (SELECT count(DISTINCT descriptor) FROM branch b2 WHERE b2.branch = b.branch) AS descriptors,
               (SELECT count(DISTINCT trial) FROM tb WHERE tb.branch = b.branch) AS trials,
               (SELECT count(DISTINCT trial) FROM tb WHERE tb.branch = b.branch AND trial NOT IN
                   (SELECT trial FROM tmatch WHERE descriptor NOT IN (SELECT descriptor FROM branch b3 WHERE b3.branch = b.branch))) AS trials_only_through_branch,
               (SELECT count(DISTINCT article) FROM ab WHERE ab.branch = b.branch AND population = 'with_stubs' AND indexing = 'any') AS articles_with_stubs,
               (SELECT count(DISTINCT article) FROM ab WHERE ab.branch = b.branch AND population = 'without_stubs' AND indexing = 'any') AS articles_without_stubs,
               (SELECT count(DISTINCT article) FROM ab WHERE ab.branch = b.branch AND population = 'with_stubs' AND indexing = 'any' AND article NOT IN
                   (SELECT article FROM amatch WHERE population = 'with_stubs' AND indexing = 'any' AND descriptor NOT IN
                       (SELECT descriptor FROM branch b4 WHERE b4.branch = b.branch))) AS articles_only_through_branch
        FROM (SELECT DISTINCT branch FROM branch) b JOIN mesh m ON m.id = b.branch
        ORDER BY trials DESC, articles_with_stubs DESC""",
          'Direct narrower branches of D012516, ranked by trials then articles.', csv='lane4_branches.csv')
    r.run('root_only', """SELECT (SELECT count(DISTINCT trial) FROM tmatch WHERE descriptor = $1) AS trials_on_root_descriptor,
            (SELECT count(DISTINCT trial) FROM tmatch WHERE trial NOT IN (SELECT trial FROM tmatch WHERE descriptor <> $1)) AS trials_only_on_root,
            (SELECT count(DISTINCT article) FROM amatch WHERE population='with_stubs' AND indexing='any' AND descriptor = $1) AS articles_on_root_descriptor""",
          'Root descriptor contribution.', [ROOT])
    r.results['code_commit'] = commit()
    r.save()


if __name__ == '__main__':
    main()
