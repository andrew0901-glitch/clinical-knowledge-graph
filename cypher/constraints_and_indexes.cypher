// Constraints + indexes for the Lunas Clinical Evidence KG v0.1.0 core export.
// Run once, before (or right after) the first load. Idempotent (IF NOT EXISTS).
//
// Every KGX node carries a globally-unique `id` (a CURIE, e.g. "PMID:10203632").
// Node labels present in the v0.1.0 core export (per manifest.json nodes_by_label):
// Article, Author, ClinicalTrial, ExternalResource, License, MeSHConcept,
// MedlinePlus, MedlinePlusGroup, RightsPolicy, Sponsor, TrialSite.

// Every node also carries the extra label :KGXNode (added by the loader), purely
// so that edge-loading MATCH (s:KGXNode {id: ...}) queries can hit a single
// label-scoped index instead of a full node scan -- Neo4j community edition has
// no label-free index. Required for the full load to finish in reasonable time.
CREATE CONSTRAINT kgxnode_id IF NOT EXISTS FOR (n:KGXNode) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT article_id IF NOT EXISTS FOR (n:Article) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT author_id IF NOT EXISTS FOR (n:Author) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT clinicaltrial_id IF NOT EXISTS FOR (n:ClinicalTrial) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT externalresource_id IF NOT EXISTS FOR (n:ExternalResource) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT license_id IF NOT EXISTS FOR (n:License) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT meshconcept_id IF NOT EXISTS FOR (n:MeSHConcept) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT medlineplus_id IF NOT EXISTS FOR (n:MedlinePlus) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT medlineplusgroup_id IF NOT EXISTS FOR (n:MedlinePlusGroup) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT rightspolicy_id IF NOT EXISTS FOR (n:RightsPolicy) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT sponsor_id IF NOT EXISTS FOR (n:Sponsor) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT trialsite_id IF NOT EXISTS FOR (n:TrialSite) REQUIRE n.id IS UNIQUE;

// Convenience lookup indexes (native identifiers / common filters).
CREATE INDEX article_pmid IF NOT EXISTS FOR (n:Article) ON (n.pmid);
CREATE INDEX article_year IF NOT EXISTS FOR (n:Article) ON (n.year);
CREATE INDEX article_community_mesh IF NOT EXISTS FOR (n:Article) ON (n.community_id_mesh);
CREATE INDEX clinicaltrial_nct IF NOT EXISTS FOR (n:ClinicalTrial) ON (n.nct_id);
CREATE INDEX meshconcept_mesh_id IF NOT EXISTS FOR (n:MeSHConcept) ON (n.mesh_id);
