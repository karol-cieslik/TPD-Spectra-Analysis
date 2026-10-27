"""Regression guards for the updated package and executable identity."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_updated_tutorial_never_directs_download_to_obsolete_build():
    for name in ('WORKED_EXAMPLES.md', 'WORKED_EXAMPLES.html'):
        text = (ROOT / 'docs/beta' / name).read_text(encoding='utf-8')
        assert '40366654717' not in text
        assert 'tpd-spectra-windows-x64-beta-0.11.0b5' in text
        assert 'VERSION.json' in text and 'SHA256SUMS.txt' in text


def test_review_documents_shipped_with_their_local_links():
    workflow = (ROOT / '.github/workflows/desktop-build.yml').read_text(encoding='utf-8')
    docs = set(re.findall(r"'(docs/[^']+)'", workflow))
    assert 'docs/beta/SHARE_WITH_COLLEAGUES.md' in docs
    for name in ('REVIEW_STATUS.md', 'SHARE_WITH_COLLEAGUES.md', 'SCIENTIFIC_CONSISTENCY_AUDIT.md'):
        file = ROOT / 'docs/beta' / name
        for target in re.findall(r'\[[^]]+\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
            if target.startswith(('https:', 'http:', '#', 'mailto:')):
                continue
            resolved = (file.parent / target.split('#')[0]).resolve().relative_to(ROOT).as_posix()
            assert resolved in docs, f'Package omits {resolved}, linked from {name}'


def test_stacked_pr_gets_frozen_build_and_version_metadata():
    workflow = (ROOT / '.github/workflows/desktop-build.yml').read_text(encoding='utf-8')
    assert "branches: [main, 'fix/beta-feedback-14-17']" in workflow
    assert '--version-file output/windows-version.txt' in workflow
    assert 'scripts/prepare_windows_beta.py' in workflow
