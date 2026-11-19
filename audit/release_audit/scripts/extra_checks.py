"""Direct raw-KGX re-read of source qualifiers/ORCID evidence omitted from narrow projections."""
from common import *
def main():
 c=duckdb.connect();c.execute("SET threads=4;SET memory_limit='8GB'");reg=Registry(c,'extra');m=json.loads((R/'source_manifest.json').read_text());root=DATA;files=[str(root/e['path']) for e in m['edges']]
 sql="""WITH raw AS (SELECT * FROM read_json(?,format='newline_delimited',columns={subject:'VARCHAR',object:'VARCHAR',original_predicate:'VARCHAR',study_aspect:'VARCHAR',mesh_type:'VARCHAR',match_method:'VARCHAR',source_table:'VARCHAR',profile_orcid:'VARCHAR'})),selected AS (SELECT *,original_predicate='lunasai:vocab.AUTHORED_BY' author FROM raw WHERE original_predicate='lunasai:vocab.AUTHORED_BY' OR (original_predicate='lunasai:vocab.HAS_MESH' AND starts_with(subject,'clinicaltrials:'))) SELECT author,study_aspect,mesh_type,match_method,source_table,count(*) edges,count(DISTINCT object) FILTER(WHERE coalesce(profile_orcid,'')<>'') author_ids_with_orcid_on_edge FROM selected GROUP BY 1,2,3,4,5 ORDER BY 1,2,3"""
 reg.run('qualifiers_and_orcid',sql,'Full raw edge reread; condition/intervention and source expansion retained. ORCID evidence on an authorship is separate from Author node completeness.',[files]);c.close()
if __name__=='__main__':main()
