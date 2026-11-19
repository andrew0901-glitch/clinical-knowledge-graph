"""Structural checks of the audit/ deposit. No release data needed."""
import csv, json, pathlib, py_compile, re, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parents[1]
AUDIT = REPO / 'audit'

PAPER = {'nodes': 12067108, 'edges': 105758066, 'identity_only_articles': 578177,
         'trials_with_results_without_stubs': 22793,
         'results_articles_cited_by_guideline_or_sr (with stubs)': 23460,
         'results_articles_cited_by_guideline_or_sr (without stubs)': 23460,
         'english_topics': 1017, 'english_topics_both_same_descriptor_full': 743}


def test_pinned_hashes_match_examples_list_and_manifest_claims():
    pinned = (AUDIT / 'release_inputs_v0.2.1.sha256').read_text()
    assert pinned == (REPO / 'examples' / 'release_inputs_v0.2.1.sha256').read_text()
    lines = pinned.splitlines()
    assert len(lines) == 107 and all(re.fullmatch(r'[0-9a-f]{64}  (nodes|edges)/\S+', l) for l in lines)
    readme = (AUDIT / 'README.md').read_text()
    for l in lines:
        assert l in readme            # the README lists every input hash
    assert '518ed9ae1f2e132aeec9a6d216cbd40d43db01e1ded9ee42901ad635c38aa17c' in readme


def test_committed_headline_numbers_equal_the_paper():
    rows = list(csv.DictReader(open(AUDIT / 'lanes/tables/headline_numbers.csv')))
    got = {r['item']: int(r['computed']) for r in rows}
    assert got == PAPER
    assert all(r['match'] == 'True' for r in rows)


def test_readme_maps_every_headline_number():
    readme = (AUDIT / 'README.md').read_text()
    for token in ['12,067,108', '105,758,066', '578,177', '22,793', '23,460', '743 of 1,017']:
        assert token in readme
    for path in re.findall(r'\[`(lanes/[^`]+|release_audit/[^`]+)`\]\(([^)]+)\)', readme):
        assert (AUDIT / path[1]).exists(), path


def test_every_python_file_compiles(tmp_path):
    for f in AUDIT.rglob('*.py'):
        py_compile.compile(str(f), cfile=str(tmp_path / (f.name + 'c')), doraise=True)


def test_markdown_links_resolve():
    bad = []
    for f in AUDIT.rglob('*.md'):
        for m in re.finditer(r'\]\(([^)#\s]+)\)', f.read_text()):
            t = m.group(1)
            if not t.startswith(('http', 'mailto')) and not (f.parent / t).exists():
                bad.append((str(f.relative_to(REPO)), t))
    assert not bad, bad


def test_manifests_are_valid_and_record_all_lanes():
    m = json.loads((AUDIT / 'manifests/REPRODUCIBILITY_MANIFEST.public.json').read_text())
    lanes = m['v023_lanes']
    assert lanes['input']['all_sha256_passed'] and lanes['input']['files_verified'] == 107
    assert {'build', 'lane1_trial_landscape', 'lane2_medlineplus_english', 'lane3_evidence_maps', 'lane3_crosscheck_companion',
            'lane4_osteosarcoma', 'lane5_paper_numbers', 'headline_numbers'} <= set(lanes['lanes'])
    assert lanes['input']['zenodo_bundles_all_match'] is True
    # the manifest hashes are of the published files
    import hashlib
    for rel, digest in list(lanes['lanes']['headline_numbers']['outputs_sha256'].items()):
        assert hashlib.sha256((AUDIT / rel).read_bytes()).hexdigest() == digest, rel
    for rel, digest in m['scripts_sha256'].items():
        assert hashlib.sha256((AUDIT / 'release_audit' / rel).read_bytes()).hexdigest() == digest, rel


def test_safety_scan_is_clean():
    r = subprocess.run([sys.executable, str(AUDIT / 'tools/safety_scan.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]


def test_excluded_material_is_not_present():
    names = {p.name for p in AUDIT.rglob('*') if p.is_file()}
    assert not any(n.startswith('jev_') for n in names)
    assert not (names & {'CHANGES_SINCE_PRECORRECTION.md', 'publish_v023.py', 'copy_receipt.json', 'correction_source_mismatches.json'})
