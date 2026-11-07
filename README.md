# clinical-evidence-kg-github

Companion code/docs repo for the **Lunas Clinical Evidence KG v0.1.0** public dataset.

> **DRAFT STATUS — READ THIS FIRST**
>
> This repo was supposed to be seeded from a prepared bundle,
> `clinical-evidence-kg-github.zip` (quick-start README, KGX→Neo4j converter,
> docker-compose, example Cypher queries, data notes). That zip was **searched
> for and not found** anywhere on the machine that built this repo (home
> directory, `/tmp`, session scratchpads, the dataset's own Zenodo/HF record).
> Everything in this repo is therefore a **first-draft scaffold written from
> scratch against the real v0.1.0 file structure**, not the owner's originally
> intended content. If you are Lorenzo (the dataset owner) and the real zip
> turns up, replace this scaffold with its contents — the structure below was
> chosen to be a reasonable drop-in target (`scripts/`, `docker/`, `cypher/`,
> `docs/`).
>
> Everything in this repo **has been run end-to-end against the real,
> published v0.1.0 KGX export** (not synthetic/toy data) — see
> `docs/VALIDATION_RESULTS.md` for measured counts, timings, and resource use.

## What this is

The dataset itself (KGX JSON Lines, CC0-licensed core graph) lives on:
- Hugging Face: [`lunas-health/clinical-evidence-kg`](https://huggingface.co/datasets/lunas-health/clinical-evidence-kg)
- Zenodo: [10.5281/zenodo.24011485](https://doi.org/10.5281/zenodo.24011485)

This repo does **not** host the data. It hosts tooling to:
1. Download the published shards from Zenodo.
2. Load them into a local Neo4j 5 Community graph via `scripts/load_kgx_to_neo4j.py`.
3. Run example Cypher queries against the loaded graph.
4. Build two convenience distribution artifacts on top of the canonical KGX
   export: a pre-built/pre-indexed Neo4j dump, and a small (~250K-edge) sample
   subgraph. See `docs/DISTRIBUTION_ARTIFACTS.md`.

KGX JSON Lines remains the **canonical, authoritative** distribution format.
Everything here is a convenience layer on top of it.

## Quick start

```bash
# 1. Start a local Neo4j 5 Community instance (no license needed)
cd docker
docker compose up -d
# wait for http://localhost:7474 to answer (neo4j/clinicalevidence)

# 2. Download one representative node + edge shard (fast smoke test)
cd ../scripts
python3 download_shards.py --out ../data --sample

# 3. Load it
python3 load_kgx_to_neo4j.py --data-dir ../data --uri bolt://localhost:7687 \
  --user neo4j --password clinicalevidence

# 4. Run example queries
cypher-shell -a bolt://localhost:7687 -u neo4j -p clinicalevidence \
  -f ../cypher/example_queries.cypher
```

For the full graph (all 8 node shards + 8 edge shards, ~5.2 GB compressed,
~10.1M nodes / ~109.7M edges):

```bash
python3 download_shards.py --out ../data --all
python3 load_kgx_to_neo4j.py --data-dir ../data --uri bolt://localhost:7687 \
  --user neo4j --password clinicalevidence --all
```

See `docs/VALIDATION_RESULTS.md` for measured load times, peak RAM and disk
use on the real full-scale load.

## Repo layout

```
scripts/           download_shards.py, load_kgx_to_neo4j.py, build_sample_subgraph.py
docker/            docker-compose.yml (Neo4j 5 Community + APOC)
cypher/            example_queries.cypher, constraints_and_indexes.cypher
docs/              DATA_NOTES.md, VALIDATION_RESULTS.md, DISTRIBUTION_ARTIFACTS.md
```

## License

Tooling in this repo (scripts, docs, docker-compose) is provided under the
MIT license (see `LICENSE`). The dataset itself is licensed per-component —
see the dataset's own `NOTICE.md` / README on Zenodo/Hugging Face. The core
graph (nodes/edges/manifest) is CC0-1.0; do not assume every file in the
dataset is CC0 (the JEV evidence-annotation sidecar is explicitly NOT CC0 and
is not part of this v0.1.0 core export).
