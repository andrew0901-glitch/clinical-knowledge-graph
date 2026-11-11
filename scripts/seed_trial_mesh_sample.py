#!/usr/bin/env python3
"""Add trial -> MeSH condition edges to an existing sample so examples/trial_landscape.py returns rows.

Why this exists: build_sample_subgraph.py caps each relationship type at 20,000 edges, and the HAS_MESH
cap is filled by Article -> MeSHConcept edges, so the sample's ClinicalTrial nodes have no condition
links at all and the trial landscape tool finds 0 trials for any condition.

What it adds, for every sample ClinicalTrial that also has a SPONSORED_BY or CONDUCTED_AT edge in the
sample (so a landscape has sponsors and sites to show):
  * its ClinicalTrial -[:HAS_MESH {study_aspect:'condition', mesh_type:'mesh-list'}]-> MeSHConcept edges
    (the ClinicalTrials.gov condition browse terms; the mesh-ancestor and intervention edges are left
    out to keep the sample small -- the tool does not read them);
  * every HAS_BROADER edge on the path from those descriptors up to their tree roots, so hierarchy
    expansion (query descriptor matched as the OBJECT of HAS_BROADER) reaches them from any ancestor;
  * any MeSHConcept node those edges need that the sample does not already hold.

Every added record is the full original line from the release (nothing reconstructed).

Usage (run AFTER build_sample_subgraph.py and seed_sample_subgraph.py):
    python3 scripts/seed_trial_mesh_sample.py --data-dir ckg --sample-dir sample_out
"""
import argparse
import collections
import glob
import gzip
import json
import os
import time
from multiprocessing import Pool

_W = {}


def _init(trials):
    _W["trials"] = trials


def _scan_edges(path):
    """Return (trial condition mesh-list HAS_MESH lines, all HAS_BROADER lines) from one edge file."""
    has_mesh, broader = [], []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if "HAS_BROADER\"" in line:
                broader.append(line.rstrip("\n"))
            elif "clinicaltrials:" in line and "HAS_MESH" in line and "mesh-list" in line:
                rec = json.loads(line)
                if (rec["subject"] in _W["trials"] and rec.get("study_aspect") == "condition"
                        and rec.get("mesh_type") == "mesh-list"):
                    has_mesh.append(line.rstrip("\n"))
    return has_mesh, broader


def _scan_nodes(args):
    path, want = args
    found = {}
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if "\"MeSHConcept\"" not in line:
                continue
            rec = json.loads(line)
            if rec["id"] in want:
                found[rec["id"]] = line.rstrip("\n")
    return found


def rel_of(rec):
    return (rec.get("original_predicate") or "").rsplit(".", 1)[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, help="dir containing nodes/ and edges/ shards (the real release)")
    ap.add_argument("--sample-dir", required=True, help="existing sample dir (updated in place)")
    ap.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    args = ap.parse_args()
    t0 = time.time()

    edges_path = os.path.join(args.sample_dir, "edges__sample.jsonl.gz")
    nodes_path = os.path.join(args.sample_dir, "nodes__sample.jsonl.gz")
    with gzip.open(edges_path, "rt", encoding="utf-8") as f:
        base_edges = [l.rstrip("\n") for l in f]
    with gzip.open(nodes_path, "rt", encoding="utf-8") as f:
        base_nodes = [l.rstrip("\n") for l in f]
    edge_ids, node_ids, trials, with_context = set(), set(), set(), set()
    for l in base_nodes:
        rec = json.loads(l)
        node_ids.add(rec["id"])
        if (rec.get("lunasai_labels") or [""])[0] == "ClinicalTrial":
            trials.add(rec["id"])
    for l in base_edges:
        rec = json.loads(l)
        edge_ids.add(rec["id"])
        if rel_of(rec) in ("SPONSORED_BY", "CONDUCTED_AT"):
            with_context.add(rec["subject"])
    selected = trials & with_context
    print(f"sample: {len(base_edges):,} edges / {len(base_nodes):,} nodes; {len(trials):,} trials, "
          f"{len(selected):,} with a sponsor or site edge", flush=True)

    edge_files = sorted(glob.glob(os.path.join(args.data_dir, "edges", "*.jsonl.gz")))
    has_mesh, broader = [], []
    with Pool(args.workers, initializer=_init, initargs=(selected,)) as p:
        for hm, br in p.imap_unordered(_scan_edges, edge_files):
            has_mesh += hm
            broader += br
    # HAS_BROADER_ANCESTOR lines also contain the substring; keep the direct edges only.
    broader = [l for l in broader if rel_of(json.loads(l)) == "HAS_BROADER"]

    descriptors = {json.loads(l)["object"] for l in has_mesh}
    up = collections.defaultdict(list)
    for l in broader:
        rec = json.loads(l)
        up[rec["subject"]].append((rec["object"], l))
    chain, seen, stack = [], set(descriptors), list(descriptors)
    while stack:
        for parent, line in up[stack.pop()]:
            chain.append(line)
            if parent not in seen:
                seen.add(parent)
                stack.append(parent)

    added_edges = {}
    for l in has_mesh + chain:
        rec = json.loads(l)
        if rec["id"] not in edge_ids:
            added_edges[rec["id"]] = l
    want_nodes = set()
    for l in added_edges.values():
        rec = json.loads(l)
        want_nodes.update((rec["subject"], rec["object"]))
    want_nodes -= node_ids
    node_files = sorted(glob.glob(os.path.join(args.data_dir, "nodes", "*.jsonl.gz")))
    found_nodes = {}
    with Pool(args.workers) as p:
        for found in p.imap_unordered(_scan_nodes, [(f, want_nodes) for f in node_files]):
            found_nodes.update(found)
    missing = want_nodes - set(found_nodes)
    if missing:
        raise SystemExit(f"{len(missing)} endpoint nodes not found in the release, e.g. {sorted(missing)[:5]}")

    final_edges = base_edges + list(added_edges.values())
    final_nodes = base_nodes + list(found_nodes.values())
    final_ids = node_ids | set(found_nodes)
    dangling = sum(1 for l in final_edges
                   if json.loads(l)["subject"] not in final_ids or json.loads(l)["object"] not in final_ids)
    with gzip.open(edges_path, "wt", encoding="utf-8") as f:
        for l in final_edges:
            f.write(l + "\n")
    with gzip.open(nodes_path, "wt", encoding="utf-8") as f:
        for l in final_nodes:
            f.write(l + "\n")

    report_path = os.path.join(args.sample_dir, "sample_build_report.json")
    report = json.load(open(report_path)) if os.path.exists(report_path) else {}
    report.update({
        "edges_kept": len(final_edges),
        "edges_by_type": dict(collections.Counter(rel_of(json.loads(l)) for l in final_edges)),
        "nodes_kept": len(final_nodes),
        "nodes_missing": dangling,
        "trial_mesh_seed": {
            "trials_seeded": len(selected),
            "trial_condition_has_mesh_edges_added": sum(1 for l in has_mesh if json.loads(l)["id"] in added_edges),
            "has_broader_edges_added": len({json.loads(l)["id"] for l in chain} & set(added_edges)),
            "mesh_nodes_added": len(found_nodes),
        },
    })
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report["trial_mesh_seed"], indent=2))
    print(f"final: {len(final_edges):,} edges / {len(final_nodes):,} nodes; dangling {dangling}; "
          f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
