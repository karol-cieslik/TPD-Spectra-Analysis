"""Run the assembled executable with no source-tree CWD or Python/Tcl overrides."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import shutil


def main():
    package=Path(sys.argv[1]).resolve()
    exe=package/'TPD-Spectra-Studio.exe'
    env=os.environ.copy()
    for key in ('PYTHONPATH','PYTHONHOME','TCL_LIBRARY','TK_LIBRARY'):
        env.pop(key,None)
    with tempfile.TemporaryDirectory(prefix='tpd-beta-package-') as folder:
        output=Path(folder)/'smoke'
        run=subprocess.run([str(exe),'--tpd-smoke-beta',str(output)],cwd=folder,env=env,
            timeout=180,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        print(run.stdout,flush=True)
        run.check_returncode()
        shutil.copy2(output/'beta_smoke.json',package/'validation/beta-package-smoke.json')


if __name__=='__main__':
    main()
