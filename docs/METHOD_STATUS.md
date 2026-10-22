# Scientific scope and method status — 0.11.0b1 candidate

Maintainer: Karol Cieślik. This is a research beta, not a validated instrument system.
Method status describes the available evidence, not regulatory certification.

| Method | Status and supported inputs | Evidence and limits |
| --- | --- | --- |
| Import and temperature screening | Legacy millisecond / Celsius schema; explicitly named signal channels | CSV and demo regressions. Generic headers still follow the legacy unit contract; unit-mapping UI is unfinished. Inspect import reports and raw/cleaned temperature. |
| Heating-rate regression | Conditional estimate for an approximately linear heating segment, K/s | Analytic ramp regressions and demo. R² is a screening diagnostic, not an instrument calibration. |
| Leading-edge slope | Apparent energy from positive signal, constant effective population and suitable baseline/window | Exact exponential reference and signal-scale invariance test. OLS interval is regression-only. No physical prefactor can be recovered from the arbitrary-unit intercept. |
| First-order Redhead | Approximate energy with user-assumed prefactor, isolated peak and approximately linear ramp | Independent synthetic first-order reference. Sensitivity to a decade change in prefactor is exported. Not a zero/second-order method. |
| Single-state kinetic fitting | Exploratory constant-ramp Polanyi–Wigner fit; normalized initial population 1; arbitrary-unit detector scale and optional constant baseline | Numerical and recovery tests, Jacobian/bounds diagnostics; no unique-mechanism guarantee or general experimental validation. |
| Four-order Explorer | Experimental comparison of fixed 0/1/2 and fitted fractional order on the same selected observations | Independent separable coverage references at six orders and three ramps; synthetic fitter tests. Full-peak selection, baseline and initialization remain consequential. |
| Explorer Monte Carlo | Experimental parametric refitting with seeded iid Gaussian noise around one fitted reference | Repeatability, cancellation and accounting tests. Conditional percentile ranges of successful refits only, withheld below 100 successes; this operational floor does not establish coverage. Not MCMC, Bayesian inference or a microscopic kinetic Monte Carlo lattice simulation. |
| Two-state and global fits | Exploratory numerical APIs | Correlated parameters, model inadequacy and error-model assumptions remain unresolved. No general uncertainty validation. |
| Nonlinear ramps, automated mechanism assignment, calibrated coverage and general confidence limits | Not supported as validated claims | Require separate scientific development and independent experimental evidence. |

## Equations, code and scientific interpretation

- `analysis.heating_rate`: least-squares slope of Celsius versus elapsed minutes, divided by 60 to obtain K/s.
- `analysis.leading_edge_fit`: fit `ln(S)=a+b/T_K`; `E_app=-b*k_B`. Multiplying detector signal changes `a` without changing the ideal slope. The obsolete `prefactor_s_inv` field is retained as unavailable (`NaN`), and the export includes `leading_edge_log_signal_intercept` and an explanation. A factor of heating rate belongs to a change from rate per second to rate per kelvin; it cannot remove unknown detector scale or coverage.
- `analysis.redhead_energy`: `k_B*T_p*(ln(nu*T_p/beta)-3.64)`, with absolute temperature in kelvin, `nu` in inverse seconds and `beta` in K/s.
- `kinetics.simulate_tpd`: `dtheta/dT=-nu*theta**n*exp(-E/(k_B*T))/beta`. Initial coverage is normalized and bounded; rate vanishes after exhaustion. Rate-coefficient units depend on the coverage convention; inverse seconds here applies to dimensionless normalized coverage, not an unqualified physical surface-density convention.
- `kinetics._fit_information_criteria`: Gaussian unknown residual variance; parameter count includes that variance plus fitted mean-model parameters. Common likelihood constants are omitted. AICc correction is approximate for constrained nonlinear fits. Use identical observations and error assumptions; a high relative weight is not a probability of a mechanism. Global normalized-residual criteria need a separate error-model audit.
- `kinetics_uncertainty`: estimate reference residual sigma with mean-model degrees of freedom; generate identical synthetic observations for every requested competitor in a replicate. Withhold the ranking if any competitor fails. Retain per-model success counts and every completed replicate record. Noise correlations, model uncertainty, baseline drift and calibration uncertainty are excluded.

The CLI reconstructs a linear kinetic temperature coordinate from acquisition time and fitted beta. A quantified measured-versus-reconstructed ramp check is still a release gate. Do not use this mode for holds/cooling/nonlinear ramps merely because the optimizer returns a result.

Scientific context: [Schmid, Parkinson and Diebold, TPD analysis](https://doi.org/10.1021/acsphyschemau.2c00031) discusses the limitations of assumed kinetic laws and prefactors. The statistical parameter-count convention follows [R's log-likelihood documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/help/logLik.lm.html). Neither reference validates this software implementation.

## Release blockers

Wrong or ambiguous units; silent source/output loss; results paired with incorrect settings; misleading physical or uncertainty labels; omitted fit failures; irreproducible core results; failure to import the documented examples; unresponsive cancellation or orphan calculation processes; missing clean-Windows acceptance. Any unresolved blocker prevents a public stable release.

## Independent review still required

No independent human scientific sign-off, real-instrument validation, interval-coverage report, representative usability study or clean-machine acceptance is claimed. See the checkpoint ledger for explicit remaining work.
