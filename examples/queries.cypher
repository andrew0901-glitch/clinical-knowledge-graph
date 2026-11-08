// Example Cypher for the Lunas Clinical Evidence KG after loading with scripts/load_neo4j.sh.
// Relationship types are the native Lunas types (from original_predicate): HAS_MESH, CITES,
// AUTHORED_BY, VALIDATED_BY, PARENT_OF, ANCESTOR_OF, STUDIES_CONDITION, TESTS_INTERVENTION, ...
// Run `CALL db.relationshipTypes()` and `CALL db.labels()` to see exactly what was loaded.
//
// IMPORTANT, verified against the real, fully-loaded v0.1.0 graph (not assumed from the schema
// docs -- two of these were backwards in an earlier draft of this file):
//   * VALIDATED_BY is (:Article)-[:VALIDATED_BY]->(:ClinicalTrial) -- the RESULTS ARTICLE is the
//     subject, the TRIAL is the object. To go from a trial to its results publication you must
//     traverse the relationship BACKWARDS: (trial)<-[:VALIDATED_BY]-(article).
//   * PARENT_OF is (narrower/child :MeSHConcept)-[:PARENT_OF]->(broader/parent :MeSHConcept) --
//     e.g. (Zona Fasciculata)-[:PARENT_OF]->(Adrenal Cortex). So `(m)-[:PARENT_OF]->(x)` gives
//     x = m's PARENT (one level UP the hierarchy, toward broader concepts), and
//     `(x)-[:PARENT_OF]->(m)` gives x = one of m's CHILDREN (one level down).
//   * AUTHORED_BY is (:Article)-[:AUTHORED_BY]->(:Author) -- already correct in the original draft.

// Speed up lookups (run once).
CREATE INDEX article_id IF NOT EXISTS FOR (n:Article) ON (n.id);
CREATE INDEX clinicaltrial_id IF NOT EXISTS FOR (n:ClinicalTrial) ON (n.id);
CREATE INDEX mesh_id IF NOT EXISTS FOR (n:MeSHConcept) ON (n.id);
CREATE INDEX mesh_name IF NOT EXISTS FOR (n:MeSHConcept) ON (n.name);
CREATE INDEX medlineplus_name IF NOT EXISTS FOR (n:MedlinePlus) ON (n.name);
CREATE INDEX author_id IF NOT EXISTS FOR (n:Author) ON (n.id);

// 1. What is in the graph
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY n DESC;
MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS n ORDER BY n DESC;

// 2. Articles with a MeSH descriptor as a major topic, most cited first
MATCH (a:Article)-[r:HAS_MESH]->(m:MeSHConcept {name: 'Asthma'})
WHERE r.is_major_topic = true
RETURN a.pmid, a.name AS title, a.journal, a.year, a.cited_by_count
ORDER BY a.cited_by_count DESC LIMIT 25;

// 3. Same, expanded one level down the MeSH hierarchy (descriptor's real children --
//    PARENT_OF points from child to parent, so children are found by reversing the arrow)
MATCH (child:MeSHConcept)-[:PARENT_OF]->(m:MeSHConcept {name: 'Asthma'})
MATCH (a:Article)-[r:HAS_MESH]->(t:MeSHConcept) WHERE (t = m OR t = child) AND r.is_major_topic = true
WITH a, count(DISTINCT t) AS matched, max(CASE WHEN t = m THEN 1 ELSE 0 END) AS direct
RETURN a.pmid, a.name, matched, direct, a.cited_by_count
ORDER BY direct DESC, matched DESC, a.cited_by_count DESC LIMIT 25;

// 4. Trial -> results publication -> who cites it
//    (VALIDATED_BY runs article -> trial, so the trial's results article is found by
//    traversing the relationship backwards: (t)<-[:VALIDATED_BY]-(a))
MATCH (t:ClinicalTrial)<-[:VALIDATED_BY]-(a:Article)
OPTIONAL MATCH (citing:Article)-[:CITES]->(a)
RETURN t.nct_id AS trial, a.pmid, a.name AS results_paper, count(DISTINCT citing) AS cited_in_graph
ORDER BY cited_in_graph DESC LIMIT 25;

// 5. An author's articles and the MeSH topics they cover most (major topics only)
MATCH (a:Article)-[:AUTHORED_BY]->(au:Author) WHERE au.name CONTAINS 'Deveza'
MATCH (a)-[r:HAS_MESH]->(m:MeSHConcept) WHERE r.is_major_topic = true
RETURN au.name, m.name AS topic, count(DISTINCT a) AS articles ORDER BY articles DESC LIMIT 25;

// ---------------------------------------------------------------------------------------------
// The four traversals below were added after real, full-scale validation (see
// docs/VALIDATION_RESULTS.md). Each is runnable as-is; replace the literal parameter values
// (trial NCT id, MedlinePlus topic name, article id, author id) with ones you care about.
// ---------------------------------------------------------------------------------------------

// 6a. Clinical trial -> its results publication (VALIDATED_BY, traversed backwards -- see the
//     note at the top of this file) -> publications that CITE that results publication,
//     restricted to in-graph articles whose NLM publication type marks them as a guideline or
//     systematic review. "Guideline"/"Practice Guideline"/"Systematic Review" are the exact
//     pub_types strings used in this release (verified against the real Article.pub_types data;
//     "Review" and "Scoping Review" also occur but are not guideline/systematic-review types).
MATCH (t:ClinicalTrial {nct_id: 'NCT00825071'})<-[:VALIDATED_BY]-(resultsArticle:Article)
MATCH (citingArticle:Article)-[:CITES]->(resultsArticle)
WHERE any(pt IN citingArticle.pub_types WHERE pt IN ['Guideline', 'Practice Guideline', 'Systematic Review'])
RETURN t.nct_id AS trial, resultsArticle.pmid AS results_pmid, resultsArticle.name AS results_title,
       citingArticle.pmid AS citing_pmid, citingArticle.name AS citing_title,
       citingArticle.pub_types AS citing_pub_types
ORDER BY citingArticle.pmid
LIMIT 50;

// 6b. MedlinePlus topic -> MeSH descriptor (direct HAS_MESH link; MedlinePlus topics carry
//     HAS_MESH edges to MeSHConcept the same way articles do) -> one level DOWN via PARENT_OF
//     to narrower/child descriptors (PubMed's MeSH "explode" behavior: a topic search
//     automatically pulls in narrower terms, not broader ones) -> articles ranked by number of
//     matching MAJOR-TOPIC MeSH descriptors, two-tier: a direct-term match always outranks a
//     hierarchy-expansion-only match, regardless of raw count (ORDER BY direct count first,
//     then hierarchy count).
//       IMPORTANT, verified against the real loaded data with 15 well-known MeSH pairs (e.g.
//       "Cushing Syndrome" -[PARENT_OF]-> "Adrenocortical Hyperfunction", "Adrenal Cortex
//       Diseases" -[PARENT_OF]-> "Adrenal Gland Diseases"), cross-checked against the edges'
//       own parent_tree_numbers/child_tree_numbers properties: PARENT_OF's SUBJECT is always
//       the narrower/child concept and its OBJECT is always the broader/parent concept (despite
//       the type's name). So "one level down to children" is `(child)-[:PARENT_OF]->(matched)`
//       -- the arrow points FROM the child TO the matched/parent descriptor, not the reverse.
//     Check tags (the 40 non-subject NLM qualifiers: Humans, Female, Male, Adult, Animals,
//     age/species/century groups, etc.) are excluded by name -- v0.1.0 carries no is_check_tag
//     flag on (:MeSHConcept) or on HAS_MESH, so the exclusion list below is the real,
//     NLM-published 40-term Check Tags MeSH Terms list (see docs/DATA_NOTES.md).
// NOTE: cypher-shell's `:param` client command must be on a single physical line (a
// multi-line form breaks when run non-interactively via `-f`/`cypher-shell < file`), so the
// 40-item list below is intentionally kept on one line.
:param checkTags => ['Humans', 'Female', 'Male', 'Animals', 'Adult', 'Middle Aged', 'Aged', 'Adolescent', 'Young Adult', 'Mice', 'Child', 'Aged, 80 and over', 'Rats', 'Child, Preschool', 'United States', 'Pregnancy', 'Infant', 'Infant, Newborn', 'Cricetinae', 'Dogs', 'Cats', 'Rabbits', 'Guinea Pigs', 'Sheep', 'Swine', 'Cattle', 'Horses', 'Bees', 'Chick Embryo', 'Chlorocebus aethiops', 'History of Medicine', 'History, Ancient', 'History, Medieval', 'History, 15th Century', 'History, 16th Century', 'History, 17th Century', 'History, 18th Century', 'History, 19th Century', 'History, 20th Century', 'History, 21st Century'];

MATCH (mp:MedlinePlus {name: 'Asthma'})-[:HAS_MESH]->(direct:MeSHConcept)
WHERE NOT direct.name IN $checkTags
WITH collect(DISTINCT direct) AS directTerms
UNWIND directTerms AS d
OPTIONAL MATCH (narrower:MeSHConcept)-[:PARENT_OF]->(d)
WHERE narrower IS NOT NULL AND NOT narrower.name IN $checkTags AND NOT narrower IN directTerms
WITH directTerms, collect(DISTINCT narrower) AS childTerms
MATCH (a:Article)-[r:HAS_MESH]->(term:MeSHConcept)
WHERE r.is_major_topic = true AND (term IN directTerms OR term IN childTerms)
WITH a, (term IN directTerms) AS isDirect
WITH a, count(CASE WHEN isDirect THEN 1 END) AS directMatches,
        count(CASE WHEN NOT isDirect THEN 1 END) AS hierarchyMatches
RETURN a.pmid, a.name AS title, directMatches, hierarchyMatches, a.cited_by_count
ORDER BY directMatches DESC, hierarchyMatches DESC, a.cited_by_count DESC
LIMIT 25;

// 6c. Article -> (CITES relationships plus shared MAJOR-TOPIC MeSH descriptors) -> most-cited
//     in-graph papers reachable this way. "Reachable" = cited by the seed article, cites the
//     seed article, or shares at least one major-topic MeSH descriptor with it; "most-cited" =
//     ranked by in-graph CITES in-degree (how many other graph articles cite that candidate).
MATCH (seed:Article {id: 'PMID:10021452'})
OPTIONAL MATCH (seed)-[:CITES]->(outCite:Article)
OPTIONAL MATCH (inCite:Article)-[:CITES]->(seed)
OPTIONAL MATCH (seed)-[r1:HAS_MESH]->(m:MeSHConcept)<-[r2:HAS_MESH]-(viaMesh:Article)
  WHERE r1.is_major_topic = true AND r2.is_major_topic = true AND viaMesh <> seed
WITH seed, collect(DISTINCT outCite) + collect(DISTINCT inCite) + collect(DISTINCT viaMesh) AS candidates
UNWIND candidates AS cand
WITH DISTINCT cand WHERE cand IS NOT NULL
MATCH (citer:Article)-[:CITES]->(cand)
RETURN cand.pmid AS pmid, cand.name AS title, count(DISTINCT citer) AS cited_in_graph
ORDER BY cited_in_graph DESC
LIMIT 25;

// 6d. Author -> their articles -> aggregate MAJOR-TOPIC MeSH profile for that author
//     (which descriptors recur, with counts).
MATCH (au:Author {id: 'lunasai:openalex_author.A5051827275'})<-[:AUTHORED_BY]-(a:Article)
MATCH (a)-[r:HAS_MESH]->(m:MeSHConcept) WHERE r.is_major_topic = true
RETURN au.name AS author, m.name AS topic, count(DISTINCT a) AS articles
ORDER BY articles DESC
LIMIT 25;
