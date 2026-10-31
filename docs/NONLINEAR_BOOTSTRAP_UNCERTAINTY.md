# Nonlinear kinetic-fit uncertainty (experimental API)

`tpd_spectra.bootstrap.bootstrap_kinetic_parameters` provides an **opt-in**, seed-controlled, parametric Gaussian bootstrap for the **single-state, fixed-order** Polanyi–Wigner fitter. It is not automatically included in ordinary result exports and has not been validated against experimental datasets.

## Usage

```python
from tpd_spectra.bootstrap import bootstrap_kinetic_parameters
result = bootstrap_kinetic_parameters(temperature_c, signal, heating_rate_k_s=1.0,
    reaction_order=1.0, n_resamples=100, seed=20261019)
print(result.as_dict())
```

The fitted predicted trace is treated as the true mean; Gaussian independent noise is generated using the sample residual standard deviation (degrees of freedom accounting for four free parameters, or three when baseline is fixed). Every replicate is independently reoptimized. Estimated 2.5th–97.5th percentile limits are *conditional on the assumed model, known heating rate and calibration, fixed desorption order and fitting window, and Gaussian error approximation*. This is not a generic 95% guarantee.

Reported intervals are **withheld** when the original fit fails, diagnostics warn of rank/conditioning/bound issues, the residual noise estimate is invalid, more than the configured fraction of resampled fits fail, fewer than 20 fits converge, or correlation cannot be computed. Warnings and failure counts remain available. Correlation between energy and log10(prefactor) is descriptive and does not prove uniqueness. No covariance-matrix Gaussian interval is inferred from the Jacobian.

## Future validation

1. Quantify interval coverage under correctly specified independent Gaussian measurement noise.
2. Stress-test model mismatch, colored/heteroscedastic noise, background drift, uncertain heating rate, and calibration shifts.
3. Investigate profile likelihood, stronger global multi-rate constraints, and clearly distinguish practical from structural identifiability.
4. Expose intervals in the GUI only after scientific validation is complete.

Bootstrap refits can be computationally expensive. The caller should run this away from the GUI event loop.

## Consolidation status

This opt-in research API is present in `main`; it is not connected to the
desktop workflow and is not interchangeable with Explorer Monte Carlo. It
currently reports intervals only for energy and prefactor, unlike Explorer
Monte Carlo's estimated free-parameter ranges. Its
20-refit floor is an experimental operational rule, not evidence of interval
coverage. Refits with diagnostic warnings are counted as unsuccessful. Fixed
zero order is rejected here because its prefactor/scale pair is non-unique;
use the current Explorer path for conditional depletion brackets. Do not use
these research percentiles as validated experimental confidence limits.
