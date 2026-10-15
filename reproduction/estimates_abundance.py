"""Render and independently verify the supplied model tables; no downloads."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

KIT = Path(__file__).resolve().parent
MODULE = KIT / 'estimates-abundance'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rscript', type=Path, required=True)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rscript = args.rscript.resolve(strict=True)
    library = args.library.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        parser.error('Output already exists; use a new directory')
    inputs = KIT.parent / 'Scripts' / 'Saunders Rep' / 'data'
    source = json.loads((MODULE/'source.json').read_text(encoding='utf-8'))
    hashes = {}
    for name, expected in source['files'].items():
        hashes[name] = hashlib.sha256((inputs/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        if hashes[name] != expected:
            parser.error('Source hash mismatch: ' + name)
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'stage':'estimates-abundance', 'status':'running',
               'source_revision':source['revision'], 'input_sha256_lf':hashes}
    try:
        # Reuse the established exact-version check before drawing anything.
        subprocess.run([sys.executable, str(KIT/'run.py'), 'environment',
                        '--rscript', str(rscript), '--library', str(library),
                        '--output', str(output/'environment')], check=True)
        env = os.environ.copy()
        env['R_USER'] = str(output/'environment/user')
        env['TMPDIR'] = str(output/'environment/temp')
        if os.name == 'nt':
            env.update(LC_ALL='English_United States.utf8',LANG='English_United States.utf8')
        with (output/'execution.log').open('wb') as log:
            subprocess.run([str(rscript),'--vanilla',str(MODULE/'render.R'),
                            str(library),str(inputs),str(output/'figures-tables')],
                           cwd=output,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        with (output/'verification.log').open('wb') as log:
            subprocess.run([sys.executable,str(MODULE/'verify.py'),
                            '--input-dir',str(inputs),'--output',str(output/'figures-tables')],
                           stdout=log,stderr=subprocess.STDOUT,check=True)
        receipt['status'] = 'completed'
    except Exception as error:
        receipt.update(status='failed',error=str(error))
        raise
    finally:
        (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(output/'receipt.json')

if __name__ == '__main__':
    main()
