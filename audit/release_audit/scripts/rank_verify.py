"""Independent Python re-score, DF/IDF calculation, subtree attribution and metric verification."""
import collections,math,subprocess,sys,hashlib
from common import *
import common
D=C
POPULATION=os.environ.get("ARTICLE_POPULATION","with_stubs")
assert POPULATION in ["with_stubs","without_stubs"]
R=P/"results"/POPULATION;R.mkdir(exist_ok=True);T=P/"tables"/POPULATION;T.mkdir(exist_ok=True);common.R=R
def filter_population(con):
 if POPULATION=="without_stubs":
  con.execute("CREATE TEMP TABLE am AS SELECT m.* FROM am m JOIN article a ON a.id=m.article WHERE NOT a.stub")
  con.execute("CREATE TEMP TABLE article AS SELECT * FROM article WHERE NOT stub")
  con.execute("CREATE TEMP TABLE nodes AS SELECT * FROM nodes WHERE NOT stub")
  con.execute("CREATE TEMP TABLE incoming AS SELECT cc.object article,count(DISTINCT cc.subject) in_corpus_citations FROM base.c cc JOIN article a ON a.id=cc.subject JOIN article b ON b.id=cc.object WHERE cc.subject<>cc.object GROUP BY cc.object")
def main():
 con=duckdb.connect(str(D/'analysis.duckdb'),read_only=True);con.execute("SET threads=4;SET memory_limit='8GB'");con.execute('ATTACH ? AS base (READ_ONLY)',[str(C/'independent_audit/audit.duckdb')]);filter_population(con);r=json.loads((R/'ranking_variants.json').read_text());stop={x[0] for x in con.execute('SELECT id FROM stop').fetchall()};qt=collections.defaultdict(set)
 for seed,kind,sid,area,term in con.execute('SELECT * FROM seeds ORDER BY key').fetchall():
  rows=con.execute('SELECT object FROM tm WHERE subject=?',[sid]).fetchall() if kind=='topic' else con.execute('SELECT descriptor FROM am WHERE article=? AND edge_major IS TRUE',[sid]).fetchall()
  qt[seed]={d for d, in rows if d not in stop}
 assert {(s,q) for s in qt for q in qt[s]}=={(x['seed'],x['query_descriptor']) for x in r['query_sets']}
 hier=con.execute('SELECT child,parent,depth,priority FROM hierarchy').fetchall();byparent=collections.defaultdict(set);children=collections.defaultdict(set)
 for child,parent,depth,priority in hier:
  byparent[parent].add(child)
  if priority==0:children[parent].add(child)
 maps={};terms=set();branches={}
 for seed in qt:
  for mode in ['none','one','full']:
   m={(q,q):0 for q in qt[seed]}
   if mode!='none':
    for child,parent,depth,priority in hier:
     if parent in qt[seed] and child not in stop and (mode=='full' or priority==0):m[parent,child]=min(depth,m.get((parent,child),depth))
   maps[seed,mode]=m;terms.update(d for q,d in m)
   for (q,d),depth in m.items():
    if depth>0:branches[seed,q,d]={(q,b) for b in children[q] if b not in stop and (d==b or d in byparent[b])}
 # Independent document-frequency census: stream raw cache edges; deduplicate adjacent (descriptor,
 # Article) pairs in Python. No SQL COUNT DISTINCT, SQL log or SQL IDF reused.
 actual={(x['seed'],x['mode'],x['query_descriptor'],x['matched_descriptor']) for x in r['idf_terms']};expected={(seed,mode,q,d) for (seed,mode),mapping in maps.items() for q,d in mapping};assert actual==expected,'Full expansion mapping differs'
 for x in r['expansion_counts']:
  mm=maps[x['seed'],x['mode']];assert [len({q for q,d in mm}),len({d for q,d in mm}),len(mm)]==[x['query_descriptors'],x['expanded_descriptors'],x['descriptor_map_rows']]
 incidence=collections.defaultdict(set);df=collections.Counter();docs=set();pairs=0;last=None
 cur=con.execute('SELECT descriptor,article FROM am WHERE edge_major IS TRUE ORDER BY descriptor,article')
 while batch:=cur.fetchmany(100000):
  for descriptor,article in batch:
   pair=descriptor,article
   if descriptor in stop or pair==last:continue
   last=pair;df[descriptor]+=1;docs.add(article);pairs+=1
   if descriptor in terms:incidence[descriptor].add(article)
 N=len(docs);assert r['idf_denominator']==[dict(descriptors=len(df),distinct_article_descriptor_pairs=pairs,documents=N)]
 weights={d:1+math.log((N+1)/(v+1)) for d,v in df.items()};del docs
 for row in r['idf_terms']:
  if row['df'] is None:assert df[row['matched_descriptor']]==0;continue
  assert row['df']==df[row['matched_descriptor']];assert abs(row['idf']-weights[row['matched_descriptor']])<1e-12
 candidates={};all_scores={};attrs={};allbranches={};allterms={}
 for seed,kind,sid,area,term in con.execute('SELECT * FROM seeds ORDER BY key').fetchall():
  allowed=None
  if kind=='article':allowed={x[0] for x in con.execute('SELECT object FROM base.c WHERE subject=? UNION SELECT subject FROM base.c WHERE object=?',[sid,sid]).fetchall()}-{sid}
  for mode in ['none','one','full']:
   raw=collections.defaultdict(lambda:collections.defaultdict(list));article_branches=collections.defaultdict(set);unresolved=collections.Counter();article_terms=collections.defaultdict(set)
   for (q,d),depth in maps[seed,mode].items():
    for a in incidence[d]:
     if allowed is not None and a not in allowed:continue
     raw[a][q].append((depth,d));article_terms[a].add(d)
     if depth>0:
      bs=branches[seed,q,d];article_branches[a].update(bs)
      if not bs:unresolved[a]+=1
   scores={}
   for a,matches in raw.items():
    closest=[min(v) for v in matches.values()];tier=[sum(d==0 for d,t in closest),sum(d==1 for d,t in closest),sum(d>1 for d,t in closest)]
    chosen=[min(v,key=lambda x:(x[0]!=0,-weights[x[1]],x[0],x[1])) for v in matches.values()]
    direct_idf=round(math.fsum(weights[t] for d,t in chosen if d==0),12);narrow_idf=round(math.fsum(weights[t] for d,t in chosen if d>0),12)
    scores[a]=(*tier,tier[1]+tier[2],direct_idf,narrow_idf)
    attrs[seed,mode,a]=dict(single_subtree_only=tier[0]==0 and len(article_branches[a])==1 and unresolved[a]==0,branches=len(article_branches[a]),unresolved=unresolved[a],direct=tier[0])
   key=seed,mode;candidates[key]=set(scores);all_scores[key]=scores;allbranches[key]=article_branches;allterms[key]=article_terms
 articles=set().union(*candidates.values());citations=dict(con.execute('SELECT * FROM incoming WHERE article IN (SELECT unnest(?::VARCHAR[]))',[sorted(articles)]).fetchall());tops={};cases=0
 for key,scores in all_scores.items():
  for variant in ['current','count','idf']:
   def ordering(a):
    d,o,b,n,di,ni=scores[a];tiers=(d,o,b) if variant=='current' else (d,n) if variant=='count' else (di,ni)
    return tuple(-v for v in tiers)+(-citations.get(a,0),a)
   ordered=sorted(scores,key=ordering)[:100];seed,mode=key;sql=[x for x in r['top100'] if x['seed']==seed and x['mode']==mode and x['variant']==variant];assert ordered==[x['article'] for x in sql],(key,variant)
   for row in sql:
    a=row['article'];s=scores[a];assert list(s[:4])==[row['direct_matches'],row['one_matches'],row['deeper_matches'],row['narrow_matches']];assert abs(s[4]-row['direct_idf'])<2e-12;assert abs(s[5]-row['narrow_idf'])<2e-12
    for k in ['single_subtree_only','branches','unresolved']:assert row[k]==attrs[seed,mode,a][k]
   for k in [20,100]:tops[seed,mode,variant,k]=ordered[:k]
   cases+=1
 for x in r['candidate_mode_overlap']:
  ca=candidates[x['seed'],x['mode_a']];cb=candidates[x['seed'],x['mode_b']];assert [len(ca&cb),len(ca),len(cb)]==[x['intersection'],x['count_a'],x['count_b']]
 for x in r['toplist_mode_overlap']:
  ca=set(tops[x['seed'],x['mode_a'],x['variant'],x['k']]);cb=set(tops[x['seed'],x['mode_b'],x['variant'],x['k']]);assert [len(ca&cb),len(ca),len(cb)]==[x['intersection'],x['count_a'],x['count_b']]
 for row in r['list_metrics']:
  key=row['seed'],row['mode'],row['variant'],row['k'];aa=[attrs[key[0],key[1],a] for a in tops[key]];expected=dict(list_size=len(aa),single_subtree_only_count=sum(a['single_subtree_only'] for a in aa),hierarchy_only_count=sum(a['direct']==0 for a in aa),multi_branch_hierarchy_only_count=sum(a['direct']==0 and a['branches']>1 for a in aa),unresolved_hierarchy_only_count=sum(a['direct']==0 and a['unresolved']>0 for a in aa))
  for k,v in expected.items():assert row[k]==v,(key,k)
  assert abs(row['single_subtree_only_share']-expected['single_subtree_only_count']/len(aa))<1e-15
 for row in r['top20_overlap']:
  key=row['seed'],row['mode'];assert len(set(tops[*key,row['variant'],20])&set(tops[*key,'current',20]))==row['intersection']
 # Independently derive the complete top-five branch and descriptor incidence lists, including
 # empty cases; therefore verifies zero concentration instead of silently dropping empty lists.
 hub_cases=0
 for key,articles in tops.items():
  seed,mode,variant,k=key;branchcounts=collections.Counter();onlycounts=collections.Counter();descriptorcounts=collections.Counter()
  for a in articles:
   for b in allbranches[seed,mode][a]:
    branchcounts[b]+=1
    if attrs[seed,mode,a]['direct']==0:onlycounts[b]+=1
   descriptorcounts.update(allterms[seed,mode][a]-qt[seed])
  expected=sorted(branchcounts,key=lambda b:(-branchcounts[b],b))[:5];sql=[x for x in r['branch_hubs'] if (x['seed'],x['mode'],x['variant'],x['k'])==key];assert expected==[(x['query_descriptor'],x['branch']) for x in sql],key
  for x in sql:
   b=x['query_descriptor'],x['branch'];assert x['top_list_incidence']==branchcounts[b];assert x['hierarchy_only_incidence']==onlycounts[b];assert x['list_size']==len(articles)
  expected=sorted(descriptorcounts,key=lambda t:(-descriptorcounts[t],t))[:5];sql=[x for x in r['descriptor_hubs'] if (x['seed'],x['mode'],x['variant'],x['k'])==key];assert expected==[x['matched_descriptor'] for x in sql],key
  for x in sql:assert x['top_list_incidence']==descriptorcounts[x['matched_descriptor']];assert x['list_size']==len(articles)
  hub_cases+=1
 output=dict(passed=True,ranking_cases=cases,list_and_hub_cases=hub_cases,documents=N,distinct_major_article_descriptor_pairs=pairs,checks=['complete query/expanded descriptor maps and fan-out','candidate and top-list intersections across modes','all six complete query sets','Python distinct-pair DF and document census','Python math.log IDF for all matching descriptors','all exact top-100 orders','all top-100 count and IDF scores','all subtree-only and multi-branch attributions','top-20 overlap against current','all top-20/top-100 share denominators','complete top-five branch and descriptor hub lists, including zero cases'],method='Independent Python sets, counters and dictionary scoring; SQL only reads source rows. No SQL aggregation/window/IDF results used to score or classify.',population=POPULATION,code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),invocation=sys.argv,script_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
 dump(R/'ranking_variants_verification.json',output);con.close();print(output,flush=True)
if __name__=='__main__':main()
