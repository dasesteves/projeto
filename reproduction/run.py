"""Offline reproduction runner. Never downloads, installs or overwrites a run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT / 'scripts'))
from summarize_estimates import summarize

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['environment', 'aggregate', 'pca', 'umap'])
    parser.add_argument('--input-dir', type=Path)
    parser.add_argument('--pca', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rscript', type=Path)
    parser.add_argument('--library', type=Path)
    args = parser.parse_args()
    inputs = []
    if args.stage in ('aggregate', 'pca'):
        if args.input_dir is None:
            parser.error('--input-dir is required')
        names = (['zperturb_beta_bin_results_broadtype_clean.csv'] if args.stage=='aggregate'
                 else ['reference_cell_metadata.csv', 'reference_raw_counts.RDS'])
        inputs = [(args.input_dir / name).resolve(strict=True) for name in names]
    if args.stage == 'umap':
        if args.pca is None:
            parser.error('--pca is required')
        inputs = [args.pca.resolve(strict=True)]
    if args.stage != 'aggregate':
        if args.rscript is None or args.library is None:
            parser.error('--rscript and --library are required')
        rscript = args.rscript.resolve(strict=True)
        library = args.library.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        parser.error('Output already exists; use a new directory')
    hashes = {str(p): digest(p) for p in inputs}
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'stage':args.stage, 'input_sha256':hashes, 'status':'running'}
    receipt_path = output/'receipt.json'
    receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    try:
        if args.stage == 'aggregate':
            receipt['groups'] = summarize(inputs[0],output/'mean-model-estimates.csv')
        else:
            env = os.environ.copy()
            for directory in ['temp','user']:
                (output/directory).mkdir()
            env.update(REPRO_KIT=str(KIT), REPRO_STAGE=args.stage,
                       REPRO_LIBRARY=str(library), R_USER=str(output/'user'),
                       TMPDIR=str(output/'temp'))
            if os.name == 'nt':
                env.update(LC_ALL='English_United States.utf8', LANG='English_United States.utf8')
            if args.input_dir:
                env['REPRO_INPUT'] = str(args.input_dir.resolve())
            if args.pca:
                env['REPRO_PCA'] = str(args.pca.resolve())
            with (output/'execution.log').open('wb') as log:
                result = subprocess.run([str(rscript),'--vanilla',str(KIT/'scripts/dispatch.R')],
                                        cwd=output,env=env,stdout=log,stderr=subprocess.STDOUT)
            receipt['exit_code'] = result.returncode
            if result.returncode:
                raise RuntimeError('R failed; see execution.log. Partial output is retained.')
        receipt['status'] = 'completed'
    except Exception as error:
        receipt.update(status='failed', error=str(error))
        raise
    finally:
        receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(str(receipt_path))

if __name__ == '__main__':
    main()
