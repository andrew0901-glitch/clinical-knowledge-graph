"""Verify the 107 manifest-listed files and build the lane DuckDB projection from them only.

python audit/lanes/scripts/build.py
"""
import json, time

from lane_common import *


def main():
    m = json.loads(MANIFEST.read_text())
    files = m['nodes'] + m['edges']
    assert len(files) == 107, len(files)
    t0 = time.time()
    verified = []
    for e in files:
        p = INPUT / e['path']
        actual = sha(p)
        verified.append(dict(path=e['path'], sha256=e['sha256'], actual_sha256=actual,
                             bytes=e.get('bytes'), records=e.get('records'), passed=actual == e['sha256']))
    bad = [v for v in verified if not v['passed']]
    dump(R / 'input_verification.json', dict(
        manifest='<CLINICAL_KG_DATA>/manifest.json', manifest_sha256=sha(MANIFEST), version=m['version'],
        snapshot_date=m['snapshot_date'], input_root='<CLINICAL_KG_DATA>', files=len(verified),
        mismatches=len(bad), all_passed=not bad, verified=verified,
        seconds=round(time.time() - t0, 1)))
    assert not bad, bad
    print(f'verified {len(verified)} files', flush=True)

    node_files = [str(INPUT / e['path']) for e in m['nodes']]
    edge_files = [str(INPUT / e['path']) for e in m['edges']]
    c = connect()
    prep = []

    def create(sql, params=None):
        t = time.time()
        c.execute(sql, params or [])
        prep.append(dict(sql=sql, parameters='<107 manifest file paths>' if params else [],
                         seconds=round(time.time() - t, 1)))
        dump(R / 'build_queries.json', prep)
        print(sql[:90], round(time.time() - t, 1), flush=True)

    node_cols = dict(id='VARCHAR', lunasai_labels='VARCHAR[]', lunasai_layer='VARCHAR', name='VARCHAR',
                     mesh_id='VARCHAR', pmid='VARCHAR', year='VARCHAR', pub_types='VARCHAR[]',
                     language='VARCHAR', topic_id='VARCHAR', mapped_topic_id='VARCHAR', nct_id='VARCHAR')
    create("CREATE OR REPLACE TABLE nodes AS SELECT id, lunasai_labels[1] AS label, lunasai_layer AS layer, name, "
           "mesh_id, pmid, try_cast(year AS INTEGER) AS year, pub_types, language, topic_id, mapped_topic_id, nct_id "
           f"FROM read_json(?, format='newline_delimited', columns={node_cols}) "
           "WHERE lunasai_labels[1] IN ('Article','MeSHConcept','MedlinePlus','ClinicalTrial')", [node_files])
    edge_cols = dict(id='VARCHAR', subject='VARCHAR', object='VARCHAR', original_predicate='VARCHAR',
                     is_major_topic='BOOLEAN', study_aspect='VARCHAR', mesh_type='VARCHAR', depth='INTEGER',
                     child_tree_numbers='VARCHAR[]', parent_tree_numbers='VARCHAR[]',
                     publication_role='VARCHAR', reference_type='VARCHAR')
    create("CREATE OR REPLACE TABLE e AS SELECT * EXCLUDE (original_predicate), "
           "split_part(original_predicate, '.', -1) AS type "
           f"FROM read_json(?, format='newline_delimited', columns={edge_cols}) "
           "WHERE split_part(original_predicate, '.', -1) IN ('HAS_MESH','CITES','HAS_BROADER','HAS_BROADER_ANCESTOR',"
           "'TRANSLATION_OF','VALIDATED_BY','CITES_BACKGROUND','HAS_DERIVED_PUBLICATION')", [edge_files])

    # Derived tables. Stubs = lunasai_layer ctgov_identity_only (the 578,177 identity-only Articles).
    create("CREATE OR REPLACE TABLE article AS SELECT id, pmid, year, coalesce(pub_types, []) AS pub_types, "
           f"layer = '{STUB_LAYER}' AS stub FROM nodes WHERE label = 'Article'")
    create("CREATE OR REPLACE TABLE populations AS SELECT * FROM (VALUES ('with_stubs', false), ('without_stubs', true)) "
           "p(population, exclude_stubs)")
    create("CREATE OR REPLACE TABLE check_tag AS SELECT id, name FROM nodes WHERE label = 'MeSHConcept' "
           "AND name IN (SELECT unnest(?::VARCHAR[]))", [CHECK_TAG_NAMES])
    create("CREATE OR REPLACE TABLE mesh AS SELECT id, mesh_id, name, id IN (SELECT id FROM check_tag) AS check_tag "
           "FROM nodes WHERE label = 'MeSHConcept'")
    create("CREATE OR REPLACE TABLE am AS SELECT e.subject AS article, e.object AS descriptor, e.is_major_topic AS major "
           "FROM e JOIN article a ON a.id = e.subject WHERE e.type = 'HAS_MESH'")
    create("CREATE OR REPLACE TABLE trial_mesh AS SELECT subject AS trial, object AS descriptor FROM e "
           "WHERE type = 'HAS_MESH' AND starts_with(subject, 'clinicaltrials:') "
           "AND study_aspect = 'condition' AND mesh_type = 'mesh-list'")
    create("CREATE OR REPLACE TABLE tm AS SELECT e.subject AS topic, e.object AS descriptor, e.is_major_topic AS major "
           "FROM e JOIN nodes n ON n.id = e.subject AND n.label = 'MedlinePlus' WHERE e.type = 'HAS_MESH'")
    # Self-citations (subject = object) are removed here, once, for every lane.
    create("CREATE OR REPLACE TABLE cites AS SELECT subject AS citer, object AS cited FROM e "
           "WHERE type = 'CITES' AND subject <> object")
    create("CREATE OR REPLACE TABLE hierarchy AS SELECT subject AS child, object AS parent, "
           "CASE WHEN type = 'HAS_BROADER' THEN 1 ELSE depth END AS depth, type, child_tree_numbers, parent_tree_numbers "
           "FROM e WHERE type IN ('HAS_BROADER','HAS_BROADER_ANCESTOR')")

    census = {r[0]: r[1] for r in c.execute("SELECT label, count(*) FROM nodes GROUP BY 1").fetchall()}
    ecensus = {r[0]: r[1] for r in c.execute("SELECT type, count(*) FROM e GROUP BY 1").fetchall()}
    stubs = c.execute("SELECT count(*) FROM article WHERE stub").fetchone()[0]
    self_cites = c.execute("SELECT count(*) FROM e WHERE type='CITES' AND subject = object").fetchone()[0]
    checks = c.execute("SELECT count(*) FROM check_tag").fetchone()[0]
    want_n, want_e = m['counts']['nodes_by_label'], m['counts']['edges_by_type']
    agree = {k: census.get(k) == want_n[k] for k in census} | {k: ecensus.get(k) == want_e[k] for k in ecensus}
    dump(R / 'build_census.json', dict(nodes=census, edges=ecensus, stubs=stubs, expected_stubs=EXPECTED_STUBS,
                                       cites_self_links_removed=self_cites, check_tags_resolved=checks,
                                       manifest_count_agreement=agree, code_commit=commit(),
                                       seconds=round(time.time() - t0, 1)))
    assert all(agree.values()), agree
    assert stubs == EXPECTED_STUBS, stubs
    assert checks == 40, checks
    c.close()
    print('BUILT', census, ecensus, stubs, self_cites, flush=True)


if __name__ == '__main__':
    main()
