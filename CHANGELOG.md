## 0.11.0b4 — beta feedback (development candidate, unreleased)

- Fit up to three independent Polanyi–Wigner populations simultaneously on one
  full spectrum, with per-component fixed order/prefactor/coverage, joint energy
  and nonnegative scale estimates, and shared offset/optional drift. Show each
  contribution, sum and residual; compare counts, save projects and export parameters.
  Withhold local intervals for ambiguous, exchangeable, bounded or ill-conditioned
  decompositions. This exploratory increment excludes component Monte Carlo and
  multicomponent zero-order depletion searches.
- Supply seeded clean/low/moderate/high-noise demonstrations and an offset/drift
  example. Preserve theoretical reference curves and kinetic validation truth.
  Plot observations as muted open markers and models as contrasting curves.
- Show Monte Carlo progress, elapsed/estimated remaining time and fit/failure
  counts beside Run/Cancel. Retain the worker thread, prevent duplicate jobs,
  and discard cancelled results even if success was already queued.
- Keep the original spectrum visible in Modeling and Kinetic Analysis without
  a named region, during calculations and after errors. Provide actionable region guidance.
- Open the shipped default demo with a prepared first-peak region; document a
  simulation, comparison, seeded Monte Carlo and explicit-fit walkthrough.

## 0.11.0b3 — external research beta (25 October 2026, unreleased)

- Consolidated the verified beta into `main`; the current Windows artifact is
  built and tested from that branch. No public release tag has been issued.
- Corrected fixed single-state zero-order fitting using depletion-edge profiling.
  Conditional prefactor/scale ranges replace misleading unique-pair claims;
  earlier zero-order results should be recalculated before interpretation.
- Provided 16 independently generated, documented synthetic examples and an
  in-app example chooser with a reproducible first-order walkthrough.
- Added inspectable, offline bug reports and diagnostic ZIPs with no automatic
  upload or raw spectrum attachment.
- Added a four-page Quick Start, project save/load and selected-run PDF/CSV/JSON/
  PNG/SVG reporting. The three-stage workflow retains the Classic/batch option.
- Independent experimental validation, human GUI/display-scaling acceptance
  and validated uncertainty coverage remain open.

## 0.11.0b2 — beta feedback and onboarding (unreleased)

- Introduced beta feedback, synthetic example collection and portable package
  resource checks. Superseded by the corrections in 0.11.0b3.

## Development preview — workflow redesign (historical)

- Add three workflow stages with shared dataset/peak identity and exclusive
  method controls; retain the classic GUI, advanced methods and CLI.
- Add debounced lightweight results, explicit cancellable fits, per-context
  settings, stale-result labels and multiple named saved runs.
- Embed existing model simulation, comparison and seeded parametric Monte
  Carlo; transfer selected hypotheses explicitly into kinetic fitting.
- Add immutable imported data, reversible processing recipes, checksummed
  portable projects and selected PDF/CSV/JSON/PNG/SVG report bundles.
- Extend workflow, persistence, export and frozen Windows verification. No
  numerical solver equations or optimizer algorithms are changed.
- Experimental-data validation and broader human/scaling acceptance remain
  release gates; this preview is not a publication-readiness claim.

## 0.11.0b1 — unreleased roadmap / Explorer candidate

- Add an original multi-size spectrum icon to the executable and desktop windows, a navy/teal identity, clearer tabs and selection states, a wrapping toolbar, plot-adjacent export and branded About. Keep scientific figures free of branding.
- Use maintainer’s preferred name Karol Cieślik and shared package/citation/About identity.
- Add reviewed save destinations, separate Show/Include, immutable run snapshots, exclusive folders, setup/computed preview, streamed logs, cancellation and results review.
- Record import row decisions and corrected temperatures.
- Correct misleading physical leading-edge prefactor reporting: unavailable for arbitrary-unit signal; retain log-signal intercept. Old prefactor interpretations must be re-evaluated.
- Include estimated residual variance in Gaussian information-criterion parameter counts; prior model rankings can change.
- Integrate PR #8 Explorer/Monte Carlo with snapshot-safe exports, queue-based GUI updates, cancellation, explicit incomplete rankings, conditional-range withholding, all completed refit records and SVG export.
- Add independent all-order coverage references and packaged Tk/Explorer/short-MC smoke.
- Track 84 original plus 10 Explorer checkpoints without claiming experimental/human acceptance.

## Unreleased beta candidate — demo import and Quick Start

- Validate required CSV headers and numeric channels before choosing a layout;
  conventional semicolon files no longer lose their header to the legacy skip.
- Preserve coarse heating ramps. Temperature cleaning now flags isolated
  reversals rather than every step above 1.5 °C, retains the recovery sample,
  and interpolates on elapsed time. Nonfinite/out-of-bounds values are still
  screened. Finite endpoint jumps and sustained discontinuities are retained
  for review, not automatically treated as spikes.
- Replace the failing Gaussian example with a reproducible, documented
  two-population first-order simulation and include it in desktop beta ZIPs.
- Replace the escaped-newline message box with a resizable, scrollable Quick
  Start dialog containing five distinct steps and tested demo settings.
- Add tests of shipped data, scientific reference values, CLI exports, actual
  Tk import/plot behavior, and dialog layout at a small window size.

## 0.10.2 — Display-aware startup

- The desktop app now opens maximized to the available display area and adjusts its minimum size for smaller screens.

## 0.10.1 — Windows startup and single-file fix

- Fixed a startup crash caused by calling a missing desktop setup method.
- Combined the desktop app and batch-analysis engine into one Windows executable.
- Updated Windows downloads and quick-start instructions to present one app file.

## 0.10.0 — Interactive desktop studio

- Rebuilt the desktop interface as an import-and-explore workspace with multi-file and folder import, trace visibility controls, overlay and small-multiple views, temperature/time axes, and normalized comparison.
- Added responsive smoothing and analysis-window controls, an output-folder picker, a high-resolution PNG export action, and direct full-batch analysis with optional kinetic fits.
- Added automatic delimiter/decimal detection for comma, semicolon, and tabular CSV data with common temperature header variants.
- Added a Windows desktop build workflow that packages a no-console GUI executable with its CLI partner and documentation.
- Refreshed the repository landing page with a visual preview, clearer install/download guidance, feature overview, output guide, and scientific-scope notes.

## 0.9.1 — License scope and release-readiness update

- Added a scoped MIT license for project-authored software code and declared the package license metadata.
- Clarified that example spectra, the historical notebook, images, and thesis-derived/third-party materials are not automatically covered by the code license.
- Updated the Windows release workflow to include the license and a clearer distribution notice in the portable beta package.
- Updated the release checklist and validation report to distinguish code licensing from data/asset redistribution rights.
- Fixed explicit setuptools package discovery after a wheel-build check exposed flat-layout ambiguity; package build is now included in release-readiness verification.
- Added an asset-rights inventory and excluded generated output manifests containing stale absolute paths from the clean release archive. The Windows beta no longer bundles experimental CSVs until redistribution rights are confirmed.

# Changelog

## 0.9.0 — Phase 7 desktop GUI and release metadata

- Added an optional Tkinter desktop interface for selecting input/output paths, configuring classical analysis, and enabling optional numerical kinetic fitting.
- Reused the CLI pipeline from the GUI to avoid diverging scientific implementations; background execution keeps the window responsive.
- Added headless unit tests for GUI argument construction and validation.
- Added the `tpd-spectra-gui` entry point, `CITATION.cff`, and a public-release checklist.
- Updated Windows packaging to build both CLI and GUI executables. The Windows artifacts still require smoke testing on a clean Windows machine.
- Kept licensing unresolved rather than assuming rights to the source or example spectra.

## 0.7.0 — Phase 5 overlapping-state model comparison

- Added an exploratory two-state Polanyi–Wigner fitter with separate energies, prefactors and signal scales plus a shared baseline and reaction order.
- Added AIC/AICc/BIC, Jacobian condition number, and warnings for ill-conditioning, weak components, close state energies, optimizer failure and high residual error.
- Added `--kinetic-model single|two-state|compare`, comparison CSV rows, and two-state diagnostic plots. Single-state remains the default.
- Added synthetic two-state recovery and invalid-input tests.
- Documented model assumptions and cautions about overfitting and parameter identifiability.


## 0.2.0 — 2026-10-14

- Added modular `tpd_spectra` analysis package and batch CLI while preserving the historical notebook.
- Fixed Redhead calculation to use kelvin consistently inside the logarithm and use heating rate in K/s.
- Fixed leading-edge region selection to apply the same mask to temperature and signal.
- Replaced off-by-one rolling filters with centered rolling mean/median and explicit edge behavior.
- Made temperature cleaning configurable and applied endpoint checks consistently.
- Added input schema validation, sorted CSV discovery, per-file error handling, fit diagnostics, portable output paths, and machine-readable exports.
- Added unit and example-data import tests.
- The original notebook's corresponding filter, Redhead, leading-edge mask and CSV export cells were patched. Full notebook execution remains unverified.


## 0.3.0 — Phase 1 scientific diagnostics

- Added ordinary least-squares residual RMSE, slope standard error and a regression-only 95% confidence interval for leading-edge energy.
- Added screening metrics for negative signal, signal dynamic range, low-signal proxy and temperature points altered by heuristic cleaning; no automatic baseline correction is performed.
- Added explicit warnings for questionable regression quality, missing leading-edge fits, non-positive leading-edge energies, peak maxima at search-window boundaries, and potentially appreciable low-signal offsets.
- Added Redhead prefactor sensitivity scenarios at 0.1× and 10× the assumed prefactor.
- Added per-spectrum diagnostic plots and an aggregated `analysis_warnings.csv` export.
- Documented the interpretation and limitations of each diagnostic and added regression tests.


## 0.4.0 — Phase 2 numerical kinetic fitting

- Added numerical coverage integration for the Polanyi–Wigner rate equation under a linear heating ramp.
- Added bounded full-trace least-squares fitting for activation energy, prefactor (log-space), signal scale and optional constant baseline; reaction order can be fixed or estimated.
- Added optional CLI workflow (`--kinetic-fit`) with fit summary CSV and overlaid experimental/model plots. The CLI reconstructs a monotonic linear-ramp coordinate from acquisition time and fitted heating rate for the model, while retaining measured temperature for display.
- Added synthetic recovery, reaction-order behavior, exhausted-coverage and input-validation tests.
- Documented model assumptions and limitations, including energy–prefactor correlation and the distinction between fit quality and mechanistic validation.

## 0.5.0 — Phase 3

- Added named analysis presets and JSON configuration loading/saving; explicit CLI flags take precedence over config values.
- Added a combined batch summary table and a project manifest with effective parameters, input file hashes, run timestamp, software version and run status.
- Improved repeat-run hygiene by removing stale warning/error CSVs when a new run has none.
- Added automated tests for project provenance and config precedence.

## 0.6.0 — Phase 4 validation and beta packaging

- Added an independent first-order analytical/quadrature cross-check for the Polanyi–Wigner coverage trajectory, plus physical-bound checks and validation of all included example CSVs.
- Expanded kinetic-fit input validation: non-finite coverage, constant signals, and invalid evaluation limits now fail explicitly rather than yielding misleading fits.
- Added additional tests for analytic recovery, physical coverage bounds, degenerate data, and duplicate temperature samples.
- Added a Windows GitHub Actions workflow that runs tests/reference validation and builds a portable PyInstaller executable ZIP on Windows; tagged versions attach the ZIP to a GitHub Release.
- Added build requirements and a dedicated executable entry point. A Windows binary must be built on a Windows runner; it is not claimed to have been built in this Linux environment.
- Documented scientific limitations, beta build instructions, and the need to establish an explicit license before public redistribution.

## 0.8.0 — Phase 6 global kinetics and noise recovery

- Added a joint Polanyi–Wigner fit that shares activation energy and prefactor across multiple heating-rate traces while retaining per-trace scale and baseline nuisance parameters.
- Added per-trace residual metrics, approximate energy/log-prefactor correlation, Jacobian conditioning, information criteria, and warnings.
- Added synthetic multi-rate parameter recovery tests and a reproducible noise-level benchmark script that exports CSV and JSON results.
- Documented shared-model assumptions and cautions on identifiability and experimental comparability.
