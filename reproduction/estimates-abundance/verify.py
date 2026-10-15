"""Independent numerical check: Python standard library only; no R objects/cache."""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, math, re, statistics

import argparse
# Assertions are the numerical checks; never certify a run with them disabled.
if not __debug__:
    raise RuntimeError('Verification requires Python without -O / PYTHONOPTIMIZE.')
parser = argparse.ArgumentParser()
parser.add_argument('--input-dir', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
out = args.output.resolve()
inputs = args.input_dir.resolve()
def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
errors = []
def close(a, b):
    a, b = float(a), float(b)
    assert math.isfinite(a) and math.isfinite(b)
    errors.append(abs(a-b))
    assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (a, b)
source = json.loads((root/'source.json').read_text(encoding='utf-8-sig'))
for name, expected in source['files'].items():
    assert hashlib.sha256((inputs/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == expected, name
raw = read(inputs/'zperturb_beta_bin_results_broadtype_clean.csv')
pig = [dict(row, source_row=str(i)) for i, row in enumerate(raw, 1)
       if re.search('phore|pigmented', row['cell_group'], re.I)]
def check_rows(expected, actual):
    assert len(expected) == len(actual)
    for e, a in zip(expected, actual):
        for key, value in e.items():
            if value == a[key]:
                continue
            try:
                close(value, a[key])
            except ValueError:
                raise AssertionError((key, value, a[key]))
check_rows(pig, read(out/'estimate-source-rows.csv'))
groups, genes = defaultdict(list), defaultdict(list)
for row in pig:
    groups[(row['gene1'], float(row['timepoint']))].append(float(row['estimate']))
    genes[row['gene1']].append(row)
times = sorted({t for _, t in groups})
grid = read(out/'estimates-by-time.csv')
assert len(grid) == len(genes)*len(times)
assert {(r['gene1'], float(r['timepoint'])) for r in grid} == {(g,t) for g in genes for t in times}
for row in grid:
    values = groups.get((row['gene1'], float(row['timepoint'])))
    if values:
        close(math.fsum(values)/len(values), row['mean_model_estimate'])
        assert int(row['source_rows']) == len(values) and row['observed'] == 'TRUE'
    else:
        assert row['mean_model_estimate'] == row['source_rows'] == 'NA'
        assert row['observed'] == 'FALSE'
means = {g: math.fsum(float(r['estimate']) for r in rows)/len(rows) for g, rows in genes.items()}
ranking = read(out/'estimates-ranking-all.csv')
assert [r['gene1'] for r in ranking] == sorted(means, key=lambda g: (-means[g],g))
assert read(out/'estimates-ranking-top10.csv') == ranking[:10]
for i, row in enumerate(ranking,1):
    g = row['gene1']
    close(means[g], row['mean_model_estimate'])
    assert int(row['rank']) == i and int(row['source_rows']) == len(genes[g])
    assert int(row['observed_times']) == len({r['timepoint'] for r in genes[g]})
    assert (row['tied_mean'] == 'TRUE') == (sum(m == means[g] for m in means.values()) > 1)
abundance = read(inputs/'ref_broad_celltype_disps.csv')
filtered = [dict(r,source_row=str(i)) for i,r in enumerate(abundance,1) if float(r['cells_per_embryo'])>3]
selected = [r for r in filtered if float(r['timepoint']) in {20,22,24,42}]
check_rows(filtered, read(out/'abundance-all-filtered.csv'))
selected_out = read(out/'abundance-selected-times.csv')
check_rows(selected, selected_out)
audit = read(out/'log-scale-audit.csv')
assert len(audit) == len(selected)
for original, derived, a in zip(selected, selected_out, audit):
    assert a['source_row'] == original['source_row']
    cv, se = float(original['cells_per_embryo_cv']), float(original['cells_per_embryo_cv.stderr'])
    close(cv-se, derived['cv_minus_stderr']); close(cv+se, derived['cv_plus_stderr'])
    assert (derived['p_below_005']=='TRUE') == (float(original['cv_z_stat_p_val']) < .05)
    for flag, columns in {
        'x_valid':['cells_per_embryo'], 'cv_valid':['cells_per_embryo_cv'],
        'fit_valid':['model_fit'], 'fit_bounds_valid':['model_fit_lower','model_fit_upper']
    }.items():
        valid = all(math.isfinite(float(original[c])) and float(original[c])>0 for c in columns)
        assert valid and a[flag] == 'TRUE'
    assert (a['errorbar_valid']=='TRUE') == (cv-se>0 and cv+se>0)
bygroup = defaultdict(list)
for r in filtered:
    bygroup[r['cell_group']].append(float(r['cv_test_stat']))
summary = read(out/'abundance-group-summary.csv')
assert {r['cell_group'] for r in summary} == set(bygroup)
for r in summary:
    values = bygroup[r['cell_group']]
    assert int(r['rows']) == len(values)
    close(statistics.median(values),r['median_cv_test_stat'])
report = {
    'status':'passed', 'source_revision':source['revision'],
    'method':'Independent Python standard-library reconstruction from source CSVs; tolerance 1e-12 absolute/relative',
    'pigment_rows':len(pig),'genes':len(genes),'observed_gene_times':len(groups),
    'missing_gene_times':len(grid)-len(groups),'abundance_rows':len(filtered),
    'selected_time_rows':len(selected),'cell_groups':len(bygroup),
    'numeric_comparisons':len(errors),'max_absolute_difference':max(errors),
    'tied_gene_means':sum(r['tied_mean']=='TRUE' for r in ranking),
    'output_sha256':{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != 'validation.json'},
    'render_sha256':digest(root/'render.R'), 'published':False,
    'limits':'Checks calculations against supplied tables, not validity of the original statistical model or biological conclusions.'
}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('output_sha256','render_sha256')},indent=2))
