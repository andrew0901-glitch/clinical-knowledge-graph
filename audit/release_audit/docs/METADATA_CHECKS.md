# Metadata checks — v0.2.0 audit (graph files identical in v0.2.1)

> **Scope.** These documents report the audit of release **v0.2.0** (Zenodo 10.5281/zenodo.24091964, HF tag `clinical-v0.2.0`). All 107 node/edge files of release v0.2.1 (Zenodo 10.5281/zenodo.24108692) are **byte-identical** (same SHA-256) to the v0.2.0 files, so every statement about graph content holds for v0.2.1. Statements about the *release metadata files* (dataset card, citation file, exporter commit) describe v0.2.0. Comparisons with earlier releases and with the unreleased pre-correction build were removed from this copy; see `../EXCLUDED.md`.

Published **Lunas Clinical Evidence KG v0.2.0**, [DOI 10.5281/zenodo.24091964](https://doi.org/10.5281/zenodo.24091964), graph snapshot 2026-11-07. Hugging Face tag `clinical-v0.2.0` is pinned to immutable commit `76af01bf51483264b95bece5ffef0999521d21cd`. All **123 HF-manifest-listed files** passed SHA-256 verification before queries. Exact compressed-shard concatenation also reproduced all **8 Zenodo graph-bundle SHA-256 values**, proving that the analyzed HF graph matches the DOI graph inventory. Source files were copied from a byte-identical local mirror or downloaded from the immutable HF revision; nothing was written to the release or production. Published manifest SHA-256: `d8db915388aaa8dbb363909c76221d9928ba39479f445095349887c2bfc3a129`.

**Complete-population** means all released records in the stated family. Three clinical areas and the same six ranking queries are **purposive examples**, not representative samples or relevance judgments. All Article-level tables distinguish **with stubs** (3,724,062) and **without stubs** (3,145,885); canonical stubs are defined exclusively by `lunasai_layer=ctgov_identity_only` (578,177), regardless of their other metadata. Without-stub traversal/ranking results use induced Article populations: exclude stub endpoints and their citation contributions.

[Exact input hashes/build claims](../results/input_verification.json), [exact preparation SQL](../results/preparation_queries.json), [population SQL/parameters](../results/analysis_queries.json), [independent population re-score](../results/headline_verification.json), and [reproducibility manifest](../../manifests/REPRODUCIBILITY_MANIFEST.public.json) bind the numbers to input files and code revisions. No paid model calls, source enrichment, production access, dataset repair or release publication occurred. PMC metadata means an identifier/graph route, not independently verified accessible full text or reuse rights.

## A1. PMC/full-text/figures/tables

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| pmcid | 1,299,544/3,724,062 (34.90%) | 1,299,544/3,145,885 (41.31%) |
| is_oa | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| open_access | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| has_full_text | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| full_text_available | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| figure_count | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| table_count | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |

v0.2 adds PMCRecord nodes and Article → HAS_PMC_RECORD links. This increases graph-route coverage without populating every Article PMCID property. All comparable property/link PMCIDs agree after prefix normalization; route availability/access rights are not verified. Every PMCRecord explicitly carries absent-reason metadata for access status and deposit date; absent figure/table counts mean **unknown**, never zero.

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| pmcid | 1,334,061/1,334,061 (100.00%) | 1,334,061/1,334,061 (100.00%) |
| doi | 1,189,722/1,334,061 (89.18%) | 1,189,722/1,334,061 (89.18%) |
| iri | 1,334,061/1,334,061 (100.00%) | 1,334,061/1,334,061 (100.00%) |
| access_status | 0/1,334,061 (0.00%) | 0/1,334,061 (0.00%) |
| deposit_date | 0/1,334,061 (0.00%) | 0/1,334,061 (0.00%) |
| is_oa | 0/1,334,061 (0.00%) | 0/1,334,061 (0.00%) |
| figure_count | 0/1,334,061 (0.00%) | 0/1,334,061 (0.00%) |
| table_count | 0/1,334,061 (0.00%) | 0/1,334,061 (0.00%) |

## A2. NLM publication types

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| pub_types | 3,024,048/3,724,062 (81.20%) | 3,024,048/3,145,885 (96.13%) |

| Exact label (nonexclusive) | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| Practice Guideline | 5,826/3,724,062 (0.16%) | 5,826/3,145,885 (0.19%) |
| Guideline | 1,299/3,724,062 (0.03%) | 1,299/3,145,885 (0.04%) |
| Systematic Review | 59,012/3,724,062 (1.58%) | 59,012/3,145,885 (1.88%) |
| Meta-Analysis | 41,156/3,724,062 (1.11%) | 41,156/3,145,885 (1.31%) |
| Review | 218,211/3,724,062 (5.86%) | 218,211/3,145,885 (6.94%) |
| Randomized Controlled Trial | 141,405/3,724,062 (3.80%) | 141,405/3,145,885 (4.49%) |

No title-derived study design or model label is substituted. Practice Guideline/Guideline define guidelines; only the explicit Systematic Review label joins that class in trial citation chains.

| Population | Guideline union / Articles | Guideline/review union / Articles |
| --- | --- | --- |
| with_stubs | 6,350/3,724,062 (0.17%) | 292,235/3,724,062 (7.85%) |
| without_stubs | 6,350/3,145,885 (0.20%) | 292,235/3,145,885 (9.29%) |


## A3. Journals

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| journal | 3,145,885/3,724,062 (84.47%) | 3,145,885/3,145,885 (100.00%) |
| issn | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| issn_l | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| nlm_id | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| journal_title | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| journal_iso_abbreviation | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| journal_medline_abbreviation | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |
| openalex_source_id | 0/3,724,062 (0.00%) | 0/3,145,885 (0.00%) |

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| name | 2,734/2,734 (100.00%) | 2,734/2,734 (100.00%) |
| pubmed_abbreviation | 2,734/2,734 (100.00%) | 2,734/2,734 (100.00%) |
| nlm_id | 376/2,734 (13.75%) | 376/2,734 (13.75%) |
| issn | 0/2,734 (0.00%) | 0/2,734 (0.00%) |
| issn_l | 0/2,734 (0.00%) | 0/2,734 (0.00%) |
| openalex_source_id | 0/2,734 (0.00%) | 0/2,734 (0.00%) |
| iri | 376/2,734 (13.75%) | 376/2,734 (13.75%) |

The release has 2,734 Journal nodes: 376 NLM-ID identities and 2,358 abbreviation fallback identities. Full title versus abbreviation is not uniformly established for fallback nodes. No ISSN/ISSN-L/OpenAlex-source identifier is exported. Exact abbreviation collisions were not observed; that does not resolve spelling/alias variants or prove globally normalized venue identity. Article OpenAlex Work IDs are not journal Source IDs.

## A4. HAS_MESH, qualifiers and check tags

| Population | Major-topic edge state | Edges |
| --- | --- | --- |
| with_stubs | False | 25,474,424 |
| with_stubs | True | 10,428,762 |
| without_stubs | False | 25,474,424 |
| without_stubs | True | 10,428,762 |

The 40-name NLM reference check-tag list is resolved to actual v0.2 descriptors (`analysis_check_tags.csv`). Both query and expanded descriptors exclude these IDs. This is an explicit stoplist, not an intrinsic MeSH-node check-tag property or a claim of exhaustive present-day NLM classification. Ranking requires an actual true edge flag; node-label lists never create links.

| Population | Comparable edge/list pairs | Disagreements |
| --- | --- | --- |
| without_stubs | 35826898 | 290 |
| with_stubs | 35826898 | 290 |

| Population | Article/major-label pairs | Unmatched exact names |
| --- | --- | --- |
| without_stubs | 10465269 | 36797 |
| with_stubs | 10465269 | 36797 |

Observed qualifier/subheading-like HAS_MESH fields: **none**. Missing qualifiers cannot be reconstructed from this release.

| Trial study aspect | Source mesh type | Edges |
| --- | --- | --- |
| condition | mesh-ancestor | 3543161 |
| condition | mesh-list | 825812 |
| intervention | mesh-ancestor | 2085674 |
| intervention | mesh-list | 360190 |

Same-condition traversal uses only `condition` + `mesh-list`. Source `mesh-ancestor` expansion and intervention mappings remain separate. The direct raw reread retains `exact_name_mesh_hierarchy` / source-table qualifiers in `extra_qualifiers_and_orcid.csv`; these are mappings, not clinical equivalence adjudications.

| Population | Indexed Articles | Articles with non-check major term | Articles with known major flags |
| --- | --- | --- | --- |
| without_stubs | 2861802 | 2854567 | 2861802 |
| with_stubs | 2861802 | 2854567 | 2861802 |

## A5. Community, PageRank and betweenness states

| Field | v0.2 with: present / zero / -1 | v0.2 without: present / zero / -1 | v0.2 range |
| --- | --- | --- | --- |
| betweenness_score | 0 / 0 / 0 | 0 / 0 / 0 | None … None |
| community_id | 2412623 / 0 / 0 | 2412623 / 0 / 0 | 96 … 2412602 |
| community_id_coarse | 2412623 / 2 / 0 | 2412623 / 2 / 0 | 0 … 4450 |
| community_id_mesh | 2851793 / 1369 / 0 | 2851793 / 1369 / 0 | 0 … 2419 |
| community_size | 2412623 / 0 / 0 | 2412623 / 0 / 0 | 1 … 104306 |
| community_size_coarse | 2412623 / 0 / 0 | 2412623 / 0 / 0 | 1 … 162346 |
| community_size_mesh | 2851793 / 0 / 0 | 2851793 / 0 / 0 | 1 … 37260 |
| pagerank_score | 3135515 / 443467 / 0 | 3135515 / 443467 / 0 | 0.0 … 551.7458521882454 |

All denominators and null/presence states are in `analytics_states.csv` and the complete raw census. The v0.2 value ranges are identical in both populations because none of the canonical stubs carries these analytic properties. Group-size consistency and distinct-value counts were rerun for both Article populations. Nonplaceholder values do not prove currentness; the README says these analytics are unscheduled and can predate the snapshot. No analytics property enters the public ranking.

## A6. Entry points

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| doi | 2,219,302/3,724,062 (59.59%) | 2,219,302/3,145,885 (70.55%) |
| pmcid | 1,299,544/3,724,062 (34.90%) | 1,299,544/3,145,885 (41.31%) |
| name | 3,145,885/3,724,062 (84.47%) | 3,145,885/3,145,885 (100.00%) |
| openalex_id | 3,041,300/3,724,062 (81.67%) | 3,041,300/3,145,885 (96.68%) |

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| orcid | 0/5,134,220 (0.00%) | 0/5,134,220 (0.00%) |
| profile_orcid | 0/5,134,220 (0.00%) | 0/5,134,220 (0.00%) |
| openalex_author_id | 5,134,220/5,134,220 (100.00%) | 5,134,220/5,134,220 (100.00%) |
| openalex_id | 0/5,134,220 (0.00%) | 0/5,134,220 (0.00%) |

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| nct_id | 606,580/606,580 (100.00%) | 606,580/606,580 (100.00%) |

| Field | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| name | 2,033/2,033 (100.00%) | 2,033/2,033 (100.00%) |
| iri | 2,033/2,033 (100.00%) | 2,033/2,033 (100.00%) |
| url | 0/2,033 (0.00%) | 0/2,033 (0.00%) |

ORCID on an authorship is distinct from Author-node coverage and is retained in the raw qualifier reread. Author IDs are not a count of perfectly disambiguated people.

## Canonical-stub marker caveat

| Observed stub property | Count / canonical stubs |
| --- | --- |
| doi | 0/578,177 (0.00%) |
| major_lists | 0/578,177 (0.00%) |
| pmcid | 0/578,177 (0.00%) |
| publication_types | 0/578,177 (0.00%) |
| titles | 0/578,177 (0.00%) |

| Incident relation | Stub-subject edges | Stub-object edges |
| --- | --- | --- |
| CITES_BACKGROUND | 507692 | 0 |
| HAS_DERIVED_PUBLICATION | 142648 | 0 |
| HAS_PMC_RECORD | 1234 | 0 |
| PUBLISHED_IN | 2010 | 0 |
| VALIDATED_BY | 103289 | 0 |

The canonical marker controls each comparison. The correction removes the prior 5,120 metadata-rich records from the stub population; remaining incident edges are measured rather than presumed absent. The before/after change report distinguishes relabeling from actual edge removal.
