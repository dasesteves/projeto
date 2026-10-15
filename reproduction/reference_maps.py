"""Draw supplied reference coordinates and verify tables independently; no UMAP fit."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

KIT = Path(__file__).resolve().parent
MODULE = KIT / 'reference-maps'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rscript', type=Path, required=True)
    parser.add_argument('--library', type=Path, required=True)
    args = parser.parse_args()
    source = args.input.resolve(strict=True)
    output = args.output.resolve()
    if output.exists(): parser.error('Output already exists; use a new directory')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != '546a8b8a47e6b746e0a652a90a09a29c7b8f64227e3eac259d1ef64daeb0ebf0':
        parser.error('Source hash mismatch')
    for name, expected in [('numpy','2.3.4'),('matplotlib','3.10.7')]:
        try: actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: actual = 'missing'
        if actual != expected: parser.error(f'{name}: expected {expected}, got {actual}; see reference-maps/requirements.txt')
    rscript = args.rscript.resolve(strict=True)
    library = args.library.resolve(strict=True)
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'stage':'reference-maps','status':'running','source_sha256':digest,'UMAP_recalculated':False}
    try:
        subprocess.run([sys.executable,str(KIT/'run.py'),'environment','--rscript',str(rscript),'--library',str(library),'--output',str(output/'environment')],check=True)
        env = os.environ.copy()
        env['R_USER'] = str(output/'environment/user')
        env['TMPDIR'] = str(output/'environment/temp')
        env['MPLCONFIGDIR'] = str(output/'matplotlib-config')
        if os.name == 'nt': env.update(LC_ALL='English_United States.utf8',LANG='English_United States.utf8')
        with (output/'execution.log').open('wb') as log:
            subprocess.run([sys.executable,str(MODULE/'render.py'),'--input',str(source),'--output',str(output/'figures-tables')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        with (output/'verification.log').open('wb') as log:
            subprocess.run([str(rscript),'--vanilla',str(MODULE/'verify.R'),str(library),str(source),str(output/'figures-tables')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        receipt['status'] = 'completed'
    except Exception as error:
        receipt.update(status='failed',error=str(error))
        raise
    finally:
        (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(output/'receipt.json')

if __name__ == '__main__': main()
