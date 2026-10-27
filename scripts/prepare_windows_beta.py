"""Record a clean commit and emit Windows version resources before freezing."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tpd_spectra import __version__


def main():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'],
                                    cwd=ROOT, text=True).strip()
    if dirty:
        raise SystemExit('Commit source changes before recording a distributable build identity.\n' + dirty)
    (ROOT / 'tpd_spectra/_build_info.py').write_text(f'COMMIT = {commit!r}\n', encoding='utf-8')
    import re
    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)b(\d+)', __version__)
    if not match:
        raise SystemExit('Expected a numbered beta version for Windows packaging')
    version_tuple = tuple(map(int, match.groups()))
    destination = ROOT / 'output/windows-version.txt'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(f'''VSVersionInfo(
      ffi=FixedFileInfo(filevers={version_tuple}, prodvers={version_tuple}, mask=0x3f,
                       flags=2, OS=0x40004, fileType=1, subtype=0, date=(0,0)),
      kids=[StringFileInfo([StringTable('040904B0', [
        StringStruct('CompanyName', 'Karol Cieslik'),
        StringStruct('FileDescription', 'TPD Spectra Studio research beta'),
        StringStruct('FileVersion', '{__version__}'),
        StringStruct('ProductVersion', '{__version__}'),
        StringStruct('ProductName', 'TPD Spectra Studio'),
        StringStruct('OriginalFilename', 'TPD-Spectra-Studio.exe'),
        StringStruct('Comments', 'Source commit: {commit}')
      ])]), VarFileInfo([VarStruct('Translation', [1033,1200])])])
''', encoding='utf-8')
    print(commit, __version__, destination)


if __name__ == '__main__':
    main()
