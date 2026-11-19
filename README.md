# Lunas Clinical Evidence Knowledge Graph

Documentation, loaders and examples for the **Lunas Clinical Evidence KG**, a public, provenance-aware knowledge graph linking biomedical literature, clinical trials, controlled vocabulary and patient information. Published by Lunas Health (LunasAI LLC).

**This repository holds no graph data.** The data lives here:

| | Where | Licence |
|---|---|---|
| Core graph v0.1.0 | Hugging Face [`lunas-health/clinical-evidence-kg`](https://huggingface.co/datasets/lunas-health/clinical-evidence-kg) (tag `clinical-v0.1.0`) · Zenodo [10.5281/zenodo.24011485](https://doi.org/10.5281/zenodo.24011485) | CC0 1.0 |
| Core graph v0.2.0 | Hugging Face `lunas-health/clinical-evidence-kg` (tag `clinical-v0.2.0`) · Zenodo [10.5281/zenodo.24091964](https://doi.org/10.5281/zenodo.24091964) | CC0 1.0 |
| Core graph v0.2.1 (current) | Hugging Face `lunas-health/clinical-evidence-kg` (tag `clinical-v0.2.2`) · Zenodo [10.5281/zenodo.24108692](https://doi.org/10.5281/zenodo.24108692) | CC0 1.0 |
| JEV evidence annotations (separately licensed annotation layer) | Zenodo [10.5281/zenodo.24012855](https://doi.org/10.5281/zenodo.24012855) · also in the Hugging Face repo | Not CC0: rights-reserved under the terms of Zenodo record 10.5281/zenodo.24012855; model predictions; no model training; not part of the graph manifest |

v0.2.1 is the current, published version. It corrects v0.2.0's dataset card metadata; the
node/edge data is byte-identical to v0.2.0. Cite it as v0.2.1 ([10.5281/zenodo.24108692](https://doi.org/10.5281/zenodo.24108692)) --
the Hugging Face tag is `clinical-v0.2.2`, a metadata-only correction to this mirror (56 leftover
v0.1 files removed, loading config now lists only the manifest's 107 files) with identical file
hashes to `clinical-v0.2.1`; it is not a new Zenodo release. The Zenodo concept DOI shared by
every version is [10.5281/zenodo.24011484](https://doi.org/10.5281/zenodo.24011484) -- always
resolves to the latest published version. The JEV sidecar is unchanged across all three releases
-- none of them ship a regenerated JEV file, so the v0.1.0 JEV record above still applies as-is.

**Annotation layer.** `jev_evidence_annotations.jsonl` and `jev_manifest.json` are the separately
licensed annotation layer. They are rights-reserved under the terms of Zenodo record
[10.5281/zenodo.24012855](https://doi.org/10.5281/zenodo.24012855), are not covered by CC0, and are
not part of the graph manifest: `manifest.json` lists only the 107 node and edge files, and the
scripts in this repository read only those.

## What is in v0.2.1

12,067,108 nodes and 105,758,066 edges in [KGX](https://github.com/biolink/kgx) JSON Lines, with [Biolink](https://biolink.github.io/biolink-model/) categories and predicates (identical to v0.2.0 -- see above). Five source families: PubMed (with MeSH indexing, and -- **new in v0.2.0** -- PMC/Journal identifiers attached to the Article record, not a separate family), OpenAlex (citations, authorship), MeSH (with hierarchy), ClinicalTrials.gov, and MedlinePlus. The v0.1.0 `ctgov_publications.jsonl` sidecar file no longer exists as a separate thing -- its content is now natively absorbed into three typed edges inside the main graph (`VALIDATED_BY`/`CITES_BACKGROUND`/`HAS_DERIVED_PUBLICATION`; see [docs/DATA_NOTES.md](docs/DATA_NOTES.md)). The JEV annotations sidecar still travels separately, unchanged from v0.1.0. Read [docs/DATA_NOTES.md](docs/DATA_NOTES.md) before analysing.

<details>
<summary>What was in v0.1.0 (10,145,579 nodes / 109,661,337 edges, five source families)</summary>

v0.1.0 did not have PMC/Journal, had a single `VALIDATED_BY` type that mixed all ClinicalTrials.gov reference roles together (45,314 edges), had `HAS_RIGHTS_EVIDENCE`/`HAS_USE_GRANT` rights-bookkeeping edges (~11.2M), and named the MeSH-tree edges `PARENT_OF`/`ANCESTOR_OF`. See the sections below for what changed.

</details>

## Quick start

### 1. Download

```bash
pip install -U huggingface_hub duckdb
hf download lunas-health/clinical-evidence-kg --repo-type dataset \
  --revision clinical-v0.2.2 --local-dir ckg          # or clinical-v0.2.0 / clinical-v0.1.0 for an earlier release
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

**Resources (measured, real, full-scale against v0.1.0 -- not an estimate; see [docs/VALIDATION_RESULTS.md](docs/VALIDATION_RESULTS.md) for the full breakdown). Not yet re-measured at v0.2.0/v0.2.1's full scale** (the sample-scale load test below is re-measured for v0.2.1; the full ~12M-node / ~105.8M-edge download is somewhat smaller in edge count than v0.1.0's ~110M, since dropping the ~11.2M rights-bookkeeping edges outweighs adding PMC/Journal, so these v0.1.0 numbers are a reasonable but unverified estimate for v0.2.0/v0.2.1, not a measurement):

| Step | Wall time | Peak memory | Disk |
|---|---:|---:|---:|
| `kgx_to_neo4j.py` (KGX -> CSV) | ~15.2 min | tens of MB (pure streaming, single-threaded) | 25 GB CSV output |
| `load_neo4j.sh` (`neo4j-admin database import full`) | ~7.2 min | 793 MiB (neo4j-admin's own report) | 55 GB final `/data` store |
| **Total load** | **~22.5 min** | **under 1 GB for conversion+import** | **~85 GB peak** (4.9 GiB download + 25 GB CSV + 55 GB store, coexisting briefly; the 25 GB CSV dir can be deleted once import succeeds, leaving 55 GB) |

The import itself is lightweight; **the real cost is disk, not RAM.** Running the server afterward to query the graph is the one step that benefits from real memory: this repo's `docker-compose.yml` configures 8 GB heap / 16 GB page cache (~32 GB with OS overhead) as a comfortable default for a dedicated machine; the example queries ran fine against as little as 6 GB heap / 8 GB page cache. Reserve disk headroom beyond the ~55 GB final store size. **v0.2.0/v0.2.1 removed the rights-bookkeeping edges entirely** (`HAS_RIGHTS_EVIDENCE`/`HAS_USE_GRANT` no longer exist in the graph at all) -- there is nothing of that kind left to `--exclude-type`.

### 4. Try the sample subgraph first (loads in under a minute)

A self-consistent ~45 MiB slice of the real v0.2.1 export: every one of the 18 relationship types present at least once (capped at 20,000 edges per type, or that type's true total if smaller), plus the real neighborhoods of the four literal seeds `examples/queries.cypher` / `scripts/quickstart.py` use by default (an author, a trial, a MedlinePlus topic, a seed article), so every example query returns real rows, not just every relationship type, plus the ClinicalTrials.gov condition-to-MeSH edges of every sample trial that has a sponsor or site, so `examples/trial_landscape.py` returns rows too. Every node referenced by a kept edge is included (0 dangling references), same KGX file-naming convention as the full download so the same scripts load it unchanged. Rebuilt fresh from the real v0.2.1 release data (byte-identical to v0.2.0's); previously this was a ~28 MiB / 174,220-node / 255,798-edge slice of v0.1.0 (16 relationship types).

| File | Size | SHA-256 |
|---|---:|---|
| `sample_out/nodes__sample.jsonl.gz` | 26,768,729 bytes | `f5b67472953479ec17014d3d55b6202156ace1aabb4ddc9ac395e12c98cb1b4f` |
| `sample_out/edges__sample.jsonl.gz` | 20,607,023 bytes | `65a3c71b7246695356596764beac1a3b156e8f87d25384ead8d9c9f36c824788` |

271,924 nodes / 322,615 edges. Build it yourself with `scripts/build_sample_subgraph.py`, then `scripts/seed_sample_subgraph.py`, then `scripts/seed_trial_mesh_sample.py` (see [docs/DISTRIBUTION_ARTIFACTS.md](docs/DISTRIBUTION_ARTIFACTS.md)), or load a copy you already have:

```bash
python scripts/kgx_to_neo4j.py --input sample_out --out neo4j_import_sample
USE_DOCKER=1 bash scripts/load_neo4j.sh neo4j_import_sample
```

Measured against the real, reseeded v0.2.1 sample: conversion 8.1s + `neo4j-admin` import 8.4s (271,924 nodes / 322,615 relationships / 9,987,419 properties, every relationship imported, peak memory 549.9 MiB) -- well under a minute end to end (excluding Docker image pull). Every one of the 12 queries in [examples/queries.cypher](examples/queries.cypher) now returns real, nonzero rows against this loaded sample (previously 3 returned zero because their literal ids didn't survive the unseeded per-type-cap build); see [docs/VALIDATION_RESULTS.md](docs/VALIDATION_RESULTS.md) for the full row-count table (measured before the trial-to-MeSH seed, which only adds edges). Against this sample the trial landscape tool returns 496 trials for Breast Neoplasms, 160 for Heart Failure, 110 for Alzheimer Disease and 3,293 for Neoplasms.

### 5. Clinical trial landscape for a condition

```bash
python examples/trial_landscape.py --input ckg --condition "Heart Failure"     # or D006333 / MESH:D006333
python examples/trial_landscape.py --input ckg --condition D006333 --merge-sites   # merge facility spellings
python examples/trial_landscape.py --input ckg --data-check                    # field completeness table
```

For a MeSH condition descriptor (expanded down its own MeSH tree branches, with direct matches kept
separate), it writes CSVs and one self-contained `report.html`: trials by sponsor, sponsor class,
phase and status; a start-year timeline; top sites and countries with how many matching trials are
recruiting at each; and trials with results articles
(`VALIDATED_BY`) with how often those articles are cited in-graph by guidelines or systematic reviews.
`--merge-sites` merges facility spellings within a city and country (case, accents, punctuation,
abbreviations such as Ctr/Centre, and company suffixes such as Inc/LLC/GmbH) and reports site counts
before and after: 60,591 -> 52,482 sites for breast neoplasms, 1,092,163 -> 940,830 across the
release. It does not resolve different names for the same place. The first run caches the trial subgraph as Parquet (about 45 s on 16 cores); later runs take 2-3 s.
`examples/trial_report.py` builds a fuller report for any topic from the same cache, one CSV per section.
A topic is a JSON spec of selection routes (MeSH trees, title text), an optional restriction and an optional
subset; `examples/topics/` has two. Every term list and the count each route contributes are written out.
Sections include active trials, industry competitors, sites (merged), countries, phase, results
articles, terminations, and benchmarks from comparable trials in the topic (by phase and sponsor class).
It also prints a field-coverage table. Fields the input does not carry are listed as missing, never dropped.
With the current release that includes primary completion date, outcomes, why_stopped, design and eligibility.
`python -m pytest tests/` runs its tests.
Example outputs for breast neoplasms, Alzheimer disease and heart failure are in
[examples/trial_landscape_examples/](examples/trial_landscape_examples/) (the large per-trial and
per-site CSVs are left out; rerun to regenerate them). Read the trial notes in
[docs/DATA_NOTES.md](docs/DATA_NOTES.md#clinical-trials-conditions-sponsors-and-sites) first.

### 6. Evidence map for a condition

```bash
python examples/evidence_map.py --input ckg --condition "Heart Failure"          # or D006333 / MESH:D006333
python examples/evidence_map.py --input ckg --condition D001943 --exclude-stubs   # drop identity-only Article stubs
python examples/evidence_map.py --input ckg --condition D012516 --expansion none --major-only
```

For a MeSH descriptor (by default expanded to every narrower descriptor via `HAS_BROADER_ANCESTOR`;
the 40 MeSH check tags such as Humans or Female are never used) it counts the indexed Articles by
study design, assigned once each in the order guideline > systematic review or meta-analysis >
randomized controlled trial > other clinical trial > observational > other, from NLM publication
types. It then reports which primary studies (randomized and other clinical trials) are cited by an
in-graph guideline, systematic review or meta-analysis, how many distinct reviews cite them, and how
many reviews and guidelines were published 2022-2026. CITES edges from an Article to itself are
dropped. Output: `summary.json`, `design.csv`, `primary_studies.csv` (each primary study with its
number of citing reviews), `citing_reviews.csv`, `recent_reviews.csv` (guidelines and SR/MA from 2022-2026),
`expansion.csv`, a self-contained `report.html` and a GitHub-readable `README.md`. Like the trial landscape tool it reads only the
files listed in `manifest.json` / `zenodo_manifest.json` and caches what it needs as Parquet (about a
minute on 16 cores the first time, seconds afterwards). The full definitions are in the script's
docstring.

On the v0.2.1 release, breast neoplasms (D001943, 9 descriptors) gives 53,369 Articles, of which
5,201 are primary studies; 2,469 of them are cited by at least one of 2,058 in-graph reviews or
guidelines. Identity-only stubs carry no publication types, MeSH or CITES edges in v0.2.x, so
`--exclude-stubs` does not change MeSH-based maps.

Tests (run against the bundled sample subgraph, plus a small hand-built graph for the citation rules):

```bash
pip install duckdb pytest
pytest tests/test_evidence_map.py
```

### 7. Audit materials

[audit/](audit/README.md) holds the audit scripts, the exact SQL, the result tables, the reproducibility manifests and the audit write-ups for this release, all computed from the public release files. Its README maps each headline number of the preprint to the file and query that produces it, lists the SHA-256 of every input file, and gives a one-command rerun from scratch (`audit/scripts/run_lanes.sh`). What was left out or redacted, and why, is in [audit/EXCLUDED.md](audit/EXCLUDED.md).

### Neo4j database dump

A `neo4j-admin database dump` was taken of both the full graph and the sample for sizing purposes only (not distributed from this repo -- see [docs/DISTRIBUTION_ARTIFACTS.md](docs/DISTRIBUTION_ARTIFACTS.md) for the measured sizes and a Hugging Face / Zenodo hosting feasibility assessment). A pre-built dump may be published separately in a later release.

## Citing

See [CITATION.cff](CITATION.cff) (currently v0.2.1, DOI `10.5281/zenodo.24108692`):

> Deveza L. *Lunas Clinical Evidence Knowledge Graph* (v0.2.1) [Data set]. Zenodo; 2026. https://doi.org/10.5281/zenodo.24108692

If you use an earlier version specifically, cite its own version DOI instead: v0.2.0 is
[10.5281/zenodo.24091964](https://doi.org/10.5281/zenodo.24091964), v0.1.0 is
[10.5281/zenodo.24011485](https://doi.org/10.5281/zenodo.24011485). The concept DOI
([10.5281/zenodo.24011484](https://doi.org/10.5281/zenodo.24011484)) always resolves to whichever
version is latest, for a citation that shouldn't pin to one version.

Cite the JEV sidecar separately ([10.5281/zenodo.24012855](https://doi.org/10.5281/zenodo.24012855)) if you use it -- unchanged by v0.2.0/v0.2.1.

## Licence

Code and documentation in this repository: CC0 1.0. Graph data: see the table above and `NOTICE.md` in the data release for per-source attribution.
