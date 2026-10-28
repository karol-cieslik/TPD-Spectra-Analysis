"""Run the assembled executable with no source-tree CWD or Python/Tcl overrides."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import shutil
from beta_package import verify_resources


def main():
    package=Path(sys.argv[1]).resolve()
    exe=package/'TPD-Spectra-Studio.exe'
    identity = verify_resources(package, os.environ.get('GITHUB_SHA'))
    env=os.environ.copy()
    for key in ('PYTHONPATH','PYTHONHOME','TCL_LIBRARY','TK_LIBRARY'):
        env.pop(key,None)
    with tempfile.TemporaryDirectory(prefix='tpd-beta-package-') as folder:
        output=Path(folder)/'smoke'
        run=subprocess.run([str(exe),'--tpd-smoke-beta',str(output)],cwd=folder,env=env,
            timeout=180,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        print(run.stdout,flush=True)
        run.check_returncode()
        import json
        evidence = json.loads((output/'beta_smoke.json').read_text(encoding='utf-8'))
        assert evidence['identity'] == identity, 'Executable and VERSION.json disagree'
        # Keep development acceptance evidence outside the researcher-facing ZIP.
        destination = Path(__file__).resolve().parents[1] / 'output/beta-package-smoke.json'
        destination.parent.mkdir(exist_ok=True)
        shutil.copy2(output/'beta_smoke.json', destination)
    print('Package manifest, links, checksums and frozen identity passed', flush=True)


if __name__=='__main__':
    main()
