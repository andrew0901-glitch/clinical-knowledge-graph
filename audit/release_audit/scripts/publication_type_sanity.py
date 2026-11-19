"""Source reference role versus exact NLM protocol labels; complete join, metadata-bounded lower bound."""
import collections
from common import *
def main():
 c=connect(True);r=Registry(c,'publication_type_sanity')
 r.run('by_role',"SELECT p.population,l.role,count(*) edges,count(DISTINCT l.article) articles,count(*) FILTER(WHERE array_length(a.pub_types)>0) edges_with_publication_type,count(*) FILTER(WHERE list_contains(a.pub_types,'Clinical Trial Protocol')) protocol_edges,count(DISTINCT l.article) FILTER(WHERE list_contains(a.pub_types,'Clinical Trial Protocol')) protocol_articles FROM result_links l JOIN article a ON a.id=l.article CROSS JOIN populations p WHERE NOT p.exclude_stubs OR NOT a.stub GROUP BY 1,2 ORDER BY 1,2",'Complete role-link join against available exact NLM pub_types; protocol counts are lower bounds when linked Articles lack publication types, not clinical role adjudication.')
 protocols=set();typed=set();stub=set();cur=c.execute('SELECT id,stub,pub_types FROM article')
 while batch:=cur.fetchmany(100000):
  for a,s,types in batch:
   if s:stub.add(a)
   if types:typed.add(a)
   if 'Clinical Trial Protocol' in (types or []):protocols.add(a)
 counts=collections.defaultdict(collections.Counter);aa=collections.defaultdict(set);pp=collections.defaultdict(set);cur=c.execute('SELECT article,role FROM result_links')
 while batch:=cur.fetchmany(100000):
  for a,role in batch:
   for pop in ['with_stubs','without_stubs']:
    if pop=='without_stubs' and a in stub:continue
    k=pop,role;counts[k].update(edges=1,edges_with_publication_type=int(a in typed),protocol_edges=int(a in protocols));aa[k].add(a)
    if a in protocols:pp[k].add(a)
 for x in r.results['by_role']:
  k=x['population'],x['role'];assert [counts[k]['edges'],len(aa[k]),counts[k]['edges_with_publication_type'],counts[k]['protocol_edges'],len(pp[k])]==[x[z] for z in ['edges','articles','edges_with_publication_type','protocol_edges','protocol_articles']]
 dump(R/'publication_type_sanity_verification.json',dict(passed=True,method='Independent Python exact publication-type membership and role-edge/Article counts.'));c.close()
if __name__=='__main__':main()
