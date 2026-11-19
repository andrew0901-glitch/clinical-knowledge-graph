"""Independent Python re-score of all headline population/metadata/traversal numbers.
Only raw source-table rows are selected by SQL. Python sets, streamed counters and integer-encoded
pairs implement joins, distinct counts and reachability independently of analytical SQL aggregates.
"""
import array,collections,subprocess,time,sys
from common import *
def main():
 start=time.time();c=connect(True);c.execute('ATTACH ? AS base (READ_ONLY)',[str(C/'independent_audit/audit.duckdb')]);r=json.loads((R/'analysis.json').read_text());raw=json.loads((R/'raw_census.json').read_text());checks=[]
 def check(name,got,want):
  assert got==want,(name,got,want);checks.append(name)
 def rows(sql):
  cur=c.execute(sql)
  while batch:=cur.fetchmany(100000):yield from batch
 # Integer identities share one node dictionary, keeping complete-population pair sets bounded.
 ids={};flags=array.array('H');labels=collections.Counter();entry={p:collections.Counter() for p in ['with_stubs','without_stubs']};pt={p:collections.Counter() for p in entry};article_indices=[]
 for ident,label,stub,name,doi,pmcid,journal,types,majors in rows('SELECT id,label,stub,name,doi,pmcid,journal,pub_types,mesh_major_topics FROM nodes'):
  check_duplicate=ident in ids;assert not check_duplicate,ident;idx=len(flags);ids[ident]=idx;labels[label]+=1;f=0
  if label=='Article':
   f=1|2*bool(stub)|4*bool(pmcid)|8*bool(set(types or [])&{'Guideline','Practice Guideline'})|16*('Systematic Review' in (types or []))|32*bool(set(types or [])&{'Guideline','Practice Guideline','Systematic Review','Meta-Analysis','Review'});article_indices.append(idx)
   for p in entry:
    if p=='without_stubs' and stub:continue
    entry[p].update(articles=1,doi=int(bool(doi)),pmcid=int(bool(pmcid)),title=int(bool(name)),journal=int(bool(journal)),publication_types=int(bool(types)),major_topic_list=int(bool(majors)));pt[p].update(set(types or []))
  flags.append(f)
 N=len(flags);check('node totals',N,raw['totals']['nodes']);check('node family census',dict(labels),raw['counts']['labels'])
 for x in r['entrypoints']:check('entrypoints '+x['population'],dict(entry[x['population']]),{k:v for k,v in x.items() if k!='population'})
 for x in r['publication_types']:check('publication type '+x['population']+' '+x['type'],pt[x['population']][x['type']],x['articles'])
 print('verified raw totals, labels, entrypoints, all publication types',flush=True)
 stop={ids[x[0]] for x in c.execute('SELECT id FROM stop').fetchall()};profiles={};cap={p:[set(),set()] for p in entry};indexed=bytearray(N);majorstats={p:collections.Counter() for p in entry}
 # Independent major-preferred query profiles from actual indexing rows; no SQL profile aggregation.
 last=None;allterms=set();majorterms=set()
 def save(a,allterms,majorterms):
  if a is not None and allterms:profiles[a]=(frozenset(allterms),frozenset(majorterms or allterms),frozenset(majorterms))
 for aid,did,major in rows('SELECT article,descriptor,edge_major FROM am ORDER BY article,descriptor'):
  a=ids[aid];d=ids[did];indexed[a]=1
  if a!=last:save(last,allterms,majorterms);last=a;allterms=set();majorterms=set()
  for p in entry:
   if p=='without_stubs' and flags[a]&2:continue
   majorstats[p][major]+=1
   if d not in stop and flags[a]&32:
    cap[p][0].add(d)
    if major is True:cap[p][1].add(d)
  if d not in stop:
   allterms.add(d)
   if major is True:majorterms.add(d)
 save(last,allterms,majorterms)
 for x in r['major_coverage']:check('major flags '+x['population']+' '+str(x['edge_major']),majorstats[x['population']][x['edge_major']],x['edges'])
 print('independent profiles built',len(profiles),flush=True)
 route=bytearray(N);journalsets={p:[set(),set(),set(),set()] for p in entry};pairsrole=collections.Counter();rolelinks={};rolecounts=collections.Counter()
 for aid,tid,typ in rows('SELECT article,trial,type FROM result_links'):
  a=ids[aid];t=ids[tid];rolecounts[typ]+=1;rolelinks.setdefault(typ,[]).append((a,t))
 for aid,jid,typ in rows("SELECT subject,object,type FROM e WHERE type IN ('PUBLISHED_IN','HAS_PMC_RECORD')"):
  a=ids[aid];j=ids[jid]
  if typ=='HAS_PMC_RECORD':route[a]=1;continue
  for p,v in journalsets.items():
   if p=='without_stubs' and flags[a]&2:continue
   v[0].add(j);v[2].add(a)
   if flags[a]&8:v[1].add(j);v[3].add(a)
 for x in r['journal_population']:
  v=journalsets[x['population']];check('journal population '+x['population'],[labels['Journal'],*map(len,v)],[x['journal_nodes'],x['journals_with_articles'],x['journals_with_guidelines'],x['linked_articles'],x['linked_guidelines']])
 # CITES: independent distinct pairs, incoming citations, guideline hits and shared-MeSH walks.
 cpairs=set();reach=set();incoming=collections.Counter();incoming_without=collections.Counter();cited={p:set() for p in entry};citecounts={p:collections.Counter() for p in entry};citedtargets={p:set() for p in entry};reachseed={p:bytearray(N) for p in entry};reachneighbor={p:bytearray(N) for p in entry};reachcounts=collections.Counter()
 for sid,oid in rows('SELECT subject,object FROM base.c'):
  a=ids[sid];b=ids[oid];nonstub=not(flags[a]&2 or flags[b]&2)
  for p in entry:
   if p=='without_stubs' and not nonstub:continue
   citecounts[p]['citation_edge_rows']+=1;citecounts[p]['self_link_rows']+=a==b;citedtargets[p].add(b)
   if flags[a]&(8|16):cited[p].add(b)
  if a==b:continue
  encoded=a*N+b
  if encoded not in cpairs:
   cpairs.add(encoded);incoming[b]+=1;citecounts['with_stubs']['distinct_nonself_citing_pairs']+=1
   if nonstub:citecounts['without_stubs']['distinct_nonself_citing_pairs']+=1;incoming_without[b]+=1
  pa=profiles.get(a);pb=profiles.get(b)
  if pa is None or pb is None:continue
  for seed,neighbor,yes in [(a,b,not pa[1].isdisjoint(pb[0])),(b,a,not pb[1].isdisjoint(pa[0]))]:
   if not yes:continue
   code=seed*N+neighbor
   if code in reach:continue
   reach.add(code);reachcounts['with_stubs']+=1;reachseed['with_stubs'][seed]=1;reachneighbor['with_stubs'][neighbor]=1
   if nonstub:reachcounts['without_stubs']+=1;reachseed['without_stubs'][seed]=1;reachneighbor['without_stubs'][neighbor]=1
 del cpairs,reach
 check('all in-corpus incoming citation counts',dict(incoming),{ids[a]:n for a,n in c.execute('SELECT * FROM incoming').fetchall()})
 check('nonstub in-corpus incoming citation counts',dict(incoming_without),{ids[a]:n for a,n in c.execute('SELECT * FROM incoming_nonstub').fetchall()})
 for p,counts in [('with_stubs',incoming),('without_stubs',incoming_without)]:
  for i in range(1,4):
   roots={ids[d] for d, in c.execute('SELECT query_descriptor FROM query_terms WHERE seed=?',['article'+str(i)]).fetchall()};matches={a:len(profile[2]&roots) for a,profile in profiles.items() if (p=='with_stubs' or not flags[a]&2) and profile[2]&roots}
   expected=r['whole_field_leaders_'+str(i)+'_'+p];reverse={idx:ident for ident,idx in ids.items() if idx in matches};ordered=sorted(matches,key=lambda a:(-counts[a],reverse[a]))[:20]
   check('whole-field ordered leaders '+str(i)+' '+p,ordered,[ids[x['id']] for x in expected])
   for row in expected:check('whole-field citation/match score '+row['id']+' '+p,[counts[ids[row['id']]],matches[ids[row['id']]]],[row['in_corpus_citations'],row['direct_query_matches']])
 for x in r['citation_denominators']:
  p=x['population'];expected={**citecounts[p], 'articles':entry[p]['articles'],'articles_cited_in_corpus':len(citedtargets[p])};check('citation population '+p,expected,{k:v for k,v in x.items() if k!='population'})
 for x in r['B3_population']:
  p=x['population'];profile_count=sum(not(p=='without_stubs' and flags[a]&2) for a in profiles);check('B3 population '+p,[entry[p]['articles'],profile_count,sum(reachseed[p]),reachcounts[p]],[x['articles'],x['articles_with_query_terms'],x['articles_with_citation_neighbor_and_shared_noncheck_query_term'],x['unique_seed_neighbor_pairs']])
 print('verified all citation/shared-MeSH population metrics',flush=True)
 families={p:{} for p in entry}
 def bits():return bytearray(N)
 for p in entry:
  for family in ['results_publications','results_cited_by_guideline_systematic','background_publications','topic_guidelines_reviews','author_indexed_articles','journal_guidelines']:families[p][family]=bits()
  families[p]['citation_shared_neighbors']=reachneighbor[p]
 for key,sqlkey in [('VALIDATED_BY','B1_population'),('CITES_BACKGROUND','background_population')]:
  for p in entry:
   links=[(a,t) for a,t in rolelinks[key] if not(p=='without_stubs' and flags[a]&2)];aa={a for a,t in links};tt={t for a,t in links};hit=aa&cited[p];target=next(x for x in r[sqlkey] if x['population']==p)
   if key=='VALIDATED_BY':
    got=[labels['ClinicalTrial'],len(tt),len(aa),len(hit),len({t for a,t in links if a in hit})];want=[target[k] for k in ['trials','trials_with_results','result_articles','result_articles_cited_by_guideline_or_systematic_review','trials_with_results_cited_by_guideline_or_systematic_review']];family='results_publications'
    for a in hit:families[p]['results_cited_by_guideline_systematic'][a]=1
   else:got=[labels['ClinicalTrial'],len(links),len(tt),len(aa),len({a*N+t for a,t in links})];want=[target[k] for k in ['trials','edge_rows','trials_with_background','background_articles','pairs']];family='background_publications'
   check(sqlkey+' '+p,got,want)
   for a in aa:families[p][family][a]=1
 # Downward topic coverage: every mapping, actual exported narrower->broader rows only.
 q=collections.defaultdict(set);h=collections.defaultdict(set);child=collections.defaultdict(set)
 for topic,desc in rows('SELECT subject,object FROM tm'):
  if ids[desc] not in stop:q[ids[topic]].add(ids[desc])
 for cid,pid,priority in rows('SELECT child,parent,priority FROM hierarchy'):
  if ids[cid] not in stop:
   h[ids[pid]].add(ids[cid])
   if priority==0:child[ids[pid]].add(ids[cid])
 td={ids[x[0]] for x in c.execute('SELECT object FROM trial_mesh').fetchall()};topic_counts={};topic_all=set()
 for p in entry:
  for mode in ['none','one','full']:
   count=collections.Counter(topics=labels['MedlinePlus'],reaching_guideline_or_review=0,reaching_major_guideline_or_review=0,reaching_condition_trial=0,reaching_both=0,reaching_major_both=0)
   for topic,roots in q.items():
    expanded=set(roots)
    if mode!='none':
     for root in roots:expanded.update(child[root] if mode=='one' else h[root]|child[root])
    gr=not expanded.isdisjoint(cap[p][0]);gm=not expanded.isdisjoint(cap[p][1]);trial=not expanded.isdisjoint(td);count['reaching_guideline_or_review']+=gr;count['reaching_major_guideline_or_review']+=gm;count['reaching_condition_trial']+=trial;count['reaching_both']+=gr and trial;count['reaching_major_both']+=gm and trial
    if mode=='full':topic_all.update(expanded)
   want=next(x for x in r['topic_population'] if x['population']==p and x['mode']==mode);check('topic '+p+' '+mode,dict(count),{k:v for k,v in want.items() if k not in ['population','mode']})
 for a,profile in profiles.items():
  terms=profile[0]
  if flags[a]&32 and not terms.isdisjoint(topic_all):
   families['with_stubs']['topic_guidelines_reviews'][a]=1
   if not flags[a]&2:families['without_stubs']['topic_guidelines_reviews'][a]=1
 # Author reach and Article PMC-route results; Journal result sets independently recorded above.
 authorstats={p:[set(),set(),set(),set()] for p in entry}
 for aid,author,matched in rows('SELECT subject,object,match_status FROM authorship'):
  a=ids[aid];au=ids[author]
  for p,sets in authorstats.items():
   if p=='without_stubs' and flags[a]&2:continue
   sets[0].add(au)
   if indexed[a]:sets[1].add(au)
   if matched=='matched':sets[2].add(au)
   if a in profiles:sets[3].add(au);families[p]['author_indexed_articles'][a]=1
 for x in r['B4_population']:
  v=authorstats[x['population']];check('author population '+x['population'],[labels['Author'],len(v[0]),len(v[1]),len(v[2])],[x['author_nodes'],x['authors_with_authorship'],x['authors_with_indexed_article'],x['authors_with_matched_authorship']])
 for p in entry:
  for a in journalsets[p][3]:families[p]['journal_guidelines'][a]=1
 for x in r['pmc_traversal_coverage']:
  p=x['population'];ii=[a for a in article_indices if families[p][x['traversal']][a]];got=[len(ii),sum(bool(flags[a]&4) for a in ii),sum(bool(route[a]) for a in ii),sum(bool(flags[a]&4 or route[a]) for a in ii)];check('PMC '+p+' '+x['traversal'],got,[x[k] for k in ['articles','pmcid','pmc_link','any_pmc_route']])
 output=dict(passed=True,checks=checks,check_count=len(checks),method='Independent Python joins, set operations, streamed counts, encoded distinct citation/seed-neighbor pairs and actual exported downward hierarchy; SQL only selects primitive source-table rows.',code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),invocation=sys.argv,elapsed_seconds=time.time()-start)
 dump(R/'headline_verification.json',output);print('VERIFIED',len(checks),'population/metadata/traversal headline assertions',flush=True);c.close()
if __name__=='__main__':main()
