# Bounded first/second-order ranking study

This extends the parameter-only assessment without rerunning it. The two
recorded 65-point inputs are reused unchanged. The protocol in
`scripts/joss_ranking_assessment.py` was fixed before this study: two candidate
orders, initial energy 1.1 eV and prefactor 1e12, no multistart, 50 evaluations,
100 conditional refits per seed, seeds 11/42/73 and nested prefixes 50/100.
Each run is isolated in a subprocess with a 120-second wall limit. Timeouts
and execution failures are distinct from per-model numerical fitting failures.

`protocol.json` retains script/input hashes and the environment. `summary.json`
retains counts for every scheduled run. Compressed JSON records retain the
individual model fits, AICc values, warnings and full replicate accounting.
Successful complete rankings, incomplete rankings, model successes and planned
runs must not be conflated. Do not turn missing or timed-out runs into zero
probabilities or successful comparisons.

Reproduce from the source root, into a new directory:

```bash
python -m scripts.joss_ranking_assessment --output output/ranking-reproduction
```

## Initialization profile

The five separate, ten-second-limited profiling runs in
`initialization_profile.json` all returned in about 1.2–1.7 seconds, including
four initializations of the second-order fit. This did not reproduce the old
slow 81-point/multistart comparison. A converged second-order fit nevertheless
changed from about 1.635 eV to 3.181 eV for the high-energy initial guess.
Optimizer convergence therefore does not establish a unique optimum. No
production solver change is justified merely by the unexplained old slowdown.

The 81-point, 100-evaluation multistart replay in `old_design_profile.json`
also completed (first order about 1.6 s, second order about 3.2 s). It returned
a first-order energy of 1.464739 eV for the 1.1 eV synthetic input. This is
an optimization/recovery limitation requiring separate investigation, not a
physical inference. The ranking study's initialization uses the known input
energy/prefactor; it is a favorable, conditional test and is not blind recovery.

## Interpretation limits

This evaluates ranking stability conditional on each fitted reference and iid
Gaussian perturbation model. It does not measure how often the physical order
is correctly recovered across independent experiments. In particular, the
drift case's reference refits do not reproduce unmodeled systematic drift;
stable rankings can coexist with model misspecification. A 100-replicate run
and three seeds do not establish universal convergence, all-order performance,
mechanism probabilities or confidence coverage. Nested prefixes are correlated.

## Windows portability correction

The original PR's scientific CI passed; Windows reported 361 passing tests and
two failures before packaging. The experimental CSV hash changed under CRLF
checkout, and the Help-copy test used a default cp1252 text decoder. The fix
sets LF checkout for the hash-tracked data and explicitly reads UTF-8 in that
test. Targeted checks passed (34 passed, two display skips); a Windows-style
Git checkout-filter test preserved the source CSV bytes. Windows CI remains
the authority for the rebuilt package, not these Linux checks.

## Completed results

| Case | Seed | Complete / requested | First / second wins | Failed rankings |
|---|---:|---:|---:|---:|
| matched_gaussian | 11 | 100 / 100 | 100 / 0 | 0 |
| matched_gaussian | 42 | 100 / 100 | 100 / 0 | 0 |
| matched_gaussian | 73 | 100 / 100 | 100 / 0 | 0 |
| baseline_drift_mismatch | 11 | 100 / 100 | 100 / 0 | 0 |
| baseline_drift_mismatch | 42 | 100 / 100 | 100 / 0 | 0 |
| baseline_drift_mismatch | 73 | 100 / 100 | 99 / 1 | 0 |

All 600 two-model replicates completed (1200 individual model fits), with
zero failed rankings and no seed-run timeouts. First order won all complete
rankings in both 50/100 nested prefixes for every seed. This establishes
observed stability for this limited first/second candidate set and favorable
initialization only. It does not establish all-order convergence, mechanism
probabilities, blind energy recovery or experimental validity.
