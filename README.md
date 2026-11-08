# Lunas Clinical Evidence Knowledge Graph

Documentation, loaders and examples for the **Lunas Clinical Evidence KG**, a public, provenance-aware knowledge graph linking biomedical literature, clinical trials, controlled vocabulary and patient information. Published by Lunas Health (LunasAI LLC).

**This repository holds no graph data.** The data lives here:

| | Where | Licence |
|---|---|---|
| Core graph v0.1.0 | Hugging Face [`lunas-health/clinical-evidence-kg`](https://huggingface.co/datasets/lunas-health/clinical-evidence-kg) (tag `clinical-v0.1.0`) · Zenodo [10.5281/zenodo.24011485](https://doi.org/10.5281/zenodo.24011485) | CC0 1.0 |
| JEV evidence annotations (sidecar) | Zenodo [10.5281/zenodo.24012855](https://doi.org/10.5281/zenodo.24012855) · also in the Hugging Face repo | Not CC0: rights reserved by LunasAI LLC; model predictions; no model training |

## What is in v0.1.0

10,145,579 nodes and 109,661,337 edges in [KGX](https://github.com/biolink/kgx) JSON Lines, with [Biolink](https://biolink.github.io/biolink-model/) categories and predicates. Five source families: PubMed (with MeSH indexing), OpenAlex (citations, authorship), MeSH (with hierarchy), ClinicalTrials.gov and MedlinePlus. Two sidecar files travel with the graph: the full ClinicalTrials.gov publication list (`ctgov_publications.jsonl`) and the JEV annotations. Read [docs/DATA_NOTES.md](docs/DATA_NOTES.md) before analysing.

## Quick start

### 1. Download

```bash
pip install -U huggingface_hub duckdb
hf download lunas-health/clinical-evidence-kg --repo-type dataset \
  --revision clinical-v0.1.0 --local-dir ckg          # ~7 GB
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

Then try [examples/queries.cypher](examples/queries.cypher). Node labels are the native Lunas labels (Article, MeSHConcept, ClinicalTrial, Author, ...) and relationship types the native types (HAS_MESH, CITES, AUTHORED_BY, VALIDATED_BY, PARENT_OF, ...). Biolink categories and predicates are kept as properties.

**Resources (measured, real, full-scale -- not an estimate; see [docs/VALIDATION_RESULTS.md](docs/VALIDATION_RESULTS.md) for the full breakdown):**

| Step | Wall time | Peak memory | Disk |
|---|---:|---:|---:|
| `kgx_to_neo4j.py` (KGX -> CSV) | ~15.2 min | tens of MB (pure streaming, single-threaded) | 25 GB CSV output |
| `load_neo4j.sh` (`neo4j-admin database import full`) | ~7.2 min | 793 MiB (neo4j-admin's own report) | 55 GB final `/data` store |
| **Total load** | **~22.5 min** | **under 1 GB for conversion+import** | **~85 GB peak** (4.9 GiB download + 25 GB CSV + 55 GB store, coexisting briefly; the 25 GB CSV dir can be deleted once import succeeds, leaving 55 GB) |

The import itself is lightweight; **the real cost is disk, not RAM.** Running the server afterward to query the graph is the one step that benefits from real memory: this repo's `docker-compose.yml` configures 8 GB heap / 16 GB page cache (~32 GB with OS overhead) as a comfortable default for a dedicated machine; the example queries in this repo ran fine against as little as 6 GB heap / 8 GB page cache on a shared host. Reserve disk headroom beyond the ~55 GB final store size -- a prior run on a shared host hit a genuine "no space left on device" mid-import when the *host's* disk (shared with unrelated processes) filled up; that is a shared-disk risk, not something this import needs on its own. To skip internal rights-bookkeeping edges, add `--exclude-type HAS_RIGHTS_EVIDENCE,HAS_USE_GRANT` to the converter.

### 4. Try the sample subgraph first (loads in under a minute)

A self-consistent ~28 MiB slice of the real v0.1.0 export: every one of the 16 relationship types present at least once (capped at 20,000 edges per type, or that type's true total if smaller), every node referenced by a kept edge included (0 dangling references), same KGX file-naming convention as the full download so the same scripts load it unchanged.

| File | Size | SHA-256 |
|---|---:|---|
| `sample_out/nodes__sample.jsonl.gz` | 16,014,336 bytes | `48bc8da6a72e02a9ce5be89640daef1cf2c6aebdc092ea4e2f022f9e970381ef` |
| `sample_out/edges__sample.jsonl.gz` | 13,763,004 bytes | `b18e695281645be6ff3dcae78606e7cd515b6682616177a7ed57f7db91dfdb0f` |

174,220 nodes / 255,798 edges. Build it yourself with `scripts/build_sample_subgraph.py` (see [docs/DISTRIBUTION_ARTIFACTS.md](docs/DISTRIBUTION_ARTIFACTS.md)), or load a copy you already have:

```bash
python scripts/kgx_to_neo4j.py --input sample_out --out neo4j_import_sample
USE_DOCKER=1 bash scripts/load_neo4j.sh neo4j_import_sample
```

Measured: conversion 5.4s + `neo4j-admin` import 7.4s -- well under a minute end to end (excluding Docker image pull).

### Neo4j database dump

A `neo4j-admin database dump` was taken of both the full graph and the sample for sizing purposes only (not distributed from this repo -- see [docs/DISTRIBUTION_ARTIFACTS.md](docs/DISTRIBUTION_ARTIFACTS.md) for the measured sizes and a Hugging Face / Zenodo hosting feasibility assessment). A pre-built dump may be published separately in a later release.

## Citing

> Deveza L. *Lunas Clinical Evidence Knowledge Graph* (v0.1.0) [Data set]. Zenodo; 2026. https://doi.org/10.5281/zenodo.24011485

Cite the JEV sidecar separately ([10.5281/zenodo.24012855](https://doi.org/10.5281/zenodo.24012855)) if you use it.

## Licence

Code and documentation in this repository: CC0 1.0. Graph data: see the table above and `NOTICE.md` in the data release for per-source attribution.
