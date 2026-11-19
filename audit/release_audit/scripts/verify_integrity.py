"""Independent external-sort check of every edge/node ID and endpoint (no hash-join proof reused)."""
import subprocess,hashlib
from common import *
def main():
 c=connect(True);d=C/'integrity_sort';d.mkdir(exist_ok=True);queries={};env=dict(os.environ,LC_ALL='C')
 def copy(name,sql):
  p=d/(name+'.txt');query="COPY ("+sql+") TO ? (FORMAT CSV, HEADER false)";n=c.execute(query,[str(p)]).fetchone()[0];queries[name]=dict(sql=query,parameters=[str(p)],records=n);return p,n
 nodes,nn=copy('node_ids','SELECT id FROM nodes');edges,ne=copy('edge_ids','SELECT id FROM e');endpoints,nt=copy('endpoints','SELECT subject id FROM e UNION ALL SELECT object FROM e')
 def sort(path,out,unique=False):
  with out.open('wb') as f:subprocess.run(['sort','-S','2G','--parallel=4','-T',str(d),*(['-u'] if unique else []),str(path)],stdout=f,env=env,check=True)
 sorted_nodes=d/'nodes.sorted';sort(nodes,sorted_nodes)
 for name,src in [('nodes',sorted_nodes),('edges',edges)]:
  out=d/(name+'.duplicates');
  with out.open('wb') as f:
   if name=='edges':
    proc=subprocess.Popen(['sort','-S','2G','--parallel=4','-T',str(d),str(src)],stdout=subprocess.PIPE,env=env);subprocess.run(['uniq','-d'],stdin=proc.stdout,stdout=f,check=True);proc.stdout.close();assert proc.wait()==0
   else:subprocess.run(['uniq','-d',str(src)],stdout=f,check=True)
  assert out.stat().st_size==0,name+' duplicate IDs';print(name,'IDs independently unique',flush=True)
 sorted_endpoints=d/'endpoints.sorted';sort(endpoints,sorted_endpoints,True);missing=d/'missing_endpoints';
 with missing.open('wb') as f:subprocess.run(['comm','-23',str(sorted_endpoints),str(sorted_nodes)],stdout=f,env=env,check=True)
 assert missing.stat().st_size==0;expected=json.loads((R/'source_manifest.json').read_text())['totals'];assert (nn,ne,nt)==(expected['nodes'],expected['edges'],2*expected['edges'])
 dump(R/'integrity_verification.json',dict(passed=True,nodes=nn,edges=ne,endpoint_occurrences=nt,duplicate_node_ids=0,duplicate_edge_ids=0,missing_endpoint_ids=0,method='Independent GNU sort/uniq ID census and comm set difference against all node IDs; primary SQL counts/distinct/hash joins not reused as proof.',sql=queries,sort_options=['LC_ALL=C','-S 2G','--parallel=4'],code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()));c.close();print('All IDs/endpoints independently verified')
if __name__=='__main__':main()
