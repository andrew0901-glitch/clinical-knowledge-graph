# Rerun the audit from scratch (public files only)

Release: **Lunas Clinical Evidence KG v0.2.1**, snapshot 2026-11-07, Zenodo [10.5281/zenodo.24108692](https://doi.org/10.5281/zenodo.24108692),
Hugging Face dataset `lunas-health/clinical-evidence-kg` tag `clinical-v0.2.2` (tag `clinical-v0.2.1` carries the same `manifest.json`,
SHA-256 `518ed9ae1f2e132aeec9a6d216cbd40d43db01e1ded9ee42901ad635c38aa17c`). Nothing here needs credentials, a database or a network
connection after the download.

## 0. Requirements

| | lanes (`lanes/`) | release audit (`release_audit/`) |
|---|---|---|
| Python | 3.12 | 3.12 |
| Packages | `duckdb==2.0.0` | `duckdb==2.0.0`, `orjson`, `matplotlib` (figures only) |
| Other | -- | GNU `sort`, `uniq`, `comm` (`verify_integrity.py`) |
| Disk (besides the 5.4 GB release) | about 4 GB | about 150 GB |
| RAM | 20 GB | 32 GB |
| Time | about 5 minutes | hours |

## 1. Fetch and verify the release (one data path)

```bash
python audit/scripts/fetch_release.py            # downloads the 107 graph files into ./data/clinical_kg_release_v0.2.1
export CLINICAL_KG_DATA=$PWD/data/clinical_kg_release_v0.2.1   # the single configurable path every script reads
```

`fetch_release.py` checks every file against `audit/release_inputs_v0.2.1.sha256` (107 hashes pinned in this repository) and deletes any
file that does not match. `--dest DIR` puts the data elsewhere; `--ref clinical-v0.2.1` fetches from the other tag; `--verify-only`
hashes existing files without downloading.

Working files are written next to the data, never inside it: `<CLINICAL_KG_DATA>.audit_work` (lanes) and
`<CLINICAL_KG_DATA>.release_audit_work` (release audit).

**From Zenodo instead.** Zenodo stores the graph as eight concatenated bundles (`nodes-w00..w03`, `edges-w00..w03`), not as the 107 files.
`audit/scripts/verify_zenodo_bundles.py` reproduces each bundle's SHA-256, byte count and record count from the 107 files and checks that the
shard hashes in Zenodo's manifest equal the pinned hashes, so the two routes are bound to the same bytes.

## 2. Lanes (everything the preprint's headline numbers need)

```bash
audit/scripts/run_lanes.sh
```

This runs, in order: `build.py` (re-verifies the 107 hashes, builds the DuckDB tables, asserts the manifest's label and edge-type counts, the
578,177 identity-only Articles and the 40 check tags), lanes 2, 3, 4 and 5, lane 1 (this repository's `examples/trial_landscape.py`), the lane 3
cross-check (this repository's `examples/evidence_map.py` over the same files, 192 field comparisons), `headline_numbers.py` (computes every
headline number of the preprint and exits non-zero if one differs from the printed value), the Zenodo bundle check and `lanes_manifest.py`
(records SQL, input hashes and output hashes in `manifests/REPRODUCIBILITY_MANIFEST.lanes.json`).

Reruns write over `lanes/results` and `lanes/tables`. Compare with `git diff --stat audit/lanes`. Expected differences are only the volatile fields
(`seconds`, `elapsed`, `run_seconds`, `code_commit`) and, in `lane1_trial_landscape.json`, the per-CSV comparison of `sites.csv` and
`results_publications.csv`, whose rows with equal sort keys can come out in a different order.

## 3. Release-wide audit (optional, large)

Run from the repository root. Keep the writers (`prepare`, `analyze`) sequential; the read-only checks can run concurrently afterwards.

```bash
python audit/release_audit/scripts/verify_inputs.py
python audit/release_audit/scripts/scan.py              # independent full raw census; writes the narrow projections
python audit/release_audit/scripts/prepare.py
python audit/release_audit/scripts/analyze.py
python audit/release_audit/scripts/extra_checks.py
python audit/release_audit/scripts/defects.py
python audit/release_audit/scripts/strict_chains.py
python audit/release_audit/scripts/metadata_unions.py
python audit/release_audit/scripts/profile_examples.py
python audit/release_audit/scripts/publication_type_sanity.py
python audit/release_audit/scripts/topic_sensitivity.py
python audit/release_audit/scripts/verify_integrity.py
python audit/release_audit/scripts/verify_headlines.py
ARTICLE_POPULATION=with_stubs    python audit/release_audit/scripts/rank.py
ARTICLE_POPULATION=with_stubs    python audit/release_audit/scripts/rank_verify.py
ARTICLE_POPULATION=without_stubs python audit/release_audit/scripts/rank.py
ARTICLE_POPULATION=without_stubs python audit/release_audit/scripts/rank_verify.py
```

The committed results in `release_audit/results` and `release_audit/tables` come from the original run of this pipeline against release v0.2.0, whose 107
graph files are byte-identical to v0.2.1's (see README). Steps that need the v0.1.0 release or the unreleased pre-correction build were removed
(`EXCLUDED.md`). SQL, parameters and denominators for every output are in `release_audit/results/*_queries.json`.

## 4. Tests

```bash
python -m pytest tests -q
```

## 5. Check the deposit itself

```bash
python audit/tools/safety_scan.py        # secrets, internal hostnames, personal machine paths: expects 0 findings
```
