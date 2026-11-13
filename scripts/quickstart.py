#!/usr/bin/env python3
"""Explore the Lunas Clinical Evidence KG with DuckDB, straight from the downloaded files.

  pip install duckdb
  python scripts/quickstart.py --input ckg                      # HF or Zenodo download folder
  python scripts/quickstart.py --input ckg --mesh "Asthma"      # pick a MeSH descriptor by name
  python scripts/quickstart.py --input ckg --parquet            # first convert to Parquet (much faster reruns)

If `manifest.json` (Hugging Face) or `zenodo_manifest.json` (Zenodo) is present under `--input`,
only the files it actually lists are read -- anything else under nodes/edges/ is ignored and
reported. Without either manifest (e.g. a locally-built sample), every matching file is read.

Relationship types: use `original_predicate` (e.g. lunasai:vocab.CITES). Many edges carry the generic
Biolink predicate biolink:related_to, so `predicate` alone does not distinguish them.

Directions verified against the real, fully-loaded graph (see docs/VALIDATION_RESULTS.md):
  * VALIDATED_BY is subject=Article (the results publication), object=ClinicalTrial. v0.2.0: this
    type now holds ONLY the ClinicalTrials.gov RESULT role -- v0.1.0 mixed background/derived
    references into the same type. Those are now their own types, same direction:
    CITES_BACKGROUND (BACKGROUND role) and HAS_DERIVED_PUBLICATION (DERIVED role). The old
    `ctgov_publications.jsonl` sidecar from v0.1.0 no longer exists -- its content is these three
    native edge types now.
  * HAS_BROADER is subject=the narrower/child MeSHConcept, object=the broader/parent MeSHConcept
    (e.g. Zona Fasciculata -[HAS_BROADER]-> Adrenal Cortex; verified against 15 well-known pairs
    and the edges' own parent_tree_numbers/child_tree_numbers), so going subject->object walks
    UP the hierarchy toward broader concepts, and object->subject (i.e. matching on `object`)
    walks DOWN toward children -- PubMed's MeSH "explode" behavior. v0.2.0 renamed this from
    v0.1.0's `PARENT_OF` (export-side name only, to match the real direction; same direction,
    clearer name). `ANCESTOR_OF` is likewise renamed `HAS_BROADER_ANCESTOR`.
  * AUTHORED_BY is subject=Article, object=Author.
  * New in v0.2.0: HAS_PMC_RECORD (subject=Article, object=PMCRecord) and PUBLISHED_IN
    (subject=Article, object=Journal). `Journal` is a first-class node type now.
  * Removed in v0.2.0: HAS_RIGHTS_EVIDENCE and HAS_USE_GRANT no longer exist.
"""
import argparse, glob, json, os, sys

try:
    import duckdb
except ImportError:
    sys.exit("pip install duckdb")

NODE_COLS = {"id": "VARCHAR", "category": "JSON", "name": "VARCHAR", "lunasai_labels": "JSON",
             "pmid": "VARCHAR", "pmcid": "VARCHAR", "year": "VARCHAR", "journal": "VARCHAR",
             "cited_by_count": "BIGINT", "pub_types": "JSON", "mesh_major_topics": "JSON"}
EDGE_COLS = {"id": "VARCHAR", "subject": "VARCHAR", "predicate": "VARCHAR", "object": "VARCHAR",
             "original_predicate": "VARCHAR", "lunasai_layer": "VARCHAR", "knowledge_level": "VARCHAR",
             "agent_type": "VARCHAR", "is_major_topic": "BOOLEAN"}

# The real, NLM-published "Check Tags MeSH Terms" (CTMTs) list -- 40 non-subject qualifiers
# (age groups, sex, species, historical periods, pregnancy) that are attached to most articles
# and are not meaningful "topics" for a traversal like query 7 below. v0.1.0 carries no
# is_check_tag flag on (:MeSHConcept) or on HAS_MESH, so this fixed list (from the NLM Lister
# Hill Center "Check Tags MeSH Terms Indexing Project" report, May 2023) is the real exclusion
# set; see docs/DATA_NOTES.md.
CHECK_TAGS = [
    "Humans", "Female", "Male", "Animals", "Adult", "Middle Aged", "Aged", "Adolescent",
    "Young Adult", "Mice", "Child", "Aged, 80 and over", "Rats", "Child, Preschool",
    "United States", "Pregnancy", "Infant", "Infant, Newborn", "Cricetinae", "Dogs", "Cats",
    "Rabbits", "Guinea Pigs", "Sheep", "Swine", "Cattle", "Horses", "Bees", "Chick Embryo",
    "Chlorocebus aethiops", "History of Medicine", "History, Ancient", "History, Medieval",
    "History, 15th Century", "History, 16th Century", "History, 17th Century",
    "History, 18th Century", "History, 19th Century", "History, 20th Century",
    "History, 21st Century",
]
GUIDELINE_OR_SYSTEMATIC_REVIEW = ["Guideline", "Practice Guideline", "Systematic Review"]


def manifest_shards(root, kind):
    """Basenames of the {kind} files actually expected on disk (minus any '{kind}__' flat-
    naming prefix, so every download layout compares equal), from whichever manifest root
    has:
      - manifest.json (Hugging Face layout): one row per shard file, e.g.
        nodes/part-w00-00000.jsonl.gz.
      - zenodo_manifest.json (Zenodo layout): Zenodo caps a record at 100 files, so many
        original shards are gzip-member-concatenated into a handful of per-worker BUNDLE
        files (e.g. nodes/nodes-w00.jsonl.gz) -- the files really on disk are the bundle
        names under "bundles", never the per-shard names inside them.
    Returns None if root has neither manifest (e.g. a locally-built sample_out/ dir, which
    has no stray-file problem to guard against)."""
    prefix = f"{kind}__"

    def norm(path):
        b = os.path.basename(path)
        return b[len(prefix):] if b.startswith(prefix) else b

    hf_path = os.path.join(root, "manifest.json")
    if os.path.exists(hf_path):
        with open(hf_path) as fh:
            manifest = json.load(fh)
        return {norm(entry["path"]) for entry in manifest.get(kind, [])}

    zenodo_path = os.path.join(root, "zenodo_manifest.json")
    if os.path.exists(zenodo_path):
        with open(zenodo_path) as fh:
            zmanifest = json.load(fh)
        return {norm(p) for p in zmanifest.get("bundles", {}) if p.startswith(f"{kind}/")}

    return None


def files_for(root, kind):
    """Explicit list of {kind} files to read: every file in the folder, unless manifest.json
    exists, in which case only the files it lists -- whatever else is in the folder is ignored."""
    for pat in (os.path.join(root, kind, "*.jsonl.gz"), os.path.join(root, f"{kind}__*.jsonl.gz")):
        found = sorted(glob.glob(pat))
        if found:
            wanted = manifest_shards(root, kind)
            if wanted is not None:
                prefix = f"{kind}__"
                def shard(p):
                    b = os.path.basename(p)
                    return b[len(prefix):] if b.startswith(prefix) else b
                ignored = [f for f in found if shard(f) not in wanted]
                if ignored:
                    print(f"ignoring {len(ignored)} {kind} file(s) not listed in the manifest "
                          f"(e.g. {os.path.basename(ignored[0])})", file=sys.stderr)
                found = [f for f in found if shard(f) in wanted]
            if found:
                return found
    sys.exit(f"no {kind} files found under {root}")


def reader(file_list, cols):
    spec = "{" + ", ".join(f"'{k}': '{v}'" for k, v in cols.items()) + "}"
    files_sql = "[" + ", ".join("'" + f.replace("'", "''") + "'" for f in file_list) + "]"
    return (f"read_json({files_sql}, format='newline_delimited', columns={spec}, "
            f"ignore_errors=true, maximum_object_size=104857600)")


def sql_list(items):
    return "[" + ", ".join("'" + i.replace("'", "''") + "'" for i in items) + "]"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--mesh", default="Asthma", help="MeSH descriptor name to explore")
    ap.add_argument("--medlineplus-topic", default="Asthma", help="MedlinePlus topic name for query 7")
    ap.add_argument("--trial", default="clinicaltrials:NCT00825071", help="ClinicalTrial id for query 6")
    ap.add_argument("--seed-pmid", default="PMID:10021452", help="Article id for query 8")
    ap.add_argument("--author-id", default="lunasai:openalex_author.A5051827275", help="Author id for query 9")
    ap.add_argument("--parquet", action="store_true", help="write nodes.parquet / edges.parquet first and query those")
    a = ap.parse_args()
    con = duckdb.connect()
    con.sql("SET preserve_insertion_order=false")
    nsrc, esrc = reader(files_for(a.input, "nodes"), NODE_COLS), reader(files_for(a.input, "edges"), EDGE_COLS)
    if a.parquet:
        np_, ep = os.path.join(a.input, "nodes.parquet"), os.path.join(a.input, "edges.parquet")
        if not os.path.exists(np_):
            print("writing nodes.parquet ...", flush=True)
            con.sql(f"COPY (SELECT * FROM {nsrc}) TO '{np_}' (FORMAT parquet)")
        if not os.path.exists(ep):
            print("writing edges.parquet ... (one pass over ~110M edges)", flush=True)
            con.sql(f"COPY (SELECT * FROM {esrc}) TO '{ep}' (FORMAT parquet)")
        nsrc, esrc = f"read_parquet('{np_}')", f"read_parquet('{ep}')"
    con.sql(f"CREATE VIEW nodes AS SELECT * FROM {nsrc}")
    con.sql(f"""CREATE VIEW edges AS SELECT *,
                regexp_extract(original_predicate, '[.:]([A-Za-z_]+)$', 1) AS rel FROM {esrc}""")

    print("\n1. Relationship types (from original_predicate)")
    con.sql("SELECT rel, count(*) AS n FROM edges GROUP BY rel ORDER BY n DESC").show(max_rows=60)

    print("\n2. Node labels")
    con.sql("""SELECT coalesce(json_extract_string(lunasai_labels, '$[0]'),
                              json_extract_string(category, '$[0]')) AS label, count(*) AS n
               FROM nodes GROUP BY label ORDER BY n DESC""").show(max_rows=40)

    print(f"\n3. Articles with MeSH descriptor '{a.mesh}' as a MAJOR topic, most cited first")
    con.sql(f"""WITH m AS (SELECT id FROM nodes WHERE lower(name) = lower('{a.mesh.replace("'", "''")}') LIMIT 5)
                SELECT n.pmid, n.name AS title, n.journal, n.year, n.cited_by_count
                FROM edges e JOIN m ON e.object = m.id JOIN nodes n ON n.id = e.subject
                WHERE e.rel = 'HAS_MESH' AND coalesce(e.is_major_topic, false)
                ORDER BY n.cited_by_count DESC NULLS LAST LIMIT 15""").show(max_width=200)

    print("\n4. Clinical trials linked to a results publication (VALIDATED_BY is subject=Article, "
          "object=ClinicalTrial; v0.2.0: RESULT role only, see CITES_BACKGROUND/HAS_DERIVED_PUBLICATION for the others)")
    con.sql("""SELECT e.object AS trial, t.name AS trial_title, n.pmid, n.name AS article_title
               FROM edges e LEFT JOIN nodes t ON t.id = e.object LEFT JOIN nodes n ON n.id = e.subject
               WHERE e.rel = 'VALIDATED_BY' LIMIT 10""").show(max_width=200)

    print("\n5. Most-cited articles within this graph (in-degree of CITES)")
    con.sql("""SELECT e.object AS article, any_value(n.name) AS title, count(*) AS cited_in_graph
               FROM edges e LEFT JOIN nodes n ON n.id = e.object
               WHERE e.rel = 'CITES' GROUP BY e.object ORDER BY cited_in_graph DESC LIMIT 10""").show(max_width=200)

    # ---------------------------------------------------------------------------------------
    # Added after real, full-scale validation (see docs/VALIDATION_RESULTS.md). Each of these
    # mirrors one of the four traversals in examples/queries.cypher.
    # ---------------------------------------------------------------------------------------

    print(f"\n6. Trial '{a.trial}' -> results publication (VALIDATED_BY, backwards) -> "
          f"citing articles that are a guideline or systematic review")
    con.sql(f"""WITH results AS (
                    SELECT e.subject AS results_pmid, e.object AS trial_id
                    FROM edges e WHERE e.rel = 'VALIDATED_BY' AND e.object = '{a.trial}'
                )
                SELECT r.trial_id, ra.name AS results_title, c.subject AS citing_pmid,
                       ca.name AS citing_title, ca.pub_types
                FROM results r
                JOIN nodes ra ON ra.id = r.results_pmid
                JOIN edges c ON c.rel = 'CITES' AND c.object = r.results_pmid
                JOIN nodes ca ON ca.id = c.subject
                WHERE list_has_any(ca.pub_types::VARCHAR[], {sql_list(GUIDELINE_OR_SYSTEMATIC_REVIEW)})
                LIMIT 50""").show(max_width=200)

    print(f"\n7. MedlinePlus topic '{a.medlineplus_topic}' -> MeSH descriptor (direct HAS_MESH) -> "
          f"one level DOWN via HAS_BROADER to narrower/child descriptors (PubMed MeSH 'explode') -> "
          f"articles ranked by MAJOR-TOPIC matches, direct-term matches outranking "
          f"hierarchy-expansion-only matches, check tags excluded")
    check_tags_sql = sql_list(CHECK_TAGS)
    con.sql(f"""WITH direct AS (
                    SELECT e.object AS mesh_id
                    FROM edges e JOIN nodes mp ON mp.id = e.subject
                    WHERE e.rel = 'HAS_MESH' AND mp.name = '{a.medlineplus_topic.replace("'", "''")}'
                ),
                direct_f AS (
                    SELECT DISTINCT d.mesh_id FROM direct d JOIN nodes m ON m.id = d.mesh_id
                    WHERE m.name NOT IN {check_tags_sql}
                ),
                -- HAS_BROADER subject=child, object=parent (verified against real data; renamed
                -- from v0.1.0's PARENT_OF, same direction), so a descriptor's CHILDREN are the
                -- edges whose OBJECT is that descriptor.
                child_f AS (
                    SELECT DISTINCT e.subject AS mesh_id
                    FROM edges e JOIN direct_f d ON d.mesh_id = e.object JOIN nodes m ON m.id = e.subject
                    WHERE e.rel = 'HAS_BROADER' AND m.name NOT IN {check_tags_sql}
                      AND e.subject NOT IN (SELECT mesh_id FROM direct_f)
                ),
                matches AS (
                    SELECT e.subject AS article_id,
                           CASE WHEN e.object IN (SELECT mesh_id FROM direct_f) THEN 1 ELSE 0 END AS is_direct
                    FROM edges e
                    WHERE e.rel = 'HAS_MESH' AND e.is_major_topic = true
                      AND e.object IN (SELECT mesh_id FROM direct_f UNION SELECT mesh_id FROM child_f)
                )
                SELECT a.pmid, a.name AS title,
                       sum(m.is_direct) AS direct_matches,
                       sum(1 - m.is_direct) AS hierarchy_matches,
                       a.cited_by_count
                FROM matches m JOIN nodes a ON a.id = m.article_id
                GROUP BY a.pmid, a.name, a.cited_by_count
                ORDER BY direct_matches DESC, hierarchy_matches DESC, a.cited_by_count DESC NULLS LAST
                LIMIT 25""").show(max_width=200)

    print(f"\n8. Article '{a.seed_pmid}' -> (CITES + shared MAJOR-TOPIC MeSH) -> "
          f"most-cited in-graph papers reachable this way")
    con.sql(f"""WITH seed_id AS (SELECT '{a.seed_pmid}' AS id),
                out_cites AS (SELECT e.object AS cand FROM edges e, seed_id WHERE e.rel='CITES' AND e.subject=seed_id.id),
                in_cites AS (SELECT e.subject AS cand FROM edges e, seed_id WHERE e.rel='CITES' AND e.object=seed_id.id),
                seed_mesh AS (SELECT e.object AS mesh_id FROM edges e, seed_id
                              WHERE e.rel='HAS_MESH' AND e.subject=seed_id.id AND e.is_major_topic=true),
                via_mesh AS (SELECT DISTINCT e.subject AS cand FROM edges e JOIN seed_mesh sm ON sm.mesh_id=e.object, seed_id
                             WHERE e.rel='HAS_MESH' AND e.is_major_topic=true AND e.subject <> seed_id.id),
                candidates AS (SELECT cand FROM out_cites UNION SELECT cand FROM in_cites UNION SELECT cand FROM via_mesh)
                SELECT c.cand AS pmid, n.name AS title, count(DISTINCT citer.subject) AS cited_in_graph
                FROM candidates c
                JOIN nodes n ON n.id = c.cand
                LEFT JOIN edges citer ON citer.rel='CITES' AND citer.object = c.cand
                GROUP BY c.cand, n.name
                ORDER BY cited_in_graph DESC
                LIMIT 25""").show(max_width=200)

    print(f"\n9. Author '{a.author_id}' -> their articles -> aggregate MAJOR-TOPIC MeSH profile")
    con.sql(f"""WITH auth_articles AS (
                    SELECT e.subject AS article_id FROM edges e
                    WHERE e.rel='AUTHORED_BY' AND e.object = '{a.author_id}'
                )
                SELECT au.name AS author, m.name AS topic, count(DISTINCT aa.article_id) AS articles
                FROM auth_articles aa
                JOIN edges hm ON hm.rel='HAS_MESH' AND hm.subject = aa.article_id AND hm.is_major_topic = true
                JOIN nodes m ON m.id = hm.object
                JOIN nodes au ON au.id = '{a.author_id}'
                GROUP BY au.name, m.name
                ORDER BY articles DESC
                LIMIT 25""").show(max_width=200)


if __name__ == "__main__":
    main()
