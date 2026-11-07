# Validation results — measured against the real v0.1.0 export

All numbers below are **measured**, on the real, published Zenodo v0.1.0
shards (not synthetic/toy data), unless explicitly marked "estimated" with
the reasoning for the extrapolation. Environment: Docker Desktop on a Linux
host, Neo4j `5.24-community` + APOC, 24 vCPU / 62 GiB RAM available to Docker,
heap 2G->4G / page cache 2G configured in `docker/docker-compose.yml`.

## Download

| Metric | Value |
|---|---|
| Shards | 8 node + 8 edge, `nodes__nodes-w0[0-7].jsonl.gz` / `edges__edges-w0[0-7].jsonl.gz` |
| Total compressed size | 5,257,041,964 bytes (~4.9 GiB) — matches `manifest.json` `totals.bytes` exactly |
| Source | `https://zenodo.org/api/records/24011485` (public, no auth) |

## One-shard smoke test (--sample path: smallest node shard + smallest edge shard)

<!-- filled in after the sample-shard load test completes -->

## Full-scale load

<!-- filled in after the full 8+8 shard load completes -->

## Fixes required to load the real data

1. **Edge MERGE key.** Original design merged edges on `(subject, rel_type,
   object)`. The real export has legitimate parallel edges of the same type
   between the same two nodes, distinguished only by properties (e.g.
   multiple `HAS_RIGHTS_EVIDENCE` edges per `(Article, RightsPolicy)` pair,
   one per `component`: `metadata`, `title`, ...). Merging on identity alone
   silently collapsed these into a single relationship. Fixed by merging on
   the edge's own globally-unique `id` (`urn:uuid:...`) instead — see
   `scripts/load_kgx_to_neo4j.py`.
2. **Edge-endpoint lookup performance.** `MATCH (s {id: ...})` with no label
   forces a full node scan on Neo4j Community (no label-free index exists).
   Fixed by adding an extra `KGXNode` label to every node and a uniqueness
   constraint on it, so edge loading does `MATCH (s:KGXNode {id: ...})`
   against an index.
3. (Additional fixes found during the full-scale run, if any, recorded here.)

## Sample subgraph build

<!-- filled in after build_sample_subgraph.py runs -->

## Neo4j dump investigation

<!-- filled in after the dump-size investigation -->
