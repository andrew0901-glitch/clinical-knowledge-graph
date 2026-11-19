# Paper-ready headline numbers — v0.2.0 audit (graph files identical in v0.2.1)

> **Scope.** These documents report the audit of release **v0.2.0** (Zenodo 10.5281/zenodo.24091964, HF tag `clinical-v0.2.0`). All 107 node/edge files of release v0.2.1 (Zenodo 10.5281/zenodo.24108692) are **byte-identical** (same SHA-256) to the v0.2.0 files, so every statement about graph content holds for v0.2.1. Statements about the *release metadata files* (dataset card, citation file, exporter commit) describe v0.2.0. Comparisons with earlier releases and with the unreleased pre-correction build were removed from this copy; see `../EXCLUDED.md`.

**Lunas Clinical Evidence Knowledge Graph**, DOI [10.5281/zenodo.24091964](https://doi.org/10.5281/zenodo.24091964); frozen snapshot 2026-11-07; HF tag `clinical-v0.2.0`, commit `76af01bf51483264b95bece5ffef0999521d21cd`. The release contains **12,067,108 nodes and 105,758,066 edges**. All 123 manifest-listed files and eight Zenodo graph-bundle hashes verified; independent sorting found no duplicate node/edge IDs or missing endpoints. Counts below are complete-population censuses.

| Measure | With stubs | Without stubs |
| --- | --- | --- |
| Article nodes | 3,724,062 | 3,145,885 |
| Canonical identity-only Articles | 578,177 | excluded |
| Trials with ≥1 RESULT-role publication | 42,075 | 22,793 |
| Distinct RESULT-role Articles | 140,372 | 45,865 |
| Results Articles cited by guideline/systematic review (nonself) | 23,460 | 23,460 |
| Trials with background references | 97,142 | 62,788 |
| Distinct background Articles | 539,317 | 146,132 |
| Articles with shared-MeSH citation neighbor | 2,533,201 | 2,533,201 |
| Journal-linked Articles | 3,147,895 | 3,145,885 |

There are **606,580 registry trials**, **2,033 MedlinePlus topics**, **5,134,220 Author nodes**, **2,734 Journal nodes** and **1,334,061 PMCRecord nodes**. Downward full expansion connects **1,486/2,033 topics** to both a guideline/review and a condition trial through the same matched MeSH descriptor. Of the Journal nodes, **376** have NLM IDs; the others are abbreviation fallbacks. No ISSN/ISSN-L is exported.

RESULT-role Articles cited by in-graph guidelines/systematic reviews have a PMC identifier/link route in 7,277/23,460 (31.02%) (with stubs); 7,277/23,460 (31.02%) (without stubs). **PMC routes are not verified accessible/OA full text**; access status, figure/table counts and reuse rights are unavailable.

The same six purposive queries were evaluated under none/one/all-descendant major-topic-only MeSH expansion, check tags excluded, using current/count/IDF ranking. These are illustrative tests, not representative retrieval benchmarks or clinical validation. Exact tables/figures, source hashes, code revisions and independently checked top-100 orders are linked from the audit reports and `REPRODUCIBILITY_MANIFEST.json`. Source RESULT labels and citations do not imply trial success or guideline endorsement.
