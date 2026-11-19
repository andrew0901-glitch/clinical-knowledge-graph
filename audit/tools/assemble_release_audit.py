"""Build audit/release_audit/ (the release-wide structural audit) from the author's research folder.

This is the redaction record for that directory: it states, in code, exactly what was copied unchanged,
what was edited and what was left out, and writes audit/release_audit/REDACTION_REGISTER.json. It needs
the author's private research folder as input, so it cannot be rerun from this repository alone; it is
published so that every exclusion is auditable.

  python assemble_release_audit.py --research <research/clinical_kg_arxiv_v02> --out <repo>/audit/release_audit

Rules (from the deposit brief): keep only material computed from the public release files; leave out anything
that reads the rights-reserved annotation layer (jev_*), production databases or non-public builds, or contains
credentials, internal hostnames or personal machine paths.
"""
import argparse, hashlib, json, pathlib, re, shutil

ap = argparse.ArgumentParser()
ap.add_argument('--research', required=True)
ap.add_argument('--out', required=True)
a = ap.parse_args()
SRC, OUT = pathlib.Path(a.research).resolve(), pathlib.Path(a.out).resolve()
REG = []   # (item, kind, reason)


def reg(item, kind, reason):
    REG.append(dict(item=item, kind=kind, reason=reason))


NONPUB_PRE = 'depends on the pre-correction build (never released); not computable from the public files'
NONPUB_V01 = 'compares with release v0.1.0 / an earlier audit tree; not computed from the 107 v0.2.1 files'
PATHS = 'private machine paths / local-only copy step'

# ---------------------------------------------------------------- scripts
KEEP_SCRIPTS = ['analyze', 'defects', 'extra_checks', 'metadata_unions', 'profile_examples', 'publication_type_sanity',
                'rank', 'rank_verify', 'scan', 'verify_headlines', 'verify_integrity']
EDITED_SCRIPTS = ['common', 'prepare', 'strict_chains', 'topic_sensitivity', 'verify_inputs']
DROP_SCRIPTS = {
    'baseline': NONPUB_V01 + ' (reads the v0.1 cache)', 'compare': NONPUB_PRE, 'record_diff': NONPUB_PRE,
    'reconcile': NONPUB_V01 + ' (reads v0.1 ctgov_publications.jsonl)', 'verify_reconciliation': NONPUB_V01,
    'verify_corrections': NONPUB_PRE, 'source_provenance': NONPUB_PRE + ' (attaches the pre-correction DB)',
    'report': NONPUB_V01 + ' and ' + NONPUB_PRE + ' (renders the v0.1/pre-correction comparison documents)',
    'manifest': 'built from private caches; replaced by audit/manifests/ (rebuilt from the published files)',
    'freeze_copy': PATHS, 'fetch_published': 'replaced by audit/scripts/fetch_release.py (private mirror path)'}
(OUT / 'scripts').mkdir(parents=True, exist_ok=True)
for n in KEEP_SCRIPTS:
    shutil.copy(SRC / 'scripts' / f'{n}.py', OUT / 'scripts' / f'{n}.py')
for n, why in DROP_SCRIPTS.items():
    reg(f'scripts/{n}.py', 'excluded script', why)


def edit(path, pairs):
    p = OUT / path
    s = p.read_text()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:70], s.count(old))
        s = s.replace(old, new)
    p.write_text(s)


# common.py -- rewritten: one data path
(OUT / 'scripts/common.py').write_text('''"""Release audit constants and exact SQL registry. Public release files only.

One configurable path: CLINICAL_KG_DATA = the release folder (manifest.json, nodes/, edges/), fetched with
audit/scripts/fetch_release.py. Large working files (projections, DuckDB, sort files) go to
<CLINICAL_KG_DATA>.release_audit_work -- budget roughly 150 GB.
"""
import os,pathlib,json,duckdb,subprocess
P=pathlib.Path(__file__).resolve().parents[1];R=P/'results';T=P/'tables';F=P/'figures'
DATA=pathlib.Path(os.environ.get('CLINICAL_KG_DATA',str(P.parents[1]/'data'/'clinical_kg_release_v0.2.1'))).resolve()
C=DATA.parent/(DATA.name+'.release_audit_work');C.mkdir(parents=True,exist_ok=True)
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\\n')
def connect(read_only=False):
 c=duckdb.connect(str(C/'analysis.duckdb'),read_only=read_only);c.execute("SET threads=4;SET memory_limit='16GB';SET preserve_insertion_order=false");return c
class Registry:
 def __init__(self,c,name):self.c=c;self.name=name;self.results={};self.queries={}
 def run(self,name,sql,denominator,params=None):
  cur=self.c.execute(sql,params or []);rows=[dict(zip([d[0] for d in cur.description],r)) for r in cur.fetchall()];self.results[name]=rows;self.queries[name]=dict(sql=sql,parameters=params or [],denominator=denominator);self.save();print(name,rows[:1],flush=True);return rows
 def save(self):dump(R/(self.name+'.json'),self.results);dump(R/(self.name+'_queries.json'),self.queries)
''')
reg('scripts/common.py', 'edited script', 'private cache/prior-audit paths replaced by the single CLINICAL_KG_DATA path; pre-correction and v0.1 constants removed')

# verify_inputs.py -- graph files only, public data layout
(OUT / 'scripts/verify_inputs.py').write_text('''"""Fail-closed SHA-256 verification of the manifest-listed graph files BEFORE reading any graph content.
Checks the 107 node/edge files of the release folder (CLINICAL_KG_DATA); sources.jsonl and metadata files are
checked only if present. python verify_inputs.py [--input DIR]"""
import argparse,concurrent.futures,hashlib,json,os,pathlib,subprocess,sys,datetime
P=pathlib.Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=pathlib.Path,default=pathlib.Path(os.environ.get('CLINICAL_KG_DATA',str(P.parents[1]/'data'/'clinical_kg_release_v0.2.1'))));a=ap.parse_args();root=a.input.resolve();raw=(root/'manifest.json').read_bytes();m=json.loads(raw);jobs=[]
 for family in ['nodes','edges']:
  for entry in m[family]:jobs.append(dict(entry,family=family))
 optional=[dict(m['sources'],family='sources')]+[dict(path=path,sha256=value,family='metadata') for path,value in m['metadata'].items()]
 jobs+=[j for j in optional if (root/j['path']).exists()]
 def check(r):
  p=(root/r['path']).resolve();assert p.is_relative_to(root),r['path'];h=hashlib.sha256()
  with p.open('rb') as inp:
   while b:=inp.read(8*1024*1024):h.update(b)
  actual=h.hexdigest();return dict(r,actual_sha256=actual,actual_bytes=p.stat().st_size,passed=actual==r['sha256'] and ('bytes' not in r or r['bytes']==p.stat().st_size))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:verified=list(pool.map(check,jobs))
 result=dict(input_root='<CLINICAL_KG_DATA>',manifest_sha256=hashlib.sha256(raw).hexdigest(),verified=verified,passed=all(r['passed'] for r in verified) and sum(r['family'] in ('nodes','edges') for r in verified)==107,manifest_claims=dict(version=m.get('version'),scope=m.get('scope'),totals=m.get('totals'),exporter_git_commit=m.get('exporter_git_commit')),code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=P).strip(),verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),optional_files_not_present=[j['path'] for j in optional if not (root/j['path']).exists()])
 (P/'results/input_verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\\n');assert result['passed'],[r for r in verified if not r['passed']]
 (P/'results/source_manifest.json').write_bytes(raw);print('VERIFIED',len(verified),'manifest-listed files;',result['manifest_sha256'])
if __name__=='__main__':main()
''')
reg('scripts/verify_inputs.py', 'edited script', 'rewritten for the public data layout (graph files; optional files only if present); no private paths; no check against a v0.2.0-only receipt')

shutil.copy(SRC / 'scripts/prepare.py', OUT / 'scripts/prepare.py')
shutil.copy(SRC / 'scripts/strict_chains.py', OUT / 'scripts/strict_chains.py')
shutil.copy(SRC / 'scripts/topic_sensitivity.py', OUT / 'scripts/topic_sensitivity.py')

# seed_data.py: the check-tag stoplist and the six purposive seeds (public node ids), formerly read from the v0.1 audit tree
sys_path = SRC.parent / 'clinical_kg_arxiv_v01' / 'scripts'
txt = (sys_path / 'addendum_common.py').read_text()
m = re.search(r'STOP_NAMES\s*=\s*(\[.*?\])', txt, re.S)
stop = eval(m.group(1))
seeds = json.loads((SRC.parent / 'clinical_kg_arxiv_v01/traversals_addendum/results/ranking_down.json').read_text())['seeds']
assert len(stop) == 40 and len(seeds) == 6
(OUT / 'scripts/seed_data.py').write_text('"""Constants formerly read from the earlier audit tree: the 40-name NLM check-tag stoplist and the six purposive\nranking seeds (node ids, areas, terms). All ids are nodes of the public release."""\nSTOP_NAMES=' + repr(stop) + '\nSEEDS=' + json.dumps(seeds, indent=1) + '\n')
reg('scripts/seed_data.py', 'new file', 'constants (40 check tags, 6 seed node ids) vendored from the earlier audit tree so prepare.py needs nothing outside the release')

edit('scripts/prepare.py', [
    ("sys.path.insert(0,str(OLD/'scripts'));from addendum_common import STOP_NAMES", "from seed_data import STOP_NAMES,SEEDS"),
    ("oldseeds=json.loads((OLD/'traversals_addendum/results/ranking_down.json').read_text())['seeds'];create(", "oldseeds=SEEDS;create("),
    ("root=pathlib.Path(json.loads((R/'input_verification.json').read_text())['input_root'])", "root=DATA"),
])
edit('scripts/scan.py', [("root=pathlib.Path(verify['input_root']);", "root=DATA;")])
edit('scripts/extra_checks.py', [("root=pathlib.Path(json.loads((R/'input_verification.json').read_text())['input_root']);", "root=DATA;")])
reg('scripts/prepare.py', 'edited script', 'input root -> CLINICAL_KG_DATA; check-tag list and seeds read from vendored seed_data.py instead of the earlier audit tree')
reg('scripts/scan.py, scripts/extra_checks.py', 'edited script', 'input root -> CLINICAL_KG_DATA (was a path stored in a result file)')

s = (OUT / 'scripts/strict_chains.py').read_text()
i, j = s.index(" old=duckdb.connect("), s.index(" old.close();") + len(" old.close();")
s = s[:i] + ' ' + s[j:]
s = s.replace(' both releases.', '.').replace('for v0.2 and matching v0.1 non-self controls.', 'for v0.2 (this release).')
assert 'v01' not in s and 'lunas-clinical' not in s
(OUT / 'scripts/strict_chains.py').write_text(s)
reg('scripts/strict_chains.py', 'edited script', 'v0.1 control block removed (needs the v0.1 databases); v0.2 computation and its independent Python re-score unchanged')
s = (OUT / 'scripts/topic_sensitivity.py').read_text()
i, j = s.index(";c=duckdb.connect(str(pathlib.Path.home()"), s.index("run(c,'v01');c.close();") + len("run(c,'v01');c.close();")
s = s[:i] + ';' + s[j:]
s = s.replace(' both releases', '').replace('hierarchy sets and strict/source-ancestor trial descriptor sets, both releases.', 'hierarchy sets and strict/source-ancestor trial descriptor sets.')
assert 'v01' not in s.replace("old=label=='v01'", '') and 'lunas-clinical' not in s, [l for l in s.splitlines() if 'v01' in l]
(OUT / 'scripts/topic_sensitivity.py').write_text(s)
reg('scripts/topic_sensitivity.py', 'edited script', 'v0.1 run removed (needs the v0.1 database); v0.2 run and its independent re-score unchanged')

# ---------------------------------------------------------------- results / tables / figures
EXCL_RESULTS = {
    'comparison_summary.json': NONPUB_PRE, 'record_diff.json': NONPUB_PRE, 'record_changes.json': NONPUB_PRE,
    'copy_receipt.json': PATHS, 'freeze_verification.json': PATHS + ' (frozen local copy check)',
    'correction_verification.json': NONPUB_PRE, 'correction_canonical_mismatches.json': NONPUB_PRE,
    'correction_source_mismatches.json': NONPUB_PRE + ' (the 38 collapsed pairs)', 'table_comparison_notes.json': NONPUB_PRE,
    'reconciliation.json': NONPUB_V01, 'reconciliation_queries.json': NONPUB_V01, 'reconciliation_verification.json': NONPUB_V01,
    'reconciliation_preparation_queries.json': NONPUB_V01 + ' and private paths',
    'strict_chains_v01.json': NONPUB_V01, 'strict_chains_v01_queries.json': NONPUB_V01,
    'topic_sensitivity_v01.json': NONPUB_V01, 'topic_sensitivity_v01_queries.json': NONPUB_V01,
    'v01_controls.json': NONPUB_V01, 'v01_controls_queries.json': NONPUB_V01,
    'source_README.md': 'copy of the v0.2.0 dataset card (already public in the release); omitted, it names the pending licensing decision on the separately governed annotation layer',
    'source_provenance.json': 'mixed: contains the pre-correction half; published half republished as source_provenance_published.json',
    'source_provenance_queries.json': 'mixed: pre-correction half removed; published half republished',
}
(OUT / 'results').mkdir(exist_ok=True)
for f in sorted((SRC / 'results').rglob('*')):
    if not f.is_file():
        continue
    rel = f.relative_to(SRC / 'results')
    if str(rel) in EXCL_RESULTS:
        reg(f'results/{rel}', 'excluded result', EXCL_RESULTS[str(rel)])
        continue
    (OUT / 'results' / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(f, OUT / 'results' / rel)
for k, name in [('', 'source_provenance_published.json'), ('_queries', 'source_provenance_published_queries.json')]:
    d = json.loads((SRC / f'results/source_provenance{k}.json').read_text())
    (OUT / 'results' / name).write_text(json.dumps({'published': d['published']}, indent=2, sort_keys=True) + '\n')
reg('results/source_provenance_published*.json', 'redacted copy', "'precorrection' half removed; 'published' half kept (computed from the release)")
(OUT / 'results/source_provenance_verification.json').unlink(missing_ok=True)
reg('results/source_provenance_verification.json', 'excluded result', 'verification of the mixed pre-correction/published computation')

EXCL_TABLES = re.compile(r'(changes_|record_|comparison|_v01|v01_|reconciliation_|source_provenance_precorrection|metadata_field_comparison|'
                         r'node_family_comparison|relationship_comparison|analytics_states)')
(OUT / 'tables').mkdir(exist_ok=True)
for f in sorted((SRC / 'tables').rglob('*.csv')):
    rel = f.relative_to(SRC / 'tables')
    if EXCL_TABLES.search(f.name):
        reg(f'tables/{rel}', 'excluded table', NONPUB_PRE if 'changes_' in f.name or 'precorrection' in f.name else NONPUB_V01)
        continue
    (OUT / 'tables' / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(f, OUT / 'tables' / rel)

(OUT / 'figures').mkdir(exist_ok=True)
for f in sorted((SRC / 'figures').iterdir()):
    if f.stem in ('trial_connectivity', 'ranking_candidates'):
        reg(f'figures/{f.name}', 'excluded figure', 'plots a v0.1 series next to v0.2')
    else:
        shutil.copy(f, OUT / 'figures' / f.name)

# scrub machine paths from copied JSON
SCRUB = [(re.compile(r'/home/[A-Za-z0-9_.-]+/\.cache/lunas-clinical-v02-published-audit/input'), '<CLINICAL_KG_DATA>'),
         (re.compile(r'/home/[A-Za-z0-9_.-]+/\.cache/lunas-clinical-v02-published-audit(/[A-Za-z0-9_./-]*)?'), r'<CLINICAL_KG_WORK>\1'),
         (re.compile(r'/home/[A-Za-z0-9_.-]+/lunas-releases/clinical_v02_1/manifest\.json'), '<CLINICAL_KG_DATA>/manifest.json'),
         (re.compile(r'research/clinical_kg_arxiv_v02/scripts/'), 'audit/release_audit/scripts/')]
scrubbed = []
for f in sorted(OUT.rglob('*.json')):
    t = f.read_text()
    n = t
    for rx, rep in SCRUB:
        n = rx.sub(rep, n)
    if n != t:
        f.write_text(n)
        scrubbed.append(str(f.relative_to(OUT)))
reg(', '.join(scrubbed), 'scrubbed (paths only)', 'machine-specific data/cache paths replaced by <CLINICAL_KG_DATA> / <CLINICAL_KG_WORK> placeholders; no values changed')

# method strings of two verification records still describe the removed v0.1 controls
for fn, a_, b_ in [('strict_chains_verification.json', ' for v0.2 and matching v0.1 non-self controls.', ' for v0.2.'),
                   ('topic_sensitivity_verification.json', 'trial descriptor sets, both releases.', 'trial descriptor sets.')]:
    f = OUT / 'results' / fn
    t = f.read_text()
    assert t.count(a_) == 1, fn
    f.write_text(t.replace(a_, b_))
reg('results/strict_chains_verification.json, results/topic_sensitivity_verification.json', 'edited result (text only)',
    "'method' sentence no longer mentions the removed v0.1 controls; verdicts unchanged")

# ---------------------------------------------------------------- documents
(OUT / 'docs').mkdir(exist_ok=True)
SCOPE = ('> **Scope.** These documents report the audit of release **v0.2.0** (Zenodo 10.5281/zenodo.24091964, HF tag `clinical-v0.2.0`). '
         'All 107 node/edge files of release v0.2.1 (Zenodo 10.5281/zenodo.24108692) are **byte-identical** (same SHA-256) to the '
         'v0.2.0 files, so every statement about graph content holds for v0.2.1. Statements about the *release metadata files* '
         '(dataset card, citation file, exporter commit) describe v0.2.0. Comparisons with earlier releases and with the '
         'unreleased pre-correction build were removed from this copy; see `../EXCLUDED.md`.\n\n')
HDR = re.compile(r'v0\.1|pre-?correction|prior', re.I)


def drop_columns(lines):
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith('|') and i + 1 < len(lines) and re.match(r'\|[-: |]+\|\s*$', lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].startswith('|'):
                j += 1
            block = [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines[i:j]]
            drop = {k for k, h in enumerate(block[0]) if HDR.search(h)}
            keep = [k for k in range(len(block[0])) if k not in drop]
            if drop and len(keep) <= 1:
                i = j
                continue
            for r, row in enumerate(block):
                if r >= 2 and re.match(r'v0\.1|v01\b|precorrection', row[0], re.I):
                    continue
                if len(row) == len(block[0]):
                    out.append('| ' + ' | '.join(row[k] for k in keep) + ' |')
                else:
                    out.append(lines[i + r])
            i = j
        else:
            out.append(lines[i])
            i += 1
    return out


def cut_section(text, start_heading, until_heading):
    i = text.index(start_heading)
    j = text.index(until_heading, i + 1)
    return text[:i] + text[j:]


def replace_once(t, old, new):
    assert t.count(old) == 1, old[:80]
    return t.replace(old, new)


INTRO3_OLD = re.compile(r' The pre-correction audit at commit `9174478`.*?provides paper-ready headline counts\.', re.S)
INTRO5_OLD = re.compile(r' Counts inherited unchanged from v0\.1 are labeled as that release\'s previously independently audited baseline; matched downward population controls were rerun\. v0\.1 source DOI: \[10\.5281/zenodo\.24011485\]\(https://doi\.org/10\.5281/zenodo\.24011485\)\.')


def common_intro(t):
    t, n = INTRO3_OLD.subn('', t)
    assert n == 1
    t, n = INTRO5_OLD.subn('', t)
    assert n == 1
    return t


def redacted_failures(t):
    # items 1 and 2 and the residual-source-loss paragraph depend on the unreleased pre-correction build
    i = t.index('1. **Prior stub-label defect retested.**')
    j = t.index('3. **Journal identities remain mostly fallback strings.**')
    ph = ('1. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* '
          'Measured on the release itself: 578,177 canonical identity-only Articles; titled stubs 0; stubs with publication types 0. '
          'Existing graph relationships on identity-only nodes do not establish that bibliographic metadata exists.\n'
          '2. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* '
          'Measured on the release itself: extra same NCT-PMID-role edges beyond one per role-pair: 0. Edge-ID uniqueness is separately verified.\n\n')
    return t[:i] + ph + t[j:]


docs = {}
t = (SRC / 'PAPER_HEADLINES.md').read_text()
t = replace_once(t, '# Paper-ready headline numbers — published v0.2.0', '# Paper-ready headline numbers — v0.2.0 audit (graph files identical in v0.2.1)')
k = t.index('Since the pre-correction audit, 5,120 Articles')
t = t[:k].rstrip() + '\n'
docs['PAPER_HEADLINES.md'] = t

t = (SRC / 'DATA_ISSUES.md').read_text()
t = replace_once(t, '# Published v0.2.0 data issues', '# Data issues — v0.2.0 audit (graph files identical in v0.2.1)')
i = t.index('1. **Prior stub-label defect retested.**')
j = t.index('3. **Journal identities remain mostly fallback strings.**')
t = t[:i] + ('1. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* Measured on the release itself: 578,177 canonical identity-only Articles; titled stubs 0; stubs with publication types 0.\n'
             '2. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* Measured on the release itself: extra same NCT-PMID-role edges beyond one per role-pair: 0.\n\n') + t[j:]
t = re.sub(r'\n\nExact failed source-retention witnesses:.*?\n', '\n', t, flags=re.S)
t = replace_once(t, '- Preserve the complete primary/alternate source union when collapsing repeated role-pairs; the 38 measured failures require a new release rather than edits to this snapshot.\n', '')
docs['DATA_ISSUES.md'] = t

t = (SRC / 'METADATA_CHECKS.md').read_text()
t = replace_once(t, '# Metadata checks — frozen v0.2.0 versus v0.1.0', '# Metadata checks — v0.2.0 audit (graph files identical in v0.2.1)')
t = common_intro(t)
t = replace_once(t, 'The v0.1 guideline and broad guideline/review unions were 6,283 and 290,783 of 3,139,339 Articles respectively.\n', '')
t = replace_once(t, 'v0.1 has Article journal strings but no Journal family. v0.2 has 2,734', 'The release has 2,734')
t = replace_once(t, 'The 40-name NLM reference check-tag list from v0.1 is resolved', 'The 40-name NLM reference check-tag list is resolved')
docs['METADATA_CHECKS.md'] = t

t = (SRC / 'TRAVERSALS_ADDENDUM.md').read_text()
t = replace_once(t, '# Resource-paper traversals and ranking — frozen v0.2.0 versus v0.1.0', '# Resource-paper traversals and ranking — v0.2.0 audit (graph files identical in v0.2.1)')
t = common_intro(t)
t = replace_once(t, ' v0.2 removes the v0.1 rights-node/edge layer and adds native publication-role/PMC/journal relations; total-edge changes are not a controlled measure of scientific coverage.', '')
t = replace_once(t, 'Historical v0.1-style self-inclusive results remain', 'Self-inclusive results remain')
t = replace_once(t, 'The v0.1 core represented legacy pairs; its separately released source-assertion sidecar is reconciled below rather than silently treated as an equivalent native graph. ', '')
t = replace_once(t, 'v0.1 had no native BACKGROUND type; the information was sidecar-only. ', '')
t = replace_once(t, 'matches the v0.1 major-preferred non-check seed profile', 'uses a major-preferred non-check seed profile')
t = replace_once(t, 'v0.1 has no Journal nodes and cannot support this native traversal. v0.2:', 'Release v0.2:')
t = replace_once(t, ', v0.1 baseline)', ')')
t = replace_once(t, ' The published IDF corpora are measured separately; their memberships are compared with the pre-correction populations.', '')
t = replace_once(t, ' and `strict_chains_v01_v01.csv`', '')
t = re.sub(r'\*\*precorrection\*\*\n\n\|.*?\n\n(?=\*\*published\*\*)', '', t, flags=re.S)
t = cut_section(t, '## v0.1 → v0.2 trial-publication reconciliation by role', '### Source roles versus protocol publication types')
t = replace_once(t, '### Source roles versus protocol publication types', '## Source roles versus protocol publication types')
t = redacted_failures(t)
docs['TRAVERSALS_ADDENDUM.md'] = t

def relink(t):
    for d in ('results', 'tables', 'figures'):
        t = t.replace(f'](%s/' % d, f'](../%s/' % d)
    t = t.replace('](REPRODUCIBILITY_MANIFEST.json)', '](../../manifests/REPRODUCIBILITY_MANIFEST.public.json)')
    t = re.sub(r'\n- \[Trial-result connectivity, SVG\][^\n]*', '', t)
    t = re.sub(r'\n- \[Ranking candidate comparison, SVG\][^\n]*', '', t)
    return t


for name, t in docs.items():
    lines = drop_columns(t.split('\n'))
    t = relink('\n'.join(lines))
    first = t.index('\n') + 1
    t = t[:first] + '\n' + SCOPE + t[first:].lstrip('\n')
    (OUT / 'docs' / name).write_text(t)
    left = [l[:120] for l in t.split('\n') if re.search(r'v0\.1|v01|pre-?correction|9174478|0c99252|CHANGES_SINCE|/home/', l, re.I)
            and not l.startswith('> **Scope')]
    reg(f'docs/{name}', 'redacted copy', 'v0.1.0-comparison columns/rows/sections, pre-correction passages and the 38-pair source-loss finding removed; scope note added')
    if left:
        print('REVIEW', name, len(left), *left[:12], sep='\n   ')
for n, why in {'CHANGES_SINCE_PRECORRECTION.md': NONPUB_PRE, 'PAPER_HEADLINES.pdf': 'rendered from the comparison script; contains the pre-correction sentences',
               'PUBLICATION_READINESS.md': 'internal readiness assessment for the authors, not requested audit material; cites the pre-correction comparison',
               'SUMMARY.md': 'replaced by audit/README.md', 'RUNBOOK.md': 'replaced by audit/RUNBOOK.md (original has private paths and the pre-correction run)',
               'REPRODUCIBILITY_MANIFEST.json': 'redacted copy rebuilt as audit/manifests/REPRODUCIBILITY_MANIFEST.public.json'}.items():
    reg(n, 'excluded document', why)

(OUT / 'REDACTION_REGISTER.json').write_text(json.dumps(REG, indent=1) + '\n')
print('register entries', len(REG))
