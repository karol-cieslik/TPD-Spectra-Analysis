# Scientific reliability roadmap

Development priorities agreed 2026-10-19. This is a planning document, not a statement that these capabilities are implemented or validated.

## Principles
Scientific correctness over feature count. Preserve working functionality, test before merge, document assumptions, do not report unsupported error bars, and distinguish numerical verification from external experimental validation.

## Order
1. **Physical/numerical audit:** units, temperature conversion, prefactor dimensions for non-first-order reactions, kinetic equations, ODE solver convergence, coverage conservation/depletion, baseline and preprocessing artifacts, measured versus constant heating ramps.
2. **Identifiability and uncertainty:** Jacobian rank/conditioning and boundary diagnostics, local covariance only when justified, physically transformed intervals, clear warnings for poorly identified fits.
3. **Synthetic benchmark engine:** zero/first/second/noninteger order, two-state overlap, multiple heating rates, noise, baseline drift, calibration offsets, incorrect model cases. Quantify bias, RMSE, fit failure, interval coverage, parameter correlations, and solver convergence.
4. **Uncertainty robustness:** reproducible bootstrap or parametric Monte Carlo with explicit residual-noise assumptions; heating-rate/temperature calibration sensitivity; fitting-window and baseline sensitivity; distinguish systematic from statistical uncertainty.
5. **Selective physical extensions:** strengthen global multi-rate fitting and initial-coverage series before coverage-dependent energy or distributed-state models; defer coupled kinetics and Bayesian methods until basic validity is established.
6. **Publishable validation:** versioned synthetic benchmarks, reference values, tests, documented limitations and provenance; author-curated digitized literature and real lab spectra as a separate later scientific validation stream.

## Integration rules
Each scientific PR adds tests and updates technical references. GUI work is separate and must consume results through established scientific APIs rather than duplicate calculations. Experimental comparisons should not be claimed until data, metadata, provenance and digitization effects are examined.
