"""Render supplied reference coordinates, never fit a UMAP. Local outputs only."""
import argparse, csv, hashlib, json, platform
from collections import Counter
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
expected = '546a8b8a47e6b746e0a652a90a09a29c7b8f64227e3eac259d1ef64daeb0ebf0'
digest = hashlib.sha256(args.input.read_bytes()).hexdigest()
if digest != expected: raise ValueError('Unexpected source hash')
args.output.mkdir(parents=True, exist_ok=False)
out = args.output
counts = Counter(); ids = set(); coords = []; times = []
missing = {'','NA'}
with args.input.open(encoding='utf-8',newline='') as f, (out/'reference-coordinates.csv').open('w',encoding='utf-8',newline='') as dest:
    reader=csv.DictReader(f); w=csv.writer(dest)
    w.writerow(['source_row','cell','timepoint','umap3d_1','umap3d_2','umap3d_3','map_eligible'])
    for i,row in enumerate(reader,1):
        if row['cell'] in ids: raise ValueError('Duplicate cell ID')
        ids.add(row['cell'])
        xyz=[float(row[k]) for k in ('umap3d_1','umap3d_2','umap3d_3')]
        if not np.isfinite(xyz).all(): raise ValueError('Non-finite coordinate')
        t=None if row['timepoint'] in missing else int(row['timepoint'])
        counts[t]+=1; times.append(-1 if t is None else t); coords.append(xyz[:2])
        w.writerow([i,row['cell'],'NA' if t is None else t,*[row[k] for k in ('umap3d_1','umap3d_2','umap3d_3')],t is not None])
xy=np.array(coords); ts=np.array(times); eligible=ts!=-1
ordered=sorted(t for t in counts if t is not None)+[None]
with (out/'cells-by-time.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['timepoint','cells','included_in_maps'])
    for t in ordered:w.writerow(['NA' if t is None else t,counts[t],t is not None])
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(11,6)); colors=['#287e8e']*(len(ordered)-1)+['#ba7740']
ax.bar(range(len(ordered)),[counts[t] for t in ordered],color=colors)
ax.set_xticks(range(len(ordered)),[str(t) if t is not None else 'Sem\ntempo' for t in ordered])
ax.set(xlabel='Tempo pós-fertilização (h); categorias',ylabel='Células no CSV',title='Composição temporal dos metadados de referência')
ax.ticklabel_format(axis='y',style='plain');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.text(.08,.025,f'{len(ids):,} células; {counts[None]:,} sem tempo. Contagens de células, não de embriões.\nFonte: GSE202639; inclui todos os rótulos presentes no ficheiro, sem novos filtros biológicos.',fontsize=9)
fig.tight_layout(rect=(0,.10,1,1));fig.savefig(out/'reference-cells-by-time.png',dpi=160);plt.close(fig)
limits=[(float(xy[:,k].min())-.5,float(xy[:,k].max())+.5) for k in (0,1)]
summaries=[]
for t,color in zip((18,24,36,48,72),('#d95030','#d18a24','#ac8b11','#338b69','#28699f')):
    selected=ts==t
    fig,ax=plt.subplots(figsize=(9,8))
    ax.scatter(xy[eligible,0],xy[eligible,1],s=.15,c='#cccccc',linewidths=0,rasterized=True)
    ax.scatter(xy[selected,0],xy[selected,1],s=.2,c=color,linewidths=0,rasterized=True)
    ax.set(xlim=limits[0],ylim=limits[1],xlabel='umap3d_1 fornecido',ylabel='umap3d_2 fornecido',title=f'Referência pré-calculada — realce de {t} h')
    ax.set_title(f'Referência pré-calculada — realce de {t} h', pad=32)
    ax.set_aspect('equal',adjustable='box')
    ax.text(0,1.02,f'Cor: {int(selected.sum()):,} células de {t} h · cinzento: referência com tempo',transform=ax.transAxes,fontsize=9)
    fig.text(.08,.025,f'Vista de 2 dimensões de uma projeção 3D fornecida pelo estudo; UMAP não recalculado.\n{int(eligible.sum()):,} células no fundo; {counts[None]:,} sem tempo excluídas dos mapas.\nMesmos eixos em todos os painéis. Não representa trajetórias nem os UMAPs Seurat por tempo.',fontsize=9)
    fig.tight_layout(rect=(0,.12,1,.97));fig.savefig(out/f'reference-map-{t}h.png',dpi=160);plt.close(fig)
    summaries.append({'timepoint':t,'highlight_cells':int(selected.sum()),'background_cells':int(eligible.sum()),'excluded_missing_time':counts[None]})
with (out/'map-membership-summary.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
report={'status':'completed','source_sha256':digest,'cells':len(ids),'missing_time':counts[None],
        'background_cells':int(eligible.sum()),'maps':summaries,'axis_limits':limits,
        'draw_order':'Source CSV order, full eligible background first, highlighted time second; no sampling or jitter.',
        'runtime':{'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':np.__version__},
        'UMAP_recalculated':False,'CDS_equivalence_proven':False,'publication':False}
(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
