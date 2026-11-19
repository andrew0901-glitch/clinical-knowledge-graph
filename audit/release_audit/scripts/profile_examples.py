"""Both-population author profiles and example citation values, independently re-scored."""
import collections
from common import *
def main():
 c=connect(True);r=Registry(c,'profile_examples');examples=json.loads((R/'examples.json').read_text());passed=[]
 for i,area in enumerate(['neurology','respiratory','cardiovascular'],1):
  author=next(x['rows'][0]['author'] for x in examples if x['traversal']=='author' and x['area']==area)
  rows=r.run('author_'+str(i),"SELECT p.population,m.descriptor,n.name,count(DISTINCT au.subject) articles,arg_min(au.id,au.subject||m.edge_id) authorship_witness,arg_min(m.edge_id,au.subject||m.edge_id) mesh_witness FROM authorship au JOIN am m ON m.article=au.subject JOIN article a ON a.id=au.subject JOIN nodes n ON n.id=m.descriptor CROSS JOIN populations p WHERE au.object=? AND NOT m.check_tag AND (NOT p.exclude_stubs OR NOT a.stub) GROUP BY 1,2,3 QUALIFY row_number() OVER(PARTITION BY p.population ORDER BY articles DESC,m.descriptor)<=10 ORDER BY p.population,articles DESC,m.descriptor",'Purposive '+area+' Author '+author+'; distinct corpus Articles per non-check descriptor, induced Article populations, not person-level expertise.',[author])
  authored={a for a, in c.execute('SELECT subject FROM authorship WHERE object=?',[author]).fetchall()};counts={p:collections.defaultdict(set) for p in ['with_stubs','without_stubs']};stubs={a for a, in c.execute('SELECT id FROM article WHERE stub AND id IN (SELECT unnest(?::VARCHAR[]))',[list(authored)]).fetchall()}
  for a,d,stop in c.execute('SELECT article,descriptor,check_tag FROM am WHERE article IN (SELECT unnest(?::VARCHAR[]))',[list(authored)]).fetchall():
   if stop:continue
   counts['with_stubs'][d].add(a)
   if a not in stubs:counts['without_stubs'][d].add(a)
  for p in counts:
   expected=sorted(counts[p],key=lambda d:(-len(counts[p][d]),d))[:10];actual=[x for x in rows if x['population']==p];assert expected==[x['descriptor'] for x in actual]
   for x in actual:assert x['articles']==len(counts[p][x['descriptor']])
  passed.append('author profile '+area)
  neighbor=next(x['rows'][0]['neighbor'] for x in examples if x['traversal']=='article' and x['area']==area)
  got=r.run('citation_'+str(i),"SELECT a.id,a.stub,coalesce(i.in_corpus_citations,0) with_stubs_citations,CASE WHEN a.stub THEN NULL ELSE coalesce(j.in_corpus_citations,0) END without_stubs_citations FROM article a LEFT JOIN incoming i ON i.article=a.id LEFT JOIN incoming_nonstub j ON j.article=a.id WHERE a.id=?",'Citation value of the exact '+area+' example neighbor in both induced populations; NULL means excluded stub, not zero citations.',[neighbor])[0]
  rawrows=c.execute("SELECT DISTINCT cc.subject,a.stub FROM e cc JOIN article a ON a.id=cc.subject WHERE cc.type='CITES' AND cc.object=? AND cc.subject<>cc.object",[neighbor]).fetchall();assert got['with_stubs_citations']==len({a for a,s in rawrows})
  if not got['stub']:assert got['without_stubs_citations']==len({a for a,s in rawrows if not s})
  passed.append('citation witness '+area)
 dump(R/'profile_examples_verification.json',dict(passed=True,checks=passed,method='Independent Python distinct Article sets by actual indexed descriptor and citing-Article set memberships.'));c.close()
if __name__=='__main__':main()
