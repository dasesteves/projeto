"""Explicit offline restore from verified Windows R 4.6 package archives."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import os

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--archives',type=Path,required=True)
p.add_argument('--library',type=Path,required=True)
p.add_argument('--rscript',type=Path,required=True)
a=p.parse_args()
if os.name != 'nt': p.error('Recorded archives target Windows x64 only')
if a.library.exists(): p.error('Choose a new, empty library path that does not exist')
manifest=json.loads((Path(__file__).parent/'windows-packages.json').read_text())
for row in manifest:
    f=a.archives/row['file']
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=row['sha256']:
        p.error('Missing or different archive: '+row['file'])
a.library.mkdir(parents=True)
env=os.environ.copy()
env.update(REPRO_ARCHIVES=str(a.archives.resolve()),REPRO_LIBRARY=str(a.library.resolve()),
           LC_ALL='English_United States.utf8',LANG='English_United States.utf8')
# Only the manifest-listed archives; never install unrelated ZIPs in the directory.
listing=a.library/'archives.txt'
listing.write_text('\n'.join(str((a.archives/r['file']).resolve()) for r in manifest)+'\n',encoding='utf-8')
env['REPRO_ARCHIVE_LIST']=str(listing.resolve())
code='stopifnot(as.character(getRversion())=="4.6.1"); install.packages(readLines(Sys.getenv("REPRO_ARCHIVE_LIST")),repos=NULL,type="win.binary",lib=Sys.getenv("REPRO_LIBRARY"))'
subprocess.run([str(a.rscript.resolve()),'--vanilla','-e',code],env=env,check=True)
print('Restore attempted. Run the environment stage to verify every package version.')
