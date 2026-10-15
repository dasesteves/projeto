import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import oligo_boxplot as entry
import download_exact as download

class IntegrationTests(unittest.TestCase):
    def test_source_is_optional_and_pinned(self):
        default=json.loads((entry.KIT/'data-downloads.json').read_text())
        self.assertNotIn(entry.SOURCE['file'],[r['file'] for r in default])
        self.assertEqual(entry.SOURCE['sha256'],'f84ef19e21c16d2190c2db38782be4d7c89a29b3fd382e59f2f5d7d30669444b')
        self.assertNotIn('unpack',entry.SOURCE)
    def test_bad_hash_stops_before_any_process_or_output(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=p/'bad.gz';src.write_bytes(b'wrong');out=p/'out'
            with patch.object(entry.subprocess,'run') as run:
                with self.assertRaises(ValueError):entry.execute(src,out,p/'Rscript',p/'lib')
                run.assert_not_called();self.assertFalse(out.exists())
    def test_existing_output_not_modified(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);out=p/'out';out.mkdir();(out/'keep').write_text('keep')
            with self.assertRaises(FileExistsError):entry.execute(p/'absent',out,p/'R',p/'lib')
            self.assertEqual((out/'keep').read_text(),'keep')
    def test_downloader_kind_routes_only_object(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'download'
            with patch('sys.argv',['download_exact.py','reference-object','--output',str(out)]),patch.object(download,'fetch',return_value={'status':'verified','file':'GSE202639_reference_cds.RDS.gz'}) as fetch:
                self.assertEqual(download.main(),0)
                self.assertEqual(fetch.call_args.args[0]['sha256'],entry.SOURCE['sha256'])
    def test_verification_failure_cannot_mark_run_completed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=p/'source';src.touch();runtime=p/'Rscript';runtime.touch();lib=p/'lib';lib.mkdir();out=p/'out'
            def fake_run(command,**kwargs):
                if any(str(c).endswith('verify.py') for c in command):
                    raise entry.subprocess.CalledProcessError(1,command)
            with patch.object(entry,'digest',return_value=entry.SOURCE['sha256']),patch.object(entry.importlib.metadata,'version',return_value='2.3.4'),patch.object(entry.subprocess,'run',side_effect=fake_run):
                with self.assertRaises(entry.subprocess.CalledProcessError):entry.execute(src,out,runtime,lib)
            receipt=json.loads((out/'receipt.json').read_text())
            self.assertEqual(receipt['status'],'failed');self.assertEqual(receipt['current_step'],'verify')

if __name__=='__main__':unittest.main()
