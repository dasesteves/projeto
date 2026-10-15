"""Independent Python verification: no imports from the R implementation."""
import csv,json,math,hashlib,sys
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
if sys.flags.optimize:raise SystemExit('Verification requires Python without -O/PYTHONOPTIMIZE')
if len(sys.argv)!=3:raise SystemExit('Usage: verify.py <metadata.csv> <figures-tables>')
source=Path(sys.argv[1]);out=Path(sys.argv[2])
counts=Counter();seen=set();n=0
with (source).open(newline='',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        assert r['cell'] not in seen;seen.add(r['cell']);n+=1
        t=None if r['timepoint']=='NA' else float(r['timepoint'])
        o=None if r['Oligo']=='NA' else r['Oligo']
        counts[t,o]+=1
def rows(name):
    with (out/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
observed={(None if r['timepoint']=='NA' else float(r['timepoint']),None if r['Oligo']=='NA' else r['Oligo']):int(r['cells']) for r in rows('groups-before-filters.csv')}
assert observed==counts
hist=defaultdict(list);full=defaultdict(list)
for (t,o),c in counts.items():
    if t is not None and o is not None:
        full[t].append(math.log10(c))
        if 1.5<=math.log10(c)<=4.5:hist[t].append(math.log10(c))
stats=rows('box-statistics-log10.csv')
assert len(stats)==len(hist)+len(full)==36
for r in stats:
    values=np.array((hist if r['mode']=='historical' else full)[float(r['timepoint'])])
    q1,med,q3=np.quantile(values,[.25,.5,.75],method='linear');iqr=q3-q1
    inside=values[(values>=q1-1.5*iqr)&(values<=q3+1.5*iqr)]
    expected=[min(q1,inside.min()),q1,med,q3,max(q3,inside.max())]
    for name,want in zip(('ymin','lower','middle','upper','ymax'),expected):assert abs(float(r[name])-want)<1e-12,(r,name,want)
    outside=sorted(values[(values<q1-1.5*iqr)|(values>q3+1.5*iqr)])
    got=sorted(float(v) for v in r['outliers_log10'].split(';') if v)
    assert int(r['outlier_count'])==len(outside)==len(got)
    assert np.allclose(got,outside,rtol=0,atol=1e-12)
receipt=json.loads((out/'receipt.json').read_text())
with (source).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==receipt['input_sha256']
for name,digest in receipt['output_sha256'].items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==digest
eligible={(t,o):c for (t,o),c in counts.items() if t is not None and o is not None and 1.5<=math.log10(c)<=4.5}
assert sum(eligible.values())==1155584 and len(eligible)==1205
for name,expected in [('groups-used-historical.csv',eligible),('excluded-groups.csv',{k:v for k,v in counts.items() if k not in eligible})]:
    got={(None if r['timepoint']=='NA' else float(r['timepoint']),None if r['Oligo']=='NA' else r['Oligo']):int(r['cells']) for r in rows(name)}
    assert got==expected
for r in rows('filter-summary-by-time.csv'):
    t=None if r['timepoint']=='NA' else float(r['timepoint']);subset={k:v for k,v in counts.items() if k[0]==t}
    missing={k:v for k,v in subset.items() if None in k};sc={k:v for k,v in subset.items() if k not in eligible and k not in missing};kept={k:v for k,v in subset.items() if k in eligible}
    for g,c,d in [('groups_before_filter','cells_before_filter',subset),('groups_missing','cells_missing',missing),('groups_scale_excluded','cells_scale_excluded',sc),('groups_historical','cells_historical',kept)]:assert int(r[g])==len(d) and int(r[c])==sum(d.values())
report={'status':'passed','rows_checked':n,'groups_checked':len(counts),'boxes_checked':len(stats),'statistic_tolerance_absolute':1e-12,
 'checks':['IDs unique; independently aggregated source matches every group','All group inclusion/exclusion rows and summaries match','All quartiles/whiskers/outliers match NumPy independent calculation','Input and all output hashes match receipt'],
 'Python':sys.version,'NumPy':np.__version__,'limit':'Verifies present metadata/statistics, not historical pixels or biological independence'}
(out/'independent-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
