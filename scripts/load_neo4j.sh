#!/usr/bin/env bash
# Bulk-import the CSVs written by kgx_to_neo4j.py into Neo4j 5.
#
#   bash scripts/load_neo4j.sh neo4j_import            # uses a local neo4j-admin
#   USE_DOCKER=1 bash scripts/load_neo4j.sh neo4j_import  # uses the official neo4j:5 image
#
# The target database must be stopped and will be overwritten. Neo4j Community has one user
# database, "neo4j", so that is the default. Enterprise users can set DB=clinicalkg.
set -euo pipefail
IMPORT_DIR="$(cd "${1:?usage: load_neo4j.sh <csv_dir>}" && pwd)"
DB="${DB:-neo4j}"
NEO4J_IMAGE="${NEO4J_IMAGE:-neo4j:5-community}"
DATA_DIR="${DATA_DIR:-$PWD/neo4j_data}"

args=()
for f in "$IMPORT_DIR"/nodes_*.csv; do args+=("--nodes=/import/$(basename "$f")"); done
for f in "$IMPORT_DIR"/edges_*.csv; do args+=("--relationships=/import/$(basename "$f")"); done
common=(--array-delimiter=";" --multiline-fields=true --skip-bad-relationships=true
        --skip-duplicate-nodes=true --bad-tolerance=1000000 --overwrite-destination=true)

if [[ "${USE_DOCKER:-0}" == "1" ]]; then
  mkdir -p "$DATA_DIR"
  docker run --rm -v "$IMPORT_DIR":/import -v "$DATA_DIR":/data "$NEO4J_IMAGE" \
    neo4j-admin database import full "${args[@]}" "${common[@]}" "$DB"
  echo "Imported into $DATA_DIR. Start Neo4j with:  docker compose up -d   (then open http://localhost:7474)"
else
  # local install: neo4j-admin resolves /import paths relative to nothing, so rewrite to absolute paths
  args=("${args[@]//\/import\//$IMPORT_DIR/}")
  neo4j-admin database import full "${args[@]}" "${common[@]}" "$DB"
  echo "Imported into database '$DB'. Start Neo4j and open http://localhost:7474"
fi
