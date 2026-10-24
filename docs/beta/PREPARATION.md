# External beta preparation record

Scope: informal review by one or two TPD colleagues. Maintainer: Dr. Karol
Cieślik, karol.j.cieslik@gmail.com. No experimental data is bundled or collected.

Base: verified redesign `11b7496` (application `d97b8f3`), with current main
documentation `01ebb47`. Existing main, beta and redesign branches are preserved.
Branch: `release/external-beta-v0.11.0b2`. Version advances from 0.11.0b1 to
0.11.0b2 for this separately identified beta; no existing releases are overwritten.

- [x] Inspect current code, tests, examples, issue templates, packaging and refs.
- [x] Feedback categories, editable report preview, copy/ZIP/email/GitHub paths.
- [x] Diagnostic privacy: allowlisted settings, no raw arrays/files/paths/names,
  sanitized exceptions/logs, explicit review, failure isolation and tests.
- [x] Extend About/contact/contribution actions without duplicate dialogs.
- [x] Physical synthetic collection with per-file truth, seeds, assumptions,
  importability, predefined recovery tolerances and overview figures.
- [x] Open Example Dataset and source/frozen resource lookup verified.
- [x] Short START_HERE, informal checklist and four-page tester Quick Start.
- [ ] Actual GUI inspection/screenshots if capture works; no fabricated images.
- [x] Full regression, all example imports, projects, reports, diagnostics and
  frozen Windows launch/dependency/resource checks completed; recovery includes
  the explicitly unresolved zero-order residual failure described below.
- [x] Downloadable artifact and release notes prepared for maintainer review.

Distribution status: review candidate only. Do not publish a release or send
invitations to colleagues on the maintainer's behalf. Record exact verification
results and limitations here before marking the review package ready.

## Local evidence (24 October 2026)

- Full development-runtime suite before final small-dialog fix: 218 passed,
  1 expected zero-order residual failure, 3 existing small-window plot-layout
  warnings. Final code is also checked in fresh Windows CI below.
- Final focused feedback suite: 12 passed, including all four actions remaining
  visible at 620×520 while form contents scroll. Email/browser calls were mocked;
  no message was sent and no issue was submitted.
- Focused examples/feedback before the layout-only fix: 33 passed, 1 expected
  residual failure. All 16 CSVs import, clean first/second/fractional recovery
  passes preset tolerances. Zero-order residual failure is explicit; other
  failures in that test are not converted to expected failures.
- Source beta smoke: 16 imports, example chooser, expected Redhead result,
  bundled-guide lookup, offline clipboard/ZIP and contact checks passed.
- Four-page PDF rendered and every page visually inspected. Unicode author name
  and units verified after font correction. Synthetic overview also inspected.
- Native GUI screenshots unavailable after refreshed-window retries:
  `FrameArrived timed out: timed out waiting on channel` and
  `window capture timed out: timed out waiting on channel`. No GUI visual/scaling
  acceptance or real screenshots claimed. Add those before finalizing the guide.
- `analysis.py`, `kinetics.py`, `kinetics_explorer.py`,
  `kinetics_uncertainty.py` and `cli.py` unchanged from the verified redesign.

## Review gates

The zero-order amplitude/residual issue requires a separately reviewed numerical
fix and independent benchmark verification before quantitative use. Experimental
validation, Monte Carlo interval coverage and human Windows display/scaling review
remain open. A successful package build does not close these scientific gates.

Draft review: https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/11

## Final automated Windows package evidence

Application commit: `535c70e8701ad575c3ceaa37bc74998908f14011`.
Later evidence-only commits do not change this executable.

- [Windows run 40111547731](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40111547731):
  **220 passed, 1 expected failure, 3 warnings**, 76.07 seconds. No GUI skips.
- Frozen checks passed: icon resources (9 sizes), CLI/demo exports, classic Tk,
  Explorer and short Monte Carlo, three-stage context isolation, model comparison,
  explicit fitting, portable project roundtrip and PDF/CSV/JSON/PNG/SVG reporting.
- Final assembled package launches from an unrelated directory with Python/Tcl
  overrides removed. All 16 examples import; chooser, guide, Redhead preview,
  offline diagnostic copy/ZIP and developer contact checks pass.
- [Linux run 40111551974](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40111551974):
  Python 3.10, 3.11 and 3.12 each report **199 passed, 21 headless Tk skips,
  1 expected failure**. These skips are not counted as GUI verification.
- [Download Windows review artifact](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40111547731/artifacts/12566303319)
  (86,130,069 bytes; GitHub login may be required; expires 22 January 2027).
- Artifact ZIP SHA256:
  `2ca090636f5609b46fd8b1fa9f65c1555404cad8fdbb83b9d55b3018af43f37c`.
  The package contains VERSION.json, executable SHA256SUMS.txt, dependencies,
  test XML and `validation/beta-package-smoke.json`.

Machine-readable evidence: [external-beta-535c70e.json](../../validation/external-beta-535c70e.json).
No prerelease/tag was created, no working branch was replaced and no invitations
were sent. This is ready for maintainer review of the limited beta scope; the
scientific and manual acceptance gates above remain open.
