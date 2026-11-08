#!/usr/bin/env bash
# Build a neo4j-admin database dump of a loaded graph and measure its size + checksum.
#
#   bash scripts/dump_and_measure.sh neo4j_data            # the dir docker-compose.yml mounts at /data
#   bash scripts/dump_and_measure.sh neo4j_data_sample ./clinical-evidence-kg-v0.1.0-sample.dump
#
# Neo4j 5 Community has no online-dump license, so the server must not be writing to this data
# directory while dumping. If you started it with `docker compose up -d`, stop it first
# (`docker compose stop`) -- this script does NOT stop a running compose service for you, since
# it doesn't know the compose project name; it only refuses to proceed if neo4j-admin reports the
# database is in use. Verified against neo4j:5-community (5.26.32) on the real, fully-loaded
# v0.1.0 graph: full graph (55 GB store) dumped to an 8.50 GiB file in ~99s; the ~28 MiB sample
# (653 MiB store) dumped to a 47.1 MiB file in <1s. See docs/DISTRIBUTION_ARTIFACTS.md.
set -euo pipefail
DATA_DIR="$(cd "${1:?usage: dump_and_measure.sh <neo4j_data_dir> [out_file]}" && pwd)"
OUT="${2:-clinical-evidence-kg-v0.1.0.dump}"
NEO4J_IMAGE="${NEO4J_IMAGE:-neo4j:5-community}"
DB="${DB:-neo4j}"

docker run --rm -v "$DATA_DIR":/data "$NEO4J_IMAGE" mkdir -p /data/dumps

docker run --rm -v "$DATA_DIR":/data "$NEO4J_IMAGE" \
  neo4j-admin database dump "$DB" --to-path=/data/dumps --overwrite-destination=true

docker run --rm -v "$DATA_DIR":/data -v "$(dirname "$(realpath "$OUT")")":/out "$NEO4J_IMAGE" \
  cp "/data/dumps/$DB.dump" "/out/$(basename "$OUT")"

echo "=== size + checksum ==="
ls -la "$OUT"
sha256sum "$OUT"
