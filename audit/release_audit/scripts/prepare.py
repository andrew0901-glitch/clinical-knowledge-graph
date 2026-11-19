"""Build auditable local SQL tables solely from verified KGX projections; exact SQL recorded."""
import sys
from common import *
from seed_data import STOP_NAMES,SEEDS
NODE_COLS={k:'VARCHAR' for k in ['id','label','lunasai_layer','name','iri','doi','pmcid','pmid','journal','url','year','openalex_id','openalex_author_id','orcid','profile_orcid','nct_id']};NODE_COLS.update(stub='BOOLEAN',pub_types='VARCHAR[]',mesh_major_topics='VARCHAR[]',props='JSON')
EDGE_COLS={k:'VARCHAR' for k in ['id','subject','object','type','predicate','original_predicate','lunasai_layer','study_aspect','mesh_type','mapping_method','source_predicate','publication_role','reference_type','source_system','source_record_id','source_row_id','source_row_table','assertion_id','currentness_status','source_url','iri','primary_knowledge_source','agent_type','knowledge_level','provenance_id','derivation','match_status']};EDGE_COLS.update(is_major_topic='BOOLEAN',depth='INTEGER',also_asserted_by_source_system='VARCHAR[]',profile_orcid_valid='BOOLEAN',publication_orcid_valid='BOOLEAN',identity_flags='VARCHAR[]',author_order='INTEGER')
def main():
 census=json.loads((R/'raw_census.json').read_text());assert not census['manifest_count_disagreements'];c=connect();prep=[]
 def create(sql,params=None):c.execute(sql,params or []);prep.append(dict(sql=sql,parameters=params or []));dump(R/'preparation_queries.json',prep);print(sql[:75],flush=True)
 create("CREATE OR REPLACE TABLE nodes AS SELECT * REPLACE(CASE WHEN json_type(props)='VARCHAR' THEN json_extract_string(props,'$')::JSON ELSE props END AS props) FROM read_json(?,format='newline_delimited',columns="+str(NODE_COLS)+")",[str(C/'nodes*.jsonl')])
 create("CREATE OR REPLACE TABLE e AS SELECT * FROM read_json(?,format='newline_delimited',columns="+str(EDGE_COLS)+")",[str(C/'edges*.jsonl')])
 # A separate read-only citation/core DB matches prior public-analysis interfaces; no production DB.
 B=C/'independent_audit';B.mkdir(exist_ok=True);create('ATTACH ? AS base_build',[str(B/'audit.duckdb')])
 create("CREATE OR REPLACE TABLE base_build.c AS SELECT id,subject,object,predicate FROM e WHERE type='CITES'")
 create("CREATE OR REPLACE TABLE base_build.core AS SELECT id,subject article,object trial,coalesce(publication_role,reference_type) reference_type FROM e WHERE type='VALIDATED_BY'")
 create('DETACH base_build');create('ATTACH ? AS base (READ_ONLY)',[str(B/'audit.duckdb')])
 create("CREATE OR REPLACE TABLE article AS SELECT *,coalesce(list_has_any(pub_types,['Practice Guideline','Guideline']),false) guideline,coalesce(list_contains(pub_types,'Systematic Review'),false) systematic_review,coalesce(list_has_any(pub_types,['Practice Guideline','Guideline','Systematic Review','Meta-Analysis','Review']),false) gr,CASE WHEN list_has_any(pub_types,['Practice Guideline','Guideline']) THEN 1 WHEN list_contains(pub_types,'Systematic Review') THEN 2 WHEN list_contains(pub_types,'Meta-Analysis') THEN 3 WHEN list_contains(pub_types,'Review') THEN 4 ELSE 5 END publication_priority FROM nodes WHERE label='Article'")
 create("CREATE OR REPLACE TABLE populations AS SELECT * FROM (VALUES ('with_stubs',false),('without_stubs',true)) p(population,exclude_stubs)")
 create('CREATE OR REPLACE TABLE stop(id VARCHAR,name VARCHAR)');create("INSERT INTO stop SELECT id,name FROM nodes WHERE label='MeSHConcept' AND name IN (SELECT unnest(?::VARCHAR[]))",[STOP_NAMES])
 create("CREATE OR REPLACE TABLE am AS SELECT e.subject article,e.object descriptor,e.id edge_id,e.is_major_topic edge_major,e.is_major_topic major,CASE WHEN array_length(a.mesh_major_topics)>0 THEN list_contains(a.mesh_major_topics,d.name) ELSE NULL END node_label_major,CASE WHEN e.is_major_topic IS NOT NULL THEN 'edge_flag' ELSE 'unknown' END major_source,EXISTS(SELECT 1 FROM stop s WHERE s.id=e.object) check_tag FROM e JOIN article a ON a.id=e.subject JOIN nodes d ON d.id=e.object AND d.label='MeSHConcept' WHERE e.type='HAS_MESH'")
 create("CREATE OR REPLACE TABLE tm AS SELECT e.id,e.subject,e.object,e.is_major_topic edge_major FROM e JOIN nodes n ON n.id=e.subject AND n.label='MedlinePlus' WHERE e.type='HAS_MESH'")
 create("CREATE OR REPLACE TABLE trial_qualified AS SELECT * FROM e WHERE type='HAS_MESH' AND starts_with(subject,'clinicaltrials:')")
 create("CREATE OR REPLACE TABLE trial_mesh AS SELECT * FROM trial_qualified WHERE study_aspect='condition' AND mesh_type='mesh-list'")
 create("CREATE OR REPLACE TABLE authorship AS SELECT * FROM e WHERE type='AUTHORED_BY'")
 create("CREATE OR REPLACE TABLE hierarchy AS SELECT subject child,object parent,id edge_id,CASE WHEN type='HAS_BROADER' THEN 1 ELSE depth END depth,CASE WHEN type='HAS_BROADER' THEN 0 ELSE 1 END priority,predicate FROM e WHERE type IN ('HAS_BROADER','HAS_BROADER_ANCESTOR')")
 create("CREATE OR REPLACE TABLE incoming AS SELECT object article,count(DISTINCT subject) in_corpus_citations FROM base.c WHERE subject<>object GROUP BY object")
 create("CREATE OR REPLACE TABLE modes AS SELECT * FROM (VALUES ('none',0),('one',1),('full',2)) t(mode,level)")
 oldseeds=SEEDS;create('CREATE OR REPLACE TABLE seeds(key VARCHAR,kind VARCHAR,id VARCHAR,area VARCHAR,term VARCHAR)')
 for s in oldseeds:create('INSERT INTO seeds VALUES (?,?,?,?,?)',[s['key'],s['kind'],s['id'],s['area'],s['term']])
 assert c.execute('SELECT count(*) FROM seeds s LEFT JOIN nodes n ON n.id=s.id WHERE n.id IS NULL').fetchone()[0]==0
 create("CREATE OR REPLACE TABLE query_terms AS SELECT DISTINCT s.key seed,m.descriptor query_descriptor FROM seeds s JOIN am m ON m.article=s.id WHERE s.kind='article' AND m.edge_major IS TRUE AND NOT m.check_tag UNION SELECT DISTINCT s.key,t.object FROM seeds s JOIN tm t ON t.subject=s.id WHERE s.kind='topic' AND NOT EXISTS(SELECT 1 FROM stop WHERE id=t.object)")
 create("CREATE OR REPLACE TABLE source_terms AS SELECT a.* FROM am a WHERE NOT check_tag AND (a.major OR NOT EXISTS(SELECT 1 FROM am x WHERE x.article=a.article AND x.major AND NOT x.check_tag))")
 create("CREATE OR REPLACE TABLE profiles AS SELECT a.article,list(DISTINCT a.descriptor) indexed_terms,list(DISTINCT s.descriptor) FILTER(WHERE s.descriptor IS NOT NULL) source_terms FROM am a LEFT JOIN source_terms s ON s.article=a.article AND s.descriptor=a.descriptor WHERE NOT a.check_tag GROUP BY a.article")
 create("CREATE OR REPLACE TABLE topic_expansion AS WITH q AS (SELECT DISTINCT subject topic,object descriptor FROM tm WHERE NOT EXISTS(SELECT 1 FROM stop WHERE id=object)),raw AS (SELECT q.topic,q.descriptor query_descriptor,m.mode,q.descriptor matched_descriptor,0 distance,NULL::VARCHAR hierarchy_edge FROM q CROSS JOIN modes m UNION ALL SELECT q.topic,q.descriptor,m.mode,h.child,h.depth,h.edge_id FROM q JOIN hierarchy h ON h.parent=q.descriptor CROSS JOIN modes m WHERE (m.level=2 OR (m.level=1 AND h.priority=0)) AND NOT EXISTS(SELECT 1 FROM stop WHERE id=h.child)) SELECT * FROM raw QUALIFY row_number() OVER(PARTITION BY topic,mode,query_descriptor,matched_descriptor ORDER BY distance,hierarchy_edge)=1")
 create("CREATE OR REPLACE TABLE result_links AS SELECT id,subject article,object trial,type,coalesce(publication_role,reference_type) role FROM e WHERE type IN ('VALIDATED_BY','CITES_BACKGROUND','HAS_DERIVED_PUBLICATION')")
 create("CREATE OR REPLACE TABLE annotation_capability AS SELECT descriptor,bool_or(a.gr) gr,bool_or(a.gr AND m.edge_major) gr_major FROM am m JOIN article a ON a.id=m.article GROUP BY descriptor")
 # Retain actual raw analytics columns for all original consistency checks (source is manifest-verified).
 ac=['community_id','community_id_coarse','community_id_mesh','community_size','community_size_coarse','community_size_mesh','pagerank_score','betweenness_score'];cols=dict(id='VARCHAR',**{x:'DOUBLE' for x in ac});manifest=json.loads((R/'source_manifest.json').read_text());root=DATA
 create("CREATE OR REPLACE TABLE analytics AS SELECT * FROM read_json(?,format='newline_delimited',columns="+str(cols)+") WHERE starts_with(id,'PMID:')",[[str(root/e['path']) for e in manifest['nodes']]])
 c.close();print('PREPARED',flush=True)
if __name__=='__main__':main()
