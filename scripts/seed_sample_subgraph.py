#!/usr/bin/env python3
"""Augment an existing build_sample_subgraph.py sample so every literal-parameter example in
examples/queries.cypher / scripts/quickstart.py actually returns rows, not just every
relationship TYPE.

Why this exists: build_sample_subgraph.py's per-type-cap strategy guarantees every relationship
TYPE appears at least once, but gives no guarantee that any one specific literal id (a named
author, a named trial, a named MedlinePlus topic, a named seed article) survives the cap. Three
example queries use such literals and measured zero rows against an unseeded sample -- see
docs/VALIDATION_RESULTS.md's "sample zero-row" note: the author-name search (query 5), the
trial-literal guideline lookup (query 6a), and the MedlinePlus topic lookup (query 6b).

This is the real script used to fix that (this exact code, run for real -- see
docs/VALIDATION_RESULTS.md for the measured before/after row counts). It uses DuckDB to resolve
each literal seed's real neighborhood quickly against a one-time Parquet cache of the full
release, then does two full raw-line extraction passes (edges, then nodes) over the real
gzipped shards so every added record keeps 100% of its original fields -- nothing is
reconstructed from a trimmed column set.

Usage (run AFTER build_sample_subgraph.py, against the same real release dir and the sample it
wrote; needs `pip install duckdb`):
    python3 scripts/seed_sample_subgraph.py --data-dir ckg --sample-dir sample_out
    python3 scripts/seed_sample_subgraph.py --data-dir ckg --sample-dir sample_out --parquet-cache /tmp/seed_cache
"""
import argparse
import gzip
import json
import os
import time

try:
    import duckdb
except ImportError:
    raise SystemExit("pip install duckdb")

# Exact literals used by examples/queries.cypher and scripts/quickstart.py's own --author-id /
# --trial / --medlineplus-topic / --seed-pmid defaults. Change these if you re-seed for different
# literals.
AUTHOR_ID = "lunasai:openalex_author.A5051827275"        # query 6d/9 (id-based)
AUTHOR_NAME_SUBSTRING = "Deveza"                          # query 5 (name CONTAINS)
TRIAL_ID = "clinicaltrials:NCT00825071"                   # query 6a/6
MEDLINEPLUS_NAME = "Asthma"                               # query 6b/7
SEED_ARTICLE_ID = "PMID:10021452"                         # query 6c/8

HAYNES_ARTICLE_CAP = 50
GUIDELINE_PUB_TYPES = ["Guideline", "Practice Guideline", "Systematic Review"]
CITING_CAP_PER_RESULTS_ARTICLE = 20
MESH_HIERARCHY_EDGE_CAP = 150
VIA_MESH_EDGE_CAP = 150

NODE_COLS = {"id": "VARCHAR", "category": "JSON", "name": "VARCHAR", "lunasai_labels": "JSON",
             "pmid": "VARCHAR", "pmcid": "VARCHAR", "year": "VARCHAR", "journal": "VARCHAR",
             "cited_by_count": "BIGINT", "pub_types": "JSON", "mesh_major_topics": "JSON"}
EDGE_COLS = {"id": "VARCHAR", "subject": "VARCHAR", "predicate": "VARCHAR", "object": "VARCHAR",
             "original_predicate": "VARCHAR", "lunasai_layer": "VARCHAR", "knowledge_level": "VARCHAR",
             "agent_type": "VARCHAR", "is_major_topic": "BOOLEAN"}


def reader(pat, cols):
    spec = "{" + ", ".join(f"'{k}': '{v}'" for k, v in cols.items()) + "}"
    return (f"read_json('{pat}', format='newline_delimited', columns={spec}, "
            f"ignore_errors=true, maximum_object_size=104857600)")


def lst(xs):
    return "(" + ",".join("'" + x.replace("'", "''") + "'" for x in xs) + ")"


def sql_list(xs):
    return "[" + ",".join("'" + x.replace("'", "''") + "'" for x in xs) + "]"


def extract_full_lines(shard_dir, want_ids, label):
    """Scan shard_dir's *.jsonl.gz files once, returning {id: raw_line} for every id in want_ids
    that was found (full original JSON preserved, nothing reconstructed)."""
    if not want_ids:
        return {}
    found = {}
    files = sorted(f for f in os.listdir(shard_dir) if f.endswith(".jsonl.gz"))
    t0 = time.time()
    scanned = 0
    for fn in files:
        if len(found) >= len(want_ids):
            break
        with gzip.open(os.path.join(shard_dir, fn), "rt", encoding="utf-8") as fh:
            for line in fh:
                scanned += 1
                s = line.strip()
                if not s:
                    continue
                rec = json.loads(s)
                if rec["id"] in want_ids and rec["id"] not in found:
                    found[rec["id"]] = s
        if len(found) >= len(want_ids):
            break
    print(f"  [{label}] scanned {scanned:,} records in {time.time()-t0:.0f}s; "
          f"found {len(found):,}/{len(want_ids):,}")
    missing = want_ids - set(found.keys())
    if missing:
        print(f"  [{label}] WARNING: {len(missing)} ids not found: {list(missing)[:5]}")
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, help="dir containing nodes/ and edges/ shards (the real release)")
    ap.add_argument("--sample-dir", required=True, help="existing sample dir written by build_sample_subgraph.py (updated in place)")
    ap.add_argument("--parquet-cache", default=None, help="dir to write/reuse nodes.parquet+edges.parquet for fast resolution (default: a temp dir, not reused across runs)")
    args = ap.parse_args()

    con = duckdb.connect()
    con.sql("SET preserve_insertion_order=false")
    nsrc, esrc = reader(os.path.join(args.data_dir, "nodes", "*.jsonl.gz"), NODE_COLS), \
                 reader(os.path.join(args.data_dir, "edges", "*.jsonl.gz"), EDGE_COLS)
    if args.parquet_cache:
        os.makedirs(args.parquet_cache, exist_ok=True)
        np_, ep = os.path.join(args.parquet_cache, "nodes.parquet"), os.path.join(args.parquet_cache, "edges.parquet")
        if not os.path.exists(np_):
            print("writing nodes.parquet cache ...", flush=True)
            con.sql(f"COPY (SELECT * FROM {nsrc}) TO '{np_}' (FORMAT parquet)")
        if not os.path.exists(ep):
            print("writing edges.parquet cache ... (one pass over the full edge set)", flush=True)
            con.sql(f"COPY (SELECT * FROM {esrc}) TO '{ep}' (FORMAT parquet)")
        nsrc, esrc = f"read_parquet('{np_}')", f"read_parquet('{ep}')"
    con.sql(f"CREATE VIEW nodes AS SELECT * FROM {nsrc}")
    con.sql(f"""CREATE VIEW edges AS SELECT *,
                regexp_extract(original_predicate, '[.:]([A-Za-z_]+)$', 1) AS rel FROM {esrc}""")

    # --- Resolve seed ids ---
    medlineplus_id = con.sql(f"""SELECT id FROM nodes WHERE json_extract_string(lunasai_labels,'$[0]')='MedlinePlus'
                                  AND lower(name)=lower('{MEDLINEPLUS_NAME}')""").fetchall()[0][0]
    deveza_ids = [r[0] for r in con.sql(f"""SELECT id FROM nodes WHERE json_extract_string(lunasai_labels,'$[0]')='Author'
                                             AND name ILIKE '%{AUTHOR_NAME_SUBSTRING}%'""").fetchall()]
    results_pmids = [r[0] for r in con.sql(f"SELECT subject FROM edges WHERE rel='VALIDATED_BY' AND object='{TRIAL_ID}'").fetchall()]
    direct_mesh = [r[0] for r in con.sql(f"SELECT object FROM edges WHERE rel='HAS_MESH' AND subject='{medlineplus_id}'").fetchall()]
    child_mesh = [r[0] for r in con.sql(f"SELECT subject FROM edges WHERE rel='HAS_BROADER' AND object IN {lst(direct_mesh)}").fetchall()] if direct_mesh else []
    seed_mesh = [r[0] for r in con.sql(f"SELECT object FROM edges WHERE rel='HAS_MESH' AND subject='{SEED_ARTICLE_ID}' AND is_major_topic").fetchall()]
    print(f"MedlinePlus '{MEDLINEPLUS_NAME}' -> {medlineplus_id}")
    print(f"Authors matching '{AUTHOR_NAME_SUBSTRING}' -> {deveza_ids}")
    print(f"Trial {TRIAL_ID} results articles -> {results_pmids}")
    print(f"MedlinePlus direct mesh -> {direct_mesh}, children -> {child_mesh}")
    print(f"Seed article {SEED_ARTICLE_ID} major-topic mesh -> {seed_mesh}")

    ids = set()

    def add(rows):
        ids.update(r[0] for r in rows)

    # Deveza authors: all AUTHORED_BY + their articles' major-topic HAS_MESH
    deveza_authored = con.sql(f"SELECT id, subject FROM edges WHERE rel='AUTHORED_BY' AND object IN {lst(deveza_ids)}").fetchall() if deveza_ids else []
    add([(r[0],) for r in deveza_authored])
    deveza_articles = {r[1] for r in deveza_authored}
    if deveza_articles:
        add(con.sql(f"SELECT id FROM edges WHERE rel='HAS_MESH' AND is_major_topic AND subject IN {lst(deveza_articles)}").fetchall())

    # Haynes (id-based) author: capped AUTHORED_BY + their articles' major-topic HAS_MESH
    haynes_authored = con.sql(f"SELECT id, subject FROM edges WHERE rel='AUTHORED_BY' AND object='{AUTHOR_ID}' ORDER BY subject LIMIT {HAYNES_ARTICLE_CAP}").fetchall()
    add([(r[0],) for r in haynes_authored])
    haynes_articles = {r[1] for r in haynes_authored}
    if haynes_articles:
        add(con.sql(f"SELECT id FROM edges WHERE rel='HAS_MESH' AND is_major_topic AND subject IN {lst(haynes_articles)}").fetchall())

    # Trial: VALIDATED_BY + CITES into results articles, prioritising guideline/systematic-review citers
    add(con.sql(f"SELECT id FROM edges WHERE rel='VALIDATED_BY' AND object='{TRIAL_ID}'").fetchall())
    if results_pmids:
        add(con.sql(f"""
            WITH citing AS (
              SELECT c.id, c.object AS results_pmid, c.subject AS citing_pmid,
                     list_has_any(n.pub_types::VARCHAR[], {sql_list(GUIDELINE_PUB_TYPES)}) AS is_gsr
              FROM edges c JOIN nodes n ON n.id = c.subject
              WHERE c.rel='CITES' AND c.object IN {lst(results_pmids)}
            )
            SELECT id FROM citing QUALIFY row_number() OVER (
              PARTITION BY results_pmid ORDER BY is_gsr DESC, citing_pmid
            ) <= {CITING_CAP_PER_RESULTS_ARTICLE}""").fetchall())

    # MedlinePlus: direct HAS_MESH + HAS_BROADER children + major-topic HAS_MESH into direct+child, capped
    add(con.sql(f"SELECT id FROM edges WHERE rel='HAS_MESH' AND subject='{medlineplus_id}'").fetchall())
    if direct_mesh:
        add(con.sql(f"SELECT id FROM edges WHERE rel='HAS_BROADER' AND object IN {lst(direct_mesh)}").fetchall())
    full_mesh = direct_mesh + child_mesh
    if full_mesh:
        add(con.sql(f"""SELECT id FROM edges WHERE rel='HAS_MESH' AND is_major_topic AND object IN {lst(full_mesh)}
                         ORDER BY subject LIMIT {MESH_HIERARCHY_EDGE_CAP}""").fetchall())

    # Seed article: CITES in/out + own major-topic HAS_MESH + viaMesh (other articles sharing it), capped
    add(con.sql(f"SELECT id FROM edges WHERE rel='CITES' AND (subject='{SEED_ARTICLE_ID}' OR object='{SEED_ARTICLE_ID}')").fetchall())
    add(con.sql(f"SELECT id FROM edges WHERE rel='HAS_MESH' AND subject='{SEED_ARTICLE_ID}' AND is_major_topic").fetchall())
    if seed_mesh:
        add(con.sql(f"""SELECT id FROM edges WHERE rel='HAS_MESH' AND is_major_topic AND object IN {lst(seed_mesh)}
                         AND subject <> '{SEED_ARTICLE_ID}' ORDER BY subject LIMIT {VIA_MESH_EDGE_CAP}""").fetchall())

    print(f"TOTAL seed edge ids wanted: {len(ids)}")

    # --- Merge into the existing sample ---
    edges_sample_path = os.path.join(args.sample_dir, "edges__sample.jsonl.gz")
    nodes_sample_path = os.path.join(args.sample_dir, "nodes__sample.jsonl.gz")
    with gzip.open(edges_sample_path, "rt") as f:
        base_edge_lines = [l.rstrip("\n") for l in f]
    with gzip.open(nodes_sample_path, "rt") as f:
        base_node_lines = [l.rstrip("\n") for l in f]
    base_edge_ids = {json.loads(l)["id"] for l in base_edge_lines}
    base_node_ids = {json.loads(l)["id"] for l in base_node_lines}
    new_edge_ids = ids - base_edge_ids
    print(f"Baseline sample: {len(base_edge_lines):,} edges / {len(base_node_lines):,} nodes; "
          f"{len(new_edge_ids):,} genuinely new edges to extract.")

    found_edges = extract_full_lines(os.path.join(args.data_dir, "edges"), new_edge_ids, "edges")
    needed_node_ids = set()
    for line in found_edges.values():
        rec = json.loads(line)
        needed_node_ids.add(rec["subject"])
        needed_node_ids.add(rec["object"])
    new_node_ids = needed_node_ids - base_node_ids
    found_nodes = extract_full_lines(os.path.join(args.data_dir, "nodes"), new_node_ids, "nodes")

    final_edge_lines = base_edge_lines + list(found_edges.values())
    final_node_lines = base_node_lines + list(found_nodes.values())
    final_node_ids = base_node_ids | set(found_nodes.keys())
    dangling = sum(1 for l in final_edge_lines
                   if json.loads(l)["subject"] not in final_node_ids or json.loads(l)["object"] not in final_node_ids)
    print(f"Final: {len(final_edge_lines):,} edges / {len(final_node_lines):,} nodes; dangling edges: {dangling}")

    with gzip.open(edges_sample_path, "wt", encoding="utf-8") as f:
        for l in final_edge_lines:
            f.write(l + "\n")
    with gzip.open(nodes_sample_path, "wt", encoding="utf-8") as f:
        for l in final_node_lines:
            f.write(l + "\n")

    import collections
    def rel_of(line):
        rec = json.loads(line)
        orig = rec.get("original_predicate") or ""
        if ":" in orig:
            orig = orig.split(":", 1)[1]
        if "." in orig:
            orig = orig.rsplit(".", 1)[-1]
        return orig.upper()
    type_counts = collections.Counter(rel_of(l) for l in final_edge_lines)
    report = {
        "edges_kept": len(final_edge_lines),
        "edges_by_type": dict(type_counts),
        "nodes_kept": len(final_node_lines),
        "nodes_missing": dangling,
        "seeded": True,
        "seed_additions": {"new_edges_added": len(found_edges), "new_nodes_added": len(found_nodes)},
    }
    with open(os.path.join(args.sample_dir, "sample_build_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
