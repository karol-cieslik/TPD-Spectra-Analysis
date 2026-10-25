# Scientific audit: parameter uncertainty and validation

Audit of `main` at commit `0f870a783effa18fd4f7880b6cb754e324b8a0d5` (v0.10.2), 19 October 2026. This document records code-level observations; it is not a claim of independent experimental validation.

## Existing functionality verified by code inspection

- `tpd_spectra/analysis.py`: leading-edge estimates include OLS slope standard error and nominal 95% Student-t intervals, transformed into activation-energy intervals.
- `tpd_spectra/kinetics.py`: `simulate_tpd` solves the coverage equation along an increasing temperature grid assuming a constant heating rate.
- `fit_polanyi_wigner`: bounded nonlinear least squares fits activation energy, log10 prefactor, log10 signal scale, optional baseline, and optional reaction order. It reports RMSE, normalized RMSE, R², AIC/AICc/BIC, and the condition number of the residual Jacobian.
- `fit_two_state_polanyi_wigner`: supports exploratory overlapping-state models with fit diagnostics.
- `tests/test_kinetics.py` and `tests/test_phase4_validation.py`: test selected synthetic recovery cases, monotonic coverage, input validation, and a first-order quadrature reference.

## Limitations requiring work

1. **Nonlinear-fit intervals are not implemented.** The single-state and two-state result dataclasses do not expose energy/prefactor confidence intervals. Do not interpret the existing Jacobian condition number as an uncertainty interval.
2. **Identifiability needs more than a condition number.** Energy/prefactor/scale correlations and bounds can make Hessian-based intervals unreliable even when a solver reports success.
3. **Nominal leading-edge intervals are conditional.** The reported OLS 95% interval reflects regression scatter under its assumptions; it does not incorporate heating-rate uncertainty, baseline uncertainty, temperature calibration, correlated residuals, or model choice.
4. **Model-selection statistics require care.** AIC/AICc/BIC comparisons should use the same observations and likelihood/error assumptions; a lower score does not establish a particular adsorption mechanism.
5. **Two-state parameters may be weakly determined** when peaks overlap strongly. Recovery tests should include indistinguishable or nearly indistinguishable states and explicit failure-to-identify outcomes.
6. **Temperature-grid preprocessing matters.** The single-state fitter averages signals at repeated temperatures, altering effective observation weighting. Future uncertainty estimates must be explicit about the fitting grid and noise model.

## Proposed incremental implementation

### PR 2 — Uncertainty diagnostics, without misleading intervals
- Report rank or singular-value diagnostics in an explicitly documented structure and flag bound-hitting fits.
- Define a consistent parameter ordering and parameterization for diagnostics (especially log10 prefactor/scale).
- Add deterministic tests for identifiable and ill-conditioned synthetic cases.
- Preserve existing public return signatures and CSV fields wherever possible.

### PR 3 — Optional covariance approximation
- For well-conditioned, interior fits with sufficient residual degrees of freedom, estimate covariance via the scaled residual Jacobian.
- Transform log10-space intervals to positive physical units correctly.
- Return unavailable/undefined intervals with explanatory warnings for rank-deficient or boundary solutions.
- Mark these as *local, conditional, asymptotic* intervals, not universal experimental uncertainties.

### PR 4 — Bootstrap and sensitivity analysis
- Add reproducible seed-controlled residual or parametric bootstrap for suitable noise models; explicitly explain the independent-residual assumption and alternatives for serial correlation.
- Propagate user-supplied heating-rate and temperature calibration uncertainty with sensitivity analysis.
- Benchmark coverage, numerical accuracy, optimizer convergence, computational cost, and interval coverage on synthetic data.

### PR 5 — GUI and export
- Expose fit confidence/diagnostic summaries and methods in the desktop GUI, with an explanation of assumptions.
- Include fitted uncertainties, method, settings, warnings, and random seed in machine-readable exports.
- Never silently display a numerical error bar when uncertainty estimation fails.

### External-data validation (separate)
- Compare against digitized literature spectra and laboratory measurements only when the relevant data and metadata have been curated, with provenance and digitization uncertainty recorded.

## Release gates

- Existing tests remain passing.
- New tests cover zero-, first-, second-, noninteger-order and overlapping-state simulation/fitting where supported, plus degenerate and boundary cases.
- Numerical results are reproducible with explicit software/settings metadata.
- No GUI uncertainty claim exceeds what the numerical assumptions justify.
- Independently collected spectra remain a separate release criterion for publication-facing validation claims.
