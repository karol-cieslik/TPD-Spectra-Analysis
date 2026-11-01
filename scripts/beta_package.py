"""Explicit researcher-facing manifest and portable-document integrity checks."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import shutil
from importlib.metadata import distributions

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'README.md', 'CHANGELOG.md', 'CITATION.cff', 'LICENSE', 'ASSET-RIGHTS.md',
    'START_HERE.md', 'tpd_spectra/assets/studio-mark.svg',
    'docs/USER_AND_SCIENTIFIC_MANUAL.md', 'docs/METHOD_STATUS.md',
    'docs/ZERO_ORDER_FITTING.md', 'docs/MULTICOMPONENT_FITTING.md',
    'docs/EXPLORER_MONTE_CARLO.md', 'docs/SUPPORT_AND_COMPATIBILITY.md',
    'docs/redesign/WORKFLOW_USER_GUIDE.md', 'docs/beta/QUICK_START.pdf',
    'docs/beta/SCIENTIFIC_HELP_TOPICS.json', 'docs/beta/WORKED_EXAMPLES.md',
    'docs/beta/WORKED_EXAMPLES.html', 'docs/beta/RELEASE_NOTES.md',
    'docs/beta/FEEDBACK_FORM.md', 'docs/beta/TESTER_CHECKLIST.md',
)
INTERNAL = (
    'docs/beta/REVIEW_STATUS.md', 'docs/beta/SHARE_WITH_COLLEAGUES.md',
    'docs/beta/SCIENTIFIC_CONSISTENCY_AUDIT.md', 'validation/WINDOWS_B5_ACCEPTANCE.md',
)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for key, value in attrs if key in ('href', 'src') and value)


def broken_links(package):
    """Resolve local Markdown/HTML links and images against the extracted tree."""
    package = Path(package).resolve()
    missing = []
    for file in package.rglob('*'):
        if 'THIRD-PARTY-LICENSES' in file.relative_to(package).parts:
            continue  # Verbatim upstream legal notices are not navigation guides.
        if file.suffix.lower() not in ('.md', '.html'):
            continue
        text = file.read_text(encoding='utf-8-sig')
        if file.suffix == '.md':
            # Documentation uses inline links; allow balanced parentheses in DOI URLs.
            targets = re.findall(r'\[[^\]]*\]\(([^\s]+?)(?:\s+"[^"]*")?\)(?=\s|[.,;:]|$)', text)
            parser = Links()
            parser.feed(text)
            targets += parser.targets
        else:
            parser = Links()
            parser.feed(text)
            targets = parser.targets
        for target in targets:
            parts = urlsplit(target.strip('<>'))
            if parts.scheme or parts.netloc or not parts.path:
                continue
            resolved = (file.parent / unquote(parts.path)).resolve()
            if not resolved.is_relative_to(package) or not resolved.exists():
                missing.append(f'{file.relative_to(package).as_posix()} -> {target}')
    return missing


def copy_resources(destination):
    destination = Path(destination)
    for item in FILES:
        target = destination / item
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / item, target)
    shutil.copytree(ROOT / 'examples', destination / 'examples', dirs_exist_ok=True)


def copy_dependency_licenses(destination):
    """Preserve nested upstream notices without flattening same-named licenses."""
    destination = Path(destination) / 'THIRD-PARTY-LICENSES'
    destination.mkdir(parents=True, exist_ok=True)
    for dist in distributions():
        for item in dist.files or ():
            parts = item.parts
            if not parts or '..' in parts:
                continue
            if not (item.name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE', 'AUTHORS'))
                    or any(part.lower() == 'licenses' for part in parts)):
                continue
            source = Path(dist.locate_file(item))
            if source.is_file():
                target = destination / dist.metadata['Name'] / Path(*parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)


def write_checksums(package):
    package = Path(package)
    lines = []
    for file in sorted(package.rglob('*')):
        if file.is_file() and file.name != 'SHA256SUMS.txt':
            lines.append(f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.relative_to(package).as_posix()}')
    (package / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='ascii')


def verify_resources(package, expected_commit=None):
    package = Path(package)
    required = (*FILES, 'TPD-Spectra-Studio.exe', 'VERSION.json', 'SHA256SUMS.txt',
                'THIRD-PARTY-LICENSES', 'examples/beta_collection/catalog.json',
                'examples/publication_data/catalog.json', 'examples/publication_data/README.md')
    for item in required:
        assert (package / item).exists(), f'Missing package resource: {item}'
    for item in INTERNAL:
        assert not (package / item).exists(), f'Internal document in colleague package: {item}'
    assert not (package / 'validation/WINDOWS_B5_RESULTS.json').exists()
    assert list((package / 'THIRD-PARTY-LICENSES').glob('*')), 'Dependency licenses missing'
    identity = json.loads((package / 'VERSION.json').read_text(encoding='utf-8-sig'))
    assert re.fullmatch('[0-9a-f]{40}', identity['commit']), 'Unrecorded build commit'
    if expected_commit:
        assert identity['commit'] == expected_commit, 'Source/portable commit mismatch'
    assert identity['version'] in (package / 'START_HERE.md').read_text(encoding='utf-8')
    assert identity['version'] in (package / 'docs/beta/RELEASE_NOTES.md').read_text(encoding='utf-8')
    errors = broken_links(package)
    assert not errors, '\n'.join(errors)
    hashes = {}
    for line in (package / 'SHA256SUMS.txt').read_text(encoding='ascii').splitlines():
        digest, name = line.split('  ', 1)
        hashes[name] = digest
        assert hashlib.sha256((package / name).read_bytes()).hexdigest() == digest, f'Checksum mismatch: {name}'
    expected = {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt'}
    assert set(hashes) == expected, 'Checksum manifest must cover every shipped file'
    return identity


if __name__ == '__main__':
    import sys
    copy_resources(sys.argv[1])
