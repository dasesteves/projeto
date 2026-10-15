"""Explicit per-user Windows R installation; not a registry-free portable extraction."""
import argparse, datetime, json, os, pathlib, platform, subprocess
from download_exact import digest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--installer',type=pathlib.Path,required=True)
    p.add_argument('--output',type=pathlib.Path,required=True)
    a=p.parse_args()
    if os.name!='nt' or platform.machine().lower() not in ('amd64','x86_64'): p.error('Windows x64 required')
    if a.output.exists(): p.error('Destination must not exist')
    expected=json.loads((pathlib.Path(__file__).parent/'r-runtime.json').read_text())[0]
    if not a.installer.is_file() or digest(a.installer)!=expected['sha256']: p.error('Installer missing or SHA-256 mismatch')
    a.output=a.output.resolve(); installer=a.installer.resolve()
    a.output.mkdir(parents=True)
    receipt={'status':'running','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'installer_sha256':expected['sha256'],'installation_scope':'current user; uninstall registration may be updated; not registry-free','runtime':str(a.output/'R-4.6.1')}
    record=a.output/'runtime-receipt.json'
    def save(): record.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    save()
    try:
        env=os.environ.copy(); env.pop('PSModulePath',None); env['REPRO_INSTALLER']=str(installer)
        signature=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',"Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop; $s=Get-AuthenticodeSignature -LiteralPath $env:REPRO_INSTALLER; $s.Status.ToString(); if($s.Status -ne 'Valid'){exit 1}"],env=env,capture_output=True,text=True)
        (a.output/"signature-check.txt").write_text(signature.stdout+signature.stderr,encoding="utf-8")
        signature.check_returncode()
        receipt['authenticode']=signature.stdout.strip(); save()
        args=[str(installer),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER','/SP-','/NOICONS','/TASKS=','/COMPONENTS=main,x64','/DIR='+str(a.output/'R-4.6.1'),'/LOG='+str(a.output/'install.log')]
        subprocess.run(args,check=True)
        for name in ('user','temp'): (a.output/name).mkdir()
        env.update(R_USER=str(a.output/'user'),TMPDIR=str(a.output/'temp'),LC_ALL='English_United States.utf8',LANG='English_United States.utf8',REPRO_EXPECTED_R=str(a.output/'R-4.6.1'))
        for name in ('R_HOME','R_LIBS','R_LIBS_USER','R_LIBS_SITE'): env.pop(name,None)
        code='stopifnot(as.character(getRversion())=="4.6.1", R.version$arch=="x86_64", normalizePath(R.home())==normalizePath(Sys.getenv("REPRO_EXPECTED_R"))); .libPaths(.Library, include.site=FALSE); print(R.version); print(R.home()); print(.libPaths()); stopifnot(identical(sum(1:10),55L)); sessionInfo()'
        check=subprocess.run([str(a.output/'R-4.6.1/bin/Rscript.exe'),'--vanilla','-e',code],env=env,check=True,capture_output=True,text=True)
        (a.output/'runtime-check.txt').write_text(check.stdout+check.stderr,encoding='utf-8')
        receipt['status']='verified'
    except Exception as exc:
        receipt['status']='failed'; receipt['error']=str(exc); save(); raise
    finally:
        receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat(); save()
    print('R 4.6.1 verified at',a.output/'R-4.6.1/bin/Rscript.exe')
if __name__=='__main__': main()
