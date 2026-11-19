# Resource-paper traversals and ranking — v0.2.0 audit (graph files identical in v0.2.1)

> **Scope.** These documents report the audit of release **v0.2.0** (Zenodo 10.5281/zenodo.24091964, HF tag `clinical-v0.2.0`). All 107 node/edge files of release v0.2.1 (Zenodo 10.5281/zenodo.24108692) are **byte-identical** (same SHA-256) to the v0.2.0 files, so every statement about graph content holds for v0.2.1. Statements about the *release metadata files* (dataset card, citation file, exporter commit) describe v0.2.0. Comparisons with earlier releases and with the unreleased pre-correction build were removed from this copy; see `../EXCLUDED.md`.

Published **Lunas Clinical Evidence KG v0.2.0**, [DOI 10.5281/zenodo.24091964](https://doi.org/10.5281/zenodo.24091964), graph snapshot 2026-11-07. Hugging Face tag `clinical-v0.2.0` is pinned to immutable commit `76af01bf51483264b95bece5ffef0999521d21cd`. All **123 HF-manifest-listed files** passed SHA-256 verification before queries. Exact compressed-shard concatenation also reproduced all **8 Zenodo graph-bundle SHA-256 values**, proving that the analyzed HF graph matches the DOI graph inventory. Source files were copied from a byte-identical local mirror or downloaded from the immutable HF revision; nothing was written to the release or production. Published manifest SHA-256: `d8db915388aaa8dbb363909c76221d9928ba39479f445095349887c2bfc3a129`.

**Complete-population** means all released records in the stated family. Three clinical areas and the same six ranking queries are **purposive examples**, not representative samples or relevance judgments. All Article-level tables distinguish **with stubs** (3,724,062) and **without stubs** (3,145,885); canonical stubs are defined exclusively by `lunasai_layer=ctgov_identity_only` (578,177), regardless of their other metadata. Without-stub traversal/ranking results use induced Article populations: exclude stub endpoints and their citation contributions.

[Exact input hashes/build claims](../results/input_verification.json), [exact preparation SQL](../results/preparation_queries.json), [population SQL/parameters](../results/analysis_queries.json), [independent population re-score](../results/headline_verification.json), and [reproducibility manifest](../../manifests/REPRODUCIBILITY_MANIFEST.public.json) bind the numbers to input files and code revisions. No paid model calls, source enrichment, production access, dataset repair or release publication occurred. PMC metadata means an identifier/graph route, not independently verified accessible full text or reuse rights.

## Snapshot census and semantics

| Family | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| Article | 3,724,062 | 3,145,885 |
| Author | 5,134,220 | 5,134,220 |
| ClinicalTrial | 606,580 | 606,580 |
| ExternalResource | 38,751 | 38,751 |
| Journal | 2,734 | 2,734 |
| License | 0 | 0 |
| MeSHConcept | 31,110 | 31,110 |
| MedlinePlus | 2,033 | 2,033 |
| MedlinePlusGroup | 88 | 88 |
| PMCRecord | 1,334,061 | 1,334,061 |
| RightsPolicy | 0 | 0 |
| Sponsor | 101,306 | 101,306 |
| TrialSite | 1,092,163 | 1,092,163 |

| Native type | v0.2 with stubs | v0.2 without stubs |
| --- | --- | --- |
| ANCESTOR_OF | 0 | 0 |
| AUTHORED_BY | 21135411 | 21135411 |
| CITES | 31922142 | 31922142 |
| CITES_BACKGROUND | 736649 | 228957 |
| CONDUCTED_AT | 3153344 | 3153344 |
| HAS_BROADER | 42519 | 42519 |
| HAS_BROADER_ANCESTOR | 185654 | 185654 |
| HAS_DERIVED_PUBLICATION | 202205 | 59557 |
| HAS_LANGUAGE_RESOURCE | 4885 | 4885 |
| HAS_MESH | 42720732 | 42720732 |
| HAS_PMC_RECORD | 1334074 | 1332840 |
| HAS_RIGHTS_EVIDENCE | 0 | 0 |
| HAS_USE_GRANT | 0 | 0 |
| IN_TOPIC_GROUP | 3651 | 3651 |
| LINKS_TO_RESOURCE | 51747 | 51747 |
| PARENT_OF | 0 | 0 |
| PUBLISHED_IN | 3147895 | 3145885 |
| RELATED_TOPIC | 6246 | 6246 |
| RESOURCE_TRANSLATION_OF | 22573 | 22573 |
| SPONSORED_BY | 931156 | 931156 |
| TRANSLATION_OF | 1016 | 1016 |
| VALIDATED_BY | 156167 | 52878 |

The independently scanned v0.2 totals are **12,067,108 nodes / 105,758,066 edges**, with unique node/edge IDs and zero missing endpoints. Direction was read from the verified README before queries and tested against every edge: Article → Author; citing Article → cited Article; **Article → ClinicalTrial** for all three publication roles; Article → Journal/PMCRecord; narrower MeSH → broader MeSH (`HAS_BROADER`, `HAS_BROADER_ANCESTOR`). Downward expansion matches the query as object and takes hierarchy subjects. The topic/trial HAS_MESH directions are also retained even though the README direction list only mentions Article HAS_MESH.

## Trial → results publication → cited by guideline/systematic review

Primary paper counts exclude self-citations. Self-inclusive results remain in `analysis_B1_population.csv`; the source graph contains self-links. Results designation means an exported source role, not expert validation, trial success, or guideline endorsement.

| Population | Trials with results / all trials | Distinct results Articles | Results Articles cited by G/SR | Trials with cited results / all trials |
| --- | --- | --- | --- | --- |
| v0.2 with_stubs | 42,075/606,580 (6.94%) | 140,372 | 23,460/140,372 (16.71%) | 13,721/606,580 (2.26%) |
| v0.2 without_stubs | 22,793/606,580 (3.76%) | 45,865 | 23,460/45,865 (51.15%) | 13,721/606,580 (2.26%) |

Excluding stubs selects Articles with much more observable bibliography and citation evidence; the higher conditional citation fraction in that subset is not evidence that stub-linked publications are clinically inferior.

## Trial → background references

v0.2 population counts use the explicit `CITES_BACKGROUND` type and observed Article → Trial direction.

| Population | Trials with background / all trials | Distinct background Articles | Edge rows | Distinct NCT–PMID pairs |
| --- | --- | --- | --- | --- |
| without_stubs | 62,788/606,580 (10.35%) | 146132 | 228957 | 228957 |
| with_stubs | 97,142/606,580 (16.01%) | 539317 | 736649 | 736649 |

## MedlinePlus → MeSH → guidelines/reviews and condition trials

Every mapped non-check descriptor is used. Guidelines/reviews are presented before other Articles using exact NLM types; the separate scored guideline/review-first views are exported with the ranking tables. A descendant denotes a narrower taxonomy relationship, not clinical interchangeability. Trial bridges require condition mesh-list rows; intervention and pre-expanded ancestor rows are excluded from the primary measure.

| Population | Expansion | Topics → G/review | Topics → major G/review | Topics → condition trial | Topics reaching both |
| --- | --- | --- | --- | --- | --- |
| v0.2 with_stubs | full | 2,021/2,033 (99.41%) | 2,019/2,033 (99.31%) | 1,498/2,033 (73.68%) | 1,496/2,033 (73.59%) |
| v0.2 with_stubs | none | 2,021/2,033 (99.41%) | 2,017/2,033 (99.21%) | 1,440/2,033 (70.83%) | 1,438/2,033 (70.73%) |
| v0.2 with_stubs | one | 2,021/2,033 (99.41%) | 2,019/2,033 (99.31%) | 1,480/2,033 (72.80%) | 1,478/2,033 (72.70%) |
| v0.2 without_stubs | full | 2,021/2,033 (99.41%) | 2,019/2,033 (99.31%) | 1,498/2,033 (73.68%) | 1,496/2,033 (73.59%) |
| v0.2 without_stubs | none | 2,021/2,033 (99.41%) | 2,017/2,033 (99.21%) | 1,440/2,033 (70.83%) | 1,438/2,033 (70.73%) |
| v0.2 without_stubs | one | 2,021/2,033 (99.41%) | 2,019/2,033 (99.31%) | 1,480/2,033 (72.80%) | 1,478/2,033 (72.70%) |

### Strict common-descriptor bridge and source-ancestor sensitivity

The preceding “both” count permits a guideline/review and trial on different mapped descriptors of the same topic. This stricter control requires the **same matched descriptor**. Registry condition `mesh-ancestor` rows are a separate sensitivity; they are never silently added to the primary condition mesh-list result. These counts were rerun and independently checked for both releases and both Article populations.

| Release | Article population | Expansion | Strict same-descriptor G/review+trial | Strict major-topic same-descriptor bridge | Trial reach including source condition ancestors | G/review + source-ancestor trial, same descriptor |
| --- | --- | --- | --- | --- | --- | --- |
| v02 | with_stubs | full | 1,486/2,033 (73.09%) | 1,486/2,033 (73.09%) | 1,498/2,033 (73.68%) | 1,486/2,033 (73.09%) |
| v02 | with_stubs | none | 1,438/2,033 (70.73%) | 1,438/2,033 (70.73%) | 1,442/2,033 (70.93%) | 1,440/2,033 (70.83%) |
| v02 | with_stubs | one | 1,468/2,033 (72.21%) | 1,468/2,033 (72.21%) | 1,480/2,033 (72.80%) | 1,468/2,033 (72.21%) |
| v02 | without_stubs | full | 1,486/2,033 (73.09%) | 1,486/2,033 (73.09%) | 1,498/2,033 (73.68%) | 1,486/2,033 (73.09%) |
| v02 | without_stubs | none | 1,438/2,033 (70.73%) | 1,438/2,033 (70.73%) | 1,442/2,033 (70.93%) | 1,440/2,033 (70.83%) |
| v02 | without_stubs | one | 1,468/2,033 (72.21%) | 1,468/2,033 (72.21%) | 1,480/2,033 (72.80%) | 1,468/2,033 (72.21%) |

## Article → citations + shared MeSH; Author → MeSH; Journal → guidelines

The Article population traversal uses a major-preferred non-check seed profile (fallback to indexed terms when no major is known). The ranking experiment below is stricter: true major-topic edges on candidates and source Article query terms. Both citation directions are considered; self-links are excluded. Field citation scores count distinct other in-corpus citing Articles. Separate **whole-field** top-20 tables are provided for both Article populations, rather than calling a citation-neighbor leader the global field leader.

| Population | Articles with query profile | Articles reaching shared-MeSH citation neighbor | Unique directed seed/neighbor pairs |
| --- | --- | --- | --- |
| v0.2 without_stubs | 2861756 | 2,533,201/3,145,885 (80.52%) | 40468473 |
| v0.2 with_stubs | 2861756 | 2,533,201/3,724,062 (68.02%) | 40468473 |

| Population | Authors with ≥1 authorship | Authors with ≥1 indexed Article |
| --- | --- | --- |
| v0.2 with_stubs | 5,134,220/5,134,220 (100.00%) | 4,684,771/5,134,220 (91.25%) |
| v0.2 without_stubs | 5,134,220/5,134,220 (100.00%) | 4,684,771/5,134,220 (91.25%) |

The three Author profiles retain exact authorship/indexing edge witnesses and match flags. Counts describe released Author IDs, not perfectly resolved people.

Release v0.2:

| Population | Journals with Articles / all Journals | Journals with guidelines / all Journals | Linked Articles | Linked guideline Articles |
| --- | --- | --- | --- | --- |
| with_stubs | 2,734/2,734 (100.00%) | 254/2,734 (9.29%) | 3147895 | 6350 |
| without_stubs | 2,310/2,734 (84.49%) | 254/2,734 (9.29%) | 3145885 | 6350 |

Fallback journal identities limit venue-level interoperability. A Journal having a guideline Article is not evidence that the journal or article is an authority for a clinical recommendation.

## PMC full-text routes on traversal results

Actual current full-text availability, access status, deposit date and reuse rights cannot be determined from the released metadata. The following is the observable **PMC route proxy**, using nonempty Article PMCID or HAS_PMC_RECORD. It must not be labeled verified accessible/open full text. Primary non-self chain denominators replace the historical self-inclusive B1 family below; all original SQL outputs remain retained.

| Complete traversal result family | Population | PMCID property | Any PMC route |
| --- | --- | --- | --- |
| author_indexed_articles | with_stubs | 1,153,794/2,790,093 (41.35%) | 1,172,507/2,790,093 (42.02%) |
| author_indexed_articles | without_stubs | 1,153,794/2,790,093 (41.35%) | 1,172,507/2,790,093 (42.02%) |
| background_publications | with_stubs | 45,940/539,317 (8.52%) | 46,107/539,317 (8.55%) |
| background_publications | without_stubs | 45,940/146,132 (31.44%) | 46,093/146,132 (31.54%) |
| citation_shared_neighbors | with_stubs | 1,030,251/2,546,024 (40.47%) | 1,038,861/2,546,024 (40.80%) |
| citation_shared_neighbors | without_stubs | 1,030,251/2,546,024 (40.47%) | 1,038,861/2,546,024 (40.80%) |
| journal_guidelines | with_stubs | 1,107/6,350 (17.43%) | 1,139/6,350 (17.94%) |
| journal_guidelines | without_stubs | 1,107/6,350 (17.43%) | 1,139/6,350 (17.94%) |
| results_cited_by_guideline_systematic | with_stubs | 7,251/23,460 (30.91%) | 7,277/23,460 (31.02%) |
| results_cited_by_guideline_systematic | without_stubs | 7,251/23,460 (30.91%) | 7,277/23,460 (31.02%) |
| results_publications | with_stubs | 14,428/140,372 (10.28%) | 18,818/140,372 (13.41%) |
| results_publications | without_stubs | 14,428/45,865 (31.46%) | 17,594/45,865 (38.36%) |
| topic_guidelines_reviews | with_stubs | 86,120/263,927 (32.63%) | 88,126/263,927 (33.39%) |
| topic_guidelines_reviews | without_stubs | 86,120/263,927 (32.63%) | 88,126/263,927 (33.39%) |

## Eighteen real path examples (purposive)

Every example has actual node and edge IDs, node source URLs where exported, and an exact named query in `analysis_queries.json`. Missing journal source URLs are explicitly retained rather than invented. Source URLs are bibliographic/registry routes, not live clinical adjudication.

### results — neurology

| Path/witness field | Actual value |
| --- | --- |
| citation_edge | urn:uuid:a3c277ef-9752-5e84-ae6f-2f10c93d696b |
| citing_article | PMID:28118460 |
| citing_types | ["Journal Article", "Meta-Analysis", "Research Support, N.I.H., Extramural", "Systematic Review"] |
| descriptor | MESH:D004827 |
| mesh_edge | urn:uuid:f0a36e6f-cd6f-5d1f-b442-71cb081baae9 |
| publication_edge | urn:uuid:b4ba48b4-824c-5bc7-95b6-418dc1371ae8 |
| result_article | PMID:18711110 |
| trial | clinicaltrials:NCT00047463 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| PMID:28118460 | Article | Screening for Obstructive Sleep Apnea in Adults: Evidence Report and Systematic Review for the US Preventive Services Task Force. | False | https://pubmed.ncbi.nlm.nih.gov/28118460/ |
| clinicaltrials:NCT00047463 | ClinicalTrial | Effects of Treating Obstructive Sleep Apnea in Epilepsy | False | https://clinicaltrials.gov/study/NCT00047463 |
| PMID:18711110 | Article | Treating obstructive sleep apnea in adults with epilepsy: a randomized pilot trial. | False | https://pubmed.ncbi.nlm.nih.gov/18711110/ |
| MESH:D004827 | MeSHConcept | Epilepsy | False | https://meshb.nlm.nih.gov/record/ui?ui=D004827 |

Exact query: `results_example_1`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### background — neurology

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:7673957 |
| descriptor | MESH:D004827 |
| mesh_edge | urn:uuid:003fe32d-fc13-5a88-ac10-ecf9b7147c8b |
| name | Clinicoradiological and pathological correlations in patients with solitary cysticercus granuloma and epilepsy: focus on presence of the parasite and oedema formation. |
| pmcid | 486031 |
| publication_edge | urn:uuid:158348a6-3ac5-5288-b135-33147dce02f4 |
| trial | clinicaltrials:NCT00001912 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| MESH:D004827 | MeSHConcept | Epilepsy | False | https://meshb.nlm.nih.gov/record/ui?ui=D004827 |
| clinicaltrials:NCT00001912 | ClinicalTrial | Brain Tissue Swelling and Seizure Activity in Inactive Cysticercosis | False | https://clinicaltrials.gov/study/NCT00001912 |
| PMID:7673957 | Article | Clinicoradiological and pathological correlations in patients with solitary cysticercus granuloma and epilepsy: focus on presence of the parasite and oedema formation. | False | https://pubmed.ncbi.nlm.nih.gov/7673957/ |

Exact query: `background_example_1`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### topic — neurology

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:12601090 |
| article_mesh_edge | urn:uuid:429ca553-3dc4-5b31-9744-3439fdbff69f |
| distance | 0 |
| hierarchy_edge | None |
| matched_descriptor | MESH:D004827 |
| mesh_type | mesh-list |
| pub_types | ["Guideline", "Journal Article", "Practice Guideline", "Research Support, Non-U.S. Gov't", "Research Support, U.S. Gov't, P.H.S.", "Systematic Review"] |
| query_descriptor | MESH:D004827 |
| study_aspect | condition |
| topic | lunasai:medlineplus_topic.1888 |
| trial | clinicaltrials:NCT00001149 |
| trial_mesh_edge | urn:uuid:b042fcb5-6df9-5914-a4a2-e2c7e28bc039 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| clinicaltrials:NCT00001149 | ClinicalTrial | Monitoring Patients With Uncontrolled Epilepsy | False | https://clinicaltrials.gov/study/NCT00001149 |
| lunasai:medlineplus_topic.1888 | MedlinePlus | Epilepsia | False | https://medlineplus.gov/spanish/epilepsy.html |
| PMID:12601090 | Article | Practice parameter: temporal lobe and localized neocortical resections for epilepsy: report of the Quality Standards Subcommittee of the American Academy of Neurology, in association with the American Epilepsy Society and the American Association of Neurological Surgeons. | False | https://pubmed.ncbi.nlm.nih.gov/12601090/ |
| MESH:D004827 | MeSHConcept | Epilepsy | False | https://meshb.nlm.nih.gov/record/ui?ui=D004827 |

Exact query: `topic_example_1`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### article — neurology

| Path/witness field | Actual value |
| --- | --- |
| citation_edge | urn:uuid:8cc2621e-f18b-50a5-ab47-52f9c1fde250 |
| cited_article | PMID:15111659 |
| citing_article | PMID:18711110 |
| descriptor | MESH:D004827 |
| in_corpus_citations | 46 |
| neighbor | PMID:15111659 |
| neighbor_mesh_edge | urn:uuid:b0222046-9c10-5256-92cb-8aaf40ad957a |
| seed_article | PMID:18711110 |
| seed_mesh_edge | urn:uuid:f0a36e6f-cd6f-5d1f-b442-71cb081baae9 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| PMID:15111659 | Article | Efficacy and tolerability of the new antiepileptic drugs I: treatment of new onset epilepsy [RETIRED]: report of the Therapeutics and Technology Assessment Subcommittee and Quality Standards Subcommittee of the American Academy of Neurology and the American Epilepsy Society. | False | https://pubmed.ncbi.nlm.nih.gov/15111659/ |
| PMID:18711110 | Article | Treating obstructive sleep apnea in adults with epilepsy: a randomized pilot trial. | False | https://pubmed.ncbi.nlm.nih.gov/18711110/ |
| MESH:D004827 | MeSHConcept | Epilepsy | False | https://meshb.nlm.nih.gov/record/ui?ui=D004827 |

Exact query: `article_example_1`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### author — neurology

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:10025774 |
| author | lunasai:openalex_author.A5018643148 |
| authorship_edge | urn:uuid:019a5bdf-ec86-5271-9201-263a7ff4f3b0 |
| descriptor | MESH:D004827 |
| identity_flags | [] |
| match_status | matched |
| mesh_edge | urn:uuid:ddd312ca-35c3-59c8-96f2-3bfb9f5e3890 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| PMID:10025774 | Article | Topiramate increases brain GABA, homocarnosine, and pyrrolidinone in patients with epilepsy. | False | https://pubmed.ncbi.nlm.nih.gov/10025774/ |
| MESH:D004827 | MeSHConcept | Epilepsy | False | https://meshb.nlm.nih.gov/record/ui?ui=D004827 |
| lunasai:openalex_author.A5018643148 | Author | Ognen A. C. Petroff | False | not exported |

Exact query: `author_example_1`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### journal — neurology

| Path/witness field | Actual value |
| --- | --- |
| descriptor | MESH:D004827 |
| guideline | PMID:12601090 |
| journal | nlm:401060 |
| journal_edge | urn:uuid:00b81f9d-ab09-5c4d-a05c-e7b5fb4695b5 |
| journal_name | Neurology |
| mesh_edge | urn:uuid:429ca553-3dc4-5b31-9744-3439fdbff69f |
| pub_types | ["Guideline", "Journal Article", "Practice Guideline", "Research Support, Non-U.S. Gov't", "Research Support, U.S. Gov't, P.H.S.", "Systematic Review"] |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| MESH:D004827 | MeSHConcept | Epilepsy | False | https://meshb.nlm.nih.gov/record/ui?ui=D004827 |
| PMID:12601090 | Article | Practice parameter: temporal lobe and localized neocortical resections for epilepsy: report of the Quality Standards Subcommittee of the American Academy of Neurology, in association with the American Epilepsy Society and the American Association of Neurological Surgeons. | False | https://pubmed.ncbi.nlm.nih.gov/12601090/ |
| nlm:401060 | Journal | Neurology | False | https://www.ncbi.nlm.nih.gov/nlmcatalog/401060 |

Exact query: `journal_example_1`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### results — respiratory

| Path/witness field | Actual value |
| --- | --- |
| citation_edge | urn:uuid:aabb8cd3-69bc-59b8-8db1-8522a0034bae |
| citing_article | PMID:35998970 |
| citing_types | ["Journal Article", "Systematic Review", "Research Support, Non-U.S. Gov't"] |
| descriptor | MESH:D001249 |
| mesh_edge | urn:uuid:d5ff1c68-6598-58c9-a3e2-fb6bf8422bf4 |
| publication_edge | urn:uuid:a1c371f6-19b9-5458-b028-297af84d2596 |
| result_article | PMID:9006232 |
| trial | clinicaltrials:NCT00005711 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| clinicaltrials:NCT00005711 | ClinicalTrial | Intervention for Hispanic Children With Asthma | False | https://clinicaltrials.gov/study/NCT00005711 |
| PMID:35998970 | Article | Approaches to improving symptom appraisal: a systematic literature review. | False | https://pubmed.ncbi.nlm.nih.gov/35998970/ |
| PMID:9006232 | Article | Implementation of individualized patient education for Hispanic children with asthma. | False | https://pubmed.ncbi.nlm.nih.gov/9006232/ |
| MESH:D001249 | MeSHConcept | Asthma | False | https://meshb.nlm.nih.gov/record/ui?ui=D001249 |

Exact query: `results_example_2`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### background — respiratory

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:10069869 |
| descriptor | MESH:D001249 |
| mesh_edge | urn:uuid:c5a1a506-c55d-56f5-8963-52d1feabbf96 |
| name | Relationships between duration of asthma and asthma severity among children in the Childhood Asthma Management Program (CAMP). |
| pmcid | None |
| publication_edge | urn:uuid:61cbba6d-7337-5bf9-84ac-bc03c85f3def |
| trial | clinicaltrials:NCT00000575 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| MESH:D001249 | MeSHConcept | Asthma | False | https://meshb.nlm.nih.gov/record/ui?ui=D001249 |
| clinicaltrials:NCT00000575 | ClinicalTrial | Childhood Asthma Management Program (CAMP) Phases I (Trial), II (CAMPCS), III (CAMPCS/2), and IV (CAMPCS/3) | False | https://clinicaltrials.gov/study/NCT00000575 |
| PMID:10069869 | Article | Relationships between duration of asthma and asthma severity among children in the Childhood Asthma Management Program (CAMP). | False | https://pubmed.ncbi.nlm.nih.gov/10069869/ |

Exact query: `background_example_2`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### topic — respiratory

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:11972488 |
| article_mesh_edge | urn:uuid:c656d515-109a-5173-9cc7-5f1487f5a29c |
| distance | 0 |
| hierarchy_edge | None |
| matched_descriptor | MESH:D001249 |
| mesh_type | mesh-list |
| pub_types | ["Guideline", "Journal Article"] |
| query_descriptor | MESH:D001249 |
| study_aspect | condition |
| topic | lunasai:medlineplus_topic.1507 |
| trial | clinicaltrials:NCT00000575 |
| trial_mesh_edge | urn:uuid:0781844a-466c-52ba-b922-3e910f071611 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| PMID:11972488 | Article | Asthma and allergies at school--a Swedish national position paper. | False | https://pubmed.ncbi.nlm.nih.gov/11972488/ |
| lunasai:medlineplus_topic.1507 | MedlinePlus | Asthma in Children | False | https://medlineplus.gov/asthmainchildren.html |
| clinicaltrials:NCT00000575 | ClinicalTrial | Childhood Asthma Management Program (CAMP) Phases I (Trial), II (CAMPCS), III (CAMPCS/2), and IV (CAMPCS/3) | False | https://clinicaltrials.gov/study/NCT00000575 |
| MESH:D001249 | MeSHConcept | Asthma | False | https://meshb.nlm.nih.gov/record/ui?ui=D001249 |

Exact query: `topic_example_2`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### article — respiratory

| Path/witness field | Actual value |
| --- | --- |
| citation_edge | urn:uuid:4514cec2-dde9-5333-818f-379b4f784e67 |
| cited_article | PMID:2398608 |
| citing_article | PMID:9006232 |
| descriptor | MESH:D001249 |
| in_corpus_citations | 102 |
| neighbor | PMID:2398608 |
| neighbor_mesh_edge | urn:uuid:0aa12c95-b295-5f05-8121-aa275cec4d51 |
| seed_article | PMID:9006232 |
| seed_mesh_edge | urn:uuid:d5ff1c68-6598-58c9-a3e2-fb6bf8422bf4 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| MESH:D001249 | MeSHConcept | Asthma | False | https://meshb.nlm.nih.gov/record/ui?ui=D001249 |
| PMID:2398608 | Article | Changing patterns of asthma hospitalization among children: 1979 to 1987. | False | https://pubmed.ncbi.nlm.nih.gov/2398608/ |
| PMID:9006232 | Article | Implementation of individualized patient education for Hispanic children with asthma. | False | https://pubmed.ncbi.nlm.nih.gov/9006232/ |

Exact query: `article_example_2`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### author — respiratory

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:10023966 |
| author | lunasai:openalex_author.A5054519215 |
| authorship_edge | urn:uuid:a7780163-b7f3-544a-bb07-4aa57aa8f539 |
| descriptor | MESH:D001249 |
| identity_flags | [] |
| match_status | matched |
| mesh_edge | urn:uuid:ff2933d5-66db-5ea2-8655-1d876f81dce9 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| lunasai:openalex_author.A5054519215 | Author | Brian Jonathon Lipworth | False | not exported |
| PMID:10023966 | Article | Leukotriene-receptor antagonists. | False | https://pubmed.ncbi.nlm.nih.gov/10023966/ |
| MESH:D001249 | MeSHConcept | Asthma | False | https://meshb.nlm.nih.gov/record/ui?ui=D001249 |

Exact query: `author_example_2`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### journal — respiratory

| Path/witness field | Actual value |
| --- | --- |
| descriptor | MESH:D001249 |
| guideline | PMID:11972488 |
| journal | nlm:7804028 |
| journal_edge | urn:uuid:8297662d-3891-5a0a-82ed-d602d75a7a35 |
| journal_name | Allergy |
| mesh_edge | urn:uuid:c656d515-109a-5173-9cc7-5f1487f5a29c |
| pub_types | ["Guideline", "Journal Article"] |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| nlm:7804028 | Journal | Allergy | False | https://www.ncbi.nlm.nih.gov/nlmcatalog/7804028 |
| MESH:D001249 | MeSHConcept | Asthma | False | https://meshb.nlm.nih.gov/record/ui?ui=D001249 |
| PMID:11972488 | Article | Asthma and allergies at school--a Swedish national position paper. | False | https://pubmed.ncbi.nlm.nih.gov/11972488/ |

Exact query: `journal_example_2`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### results — cardiovascular

| Path/witness field | Actual value |
| --- | --- |
| citation_edge | urn:uuid:137bdfa7-6fda-5355-bef7-c370a9a8772d |
| citing_article | PMID:25155419 |
| citing_types | ["Journal Article", "Practice Guideline", "Research Support, U.S. Gov't, P.H.S."] |
| descriptor | MESH:D006973 |
| mesh_edge | urn:uuid:4288c589-5b69-5ffd-9e74-92fa1144a542 |
| publication_edge | urn:uuid:821fff14-8d8a-5a4a-a1e2-7a2725e2cf07 |
| result_article | PMID:16585662 |
| trial | clinicaltrials:NCT00000616 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| PMID:25155419 | Article | Behavioral counseling to promote a healthful diet and physical activity for cardiovascular disease prevention in adults with cardiovascular risk factors: U.S. Preventive Services Task Force Recommendation Statement. | False | https://pubmed.ncbi.nlm.nih.gov/25155419/ |
| clinicaltrials:NCT00000616 | ClinicalTrial | PREMIER: Lifestyle Interventions for Blood Pressure Control | False | https://clinicaltrials.gov/study/NCT00000616 |
| PMID:16585662 | Article | Effects of comprehensive lifestyle modification on diet, weight, physical fitness, and blood pressure control: 18-month results of a randomized trial. | False | https://pubmed.ncbi.nlm.nih.gov/16585662/ |
| MESH:D006973 | MeSHConcept | Hypertension | False | https://meshb.nlm.nih.gov/record/ui?ui=D006973 |

Exact query: `results_example_3`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### background — cardiovascular

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:11799087 |
| descriptor | MESH:D006973 |
| mesh_edge | urn:uuid:e5eef0d5-b3c6-53bb-994b-95a610a4e72d |
| name | Development of predictive models for long-term cardiovascular risk associated with systolic and diastolic blood pressure. |
| pmcid | None |
| publication_edge | urn:uuid:06abe0c9-c26a-5ddb-8472-01f4a79a7fdb |
| trial | clinicaltrials:NCT00000479 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| MESH:D006973 | MeSHConcept | Hypertension | False | https://meshb.nlm.nih.gov/record/ui?ui=D006973 |
| clinicaltrials:NCT00000479 | ClinicalTrial | Women's Health Study (WHS): A Randomized Trial of Low-dose Aspirin and Vitamin E in the Primary Prevention of Cardiovascular Disease and Cancer | False | https://clinicaltrials.gov/study/NCT00000479 |
| PMID:11799087 | Article | Development of predictive models for long-term cardiovascular risk associated with systolic and diastolic blood pressure. | False | https://pubmed.ncbi.nlm.nih.gov/11799087/ |

Exact query: `background_example_3`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### topic — cardiovascular

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:10920346 |
| article_mesh_edge | urn:uuid:f37a8995-41eb-5521-8adb-72217de77b1c |
| distance | 0 |
| hierarchy_edge | None |
| matched_descriptor | MESH:D006973 |
| mesh_type | mesh-list |
| pub_types | ["Guideline", "Journal Article", "Practice Guideline"] |
| query_descriptor | MESH:D006973 |
| study_aspect | condition |
| topic | lunasai:medlineplus_topic.1955 |
| trial | clinicaltrials:NCT00000421 |
| trial_mesh_edge | urn:uuid:84ba5b01-dc7c-5b7a-82e3-c4e0441f0c9c |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| clinicaltrials:NCT00000421 | ClinicalTrial | Serologically Active, Clinically Stable Systemic Lupus Erythematosus | False | https://clinicaltrials.gov/study/NCT00000421 |
| lunasai:medlineplus_topic.1955 | MedlinePlus | Presión arterial alta | False | https://medlineplus.gov/spanish/highbloodpressure.html |
| MESH:D006973 | MeSHConcept | Hypertension | False | https://meshb.nlm.nih.gov/record/ui?ui=D006973 |
| PMID:10920346 | Article | Report of the National High Blood Pressure Education Program Working Group on High Blood Pressure in Pregnancy. | False | https://pubmed.ncbi.nlm.nih.gov/10920346/ |

Exact query: `topic_example_3`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### article — cardiovascular

| Path/witness field | Actual value |
| --- | --- |
| citation_edge | urn:uuid:e7fd2ec4-2692-5fda-89f9-8c0538cd63a6 |
| cited_article | PMID:12748199 |
| citing_article | PMID:16585662 |
| descriptor | MESH:D006973 |
| in_corpus_citations | 2680 |
| neighbor | PMID:12748199 |
| neighbor_mesh_edge | urn:uuid:6e147f29-4285-59e6-994f-7f7c0fe35002 |
| seed_article | PMID:16585662 |
| seed_mesh_edge | urn:uuid:4288c589-5b69-5ffd-9e74-92fa1144a542 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| PMID:12748199 | Article | The Seventh Report of the Joint National Committee on Prevention, Detection, Evaluation, and Treatment of High Blood Pressure: the JNC 7 report. | False | https://pubmed.ncbi.nlm.nih.gov/12748199/ |
| MESH:D006973 | MeSHConcept | Hypertension | False | https://meshb.nlm.nih.gov/record/ui?ui=D006973 |
| PMID:16585662 | Article | Effects of comprehensive lifestyle modification on diet, weight, physical fitness, and blood pressure control: 18-month results of a randomized trial. | False | https://pubmed.ncbi.nlm.nih.gov/16585662/ |

Exact query: `article_example_3`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### author — cardiovascular

| Path/witness field | Actual value |
| --- | --- |
| article | PMID:10022680 |
| author | lunasai:openalex_author.A5051725638 |
| authorship_edge | urn:uuid:ebacb8b2-4460-5f0a-9133-4dffa5ad2185 |
| descriptor | MESH:D006973 |
| identity_flags | [] |
| match_status | matched |
| mesh_edge | urn:uuid:c2362d0f-ee3e-5c2b-bbab-891a77a17e66 |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| MESH:D006973 | MeSHConcept | Hypertension | False | https://meshb.nlm.nih.gov/record/ui?ui=D006973 |
| PMID:10022680 | Article | Successful outcomes in pheochromocytoma surgery in the modern era. | False | https://pubmed.ncbi.nlm.nih.gov/10022680/ |
| lunasai:openalex_author.A5051725638 | Author | JAMES C. ULCHAKER | False | not exported |

Exact query: `author_example_3`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### journal — cardiovascular

| Path/witness field | Actual value |
| --- | --- |
| descriptor | MESH:D006973 |
| guideline | PMID:10920346 |
| journal | nlm:370476 |
| journal_edge | urn:uuid:b798f746-fdf5-574f-930d-363e1266d5c5 |
| journal_name | American Journal of Obstetrics and Gynecology |
| mesh_edge | urn:uuid:f37a8995-41eb-5521-8adb-72217de77b1c |
| pub_types | ["Guideline", "Journal Article", "Practice Guideline"] |

| Node ID | Label | Name | Stub | Exported source URL |
| --- | --- | --- | --- | --- |
| MESH:D006973 | MeSHConcept | Hypertension | False | https://meshb.nlm.nih.gov/record/ui?ui=D006973 |
| nlm:370476 | Journal | American Journal of Obstetrics and Gynecology | False | https://www.ncbi.nlm.nih.gov/nlmcatalog/370476 |
| PMID:10920346 | Article | Report of the National High Blood Pressure Education Program Working Group on High Blood Pressure in Pregnancy. | False | https://pubmed.ncbi.nlm.nih.gov/10920346/ |

Exact query: `journal_example_3`. Citation counts in example rows use the with-stubs graph; separately exported whole-field and ranking tables give both induced populations.

### Author profile frequencies and citation witness values in both populations

Earlier per-example `analysis_author_profile_*` exports are with-stubs views. Use these separately verified profiles for the paper; exact per-population top tens and witnesses are exported.

**neurology**

| Population | Descriptor | Term | Distinct Articles |
| --- | --- | --- | --- |
| with_stubs | MESH:D009682 | Magnetic Resonance Spectroscopy | 18 |
| with_stubs | MESH:D001921 | Brain | 12 |
| with_stubs | MESH:D005680 | gamma-Aminobutyric Acid | 10 |
| with_stubs | MESH:D013997 | Time Factors | 8 |
| with_stubs | MESH:D000927 | Anticonvulsants | 7 |
| with_stubs | MESH:D004827 | Epilepsy | 5 |
| with_stubs | MESH:D002336 | Carnosine | 4 |
| with_stubs | MESH:D007773 | Lactates | 4 |
| with_stubs | MESH:D008279 | Magnetic Resonance Imaging | 4 |
| with_stubs | MESH:D009778 | Occipital Lobe | 4 |
| without_stubs | MESH:D009682 | Magnetic Resonance Spectroscopy | 18 |
| without_stubs | MESH:D001921 | Brain | 12 |
| without_stubs | MESH:D005680 | gamma-Aminobutyric Acid | 10 |
| without_stubs | MESH:D013997 | Time Factors | 8 |
| without_stubs | MESH:D000927 | Anticonvulsants | 7 |
| without_stubs | MESH:D004827 | Epilepsy | 5 |
| without_stubs | MESH:D002336 | Carnosine | 4 |
| without_stubs | MESH:D007773 | Lactates | 4 |
| without_stubs | MESH:D008279 | Magnetic Resonance Imaging | 4 |
| without_stubs | MESH:D009778 | Occipital Lobe | 4 |

| Citation witness Article | Marked stub | With-stubs in-corpus citations | Without-stubs in-corpus citations |
| --- | --- | --- | --- |
| PMID:15111659 | False | 46 | 46 |

**respiratory**

| Population | Descriptor | Term | Distinct Articles |
| --- | --- | --- | --- |
| with_stubs | MESH:D001249 | Asthma | 92 |
| with_stubs | MESH:D018592 | Cross-Over Studies | 46 |
| with_stubs | MESH:D004311 | Double-Blind Method | 42 |
| with_stubs | MESH:D000280 | Administration, Inhalation | 40 |
| with_stubs | MESH:D004305 | Dose-Response Relationship, Drug | 28 |
| with_stubs | MESH:D001993 | Bronchodilator Agents | 27 |
| with_stubs | MESH:D018927 | Anti-Asthmatic Agents | 27 |
| with_stubs | MESH:D000420 | Albuterol | 26 |
| with_stubs | MESH:D000893 | Anti-Inflammatory Agents | 24 |
| with_stubs | MESH:D005541 | Forced Expiratory Volume | 24 |
| without_stubs | MESH:D001249 | Asthma | 92 |
| without_stubs | MESH:D018592 | Cross-Over Studies | 46 |
| without_stubs | MESH:D004311 | Double-Blind Method | 42 |
| without_stubs | MESH:D000280 | Administration, Inhalation | 40 |
| without_stubs | MESH:D004305 | Dose-Response Relationship, Drug | 28 |
| without_stubs | MESH:D001993 | Bronchodilator Agents | 27 |
| without_stubs | MESH:D018927 | Anti-Asthmatic Agents | 27 |
| without_stubs | MESH:D000420 | Albuterol | 26 |
| without_stubs | MESH:D000893 | Anti-Inflammatory Agents | 24 |
| without_stubs | MESH:D005541 | Forced Expiratory Volume | 24 |

| Citation witness Article | Marked stub | With-stubs in-corpus citations | Without-stubs in-corpus citations |
| --- | --- | --- | --- |
| PMID:2398608 | False | 102 | 102 |

**cardiovascular**

| Population | Descriptor | Term | Distinct Articles |
| --- | --- | --- | --- |
| with_stubs | MESH:D011471 | Prostatic Neoplasms | 22 |
| with_stubs | MESH:D001918 | Brachytherapy | 15 |
| with_stubs | MESH:D011468 | Prostatectomy | 14 |
| with_stubs | MESH:D016896 | Treatment Outcome | 12 |
| with_stubs | MESH:D017430 | Prostate-Specific Antigen | 12 |
| with_stubs | MESH:D005500 | Follow-Up Studies | 11 |
| with_stubs | MESH:D011470 | Prostatic Hyperplasia | 9 |
| with_stubs | MESH:D012189 | Retrospective Studies | 8 |
| with_stubs | MESH:D013997 | Time Factors | 8 |
| with_stubs | MESH:D001749 | Urinary Bladder Neoplasms | 7 |
| without_stubs | MESH:D011471 | Prostatic Neoplasms | 22 |
| without_stubs | MESH:D001918 | Brachytherapy | 15 |
| without_stubs | MESH:D011468 | Prostatectomy | 14 |
| without_stubs | MESH:D016896 | Treatment Outcome | 12 |
| without_stubs | MESH:D017430 | Prostate-Specific Antigen | 12 |
| without_stubs | MESH:D005500 | Follow-Up Studies | 11 |
| without_stubs | MESH:D011470 | Prostatic Hyperplasia | 9 |
| without_stubs | MESH:D012189 | Retrospective Studies | 8 |
| without_stubs | MESH:D013997 | Time Factors | 8 |
| without_stubs | MESH:D001749 | Urinary Bladder Neoplasms | 7 |

| Citation witness Article | Marked stub | With-stubs in-corpus citations | Without-stubs in-corpus citations |
| --- | --- | --- | --- |
| PMID:12748199 | False | 2680 | 2680 |

## Part C. Downward major-topic MeSH ranking and count/IDF variants

The same six seed IDs are reused. Topics use **all mapped descriptors**; Article query sets use actual non-check major edges. None = direct descriptor; one = observed narrower subjects of HAS_BROADER; full = all observed narrower subjects of HAS_BROADER_ANCESTOR plus direct child rows. Each original query descriptor gets at most one closest credit. Current rank is `(direct count, one-level count, deeper count, distinct nonself in-corpus citations)`; count variant merges narrower depths and ranks `(direct count, narrower count, citations)`. IDF uses `1 + ln((N+1)/(df(t)+1))` over actual non-check major-topic Article–descriptor pairs, where t is the **actual matched descriptor**. Direct matches supersede narrower matches; otherwise the maximum-IDF narrower descriptor gets that original query credit. Rank direct IDF before narrower IDF; round to 12 decimals, Article ID tie-break. No fitted weights, model calls, PageRank or private method is used.

Single-subtree-only means no direct match to any query descriptor and all narrower matches resolve unambiguously to exactly one `(query descriptor, immediate child)` branch. Polyhierarchy is not forcibly assigned to one branch; unresolved memberships are separate. Hub concentration is the maximum distinct top-list Articles supported by a branch / actual list size, including Articles that also match directly. Short lists use their actual size. Top-20 overlap is versus current rank for that same release/population/mode. Exact candidate-set and top-20/top-100 intersections across expansion modes are additionally in `ranking_*_candidate_mode_overlap.csv` and `ranking_*_toplist_mode_overlap.csv`; intersections and both list denominators permit exact Jaccard calculation. The descriptor incidence and branch diagnostics are both exported; multiple incidences overlap and cannot be summed.

| Dataset/population | Query | Expansion | Descriptors | Descriptor fan-out | Candidates | Candidate fan-out | Direct candidates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| with_stubs | article1 | full | 30 | 10.000 | 12 | 1.091 | 11 |
| with_stubs | article1 | none | 3 | 1.000 | 11 | 1.000 | 11 |
| with_stubs | article1 | one | 12 | 4.000 | 12 | 1.091 | 11 |
| with_stubs | article2 | full | 12 | 3.000 | 4 | 1.000 | 4 |
| with_stubs | article2 | none | 4 | 1.000 | 4 | 1.000 | 4 |
| with_stubs | article2 | one | 12 | 3.000 | 4 | 1.000 | 4 |
| with_stubs | article3 | full | 40 | 13.333 | 36 | 1.059 | 34 |
| with_stubs | article3 | none | 3 | 1.000 | 34 | 1.000 | 34 |
| with_stubs | article3 | one | 22 | 7.333 | 34 | 1.000 | 34 |
| with_stubs | topic1 | full | 27 | 27.000 | 8119 | 1.723 | 4713 |
| with_stubs | topic1 | none | 1 | 1.000 | 4713 | 1.000 | 4713 |
| with_stubs | topic1 | one | 9 | 9.000 | 5838 | 1.239 | 4713 |
| with_stubs | topic2 | full | 7 | 7.000 | 16601 | 1.033 | 16075 |
| with_stubs | topic2 | none | 1 | 1.000 | 16075 | 1.000 | 16075 |
| with_stubs | topic2 | one | 7 | 7.000 | 16601 | 1.033 | 16075 |
| with_stubs | topic3 | full | 14 | 7.000 | 23454 | 1.332 | 17604 |
| with_stubs | topic3 | none | 2 | 1.000 | 17604 | 1.000 | 17604 |
| with_stubs | topic3 | one | 11 | 5.500 | 23045 | 1.309 | 17604 |
| without_stubs | article1 | full | 30 | 10.000 | 12 | 1.091 | 11 |
| without_stubs | article1 | none | 3 | 1.000 | 11 | 1.000 | 11 |
| without_stubs | article1 | one | 12 | 4.000 | 12 | 1.091 | 11 |
| without_stubs | article2 | full | 12 | 3.000 | 4 | 1.000 | 4 |
| without_stubs | article2 | none | 4 | 1.000 | 4 | 1.000 | 4 |
| without_stubs | article2 | one | 12 | 3.000 | 4 | 1.000 | 4 |
| without_stubs | article3 | full | 40 | 13.333 | 36 | 1.059 | 34 |
| without_stubs | article3 | none | 3 | 1.000 | 34 | 1.000 | 34 |
| without_stubs | article3 | one | 22 | 7.333 | 34 | 1.000 | 34 |
| without_stubs | topic1 | full | 27 | 27.000 | 8119 | 1.723 | 4713 |
| without_stubs | topic1 | none | 1 | 1.000 | 4713 | 1.000 | 4713 |
| without_stubs | topic1 | one | 9 | 9.000 | 5838 | 1.239 | 4713 |
| without_stubs | topic2 | full | 7 | 7.000 | 16601 | 1.033 | 16075 |
| without_stubs | topic2 | none | 1 | 1.000 | 16075 | 1.000 | 16075 |
| without_stubs | topic2 | one | 7 | 7.000 | 16601 | 1.033 | 16075 |
| without_stubs | topic3 | full | 14 | 7.000 | 23454 | 1.332 | 17604 |
| without_stubs | topic3 | none | 2 | 1.000 | 17604 | 1.000 | 17604 |
| without_stubs | topic3 | one | 11 | 5.500 | 23045 | 1.309 | 17604 |

### Full-descendant top-list comparison (all rules, both stub populations)

The complete none/one/full × rule × top-20/top-100 matrix is `ranking_metric_comparison.csv`; this table shows full expansion.

| Dataset/pop | Query | Rule | Single-only @20 | Single-only @100 | Top-20 overlap | Hub @20 | Hub @100 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| with_stubs | article1 | current | 0/12 (0.00%) | 0/12 (0.00%) | 12/12 | 1/12 (8.33%) | 1/12 (8.33%) |
| with_stubs | article1 | count | 0/12 (0.00%) | 0/12 (0.00%) | 12/12 | 1/12 (8.33%) | 1/12 (8.33%) |
| with_stubs | article1 | idf | 0/12 (0.00%) | 0/12 (0.00%) | 12/12 | 1/12 (8.33%) | 1/12 (8.33%) |
| with_stubs | article2 | current | 0/4 (0.00%) | 0/4 (0.00%) | 4/4 | 0/4 (0.00%) | 0/4 (0.00%) |
| with_stubs | article2 | count | 0/4 (0.00%) | 0/4 (0.00%) | 4/4 | 0/4 (0.00%) | 0/4 (0.00%) |
| with_stubs | article2 | idf | 0/4 (0.00%) | 0/4 (0.00%) | 4/4 | 0/4 (0.00%) | 0/4 (0.00%) |
| with_stubs | article3 | current | 0/20 (0.00%) | 1/36 (2.78%) | 20/20 | 2/20 (10.00%) | 4/36 (11.11%) |
| with_stubs | article3 | count | 0/20 (0.00%) | 1/36 (2.78%) | 20/20 | 2/20 (10.00%) | 4/36 (11.11%) |
| with_stubs | article3 | idf | 0/20 (0.00%) | 1/36 (2.78%) | 18/20 | 2/20 (10.00%) | 4/36 (11.11%) |
| with_stubs | topic1 | current | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 1/100 (1.00%) |
| with_stubs | topic1 | count | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 1/100 (1.00%) |
| with_stubs | topic1 | idf | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 1/100 (1.00%) |
| with_stubs | topic2 | current | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 0/100 (0.00%) |
| with_stubs | topic2 | count | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 0/100 (0.00%) |
| with_stubs | topic2 | idf | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 0/100 (0.00%) |
| with_stubs | topic3 | current | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 2/100 (2.00%) |
| with_stubs | topic3 | count | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 2/100 (2.00%) |
| with_stubs | topic3 | idf | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 2/100 (2.00%) |
| without_stubs | article1 | current | 0/12 (0.00%) | 0/12 (0.00%) | 12/12 | 1/12 (8.33%) | 1/12 (8.33%) |
| without_stubs | article1 | count | 0/12 (0.00%) | 0/12 (0.00%) | 12/12 | 1/12 (8.33%) | 1/12 (8.33%) |
| without_stubs | article1 | idf | 0/12 (0.00%) | 0/12 (0.00%) | 12/12 | 1/12 (8.33%) | 1/12 (8.33%) |
| without_stubs | article2 | current | 0/4 (0.00%) | 0/4 (0.00%) | 4/4 | 0/4 (0.00%) | 0/4 (0.00%) |
| without_stubs | article2 | count | 0/4 (0.00%) | 0/4 (0.00%) | 4/4 | 0/4 (0.00%) | 0/4 (0.00%) |
| without_stubs | article2 | idf | 0/4 (0.00%) | 0/4 (0.00%) | 4/4 | 0/4 (0.00%) | 0/4 (0.00%) |
| without_stubs | article3 | current | 0/20 (0.00%) | 1/36 (2.78%) | 20/20 | 2/20 (10.00%) | 4/36 (11.11%) |
| without_stubs | article3 | count | 0/20 (0.00%) | 1/36 (2.78%) | 20/20 | 2/20 (10.00%) | 4/36 (11.11%) |
| without_stubs | article3 | idf | 0/20 (0.00%) | 1/36 (2.78%) | 18/20 | 2/20 (10.00%) | 4/36 (11.11%) |
| without_stubs | topic1 | current | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 1/100 (1.00%) |
| without_stubs | topic1 | count | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 1/100 (1.00%) |
| without_stubs | topic1 | idf | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 1/100 (1.00%) |
| without_stubs | topic2 | current | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 0/100 (0.00%) |
| without_stubs | topic2 | count | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 0/100 (0.00%) |
| without_stubs | topic2 | idf | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 0/100 (0.00%) |
| without_stubs | topic3 | current | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 2/100 (2.00%) |
| without_stubs | topic3 | count | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 2/100 (2.00%) |
| without_stubs | topic3 | idf | 0/20 (0.00%) | 0/100 (0.00%) | 20/20 | 0/20 (0.00%) | 2/100 (2.00%) |

The v0.2 IDF/DF census and all selected descriptor credits are exported for each induced population. Equal measured DF corpora would not by themselves imply equal citation-based tie-breaks. The independent re-score separately recomputes the full DF corpus, IDF, every ordered top 100 and every hub/subtree diagnostic for **54 cases per population**, **108 ranking cases / 216 list diagnostics** in total. Topic top lists with abundant direct matches have little power to measure hierarchy-only subtype dominance; zero single-subtree-only share is not a precision/relevance metric. No hub-control or relevance improvement is claimed without an observed reduction and clinical judgment.

### Scoring-variant effects versus current ranking

Each context is a query × expansion mode × cutoff (six queries × three modes × two cutoffs = 36 per population/rule). Denominators are identical across rules within each context. Lower concentration/share is a descriptive change, not a relevance gain; many topic contexts contain only direct hits.

| Population | Variant | Hub lower / same / higher | Single-subtree-only lower / same / higher |
| --- | --- | --- | --- |
| with_stubs | count | 0 / 36 / 0 | 0 / 36 / 0 |
| with_stubs | idf | 0 / 36 / 0 | 0 / 36 / 0 |
| without_stubs | count | 0 / 36 / 0 | 0 / 36 / 0 |
| without_stubs | idf | 0 / 36 / 0 | 0 / 36 / 0 |

### Source-array presence versus distinct-source evidence

The following complete-population counts distinguish a nonempty alternate-source array from genuinely distinct source labels. Collapsed rows are not independent clinical evidence. Compare counts per edge separately from per-pair union-retention failures.

**published**

| Native role type | Edges | Nonempty alternate array | Empty alternate array | At least two distinct sources | Primary label repeated in alternate array |
| --- | --- | --- | --- | --- | --- |
| CITES_BACKGROUND | 736649 | 18097 | 10 | 18097 | 0 |
| HAS_DERIVED_PUBLICATION | 202205 | 3621 | 31 | 3621 | 0 |
| VALIDATED_BY | 156167 | 2830 | 0 | 2830 | 0 |

## Paper figures

- [PMC-route coverage, SVG](../figures/pmc_route_coverage.svg) ([PNG](../figures/pmc_route_coverage.png)); values: `paper_pmc_coverage.csv`.

## Source roles versus protocol publication types

This exact-label join counts known metadata only. Missing publication types, especially on stubs, prevent a complete publication-subtype census. A Clinical Trial Protocol label alongside source RESULT is a metadata-role overlap requiring adjudication, not proof that the registry is wrong or that the paper has no results. No method/protocol category is inferred from titles.

| Population | Source role | Link edges | Edges with known publication types | Protocol-labeled edges | Distinct protocol-labeled Articles |
| --- | --- | --- | --- | --- | --- |
| with_stubs | BACKGROUND | 736649 | 216211 | 536 | 487 |
| with_stubs | DERIVED | 202205 | 58150 | 3854 | 3810 |
| with_stubs | RESULT | 156167 | 50672 | 162 | 157 |
| without_stubs | BACKGROUND | 228957 | 216211 | 536 | 487 |
| without_stubs | DERIVED | 59557 | 58150 | 3854 | 3810 |
| without_stubs | RESULT | 52878 | 50672 | 162 | 157 |

## What looks wrong or remains scientifically unresolved

1. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* Measured on the release itself: 578,177 canonical identity-only Articles; titled stubs 0; stubs with publication types 0. Existing graph relationships on identity-only nodes do not establish that bibliographic metadata exists.
2. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* Measured on the release itself: extra same NCT-PMID-role edges beyond one per role-pair: 0. Edge-ID uniqueness is separately verified.

3. **Journal identities remain mostly fallback strings.** Only 376/2,734 have NLM IDs; ISSN/ISSN-L/source IDs are absent and 2,358 have no exported source URL. Zero exact abbreviation collisions does not resolve aliases.
4. **PMC routes are not verified full-text/OA availability.** Access/deposit/figure/table metadata is absent; a graph route can exist without an Article PMCID property.
5. **Provenance gaps remain.** See the per-type completeness table. Release-linked IDs, primary source identifiers, direct source URLs and agent classes answer different questions.
6. **Selection and semantic limitations remain.** Removing true stubs selects for observable bibliography/citations. Registry RESULT/BACKGROUND/DERIVED roles are not clinical-quality adjudications; citations are not endorsement and exact-name/hierarchy trial mapping is not proof of equivalent populations.
7. **Analytics currentness remains unresolved.** The published README states that PageRank/community runs can predate the source snapshot. No analytics property enters the transparent ranking.
8. **Publication metadata has residual inconsistencies.** The README citation still uses a TBD DOI despite the valid published DOI; broad VALIDATED_BY wording appears before the explicit role split and the HAS_MESH direction list omits trial/topic uses. The recorded exporter commit has dirty=true; exact published file hashes, not that commit alone, define this resource. Source registry/shard manifests are available on HF; Zenodo uses the separately verified bundles.
9. **Exact major-label strings do not always link.** Unmatched labels and PMC records with multiple PubMed endpoints are measured, not assigned an unobserved cause or repaired.
10. **Self-citation sensitivity is explicit.** Primary paper chains exclude self-links; historical self-inclusive controls are retained.
11. **Protocol labels overlap source RESULT roles.** The exact NLM-label join is a metadata-bounded lower bound and requires clinical/source adjudication; it does not prove a registry-role error.

The data support descriptive source-integrated resource and connectivity claims. They do not establish expert validation, causal benefit, clinical retrieval quality, complete literature recall, perfect identity resolution, verified OA/full text, or a novel ranking algorithm. Six query examples are purposive, not a representative benchmark.
