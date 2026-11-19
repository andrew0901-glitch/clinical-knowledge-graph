"""Shared constants for the v0.2.1 audit lanes (trial landscape, MedlinePlus English-only,
evidence maps, osteosarcoma hierarchy, final paper numbers).

Inputs: ONLY the 107 node/edge files listed in the v0.2.1 release manifest.json (public release,
Zenodo 10.5281/zenodo.24108692 / Hugging Face tag clinical-v0.2.2). Every file's SHA-256 is
re-verified by build.py before any table is built. Local DuckDB only; no network, no paid calls,
no production access.

One configurable path: CLINICAL_KG_DATA = the release folder (contains manifest.json, nodes/, edges/).
Fetch it with audit/scripts/fetch_release.py. The DuckDB working files are written next to it, in
<CLINICAL_KG_DATA>.audit_work (never inside the release folder).
"""
import hashlib, json, os, pathlib, subprocess

import duckdb

L = pathlib.Path(__file__).resolve().parents[1]          # audit/lanes
AUDIT = L.parent                                         # audit
REPO = AUDIT.parent                                      # repository root
R, T = L / 'results', L / 'tables'
DATA = pathlib.Path(os.environ.get('CLINICAL_KG_DATA', str(REPO / 'data' / 'clinical_kg_release_v0.2.1'))).resolve()
MANIFEST = DATA / 'manifest.json'
INPUT = DATA
CACHE = DATA.parent / (DATA.name + '.audit_work')
DB = CACHE / 'lanes.duckdb'


def pub(x):
    """Render a path for a published record: the machine-specific prefix becomes a placeholder."""
    s = str(x)
    return s.replace(str(CACHE), '<CLINICAL_KG_DATA>.audit_work').replace(str(DATA), '<CLINICAL_KG_DATA>')


# The declared 40-name NLM check-tag list (also in release_audit/tables/analysis_check_tags.csv).
CHECK_TAG_NAMES = [
    'Adolescent', 'Adult', 'Aged', 'Aged, 80 and over', 'Animals', 'Bees', 'Cats', 'Cattle',
    'Chick Embryo', 'Child', 'Child, Preschool', 'Chlorocebus aethiops', 'Cricetinae', 'Dogs',
    'Female', 'Guinea Pigs', 'History of Medicine', 'History, 15th Century', 'History, 16th Century',
    'History, 17th Century', 'History, 18th Century', 'History, 19th Century', 'History, 20th Century',
    'History, 21st Century', 'History, Ancient', 'History, Medieval', 'Horses', 'Humans', 'Infant',
    'Infant, Newborn', 'Male', 'Mice', 'Middle Aged', 'Pregnancy', 'Rabbits', 'Rats', 'Sheep', 'Swine',
    'United States', 'Young Adult']
assert len(CHECK_TAG_NAMES) == 40

STUB_LAYER = 'ctgov_identity_only'
EXPECTED_STUBS = 578177


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def commit():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=L).strip()


def dump(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    # pub(): any machine-specific data/work path that reached a record is written as a placeholder.
    p.write_text(pub(json.dumps(v, indent=2, sort_keys=True, default=str)) + '\n')


def connect(read_only=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    c = duckdb.connect(str(DB), read_only=read_only)
    c.execute("SET threads=8; SET memory_limit='20GB'; SET preserve_insertion_order=false")
    return c


class Registry:
    """Runs and records every query (exact SQL, parameters, denominator note) for one lane."""

    def __init__(self, c, name):
        self.c, self.name, self.results, self.queries = c, name, {}, {}

    def run(self, key, sql, note, params=None, csv=None):
        cur = self.c.execute(sql, params or [])
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        self.results[key] = rows
        self.queries[key] = dict(sql=sql, parameters=params or [], note=note)
        if csv:
            T.mkdir(parents=True, exist_ok=True)
            import csv as _csv
            with open(T / csv, 'w', newline='') as fh:
                w = _csv.writer(fh)
                w.writerow(cols)
                for r in rows:
                    w.writerow([r[c] for c in cols])
        self.save()
        print(key, rows[:2], flush=True)
        return rows

    def save(self):
        dump(R / f'{self.name}.json', self.results)
        dump(R / f'{self.name}_queries.json', self.queries)


def full_expansion_sql(root_param='$1'):
    """Descriptor-level full downward expansion (paper 'full descendants'): the root plus every
    HAS_BROADER_ANCESTOR subject whose object is the root; check tags removed."""
    return (f"SELECT {root_param} AS descriptor, 0 AS depth UNION "
            f"SELECT child, min(depth) FROM hierarchy WHERE type = 'HAS_BROADER_ANCESTOR' AND parent = {root_param} "
            "AND child NOT IN (SELECT id FROM check_tag) GROUP BY child")


def tree_precise_expansion(c, root):
    """PubMed-style explode used by examples/trial_landscape.py: follow HAS_BROADER only where the
    child tree number sits directly under a tree number already reached from the root."""
    from collections import defaultdict
    by_parent, tns = defaultdict(list), defaultdict(set)
    for child, parent, ctn, ptn in c.execute("SELECT child, parent, child_tree_numbers, parent_tree_numbers "
                                             "FROM hierarchy WHERE type = 'HAS_BROADER'").fetchall():
        by_parent[parent].append((child, ctn or []))
        tns[child].update(ctn or [])
        tns[parent].update(ptn or [])
    depth, frontier = {root: 0}, [(root, tn) for tn in sorted(tns[root])]
    while frontier:
        nxt = []
        for node, tn in frontier:
            for child, ctns in by_parent[node]:
                for ctn in ctns:
                    if ctn.rsplit('.', 1)[0] == tn:
                        d = depth[node] + 1
                        if child not in depth or d < depth[child]:
                            depth[child] = d
                        nxt.append((child, ctn))
        frontier = nxt
    checks = {r[0] for r in c.execute("SELECT id FROM check_tag").fetchall()}
    return {k: v for k, v in depth.items() if k not in checks}
