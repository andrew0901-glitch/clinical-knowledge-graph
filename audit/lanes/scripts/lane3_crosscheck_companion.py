"""Independent check of lane 3: run the companion repo's examples/evidence_map.py (its own DuckDB pass
over the same 107 manifest files, separate SQL) and compare every summary field with lane3_evidence_maps.json.

python lane3_crosscheck_companion.py     (runs this repository's examples/evidence_map.py)
"""
import argparse, subprocess, sys

from lane_common import *

FIELDS = ['articles', 'primary_studies', 'primary_cited_by_review', 'primary_not_cited_by_review',
          'rct_cited_by_review', 'other_trial_cited_by_review', 'distinct_citing_reviews',
          'distinct_citing_reviews_in_map', 'sr_or_ma_2022_2026', 'guideline_2022_2026',
          'guideline', 'sr_or_ma', 'rct', 'other_trial', 'observational', 'other']
VARIANTS = {'with_stubs_any': ([], 'any', 'with_stubs'), 'without_stubs_any': (['--exclude-stubs'], 'any', 'without_stubs'),
            'with_stubs_major': (['--major-only'], 'major', 'with_stubs'),
            'without_stubs_major': (['--exclude-stubs', '--major-only'], 'major', 'without_stubs')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--companion', default=str(REPO), help='repository root holding examples/ (default: this repo)')
    a = ap.parse_args()
    comp = pathlib.Path(a.companion).resolve()
    tool = comp / 'examples/evidence_map.py'
    view, cache, out = CACHE / 'release_v021_view', CACHE / 'em_cache', CACHE / 'em_out'
    assert (view / 'manifest.json').exists(), 'run lane1_trial_landscape.py first (builds the manifest-only view)'
    lane3 = json.loads((R / 'lane3_evidence_maps.json').read_text())
    first, comparisons, mismatches = True, [], 0
    for d in ['D001943', 'D000544', 'D006333']:
        for name, (flags, indexing, population) in VARIANTS.items():
            cmd = [sys.executable, str(tool), '--input', str(view), '--cache', str(cache), '--condition', d,
                   '--out', str(out / f'{d}_{name}')] + flags + (['--rebuild-cache'] if first else [])
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
            first = False
            s = json.loads((out / f'{d}_{name}' / 'summary.json').read_text())
            flat = dict(s, **s['by_design'])
            row = next(r for r in lane3[f'{d}_map'] if r['indexing'] == indexing and r['population'] == population)
            diffs = {k: dict(companion=flat[k], lane3=row[k]) for k in FIELDS if flat[k] != row[k]}
            mismatches += len(diffs)
            comparisons.append(dict(condition=d, variant=name, fields=len(FIELDS), differences=diffs))
    dump(R / 'lane3_crosscheck_companion.json', dict(
        tool=str(tool.relative_to(comp)), tool_sha256=sha(tool),
        tool_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=comp).strip(),
        cache_meta=json.loads((cache / 'meta.json').read_text()), comparisons=comparisons,
        total_field_comparisons=sum(c['fields'] for c in comparisons), mismatches=mismatches,
        passed=mismatches == 0, code_commit=commit()))
    print('mismatches', mismatches)
    sys.exit(0 if mismatches == 0 else 1)


if __name__ == '__main__':
    main()
