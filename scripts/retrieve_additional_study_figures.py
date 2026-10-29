"""Retrieve five identified reference images, verifying previously observed hashes.

Use a destination outside the checkout. Images retain their source licences,
including CC-BY-NC-3.0 for Perrero et al.; this performs no digitization or fits.
"""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.destination.resolve()
    if destination == root or root in destination.parents:
        parser.error('Choose a destination outside the repository to keep source licences separate.')
    manifest = json.loads((root / 'validation/experimental/additional_studies_2026_10_29/source_manifest.json').read_text())
    destination.mkdir(parents=True, exist_ok=True)
    for source in manifest['figures']:
        path = destination / source['file']
        if path.exists():
            data = path.read_bytes()
        else:
            with urllib.request.urlopen(source['url'], timeout=30) as response:
                data = response.read()
        if len(data) != source['bytes'] or hashlib.sha256(data).hexdigest() != source['sha256']:
            raise ValueError(f"Source changed or download incomplete: {source['file']}")
        if not path.exists():
            path.write_bytes(data)
        print(f"Verified {source['file']} ({source['licence']})")
    (destination / 'source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
