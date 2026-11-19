"""Non-self guideline/SR citation control for paper trial-result chains,."""
import collections,subprocess
from common import *
def main():
 c=connect(True);r=Registry(c,'strict_chains')
 r.run('v02',"WITH hit AS (SELECT DISTINCT cc.object article,p.population FROM e cc JOIN article g ON g.id=cc.subject CROSS JOIN populations p WHERE cc.type='CITES' AND cc.subject<>cc.object AND (g.guideline OR g.systematic_review) AND (NOT p.exclude_stubs OR NOT g.stub)) SELECT p.population,(SELECT count(*) FROM nodes WHERE label='ClinicalTrial') trials,count(DISTINCT l.trial) trials_with_results,count(DISTINCT l.article) result_articles,count(DISTINCT l.article) FILTER(WHERE h.article IS NOT NULL) result_articles_cited_by_guideline_or_systematic_review,count(DISTINCT l.trial) FILTER(WHERE h.article IS NOT NULL) trials_with_results_cited_by_guideline_or_systematic_review FROM result_links l JOIN article a ON a.id=l.article CROSS JOIN populations p LEFT JOIN hit h ON h.article=l.article AND h.population=p.population WHERE l.type='VALIDATED_BY' AND (NOT p.exclude_stubs OR NOT a.stub) GROUP BY p.population",'Primary paper definition excludes self-citations and all stub endpoints in without-stubs population; historical B1 without self exclusion is separately retained.')
 r.run('pmc_v02',"WITH hit AS (SELECT DISTINCT cc.object article,p.population FROM e cc JOIN article g ON g.id=cc.subject CROSS JOIN populations p WHERE cc.type='CITES' AND cc.subject<>cc.object AND (g.guideline OR g.systematic_review) AND (NOT p.exclude_stubs OR NOT g.stub)),aa AS (SELECT DISTINCT l.article,p.population FROM result_links l JOIN article a ON a.id=l.article CROSS JOIN populations p JOIN hit h ON h.article=l.article AND h.population=p.population WHERE l.type='VALIDATED_BY' AND (NOT p.exclude_stubs OR NOT a.stub)) SELECT aa.population,count(*) articles,count(*) FILTER(WHERE coalesce(a.pmcid,'')<>'') pmcid,count(*) FILTER(WHERE coalesce(a.pmcid,'')<>'' OR EXISTS(SELECT 1 FROM e WHERE type='HAS_PMC_RECORD' AND subject=a.id)) any_pmc_route FROM aa JOIN article a ON a.id=aa.article GROUP BY 1",'Primary non-self result->guideline/SR chains; PMC metadata route proxy only.')
 # Independently re-score using only primitive rows, with classification and set joins in Python.
 gids={};stub=set()
 for ident,is_stub,types in c.execute('SELECT id,stub,pub_types FROM article').fetchall():
  if is_stub:stub.add(ident)
  if set(types or [])&{'Guideline','Practice Guideline','Systematic Review'}:gids[ident]=is_stub
 hit={p:set() for p in ['with_stubs','without_stubs']};cur=c.execute("SELECT subject,object FROM e WHERE type='CITES' AND subject IN (SELECT unnest(?::VARCHAR[]))",[list(gids)])
 while batch:=cur.fetchmany(100000):
  for a,b in batch:
   if a==b:continue
   hit['with_stubs'].add(b)
   if not gids[a] and b not in stub:hit['without_stubs'].add(b)
 links=c.execute("SELECT article,trial FROM result_links WHERE type='VALIDATED_BY'").fetchall()
 for x in r.results['v02']:
  p=x['population'];selected=[(a,t) for a,t in links if p=='with_stubs' or a not in stub];aa={a for a,t in selected};tt={t for a,t in selected};assert [len(tt),len(aa),len(aa&hit[p]),len({t for a,t in selected if a in hit[p]})]==[x[k] for k in ['trials_with_results','result_articles','result_articles_cited_by_guideline_or_systematic_review','trials_with_results_cited_by_guideline_or_systematic_review']]
 pmcid={x[0] for x in c.execute("SELECT id FROM article WHERE coalesce(pmcid,'')<>''").fetchall()};route=pmcid|{x[0] for x in c.execute("SELECT subject FROM e WHERE type='HAS_PMC_RECORD'").fetchall()}
 for x in r.results['pmc_v02']:
  p=x['population'];aa={a for a,t in links if (p=='with_stubs' or a not in stub) and a in hit[p]};assert [len(aa),len(aa&pmcid),len(aa&route)]==[x[k] for k in ['articles','pmcid','any_pmc_route']]
 c.close()
 dump(R/'strict_chains_verification.json',dict(passed=True,method='Independent Python citing-type lookup, self-link exclusion, stub filtering, PMC-route intersection and result-link set joins for v0.2 (this release).',code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()))
if __name__=='__main__':main()
