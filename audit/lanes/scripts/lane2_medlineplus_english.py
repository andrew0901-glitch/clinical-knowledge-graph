"""Lane 2: MedlinePlus topic table, English-only, plus Spanish/English MeSH-mapping agreement.

Definitions are the paper topic table's (analysis_topic_population):
  topic descriptors   = HAS_MESH from the MedlinePlus topic, check tags removed
  none / one / full   = the descriptor itself / + HAS_BROADER children / + every HAS_BROADER_ANCESTOR descendant
                        (check-tag descendants removed)
  guideline or review = some Article indexed (HAS_MESH, any) to a matched descriptor has pub_types in
                        {Guideline, Practice Guideline, Systematic Review, Meta-Analysis, Review};
                        *_major variants require the Article's HAS_MESH is_major_topic = true
  condition trial     = some ClinicalTrial HAS_MESH study_aspect='condition', mesh_type='mesh-list' to a matched descriptor
  both                = guideline/review and condition trial reach, through the same matched descriptor
                        (the paper's caption wording). 'both_any' = both reached, possibly via different descriptors.
English vs Spanish: MedlinePlus node `language`; TRANSLATION_OF runs Spanish (subject) -> English (object).
"""
import csv

from lane_common import *

GR_TYPES = ['Guideline', 'Practice Guideline', 'Systematic Review', 'Meta-Analysis', 'Review']


def main():
    c = connect(read_only=True)
    r = Registry(c, 'lane2_medlineplus')
    c.execute("CREATE OR REPLACE TEMP TABLE modes AS SELECT * FROM (VALUES ('none',0),('one',1),('full',2)) t(mode,level)")
    c.execute("CREATE OR REPLACE TEMP TABLE topic AS SELECT id, name, language, topic_id, mapped_topic_id FROM nodes "
              "WHERE label = 'MedlinePlus'")
    c.execute("CREATE OR REPLACE TEMP TABLE q AS SELECT DISTINCT topic, descriptor FROM tm "
              "WHERE descriptor NOT IN (SELECT id FROM check_tag)")
    c.execute("""CREATE OR REPLACE TEMP TABLE x AS
        SELECT q.topic, m.mode, q.descriptor AS matched FROM q CROSS JOIN modes m
        UNION
        SELECT q.topic, m.mode, h.child FROM q JOIN hierarchy h ON h.parent = q.descriptor CROSS JOIN modes m
        WHERE ((m.level = 1 AND h.type = 'HAS_BROADER') OR (m.level = 2 AND h.type = 'HAS_BROADER_ANCESTOR'))
          AND h.child NOT IN (SELECT id FROM check_tag)""")
    c.execute(f"""CREATE OR REPLACE TEMP TABLE cap AS
        SELECT am.descriptor, p.population,
               bool_or(list_has_any(a.pub_types, {GR_TYPES})) AS gr,
               bool_or(list_has_any(a.pub_types, {GR_TYPES}) AND am.major) AS gr_major
        FROM am JOIN article a ON a.id = am.article CROSS JOIN populations p
        WHERE NOT (p.exclude_stubs AND a.stub) GROUP BY 1, 2""")
    c.execute("CREATE OR REPLACE TEMP TABLE trialcap AS SELECT DISTINCT descriptor FROM trial_mesh")
    c.execute("""CREATE OR REPLACE TEMP TABLE per_topic AS
        SELECT t.id AS topic, t.name, t.language, m.mode, p.population,
               coalesce(bool_or(cap.gr), false) AS gr, coalesce(bool_or(cap.gr_major), false) AS gr_major,
               coalesce(bool_or(tc.descriptor IS NOT NULL), false) AS trial,
               coalesce(bool_or(cap.gr AND tc.descriptor IS NOT NULL), false) AS both_same,
               coalesce(bool_or(cap.gr_major AND tc.descriptor IS NOT NULL), false) AS both_major_same,
               count(DISTINCT x.matched) AS matched_descriptors
        FROM topic t CROSS JOIN modes m CROSS JOIN populations p
        LEFT JOIN x ON x.topic = t.id AND x.mode = m.mode
        LEFT JOIN cap ON cap.descriptor = x.matched AND cap.population = p.population
        LEFT JOIN trialcap tc ON tc.descriptor = x.matched
        GROUP BY ALL""")
    table_sql = """SELECT population, mode, {lang} AS topic_set, count(*) AS topics,
               count(*) FILTER (WHERE gr) AS reaching_guideline_or_review,
               count(*) FILTER (WHERE trial) AS reaching_condition_trial,
               count(*) FILTER (WHERE both_same) AS reaching_both_same_descriptor,
               count(*) FILTER (WHERE gr AND trial) AS reaching_both_any_descriptor,
               count(*) FILTER (WHERE gr_major) AS reaching_major_guideline_or_review,
               count(*) FILTER (WHERE both_major_same) AS reaching_major_both_same_descriptor
        FROM per_topic {where} GROUP BY population, mode ORDER BY population, list_position(['none', 'one', 'full'], mode)"""
    r.run('table_english_only', table_sql.format(lang="'english'", where="WHERE language = 'en'"),
          'English MedlinePlus topics only (language=en). Paper topic-table rows.', csv='lane2_topic_table_english.csv')
    r.run('table_all_topics', table_sql.format(lang="'all'", where=""),
          'All 2,033 topics (English + Spanish), for reconciliation with analysis_topic_population.',
          csv='lane2_topic_table_all.csv')
    r.run('table_spanish_only', table_sql.format(lang="'spanish'", where="WHERE language = 'es'"),
          'Spanish topics only.', csv='lane2_topic_table_spanish.csv')
    r.run('languages', "SELECT language, count(*) AS topics FROM topic GROUP BY 1 ORDER BY 1", 'MedlinePlus nodes.')
    r.run('translation_direction', """SELECT s.language AS subject_language, o.language AS object_language, count(*) AS edges,
            count(DISTINCT e.subject) AS subjects, count(DISTINCT e.object) AS objects
        FROM e JOIN topic s ON s.id = e.subject JOIN topic o ON o.id = e.object WHERE e.type = 'TRANSLATION_OF' GROUP BY 1, 2""",
          'All TRANSLATION_OF edges.')
    r.run('unpaired', """SELECT t.language, count(*) AS topics_without_translation_edge FROM topic t
        WHERE NOT EXISTS (SELECT 1 FROM e WHERE e.type='TRANSLATION_OF' AND (e.subject = t.id OR e.object = t.id))
        GROUP BY 1""", 'Topics with no TRANSLATION_OF edge in either direction.')
    # Mapping agreement: compare full HAS_MESH descriptor sets (check tags kept and removed).
    c.execute("""CREATE OR REPLACE TEMP TABLE pairs AS SELECT e.subject AS es, e.object AS en FROM e
        WHERE e.type = 'TRANSLATION_OF'""")
    c.execute("""CREATE OR REPLACE TEMP TABLE sets AS SELECT topic, list_sort(list(DISTINCT descriptor)) AS all_d,
            list_sort(list(DISTINCT descriptor) FILTER (WHERE descriptor NOT IN (SELECT id FROM check_tag))) AS nc_d,
            list_sort(list(DISTINCT descriptor || CASE WHEN major THEN '*' ELSE '' END)) AS all_major
        FROM tm GROUP BY 1""")
    c.execute("""CREATE OR REPLACE TEMP TABLE pair_cmp AS SELECT p.es, p.en, coalesce(s.all_d, []) AS es_d, coalesce(n.all_d, []) AS en_d,
            coalesce(s.all_major, []) AS es_m, coalesce(n.all_major, []) AS en_m
        FROM pairs p LEFT JOIN sets s ON s.topic = p.es LEFT JOIN sets n ON n.topic = p.en""")
    r.run('mapping_agreement', """SELECT count(*) AS pairs,
            count(*) FILTER (WHERE es_d = en_d) AS identical_descriptor_sets,
            count(*) FILTER (WHERE es_m = en_m) AS identical_descriptor_and_major_flags,
            count(*) FILTER (WHERE es_d <> en_d) AS differing_descriptor_sets,
            count(*) FILTER (WHERE len(es_d) = 0) AS spanish_unmapped,
            count(*) FILTER (WHERE len(en_d) = 0) AS english_unmapped,
            count(*) FILTER (WHERE es_d <> en_d AND list_has_all(en_d, es_d)) AS spanish_strict_subset,
            count(*) FILTER (WHERE es_d <> en_d AND list_has_all(es_d, en_d)) AS spanish_strict_superset
        FROM pair_cmp""", 'Every TRANSLATION_OF pair; HAS_MESH descriptor sets incl. check tags.')
    r.run('mapping_differences', """SELECT p.es, s.name AS es_name, p.en, n.name AS en_name,
            list_filter(es_d, lambda d: NOT list_contains(en_d, d)) AS only_spanish,
            list_filter(en_d, lambda d: NOT list_contains(es_d, d)) AS only_english
        FROM pair_cmp p JOIN topic s ON s.id = p.es JOIN topic n ON n.id = p.en
        WHERE es_d <> en_d OR es_m <> en_m ORDER BY p.en""", 'Pairs whose sets or major flags differ.',
          csv='lane2_translation_mapping_differences.csv')
    # Per-topic CSV (both populations, all modes), with translation partner.
    c.execute(f"""COPY (
        SELECT t.id AS topic, t.name, t.language, t.topic_id,
               coalesce(pe.en, pe2.es) AS translation_partner,
               (SELECT count(DISTINCT descriptor) FROM q WHERE q.topic = t.id) AS topic_descriptors_non_check,
               pt.population, pt.mode, pt.matched_descriptors, pt.gr AS reaches_guideline_or_review,
               pt.trial AS reaches_condition_trial, pt.both_same AS reaches_both_same_descriptor,
               pt.gr AND pt.trial AS reaches_both_any_descriptor, pt.gr_major AS reaches_major_guideline_or_review,
               pt.both_major_same AS reaches_major_both_same_descriptor
        FROM topic t JOIN per_topic pt ON pt.topic = t.id
        LEFT JOIN pairs pe ON pe.es = t.id LEFT JOIN pairs pe2 ON pe2.en = t.id
        ORDER BY t.language, t.name, pt.population, CASE pt.mode WHEN 'none' THEN 0 WHEN 'one' THEN 1 ELSE 2 END
        ) TO '{T / 'lane2_per_topic.csv'}' (HEADER)""")
    r.queries['per_topic_csv'] = dict(sql='COPY per_topic joined to topic and TRANSLATION_OF partner -> tables/lane2_per_topic.csv',
                                      parameters=[], note='One row per topic x population x mode (2,033 x 2 x 3).')
    r.results['per_topic_csv_rows'] = c.execute(f"SELECT count(*) FROM read_csv('{T / 'lane2_per_topic.csv'}')").fetchone()[0]
    r.results['code_commit'] = commit()
    r.save()


if __name__ == '__main__':
    main()
