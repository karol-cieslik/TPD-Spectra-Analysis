# TPD Spectra Studio 0.11.0b3 — external beta notes

This is a research beta for informal colleague feedback, not a stable release
or a claim of experimental validation. The consolidated application is on
`main`. For downloading and starting, see [START_HERE](../../START_HERE.md);
technical build evidence is maintained separately in the repository.

## Changes

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
- Sixteen physical synthetic datasets with independent generation, per-file truth,
  seeds, units, noise/baseline descriptions and automated import/recovery checks.
- Open Example Dataset, parameter hints, accessible Quick Start and feedback.
- Four-page Quick Start, short START_HERE and optional colleague test checklist.
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
- Analysis reports and portable projects contain scientific data; the separate
  diagnostic ZIP contains only its editable report and explanatory README.

If you find a confusing step, a crash or a scientific discrepancy, use the
application's **Report a Bug / Send Feedback** action or email the maintainer.
