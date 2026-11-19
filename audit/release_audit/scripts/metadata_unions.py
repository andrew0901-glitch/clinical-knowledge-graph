"""Nonexclusive publication-type unions and actual major-topic Article coverage, independently checked."""
import collections
from common import *
def main():
 c=connect(True);r=Registry(c,'metadata_unions')
 r.run('publication_unions',"SELECT p.population,count(*) articles,count(*) FILTER(WHERE a.guideline) guideline_union,count(*) FILTER(WHERE a.systematic_review) systematic_review,count(*) FILTER(WHERE a.gr) guideline_review_union FROM article a CROSS JOIN populations p WHERE NOT p.exclude_stubs OR NOT a.stub GROUP BY 1",'All Articles, exact NLM labels; nonexclusive categories are unioned rather than summed.')
 r.run('major_article_coverage',"SELECT p.population,count(DISTINCT m.article) indexed_articles,count(DISTINCT m.article) FILTER(WHERE m.edge_major AND NOT m.check_tag) articles_with_noncheck_major,count(DISTINCT m.article) FILTER(WHERE m.edge_major IS NOT NULL) articles_with_any_known_major FROM am m JOIN article a ON a.id=m.article CROSS JOIN populations p WHERE NOT p.exclude_stubs OR NOT a.stub GROUP BY 1",'All indexed Articles, including true/false known major flags. No node-list fallback.')
 counts={p:collections.Counter(articles=0,guideline_union=0,systematic_review=0,guideline_review_union=0) for p in ['with_stubs','without_stubs']};stub=set();cur=c.execute('SELECT id,stub,pub_types FROM article')
 while batch:=cur.fetchmany(100000):
  for ident,s,types in batch:
   if s:stub.add(ident)
   ts=set(types or [])
   for pop,ct in counts.items():
    if pop=='without_stubs' and s:continue
    ct.update(articles=1,guideline_union=int(bool(ts&{'Practice Guideline','Guideline'})),systematic_review=int('Systematic Review' in ts),guideline_review_union=int(bool(ts&{'Practice Guideline','Guideline','Systematic Review','Meta-Analysis','Review'})))
 for x in r.results['publication_unions']:assert dict(counts[x['population']])=={k:v for k,v in x.items() if k!='population'}
 sets={p:[set(),set(),set()] for p in counts};cur=c.execute('SELECT article,edge_major,check_tag FROM am')
 while batch:=cur.fetchmany(100000):
  for ident,major,check in batch:
   for p,v in sets.items():
    if p=='without_stubs' and ident in stub:continue
    v[0].add(ident)
    if major is True and not check:v[1].add(ident)
    if major is not None:v[2].add(ident)
 for x in r.results['major_article_coverage']:assert list(map(len,sets[x['population']]))==[x[k] for k in ['indexed_articles','articles_with_noncheck_major','articles_with_any_known_major']]
 dump(R/'metadata_unions_verification.json',dict(passed=True,method='Independent Python exact label unions and Article sets over actual major-topic rows.'));c.close()
if __name__=='__main__':main()
