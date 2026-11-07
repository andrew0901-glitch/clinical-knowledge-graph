import sys, os, time
sys.path.insert(0, ".")
from load_kgx_to_neo4j import load_edges, CONSTRAINTS
from neo4j import GraphDatabase

d = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "clinicalevidence"))
base = "/tmp/claude-1000/-home-ldeveza-projects-lunasai-knowledge-graph/5e2bb7ad-fe77-4df5-8b41-5cddf3357eae/scratchpad/zenodo/full"
files = sorted(f for f in os.listdir(base) if f.startswith("edges__") and f.endswith(".jsonl.gz"))
total = 0
t0 = time.time()
with d.session() as s:
    for stmt in CONSTRAINTS:
        s.run(stmt)
    for ef in files:
        total += load_edges(s, os.path.join(base, ef), batch_size=20000)
print(f"TOTAL {total:,} edges in {time.time()-t0:.1f}s")
d.close()
