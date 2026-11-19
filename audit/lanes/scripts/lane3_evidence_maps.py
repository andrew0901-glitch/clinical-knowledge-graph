"""Lane 3: evidence maps for D001943, D000544, D006333 under full downward expansion.

Map Articles  = Articles with HAS_MESH to any descriptor in the expansion (indexing='any'), or with
                is_major_topic = true (indexing='major'); check tags never in the expansion.
Design        = exclusive, first match in order (NLM pub_types):
                guideline   {Guideline, Practice Guideline}
                sr_or_ma    {Systematic Review, Meta-Analysis, Network Meta-Analysis}
                rct         {Randomized Controlled Trial, Randomized Controlled Trial, Veterinary}
                other_trial {Clinical Trial, Clinical Trial Phase I-IV, Controlled Clinical Trial,
                             Pragmatic Clinical Trial, Equivalence Trial, Adaptive Clinical Trial,
                             Clinical Trial, Veterinary}   (Clinical Trial Protocol is NOT a trial report -> other)
                observational {Observational Study, Observational Study, Veterinary}
                other       everything else, including no pub_types
Primary study = design rct or other_trial.
Citing review = any in-graph Article whose pub_types include a guideline or SR/MA type (non-exclusive);
                CITES self-links (subject = object) removed in build.py. Citing reviews may lie outside the map.
Populations   = with_stubs / without_stubs (identity-only stubs removed as map Articles and as citers).
"""
from lane_common import *

CONDITIONS = ['D001943', 'D000544', 'D006333']
GUIDELINE = ['Guideline', 'Practice Guideline']
SRMA = ['Systematic Review', 'Meta-Analysis', 'Network Meta-Analysis']
RCT = ['Randomized Controlled Trial', 'Randomized Controlled Trial, Veterinary']
OTHER_TRIAL = ['Clinical Trial', 'Clinical Trial, Phase I', 'Clinical Trial, Phase II', 'Clinical Trial, Phase III',
               'Clinical Trial, Phase IV', 'Controlled Clinical Trial', 'Pragmatic Clinical Trial', 'Equivalence Trial',
               'Adaptive Clinical Trial', 'Clinical Trial, Veterinary']
OBSERVATIONAL = ['Observational Study', 'Observational Study, Veterinary']
DESIGN_SQL = (f"CASE WHEN list_has_any(pub_types, {GUIDELINE}) THEN 'guideline' "
              f"WHEN list_has_any(pub_types, {SRMA}) THEN 'sr_or_ma' "
              f"WHEN list_has_any(pub_types, {RCT}) THEN 'rct' "
              f"WHEN list_has_any(pub_types, {OTHER_TRIAL}) THEN 'other_trial' "
              f"WHEN list_has_any(pub_types, {OBSERVATIONAL}) THEN 'observational' ELSE 'other' END")
REVIEW_SQL = f"list_has_any(pub_types, {GUIDELINE + SRMA})"


def main():
    c = connect(read_only=True)
    r = Registry(c, 'lane3_evidence_maps')
    c.execute(f"CREATE OR REPLACE TEMP TABLE art AS SELECT id, year, stub, {DESIGN_SQL} AS design, "
              f"{REVIEW_SQL} AS review FROM article")
    c.execute("CREATE OR REPLACE TEMP TABLE idx AS SELECT * FROM (VALUES ('any'), ('major')) t(indexing)")
    for d in CONDITIONS:
        root = 'MESH:' + d
        c.execute(f"CREATE OR REPLACE TEMP TABLE exp AS {full_expansion_sql()}", [root])
        tree = tree_precise_expansion(c, root)
        c.execute("CREATE OR REPLACE TEMP TABLE exp_tree AS SELECT unnest(?::VARCHAR[]) AS descriptor", [sorted(tree)])
        r.run(f'{d}_expansion', "SELECT e.descriptor, m.mesh_id, m.name, e.depth, e.descriptor IN (SELECT descriptor FROM exp_tree) "
              "AS in_tree_precise FROM exp e JOIN mesh m ON m.id = e.descriptor ORDER BY e.depth, m.name",
              'Full downward expansion (HAS_BROADER_ANCESTOR closure, check tags removed); tree-precise membership flagged.',
              csv=f'lane3_{d}_expansion.csv')
        c.execute("""CREATE OR REPLACE TEMP TABLE mapa AS SELECT DISTINCT i.indexing, p.population, a.*
            FROM am JOIN exp x ON x.descriptor = am.descriptor JOIN art a ON a.id = am.article
            CROSS JOIN idx i CROSS JOIN populations p
            WHERE (i.indexing = 'any' OR am.major) AND NOT (p.exclude_stubs AND a.stub)""")
        c.execute("""CREATE OR REPLACE TEMP TABLE prim_cit AS
            SELECT m.indexing, m.population, m.id AS primary_id, m.design, ci.citer
            FROM mapa m JOIN cites ci ON ci.cited = m.id JOIN art g ON g.id = ci.citer AND g.review
            JOIN populations p ON p.population = m.population
            WHERE m.design IN ('rct', 'other_trial') AND NOT (p.exclude_stubs AND g.stub)""")
        r.run(f'{d}_map', f"""
            WITH pc AS (SELECT indexing, population, count(DISTINCT primary_id) AS primary_cited_by_review,
                               count(DISTINCT primary_id) FILTER (WHERE design = 'rct') AS rct_cited_by_review,
                               count(DISTINCT primary_id) FILTER (WHERE design = 'other_trial') AS other_trial_cited_by_review
                        FROM prim_cit GROUP BY 1, 2),
                 cr AS (SELECT q.indexing, q.population, count(DISTINCT q.citer) AS distinct_citing_reviews,
                               count(DISTINCT q.citer) FILTER (WHERE mx.id IS NOT NULL) AS distinct_citing_reviews_in_map
                        FROM prim_cit q LEFT JOIN mapa mx ON mx.id = q.citer AND mx.indexing = q.indexing
                             AND mx.population = q.population GROUP BY 1, 2),
                 agg AS (SELECT indexing, population, count(*) AS articles,
                   count(*) FILTER (WHERE design = 'guideline') AS guideline,
                   count(*) FILTER (WHERE design = 'sr_or_ma') AS sr_or_ma,
                   count(*) FILTER (WHERE design = 'rct') AS rct,
                   count(*) FILTER (WHERE design = 'other_trial') AS other_trial,
                   count(*) FILTER (WHERE design = 'observational') AS observational,
                   count(*) FILTER (WHERE design = 'other') AS other,
                   count(*) FILTER (WHERE design IN ('rct','other_trial')) AS primary_studies,
                   count(*) FILTER (WHERE design = 'sr_or_ma' AND year BETWEEN 2022 AND 2026) AS sr_or_ma_2022_2026,
                   count(*) FILTER (WHERE design = 'guideline' AND year BETWEEN 2022 AND 2026) AS guideline_2022_2026,
                   count(*) FILTER (WHERE year IS NULL) AS articles_without_year
                   FROM mapa GROUP BY 1, 2)
            SELECT '{d}' AS condition, a.indexing, a.population, (SELECT count(*) FROM exp) AS descriptors,
                   a.articles, a.guideline, a.sr_or_ma, a.rct, a.other_trial, a.observational, a.other, a.primary_studies,
                   coalesce(pc.primary_cited_by_review, 0) AS primary_cited_by_review,
                   a.primary_studies - coalesce(pc.primary_cited_by_review, 0) AS primary_not_cited_by_review,
                   coalesce(pc.rct_cited_by_review, 0) AS rct_cited_by_review,
                   coalesce(pc.other_trial_cited_by_review, 0) AS other_trial_cited_by_review,
                   coalesce(cr.distinct_citing_reviews, 0) AS distinct_citing_reviews,
                   coalesce(cr.distinct_citing_reviews_in_map, 0) AS distinct_citing_reviews_in_map,
                   a.sr_or_ma_2022_2026, a.guideline_2022_2026, a.articles_without_year
            FROM agg a LEFT JOIN pc USING (indexing, population) LEFT JOIN cr USING (indexing, population)
            ORDER BY a.indexing, a.population""",
              'Census of map Articles (full expansion). Citing reviews: any in-graph guideline/SR/MA, self-links removed.',
              csv=f'lane3_{d}_map.csv')
        r.run(f'{d}_recent_reviews_by_year', """SELECT indexing, population, year, count(*) FILTER (WHERE design='sr_or_ma') AS sr_or_ma,
                   count(*) FILTER (WHERE design='guideline') AS guideline
            FROM mapa WHERE year BETWEEN 2022 AND 2026 GROUP BY ALL ORDER BY indexing, population, year""",
              'Exclusive design; year = Article year property.', csv=f'lane3_{d}_reviews_2022_2026.csv')
        r.run(f'{d}_tree_precise_sensitivity', """SELECT p.population, count(DISTINCT a.id) AS articles_any_tree_precise,
                   (SELECT count(*) FROM exp_tree) AS descriptors_tree_precise,
                   (SELECT count(DISTINCT trial) FROM trial_mesh t JOIN exp_tree x USING (descriptor)) AS condition_trials_tree_precise,
                   (SELECT count(DISTINCT trial) FROM trial_mesh t JOIN exp x USING (descriptor)) AS condition_trials_full
            FROM am JOIN exp_tree x ON x.descriptor = am.descriptor JOIN art a ON a.id = am.article CROSS JOIN populations p
            WHERE NOT (p.exclude_stubs AND a.stub) GROUP BY 1 ORDER BY 1""",
              'Tree-precise explode (trial_landscape.py rule) vs descriptor-level full closure.')
        c.execute("""CREATE OR REPLACE TEMP TABLE exp_hb AS WITH RECURSIVE t(descriptor) AS (SELECT $1 UNION
            SELECT h.child FROM hierarchy h JOIN t ON h.parent = t.descriptor WHERE h.type = 'HAS_BROADER')
            SELECT descriptor FROM t WHERE descriptor NOT IN (SELECT id FROM check_tag)""", [root])
        r.run(f'{d}_has_broader_closure_sensitivity', """SELECT p.population,
                   (SELECT count(*) FROM exp_hb) AS descriptors_has_broader_closure,
                   (SELECT list(m.name ORDER BY m.name) FROM exp_hb x JOIN mesh m ON m.id = x.descriptor
                     WHERE x.descriptor NOT IN (SELECT descriptor FROM exp)) AS extra_descriptors,
                   count(DISTINCT a.id) AS articles_any_has_broader_closure,
                   count(DISTINCT a.id) FILTER (WHERE am.descriptor NOT IN (SELECT descriptor FROM exp)
                     AND a.id NOT IN (SELECT am2.article FROM am am2 JOIN exp USING (descriptor))) AS articles_added,
                   (SELECT count(DISTINCT trial) FROM trial_mesh JOIN exp_hb USING (descriptor)) AS condition_trials_has_broader_closure
            FROM am JOIN exp_hb x ON x.descriptor = am.descriptor JOIN art a ON a.id = am.article CROSS JOIN populations p
            WHERE NOT (p.exclude_stubs AND a.stub) GROUP BY 1 ORDER BY 1""",
              'Untyped transitive HAS_BROADER closure (ignores tree numbers) vs the tree-precise HAS_BROADER_ANCESTOR closure used as primary.')
    r.results['design_rule'] = dict(order=['guideline', 'sr_or_ma', 'rct', 'other_trial', 'observational', 'other'],
                                    guideline=GUIDELINE, sr_or_ma=SRMA, rct=RCT, other_trial=OTHER_TRIAL,
                                    observational=OBSERVATIONAL, citing_review_types=GUIDELINE + SRMA)
    r.results['code_commit'] = commit()
    r.save()


if __name__ == '__main__':
    main()
