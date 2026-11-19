"""Lane 1: rerun the companion repo's examples/trial_landscape.py on the v0.2.1 release files for
D001943, D000544 and D006333, compare with the committed v0.2.1 example summaries, and state which
Article population and self-citation rule the tool uses (with both-population sensitivity numbers).

python lane1_trial_landscape.py            (runs this repository's examples/trial_landscape.py)
The tool is given a folder holding exactly the 107 manifest files (symlinks) plus manifest.json.
"""
import argparse, csv, os, shutil, subprocess, sys

from lane_common import *

CONDITIONS = {'D001943': 'breast_neoplasms_D001943', 'D000544': 'alzheimer_disease_D000544',
              'D006333': 'heart_failure_D006333'}
VOLATILE = {'run_seconds'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--companion', default=str(REPO), help='repository root holding examples/ (default: this repo)')
    a = ap.parse_args()
    comp = pathlib.Path(a.companion).resolve()
    tool = comp / 'examples/trial_landscape.py'
    tool_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=comp).strip()
    view = CACHE / 'release_v021_view'
    shutil.rmtree(view, ignore_errors=True)
    (view / 'nodes').mkdir(parents=True)
    (view / 'edges').mkdir(parents=True)
    shutil.copy(MANIFEST, view / 'manifest.json')
    m = json.loads(MANIFEST.read_text())
    for e in m['nodes'] + m['edges']:
        os.symlink(INPUT / e['path'], view / e['path'])
    out_root, cache = CACHE / 'lane1_out', CACHE / 'tl_cache'
    shutil.rmtree(out_root, ignore_errors=True)
    cmds = [[sys.executable, str(tool), '--input', str(view), '--cache', str(cache), '--rebuild-cache',
             '--data-check', '--out', str(out_root / 'data_check')]]
    cmds += [[sys.executable, str(tool), '--input', str(view), '--cache', str(cache), '--condition', d,
              '--out', str(out_root / d)] for d in CONDITIONS]
    for cmd in cmds:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)

    con = duckdb.connect()
    for t in ('articles', 'result_citers'):
        con.execute(f"CREATE VIEW {t} AS SELECT * FROM '{cache}/{t}.parquet'")
    q = lambda s: con.execute(s).fetchone()[0]
    report = dict(tool=str(tool.relative_to(comp)), tool_commit=tool_commit, tool_sha256=sha(tool),
                  input_view=pub(view), code_commit=commit(),
                  self_link_rows_in_tool_result_citers=q("SELECT count(*) FROM result_citers WHERE citer = cited"),
                  conditions={})
    rows_out = []
    for d, folder in CONDITIONS.items():
        new = json.loads((out_root / d / 'summary.json').read_text())
        old = json.loads((comp / 'examples/trial_landscape_examples' / folder / 'summary.json').read_text())
        diffs = {k: dict(committed=old.get(k), rerun=new.get(k)) for k in sorted(set(old) | set(new))
                 if old.get(k) != new.get(k)}
        csv_cmp = {}
        for f in sorted((comp / 'examples/trial_landscape_examples' / folder).glob('*.csv')):
            a, b = f.read_bytes(), (out_root / d / f.name).read_bytes()
            # rows with equal sort keys can come out in a different order from run to run; same rows = same content
            csv_cmp[f.name] = ('identical' if a == b else 'same_rows_different_order_of_tied_rows'
                               if sorted(a.splitlines()) == sorted(b.splitlines()) else 'differs')
        rp = out_root / d / 'results_publications.csv'
        con.execute(f"CREATE OR REPLACE TABLE rp AS SELECT * FROM read_csv('{rp}')")
        con.execute("CREATE OR REPLACE TABLE ns AS SELECT DISTINCT c.cited FROM result_citers c JOIN articles a "
                    "ON a.id = c.citer WHERE c.citer <> c.cited AND (a.is_guideline OR a.is_systematic_review)")
        j = "JOIN ns ON ns.cited = 'PMID:' || rp.pmid::VARCHAR"
        sens = dict(
            results_article_rows_tool=q("SELECT count(*) FROM rp"),
            results_articles_distinct=q("SELECT count(DISTINCT pmid) FROM rp"),
            results_articles_distinct_without_stubs=q("SELECT count(DISTINCT pmid) FROM rp WHERE NOT article_is_stub"),
            results_article_rows_stub=q("SELECT count(*) FROM rp WHERE article_is_stub"),
            results_articles_distinct_stub=q("SELECT count(DISTINCT pmid) FROM rp WHERE article_is_stub"),
            trials_with_results_article_with_stubs=q("SELECT count(DISTINCT nct_id) FROM rp"),
            trials_with_results_article_without_stubs=q("SELECT count(DISTINCT nct_id) FROM rp WHERE NOT article_is_stub"),
            cited_by_guideline_or_sr_rows_tool=q("SELECT count(*) FROM rp WHERE cited_by_guideline_or_sr > 0"),
            cited_by_guideline_or_sr_rows_nonself=q(f"SELECT count(*) FROM rp {j}"),
            cited_by_guideline_or_sr_distinct_nonself_with_stubs=q(f"SELECT count(DISTINCT pmid) FROM rp {j}"),
            cited_by_guideline_or_sr_distinct_nonself_without_stubs=q(
                f"SELECT count(DISTINCT pmid) FROM rp {j} WHERE NOT article_is_stub"),
        )
        report['conditions'][d] = dict(summary=new, committed_summary_differences=diffs,
                                       substantive_differences={k: v for k, v in diffs.items() if k not in VOLATILE
                                                                and v['committed'] is not None},
                                       fields_absent_from_committed=[k for k, v in diffs.items() if v['committed'] is None],
                                       committed_csv_comparison=csv_cmp, population_sensitivity=sens)
        for k, v in new.items():
            if k in ('condition', 'csv_rows'):
                continue
            rows_out.append([d, k, json.dumps(v), json.dumps(old.get(k)), 'same' if old.get(k) == v else
                             ('absent in committed' if k not in old else 'differs')])
        for k, v in new['csv_rows'].items():
            rows_out.append([d, f'csv_rows.{k}', v, old.get('csv_rows', {}).get(k),
                             'same' if old.get('csv_rows', {}).get(k) == v else 'differs'])
    dc_new = (out_root / 'data_check/data_check.csv').read_bytes()
    dc_old = (comp / 'examples/trial_landscape_examples/data_check.csv').read_bytes()
    report['data_check_identical'] = dc_new == dc_old
    report['tool_rules'] = dict(
        article_population='with_stubs: VALIDATED_BY articles are reported whether or not lunasai_layer is '
                           'ctgov_identity_only (flagged per row as article_is_stub); no stub filter anywhere.',
        results_articles_unit='trial-article VALIDATED_BY rows, not distinct articles',
        self_citation='not excluded: result_citers keeps CITES rows with subject = object',
        citing_types='guideline_or_sr = Guideline / Practice Guideline OR Systematic Review (Meta-Analysis '
                     'reported separately, not in the summary metric); citing articles may be anywhere in the graph',
        hierarchy='tree-number-precise downward explode of HAS_BROADER (descriptors_in_expansion), not the '
                  'descriptor-level closure (descriptor_level_closure, reported for comparison)',
        trial_condition_link="HAS_MESH study_aspect='condition' AND mesh_type='mesh-list'")
    dump(R / 'lane1_trial_landscape.json', report)
    T.mkdir(parents=True, exist_ok=True)
    with open(T / 'lane1_summary_fields.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['condition', 'field', 'rerun', 'committed_v0_2_1', 'status'])
        w.writerows(rows_out)
    for d in CONDITIONS:
        (R / 'lane1_summaries').mkdir(parents=True, exist_ok=True)
        shutil.copy(out_root / d / 'summary.json', R / 'lane1_summaries' / f'{d}_summary.json')
    print(json.dumps({d: v['substantive_differences'] for d, v in report['conditions'].items()}, indent=1))


if __name__ == '__main__':
    main()
