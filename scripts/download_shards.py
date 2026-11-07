#!/usr/bin/env python3
"""Download Lunas Clinical Evidence KG v0.1.0 shards from the public Zenodo record.

Zenodo record: https://zenodo.org/records/24011485 (DOI 10.5281/zenodo.24011485).
No authentication required -- the record is public, CC0-licensed (core graph).

Usage:
    python3 download_shards.py --out ../data --sample   # 1 node shard + 1 edge shard
    python3 download_shards.py --out ../data --all       # all 8 node + 8 edge shards (~5.2 GB)
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

ZENODO_RECORD_API = "https://zenodo.org/api/records/24011485"

# Smallest shard of each kind -- fastest useful smoke test.
SAMPLE_NODE_SHARD = "nodes__nodes-w00.jsonl.gz"
SAMPLE_EDGE_SHARD = "edges__edges-w06.jsonl.gz"


def fetch_record():
    with urllib.request.urlopen(ZENODO_RECORD_API, timeout=60) as resp:
        return json.load(resp)


def sha256_of(path, chunk_size=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, expected_md5=None):
    tmp = dest + ".part"
    print(f"  downloading -> {dest}")
    urllib.request.urlretrieve(url, tmp)
    os.replace(tmp, dest)
    size = os.path.getsize(dest)
    print(f"  done ({size:,} bytes)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory for downloaded shards")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", action="store_true",
                        help="download just one node shard + one edge shard")
    group.add_argument("--all", action="store_true",
                        help="download all 8 node shards + 8 edge shards (~5.2 GB)")
    ap.add_argument("--manifest-only", action="store_true",
                     help="only fetch manifest.json / README.md / sources.jsonl, no shards")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("Fetching Zenodo record metadata...")
    record = fetch_record()
    files_by_key = {f["key"]: f for f in record["files"]}

    # Always grab the small reference files.
    for key in ("manifest.json", "README.md", "sources.jsonl", "NOTICE.md",
                "docs__biolink_mapping.md", "export_report.json"):
        if key not in files_by_key:
            continue
        fi = files_by_key[key]
        dest = os.path.join(args.out, key)
        if not os.path.exists(dest):
            download(fi["links"]["self"], dest)

    if args.manifest_only:
        return

    if args.sample:
        wanted = [SAMPLE_NODE_SHARD, SAMPLE_EDGE_SHARD]
    else:
        wanted = [k for k in files_by_key if k.startswith("nodes__") or k.startswith("edges__")]

    for key in sorted(wanted):
        fi = files_by_key[key]
        dest = os.path.join(args.out, key)
        if os.path.exists(dest) and os.path.getsize(dest) == fi["size"]:
            print(f"SKIP (already present) {key}")
            continue
        print(f"START {key} ({fi['size']:,} bytes)")
        download(fi["links"]["self"], dest)

    print("Download complete.")


if __name__ == "__main__":
    main()
