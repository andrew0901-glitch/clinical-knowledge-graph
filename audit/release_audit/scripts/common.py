"""Release audit constants and exact SQL registry. Public release files only.

One configurable path: CLINICAL_KG_DATA = the release folder (manifest.json, nodes/, edges/), fetched with
audit/scripts/fetch_release.py. Large working files (projections, DuckDB, sort files) go to
<CLINICAL_KG_DATA>.release_audit_work -- budget roughly 150 GB.
"""
import os,pathlib,json,duckdb,subprocess
P=pathlib.Path(__file__).resolve().parents[1];R=P/'results';T=P/'tables';F=P/'figures'
DATA=pathlib.Path(os.environ.get('CLINICAL_KG_DATA',str(P.parents[1]/'data'/'clinical_kg_release_v0.2.1'))).resolve()
C=DATA.parent/(DATA.name+'.release_audit_work');C.mkdir(parents=True,exist_ok=True)
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def connect(read_only=False):
 c=duckdb.connect(str(C/'analysis.duckdb'),read_only=read_only);c.execute("SET threads=4;SET memory_limit='16GB';SET preserve_insertion_order=false");return c
class Registry:
 def __init__(self,c,name):self.c=c;self.name=name;self.results={};self.queries={}
 def run(self,name,sql,denominator,params=None):
  cur=self.c.execute(sql,params or []);rows=[dict(zip([d[0] for d in cur.description],r)) for r in cur.fetchall()];self.results[name]=rows;self.queries[name]=dict(sql=sql,parameters=params or [],denominator=denominator);self.save();print(name,rows[:1],flush=True);return rows
 def save(self):dump(R/(self.name+'.json'),self.results);dump(R/(self.name+'_queries.json'),self.queries)
