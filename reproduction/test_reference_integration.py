"""Integration guards; downloads substituted to avoid network in unit tests."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import download_exact

KIT = Path(__file__).resolve().parent

class IntegrationTests(unittest.TestCase):
    def test_metadata_selection_does_not_fetch_count_matrix(self):
        seen = []
        def fake_fetch(item, target):
            seen.append(item['file'])
            return {'file': item['file'], 'status': 'verified'}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'download'
            argv = ['download_exact.py', 'data', '--only', 'GSE202639_reference_cell_metadata.csv.gz', '--output', str(out)]
            with patch.object(sys, 'argv', argv), patch.object(download_exact, 'fetch', fake_fetch), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(download_exact.main(), 0)
            self.assertEqual(seen, ['GSE202639_reference_cell_metadata.csv.gz'])
            self.assertEqual(json.loads((out/'download-receipt.json').read_text())['status'], 'verified')

    def test_unknown_selection_creates_no_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'download'
            with patch.object(sys, 'argv', ['download_exact.py','data','--only','missing.csv','--output',str(out)]), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit): download_exact.main()
            self.assertFalse(out.exists())

    def test_unfiltered_download_keeps_all_data(self):
        seen=[]
        def fake_fetch(item,target):
            seen.append(item['file'])
            return {'file':item['file'],'status':'verified'}
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(sys,'argv',['download_exact.py','data','--output',str(Path(tmp)/'new')]), patch.object(download_exact,'fetch',fake_fetch), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(download_exact.main(),0)
        self.assertEqual(set(seen),{'GSE202639_reference_cell_metadata.csv.gz','GSE202639_reference_raw_counts.RDS.gz','zperturb_beta_bin_results_broadtype_clean.csv'})

    def test_partial_download_is_failed_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'new'
            with patch.object(sys,'argv',['download_exact.py','data','--only','GSE202639_reference_cell_metadata.csv.gz','--output',str(out)]), patch.object(download_exact,'fetch',return_value={'file':'metadata','status':'failed','error':'simulated network failure'}), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(download_exact.main(),1)
            self.assertEqual(json.loads((out/'download-receipt.json').read_text())['status'],'failed')

    def test_existing_run_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source.csv';source.write_text('invalid')
            out=root/'run';out.mkdir();sentinel=out/'keep.txt';sentinel.write_text('keep')
            result=subprocess.run([sys.executable,str(KIT/'reference_maps.py'),'--input',str(source),'--output',str(out),'--rscript',sys.executable,'--library',tmp],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Output already exists',result.stderr)
            self.assertEqual(sentinel.read_text(),'keep')
            self.assertEqual(list(out.iterdir()),[sentinel])

    def test_bad_source_rejected_without_creating_run(self):
        self.assertTrue((KIT/'reference_maps.py').is_file(), 'Reference entrypoint missing')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'wrong.csv';source.write_text('not the reference')
            out=root/'run'
            result=subprocess.run([sys.executable,str(KIT/'reference_maps.py'),'--input',str(source),'--output',str(out),'--rscript',sys.executable,'--library',tmp],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Source hash mismatch',result.stderr)
            self.assertFalse(out.exists())

if __name__ == '__main__': unittest.main()
