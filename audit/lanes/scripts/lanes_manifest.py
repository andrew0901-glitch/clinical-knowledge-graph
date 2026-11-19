"""Record the audit lanes in audit/manifests/REPRODUCIBILITY_MANIFEST.lanes.json under the key `v023_lanes`:
per output its SQL registry, the SHA-256 of every input file, the code commit and the SHA-256 of every output.

python audit/lanes/scripts/lanes_manifest.py        (after all lanes and verify_zenodo_bundles.py have run)
"""
import importlib.metadata, platform, sys

from lane_common import *

LANES = {
    'build': dict(script='scripts/build.py', result='results/build_census.json', queries='results/build_queries.json',
                  outputs=['results/build_census.json', 'results/input_verification.json']),
    'lane1_trial_landscape': dict(script='scripts/lane1_trial_landscape.py', result='results/lane1_trial_landscape.json',
                                  queries=None, outputs=['results/lane1_trial_landscape.json', 'tables/lane1_summary_fields.csv',
                                                         'results/lane1_summaries/*.json']),
    'lane2_medlineplus_english': dict(script='scripts/lane2_medlineplus_english.py', result='results/lane2_medlineplus.json',
                                      queries='results/lane2_medlineplus_queries.json',
                                      outputs=['results/lane2_medlineplus.json', 'tables/lane2_*.csv']),
    'lane3_evidence_maps': dict(script='scripts/lane3_evidence_maps.py', result='results/lane3_evidence_maps.json',
                                queries='results/lane3_evidence_maps_queries.json',
                                outputs=['results/lane3_evidence_maps.json', 'tables/lane3_*.csv']),
    'lane3_crosscheck_companion': dict(script='scripts/lane3_crosscheck_companion.py',
                                       result='results/lane3_crosscheck_companion.json', queries=None,
                                       outputs=['results/lane3_crosscheck_companion.json']),
    'lane4_osteosarcoma': dict(script='scripts/lane4_osteosarcoma.py', result='results/lane4_osteosarcoma.json',
                               queries='results/lane4_osteosarcoma_queries.json',
                               outputs=['results/lane4_osteosarcoma.json', 'tables/lane4_*.csv']),
    'lane5_paper_numbers': dict(script='scripts/lane5_paper_numbers.py', result='results/lane5_paper_numbers.json',
                                queries='results/lane5_paper_numbers_queries.json',
                                outputs=['results/lane5_paper_numbers.json', 'tables/lane5_*.csv']),
    'headline_numbers': dict(script='scripts/headline_numbers.py', result='results/headline_numbers.json',
                             queries='results/headline_numbers_queries.json',
                             outputs=['results/headline_numbers.json', 'tables/headline_*.csv']),
}


def files(patterns):
    out = {}
    for pat in patterns:
        for p in sorted(L.glob(pat)):
            out[str(p.relative_to(AUDIT))] = sha(p)
    return out


def main():
    iv = json.loads((R / 'input_verification.json').read_text())
    assert iv['all_passed'] and iv['files'] == 107
    census = json.loads((R / 'build_census.json').read_text())
    zen = json.loads((R / 'zenodo_bundle_verification.json').read_text())
    entry = dict(
        description='Audit lanes for release v0.2.1: build + census, trial-landscape rerun, MedlinePlus English-only topic '
                    'table, evidence maps, osteosarcoma hierarchy example, final paper numbers, headline numbers. '
                    'Local DuckDB over the 107 release graph files only.',
        input=dict(release_version=iv['version'], snapshot_date=iv['snapshot_date'], manifest=iv['manifest'],
                   manifest_sha256=iv['manifest_sha256'], input_root=iv['input_root'], files_verified=iv['files'],
                   all_sha256_passed=iv['all_passed'],
                   file_sha256={v['path']: v['actual_sha256'] for v in iv['verified']},
                   verification_record='lanes/results/input_verification.json',
                   pinned_hash_list='release_inputs_v0.2.1.sha256',
                   zenodo_bundle_verification='lanes/results/zenodo_bundle_verification.json',
                   zenodo_bundles_all_match=zen['all_match']),
        build=dict(script='lanes/scripts/build.py', sql_registry='lanes/results/build_queries.json',
                   census='lanes/results/build_census.json', code_commit=census['code_commit'],
                   cites_self_links_removed=census['cites_self_links_removed'], stubs=census['stubs'],
                   check_tags_resolved=census['check_tags_resolved'], cache_db=pub(DB)),
        rules=dict(
            populations='with_stubs and without_stubs; stubs = Article lunasai_layer ctgov_identity_only (578,177), '
                        'removed as map Articles and as citers. In v0.2.1 stubs have no pub_types, HAS_MESH or CITES, '
                        'so MeSH-reached Article results are identical in both populations.',
            self_citations='CITES with subject = object removed (24,044 edges).',
            check_tags='40-name NLM check-tag list never used as query, matched or expansion descriptor.',
            full_expansion='descriptor + HAS_BROADER_ANCESTOR descendants (tree-number precise in this release).'),
        lanes={},
        environment=dict(python=sys.version, platform=platform.platform(),
                         packages={k: importlib.metadata.version(k) for k in ['duckdb']},
                         sql_threads=8, sql_memory_limit='20GB'),
        restrictions='No production access, no paid model calls, no rights-reserved annotation-layer files. The only network '
                     'use is downloading the public release files and reading the public Hugging Face / Zenodo record '
                     'metadata (audit/scripts/fetch_release.py, verify_zenodo_bundles.py). No release file was changed.',
        recorded_at_commit=commit())
    for name, spec in LANES.items():
        res = json.loads((L / spec['result']).read_text())
        entry['lanes'][name] = dict(
            script=f"lanes/{spec['script']}", script_sha256=sha(L / spec['script']),
            code_commit=res.get('code_commit') if isinstance(res, dict) else None,
            sql_registry=f"lanes/{spec['queries']}" if spec['queries'] else None,
            outputs_sha256=files(spec['outputs']))
    entry['lanes']['lane1_trial_landscape']['tool'] = {k: json.loads((R / 'lane1_trial_landscape.json').read_text())[k]
                                                      for k in ('tool', 'tool_sha256')}
    x = json.loads((R / 'lane3_crosscheck_companion.json').read_text())
    entry['lanes']['lane3_crosscheck_companion']['tool'] = {k: x[k] for k in ('tool', 'tool_sha256')}
    entry['release_fetch_and_verify'] = {s: sha(AUDIT / 'scripts' / s) for s in ('fetch_release.py', 'verify_zenodo_bundles.py')}
    entry['companion_pr9'] = json.loads((R / 'companion_pr9_merge.json').read_text())
    entry['report_sha256'] = files(['LANES_REPORT.md'])
    entry['scripts_sha256'] = {str(p.relative_to(AUDIT)): sha(p) for p in sorted((L / 'scripts').glob('*.py'))}
    mpath = AUDIT / 'manifests' / 'REPRODUCIBILITY_MANIFEST.lanes.json'
    mpath.parent.mkdir(exist_ok=True)
    mpath.write_text(json.dumps({'v023_lanes': entry}, indent=2, sort_keys=True) + '\n')
    print('recorded', list(entry['lanes']))


if __name__ == '__main__':
    main()
