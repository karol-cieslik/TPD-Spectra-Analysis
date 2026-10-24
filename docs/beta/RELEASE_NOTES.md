# 0.11.0b2 - external beta review candidate

Prepared for Karol Cieślik's review, not a published release or declaration of
scientific validation. Existing main, beta and workflow-preview branches remain
intact. Download/build evidence is recorded in PREPARATION.md after verification.

## Changes

- Inspectable feedback reports with categories, optional contact/steps, sanitized
  diagnostics, offline copy and ZIP, and explicitly reviewed email/GitHub drafts.
  No automatic submission or spectral attachment.
- About/contact/contribution links for Dr. Karol Cieślik.
- Sixteen physical synthetic datasets with independent generation, per-file truth,
  seeds, units, noise/baseline descriptions and automated import/recovery checks.
- Open Example Dataset, parameter hints, accessible Quick Start and feedback.
- Four-page Quick Start, short START_HERE and optional colleague test checklist.
- Preserved classic/batch functionality, three-stage workflow, project/report
  exports and seeded parametric Monte Carlo. Numerical engines are unchanged.

## Known limitations and review gates

- **Zero-order quantitative fitting is not validated:** clean-reference amplitude
  bias produces normalized RMSE≈0.0561 against the retained 0.02 threshold.
  A strict expected-failure test keeps this issue visible. Convergence alone is
  insufficient; UI warns before interpretation. Other clean fixed-order checks
  use truth-informed starts and do not establish blind identification.
- Parametric Monte Carlo assumes iid Gaussian noise around a fitted reference.
  It is not microscopic kinetic MC, MCMC, mechanism probability or a validated
  uncertainty-coverage procedure. Ranges are withheld below 100 successful refits.
- Real-instrument validation, independent scientific review and human Windows
  layout/scaling acceptance remain open. Capture failed with `FrameArrived timed
  out` and `window capture timed out`; the guide contains no invented screenshots.
  Add actual reviewed GUI screenshots before treating the guide as final.
- Windows executable is unsigned. Follow institutional software policies.
- Analysis reports and portable projects contain scientific data; the separate
  diagnostic ZIP contains only its editable report and explanatory README.

Do not publish a prerelease or invite colleagues automatically. First review the
build evidence, outstanding gates and the scope of the proposed limited beta.
