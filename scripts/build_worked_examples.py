"""Rebuild the self-contained offline Quick Start HTML from the reviewed Markdown."""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'docs/beta/WORKED_EXAMPLES.md'
    header = ROOT / 'scripts/worked_examples_head.html'
    destination = ROOT / 'docs/beta/WORKED_EXAMPLES.html'
    subprocess.run(['pandoc', '--from=gfm', '--to=html', '--standalone',
                    '--metadata=title:TPD Spectra Studio — Worked Quick Start',
                    '--include-in-header=' + str(header), str(source),
                    '--output=' + str(destination)], check=True)
    print(destination)


if __name__ == '__main__':
    main()
