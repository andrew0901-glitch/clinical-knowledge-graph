#!/usr/bin/env python3
"""Write the --full-record input of trial_report.py from a release's ClinicalTrial node files.

  python examples/extract_full_record.py --input <release dir> --out full_record.parquet

Reads only the files manifest.json lists (same rule as the loaders). Releases from the one after v0.2.x carry the
ClinicalTrials.gov full study record on ClinicalTrial nodes (official_title, intervention_names, outcomes,
primary_completion_date, why_stopped, design, eligibility, results_first_posted_date); with an older release the
output has nct_id only and trial_report.py marks those fields as missing.
"""
import argparse, gzip, json, os, sys

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from trial_report import FULL_FIELDS  # noqa: E402


def node_files(root):
    man = json.load(open(os.path.join(root, "manifest.json")))
    return [os.path.join(root, e["path"]) for e in man["nodes"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tmp = a.out + ".jsonl"
    n = 0
    with open(tmp, "w") as out:
        for path in node_files(a.input):
            with gzip.open(path, "rt") as fh:
                for line in fh:
                    if '"ClinicalTrial"' not in line:
                        continue
                    r = json.loads(line)
                    if "ClinicalTrial" not in (r.get("lunasai_labels") or []):
                        continue
                    row = {"nct_id": r.get("nct_id")}
                    row.update({f: r.get(f) for f in FULL_FIELDS})
                    out.write(json.dumps(row) + "\n")
                    n += 1
    duckdb.sql(f"COPY (SELECT * FROM read_json('{tmp}', format='newline_delimited', maximum_object_size=50000000, "
               f"columns={{{', '.join(repr(c) + ': ' + repr(t) for c, t in _types())}}})) TO '{a.out}' (FORMAT parquet)")
    os.remove(tmp)
    print(f"{n:,} trials -> {a.out}")


def _types():
    lists = {f for f in FULL_FIELDS if f.endswith(("_names", "_types", "_measures", "_frames"))}
    yield "nct_id", "VARCHAR"
    for f in FULL_FIELDS:
        yield f, "VARCHAR[]" if f in lists else ("BOOLEAN" if f == "eligibility_healthy_volunteers" else "VARCHAR")


if __name__ == "__main__":
    main()
