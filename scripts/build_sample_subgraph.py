#!/usr/bin/env python3
"""Build a small, representative sample subgraph from the real v0.1.0 KGX export.

Target: ~250K edges, every relationship type present at least once, loads in
about a minute. Strategy: cap each relationship type at --per-type-cap edges
(default 20,000), scanning edge shards until every type has hit either its
cap or its true total (from manifest.json counts.edges_by_type, so we know
when a rare type is exhausted and can stop looking for more of it). Then
pull every node referenced by a kept edge out of the node shards.

Usage:
    python3 build_sample_subgraph.py --data-dir ../data --out ../sample \
        --manifest ../data/manifest.json --per-type-cap 20000
"""
import argparse
import gzip
import json
import os
import sys
import time


def derive_rel_type(rec):
    orig = rec.get("original_predicate")
    if orig:
        if ":" in orig:
            orig = orig.split(":", 1)[1]
        if "." in orig:
            orig = orig.rsplit(".", 1)[-1]
        return orig.upper()
    pred = rec.get("predicate", "related_to")
    if ":" in pred:
        pred = pred.split(":", 1)[1]
    return pred.upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, help="dir containing edges__*.jsonl.gz / nodes__*.jsonl.gz")
    ap.add_argument("--manifest", required=True, help="path to manifest.json")
    ap.add_argument("--out", required=True, help="output dir for sample shards")
    ap.add_argument("--per-type-cap", type=int, default=20000)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    manifest = json.load(open(args.manifest))
    type_totals = manifest["counts"]["edges_by_type"]
    type_targets = {t: min(args.per_type_cap, n) for t, n in type_totals.items()}
    print("Per-type sample targets:", json.dumps(type_targets, indent=2))

    edge_files = sorted(f for f in os.listdir(args.data_dir)
                         if f.startswith("edges__") and f.endswith(".jsonl.gz"))

    type_counts = {t: 0 for t in type_totals}
    needed_ids = set()
    kept_edges = []

    def all_satisfied():
        return all(type_counts[t] >= type_targets[t] for t in type_targets)

    t0 = time.time()
    scanned = 0
    for ef in edge_files:
        if all_satisfied():
            break
        path = os.path.join(args.data_dir, ef)
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                scanned += 1
                if scanned % 2_000_000 == 0:
                    elapsed = time.time() - t0
                    print(f"  scanned {scanned:,} edges ({elapsed:.0f}s), kept {len(kept_edges):,}, "
                          f"satisfied {sum(1 for t in type_targets if type_counts[t] >= type_targets[t])}/{len(type_targets)} types")
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                rt = derive_rel_type(rec)
                if rt not in type_targets:
                    # unknown type (shouldn't happen -- manifest should be exhaustive)
                    type_targets[rt] = args.per_type_cap
                    type_counts[rt] = 0
                if type_counts[rt] >= type_targets[rt]:
                    continue
                type_counts[rt] += 1
                needed_ids.add(rec["subject"])
                needed_ids.add(rec["object"])
                kept_edges.append(line)
            if all_satisfied():
                break

    print(f"Scanned {scanned:,} edge records in {time.time()-t0:.0f}s; kept {len(kept_edges):,} edges "
          f"across {len(type_counts)} types; need {len(needed_ids):,} distinct node ids.")

    out_edges_path = os.path.join(args.out, "edges__sample.jsonl.gz")
    with gzip.open(out_edges_path, "wt", encoding="utf-8") as f:
        for line in kept_edges:
            f.write(line + "\n")
    print(f"Wrote {out_edges_path} ({os.path.getsize(out_edges_path):,} bytes)")

    # Second pass: pull referenced nodes out of the node shards.
    node_files = sorted(f for f in os.listdir(args.data_dir)
                         if f.startswith("nodes__") and f.endswith(".jsonl.gz"))
    kept_nodes = []
    found_ids = set()
    t1 = time.time()
    for nf in node_files:
        if len(found_ids) >= len(needed_ids):
            break
        path = os.path.join(args.data_dir, nf)
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                # cheap pre-check without full JSON parse
                rec = json.loads(s)
                if rec["id"] in needed_ids and rec["id"] not in found_ids:
                    kept_nodes.append(s)
                    found_ids.add(rec["id"])

    missing = needed_ids - found_ids
    print(f"Found {len(found_ids):,}/{len(needed_ids):,} referenced nodes in {time.time()-t1:.0f}s "
          f"({len(missing):,} missing -- likely in withheld/out-of-scope layers or sidecar-only ids).")

    out_nodes_path = os.path.join(args.out, "nodes__sample.jsonl.gz")
    with gzip.open(out_nodes_path, "wt", encoding="utf-8") as f:
        for line in kept_nodes:
            f.write(line + "\n")
    print(f"Wrote {out_nodes_path} ({os.path.getsize(out_nodes_path):,} bytes)")

    summary = {
        "edges_kept": len(kept_edges),
        "edges_by_type": type_counts,
        "nodes_kept": len(kept_nodes),
        "nodes_missing": len(missing),
    }
    with open(os.path.join(args.out, "sample_build_report.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
