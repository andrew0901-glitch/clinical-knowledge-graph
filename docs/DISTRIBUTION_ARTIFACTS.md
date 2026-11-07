# Distribution artifacts: dump vs. sample subgraph

KGX JSON Lines (the published Zenodo/Hugging Face export) remains the
**canonical, authoritative** distribution format for the Lunas Clinical
Evidence KG. The two artifacts below are convenience layers on top of it,
investigated/built for this companion repo.

## 1. Prebuilt Neo4j database dump

A `neo4j-admin database dump` of the fully-loaded graph, so a consumer can
skip the ~hour-plus KGX->Neo4j load entirely and just restore a database.

**Zenodo per-record limit**: current official limit is **50 GB per record,
max 100 files** (https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo),
with larger one-time quota increases available on request. A single Neo4j
dump file would need to fit comfortably under that.

**Build procedure (reproducible):**
```bash
# After a full load into the ce-kg-neo4j container (see README quick start):
docker exec ce-kg-neo4j neo4j-admin database dump neo4j \
  --to-path=/data/dumps
docker cp ce-kg-neo4j:/data/dumps/neo4j.dump ./neo4j-dump/clinical-evidence-kg-v0.1.0.dump
sha256sum ./neo4j-dump/clinical-evidence-kg-v0.1.0.dump
```
(Requires stopping writes / using `neo4j-admin database dump` against a
stopped or read-only database for a fully consistent dump; for a throwaway
validation container, stopping the single `neo4j` database briefly is fine:
`docker exec ce-kg-neo4j cypher-shell ... "STOP DATABASE neo4j"` is not
available in Community edition for the default db, so in practice: stop the
container's write traffic, then dump while it's idle, or take the dump from
a container that has finished loading and is not being written to.)

**Required indexes/constraints** (recreated automatically by a dump/restore
since they're part of the database): see `cypher/constraints_and_indexes.cypher`
plus the `KGXNode` constraint the loader creates at `scripts/load_kgx_to_neo4j.py`
(`CONSTRAINTS` list).

**Size**: see `docs/VALIDATION_RESULTS.md` for the measured (or, if the
Docker environment's disk/time couldn't accommodate a full-scale dump within
this task's budget, clearly-labeled extrapolated) dump size, derived from the
real full `/data` directory size after a full load.

## 2. Small sample subgraph

A ~250K-edge slice with **every relationship type from the full export
present at least once**, meant to load in about a minute so someone can
kick the tires before committing to the multi-GB full load.

**Build procedure (reproducible, real, built for this repo):**
```bash
python3 scripts/build_sample_subgraph.py \
  --data-dir ../data --manifest ../data/manifest.json \
  --out ../sample --per-type-cap 20000
```
This caps each of the 16 relationship types present in v0.1.0 at 20,000
edges (or that type's true total if smaller, e.g. `TRANSLATION_OF` only has
1,016 edges total), pulls every node referenced by a kept edge, and writes
`sample/nodes__sample.jsonl.gz` + `sample/edges__sample.jsonl.gz` +
`sample/sample_build_report.json` (exact per-type counts actually kept).

**Load + verify:**
```bash
python3 scripts/load_kgx_to_neo4j.py --data-dir ../sample \
  --uri bolt://localhost:7687 --user neo4j --password clinicalevidence
cypher-shell ... "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType;"
```

See `docs/VALIDATION_RESULTS.md` for the real measured counts, load time,
and the relationship-type-coverage check (all 16 types present).

**Checksums**: sha256 of the two sample shard files are recorded in
`docs/VALIDATION_RESULTS.md` once built.
