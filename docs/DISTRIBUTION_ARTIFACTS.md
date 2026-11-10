# Distribution artifacts: sample subgraph and Neo4j dump

KGX JSON Lines (the published Zenodo/Hugging Face export) remains the **canonical, authoritative**
distribution format for the Lunas Clinical Evidence KG. The two artifacts below are convenience
layers on top of it. **Section 1 (sample subgraph) is rebuilt and measured for v0.2.1, below**
(v0.2.1 ships byte-identical node/edge data to v0.2.0 -- this release only corrects the dataset
card, so the sample was rebuilt fresh against the same data for an accurate v0.2.1-labeled record,
not reused from the v0.2.0 pass). **Section 2 (Neo4j dump sizing) is historical v0.1.0 — not
re-measured at v0.2.0/v0.2.1 scale**, since that requires a full multi-hour load this pass did not
re-run; see [VALIDATION_RESULTS.md](VALIDATION_RESULTS.md) for what was and wasn't re-measured.
**Neither artifact is uploaded anywhere by this repo or this task** — sizing/feasibility only.

## 1. Small sample subgraph (v0.2.1, measured)

A ~44 MiB slice of the real v0.2.1 export, meant to load in under a minute so someone can try the
schema and example queries before committing to the full multi-GB load.

**Self-consistency (hard requirement, verified):** every one of the 295,798 kept edges has both
its endpoint nodes present among the 270,965 kept nodes. **0 dangling references.**

**Build procedure (reproducible, real):**

```bash
python3 scripts/build_sample_subgraph.py \
  --data-dir ckg --manifest ckg/manifest.json \
  --out sample_out --per-type-cap 20000
```

`--data-dir` must contain `nodes/` and `edges/` subdirectories of `*.jsonl.gz` shards — the real
Hugging Face/Zenodo/exporter layout (fixed in this pass: the script previously looked for flat
`edges__*.jsonl.gz`/`nodes__*.jsonl.gz` files directly inside `--data-dir`, which doesn't match
the real layout and would have found zero files against the real v0.1.0 download too — see
VALIDATION_RESULTS.md's "Bug found" note). Strategy: cap each of the 18 relationship types in
`manifest.json`'s `counts.edges_by_type` at 20,000 edges (or that type's true total if smaller —
e.g. `TRANSLATION_OF` only has 1,016 edges total, so all of them are kept), scanning edge shards
until every type hits its cap or is exhausted; then pull every node referenced by a kept edge out
of the node shards. Writes `sample_out/nodes__sample.jsonl.gz` + `sample_out/edges__sample.jsonl.gz`
in the Zenodo-style flat naming convention (`{kind}__*.jsonl.gz`), so `scripts/kgx_to_neo4j.py`
and `scripts/quickstart.py` load it with no code changes, just a different `--input` directory.

**Measured build:** 284s to scan all 105,758,066 edges + 40s to resolve the 270,965 referenced
nodes = 324s total.

| File | Size | SHA-256 |
|---|---:|---|
| `nodes__sample.jsonl.gz` | 26,671,197 bytes | `918d514b00d28fdf945165e8e9c305a1a038f9fc459cf96a73a9d7d19079b75e` |
| `edges__sample.jsonl.gz` | 19,517,047 bytes | `fd1cc30f0f0834551bff3b0c2d61feed2796c2c1c3f2aa6fb5ee9b936406a469` |
| **Combined** | **46,188,244 bytes (~44.0 MiB)** | |

Per-type counts kept: AUTHORED_BY 20,000 · CITES 20,000 · CITES_BACKGROUND 20,000 · CONDUCTED_AT
20,000 · HAS_BROADER 20,000 · HAS_BROADER_ANCESTOR 20,000 · HAS_DERIVED_PUBLICATION 20,000 ·
HAS_LANGUAGE_RESOURCE 4,885 (full population) · HAS_MESH 20,000 · HAS_PMC_RECORD 20,000 ·
IN_TOPIC_GROUP 3,651 (full) · LINKS_TO_RESOURCE 20,000 · PUBLISHED_IN 20,000 · RELATED_TOPIC 6,246
(full) · RESOURCE_TRANSLATION_OF 20,000 · SPONSORED_BY 20,000 · TRANSLATION_OF 1,016 (full) ·
VALIDATED_BY 20,000. (v0.1.0 had 16 types here: no `HAS_PMC_RECORD`/`PUBLISHED_IN`; had
`HAS_RIGHTS_EVIDENCE`/`HAS_USE_GRANT`; named the MeSH-tree types `PARENT_OF`/`ANCESTOR_OF`.)

**Load + verify (measured, real, through the actual repo pipeline):**

```bash
python3 scripts/kgx_to_neo4j.py --input sample_out --out neo4j_import_sample
USE_DOCKER=1 bash scripts/load_neo4j.sh neo4j_import_sample
```

| Metric | Value |
|---|---:|
| Conversion | 8.1s |
| `neo4j-admin database import full` | 7.472s (reported), 16.7s wall incl. Docker overhead |
| Nodes / edges loaded | 270,965 / 295,798 (exact match) |
| Properties loaded | 9,784,822 |
| Peak import memory | 549.8 MiB |
| Labels present after load | 11/11, confirmed via `CALL db.labels()` |
| Relationship types present after load | 18/18, confirmed via `CALL db.relationshipTypes()` |
| Bad/skipped/duplicate relationships | 0 |

## 2. Neo4j database dump (historical v0.1.0 — sizing only, not re-measured for v0.2.0, not distributed)

A `neo4j-admin database dump` of a fully-loaded graph, so a consumer could in principle skip the
~20-minute KGX->Neo4j load and just restore a database. **This was built and measured for sizing
purposes only against v0.1.0; this task did not upload it anywhere, and did not re-run it for
v0.2.0/v0.2.1** (that requires a full-scale load, out of scope for this pass — see
VALIDATION_RESULTS.md). Since v0.2.0/v0.2.1's full graph (105,758,066 edges) is close in size to
v0.1.0's (109,661,337 edges) — fewer rights-bookkeeping edges roughly offsetting new PMC/Journal
edges — these v0.1.0 numbers are a reasonable estimate for v0.2.1's dump size, not a measurement.

**Build procedure (reproducible — used for real on both the full graph and the sample):**

```bash
# After a full load into a container mounting the same /data volume:
docker stop <container>   # Neo4j 5 Community has no online-dump license; the DB must be stopped
docker run --rm -v <data-dir>:/data neo4j:5-community \
  neo4j-admin database dump neo4j --to-path=/data/dumps --overwrite-destination=true
docker cp <container>:/data/dumps/neo4j.dump ./clinical-evidence-kg-v0.1.0.dump
sha256sum ./clinical-evidence-kg-v0.1.0.dump
```

**Measured sizes:**

| Dump | Store size (source) | Dump size | SHA-256 | Dump time |
|---|---:|---:|---|---:|
| Full graph (10,145,579 nodes / 109,661,337 relationships) | 55 GB | **9,131,222,030 bytes (8.50 GiB)** | `c7a48e25968a39db1ad4801a18005de0f0aba0ff171f0bc349e3dc383308506c` | 99.2s |
| Sample (174,220 nodes / 255,798 relationships) | 653.1 MiB | **49,435,734 bytes (47.1 MiB)** | `c346541282d52d1802c01f26933f4273f40d7a05dbbe356fee5f58111d7d0844` | 0.5s |

**Required indexes/constraints**: none are created automatically by the CSV bulk import itself;
`examples/queries.cypher` creates a small set (`Article.id`, `ClinicalTrial.id`,
`MeSHConcept.id`/`.name`, `MedlinePlus.name`, `Author.id`) that a restored dump would carry as
part of the database.

### Hosting feasibility (assessment only, nothing uploaded)

- **Hugging Face**: no practical limit concern — HF's LFS-backed storage routinely hosts files far
  larger than 8.5 GiB. Both dumps would upload without special handling.
- **Zenodo**: current documented limit, verified live 2026-11-07
  (`https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo`):
  **"up to 50GB per record with a maximum of 100 files"**, with a one-time increase to 200 GB
  available on request. **Both dumps fit comfortably under the standard 50 GB limit** — no quota
  increase needed for either.

**Sample subgraph remains the lighter, instantly-loadable convenience artifact** (28.4 MiB
source / 47.1 MiB dump, loads in under a minute); the full dump (8.50 GiB) is a measured,
real option for a later release decision, not something this task published.
