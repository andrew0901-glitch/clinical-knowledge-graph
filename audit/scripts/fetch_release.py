"""Fetch the Lunas Clinical Evidence KG v0.2.1 graph files and verify them against pinned SHA-256 hashes.

Public sources, no credentials:
  Hugging Face dataset lunas-health/clinical-evidence-kg, tag clinical-v0.2.2 (or clinical-v0.2.1; both tags
  carry the identical manifest.json, sha256 518ed9ae...). Zenodo 10.5281/zenodo.24108692 holds the same 107
  graph files as eight concatenated bundles: verify those with audit/scripts/verify_zenodo_bundles.py.

The 107 node/edge files are checked against audit/release_inputs_v0.2.1.sha256 (pinned in this repository,
independent of the downloaded manifest). Nothing is read or parsed before its hash matches.

  python audit/scripts/fetch_release.py                    # -> $CLINICAL_KG_DATA or ./data/clinical_kg_release_v0.2.1
  python audit/scripts/fetch_release.py --dest /big/disk/clinical_kg --ref clinical-v0.2.1
  python audit/scripts/fetch_release.py --verify-only      # hash what is already on disk, download nothing
"""
import argparse, concurrent.futures, hashlib, os, pathlib, sys, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
PINNED = HERE.parent / 'release_inputs_v0.2.1.sha256'
MANIFEST_SHA256 = '518ed9ae1f2e132aeec9a6d216cbd40d43db01e1ded9ee42901ad635c38aa17c'
HF = 'https://huggingface.co/datasets/lunas-health/clinical-evidence-kg/resolve/{ref}/{path}'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 23), b''):
            h.update(b)
    return h.hexdigest()


def pinned():
    out = {}
    for line in PINNED.read_text().splitlines():
        digest, path = line.split(None, 1)
        out[path.strip()] = digest
    assert len(out) == 107, len(out)
    return out


def download(url, to):
    to.parent.mkdir(parents=True, exist_ok=True)
    part = to.with_name(to.name + '.partial')
    req = urllib.request.Request(url, headers={'User-Agent': 'clinical-evidence-kg-audit'})
    with urllib.request.urlopen(req, timeout=120) as inp, open(part, 'wb') as out:
        while chunk := inp.read(1 << 23):
            out.write(chunk)
    part.replace(to)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dest', default=os.environ.get('CLINICAL_KG_DATA', str(REPO / 'data' / 'clinical_kg_release_v0.2.1')))
    ap.add_argument('--ref', default='clinical-v0.2.2', choices=['clinical-v0.2.2', 'clinical-v0.2.1'])
    ap.add_argument('--verify-only', action='store_true')
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    dest = pathlib.Path(a.dest).resolve()
    want = pinned()

    manifest = dest / 'manifest.json'
    if not a.verify_only and not (manifest.exists() and sha256(manifest) == MANIFEST_SHA256):
        download(HF.format(ref=a.ref, path='manifest.json'), manifest)
    assert manifest.exists() and sha256(manifest) == MANIFEST_SHA256, 'manifest.json is not the pinned v0.2.1 manifest'

    def get(item):
        path, digest = item
        to = dest / path
        status = 'present'
        if not (to.exists() and sha256(to) == digest):
            if a.verify_only:
                return path, 'MISSING_OR_WRONG'
            status = 'downloaded'
            download(HF.format(ref=a.ref, path=urllib.parse.quote(path)), to)
            if sha256(to) != digest:
                to.unlink()
                return path, 'HASH_MISMATCH'
        return path, status

    bad, n = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        for path, status in pool.map(get, sorted(want.items())):
            n += 1
            if status in ('MISSING_OR_WRONG', 'HASH_MISMATCH'):
                bad.append((path, status))
            print(f'[{n}/107] {status:10s} {path}', flush=True)
    if bad:
        print('FAILED:', *bad, sep='\n  ')
        sys.exit(1)
    print(f'OK: 107 graph files in {dest} match the pinned SHA-256 list; manifest sha256 {MANIFEST_SHA256}')
    print(f'Use:  export CLINICAL_KG_DATA={dest}')


if __name__ == '__main__':
    main()
