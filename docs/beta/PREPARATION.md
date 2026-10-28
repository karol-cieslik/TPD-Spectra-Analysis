# External beta preparation record

> Historical development snapshot. PRs #19–21 are now merged into main.
> For current beta/download status see [START_HERE](../../START_HERE.md). Original evidence below is preserved.

## 0.11.0b3: dedicated zero-order correction

Current branch: `release/external-beta-v0.11.0b3`; the 0.11.0b2 branch and
artifacts remain intact. The single-state fixed-zero-order fitter now searches
the sampled depletion edge, records conditional prefactor/scale brackets and
withholds misleading Monte Carlo prefactor percentiles. Its original residual
test now passes without an expected-failure marker or a relaxed tolerance.

The historical failures and builds below refer to 0.11.0b2. Current method scope
and limitations are documented in [ZERO_ORDER_FITTING.md](../ZERO_ORDER_FITTING.md).
Verified application commit: `e655f8d621b4d13a341588f2e4d3fae5f21f1736`.
Draft review: https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/12

- Windows run [40180695189](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40180695189):
  **237 passed, zero expected failures, 3 existing plot-layout warnings**, 46.06 s.
- Frozen executable and assembled-package checks passed: icon, CLI/demo,
  classic GUI/Explorer/short MC, workflow comparison/context/fit/project/report,
  16 bundled examples, guide and offline feedback. The new explicit zero-order
  GUI fit, conditional ranges, project/report and two seeded MC refits also passed.
- Linux run [40180718560](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40180718560):
  Python 3.10, 3.11 and 3.12 each **214 passed, 23 headless GUI skips**, no expected failures.
- [Download Windows 0.11.0b3](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40180695189/artifacts/12593773676)
  (86,152,773 bytes; artifact expires 2027-01-23).
- ZIP SHA256: `ec4cb3a7117ef0e2257b2bb1d4f6704652d30db74542e5ad3b228185692acea7`.
- Evidence: `validation/zero-order-e655f8d.json`. The unchanged original example
  recovers 1.2000000002 eV (input 1.2 eV), normalized RMSE about 1.05e-11
  against its unchanged 0.02 threshold.

These automated checks do not establish manual clean-machine layout/scaling
acceptance, real-instrument validity or uncertainty coverage. Multi-state/global
zero-order optimizers remain outside this correction. No release was published.

## Latest build: equation-panel follow-up

Application commit `88378fed6e72baa74eb6e3c54ed80e0845e293ff` adds read-only
equations above the modeling, method-specific fitting and Monte Carlo inputs.
Expandable legends explain symbols, units and assumptions without changing
parameters or starting calculations. The numerical engines are unchanged.

- [Updated Windows download](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40112805670/artifacts/12566939531)
  includes the equation panels; the earlier artifact below remains available.
- Windows: **221 passed, 1 expected failure, 3 existing layout warnings** in
  78.69 seconds. All frozen CLI/GUI, Monte Carlo, context, project/report,
  examples/resources and offline feedback checks passed.
- Linux Python 3.10, 3.11 and 3.12: **199 passed, 22 headless GUI skips,
  1 expected failure** each. Local workflow UI checks: 13 passed.
- ZIP SHA256: `8445744ba754f62ac13404217f52205c7d15cfc863d61b2c9db506d4db955659`.
  Size: 86,138,660 bytes; expires 22 January 2027.
- [Machine-readable build evidence](../../validation/equations-88378fe.json).

The known zero-order residual failure, human Windows layout/scaling acceptance,
actual GUI screenshots and independent scientific validation remain open.
This update does not change the beta's readiness classification. No release
was published. The records below document the earlier package.

## Original external-beta preparation

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
