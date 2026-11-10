#!/usr/bin/env python3
"""Convert the Lunas Clinical Evidence KG (KGX JSONL.gz) into CSV files for Neo4j's bulk importer.

Works on either download layout:
  Hugging Face:  <dir>/nodes/*.jsonl.gz      <dir>/edges/*.jsonl.gz
  Zenodo:        <dir>/nodes__*.jsonl.gz     <dir>/edges__*.jsonl.gz

  python scripts/kgx_to_neo4j.py --input ckg --out neo4j_import
  bash scripts/load_neo4j.sh neo4j_import          # then run the bulk import

  # --exclude-type still works (comma-separated relationship types to skip) but v0.2.0 has
  # nothing comparable to v0.1.0's HAS_RIGHTS_EVIDENCE/HAS_USE_GRANT left to exclude -- that
  # whole rights-bookkeeping layer was dropped entirely, not just made optional.

How the graph maps to Neo4j:
  * Node label     = the native Lunas label (lunasai_labels) if present, else the Biolink category
                     (biolink:Article -> Article). Biolink categories are kept in the `category` property.
  * Relationship   = the native relationship type from `original_predicate`
                     (lunasai:vocab.CITES -> CITES). Many edges use the generic Biolink predicate
                     biolink:related_to, so `predicate` alone would collapse distinct relationships.
                     The Biolink predicate is kept as the `biolink_predicate` property.
  * Properties     = typed columns inferred from a sample of every file. Lists become Neo4j arrays,
                     nested objects become JSON strings. Keys first seen after sampling go into a
                     JSON string property `extra`, so nothing is dropped.

One streaming pass over the data plus a sampling pass; nothing is loaded into memory.
"""
import argparse, collections, csv, glob, gzip, json, os, re, sys, time

try:
    import orjson
    loads = orjson.loads
except ImportError:
    loads = json.loads

ARRAY_DELIM = ";"
csv.field_size_limit(sys.maxsize)


def files(root, kind):
    f = sorted(glob.glob(os.path.join(root, kind, "*.jsonl.gz"))) + \
        sorted(glob.glob(os.path.join(root, f"{kind}__*.jsonl.gz")))
    if not f:
        sys.exit(f"no {kind} files under {root} (expected {kind}/*.jsonl.gz or {kind}__*.jsonl.gz)")
    return f


def safe(name):
    s = re.sub(r"[^A-Za-z0-9_]", "_", str(name)).strip("_")
    return s or "Unknown"


def node_label(r):
    labs = r.get("lunasai_labels")
    if isinstance(labs, list) and labs:
        return [safe(str(x).split(":")[-1].split(".")[-1]) for x in labs]
    if isinstance(labs, str) and labs:
        return [safe(labs.split(":")[-1].split(".")[-1])]
    cat = r.get("category")
    cats = cat if isinstance(cat, list) else [cat] if cat else ["NamedThing"]
    return [safe(str(c).split(":")[-1]) for c in cats]


def rel_type(r):
    p = r.get("original_predicate") or r.get("predicate") or "related_to"
    return safe(str(p).split(":")[-1].split(".")[-1]).upper()


def vtype(v):
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "long"
    if isinstance(v, float):
        return "double"
    if isinstance(v, list):
        return "string[]"
    return "string"


def merge_type(a, b):
    if a is None or a == b:
        return b
    if {a, b} == {"long", "double"}:
        return "double"
    if a.endswith("[]") or b.endswith("[]"):
        return "string[]"
    return "string"


def cell(v, t):
    if v is None:
        return ""
    if t == "string[]":
        items = v if isinstance(v, list) else [v]
        return ARRAY_DELIM.join(
            (json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else str(x)).replace(ARRAY_DELIM, ",")
            for x in items if x is not None)
    if t == "boolean":
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def read(path, limit=None):
    with gzip.open(path, "rb") as fh:
        for i, line in enumerate(fh):
            if limit is not None and i >= limit:
                return
            line = line.strip()
            if line:
                yield loads(line)


RESERVED_NODE = {"id"}
# "biolink_predicate" is reserved too: a handful of edges (e.g. AUTHORED_BY) carry a literal
# biolink_predicate field (a more specific predicate than the generic `predicate`, e.g.
# biolink:has_author vs biolink:related_to). The fixed biolink_predicate:string output column
# below already captures this (preferring the specific value when present), so without this
# reservation the schema sampler would also emit it as a normal property column -- producing a
# second, colliding "biolink_predicate:string" CSV header that neo4j-admin import rejects.
RESERVED_EDGE = {"subject", "object", "id", "original_predicate", "predicate", "biolink_predicate"}


def sample_schema(paths, keyfn, reserved, per_file):
    # IMPORTANT: this must scan each WHOLE file, not just its first `per_file` lines. At full
    # v0.1.0 scale, node records are written in large contiguous blocks by label (e.g. ~1M+
    # Article records before the first ClinicalTrial/Sponsor/TrialSite/MeSHConcept record even
    # appears in a given shard), and several edge types (CONDUCTED_AT, SPONSORED_BY,
    # HAS_BROADER, HAS_BROADER_ANCESTOR, ...; named PARENT_OF/ANCESTOR_OF in v0.1.0) are
    # similarly clustered. A per-file line cap here silently produced
    # id/:LABEL/extra-only CSVs (every real property swept into the `extra` JSON blob) for 10 of
    # 11 node labels and 10 of 16 relationship types (v0.1.0 counts) -- caught only by querying the real,
    # fully-loaded graph (see docs/VALIDATION_RESULTS.md). `per_file` still bounds memory and
    # per-record work: once a label/type has contributed `per_file` samples, further records of
    # that label/type are skipped (not merged into the schema dict), so the schema dicts stay
    # small; only the full scan itself (cheap -- one JSON parse + a counter check per record) is
    # unavoidable, since a rare label/type can appear anywhere in a shard.
    schema = collections.defaultdict(dict)
    counts = collections.Counter()
    for p in paths:
        for r in read(p):
            k = keyfn(r)
            k = k[0] if isinstance(k, list) else k
            if counts[k] >= per_file:
                continue
            counts[k] += 1
            for f, v in r.items():
                if f in reserved or v is None:
                    continue
                schema[k][f] = merge_type(schema[k].get(f), vtype(v))
    return schema


class Writers:
    def __init__(self, out, prefix, header_fn):
        self.out, self.prefix, self.header_fn = out, prefix, header_fn
        self.w, self.fh, self.counts = {}, {}, collections.Counter()

    def get(self, key):
        if key not in self.w:
            fh = open(os.path.join(self.out, f"{self.prefix}_{key}.csv"), "w", newline="", encoding="utf-8")
            w = csv.writer(fh)
            w.writerow(self.header_fn(key))
            self.w[key], self.fh[key] = w, fh
        return self.w[key]

    def close(self):
        for fh in self.fh.values():
            fh.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="download folder (HF or Zenodo layout)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--exclude-type", default="", help="comma-separated relationship types to skip, e.g. CITES_BACKGROUND,HAS_DERIVED_PUBLICATION")
    ap.add_argument("--sample-per-file", type=int, default=20000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    excl = {s.strip().upper() for s in a.exclude_type.split(",") if s.strip()}
    nfiles, efiles = files(a.input, "nodes"), files(a.input, "edges")
    t0 = time.time()

    print("sampling schemas ...", flush=True)
    nschema = sample_schema(nfiles, node_label, RESERVED_NODE, a.sample_per_file)
    eschema = sample_schema(efiles, rel_type, RESERVED_EDGE, a.sample_per_file)
    ncols = {k: sorted(v) for k, v in nschema.items()}
    ecols = {k: sorted(v) for k, v in eschema.items()}

    def nheader(k):
        return ["id:ID", ":LABEL"] + [f"{c}:{nschema[k][c]}" for c in ncols.get(k, [])] + ["extra:string"]

    def eheader(k):
        return [":START_ID", ":END_ID", ":TYPE", "edge_id:string", "biolink_predicate:string"] + \
               [f"{c}:{eschema[k][c]}" for c in ecols.get(k, [])] + ["extra:string"]

    nw = Writers(a.out, "nodes", nheader)
    for p in nfiles:
        for r in read(p):
            labs = node_label(r)
            k = labs[0]
            cols = ncols.get(k, [])
            known = set(cols) | RESERVED_NODE
            extra = {f: v for f, v in r.items() if f not in known and v is not None}
            nw.get(k).writerow([r["id"], ARRAY_DELIM.join(labs)] +
                               [cell(r.get(c), nschema[k][c]) for c in cols] +
                               [json.dumps(extra, ensure_ascii=False) if extra else ""])
            nw.counts[k] += 1
        print(f"  nodes {os.path.basename(p)}  total {sum(nw.counts.values()):,}", flush=True)
    nw.close()

    ew = Writers(a.out, "edges", eheader)
    skipped = collections.Counter()
    for p in efiles:
        for r in read(p):
            k = rel_type(r)
            if k in excl:
                skipped[k] += 1
                continue
            cols = ecols.get(k, [])
            known = set(cols) | RESERVED_EDGE
            extra = {f: v for f, v in r.items() if f not in known and v is not None}
            ew.get(k).writerow([r["subject"], r["object"], k, r.get("id", ""), r.get("biolink_predicate") or r.get("predicate", "")] +
                               [cell(r.get(c), eschema[k][c]) for c in cols] +
                               [json.dumps(extra, ensure_ascii=False) if extra else ""])
            ew.counts[k] += 1
        print(f"  edges {os.path.basename(p)}  total {sum(ew.counts.values()):,}", flush=True)
    ew.close()

    summary = {"nodes_by_label": dict(nw.counts), "edges_by_type": dict(ew.counts),
               "skipped_edge_types": dict(skipped), "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(a.out, "conversion_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary, indent=1))
    print(f"\nnext: bash scripts/load_neo4j.sh {a.out}")


if __name__ == "__main__":
    main()
