"""Keep first-use and beta-review links locally resolvable."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ('README.md', 'START_HERE.md', 'docs/beta/REVIEW_STATUS.md',
        'docs/beta/RELEASE_NOTES.md', 'docs/beta/TESTER_CHECKLIST.md',
        'docs/beta/FEEDBACK_FORM.md', 'docs/beta/SHARE_WITH_COLLEAGUES.md')
LINK = re.compile(r'(?<!!)\[[^]]+\]\(([^)]+)\)')


def test_local_onboarding_links_exist():
    missing = []
    for item in DOCS:
        file = ROOT / item
        for target in LINK.findall(file.read_text(encoding='utf-8')):
            if target.startswith(('http:', 'https:', 'mailto:', '#')):
                continue
            rel_path = target.split('#', 1)[0]
            if not (file.parent / rel_path).exists():
                missing.append(f'{item} → {target}')
    assert not missing, '\n'.join(missing)


def test_current_docs_share_application_version_and_main_download():
    from tpd_spectra import __version__
    current = ('README.md', 'START_HERE.md', 'docs/beta/RELEASE_NOTES.md',
               'docs/METHOD_STATUS.md', 'docs/USER_AND_SCIENTIFIC_MANUAL.md',
               'docs/redesign/WORKFLOW_USER_GUIDE.md', 'docs/beta/WORKED_EXAMPLES.md',
               'docs/beta/WORKED_EXAMPLES.html')
    for name in current:
        text = (ROOT / name).read_text(encoding='utf-8')
        assert __version__ in text, name
        # Historical version mentions are allowed; actionable obsolete downloads are not.
        for artifact in re.findall(r'tpd-spectra-windows-x64-beta-([0-9.a-z]+)', text):
            assert artifact == __version__, (name, artifact)
        assert 'git checkout ux/' not in text
        assert not re.search(r'(?:Both PRs|PRs #19 and #20|Newer work) (?:remain|remains|are) (?:separate from|in draft|draft)', text)
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'successful **main**' in readme
    assert f'version: {__version__}' in (ROOT / 'CITATION.cff').read_text(encoding='utf-8')
    guide = (ROOT / 'scripts/generate_beta_guide.py').read_text(encoding='utf-8')
    assert __version__ in guide and 'pull/19' not in guide
    assert '20 replicates' in guide
    assert 'VERSION.json' in readme and 'SHA256SUMS.txt' in readme
    status = (ROOT / 'docs/beta/REVIEW_STATUS.md').read_text(encoding='utf-8')
    assert 'PR #21' in status and 'merged' in status
    assert 'visual' in status and 'experimental' in status


def test_colleague_feedback_is_optional_and_privacy_conscious():
    form = (ROOT / 'docs/beta/FEEDBACK_FORM.md').read_text(encoding='utf-8')
    assert 'not' in form.lower() and 'experimental' in form.lower()
    assert 'Nothing is submitted' in form
    assert 'karol.j.cieslik@gmail.com' in form
    assert 'VERSION.json' in form


def test_colleague_handoff_requires_fresh_accepted_windows_build():
    handoff = (ROOT / 'docs/beta/SHARE_WITH_COLLEAGUES.md').read_text(encoding='utf-8')
    assert 'do not contain' in handoff
    assert 'Do not send that old ZIP' in handoff
    assert 'Windows machine without Python' in handoff
    assert 'only after verification' in handoff
    assert 'permission' in handoff.lower()
