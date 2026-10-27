# Scientific consistency audit: colleague beta

> Historical development snapshot. PRs #19–21 are now merged into main.
> For current beta/download status see [START_HERE](../../START_HERE.md). Original evidence below is preserved.

**Scope:** the source changes proposed in draft PR #20, stacked on PR #19 and the historical `0.11.0b4` candidate. This is a **source/documentation audit**, not a completed Windows-binary acceptance test or experimental validation.

The scientific Help catalog, [worked examples](WORKED_EXAMPLES.md), result role labels and underlying model implementations were compared for agreement. The checks below are deliberately narrow: they establish what the program computes and how it should be described, not whether one fitted mechanism is physically correct.

| User-facing statement | Source or verification | Interpretation / checkpoint |
| --- | --- | --- |
| Temperature entry is °C; the Arrhenius law uses K; heating rate is K/s. | `analysis.py`, `kinetics.py`, `multicomponent.py`; example JSON `beta_K_s`. | Verified. Acquisition calibration and non-linear heating remain outside the current model. |
| Manual simulation inputs are supplied hypotheses, not fitted values. | `workflow_modeling.py:simulate`, `kinetics.simulate_tpd`. | Verified. A plotted match is not a completed inverse fit. |
| Single-state fit uses normalized coverage 1 at the first fitted temperature and an optional constant baseline. | `kinetics.fit_polanyi_wigner`. | Verified; changing the cropped start can change the inferred kinetics. |
| Redhead is a **first-order approximation** with an assumed prefactor. | `analysis.redhead_energy`. | Verified. On the bundled clean first-order example (1.2 eV truth), the selected maximum is 155.0 °C and the formula returns **1.19367 eV** (approximately 0.53% low). |
| Leading-edge slope gives apparent energy, not an identifiable physical prefactor. | `analysis.leading_edge_fit`. | Verified. Over 90–110 °C in the same clean example it gives **1.19183 eV** (approximately 0.68% low); it is a regression-window-dependent estimate. |
| Positive-order Polanyi–Wigner fit optimizes energy, log-prefactor, log-scale, optional constant baseline and optionally order. | `kinetics.fit_polanyi_wigner`. | Verified. A converged solution can still have correlated or non-identifiable parameters. |
| Fixed-zero-order fit treats the depletion edge specially; numerical prefactor and scale are not uniquely identified. | `zero_order.py`; `docs/ZERO_ORDER_FITTING.md`. | Verified. Compatible sampling brackets must **not** be called confidence intervals. |
| Joint 1–3 component fit holds each order, prefactor and initial normalized coverage fixed. | `multicomponent.fit_components`. | Verified. It fits energies and nonnegative scales, with optional common offset and **optional** drift. Help now explicitly calls drift method-dependent, not invariably fitted. |
| Component-count comparison uses only prefixes of entered component rows. | `multicomponent.compare_component_counts`. | Verified. It is not an exhaustive physical state search; count-selection criteria are heuristic when fits become singular. |
| Monte Carlo is Gaussian perturbation around the lowest-AICc usable reference from a current comparison. | `kinetics_uncertainty.run_kinetics_monte_carlo`, `workflow_modeling.py`. | Verified. It is **not** Bayesian MCMC, microscopic kinetic Monte Carlo, or a generator of independent mechanism probabilities. |
| Conditional Monte Carlo ranges use the 2.5th–97.5th percentiles of successful refits; at least 100 successes are required in the GUI. | `kinetics_uncertainty.py`. | Verified. These ranges exclude structural, calibration, heating-rate and residual-correlation uncertainty. The 20-replicate tutorial cannot produce ranges at that threshold. |
| Missing mathematical symbols should not show empty parentheses in Help titles. | `scientific_help.topic_heading`. | Corrected in this audit; symbols are now printed only when nonblank. |

## Numerical reproducibility checkpoint

`tests/test_beta_science_audit.py` checks the clean teaching file and its JSON metadata, numerical first-order Redhead and rising-edge expectations, the fixed assumptions and Monte Carlo role explanations. The rest of the software's existing synthetic regression tests remain the primary implementation tests. These checks **do not** reproduce the Windows graphical workflow.

## Release blockers that documentation cannot resolve

1. Rebuild the Windows executable from the **merged** source after PR #19 and PR #20 are reviewed; the historical `0.11.0b4` download does not contain these Help/UI/documentation changes.
2. Perform hands-on Windows first-run, component fit, Monte Carlo progress/cancel, offline Help, file export and feedback/privacy smoke checks. Capture the actual installer/executable hash and the results.
3. Obtain independent experimental traces with explicit permission and acquisition metadata (temperature/ramp, baseline, detector signal provenance). Compare recovered parameters and residual structures against reference analysis. Synthetic data alone cannot support general physical-parameter accuracy claims.
4. Before a paper or stable release, quantify model misspecification, failure rates, and interval coverage on independent and noisy reference cases, including sensitivity to arbitrary crop boundaries, initial guesses and assumed prefactors.

See also [method status](../METHOD_STATUS.md), [multicomponent assumptions](../MULTICOMPONENT_FITTING.md), [zero-order limitations](../ZERO_ORDER_FITTING.md) and [beta review status](REVIEW_STATUS.md).
