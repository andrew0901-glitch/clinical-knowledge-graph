# Data notes for v0.2.1

Things to know before analysing the graph. Each will be addressed or documented further in later releases. (v0.1.0's version of this doc is at the bottom of this file's git history if you need it; v0.1.0 stays exactly as published. v0.2.1 ships byte-identical node/edge data to v0.2.0 -- this release only corrects the dataset card -- so every substantive note below is unchanged from v0.2.0, just re-verified against the authoritative manifest.)

## Relationship types: use `original_predicate`

Every edge has a Biolink `predicate` and a native `original_predicate` (for example `lunasai:vocab.CITES`). Many relationship types share the generic Biolink predicate `biolink:related_to`, so filtering on `predicate` alone mixes citations, authorship and other relationships. Filter on `original_predicate`. The loaders in this repository do this automatically.

## Core graph versus sidecars

- **Core graph** (`nodes/`, `edges/`): source-asserted relationships from PubMed, MeSH, OpenAlex, ClinicalTrials.gov, MedlinePlus, and (new in v0.2.0) PMC/Journal, plus MeSH hierarchy relationships derived from the published MeSH tree.
- **ClinicalTrials.gov publication references, by role** (replaces the v0.1.0 `ctgov_publications.jsonl` sidecar file, which no longer exists as a separate thing -- its content is now native, typed edges in the core graph): every trial<->publication reference ClinicalTrials.gov records is one of three role-pure, same-direction (`Article -> ClinicalTrial`) edge types:
  - `VALIDATED_BY` (156,167 edges) -- the `RESULT` role: the article reports the trial's own results. This is a narrower, more precise set than v0.1.0's `VALIDATED_BY` (45,314 edges), which mixed all three roles under one type.
  - `CITES_BACKGROUND` (736,649 edges) -- the `BACKGROUND` role: the article is cited as rationale/background for running the trial, not a results report.
  - `HAS_DERIVED_PUBLICATION` (202,205 edges) -- the `DERIVED` role: the article reports a secondary/derived analysis of the trial's data, not its primary results.
  (These three counts are corrected from this doc's v0.2.0 revision, which carried pre-collapse figures -- 156,197 / 737,005 / 202,551 -- from before a post-export duplicate-pair collapse pass; the numbers above are the authoritative, final-shipped counts straight from `manifest.json counts.edges_by_type`.)
  All three read backwards from their own names ("trial VALIDATED_BY paper" sounds like the trial validates the paper) -- the real direction is the paper carrying the claim about the trial: `(:Article)-[:VALIDATED_BY|CITES_BACKGROUND|HAS_DERIVED_PUBLICATION]->(:ClinicalTrial)`.
- **PMC identifiers and journals (new in v0.2.0)**: `(:Article)-[:HAS_PMC_RECORD]->(:PMCRecord)` links an article to its PubMed Central deposit **identifier record** where one exists (`pmcid`/`pmid`/`doi` -- an identifiable-resource pointer only, never abstract/full-text/figures, same as the "Full text" note below). `(:Article)-[:PUBLISHED_IN]->(:Journal)` links it to a first-class `Journal` node. `Journal` nodes did not exist in v0.1.0 (see "Journals" below). `Article.journal` (the plain MEDLINE abbreviation string) still exists unchanged alongside this richer linkage.
- **JEV annotations**: model-generated labels on articles (guideline candidate; clinical versus scientific review). These are predictions, separately licensed, and the only model-inferred content in the release. Unchanged from v0.1.0 -- v0.2.1 does not ship a regenerated JEV file.
- **Identity-only Article stubs**: a ClinicalTrials.gov publication-assertion edge whose Article endpoint has no PubMed bibliographic record yet (not synced/enriched) still ships, pointed at a minimal stub Article so no edge ever references a dangling id. The stub marker is the Article property-value pair `lunasai_layer == 'ctgov_identity_only'` (not a label, not a separate node type) -- check that exact property before assuming an `Article` node has a title/abstract/MeSH indexing.

## Clinical trials: conditions, sponsors and sites

Measured on the v0.2.1 files with `examples/trial_landscape.py --data-check` (full table in
[examples/trial_landscape_examples/data_check.csv](../examples/trial_landscape_examples/data_check.csv)).

- **Trial conditions are edges, not properties.** `ClinicalTrial` nodes have no conditions or MeSH
  field. The link is `(:ClinicalTrial)-[:HAS_MESH]->(:MeSHConcept)` (6,814,837 edges, counted inside
  the manifest's `HAS_MESH` total alongside the Article edges). They carry ClinicalTrials.gov's own
  browse terms: `study_aspect` is `condition` or `intervention`; `mesh_type` is `mesh-list` (the
  trial's own browse term) or `mesh-ancestor` (ancestors ClinicalTrials.gov adds). For "trials of
  condition X" use `study_aspect='condition' AND mesh_type='mesh-list'` (825,812 edges, 471,229
  trials, 77.8% of trials with a registry record) and expand the hierarchy yourself; the
  `mesh-ancestor` edges select the same trials. Against the ClinicalTrials.gov API on 999 random
  trials, the `mesh-list` condition edges had 98.1% recall and 99.85% precision. The misses are
  Supplementary Concept Records (the graph holds descriptors only) and descriptors renamed in MeSH
  2026 (the edges were matched by name; for example `Postoperative Pain`, formerly
  `Pain, Postoperative`, has no trial edges).
- **Sponsor class is on the edge.** `Sponsor` nodes hold only a lower-cased name. ClinicalTrials.gov's
  `agency_class` (INDUSTRY, OTHER, NIH, FED, OTHER_GOV, NETWORK, INDIV, UNKNOWN, AMBIG) and
  `lead_or_collaborator` are on `SPONSORED_BY`. There is no "academic" class; universities and
  hospitals are OTHER.
- **The newest 22,567 trials (NCT07563270 onward) have no `SPONSORED_BY` or `CONDUCTED_AT` edges.**
  That includes 6,586 of the 64,497 recruiting trials and about half of the trials starting in 2026.
  Most of them (16,181) do have condition edges, so they appear in condition counts but not in any
  sponsor, site or country figure.
- **Sites** (`TrialSite`) are facility name + city + state + country (state 53% overall, 100% for
  US sites); no postcode or coordinates. The key is the registered spelling, so one hospital can
  appear as several sites. `CONDUCTED_AT.status` (per-site recruitment status) is set on 15.8% of
  edges, but on 97% of edges of recruiting trials.
- **Dates**: month-precision start/completion dates are stored as the last day of the month (38.6%
  of start dates). Use the year.
- **Results articles**: 67% of the 140,372 `VALIDATED_BY` articles are identity-only stubs (no title,
  publication types or citations), so in-graph uptake by guidelines and reviews can only be measured
  for the other third. Guideline is a rare publication type (6,350 articles).

## Edge metadata

`knowledge_level` and `agent_type` are populated on some relationship types (for example MeSH indexing) and empty on others in v0.1.0. All core relationships are source-asserted or derived deterministically from source hierarchies; the empty fields are a metadata gap, not an indication of inference.

## Rights-bookkeeping edges: removed in v0.2.0 (unchanged in v0.2.1)

v0.1.0 had `HAS_RIGHTS_EVIDENCE` and `HAS_USE_GRANT` edges (about 11.2 million) linking articles to LunasAI rights-policy records describing the licence basis for each record. **v0.2.0/v0.2.1 ship neither those edges nor any replacement** -- the whole rights-bookkeeping layer was dropped as an export layer. There is currently no way to trace per-article rights basis from this release at all; the `--exclude-type` converter flag still works mechanically but has nothing of that kind left to exclude.

## Computed article properties

Article nodes carry graph statistics computed by LunasAI: `pagerank_score`, `community_id`, `community_id_coarse`, `community_id_mesh` and related sizes. These are derived analytics, not source facts. `betweenness_score` does not ship at all in v0.2.0/v0.2.1 (the computed values were a non-representative placeholder, uniformly zero, and were dropped rather than shipped as if real; it was present and zero throughout v0.1.0 and should not have been used there either). `cited_by_count` comes from OpenAlex and counts citations across all literature; citation counts within this graph come from `CITES` edges.

## MeSH

`HAS_MESH` edges carry `is_major_topic`. Check tags (Humans, Female, Male, Adult, Animals and similar) are attached to most articles; exclude them or restrict to major topics for meaningful topic traversals.

## Journals

`journal` is the MEDLINE journal abbreviation stored on Article nodes (for example `J Clin Invest`). Journals are not separate nodes in v0.1.0.

## Full text

The release contains article metadata and identifiers (PMID, PMCID where present, DOI where available), not article full text or figures.
