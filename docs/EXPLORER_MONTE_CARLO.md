# Kinetics Explorer and conditional Monte Carlo

Open a spectrum, then select **Kinetics Explorer · experimental**. It uses the raw signal and cleaned temperature. It does not inherit display smoothing or normalization. Select an isolated peak with its leading and trailing sides, enter the justified heating rate, select candidate orders and decide whether to fit a constant baseline. Compare models and inspect every residual, failed start and boundary warning.

Zero, first and second order have fixed orders 0, 1 and 2. Fractional order is a free parameter bounded to 0.2–3; that label does not establish a fractional physical mechanism. Deterministic multiple starts reduce initialization dependence but do not guarantee a global optimum. Fixed-order fits estimate energy, prefactor, detector scale and optionally baseline. Initial guesses are 1 eV/1e13 s⁻¹ plus 0.8 eV/1e10 s⁻¹ and 1.4 eV/1e13 s⁻¹. Maximum evaluations per start: 300. See the source for bounds and numerical tolerances.

After comparison, **Monte Carlo…** uses that exact fitted data/settings snapshot. Changes to inputs, range, baseline, heating rate or selected orders require a new comparison. The reference is the lowest-AICc converged candidate. Before running, review that reference's residuals. Choose a seed and replicate count (1–10000; default 500). Cancellation is checked between numerical fit evaluations and retains only completed replicates.

In the three-stage workflow, **Modeling & Order Identification** has a persistent
Monte Carlo control above the plot. **Run Monte Carlo** shows a progress bar,
completed/total replicates and percentage, elapsed time and an approximate
remaining time once refits begin. The estimate can fluctuate because fitting
cost varies. **Cancel** changes the state to Cancelling until the current
numerical evaluation returns. Calculations use the existing worker thread;
progress and plots update on the GUI thread. Duplicate calculations are blocked.
The input spectrum and previous successful results remain visible. Cancellation
or an error keeps the previous result; partial Monte Carlo output does not replace
it. A successful completion reports successful and failed **individual model
fits**, separately from incomplete **replicate rankings**. These counts differ
when more than one model is requested. Retry after reviewing an error or after
cancellation; use the same seed and settings to reproduce the calculation.

The calculation generates independent Gaussian residual noise around the fitted reference and refits the selected models to each simulated trace. This is parametric Monte Carlo refitting, **not microscopic kinetic Monte Carlo and not Bayesian MCMC**. Replicate fitting uses the reference energy/prefactor as its initial guess, 150 maximum evaluations and no multistart. These choices affect convergence and must be included in interpretation.

A winner is counted only when every requested model converges. Failed/incomplete rankings remain in the denominator; individual successful parameter refits are still counted and retained. For positive-order models the 2.5–97.5 percentile ranges now include each estimated parameter: energy, log-prefactor, signal scale, optional fitted baseline, and free order for the fractional model. Fixed orders are assumptions, so they receive no order interval. Zero order reports an energy range, but not prefactor/scale percentiles because those parameters are non-unique. Ranges are **conditional refit ranges**, not demonstrated 95% confidence intervals, and are withheld below 100 successful refits. This practical minimum is not a guarantee of stability or nominal coverage. Check seed/count sensitivity before scientific use.

Clean synthetic traces can leave almost no meaningful detector noise to estimate. Residuals from a wrong model or a drifting baseline also do not represent iid detector noise. The provided drift/trigonometric example deliberately violates the Gaussian assumption. None of these synthetic files is experimental validation.

**Export results** asks for a parent folder and creates a separate run folder. It writes the original fit snapshot, comparisons, fitted curves/residuals, PNG and SVG figures, seed/noise settings, conditional-range status, all completed replicate records and software identity. Export never reads edited controls as if they were the original fitting settings. Both the full source file hash (when available) and selected array hash support provenance. Reproducibility still depends on retaining the source and software environment.

## Scientific status

The Explorer originated in earlier development branches and was incorporated
into the 0.11.0b3 beta on `main`. Its automated tests cover lifecycle,
settings snapshots, cancellation, exports and accounting for failed fits.
These checks are not a validation of kinetic-order identification or interval
coverage.

Independent experimental comparisons, broader noise/model-misspecification
studies, parameter-recovery and coverage evaluation, and hands-on review of the
packaged application remain necessary before quantitative uncertainty claims.
See [Scientific scope and method status](METHOD_STATUS.md) for current limits.
