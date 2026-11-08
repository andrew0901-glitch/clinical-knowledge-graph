# Data notes for v0.1.0

Things to know before analysing the graph. Each will be addressed or documented further in later releases.

## Relationship types: use `original_predicate`

Every edge has a Biolink `predicate` and a native `original_predicate` (for example `lunasai:vocab.CITES`). Many relationship types share the generic Biolink predicate `biolink:related_to`, so filtering on `predicate` alone mixes citations, authorship and other relationships. Filter on `original_predicate`. The loaders in this repository do this automatically.

## Core graph versus sidecars

- **Core graph** (`nodes/`, `edges/`): source-asserted relationships from PubMed, MeSH, OpenAlex, ClinicalTrials.gov and MedlinePlus, plus MeSH hierarchy relationships derived from the published MeSH tree.
- **`ctgov_publications.jsonl`**: about 1.09 million (trial, PMID) pairs covering every publication ClinicalTrials.gov associates with a trial. The core graph's `VALIDATED_BY` edges (45,314) are trial-to-results-publication links; nearly all of them also appear in this file. The file additionally holds background and other references, which are not results.
- **JEV annotations**: model-generated labels on articles (guideline candidate; clinical versus scientific review). These are predictions, separately licensed, and the only model-inferred content in the release.

## Edge metadata

`knowledge_level` and `agent_type` are populated on some relationship types (for example MeSH indexing) and empty on others in v0.1.0. All core relationships are source-asserted or derived deterministically from source hierarchies; the empty fields are a metadata gap, not an indication of inference.

## Rights-bookkeeping edges

`HAS_RIGHTS_EVIDENCE` and `HAS_USE_GRANT` edges (about 11.2 million) link articles to LunasAI rights-policy records describing the licence basis for each record. They are governance metadata, not clinical relationships. Exclude them when counting or traversing clinical connections (`--exclude-type HAS_RIGHTS_EVIDENCE,HAS_USE_GRANT` in the Neo4j converter).

## Computed article properties

Article nodes carry graph statistics computed by LunasAI: `pagerank_score`, `community_id`, `community_id_coarse`, `community_id_mesh` and related sizes. These are derived analytics, not source facts. `betweenness_score` is 0 throughout v0.1.0 and should not be used. `cited_by_count` comes from OpenAlex and counts citations across all literature; citation counts within this graph come from `CITES` edges.

## MeSH

`HAS_MESH` edges carry `is_major_topic`. Check tags (Humans, Female, Male, Adult, Animals and similar) are attached to most articles; exclude them or restrict to major topics for meaningful topic traversals.

## Journals

`journal` is the MEDLINE journal abbreviation stored on Article nodes (for example `J Clin Invest`). Journals are not separate nodes in v0.1.0.

## Full text

The release contains article metadata and identifiers (PMID, PMCID where present, DOI where available), not article full text or figures.
