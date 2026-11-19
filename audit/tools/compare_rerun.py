"""Compare a rerun's JSON results with the committed ones.

Ignored: volatile fields (seconds, elapsed, code_commit, timestamps, invocation), the order of rows (several
queries have no ORDER BY) and machine paths (replaced by <CLINICAL_KG_DATA> / <CLINICAL_KG_WORK>). Anything else
that differs is reported. Used to write release_audit/results/rerun_verification_v0.2.1.json.

  python compare_rerun.py COMMITTED_DIR RERUN_DIR name.json [name.json ...]
"""
import json, pathlib, re, sys

VOL = re.compile(r'(seconds|elapsed|code_commit|verified_at|checked_at|invocation)$')
PATH = [(re.compile(r'/[^"\s]*?\.release_audit_work'), '<CLINICAL_KG_WORK>'), (re.compile(r'/[^"\s]*?clinical_kg_release_v0\.2\.1'), '<CLINICAL_KG_DATA>')]


def canon(x):
    if isinstance(x, dict):
        return {k: canon(v) for k, v in x.items() if not VOL.search(k)}
    if isinstance(x, list):
        return sorted((canon(i) for i in x), key=lambda i: json.dumps(i, sort_keys=True))
    return x


def load(p):
    t = p.read_text()
    for rx, rep in PATH:
        t = rx.sub(rep, t)
    return canon(json.loads(t))


if __name__ == '__main__':
    committed, rerun = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out = {}
    for name in sys.argv[3:]:
        out[name] = 'identical' if load(committed / name) == load(rerun / name) else 'DIFFERENT'
    print(json.dumps(out, indent=1))
    sys.exit(0 if all(v == 'identical' for v in out.values()) else 1)
