# Example reports

Six reports for three MeSH conditions, built from the graph files of the public **Lunas Clinical Evidence KG v0.2.1**
release (snapshot 2026-11-07; Zenodo [10.5281/zenodo.24108692](https://doi.org/10.5281/zenodo.24108692); Hugging Face
`lunas-health/clinical-evidence-kg`, tag `clinical-v0.2.2`, whose graph files are identical to v0.2.1). Each folder has a
`README.md` that reads on GitHub, a self-contained `report.html` with the same content and charts (no scripts or external
files; download it and open it in a browser), `summary.json`, and the CSV files the report is built from.

Only the 107 node and edge files listed in the release `manifest.json` were read. The annotation-layer files
(`jev_evidence_annotations.jsonl`, `jev_manifest.json`) were not used.

## Trial landscape (`trial_landscape.py`)

Trials whose ClinicalTrials.gov condition browse terms include the descriptor or a narrower descriptor (MeSH tree-number
explode). A results Article is linked to a trial with the RESULT role (`VALIDATED_BY`); one Article can be linked to several
trials, so both distinct Articles and trial-article links are given. Identity-only Articles carry a PMID but no PubMed record.
"Cited by a guideline or SR": cited (CITES) by at least one Article in the graph whose NLM publication types include Guideline,
Practice Guideline or Systematic Review, an Article citing itself excluded.

| Condition | Report | Trials | Results Articles (distinct / with PubMed record) | Results trial-article links | Distinct results Articles cited by a guideline or SR |
|---|---|---:|---:|---:|---:|
| Breast Neoplasms (D001943) | [README](trial_landscape_examples/breast_neoplasms_D001943/README.md) · [report.html](trial_landscape_examples/breast_neoplasms_D001943/report.html) | 14,321 | 3,087 / 1,211 | 3,258 | 646 |
| Alzheimer Disease (D000544) | [README](trial_landscape_examples/alzheimer_disease_D000544/README.md) · [report.html](trial_landscape_examples/alzheimer_disease_D000544/report.html) | 3,853 | 692 / 188 | 714 | 65 |
| Heart Failure (D006333) | [README](trial_landscape_examples/heart_failure_D006333/README.md) · [report.html](trial_landscape_examples/heart_failure_D006333/report.html) | 5,828 | 1,738 / 563 | 1,845 | 305 |

## Evidence map (`evidence_map.py --major-only`)

Articles indexed as a major topic to the descriptor or a narrower descriptor (`HAS_BROADER_ANCESTOR`, which follows MeSH tree
numbers), each assigned to one design class in the order guideline > systematic review or meta-analysis > randomized
controlled trial > other clinical trial > observational study > other, from NLM publication types. Primary studies are the
randomized and other clinical trials; "cited" means cited by at least one guideline, systematic review or meta-analysis
anywhere in the graph, an Article citing itself excluded. The 2022-2026 guidelines and reviews are listed with PMID, title
and year in each report.

| Condition | Report | Articles | Primary studies | Cited / not cited within the graph | RCTs cited | Distinct citing guidelines and reviews | SR or MA / guidelines 2022-2026 |
|---|---|---:|---:|---:|---:|---:|---:|
| Breast Neoplasms (D001943) | [README](evidence_map_examples/breast_neoplasms_D001943/README.md) · [report.html](evidence_map_examples/breast_neoplasms_D001943/report.html) | 47,004 | 4,854 | 2,297 / 2,557 | 1,706 | 1,874 | 397 / 46 |
| Alzheimer Disease (D000544) | [README](evidence_map_examples/alzheimer_disease_D000544/README.md) · [report.html](evidence_map_examples/alzheimer_disease_D000544/report.html) | 11,925 | 516 | 226 / 290 | 182 | 244 | 107 / 2 |
| Heart Failure (D006333) | [README](evidence_map_examples/heart_failure_D006333/README.md) · [report.html](evidence_map_examples/heart_failure_D006333/report.html) | 13,500 | 1,982 | 954 / 1,028 | 863 | 1,134 | 162 / 15 |

## How these were produced

Citation counts include only citations between Articles in the graph, so all cited counts are lower bounds; an Article not
cited within the graph may be cited elsewhere. The 578,177 identity-only Articles carry no publication types, MeSH terms or
citation edges in this release, so the evidence maps are the same with or without them.

| | |
|---|---|
| Release | Lunas Clinical Evidence KG v0.2.1, snapshot 2026-11-07 |
| Release `manifest.json` SHA-256 | `518ed9ae1f2e132aeec9a6d216cbd40d43db01e1ded9ee42901ad635c38aa17c` |
| Input files | the 107 node and edge files in `manifest.json`; each SHA-256 checked before the run: [release_inputs_v0.2.1.sha256](release_inputs_v0.2.1.sha256) (`sha256sum -c` format) |
| Tool commit | [`7e65aa6`](https://github.com/lunas-health/clinical-evidence-kg/commit/7e65aa625ff7c9103d0c66007fdecfe193e6b817) for both tools |
| `trial_landscape.py` SHA-256 | `9a2bf6b098a51896bea1234b469b2a586f752c56cfc0e3f294893cabb1b19adf` |
| `evidence_map.py` SHA-256 | `b1882df0e7bcc4a9e996bd8b285759c0e19ad7029ea49e57a4f8c2cae08664ef` |

```bash
hf download lunas-health/clinical-evidence-kg --repo-type dataset --revision clinical-v0.2.2 --local-dir ckg \
  --include "manifest.json" "nodes/*" "edges/*"
(cd ckg && sha256sum -c ../examples/release_inputs_v0.2.1.sha256)
for d in D001943 D000544 D006333; do
  python examples/trial_landscape.py --input ckg --condition $d --out out/trial_landscape/$d
  python examples/evidence_map.py --input ckg --condition $d --major-only --out out/evidence_map/$d
done
```

`trial_landscape_examples/data_check.csv` is the field-completeness table (`trial_landscape.py --data-check`).
Trial data originate from ClinicalTrials.gov; PubMed and MeSH from the U.S. National Library of Medicine; citations from
OpenAlex. Graph files: CC0 1.0.
