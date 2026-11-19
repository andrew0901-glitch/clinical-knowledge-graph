"""Build audit/manifests/REPRODUCIBILITY_MANIFEST.public.json: the author's reproducibility manifest for the
release-wide audit, redacted for publication, with the lanes entry (`v023_lanes`) merged in.

Removed (see audit/EXCLUDED.md): entries about the unreleased pre-correction build and the v0.1.0 comparison,
private cache/mirror paths, hashes of excluded files. Every kept file hash is recomputed from the published copy.
Needs the author's private manifest as input, so it is published as a record of the redaction.

  python build_public_manifest.py --research <research/clinical_kg_arxiv_v02> --audit <repo>/audit
"""
import argparse, hashlib, json, pathlib, re

ap = argparse.ArgumentParser()
ap.add_argument('--research', required=True)
ap.add_argument('--audit', required=True)
a = ap.parse_args()
SRC, AUDIT = pathlib.Path(a.research), pathlib.Path(a.audit)
RA = AUDIT / 'release_audit'
m = json.loads((SRC / 'REPRODUCIBILITY_MANIFEST.json').read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree(sub, pat):
    return {str(p.relative_to(RA)): sha(p) for p in sorted((RA / sub).rglob(pat)) if p.is_file()}


DROP = ['cache_inputs', 'comparison_summary', 'copy_receipt', 'input_root', 'precorrection_audit_commit',
        'precorrection_manifest_sha256', 'precorrection_root', 'precorrection_source_manifest_sha256', 'record_comparison',
        'release_data_quality_checks', 'v01_source_doi', 'v01_source_input_manifest_sha256', 'v01_source_inputs',
        'standalone_pdf_sha256', 'v023_lanes', 'artifacts_sha256', 'scripts_sha256', 'reports_sha256', 'audit_code_commit']
out = {k: v for k, v in m.items() if k not in DROP}
out['original_research_code_commit'] = m['audit_code_commit']       # a commit of the author's research repository
out['artifacts_sha256'] = {**tree('results', '*'), **tree('tables', '*.csv'), **tree('figures', '*')}
out['scripts_sha256'] = tree('scripts', '*.py')
out['reports_sha256'] = tree('docs', '*.md')
gone = {k for k in m['verification'] if not (RA / k).exists()}
out['verification'] = {k: v for k, v in m['verification'].items() if k not in gone}
out['query_registries'] = [q for q in m['query_registries'] if (RA / q).exists()]
out['redaction'] = dict(
    note='Redacted copy of the manifest of the release-wide audit (run against release v0.2.0, whose 107 graph files are '
         'byte-identical to v0.2.1). See audit/EXCLUDED.md and audit/release_audit/REDACTION_REGISTER.json.',
    removed_keys=DROP, removed_verification_entries=sorted(gone),
    release_docs_note='artifact/script/report hashes are of the PUBLISHED (redacted/edited) files, not of the originals')
out['v023_lanes'] = json.loads((AUDIT / 'manifests/REPRODUCIBILITY_MANIFEST.lanes.json').read_text())['v023_lanes']
text = json.dumps(out, indent=2, sort_keys=True)
for rx, rep in [(r'/home/[A-Za-z0-9_.-]+/\.cache/lunas-clinical-v02-published-audit/input', '<CLINICAL_KG_DATA>'),
                (r'/home/[A-Za-z0-9_.-]+/\.cache/lunas-clinical-v02-published-audit(/[A-Za-z0-9_./-]*)?', r'<CLINICAL_KG_WORK>\1'),
                (r'/home/[A-Za-z0-9_.-]+/lunas-releases/clinical_v02(_1)?(/manifest\.json)?', '<local release mirror>'),
                (r'research/clinical_kg_arxiv_v02/scripts/', 'audit/release_audit/scripts/')]:
    text = re.sub(rx, rep, text)
assert '/home' + '/' not in text
(AUDIT / 'manifests/REPRODUCIBILITY_MANIFEST.public.json').write_text(text + '\n')
print('written', len(text), 'bytes; verification entries kept', len(out['verification']), 'removed', sorted(gone))
