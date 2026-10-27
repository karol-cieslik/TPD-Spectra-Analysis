# Contributing to TPD Spectra Studio

TPD Spectra Studio is scientific analysis software. Corrections that improve reliability and reproducibility are prioritized over feature additions.

## Getting started

Use Python 3.10 or newer. Clone the repository, create a virtual environment, install development dependencies and the package:

```bash
python -m pip install -r requirements-build.txt
python -m pip install -e .
python -m pytest -q
```

Run the graphical application using `python run_tpd_spectra_gui.py`; for CLI commands run `tpd-spectra --help`.

## Code organization

- `tpd_spectra/analysis.py`: ingestion, preprocessing, leading-edge and Redhead calculations.
- `tpd_spectra/kinetics.py`: numerical desorption models and inverse fitting.
- `tpd_spectra/identifiability.py`: numerical fitting diagnostics.
- `tpd_spectra/gui.py` and `gui_ranges.py`: GUI and plot-interval input.
- `tpd_spectra/workflow_gui.py`, `workflow_modeling.py` and `workflow_results_gui.py`:
  the three-stage desktop flow and its result presentation.
- `tpd_spectra/scientific_help.py`, `quickstart_dialog.py` and
  `result_view.py`: offline Help, onboarding and scientifically labeled outputs.
- `docs/beta/SCIENTIFIC_HELP_TOPICS.json`: maintained Help content; keep IDs
  stable and update the browser/tests together when changing parameter meaning.
- `tpd_spectra/cli.py`: command-line and batch analysis.
- `tests/`: automated regression and scientific tests.
- `docs/USER_AND_SCIENTIFIC_MANUAL.md`: user guide, scientific assumptions and known limitations.

## Submitting a change

1. Open an issue explaining the scientific or software problem and a reproducible case.
2. Work in a short-lived branch. Do not change `main` directly.
3. Add regression tests for changes in parsing, scientific equations, optimization or outputs.
4. Record the input units, physical assumptions, numerical tolerances and expected failure modes.
5. Run `python -m pytest -q`. Check the Windows CI run if changing packaging or GUI behavior.
6. Submit a focused PR describing what changed, validation evidence, performance impacts, limitations and documentation updates.

Do not silently change default models, fitted parameter definitions, CSV schema, or exported metadata. Flag breaking changes and preserve a migration route.

## Scientific validation expectations

Synthetic tests should include known parameters and varied numerical conditions. Distinguish numerical self-consistency (same forward/inverse model), comparisons to independent implementations, and experimental validation against provenance-tracked measurements. Include failed fits in benchmark denominators. Do not assert kinetic uniqueness based on a high R². Uncertainty intervals must describe assumptions and be withheld when evidence is inadequate.

## Good first contributions

Clear error messages, independently generated example datasets with rights metadata, platform compatibility, plotting/accessibility fixes, tests for malformed input and regression documentation are especially welcome.

## Data, licensing and security

The MIT license covers project-authored code as stated in `LICENSE`. Do not submit copyrighted experimental spectra, instrument data, third-party figures or thesis assets without documented permission and attribution. Never upload credentials, private sample metadata or identifiable lab information. Report reproducible defects without exposing proprietary measurements; substitute sanitized or synthetic traces when possible.

## Publication and credit

Contributions are tracked in issues and pull requests. Scientific authorship, manuscript acknowledgement and software contribution credit should be discussed transparently before submission; a merged PR alone does not imply article authorship. Cite the released software version using `CITATION.cff` once metadata is finalized.
