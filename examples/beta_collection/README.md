# Physical synthetic TPD collection

All 16 CSVs are **simulations, not experimental measurements**. Start with
`first_order_single_peak.csv`. The GUI's **Open Example Dataset** supplies the
documented ramp and a full-trace interval. Each CSV has an adjacent JSON file
with truth, units, seed, noise, baseline, generation method, limitations and hash.
`catalog.json` powers the chooser. [Overview](overview.png) shows every trace.

| Files | Intended observation |
| --- | --- |
| zero/first/second_order_single_peak | Fixed-order isolated references |
| fractional_order_1p5 | Phenomenological constant order 1.5 |
| two/three_overlapping_peaks | Additive independent populations; single-state models are inadequate |
| first_order_noisy | iid Gaussian noise, 1% of clean maximum |
| first_order_noisy_baseline | Same noise plus constant offset and linear drift |
| challenging_overlap_drift | Mixed orders, AR(1) noise and drift deliberately violate simple assumptions |
| heating_rate_0p5/2p0/5p0_K_s | Compare with first-order reference at 1 K/s; higher ramp shifts maximum upward |
| zero/first_order_coverage_0p25/0p5 | Compare with coverage-one reference; zero-order maxima shift, first-order amplitudes scale |

The independent generator `scripts/generate_beta_examples.py` integrates
`dθ/dT = -(ν/β) θⁿ exp(-E/kBT)` by cumulative trapezoidal quadrature on a
0.005 K grid and the separable analytic coverage solution. It does not call the
production ODE or fitting engine. CSV sampling is 0.5 K, 50–450 °C, 801 points;
time is milliseconds, signal arbitrary detector units proportional to rate.
The single-state references use E=1.2 eV, ν=1e13 s⁻¹, θ₀=1, β=1 K/s and detector
scale 10000. Multi-state truths and noise/baseline parameters are in each JSON.

Coverage is dimensionless. The inverse fitter normalizes coverage to one at the
selected interval start. For another initial coverage, the corresponding
effective prefactor is ν·θ₀^(n−1), and amplitude scales with θ₀. Thus a fitted
prefactor is not automatically the generator's prefactor. Truncating a peak also
changes effective initial coverage. No absolute coverage calibration is implied.

## Checks and unresolved issue

All files must import without manual cleaning changes; tests check ramp, finite
values, point count, monotonic temperature and CSV hashes. Clean n=1, 2 and 1.5
fits pass predefined energy (2%), log10(prefactor) (0.3) and normalized RMSE
(0.01) tolerances with truth-informed initialization. These verify numerical
consistency, not blind recovery or identifiability.

**Zero-order recovery remains a known failure.** The existing solver can report
convergence at E≈1.20028 eV and ν≈9.99e12 s⁻¹ while scale is ≈14477 instead of
10000 and normalized RMSE≈0.0561, above the original 0.02 limit. The regression
is a strict expected failure; the threshold was not relaxed. Zero-order examples
remain useful for qualitative inspection, not validated quantitative fitting.

No readsorption, transport, instrument response or lateral interaction is modeled.
Fractional order is not a microscopic mechanism. Constant-baseline fitting cannot
remove linear drift; iid-noise Monte Carlo cannot represent correlated noise.
Three-state inverse fitting is not offered by the redesigned GUI. Compare
residuals, alternative explanations and acquisition conditions before interpreting
any real spectrum. These tests do not establish experimental validity.

This newly authored synthetic collection and generator are provided under the
repository's MIT license. This does not extend rights to unrelated historical
or experimental assets.
