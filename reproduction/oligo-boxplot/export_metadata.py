"""Export six colData fields from this pinned object's bounded extraction."""
import csv,hashlib,json,sys
from pathlib import Path
from read_vectors import columns,iter_vector

def export(folder,output):
    cols,rownames=columns(folder)
    names=['cell','timepoint','Oligo','embryo','expt','gene_target'];count=0
    with output.open('x',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(names)
        streams=zip(*(iter_vector(cols[n],folder) for n in names),strict=True)
        for row,rid in zip(streams,iter_vector(rownames,folder),strict=True):
            if row[0]!=rid:raise ValueError('colData rownames/cell mismatch')
            vals=[None if v is None or (n=='timepoint' and int(v)==-2147483648) else v for n,v in zip(names,row)]
            w.writerow(['NA' if v is None else v for v in vals]);count+=1
    with output.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    if count!=1241018 or h!='98884c9a9ec2433b5c001cb50ae404ca4849e508d54d59b6037eb105ad3aef53':
        raise ValueError('Export does not match the verified metadata; do not use partial output')
    (output.parent/'metadata-receipt.json').write_text(json.dumps({'status':'verified','rows':count,'sha256':h,'imputed':False},indent=2))

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: export_metadata.py <extracted> <new-metadata.csv>')
    export(Path(sys.argv[1]),Path(sys.argv[2]))
