# Lunas Clinical Evidence Knowledge Graph

Documentation, loaders and examples for the **Lunas Clinical Evidence KG**, a public, provenance-aware knowledge graph linking biomedical literature, clinical trials, controlled vocabulary and patient information. Published by Lunas Health (LunasAI LLC).

**This repository holds no graph data.** The data lives here:

| | Where | Licence |
|---|---|---|
| Core graph v0.1.0 | Hugging Face [`lunas-health/clinical-evidence-kg`](https://huggingface.co/datasets/lunas-health/clinical-evidence-kg) (tag `clinical-v0.1.0`) · Zenodo [10.5281/zenodo.24011485](https://doi.org/10.5281/zenodo.24011485) | CC0 1.0 |
| Core graph v0.2.0 | Hugging Face `lunas-health/clinical-evidence-kg` (tag `clinical-v0.2.0`) · Zenodo concept DOI [10.5281/zenodo.24011485](https://doi.org/10.5281/zenodo.24011485) (new version DOI <!-- TODO v0.2.0 DOI: fill in after Zenodo publish --> pending) | CC0 1.0 |
| JEV evidence annotations (sidecar) | Zenodo [10.5281/zenodo.24012855](https://doi.org/10.5281/zenodo.24012855) · also in the Hugging Face repo | Not CC0: rights reserved by LunasAI LLC; model predictions; no model training |

v0.2.0 has not been published yet as of this writing (Zenodo/Hugging Face upload pending); the row above states what it will be, not a live link. The JEV sidecar is unchanged for v0.2.0 -- v0.2.0 does not ship a regenerated JEV file, so the v0.1.0 JEV record above still applies as-is.

## What is in v0.2.0

12,067,108 nodes and 105,758,798 edges in [KGX](https://github.com/biolink/kgx) JSON Lines, with [Biolink](https://biolink.github.io/biolink-model/) categories and predicates. Six source families: PubMed (with MeSH indexing), OpenAlex (citations, authorship), MeSH (with hierarchy), ClinicalTrials.gov, MedlinePlus, and **PMC/Journal (new in v0.2.0)**. The v0.1.0 `ctgov_publications.jsonl` sidecar file no longer exists as a separate thing -- its content is now natively absorbed into three typed edges inside the main graph (`VALIDATED_BY`/`CITES_BACKGROUND`/`HAS_DERIVED_PUBLICATION`; see [docs/DATA_NOTES.md](docs/DATA_NOTES.md)). The JEV annotations sidecar still travels separately, unchanged from v0.1.0. Read [docs/DATA_NOTES.md](docs/DATA_NOTES.md) before analysing.

<details>
<summary>What was in v0.1.0 (10,145,579 nodes / 109,661,337 edges, five source families)</summary>

v0.1.0 did not have PMC/Journal, had a single `VALIDATED_BY` type that mixed all ClinicalTrials.gov reference roles together (45,314 edges), had `HAS_RIGHTS_EVIDENCE`/`HAS_USE_GRANT` rights-bookkeeping edges (~11.2M), and named the MeSH-tree edges `PARENT_OF`/`ANCESTOR_OF`. See the sections below for what changed.

</details>

## Quick start

### 1. Download

```bash
pip install -U huggingface_hub duckdb
hf download lunas-health/clinical-evidence-kg --repo-type dataset \
  --revision clinical-v0.2.0 --local-dir ckg          # pending publish; use clinical-v0.1.0 for the current live release
```

Or download the Zenodo record; the scripts accept either layout.

### 2. Explore in Python (no database)

```bash
python scripts/quickstart.py --input ckg                 # counts, a MeSH query, trials, most-cited
python scripts/quickstart.py --input ckg --mesh "Hypertension" --parquet   # Parquet makes reruns fast
```

DuckDB reads the gzipped files directly. `--parquet` writes `nodes.parquet` and `edges.parquet` once (one pass over the edges) and queries those afterwards.

### 3. Load into Neo4j 5

```bash
python scripts/kgx_to_neo4j.py --input ckg --out neo4j_import
USE_DOCKER=1 bash scripts/load_neo4j.sh neo4j_import      # or: bash scripts/load_neo4j.sh neo4j_import  (local neo4j-admin)
docker compose up -d                                      # http://localhost:7474
```

Then try [examples/queries.cypher](examples/queries.cypher). Node labels are the native Lunas labels (Article, MeSHConcept, ClinicalTrial, Author, PMCRecord, Journal, ...) and relationship types the native types (HAS_MESH, CITES, AUTHORED_BY, VALIDATED_BY, CITES_BACKGROUND, HAS_DERIVED_PUBLICATION, HAS_BROADER, HAS_BROADER_ANCESTOR, HAS_PMC_RECORD, PUBLISHED_IN, ...). Biolink categories and predicates are kept as properties.

**Resources (measured, real, full-scale against v0.1.0 -- not an estimate; see [docs/VALIDATION_RESULTS.md](docs/VALIDATION_RESULTS.md) for the full breakdown). Not yet re-measured at v0.2.0's full scale** (v0.2.0's sample-scale load test below is re-measured; the full ~12M-node / ~106M-edge download is somewhat smaller in edge count than v0.1.0's ~110M, since dropping the ~11.2M rights-bookkeeping edges outweighs adding PMC/Journal, so these v0.1.0 numbers are a reasonable but unverified estimate for v0.2.0, not a measurement):

| Step | Wall time | Peak memory | Disk |
|---|---:|---:|---:|
| `kgx_to_neo4j.py` (KGX -> CSV) | ~15.2 min | tens of MB (pure streaming, single-threaded) | 25 GB CSV output |
| `load_neo4j.sh` (`neo4j-admin database import full`) | ~7.2 min | 793 MiB (neo4j-admin's own report) | 55 GB final `/data` store |
| **Total load** | **~22.5 min** | **under 1 GB for conversion+import** | **~85 GB peak** (4.9 GiB download + 25 GB CSV + 55 GB store, coexisting briefly; the 25 GB CSV dir can be deleted once import succeeds, leaving 55 GB) |

The import itself is lightweight; **the real cost is disk, not RAM.** Running the server afterward to query the graph is the one step that benefits from real memory: this repo's `docker-compose.yml` configures 8 GB heap / 16 GB page cache (~32 GB with OS overhead) as a comfortable default for a dedicated machine; the example queries in this repo ran fine against as little as 6 GB heap / 8 GB page cache on a shared host. Reserve disk headroom beyond the ~55 GB final store size -- a prior run on a shared host hit a genuine "no space left on device" mid-import when the *host's* disk (shared with unrelated processes) filled up; that is a shared-disk risk, not something this import needs on its own. **v0.2.0 removed the rights-bookkeeping edges entirely** (`HAS_RIGHTS_EVIDENCE`/`HAS_USE_GRANT` no longer exist in the graph at all) -- there is nothing of that kind left to `--exclude-type`.

### 4. Try the sample subgraph first (loads in under a minute)

A self-consistent ~44 MiB slice of the real v0.2.0 export: every one of the 18 relationship types present at least once (capped at 20,000 edges per type, or that type's true total if smaller), every node referenced by a kept edge included (0 dangling references), same KGX file-naming convention as the full download so the same scripts load it unchanged. Rebuilt from the real v0.2.0 release data; previously this was a ~28 MiB / 174,220-node / 255,798-edge slice of v0.1.0 (16 relationship types).

| File | Size | SHA-256 |
|---|---:|---|
| `sample_out/nodes__sample.jsonl.gz` | 26,666,822 bytes | `9e2d3ad72e022ac52d24ca65a9379950fa2c5038c90ac25b4dec3f50d10dfc8a` |
| `sample_out/edges__sample.jsonl.gz` | 19,529,850 bytes | `f37b662e4efb1e3b0578a6f17f7d7f04af8d693e579f125eb43a79406e75a9f9` |

270,864 nodes / 295,798 edges. Build it yourself with `scripts/build_sample_subgraph.py` (see [docs/DISTRIBUTION_ARTIFACTS.md](docs/DISTRIBUTION_ARTIFACTS.md)), or load a copy you already have:

```bash
python scripts/kgx_to_neo4j.py --input sample_out --out neo4j_import_sample
USE_DOCKER=1 bash scripts/load_neo4j.sh neo4j_import_sample
```

Measured against the real v0.2.0 sample: conversion 7.7s + `neo4j-admin` import 7.9s (270,864 nodes / 295,798 relationships / 9,783,254 properties, 0 bad/skipped/duplicate relationships, peak memory 549.8 MiB) -- well under a minute end to end (excluding Docker image pull). Every query in [examples/queries.cypher](examples/queries.cypher) ran cleanly against this loaded sample with no syntax/type errors; see [docs/VALIDATION_RESULTS.md](docs/VALIDATION_RESULTS.md) for the full v0.2.0 run.

### Neo4j database dump

A `neo4j-admin database dump` was taken of both the full graph and the sample for sizing purposes only (not distributed from this repo -- see [docs/DISTRIBUTION_ARTIFACTS.md](docs/DISTRIBUTION_ARTIFACTS.md) for the measured sizes and a Hugging Face / Zenodo hosting feasibility assessment). A pre-built dump may be published separately in a later release.

## Citing

> Deveza L. *Lunas Clinical Evidence Knowledge Graph* (v0.1.0) [Data set]. Zenodo; 2026. https://doi.org/10.5281/zenodo.24011485

If you use v0.2.0 specifically, cite its own version DOI once published <!-- TODO v0.2.0 DOI: fill in after Zenodo publish --> (same concept DOI, `10.5281/zenodo.24011485`, resolves to whichever version is latest).

Cite the JEV sidecar separately ([10.5281/zenodo.24012855](https://doi.org/10.5281/zenodo.24012855)) if you use it -- unchanged by v0.2.0.

## Licence

Code and documentation in this repository: CC0 1.0. Graph data: see the table above and `NOTICE.md` in the data release for per-source attribution.
