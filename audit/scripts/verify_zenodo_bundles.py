"""Cross-check the Zenodo deposit (10.5281/zenodo.24108692) against the 107 graph files on disk.

Zenodo stores the graph as eight concatenated bundles (nodes-w00..w03, edges-w00..w03). This script fetches
the public record's zenodo_manifest.json (its MD5 is verified against the record API), then reproduces every
bundle's SHA-256 and byte/record count by concatenating the listed source shards in order, and checks that
each listed shard hash equals the pinned hash in audit/release_inputs_v0.2.1.sha256. Run after fetch_release.py.

  python audit/scripts/verify_zenodo_bundles.py [--data DIR]
"""
import argparse, gzip, hashlib, json, os, pathlib, sys, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECORD = 'https://zenodo.org/api/records/24108692'


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'clinical-evidence-kg-audit'})
    with urllib.request.urlopen(req, timeout=120) as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=os.environ.get('CLINICAL_KG_DATA', str(REPO / 'data' / 'clinical_kg_release_v0.2.1')))
    a = ap.parse_args()
    data = pathlib.Path(a.data).resolve()
    pinned = {p.strip(): d for d, p in (l.split(None, 1) for l in (HERE.parent / 'release_inputs_v0.2.1.sha256').read_text().splitlines())}
    record = json.loads(get(RECORD))
    assert record['doi'] == '10.5281/zenodo.24108692', record['doi']
    entry = next(x for x in record['files'] if x['key'] == 'zenodo_manifest.json')
    raw = get(entry['links']['self'])
    algo, want = entry['checksum'].split(':', 1)
    assert hashlib.new(algo, raw).hexdigest() == want, 'zenodo_manifest.json does not match the record checksum'
    z = json.loads(raw)
    seen, report, ok = set(), [], True
    for name, b in z['bundles'].items():
        h, size, records = hashlib.sha256(), 0, 0
        for s in b['source_shards']:
            assert s['path'] not in seen and pinned[s['path']] == s['sha256'], s['path']
            seen.add(s['path'])
            with open(data / s['path'], 'rb') as f:
                while chunk := f.read(1 << 23):
                    h.update(chunk)
                    size += len(chunk)
            records += s['records']
        good = h.hexdigest() == b['sha256'] and size == b['bytes'] and records == b['records']
        ok &= good
        report.append(dict(bundle=name, sha256=h.hexdigest(), bytes=size, records=records, matches_zenodo_manifest=good))
        print(('OK  ' if good else 'FAIL'), name, h.hexdigest()[:16], size, records, flush=True)
    assert seen == set(pinned), 'bundles do not cover exactly the 107 pinned graph files'
    out = HERE.parent / 'lanes' / 'results' / 'zenodo_bundle_verification.json'
    out.write_text(json.dumps(dict(doi=record['doi'], zenodo_manifest_md5=want, bundles=report, shards_covered=len(seen),
                                   all_match=ok), indent=2, sort_keys=True) + '\n')
    print('ALL BUNDLES MATCH' if ok else 'MISMATCH')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
