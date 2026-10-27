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


def test_readme_distinguishes_unreleased_ui_from_old_windows_artifact():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'PR #19' in text and 'PR #20' in text
    assert 'not in that older executable' in text
    assert 'VERSION.json' in text
    status = (ROOT / 'docs/beta/REVIEW_STATUS.md').read_text(encoding='utf-8')
    assert 'new Windows build' in status
    assert 'scientific' in status.lower()


def test_colleague_feedback_is_optional_and_privacy_conscious():
    form = (ROOT / 'docs/beta/FEEDBACK_FORM.md').read_text(encoding='utf-8')
    assert 'not' in form.lower() and 'experimental' in form.lower()
    assert 'Nothing is submitted' in form
    assert 'karol.j.cieslik@gmail.com' in form
    assert 'VERSION.json' in form


def test_colleague_handoff_requires_fresh_accepted_windows_build():
    handoff = (ROOT / 'docs/beta/SHARE_WITH_COLLEAGUES.md').read_text(encoding='utf-8')
    assert 'does not contain' in handoff
    assert 'Do not send that old ZIP' in handoff
    assert 'Windows machine without Python' in handoff
    assert 'only after verification' in handoff
    assert 'permission' in handoff.lower()
