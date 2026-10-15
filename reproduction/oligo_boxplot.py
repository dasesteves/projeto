"""Pinned reference object -> colData -> Oligo boxplots and verified tables. Offline."""
import argparse,hashlib,importlib.metadata,json,os,subprocess,sys
from pathlib import Path
KIT=Path(__file__).resolve().parent
MODULE=KIT/'oligo-boxplot'
SOURCE=json.loads((MODULE/'source.json').read_text())[0]

def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def execute(source,output,rscript,library):
    if output.exists():raise FileExistsError('Output exists; use a new directory')
    if digest(source)!=SOURCE['sha256']:raise ValueError('Reference object hash mismatch')
    if importlib.metadata.version('numpy')!='2.3.4':raise ValueError('Use NumPy 2.3.4; see oligo-boxplot/requirements.txt')
    rscript=rscript.resolve(strict=True);library=library.resolve(strict=True)
    output.mkdir(parents=True,exist_ok=False)
    receipt={'stage':'oligo-boxplot','status':'running','object_sha256':SOURCE['sha256'],'source_url':SOURCE['url']}
    path=output/'receipt.json'
    def save():path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        subprocess.run([sys.executable,str(KIT/'run.py'),'environment','--rscript',str(rscript),'--library',str(library),'--output',str(output/'environment')],check=True)
        env=os.environ.copy();env.update(R_USER=str(output/'environment/user'),TMPDIR=str(output/'environment/temp'))
        if os.name=='nt':env.update(LC_ALL='English_United States.utf8',LANG='English_United States.utf8')
        steps=[
          ('extract',[sys.executable,str(MODULE/'extract_stream.py'),str(source),str(output/'extracted')]),
          ('metadata',[sys.executable,str(MODULE/'export_metadata.py'),str(output/'extracted'),str(output/'metadata.csv')]),
          ('render',[str(rscript),'--vanilla',str(MODULE/'render.R'),str(library),str(output/'metadata.csv'),str(output/'figures-tables')]),
          ('verify',[sys.executable,str(MODULE/'verify.py'),str(output/'metadata.csv'),str(output/'figures-tables')])]
        for stage,cmd in steps:
            receipt['current_step']=stage;save()
            with (output/(stage+'.log')).open('wb') as log:
                subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        receipt.update(status='completed',metadata_sha256=digest(output/'metadata.csv'),
          validation='All cell counts, filters, summaries and 36 boxes independently checked',
          limits=['Not a generic RDS reader; only pinned object accepted','Not historical image equivalence','No metadata imputation','No matrices or UMAP recalculated'])
    except Exception as e:
        receipt.update(status='failed',error=str(e));raise
    finally:save()
    return path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--object',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rscript',type=Path,required=True)
    p.add_argument('--library',type=Path,required=True)
    a=p.parse_args()
    print(execute(a.object.resolve(),a.output.resolve(),a.rscript,a.library))
if __name__=='__main__':main()
