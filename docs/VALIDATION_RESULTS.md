# Validation results

Two validation passes are recorded in this file: a **v0.2.0 sample-scale pass** (this release,
below) and the original **v0.1.0 full-scale pass** (kept below it, unchanged, for history). The
v0.2.0 pass was NOT a full-scale re-run — it rebuilt and load-tested the sample subgraph and ran
every example query against it, using the real, validated v0.2.0 release build
(`release_out/clinical_v02`, 12,067,108 nodes / 105,758,798 edges). The v0.1.0 full-scale numbers
(full 8-shard download, full load, full dump sizing) were **not** re-measured at v0.2.0 scale —
that would be a multi-hour undertaking outside this pass's scope — so those sections below are
historical v0.1.0 measurements, not v0.2.0 claims. Numbers never invented either way.

## v0.2.0 sample-scale validation (this release, measured)

Environment: Docker Desktop (WSL2) on a Linux host, `neo4j:5-community`, run in an isolated
container on non-default host ports so as not to disturb an unrelated pre-existing `ce-kg-neo4j`
container found already bound to the default 7474/7687 ports on this shared machine (left
untouched — ownership/purpose unknown, not created by this pass).

### Bug found rebuilding the sample against the real v0.2.0 release layout

`scripts/build_sample_subgraph.py` looked for files literally named `edges__*.jsonl.gz` /
`nodes__*.jsonl.gz` directly inside `--data-dir`. The real layout — confirmed against both the
live v0.1.0 Hugging Face repo's file tree (`https://huggingface.co/api/datasets/lunas-health/
clinical-evidence-kg/tree/clinical-v0.1.0`) and the v0.2.0 release build — is `nodes/` and
`edges/` **subdirectories** containing plain `part-*.jsonl.gz` shards; no file anywhere is named
with that `nodes__`/`edges__` prefix. This script would have found **zero** files against the
real v0.1.0 download too — it is a pre-existing bug, not something introduced by v0.2.0, just
never caught because this is the first time anyone ran it against the real downloaded/exported
layout rather than a `nodes__`-renamed test fixture. Fixed by having it list `<data-dir>/nodes/`
and `<data-dir>/edges/` directly. (`scripts/kgx_to_neo4j.py`'s own `files()` already checked both
the `nodes/*.jsonl.gz` and `nodes__*.jsonl.gz` patterns, so it needed no equivalent fix.)

### Sample build (measured, real, against the real v0.2.0 release data)

`scripts/build_sample_subgraph.py --per-type-cap 20000` against the full, real v0.2.0 export
(`nodes/`, `edges/`, 105,758,798 real edge records scanned):

| Metric | Value |
|---|---:|
| Scan time | 295s (edges) + 42s (node lookup) = 337s |
| Edges kept | 295,798 — **all 18/18 relationship types present** (every type in `manifest.json counts.edges_by_type`) |
| Nodes kept | 270,864 |
| Nodes missing (referenced but not found) | **0** — every edge endpoint resolves |
| `sample_out/nodes__sample.jsonl.gz` | 26,666,822 bytes, sha256 `9e2d3ad72e022ac52d24ca65a9379950fa2c5038c90ac25b4dec3f50d10dfc8a` |
| `sample_out/edges__sample.jsonl.gz` | 19,529,850 bytes, sha256 `f37b662e4efb1e3b0578a6f17f7d7f04af8d693e579f125eb43a79406e75a9f9` |
| Combined size | 46,196,672 bytes (~44.1 MiB) |

Per-type counts (18 types, up from 16 in v0.1.0 — `HAS_RIGHTS_EVIDENCE`/`HAS_USE_GRANT` are gone;
`HAS_PMC_RECORD`/`PUBLISHED_IN` are new; `PARENT_OF`/`ANCESTOR_OF` are renamed `HAS_BROADER`/
`HAS_BROADER_ANCESTOR`): `HAS_MESH`/`AUTHORED_BY`/`CITES`/`CITES_BACKGROUND`/`VALIDATED_BY`/
`HAS_DERIVED_PUBLICATION`/`SPONSORED_BY`/`CONDUCTED_AT`/`LINKS_TO_RESOURCE`/
`RESOURCE_TRANSLATION_OF`/`HAS_BROADER`/`HAS_BROADER_ANCESTOR`/`HAS_PMC_RECORD`/`PUBLISHED_IN` all
hit the 20,000 cap; `IN_TOPIC_GROUP` 3,651, `RELATED_TOPIC` 6,246, `HAS_LANGUAGE_RESOURCE` 4,885,
`TRANSLATION_OF` 1,016 are full populations (true totals below the cap), same as v0.1.0.

### Sample load test (measured, real)

```
python scripts/kgx_to_neo4j.py --input sample_out --out neo4j_import_sample
USE_DOCKER=1 bash scripts/load_neo4j.sh neo4j_import_sample
```

| Metric | Value |
|---|---:|
| Conversion (`kgx_to_neo4j.py`) | 7.7s |
| Bulk import (`neo4j-admin database import full`) | 7.858s (`neo4j-admin`'s own "IMPORT DONE" time), 14.7s wall including Docker startup |
| Imported | **270,864 nodes / 295,798 relationships / 9,783,254 properties** — exact match to the build report |
| Bad / skipped / duplicate relationships | **0** (checked the full import log for `bad`/`skip`/`duplicate`/`error`/`warn` lines — none found) |
| Peak memory | 549.8 MiB (`neo4j-admin`'s own summary line) |
| Labels after load (`CALL db.labels()`) | 11/11: Article, Author, ClinicalTrial, ExternalResource, **Journal**, MeSHConcept, MedlinePlus, MedlinePlusGroup, **PMCRecord**, Sponsor, TrialSite |
| Relationship types after load (`CALL db.relationshipTypes()`) | 18/18: AUTHORED_BY, CITES, CITES_BACKGROUND, CONDUCTED_AT, **HAS_BROADER**, **HAS_BROADER_ANCESTOR**, HAS_DERIVED_PUBLICATION, HAS_LANGUAGE_RESOURCE, HAS_MESH, **HAS_PMC_RECORD**, IN_TOPIC_GROUP, LINKS_TO_RESOURCE, **PUBLISHED_IN**, RELATED_TOPIC, RESOURCE_TRANSLATION_OF, SPONSORED_BY, TRANSLATION_OF, VALIDATED_BY — confirmed `HAS_RIGHTS_EVIDENCE`/`HAS_USE_GRANT` genuinely absent |
| Target ("loads in about a minute") | **Met, comfortably** |

### Example queries — run against the loaded v0.2.0 sample (all of `examples/queries.cypher`, including the two new PMC/Journal queries 6e/6f)

Every statement in the updated `examples/queries.cypher` executed with **no syntax or type
errors** against the loaded sample. Result rows, where present, looked sane (asthma/MeSH queries,
`VALIDATED_BY`-backwards trial->results->citing-articles, author/MeSH aggregation, the new PMC/
Journal queries all returned real, readable rows — see the file for live examples: e.g. query 6e
returned `Pediatric Research` / `Rheumatology Oxford` articles with their PMC id and journal
name). Four queries returned **zero rows** against this particular random sample, which is
expected and not a bug: queries 5, 6a and 6b use **literal parameter values** (an author name,
an NCT id, a MedlinePlus topic name) that were originally chosen against the full v0.1.0 graph —
nothing guarantees any specific literal id lands inside a ~296K-edge random sample out of 105.8M
real edges (e.g. the seed trial for 6a, `NCT00825071`, simply isn't one of the 54,222
`ClinicalTrial` nodes this particular sample happened to keep). The file's own header comment
already tells readers to swap in ids they care about. This matches v0.1.0's own documented
behavior for these same literal-parameter queries (see the "Example queries" table below, whose
real nonzero row counts were always measured against the **full** graph, not the sample).

## v0.1.0 full-scale validation (historical — measured against the real v0.1.0 export, using the real starter package)

All numbers below are **measured**, running the real repo scripts (`scripts/quickstart.py`,
`scripts/kgx_to_neo4j.py`, `scripts/load_neo4j.sh`) exactly as shipped (plus the bug fixes
documented below, applied to those same files) against the real, published Zenodo/Hugging Face
v0.1.0 shards (not synthetic/toy data). Environment: Docker Desktop (WSL2) on a Linux host,
`neo4j:5-community` (resolves to Neo4j 5.26.32), shared with other concurrent, unrelated
workloads on the same machine — host specs and a memory-safety note are at the bottom.

## Download

| Metric | Value |
|---|---|
| Shards | 8 node + 8 edge, `nodes__nodes-w0[0-7].jsonl.gz` / `edges__edges-w0[0-7].jsonl.gz` (Zenodo layout; HF layout `nodes/*.jsonl.gz` / `edges/*.jsonl.gz` also supported by the scripts) |
| Total compressed size | 5,257,041,964 bytes (~4.90 GiB) — matches `manifest.json` `totals.bytes` exactly |
| Source | `https://zenodo.org/api/records/24011485` (public, no auth); same bytes mirrored on Hugging Face |

## Step 1: `scripts/kgx_to_neo4j.py` (KGX JSONL.gz -> Neo4j bulk-import CSVs)

Full 8-shard run, real data, measured:

| Metric | Value |
|---|---:|
| Wall time | 910.5s (~15.2 min), single-threaded, 99% CPU |
| Peak memory | tens of MB (repeatedly sampled via `ps` during the run: 17,060–24,552 KB RSS) — the converter streams one record at a time and never buffers the dataset, so this is a genuine property of the design, not a fluke of this run |
| Output | 25 GB of CSV (`nodes_*.csv` / `edges_*.csv`), one file per node label / relationship type |
| Nodes converted | 10,145,579 (exact match to `manifest.json`) |
| Edges converted | 109,661,337 (exact match to `manifest.json`) |

## Step 2: `scripts/load_neo4j.sh` (`neo4j-admin database import full`, `USE_DOCKER=1`)

| Metric | Value |
|---|---:|
| Wall time | 433s (~7.2 min) including Docker container start/stop overhead; `neo4j-admin`'s own reported import time was 7m 6s |
| Peak memory | **792.8 MiB** (reported directly by `neo4j-admin`'s own summary line) |
| Final `/data` store size | 55 GB |
| Imported | **10,145,579 nodes / 109,661,337 relationships / 975,626,574 properties** |

**10,145,579 / 109,661,337 is an exact match to `manifest.json`'s `totals.nodes` / `totals.edges`.**
Re-confirmed independently by querying the loaded graph: `MATCH (n) RETURN count(n)` ->
`10145579`; `MATCH ()-[r]->() RETURN count(r)` -> `109661337`. Per-label / per-type breakdown
(from `conversion_summary.json`, cross-checked against `CALL db.labels()` / live counts on the
loaded graph):

| Label | Count | Label | Count |
|---|---:|---|---:|
| Author | 5,134,220 | License | 76 |
| Article | 3,139,339 | RightsPolicy | 11 |
| TrialSite | 1,092,163 | | |
| ClinicalTrial | 606,482 | | |
| Sponsor | 101,306 | | |
| ExternalResource | 38,751 | | |
| MeSHConcept | 31,110 | | |
| MedlinePlus | 2,033 | | |
| MedlinePlusGroup | 88 | | |

| Relationship type | Count | Relationship type | Count |
|---|---:|---|---:|
| HAS_MESH | 42,629,950 | PARENT_OF | 42,519 |
| CITES | 30,203,219 | RESOURCE_TRANSLATION_OF | 22,573 |
| AUTHORED_BY | 21,135,333 | RELATED_TOPIC | 6,246 |
| HAS_RIGHTS_EVIDENCE | 7,218,698 | HAS_LANGUAGE_RESOURCE | 4,885 |
| HAS_USE_GRANT | 4,026,032 | IN_TOPIC_GROUP | 3,651 |
| CONDUCTED_AT | 3,153,344 | TRANSLATION_OF | 1,016 |
| SPONSORED_BY | 931,156 | | |
| ANCESTOR_OF | 185,654 | | |
| LINKS_TO_RESOURCE | 51,747 | | |
| VALIDATED_BY | 45,314 | | |

## Totals: counts vs. target

**Target (manifest.json `totals`): 10,145,579 nodes / 109,661,337 edges.**
**Measured (loaded graph, live query): 10,145,579 nodes / 109,661,337 edges.**
**Exact match. No gap to explain.**

## Bugs found in the real starter package, running it for real at full scale (historical v0.1.0 pass) — and exactly how each was fixed

The starter package had evidently never been run end-to-end against the real, full-scale v0.1.0
export before. Every one of these was invisible on a toy/small fixture and only surfaced once the
real ~10M-node / ~110M-edge data was run through it.

### 1. `scripts/kgx_to_neo4j.py` — schema sampling missed 10 of 11 node labels and 10 of 16 relationship types (the headline bug)

`sample_schema()` originally did `for p in paths: for r in read(p, per_file): ...`, i.e. it only
looked at the **first `per_file` (default 20,000) lines of each individual file** to infer which
properties each node label / relationship type has. At real scale, node records are written in
large contiguous blocks by label within each shard — e.g. one shard alone has 392,157 `Article`
records before a single `ClinicalTrial` record appears — so the 20,000-line sampling window
*never saw* 10 of the 11 node labels (every one except `Article`) or 10 of the 16 relationship
types (everything except `HAS_MESH`, `CITES`, `AUTHORED_BY`, `HAS_RIGHTS_EVIDENCE`,
`HAS_USE_GRANT`, `VALIDATED_BY` — together ~96% of all edges by volume, which is exactly why a
quick smoke test wouldn't have caught this). Every property of every unsampled label/type
silently collapsed into the single catch-all `extra` JSON string column, so e.g.
`nodes_ClinicalTrial.csv`'s header was just `id:ID,:LABEL,extra:string` instead of carrying
`nct_id`, `name`, `phase`, `overall_status`, etc. as real typed columns.

**Caught by:** querying the loaded (buggy) graph directly — `MATCH (t:ClinicalTrial) RETURN
keys(t)` returned `["extra", "id"]` only, and a `VALIDATED_BY`-driven query that should have
returned real `ClinicalTrial.nct_id` values returned `NULL` for every row instead.

**Fixed by:** scanning each file in full during sampling (no line-position cap) while still
bounding memory and per-record cost by capping samples **per label/type** — once a given
label/type has contributed `per_file` samples, further records of that label/type are skipped for
schema purposes (not re-read for schema, so the schema dicts stay small; the file still has to be
read once regardless since a rare label/type can appear anywhere). This is a real, measured cost:
conversion time rose from 742.5s (buggy, capped) to 910.5s (fixed, full scan) — judged the right
trade for correctness. Verified post-fix: every node label and every relationship type now has
its real typed columns (`nodes_ClinicalTrial.csv`, `nodes_MeSHConcept.csv`, `edges_PARENT_OF.csv`,
`edges_CONDUCTED_AT.csv`, etc. all spot-checked), and the loaded graph's `ClinicalTrial.nct_id`
etc. now resolve correctly.

### 2. `scripts/kgx_to_neo4j.py` — duplicate `biolink_predicate` CSV column

The real `AUTHORED_BY` edge records carry their own literal `biolink_predicate` field (e.g.
`biolink:has_author`, more specific than the generic `predicate` field `biolink:related_to`). The
converter's fixed output header already reserves a `biolink_predicate:string` column (sourced from
`predicate`), but `biolink_predicate` was not in `RESERVED_EDGE`, so the schema sampler *also*
emitted it as an ordinary property column — producing a CSV with **two** columns both literally
named `biolink_predicate:string`, which `neo4j-admin database import` rejects (duplicate headers).
Caught on the very first real-data smoke test (a single node+edge shard), before the full run.
Fixed by adding `biolink_predicate` to `RESERVED_EDGE` and preferring it over the generic
`predicate` for the fixed column's value (`r.get("biolink_predicate") or r.get("predicate", "")`),
so the more specific native predicate is kept rather than silently dropped.

### 3. `examples/queries.cypher` / `scripts/quickstart.py` — `VALIDATED_BY` direction assumed backwards

The starter package's query 4 (both the Cypher and the DuckDB version) assumed
`(trial)-[:VALIDATED_BY]->(article)`. The real data is the opposite:
`(article:Article)-[:VALIDATED_BY]->(trial:ClinicalTrial)` — verified directly on a raw edge
record (`subject` = `PMID:...`, `object` = `clinicaltrials:NCT...`, `source_table:
"clinical_trials_study_references"`, `reference_type: "RESULT"`). With the original direction the
query didn't error — it silently returned a `trial` column of `NULL` for every row (the pattern
still matched, just with the binding backwards). Fixed: `MATCH (t:ClinicalTrial)<-[:VALIDATED_BY]-
(a:Article)` in Cypher; swapped `subject`/`object` in the DuckDB join.

### 4. `examples/queries.cypher` — multi-line `:param` breaks under non-interactive `cypher-shell -f`

A `:param checkTags => [...]` spanning several physical lines (for readability) works fine typed
interactively into `cypher-shell`, but running the same file non-interactively via `-f file.cypher`
fails: `Failed to evaluate expression {checkTags: [...` / `Invalid input '}': expected an
expression` — the client command only consumes its first physical line. Fixed by collapsing the
40-item Check Tags list onto one line, with a comment explaining why.

### 5. `PARENT_OF`'s direction is the reverse of what its name suggests — not a code bug, a real-data semantics trap

Verified against 15 well-known MeSH pairs (e.g. "Zona Fasciculata" -[PARENT_OF]-> "Adrenal
Cortex"; a 2-hop chain "Cushing Syndrome" -[PARENT_OF]-> "Adrenocortical Hyperfunction"
-[PARENT_OF]-> "Adrenal Gland Diseases") and cross-checked against the edges' own
`parent_tree_numbers` / `child_tree_numbers` properties (the `child_tree_numbers` value is always
a longer, more specific dotted path than `parent_tree_numbers`, and that longer path always
belongs to the edge's `subject`): **`(subject)-[:PARENT_OF]->(object)` always has `subject` = the
narrower/child concept and `object` = the broader/parent concept** — backwards from what the
relationship's name implies on its own. The starter package's own query 3 ("expanded one level
down... descriptor's children") needed its arrow reversed to actually reach children
(`(child)-[:PARENT_OF]->(m)`, not `(m)-[:PARENT_OF]->(child)`), and the same correction applies to
the new MeSH-hierarchy example query below. Documented inline, with the evidence, in both
`examples/queries.cypher` and `scripts/quickstart.py`.

### 6. README — wrong node label in prose

The Quick Start section listed example node labels as "Article, MeshDescriptor, ClinicalTrial,
Author, ...". The real label (confirmed via `CALL db.labels()` and every node sample) is
`MeSHConcept`, not `MeshDescriptor`. Fixed.

## Memory / resource safety note

This load test ran on a host shared with other, unrelated, concurrent work (confirmed
independently by the environment's owner). Real measured host memory during the heaviest step
(the `neo4j-admin` bulk import) never dropped below ~35 GiB available (`free -h`), comfortably
above a 15 GiB reserve kept for the other workload throughout. The Neo4j server used afterward to
run queries and take dumps was deliberately capped with a hard Docker memory limit
(`--memory=18g`) and a reduced heap/page-cache (6 GB / 8 GB, vs. the repo's own `docker-
compose.yml` defaults of 8 GB / 16 GB sized for a dedicated machine) specifically to avoid
contending with that other workload; it was never close to its cap (peaked under 5 GiB). Two
Neo4j containers used for this testing (`ce-kg-neo4j-full`, `ce-kg-neo4j-sample`) were stopped
deliberately after use — confirmed via `docker inspect` (`OOMKilled: false` on both) to be clean
stops, not crashes.

## Example queries — real row counts against the fully-loaded graph (historical v0.1.0 full-graph run)

See `examples/queries.cypher` and `scripts/quickstart.py` for the full, runnable text. All run
against the real, fully-loaded v0.1.0 10,145,579-node / 109,661,337-edge graph (query 6a's
`PARENT_OF` references below are v0.1.0's native name for what v0.2.0 renamed to `HAS_BROADER`).
These row counts have not been re-measured against the full v0.2.0 graph (only the sample, above).

| # | Traversal | Real result |
|---|---|---|
| a | `ClinicalTrial NCT00825071` -> results publication (`VALIDATED_BY`, traversed backwards) -> citing articles that are a guideline or systematic review | **38 rows** |
| b | `MedlinePlus "Asthma"` -> direct `HAS_MESH` MeSH descriptors -> one level down via `PARENT_OF` to child descriptors -> major-topic articles, two-tier ranked (direct-term matches before child-term matches) | **16,573 distinct articles** matched (top 25 shown in the examples file) |
| c | `Article PMID:10021452` -> (`CITES` + shared major-topic MeSH) -> most-cited in-graph papers reachable this way | **32,406 candidate papers**, ranked by in-graph citation count (top 25 shown) |
| d | `Author "Barton F. Haynes" (A5051827275)` -> their articles -> aggregate major-topic MeSH profile | **206 distinct MeSH topics across 687 (article, topic) pairs** |

## Sample subgraph build + load (historical v0.1.0 numbers — see the v0.2.0 section at the top of this file for the current sample)

`scripts/build_sample_subgraph.py --per-type-cap 20000` against the full, real 8-edge-shard set:

| Metric | Value |
|---|---:|
| Scan time | 294s (edges) + 39s (node lookup) = 333s |
| Edges kept | 255,798 — **all 16/16 relationship types present** (every type in `manifest.json counts.edges_by_type`) |
| Nodes kept | 174,220 |
| Nodes missing (referenced but not found) | **0** — every edge endpoint resolves |
| `sample_out/nodes__sample.jsonl.gz` | 16,014,336 bytes, sha256 `48bc8da6a72e02a9ce5be89640daef1cf2c6aebdc092ea4e2f022f9e970381ef` |
| `sample_out/edges__sample.jsonl.gz` | 13,763,004 bytes, sha256 `b18e695281645be6ff3dcae78606e7cd515b6682616177a7ed57f7db91dfdb0f` |
| Combined size | 29,777,340 bytes (~28.4 MiB) |

**Load test**, through the exact same real pipeline (`kgx_to_neo4j.py` + `load_neo4j.sh`,
separate container so it doesn't contend with the full-scale load):

| Metric | Value |
|---|---:|
| Conversion (`kgx_to_neo4j.py`) | 5.4s |
| Bulk import (`neo4j-admin database import full`) | 7.4s (`neo4j-admin`'s own "IMPORT DONE" time), 13.4s wall including Docker container start/stop |
| Nodes / edges loaded | 174,220 / 255,798 — exact match to the build report |
| All 16 relationship types present after load | Confirmed via `CALL db.relationshipTypes()` |
| Target ("loads in about a minute") | **Met, comfortably** |

## Neo4j database dump sizing (historical v0.1.0 — measured, real — not uploaded anywhere; not re-measured for v0.2.0)

Both dumps were taken with `neo4j-admin database dump` (Neo4j 5.26.32, the version in this repo's
`docker-compose.yml`), against the stopped database (Neo4j 5 Community has no online-dump
license), via a one-off `neo4j-admin` container sharing the same data volume as the stopped
server — not uploaded or published anywhere, per this task's scope.

| Dump | Store size (source) | Dump size | SHA-256 | Dump time |
|---|---:|---:|---|---:|
| Full graph | 55 GB (`/data`, 42 files) | **9,131,222,030 bytes (8.50 GiB)** | `c7a48e25968a39db1ad4801a18005de0f0aba0ff171f0bc349e3dc383308506c` | 99.2s |
| Sample | 653.1 MiB (`/data`, 36 files) | **49,435,734 bytes (47.1 MiB)** | `c346541282d52d1802c01f26933f4273f40d7a05dbbe356fee5f58111d7d0844` | 0.5s |

### Hosting feasibility

- **Hugging Face**: no practical size concern for either file — HF routinely hosts files of this
  size (and much larger) via its LFS-backed storage. Both dumps would upload without any special
  handling.
- **Zenodo**: current documented limit, verified live on 2026-11-07 via
  `https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo`:
  **"We currently accept up to 50GB per record with a maximum of 100 files"**, with a one-time
  increase to 200 GB available on request. **Both the full (8.50 GiB) and sample (47.1 MiB) dumps
  fit comfortably under the standard 50 GB limit** — no quota increase needed for either.

**Required indexes/constraints for a restored dump**: `scripts/kgx_to_neo4j.py`'s CSV import
doesn't create any indexes itself; `examples/queries.cypher`'s `CREATE INDEX ... IF NOT EXISTS`
statements (on `Article.id`, `ClinicalTrial.id`, `MeSHConcept.id`, `MeSHConcept.name`,
`MedlinePlus.name`, `Author.id`) are the ones used for this validation and are recreated
automatically on restore since they're part of the database itself.

## Host environment (for reproducibility — v0.1.0 full-scale pass; the v0.2.0 sample pass ran on the same class of machine, see its section at the top)

24 vCPU / 62 GiB RAM (WSL2 VM), `/dev/sdf` 1007 GB (267–357 GB free at various points during this
run; shared with other, unrelated concurrent workloads), Docker Desktop 28.4.0, image
`neo4j:5-community` (resolves to Neo4j 5.26.32).
