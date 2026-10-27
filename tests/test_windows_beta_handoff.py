"""Regression guards for the updated package and executable identity."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_updated_tutorial_never_directs_download_to_obsolete_build():
    from tpd_spectra import __version__
    for name in ('WORKED_EXAMPLES.md', 'WORKED_EXAMPLES.html'):
        text = (ROOT / 'docs/beta' / name).read_text(encoding='utf-8')
        assert '40366654717' not in text
        assert f'tpd-spectra-windows-x64-beta-{__version__}' in text
        assert 'VERSION.json' in text and 'SHA256SUMS.txt' in text


def test_researcher_manifest_excludes_internal_records_and_resolves_links(tmp_path):
    from scripts.beta_package import FILES, INTERNAL, copy_resources, broken_links
    copy_resources(tmp_path)
    for name in FILES:
        assert (tmp_path / name).is_file()
    for name in INTERNAL:
        assert not (tmp_path / name).exists()
    assert not broken_links(tmp_path)
    # Prove the audit catches both Markdown links and HTML/README image assets.
    (tmp_path / 'docs/METHOD_STATUS.md').unlink()
    (tmp_path / 'tpd_spectra/assets/studio-mark.svg').unlink()
    errors = broken_links(tmp_path)
    assert any('METHOD_STATUS.md' in e for e in errors)
    assert any('studio-mark.svg' in e for e in errors)


def test_package_checksums_cover_documentation_and_reject_tampering(tmp_path):
    from scripts.beta_package import write_checksums, verify_resources, copy_resources
    from tpd_spectra.identity import build_identity
    import json
    import pytest
    copy_resources(tmp_path)
    (tmp_path / 'TPD-Spectra-Studio.exe').write_bytes(b'packaging-test-fixture')
    (tmp_path / 'THIRD-PARTY-LICENSES').mkdir()
    (tmp_path / 'THIRD-PARTY-LICENSES/test-LICENSE').write_text('fixture')
    identity = dict(build_identity(), commit='a' * 40)
    (tmp_path / 'VERSION.json').write_text(json.dumps(identity), encoding='utf-8')
    write_checksums(tmp_path)
    assert verify_resources(tmp_path, 'a' * 40) == identity
    with pytest.raises(AssertionError, match='commit mismatch'):
        verify_resources(tmp_path, 'b' * 40)
    (tmp_path / 'docs/beta/FEEDBACK_FORM.md').write_text('changed after assembly')
    with pytest.raises(AssertionError, match='Checksum mismatch'):
        verify_resources(tmp_path)


def test_main_pr_gets_frozen_build_and_version_metadata():
    workflow = (ROOT / '.github/workflows/desktop-build.yml').read_text(encoding='utf-8')
    assert "branches: [main, 'fix/beta-feedback-14-17']" in workflow
    assert '--version-file output/windows-version.txt' in workflow
    assert 'scripts/prepare_windows_beta.py' in workflow
    assert 'python scripts/beta_package.py release-package' in workflow
    assert 'write_checksums' in workflow
    assert "- 'docs/**'" in workflow


def test_dependency_licenses_preserve_nested_attribution(tmp_path, monkeypatch):
    from scripts import beta_package
    upstream = tmp_path / 'installed'
    names = ('one.dist-info/licenses/LICENSE', 'one.dist-info/licenses/sub/LICENSE')
    for index, name in enumerate(names):
        file = upstream / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f'upstream notice {index}')

    class Distribution:
        metadata = {'Name': 'one'}
        files = [Path(name) for name in names]

        def locate_file(self, path):
            return upstream / path

    monkeypatch.setattr(beta_package, 'distributions', lambda: [Distribution()])
    beta_package.copy_dependency_licenses(tmp_path / 'package')
    for index, name in enumerate(names):
        copied = tmp_path / 'package/THIRD-PARTY-LICENSES/one' / name
        assert copied.read_text() == f'upstream notice {index}'
