# Audit lanes for release v0.2.1 (Nov 2026)

**Input.** Only the 107 node and edge files listed in the v0.2.1 `manifest.json` (snapshot 2026-11-07), fetched from the public release (`../scripts/fetch_release.py`).
- `scripts/build.py` re-verified every SHA-256 (107/107) and built one local DuckDB file.
- Label and edge-type counts match the manifest exactly.
- Stubs (`ctgov_identity_only`): 578,177.
- CITES self-links removed: 24,044.
- MeSH check tags: all 40 resolve, and none is ever used as a query, matched or expansion descriptor.
- SQL, input hashes, code commits and output hashes are under `v023_lanes` in `../manifests/REPRODUCIBILITY_MANIFEST.lanes.json` (also merged into `../manifests/REPRODUCIBILITY_MANIFEST.public.json`).
- Every lane was rerun from scratch from the public files for this deposit; lanes 2-5 and the build census reproduce the earlier run's values exactly (see `../README.md`).

**Populations.** Every Article-level result below is reported for both populations: with and without the 578,177 identity-only stubs. In v0.2.1 the stubs carry no `pub_types`, HAS_MESH or CITES edges (0 of each), so the two populations give identical numbers for every MeSH-reached Article count. That is a fact about this release, not an assumption. The tables in `tables/` keep both rows.

## Lane 1: trial landscape rerun (`examples/trial_landscape.py` of this repository)

The tool is run over a folder holding exactly the 107 manifest files. Every summary field of the three committed v0.2.1 example summaries is **identical** to the rerun except `run_seconds`, which changes from run to run. Seven of the nine committed CSVs per condition are byte-identical; `sites.csv` and `results_publications.csv` contain the same rows in a different order, because rows with equal sort keys are not ordered deterministically (`lane1_trial_landscape.json` → `committed_csv_comparison`: `same_rows_different_order_of_tied_rows`). `data_check.csv` is identical.

All fields: `tables/lane1_summary_fields.csv`.

| field | D001943 | D000544 | D006333 |
|---|---:|---:|---:|
| descriptors_in_expansion / descriptor_level_closure | 9 / 11 | 1 / 1 | 6 / 6 |
| trials (direct / narrower only) | 14,321 (13,445 / 876) | 3,853 (3,853 / 0) | 5,828 (5,560 / 268) |
| recruiting / not yet recruiting | 1,992 / 645 | 536 / 168 | 688 / 247 |
| interventional | 11,198 | 3,037 | 3,932 |
| lead sponsors | 3,040 | 1,265 | 1,853 |
| trials with sites | 12,611 | 3,333 | 5,071 |
| trials / recruiting without sponsor record | 437 / 163 | 122 / 58 | 173 / 47 |
| sites (= before merge) / countries | 60,591 / 119 | 18,423 / 72 | 29,720 / 127 |
| trials with results article | 1,006 | 244 | 467 |
| results_articles | 3,258 | 714 | 1,845 |
| results_articles_cited_by_guideline_or_sr | 735 | 68 | 329 |
| CT.gov ancestor-term crosscheck (trials / also ours) | 14,321 / 14,321 | 3,853 / 3,853 | 5,828 / 5,828 |

**The tool's rules** (from the code, with the counts measured):
- **Article population: with stubs.** No stub filter anywhere; rows are only flagged `article_is_stub`.
- **`results_articles` counts trial–article VALIDATED_BY rows, not distinct Articles.**

| | D001943 | D000544 | D006333 |
|---|---:|---:|---:|
| rows (tool) | 3,258 | 714 | 1,845 |
| distinct Articles, with stubs | 3,087 | 692 | 1,738 |
| distinct Articles, without stubs | 1,211 | 188 | 563 |
| stub rows (distinct stub Articles) | 1,931 (1,876) | 521 (504) | 1,251 (1,175) |
| distinct Articles cited by a non-self guideline/SR, with = without stubs | 646 | 65 | 305 |
| trials with results article, with / without stubs | 1,006 / 553 | 244 / 106 | 467 / 251 |

- **Self-citation: not excluded.** The tool's citer table holds 49 self-link rows release-wide. Excluding them changes none of the three conditions: 735 / 68 / 329 cited rows either way. Without stubs these counts also stay 735 / 68 / 329, because stubs are never cited by a guideline or SR in-graph.
- **Citing types:** "guideline or SR" means Guideline / Practice Guideline / Systematic Review. Meta-Analysis is a separate column and not part of the summary metric.
- **Hierarchy:** tree-number-precise explode, the same set as the release's HAS_BROADER_ANCESTOR.

## Lane 2: MedlinePlus English-only (`tables/lane2_topic_table_english.csv`, per topic: `tables/lane2_per_topic.csv`)

- MedlinePlus has 1,017 English and 1,016 Spanish topics.
- TRANSLATION_OF runs Spanish → English, 1,016 edges, one-to-one. One English topic has no Spanish counterpart.
- **Spanish records always share their English counterpart's MeSH mappings:** 1,016 / 1,016 pairs have identical descriptor sets *and* identical major-topic flags. Two pairs are unmapped on both sides.

English-only (n = 1,017), identical with and without stubs:

| expansion | guideline or review | condition trial | both, same descriptor | both, any descriptor |
|---|---:|---:|---:|---:|
| none | 1,011 | 720 | 719 | 719 |
| one level | 1,011 | 740 | 734 | 739 |
| full descendants | 1,011 | 749 | 743 | 748 |

Major-topic guideline-or-review reach: 1,009 / 1,010 / 1,010. Reconciliation with all 2,033 topics: guideline or review 2,021; condition trial 1,440 / 1,480 / 1,498; both, same descriptor 1,438 / 1,468 / **1,486**; both, any descriptor 1,438 / 1,478 / **1,496**.

## Lane 3: evidence maps, full downward expansion (`tables/lane3_*`)

Design rule: exclusive, in the order guideline > SR or MA > RCT > other clinical trial > observational > other. The type lists are in `results/lane3_evidence_maps.json` → `design_rule`. Citing review means any in-graph guideline, SR or MA, self-links removed.

| HAS_MESH any (with = without stubs) | D001943 | D000544 | D006333 |
|---|---:|---:|---:|
| descriptors | 9 | 1 | 6 |
| Articles | 53,369 | 14,468 | 16,709 |
| guideline / SR or MA | 197 / 1,194 | 6 / 284 | 29 / 496 |
| RCT / other trial | 3,248 / 1,953 | 364 / 198 | 1,886 / 401 |
| observational / other | 406 / 46,371 | 153 / 13,463 | 501 / 13,396 |
| primary studies: cited / not cited by in-graph SR, MA or guideline | 2,469 / 2,732 | 249 / 313 | 1,122 / 1,165 |
| RCTs cited | 1,837 of 3,248 | 196 of 364 | 1,002 of 1,886 |
| distinct citing reviews (of which in map) | 2,058 (797) | 266 (85) | 1,477 (342) |
| SR or MA / guidelines published 2022–2026 | 419 / 47 | 124 / 2 | 178 / 15 |

Major-topic-only results are in the same CSVs. For example, D001943: 47,004 Articles, 2,297 of 4,854 primary studies cited, 1,874 citing reviews.

**Independent check:** the new companion `examples/evidence_map.py` was run separately over the same 107 files and compared on 16 fields × 4 variants × 3 conditions, with **0 mismatches** (`results/lane3_crosscheck_companion.json`).

## Lane 4: Osteosarcoma (D012516), full expansion (`tables/lane4_*`)

The expansion has 3 descriptors: Osteosarcoma, plus two narrower branches. One of them is **Sarcoma, Ewing (D012512)**, which sits under Osteosarcoma in the MeSH tree (C04.557.450.565.575.650.800 and C04.557.450.795.620.800).

| | value |
|---|---:|
| condition trials, full expansion | 598 |
| direct on Osteosarcoma | 467 |
| reached **only** through Ewing sarcoma | **130 (21.7%)** |
| without the Ewing branch | 468 |
| Articles with the Ewing branch (any indexing; with = without stubs) | 4,668 |
| Articles without the Ewing branch | 3,590 |
| Articles only through Ewing (major-topic: 942 of 3,706) | 1,078 (23.1%) |

Narrower branches ranked by contribution:
1. **Sarcoma, Ewing:** 244 trials (130 only through it), 1,312 Articles (1,078 only through it).
2. **Osteosarcoma, Juxtacortical:** 2 trials (1 only through it), 38 Articles (30 only through it).

## Discrepancies and caveats

1. **Topic "both" has two definitions.** The paper headline and caption say "1,486 / 2,033 topics reach both through the same matched MeSH descriptor", and 1,486 is reproduced exactly. But the committed `tables/analysis_topic_population.csv` column `reaching_both` (1,496 for full) counts topics that reach a guideline/review and a condition trial through *any* descriptors. Use one definition throughout the table and text. English-only: 743 (same descriptor) vs 748 (any descriptor).
2. **The trial-landscape `results_articles` field is a row count, not a distinct-Article count, and it includes stubs.** The paper should label it that way, or use the distinct and without-stub values above.
3. **"Full descendants" means tree-precise in this release.** HAS_BROADER_ANCESTOR follows tree numbers. Walking HAS_BROADER transitively ignores tree numbers and adds two descriptors to D001943: Carcinoma, Intraductal, Noninfiltrating and Paget's Disease, Mammary. That adds 121 Articles and 64 trials (14,385 vs 14,321). These descriptors reach Breast Neoplasms only through Breast Carcinoma In Situ's *other* tree position. The trial tool's `descriptor_level_closure` (11) is this untyped closure.
4. **Stub sensitivity is null for every MeSH-reached Article metric** because stubs have no MeSH, pub_types or CITES edges. It is non-null only for trial-linked Article counts (lane 1).

## Lane 5: final paper numbers (`scripts/lane5_paper_numbers.py`, `tables/lane5_*`)

### Evidence maps, major topic only, tree-number full expansion

Results are identical with and without stubs.

| | D001943 | D000544 | D006333 |
|---|---:|---:|---:|
| Articles | 47,004 | 11,925 | 13,500 |
| guideline | 180 | 5 | 25 |
| SR or MA | 1,101 | 240 | 410 |
| RCT | 3,031 | 340 | 1,653 |
| other clinical trial | 1,823 | 176 | 329 |
| observational | 370 | 128 | 413 |
| other | 40,499 | 11,036 | 10,670 |
| primary studies (RCT + other trial) | 4,854 | 516 | 1,982 |
| cited / not cited (counted separately; they sum to primary) | 2,297 / 2,557 | 226 / 290 | 954 / 1,028 |
| RCTs cited | 1,706 | 182 | 863 |
| distinct citing reviews | 1,874 | 244 | 1,134 |
| SR or MA / guideline, 2022–2026 | 397 / 46 | 107 / 2 | 162 / 15 |

**Rules as implemented.**
- **Design classes.** Each Article goes in the first class it matches:
  - guideline: Guideline, Practice Guideline
  - SR or MA: Systematic Review, Meta-Analysis, Network Meta-Analysis
  - RCT: Randomized Controlled Trial, plus its Veterinary variant
  - other clinical trial: Clinical Trial; Clinical Trial, Phase I–IV; Controlled Clinical Trial; Pragmatic Clinical Trial; Equivalence Trial; Adaptive Clinical Trial; Clinical Trial, Veterinary
  - observational: Observational Study, plus its Veterinary variant
  - other: everything else, including Clinical Trial Protocol and Articles with no types
- **Primary studies:** the RCT and other-clinical-trial classes.
- **Citing set:** any Article in the graph whose types include a guideline, SR, MA or Network MA type. It is *not* restricted to Articles indexed with the condition. CITES self-links are removed.
- **Year window:** integer `year` from 2022 to 2026 inclusive. All map Articles have a year; the range is 1990–2026.

### Trial-landscape results Articles, recomputed from the release files

| | D001943 | D000544 | D006333 |
|---|---:|---:|---:|
| results_articles (VALIDATED_BY rows) | 3,258 | 714 | 1,845 |
| distinct results Articles, with stubs | 3,087 | 692 | 1,738 |
| distinct results Articles, without stubs | 1,211 | 188 | 563 |
| results_articles_cited_by_guideline_or_sr | 735 rows | 68 rows | 329 rows |
| distinct results Articles cited by a guideline or SR, with = without stubs | 646 | 65 | 305 |

`results_articles_cited_by_guideline_or_sr` counts **rows**. The distinct counts are the same under the tool's rule (self-links kept) and with self-links removed, and the same with and without stubs. "Guideline or SR" here means Guideline / Practice Guideline / Systematic Review only, not Meta-Analysis.

### ClinicalTrial node properties

606,580 nodes, of which 605,610 have a registry record (title present). Fill rates are over all nodes / over registry records:

| key(s) | fill rate |
|---|---|
| id, iri, nct_id, category, lunasai_labels, lunasai_layer, url_source | 100% |
| name (title, ≤300 chars) | 99.84 / 100% |
| overall_status | 99.84 / 100% |
| start/completion date kind + origin, valid_start_date_basis | 99.84 / 100% |
| last_update_posted_date (+ kind, origin), valid_start_date | 99.84 / 100% |
| study_type | 99.68 / 99.84% |
| start_date | 98.96 / 99.11% |
| enrollment | 98.66 / 98.82% |
| completion_date | 97.09 / 97.24% |
| phase (includes "NA") | 76.17 / 76.29% |
| invalid_reason, valid_end_date | 18 nodes |
| provenance_id | present on all nodes, always null |

**Verdict on the paper's statement: confirmed, with additions.** Trial nodes have no interventions, outcomes, design details, eligibility, stop reasons or enrollment type. The statement should add three things:
- Trial nodes also carry the last-update-posted date.
- 18 nodes carry `invalid_reason` (deleted in the source).
- The title is held in `name`. Its 300-character maximum matches ClinicalTrials.gov's brief-title limit, but the release does not label it as the brief title.
