# TPD Spectra Studio 0.11.0b7 — research beta notes

Public download: [v0.11.0b7 — Research Beta](https://github.com/karol-cieslik/TPD-Spectra-Analysis/releases/tag/v0.11.0b7).
Extract the complete Windows ZIP and retain its docs/examples. `VERSION.json`
records the source commit; the ZIP checksum and packaged `SHA256SUMS.txt` support
integrity checks. The package includes the changes merged in PR #37. Earlier
Actions artifacts sharing the b7 label may not include them. This remains a
research beta; scientific estimates are conditional on the chosen model.

## Changes in b7

- Reduced the header and replaced the two-row, nine-button command strip with
  **File / Examples / View / Help** menus and only three quick actions.
  Import, project, export, scientific help, about, classic view and feedback
  remain available; keyboard shortcuts include Ctrl+O, Ctrl+S and F1.
- Split **Browse examples…** into **Simulated** (21 known-input models) and
  **Publication-derived** (nine licensed curves from six sources), with citations,
  DOI, figure, units, heating rate, licence and methodological warnings in
  a readable detail pane.
- Package original licensed numeric CSV coordinates beside instrument-compatible
  views; missing digitization points are omitted, not filled. Figure-derived
  time is an explicit nominal-ramp coordinate and is **not observed time**.
  CO correspondence and noncommercial/reuse-unclear figures remain excluded.
- Unified 1–3 component workflow: **Fit Multiple Peaks… → choose count →
  verify rate → select positions → Fit N Components**, with numeric position
  entry and Advanced controls. This supersedes the two formerly separate entry points.
  First-order Redhead guesses and ±30% search bounds are initialization aids.
- Published heating rates are suggestions requiring explicit confirmation.
  Zaki D₂O/Fe₃O₄ suggests **3 K/s**; Modeling and Kinetic Analysis have separate
  settings. Opening a published example no longer silently applies its rate.
- Thermal multistart and coordinate scaling address flat, baseline-dominated
  fits. Titles/status flag baseline-only, poor fits and collapsed components;
  every component, sum, baseline and residual has distinct styling. Inspect the
  full diagnostics and fixed assumptions before interpreting any result.
- The retained Zaki stress test improves numerically (normalized RMSE ≈0.261
  to ≈0.126), but correlated residuals still withhold intervals. It does not
  validate two first-order populations or experimental energies. The physical
  PW model and separate one-peak engines are unchanged. See the updated
  [workflow, safeguards and validation](../MULTICOMPONENT_FITTING.md).

This versioned prerelease is intended for public beta feedback. Independent
experimental validation, calibrated uncertainty and broader human visual/DPI
and clean-machine acceptance remain open. Please report bugs, suggestions or
scientific discrepancies to **karol.j.cieslik@gmail.com** or use in-app Help →
Report a bug / Send feedback.

## Fixes in b6

- Report / Export shows an explicit explanation if no labeled analysis run has been saved and displays the saved-run count next to the button.
- Updating an existing peak interval refreshes invalid leading-edge limits to the new bounds; custom subintervals within those bounds are preserved.
- Modeling plots focus on the selected peak interval; stale comparisons remain retained but no longer replace the current plotted data.
- Manual simulations and fitted comparisons use separate display modes so an oversized simulation does not squash the fitted curves. A warning explains large simulation-to-data amplitude differences.

## Features carried over from b5

- Structured Results tabs distinguish fitted, assumed and calculated quantities
  and retain submitted settings and scientific cautions.
- Searchable offline scientific Help contains 41 topics, with field-level help.
- Five guided in-app exercises and an offline HTML worked guide accompany the
  brief five-page Quick Start PDF.
- Windows executable version metadata and portable commit identity agree.
- The portable package contains researcher documentation, examples and licenses;
  internal planning, audit and acceptance records remain in the repository.

Automated Windows tests and frozen smoke checks have passed. Human visual/DPI
inspection and independent Windows 10/11 installation without Python remain
outstanding. Run those checks on the exact downloaded ZIP before sharing it.

## Changes

- The import preview supports CSV, TSV and TXT, with per-file channel mapping, source-unit confirmation, and accepted/rejected row counts before data enter the workspace. Reviewed import choices are carried into saved analysis runs.
- The default demo opens with a prepared region; raw spectra remain visible
  across stages, missing regions, calculations, failures and cancellation.
- Monte Carlo progress, elapsed/estimated remaining time, Cancel and fit/failure
  counts are prominent. Existing threaded calculation and seeds are retained.
- Seeded 1/2/5% detector-noise variants and offset/drift demonstrations preserve
  clean physical truth; observation markers and model curves are distinguishable.
- Up to three independent Polanyi–Wigner components fit simultaneously on one
  full spectrum. Fixed component orders/prefactors/coverages, joint energy/scale
  estimates, shared offset/drift, heuristic count comparison, conditional local
  uncertainty and individual exports are documented in [the component guide](../MULTICOMPONENT_FITTING.md).
- Component Monte Carlo and multicomponent zero-order searches remain outside
  this increment. Synthetic recovery does not establish physical state identity.

- Fixed-single-state zero-order fits now search the depletion edge explicitly,
  profile energy and solve amplitude/baseline. The original clean-reference
  residual limit is unchanged and its expected-failure marker is removed.
- Prefactor/scale brackets, conditions and representative-value labels persist
  through saved projects and reports. Monte Carlo retains per-refit brackets and
  withholds misleading percentiles of representative zero-order prefactors.
- Old zero-order results and prior modeling sessions remain inspectable but are
  stale for new calculations. Recompare before Monte Carlo or model transfer.

- Inspectable feedback reports with categories, optional contact/steps, sanitized
  diagnostics, offline copy and ZIP, and explicitly reviewed email/GitHub drafts.
  No automatic submission or spectral attachment.
- About/contact/contribution links for Dr. Karol Cieślik.
- Twenty-one physical synthetic datasets with independent generation, per-file truth,
  seeds, units, noise/baseline descriptions and automated import/recovery checks.
- Browse examples (synthetic and cited publication-derived spectra), parameter hints, accessible Quick Start and feedback.
- Updated Quick Start, short START_HERE and optional colleague test checklist.
- Preserved classic/batch functionality, three-stage workflow, project/report
  exports and seeded parametric Monte Carlo. Positive-order integration and
  fitting algorithms are retained. Fixed-order initialization now respects the
  requested order rather than clipping it to the free-order search bounds.

## Known limitations and review gates

- Zero-order brackets reflect point sampling at fitted energy and normalized
  initial coverage, not statistical confidence. Numerical completion is not
  physical validation. Edge-search information criteria are heuristic. At least
  three samples after depletion are required; unresolved edges are rejected.
  Multi-state/global zero-order local-optimizer paths are unchanged and remain
  experimental, with explicit warnings. Independent real-data review remains open.
- Parametric Monte Carlo assumes iid Gaussian noise around a fitted reference.
  It is not microscopic kinetic MC, MCMC, mechanism probability or a validated
  uncertainty-coverage procedure. Ranges are withheld below 100 successful refits.
- Real-instrument validation, independent scientific review and human Windows
  layout/scaling acceptance remain open. Please report any clipped controls or
  unusual layout at your usual display resolution and scaling.
- Windows executable is unsigned. Follow institutional software policies.
- Verify the exact source commit in `VERSION.json`; do not substitute a historical artifact for the current beta.
- Analysis reports and portable projects contain scientific data; the separate
  diagnostic ZIP contains only its editable report and explanatory README.

If you find a confusing step, a crash or a scientific discrepancy, use the
application's **Report a Bug / Send Feedback** action or email the maintainer.
