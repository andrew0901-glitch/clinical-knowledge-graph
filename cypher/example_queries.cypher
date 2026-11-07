// Example queries against the Lunas Clinical Evidence KG v0.1.0 core export.
// Relationship types actually present in v0.1.0 (per manifest.json counts.edges_by_type):
// ANCESTOR_OF, AUTHORED_BY, CITES, CONDUCTED_AT, HAS_LANGUAGE_RESOURCE, HAS_MESH,
// HAS_RIGHTS_EVIDENCE, HAS_USE_GRANT, IN_TOPIC_GROUP, LINKS_TO_RESOURCE, PARENT_OF,
// RELATED_TOPIC, RESOURCE_TRANSLATION_OF, SPONSORED_BY, TRANSLATION_OF, VALIDATED_BY.

// 1. Sanity check: node/edge counts by type, compare against manifest.json.
MATCH (n) RETURN labels(n) AS labels, count(*) AS n ORDER BY n DESC;
CALL db.relationshipTypes() YIELD relationshipType
CALL apoc.cypher.run('MATCH ()-[r:`' + relationshipType + '`]->() RETURN count(r) AS c', {})
YIELD value
RETURN relationshipType, value.c AS count ORDER BY count DESC;

// 2. A highly-cited, highly co-authored Article and its immediate neighborhood.
MATCH (a:Article)
WHERE a.cited_by_count IS NOT NULL
RETURN a.id, a.name, a.year, a.cited_by_count, a.pagerank_score
ORDER BY a.cited_by_count DESC
LIMIT 10;

// 3. Authors of a given Article.
MATCH (a:Article {id: "PMID:10203632"})<-[:AUTHORED_BY]-(auth:Author)
RETURN auth.id, auth.name;

// 4. MeSH indexing for an Article.
MATCH (a:Article {id: "PMID:10203632"})-[:HAS_MESH]->(m:MeSHConcept)
RETURN m.mesh_id, m.preferred_term;

// 5. Citation neighborhood (one hop in, one hop out) of an Article.
MATCH (a:Article {id: "PMID:10203632"})
OPTIONAL MATCH (a)-[:CITES]->(cited:Article)
OPTIONAL MATCH (citing:Article)-[:CITES]->(a)
RETURN a.id AS article,
       count(DISTINCT cited) AS n_cites_out,
       count(DISTINCT citing) AS n_cited_by_in;

// 6. A ClinicalTrial, its sponsor, sites, and any validating Article.
MATCH (ct:ClinicalTrial)
OPTIONAL MATCH (ct)-[:SPONSORED_BY]->(sp:Sponsor)
OPTIONAL MATCH (ct)-[:CONDUCTED_AT]->(site:TrialSite)
OPTIONAL MATCH (art:Article)-[:VALIDATED_BY]->(ct)
RETURN ct.nct_id, ct.name, sp.name AS sponsor,
       count(DISTINCT site) AS n_sites, count(DISTINCT art) AS n_validating_articles
LIMIT 10;

// 7. MeSH tree traversal: descendants of a MeSH concept via PARENT_OF.
MATCH (root:MeSHConcept {mesh_id: "MESH:D000818"})
MATCH (root)-[:PARENT_OF*1..3]->(descendant:MeSHConcept)
RETURN DISTINCT descendant.mesh_id, descendant.preferred_term
LIMIT 25;

// 8. MedlinePlus consumer-health topic and the clinical concepts it explains/links.
MATCH (topic:MedlinePlus)
OPTIONAL MATCH (topic)-[:HAS_MESH]->(m:MeSHConcept)
OPTIONAL MATCH (topic)-[:LINKS_TO_RESOURCE]->(res)
RETURN topic.id, topic.name, collect(DISTINCT m.preferred_term)[0..5] AS mesh_terms,
       count(DISTINCT res) AS n_linked_resources
LIMIT 10;

// 9. Every relationship type present at least once (completeness check for a sample build).
CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType;

// 10. Rights/provenance check on an Article (HAS_RIGHTS_EVIDENCE / HAS_USE_GRANT).
MATCH (a:Article {id: "PMID:10203632"})
OPTIONAL MATCH (a)-[:HAS_RIGHTS_EVIDENCE]->(ev)
OPTIONAL MATCH (a)-[:HAS_USE_GRANT]->(grant)
RETURN a.id, count(DISTINCT ev) AS n_rights_evidence, count(DISTINCT grant) AS n_use_grants;
