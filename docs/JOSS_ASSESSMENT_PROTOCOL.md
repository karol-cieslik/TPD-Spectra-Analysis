# Bounded JOSS numerical assessment protocol

Specified before running the new assessment on 28 October 2026.

## Scope and decisions

No new physical-method or calibrated-confidence-interval claim is made. The
publication scope is constant-ramp model-dependent analysis and conditional
Monte Carlo stability. Existing independent reference tests are retained.

Run `python -m scripts.joss_assessment --output validation/joss` from the root.

1. Independently integrate the Arrhenius factor by adaptive quadrature and use
   the separable population solution at orders 0, .5, 1, 1.5, 2, 2.5 and beta
   .2, 1, 5 K/s, at 141 and 281 points over 80–360 Celsius. E=.9 eV,
   nu=1e10, initial normalized population .8. Maximum absolute population
   difference must be <=2e-6, reusing the existing reference-test tolerance.
   This is a bounded numerical tolerance, not an experimental energy accuracy.
2. Generate an independent first-order signal at E=1.1 eV, nu=1e12, beta=1,
   65 points over 80–340 Celsius and detector scale 1e4. Two cases: iid
   Gaussian noise at 1.5% of the clean peak, and 6% Gaussian noise plus linear
   drift spanning 8% of the peak. Both have offset 2 and data seed 123.
3. Fit the first-order candidate with initial E=1.1, nu=1e12 and
   50 evaluations, without multistart. Refit 200 perturbations for seeds 11,42,73;
   each refit has 50 evaluations and no multistart. Analyze nested prefixes
   of 100 and 200; prefixes share draws and are not independent experiments.
4. Retain every completed candidate record, failed ranking and interval
   suppression. Report parameter percentile endpoint and ranking-frequency
   sensitivity across counts/seeds. The 100-success display floor is not a
   convergence or coverage guarantee. No universal stability cutoff is assumed.
   With one candidate, ranking frequencies are trivial and do not test model
   selection. Multi-candidate ranking convergence remains an open checkpoint.
5. The drift case deliberately violates the fitted-reference iid noise model.
   Apparent stability must not be interpreted as correct physical inference.
   One noisy dataset per case cannot quantify frequentist coverage or bias.

Output includes source baseline, script hash, environment, inputs, initial fits,
per-replicate records and summaries. Wall time is environment-specific and not
a performance claim. Source changes and exact test evidence are recorded in the
checkpoint progress report. Never relabel these signals as experimental data.

## Execution amendment

The first attempted design used two candidates, 81 points and multistart.
Its initial comparison did not return in the available observation period,
before any MC run completed. No statistical result from that attempt is used.
The bounded design above was fixed before its MC outputs were generated.
It narrows the claim to parameter stability and records the uncompleted
multi-candidate design rather than treating it as a success.
