#!/bin/bash
# Build a neo4j-admin database dump of the fully-loaded graph and measure its size.
# Run AFTER the full load (scripts/load_all_nodes.py + scripts/load_all_edges.py)
# has finished against the ce-kg-neo4j container. The database must be stopped
# for a consistent offline dump with Neo4j 5 Community (no online-dump license).
set -e
echo "=== pre-dump counts ==="
docker exec ce-kg-neo4j cypher-shell -u neo4j -p clinicalevidence \
  "MATCH (n) RETURN count(n) AS nodes;" \
  "MATCH ()-[r]->() RETURN count(r) AS edges;" 2>&1 || true

echo "=== stopping neo4j process inside the container (keep container up) ==="
docker exec ce-kg-neo4j neo4j stop || true
sleep 3

echo "=== dumping ==="
docker exec ce-kg-neo4j neo4j-admin database dump neo4j --to-path=/data/dumps --overwrite-destination=true

echo "=== restarting neo4j ==="
docker exec -d ce-kg-neo4j neo4j start

echo "=== copying dump out ==="
mkdir -p ../neo4j-dump
docker cp ce-kg-neo4j:/data/dumps/neo4j.dump ../neo4j-dump/clinical-evidence-kg-v0.1.0.dump

echo "=== size + checksum ==="
ls -la ../neo4j-dump/clinical-evidence-kg-v0.1.0.dump
sha256sum ../neo4j-dump/clinical-evidence-kg-v0.1.0.dump
