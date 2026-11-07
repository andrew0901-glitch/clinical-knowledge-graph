#!/usr/bin/env python3
"""Load Lunas Clinical Evidence KG v0.1.0 KGX JSON-Lines shards into Neo4j 5.

KGX node record shape (observed on the real v0.1.0 export):
    {
      "id": "PMID:10203632",                 // globally-unique CURIE
      "category": ["biolink:Article"],
      "name": "...",
      "lunasai_labels": ["Article"],          // Neo4j label(s) to apply
      ... many more flat scalar/list properties ...
    }

KGX edge record shape:
    {
      "id": "urn:uuid:...",                   // globally-unique edge id
      "subject": "PMID:10203632",
      "predicate": "biolink:related_to",
      "object": "PMID:20012345",
      "original_predicate": "lunasai:vocab.CITES",   // native Neo4j relationship type
      "category": ["biolink:Association"],
      ... provenance / evidence properties ...
    }

The native Neo4j relationship type is derived from `original_predicate`
(stripping any `lunasai:vocab.` prefix) when present, falling back to the
upper-cased, `biolink:`-stripped `predicate` otherwise.

Every node additionally gets an extra `KGXNode` label so edge-loading lookups
(`MATCH (s:KGXNode {id: ...})`) hit a label-scoped index instead of a full
node scan -- Neo4j Community has no label-free index. Edges are MERGE-matched
on the KGX edge's own globally-unique `id` (an URN/UUID, NOT
subject+predicate+object) because the real export legitimately has parallel
edges of the same type between the same two nodes distinguished only by
properties (e.g. multiple HAS_RIGHTS_EVIDENCE edges per Article x
RightsPolicy pair, one per `component`). Merging on (subject, rel_type,
object) alone silently collapsed those into one edge during validation --
see docs/VALIDATION_RESULTS.md.

Performance note: an earlier version used apoc.merge.node / apoc.merge.
relationship per row inside UNWIND. On the real data that measured ~5-6k
edges/sec -- a full 109M-edge load would have taken ~5+ hours. Per-row
procedure-call overhead inside UNWIND is the cause. This version groups rows
by (label-set) / (relationship type) in Python and issues one native Cypher
MERGE per group per batch, with the label/type name spliced into the query
text (validated against a strict allow-list regex first, then only ever
drawn from the finite, known set of labels/types in this export -- never
from unvalidated free text) instead of going through APOC. This is roughly
an order of magnitude faster -- see docs/VALIDATION_RESULTS.md for the
measured before/after numbers.

APOC is still enabled in docker-compose.yml (harmless, handy for ad hoc
exploration) but is no longer required by this script.

Usage:
    python3 load_kgx_to_neo4j.py --data-dir ../data --uri bolt://localhost:7687 \
        --user neo4j --password clinicalevidence
"""
import argparse
import gzip
import json
import os
import re
import sys
import time
from collections import defaultdict

from neo4j import GraphDatabase

BATCH_SIZE = 5000

CONSTRAINTS = [
    "CREATE CONSTRAINT kgxnode_id IF NOT EXISTS FOR (n:KGXNode) REQUIRE n.id IS UNIQUE",
]

RESERVED_NODE_KEYS = {"id", "lunasai_labels"}
RESERVED_EDGE_KEYS = {"subject", "object", "id"}

_SAFE_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def safe_ident(name):
    """Validate a label/relationship-type name before splicing it into Cypher text.
    Only ever called with values drawn from this export's finite, known
    vocabulary (node lunasai_labels / derived relationship types) -- never
    from arbitrary external input."""
    if not _SAFE_IDENT.match(name):
        raise ValueError(f"unsafe identifier for Cypher splice: {name!r}")
    return name


def open_jsonl_gz(path):
    return gzip.open(path, "rt", encoding="utf-8")


def iter_records(path):
    with open_jsonl_gz(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def derive_rel_type(rec):
    orig = rec.get("original_predicate")
    if orig:
        # strip a "lunasai:vocab." (or any single-colon-namespace) prefix
        if ":" in orig:
            orig = orig.split(":", 1)[1]
        if "." in orig:
            orig = orig.rsplit(".", 1)[-1]
        return orig.upper()
    pred = rec.get("predicate", "related_to")
    if ":" in pred:
        pred = pred.split(":", 1)[1]
    return pred.upper()


def node_labels(rec):
    labels = rec.get("lunasai_labels") or []
    if not labels:
        # fall back to stripped biolink category, e.g. "biolink:Article" -> "Article"
        cats = rec.get("category") or []
        labels = [c.split(":", 1)[1] for c in cats if ":" in c]
    labels = list(dict.fromkeys(list(labels) + ["KGXNode"]))  # dedup, keep order
    return tuple(labels)


def node_row(rec):
    props = {k: v for k, v in rec.items() if k not in RESERVED_NODE_KEYS}
    props["id"] = rec["id"]
    return {"id": rec["id"], "props": _clean_props(props)}


def edge_row(rec):
    # rec["id"] is the KGX edge's own globally-unique id -- used as the merge
    # key so legitimate parallel edges of the same type between the same two
    # nodes (distinguished only by properties) are not collapsed into one.
    props = {k: v for k, v in rec.items() if k not in RESERVED_EDGE_KEYS}
    props["kgx_id"] = rec["id"]
    return {
        "subject": rec["subject"],
        "object": rec["object"],
        "edge_id": rec["id"],
        "props": _clean_props(props),
    }


def _clean_props(props):
    # Neo4j properties can't be nested maps; flatten dict values to JSON strings,
    # drop None, keep lists of scalars as-is (Neo4j supports homogeneous arrays).
    out = {}
    for k, v in props.items():
        if v is None:
            continue
        if isinstance(v, dict):
            out[k] = json.dumps(v, sort_keys=True)
        elif isinstance(v, list):
            if all(isinstance(x, (str, int, float, bool)) for x in v):
                out[k] = v
            else:
                out[k] = json.dumps(v, sort_keys=True)
        else:
            out[k] = v
    return out


def node_query_for_labels(labels):
    label_str = "".join(f":`{safe_ident(l)}`" for l in labels)
    return f"""
UNWIND $rows AS row
MERGE (n{label_str} {{id: row.id}})
SET n += row.props
"""


def edge_query_for_type(rel_type):
    t = safe_ident(rel_type)
    return f"""
UNWIND $rows AS row
MATCH (s:KGXNode {{id: row.subject}})
MATCH (o:KGXNode {{id: row.object}})
MERGE (s)-[r:`{t}` {{id: row.edge_id}}]->(o)
SET r += row.props
"""


def load_nodes(session, path, batch_size=BATCH_SIZE):
    groups = defaultdict(list)
    query_cache = {}
    count = 0
    t0 = time.time()

    def flush(labels):
        rows = groups[labels]
        if not rows:
            return
        q = query_cache.get(labels)
        if q is None:
            q = node_query_for_labels(labels)
            query_cache[labels] = q
        session.run(q, rows=rows)
        groups[labels] = []

    for rec in iter_records(path):
        labels = node_labels(rec)
        groups[labels].append(node_row(rec))
        count += 1
        if len(groups[labels]) >= batch_size:
            flush(labels)
    for labels in list(groups.keys()):
        flush(labels)

    dt = time.time() - t0
    print(f"  {os.path.basename(path)}: {count:,} nodes in {dt:.1f}s ({count/max(dt,0.01):.0f}/s)")
    return count


def load_edges(session, path, batch_size=BATCH_SIZE):
    groups = defaultdict(list)
    query_cache = {}
    count = 0
    t0 = time.time()

    def flush(rel_type):
        rows = groups[rel_type]
        if not rows:
            return
        q = query_cache.get(rel_type)
        if q is None:
            q = edge_query_for_type(rel_type)
            query_cache[rel_type] = q
        session.run(q, rows=rows)
        groups[rel_type] = []

    for rec in iter_records(path):
        rel_type = derive_rel_type(rec)
        groups[rel_type].append(edge_row(rec))
        count += 1
        if len(groups[rel_type]) >= batch_size:
            flush(rel_type)
    for rel_type in list(groups.keys()):
        flush(rel_type)

    dt = time.time() - t0
    print(f"  {os.path.basename(path)}: {count:,} edges in {dt:.1f}s ({count/max(dt,0.01):.0f}/s)")
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--uri", default="bolt://localhost:7687")
    ap.add_argument("--user", default="neo4j")
    ap.add_argument("--password", required=True)
    ap.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = ap.parse_args()

    node_files = sorted(f for f in os.listdir(args.data_dir)
                         if f.startswith("nodes__") and f.endswith(".jsonl.gz"))
    edge_files = sorted(f for f in os.listdir(args.data_dir)
                         if f.startswith("edges__") and f.endswith(".jsonl.gz"))

    if not node_files and not edge_files:
        print("No shard files found in --data-dir. Run download_shards.py first.", file=sys.stderr)
        sys.exit(1)

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    total_nodes = 0
    total_edges = 0
    t0 = time.time()
    with driver.session() as session:
        for stmt in CONSTRAINTS:
            session.run(stmt)

        print(f"Loading {len(node_files)} node shard(s)...")
        for nf in node_files:
            total_nodes += load_nodes(session, os.path.join(args.data_dir, nf), args.batch_size)

        print(f"Loading {len(edge_files)} edge shard(s)...")
        for ef in edge_files:
            total_edges += load_edges(session, os.path.join(args.data_dir, ef), args.batch_size)

    dt = time.time() - t0
    print(f"\nDone. {total_nodes:,} nodes, {total_edges:,} edges loaded in {dt:.1f}s.")
    driver.close()


if __name__ == "__main__":
    main()
