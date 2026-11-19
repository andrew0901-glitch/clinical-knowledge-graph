"""Independent full raw KGX census and narrow projections, after manifest verification.
No exporter imports or connectors. Source never written. All retained metadata read from actual keys.
"""
import collections,gzip,hashlib,multiprocessing,orjson,re,time,sys,subprocess
from common import *
NODE_KEYS=['id','name','iri','doi','pmcid','pmid','pub_types','journal','url','year','mesh_major_topics','openalex_id','openalex_author_id','orcid','profile_orcid','nct_id','preferred_term','tree_numbers','issn','issns','issn_l','nlm_id','nlm_unique_id','journal_title','title','iso_abbreviation','medline_abbreviation','openalex_source_id','access_status','is_oa','full_text_available','figure_count','table_count']
EDGE_KEYS=['id','subject','object','predicate','original_predicate','lunasai_layer','is_major_topic','depth','study_aspect','mesh_type','mapping_method','source_predicate','publication_role','reference_type','source_system','source_record_id','source_row_id','source_row_table','assertion_id','also_asserted_by_source_system','currentness_status','source_url','iri','primary_knowledge_source','agent_type','knowledge_level','provenance_id','derivation','match_status','profile_orcid_valid','publication_orcid_valid','identity_flags','author_order']
def nonempty(v):return v is not None and v!='' and v!=[] and v!={}
def work(job):
 kind,i,files,root=job;ct=collections.defaultdict(collections.Counter);numeric={};samples={};file_counts={}
 out=C/(kind+str(i)+'.jsonl')
 with out.open('wb') as dest:
  for entry in files:
   n=0
   with gzip.open(root/entry['path'],'rb') as src:
    for line in src:
     r=orjson.loads(line);n+=1
     if kind=='nodes':
      labels=r.get('lunasai_labels') or [];label='|'.join(labels);stub=r.get('lunasai_layer')=='ctgov_identity_only';ct['labels'][label]+=1;families=[label]
      if 'Article' in labels:families=['Article.all']+(['Article.nonstub'] if not stub else ['Article.stub'])
      for family in families:
       ct[family+'.total']['records']+=1;ct[family+'.keys'].update(r.keys());ct[family+'.nonnull'].update(k for k,v in r.items() if v is not None);ct[family+'.nonempty'].update(k for k,v in r.items() if nonempty(v))
       if family.startswith('Article.'):
        ct[family+'.pub_types'].update(set(r.get('pub_types') or []))
        for k,v in r.items():
         if re.search('community|pagerank|page_rank|betweenness',k,re.I):
          st=numeric.setdefault(family+'|'+k,dict(present=0,null=0,zero=0,minus_one=0,other=0,min=None,max=None));st['present']+=1
          if v is None:st['null']+=1
          elif isinstance(v,(float,int)) and not isinstance(v,bool):
           st['zero' if v==0 else 'minus_one' if v==-1 else 'other']+=1;st['min']=v if st['min'] is None else min(st['min'],v);st['max']=v if st['max'] is None else max(st['max'],v)
          else:st['other']+=1
      ct['node_provenance'][str(bool(r.get('provenance_id')))]+=1
      if label not in samples:samples[label]=r
      projected={k:r.get(k) for k in NODE_KEYS};projected.update(label=label,stub=stub,lunasai_layer=r.get('lunasai_layer'))
      if label in ['Journal','PMCRecord']:projected['props']=orjson.dumps(r).decode()
     else:
      typ=r.get('original_predicate','').rsplit('.',1)[-1];ct['types'][typ]+=1;ct[typ+'.keys'].update(r.keys());ct[typ+'.nonnull'].update(k for k,v in r.items() if v is not None);ct['edge_provenance'][str(bool(r.get('provenance_id')))]+=1;ct['edge_knowledge'][str(r.get('knowledge_level'))+'|'+str(r.get('agent_type'))]+=1;ct['edge_derivation'][str(r.get('derivation'))]+=1;ct['edge_primary_source'][str(r.get('primary_knowledge_source'))]+=1
      if typ=='HAS_MESH':
       family='Article' if r['subject'].startswith('PMID:') else 'Trial' if r['subject'].startswith('clinicaltrials:') else 'Other';ct['mesh_major'][family+'|'+str(r.get('is_major_topic','MISSING'))]+=1;ct['mesh_semantics'][family+'|'+str(r.get('study_aspect'))+'|'+str(r.get('mesh_type'))]+=1
      if typ not in samples:samples[typ]=r
      projected={k:r.get(k) for k in EDGE_KEYS};projected['type']=typ
     dest.write(orjson.dumps(projected)+b'\n')
   file_counts[entry['path']]=n;print('scanned',entry['path'],n,flush=True)
 return dict(counts=ct,numeric=numeric,samples=samples,file_counts=file_counts)
def main():
 start=time.time();verify=json.loads((R/'input_verification.json').read_text());assert verify['passed'];root=DATA;assert hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest()==verify['manifest_sha256'];m=json.loads((R/'source_manifest.json').read_text());jobs=[]
 for kind in ['nodes','edges']:
  for i in range(4):jobs.append((kind,i,m[kind][i::4],root))
 with multiprocessing.get_context('fork').Pool(4) as pool:results=pool.map(work,jobs)
 ct=collections.defaultdict(collections.Counter);numeric={};samples={};counts={}
 for r in results:
  for k,v in r['counts'].items():ct[k].update(v)
  for k,v in r['numeric'].items():
   st=numeric.setdefault(k,dict(present=0,null=0,zero=0,minus_one=0,other=0,min=None,max=None))
   for n in ['present','null','zero','minus_one','other']:st[n]+=v[n]
   for n,fn in [('min',min),('max',max)]:
    if v[n] is not None:st[n]=v[n] if st[n] is None else fn(st[n],v[n])
  samples.update(r['samples']);counts.update(r['file_counts'])
 disagreements={e['path']:dict(expected=e['records'],observed=counts[e['path']]) for kind in ['nodes','edges'] for e in m[kind] if counts[e['path']]!=e['records']}
 totals={kind:sum(counts[e['path']] for e in m[kind]) for kind in ['nodes','edges']}
 dump(R/'raw_census.json',dict(counts=ct,numeric=numeric,samples=samples,file_counts=counts,totals=totals,manifest_count_disagreements=disagreements,elapsed_seconds=time.time()-start,code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),invocation=sys.argv));print('RAW CENSUS COMPLETE',totals,'file disagreements',disagreements,flush=True)
if __name__=='__main__':main()
