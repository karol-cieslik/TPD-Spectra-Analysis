"""A raw CRLF Git blob must remain clean on a Windows-style checkout."""
from pathlib import Path
import subprocess


def test_retained_csv_checkout_preserves_blob_bytes(tmp_path):
    root = Path(__file__).resolve().parents[1]
    def git(*args, **kwargs):
        return subprocess.run(['git', '-C', str(tmp_path), *args], check=True,
                              capture_output=True, **kwargs)
    git('init')
    git('config', 'core.autocrlf', 'true')
    (tmp_path / '.gitattributes').write_bytes((root / '.gitattributes').read_bytes())
    for relative in ['validation/experimental/ice_2024/predictions.csv',
                     'validation/experimental/ptcda_au111/inventory.csv',
                     'validation/experimental/ptcda_au111/metadata_inventory.csv']:
        # Store raw bytes directly, matching the retained non-normalized blobs.
        original = b'Temperature,Signal\r\n100,1.25\r\n'
        sha = git('hash-object', '-w', '--stdin', input=original).stdout.decode().strip()
        git('update-index', '--add', '--cacheinfo', '100644', sha, relative)
    git('add', '.gitattributes')
    git('checkout-index', '-f', '-a')
    git('update-index', '--refresh')
    git('diff-files', '--exit-code')
    for relative in ['validation/experimental/ice_2024/predictions.csv',
                     'validation/experimental/ptcda_au111/inventory.csv',
                     'validation/experimental/ptcda_au111/metadata_inventory.csv']:
        assert (tmp_path / relative).read_bytes() == original
