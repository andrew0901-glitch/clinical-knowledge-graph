# Data notes for v0.2.0

Things to know before analysing the graph. Each will be addressed or documented further in later releases. (v0.1.0's version of this doc is at the bottom of this file's git history if you need it; v0.1.0 stays exactly as published.)

## Relationship types: use `original_predicate`

Every edge has a Biolink `predicate` and a native `original_predicate` (for example `lunasai:vocab.CITES`). Many relationship types share the generic Biolink predicate `biolink:related_to`, so filtering on `predicate` alone mixes citations, authorship and other relationships. Filter on `original_predicate`. The loaders in this repository do this automatically.

## Core graph versus sidecars

- **Core graph** (`nodes/`, `edges/`): source-asserted relationships from PubMed, MeSH, OpenAlex, ClinicalTrials.gov, MedlinePlus, and (new in v0.2.0) PMC/Journal, plus MeSH hierarchy relationships derived from the published MeSH tree.
- **ClinicalTrials.gov publication references, by role** (replaces the v0.1.0 `ctgov_publications.jsonl` sidecar file, which no longer exists as a separate thing -- its content is now native, typed edges in the core graph): every trial<->publication reference ClinicalTrials.gov records is one of three role-pure, same-direction (`Article -> ClinicalTrial`) edge types:
  - `VALIDATED_BY` (156,197 edges) -- the `RESULT` role: the article reports the trial's own results. This is a narrower, more precise set than v0.1.0's `VALIDATED_BY` (45,314 edges), which mixed all three roles under one type.
  - `CITES_BACKGROUND` (737,005 edges) -- the `BACKGROUND` role: the article is cited as rationale/background for running the trial, not a results report.
  - `HAS_DERIVED_PUBLICATION` (202,551 edges) -- the `DERIVED` role: the article reports a secondary/derived analysis of the trial's data, not its primary results.
  All three read backwards from their own names ("trial VALIDATED_BY paper" sounds like the trial validates the paper) -- the real direction is the paper carrying the claim about the trial: `(:Article)-[:VALIDATED_BY|CITES_BACKGROUND|HAS_DERIVED_PUBLICATION]->(:ClinicalTrial)`.
- **PMC identifiers and journals (new in v0.2.0)**: `(:Article)-[:HAS_PMC_RECORD]->(:PMCRecord)` links an article to its PubMed Central deposit **identifier record** where one exists (`pmcid`/`pmid`/`doi` -- an identifiable-resource pointer only, never abstract/full-text/figures, same as the "Full text" note below). `(:Article)-[:PUBLISHED_IN]->(:Journal)` links it to a first-class `Journal` node. `Journal` nodes did not exist in v0.1.0 (see "Journals" below). `Article.journal` (the plain MEDLINE abbreviation string) still exists unchanged alongside this richer linkage.
- **JEV annotations**: model-generated labels on articles (guideline candidate; clinical versus scientific review). These are predictions, separately licensed, and the only model-inferred content in the release. Unchanged from v0.1.0 -- v0.2.0 does not ship a regenerated JEV file.

## Edge metadata

`knowledge_level` and `agent_type` are populated on some relationship types (for example MeSH indexing) and empty on others in v0.1.0. All core relationships are source-asserted or derived deterministically from source hierarchies; the empty fields are a metadata gap, not an indication of inference.

## Rights-bookkeeping edges: removed in v0.2.0

v0.1.0 had `HAS_RIGHTS_EVIDENCE` and `HAS_USE_GRANT` edges (about 11.2 million) linking articles to LunasAI rights-policy records describing the licence basis for each record. **v0.2.0 ships neither those edges nor any replacement** -- the whole rights-bookkeeping layer was dropped as an export layer (owner decision 2026-11-07). There is currently no way to trace per-article rights basis from this release at all; the `--exclude-type` converter flag still works mechanically but has nothing of that kind left to exclude.

## Computed article properties

Article nodes carry graph statistics computed by LunasAI: `pagerank_score`, `community_id`, `community_id_coarse`, `community_id_mesh` and related sizes. These are derived analytics, not source facts. `betweenness_score` is 0 throughout v0.1.0 and should not be used. `cited_by_count` comes from OpenAlex and counts citations across all literature; citation counts within this graph come from `CITES` edges.

## MeSH

`HAS_MESH` edges carry `is_major_topic`. Check tags (Humans, Female, Male, Adult, Animals and similar) are attached to most articles; exclude them or restrict to major topics for meaningful topic traversals.

## Journals

`journal` is the MEDLINE journal abbreviation stored on Article nodes (for example `J Clin Invest`). Journals are not separate nodes in v0.1.0.

## Full text

The release contains article metadata and identifiers (PMID, PMCID where present, DOI where available), not article full text or figures.
