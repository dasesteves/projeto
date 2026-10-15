import hashlib, importlib.util, io, pathlib, tempfile, unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('download_exact',pathlib.Path(__file__).resolve().parents[1]/'download_exact.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class Response(io.BytesIO):
    def geturl(self): return 'https://example.org/file'
class Downloads(unittest.TestCase):
    def test_verified(self):
        with tempfile.TemporaryDirectory() as d, patch.object(m.urllib.request,'urlopen',return_value=Response(b'abc')):
            r=m.fetch({'file':'x','url':'https://example.org/file','sha256':hashlib.sha256(b'abc').hexdigest()},pathlib.Path(d))
            self.assertEqual(r['status'],'verified'); self.assertEqual((pathlib.Path(d)/'x').read_bytes(),b'abc')
    def test_mismatch_does_not_publish(self):
        with tempfile.TemporaryDirectory() as d, patch.object(m.urllib.request,'urlopen',return_value=Response(b'bad')):
            r=m.fetch({'file':'x','url':'https://example.org/file','sha256':'0'*64},pathlib.Path(d))
            self.assertEqual(r['status'],'failed'); self.assertFalse((pathlib.Path(d)/'x').exists())
    def test_network_failure(self):
        with tempfile.TemporaryDirectory() as d, patch.object(m.urllib.request,'urlopen',side_effect=OSError('unavailable')):
            r=m.fetch({'file':'x','url':'https://example.org/file','sha256':'0'*64},pathlib.Path(d))
            self.assertEqual(r['status'],'failed'); self.assertFalse((pathlib.Path(d)/'x').exists())
if __name__=='__main__': unittest.main()
