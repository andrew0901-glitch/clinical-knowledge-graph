"""Same-descriptor topic bridges and source-ancestor trial sensitivity,; independent sets."""
import collections
from common import *
def run(con,label):
 r=Registry(con,'topic_sensitivity_'+label);old=label=='v01'
 con.execute("CREATE TEMP TABLE au AS SELECT id,"+('false' if old else 'stub')+" stub,gr FROM article")
 con.execute("CREATE TEMP TABLE tc AS SELECT m.descriptor,p.population,bool_or(a.gr) gr,bool_or(a.gr AND m.edge_major) gr_major FROM am m JOIN au a ON a.id=m.article CROSS JOIN (VALUES ('with_stubs',false),('without_stubs',true)) p(population,exclude) WHERE NOT p.exclude OR NOT a.stub GROUP BY 1,2")
 con.execute("CREATE TEMP TABLE tx AS WITH q AS (SELECT DISTINCT subject topic,object descriptor FROM tm WHERE NOT EXISTS(SELECT 1 FROM stop WHERE id=object)),raw AS (SELECT topic,m.mode,descriptor FROM q CROSS JOIN modes m UNION SELECT q.topic,m.mode,h.child FROM q JOIN hierarchy h ON h.parent=q.descriptor CROSS JOIN modes m WHERE (m.level=2 OR (m.level=1 AND h.priority=0)) AND NOT EXISTS(SELECT 1 FROM stop WHERE id=h.child)) SELECT DISTINCT * FROM raw")
 sql="""WITH cov AS (SELECT x.topic,x.mode,p.population,bool_or(coalesce(c.gr,false) AND EXISTS(SELECT 1 FROM trial_mesh t WHERE t.object=x.descriptor)) same_bridge,bool_or(coalesce(c.gr_major,false) AND EXISTS(SELECT 1 FROM trial_mesh t WHERE t.object=x.descriptor)) same_major_bridge,bool_or(EXISTS(SELECT 1 FROM trial_qualified t WHERE t.study_aspect='condition' AND t.object=x.descriptor)) source_ancestor_trial,bool_or(coalesce(c.gr,false) AND EXISTS(SELECT 1 FROM trial_qualified t WHERE t.study_aspect='condition' AND t.object=x.descriptor)) source_ancestor_same_bridge FROM tx x CROSS JOIN (VALUES ('with_stubs'),('without_stubs')) p(population) LEFT JOIN tc c ON c.descriptor=x.descriptor AND c.population=p.population GROUP BY 1,2,3) SELECT population,mode,(SELECT count(*) FROM nodes WHERE label='MedlinePlus') topics,count(*) FILTER(WHERE same_bridge) topics_with_same_descriptor_guide_trial_bridge,count(*) FILTER(WHERE same_major_bridge) topics_with_same_major_descriptor_bridge,count(*) FILTER(WHERE source_ancestor_trial) topics_reaching_source_condition_ancestor_or_list_trial,count(*) FILTER(WHERE source_ancestor_same_bridge) topics_with_guide_and_source_ancestor_trial_same_bridge FROM cov GROUP BY 1,2 ORDER BY 1,2"""
 r.run('population',sql,'Complete '+label+' topic population; strict shared descriptor bridge plus separately labeled trial source-ancestor sensitivity. v0.1 has no canonical identity-only layer.')
 stop={x[0] for x in con.execute('SELECT id FROM stop').fetchall()};roots=collections.defaultdict(set);h=collections.defaultdict(set);ch=collections.defaultdict(set)
 for t,d in con.execute('SELECT subject,object FROM tm').fetchall():
  if d not in stop:roots[t].add(d)
 for a,b,pr in con.execute('SELECT child,parent,priority FROM hierarchy').fetchall():
  if a in stop:continue
  h[b].add(a)
  if pr==0:ch[b].add(a)
 gids={};cur=con.execute('SELECT id,'+('false' if old else 'stub')+',pub_types FROM article')
 while batch:=cur.fetchmany(100000):
  for ident,stub,types in batch:
   if set(types or [])&{'Practice Guideline','Guideline','Systematic Review','Meta-Analysis','Review'}:gids[ident]=stub
 cap=collections.Counter();cur=con.execute('SELECT article,descriptor,edge_major FROM am WHERE article IN (SELECT unnest(?::VARCHAR[]))',[list(gids)])
 while batch:=cur.fetchmany(100000):
  for a,d,major in batch:
   if d in stop:continue
   cap[d]|=1|(2 if major is True else 0)|(0 if gids[a] else 4)|(8 if major is True and not gids[a] else 0)
 listed=set();source=set();cur=con.execute('SELECT object,mesh_type FROM trial_qualified WHERE study_aspect=\'condition\'')
 while batch:=cur.fetchmany(100000):
  for d,typ in batch:
   source.add(d)
   if typ=='mesh-list':listed.add(d)
 for x in r.results['population']:
  counts=[0,0,0,0];gflag,mflag=(1,2) if x['population']=='with_stubs' else (4,8)
  for t,qq in roots.items():
   terms=set(qq)
   if x['mode']!='none':
    for q in qq:terms.update(ch[q] if x['mode']=='one' else h[q]|ch[q])
   counts[0]+=any(cap[d]&gflag and d in listed for d in terms);counts[1]+=any(cap[d]&mflag and d in listed for d in terms);counts[2]+=not terms.isdisjoint(source);counts[3]+=any(cap[d]&gflag and d in source for d in terms)
  assert counts==[x[k] for k in ['topics_with_same_descriptor_guide_trial_bridge','topics_with_same_major_descriptor_bridge','topics_reaching_source_condition_ancestor_or_list_trial','topics_with_guide_and_source_ancestor_trial_same_bridge']],(label,x,counts)
 return True
def main():
 c=connect(True);run(c,'v02');c.close();dump(R/'topic_sensitivity_verification.json',dict(passed=True,method='Independent Python source-type classification, descriptor capabilities, downward hierarchy sets and strict/source-ancestor trial descriptor sets,.'))
if __name__=='__main__':main()
