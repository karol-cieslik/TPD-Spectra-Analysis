# Post-fix conditional Monte Carlo reassessment

This is a new assessment of the peak-informed initialization correction at
source commit 39c9d7a96d00e40ca5d7ee777f89ea37155e3d7b. Local kinetics.py was
verified against that commit's Git blob before execution. Earlier parameter
and ranking datasets remain untouched as historical pre-correction evidence.

## Protocol

The existing matched-Gaussian and baseline-drift input CSVs are reused without
regeneration. For each case, seeds 11/42/73 each request 200 conditional
replicates comparing first and second orders. Reference comparisons use the
same favorable E=1.1 eV, nu=1e12 starts as the earlier controlled assessment,
50 evaluations and no multistart. Refits use the existing reference-based
initialization. Nested 50/100/200 prefixes assess observed count sensitivity.
These are correlated prefixes, not independent experiments.

Each seed runs in an isolated process with a 300-second wall deadline; at most
three processes run concurrently. Scheduled runs, timeouts, execution errors,
completed replicates and incomplete candidate rankings are reported separately.
The numerical-reference matrix and experimental input checks are not rerun:
the task here is reassessment of conditional Monte Carlo after initialization
changed. Provenance includes source/script/input hashes and environment.

Reproduce into a new directory from the source root:

```bash
python -m scripts.joss_postfix_assessment --output output/postfix-reproduction
```

## Evidence boundaries

This is a bounded two-candidate stability comparison, not blind energy recovery,
all-order convergence, frequentist confidence coverage, or physical mechanism
probabilities. Systematic drift is not restored by drawing iid noise around
an already fitted reference. A consistent ranking can therefore coexist with
model inadequacy. Calibration, baseline, window and reference-model uncertainty
are not exhaustively propagated.

Scientific CI and the full Windows build passed for the source commit above
(runs 40778863524 and 40778863504). They do not replace independent scientific
review or human clean-machine/visual acceptance. Any subsequent evidence-only
commit has its own CI status.

## Completed results

| Case | Seed | First / second wins (200) | First-order energy range (eV) | Max endpoint change from pre-fix (eV) |
|---|---:|---:|---|---:|
| baseline_drift_mismatch | 11 | 199 / 1 | 1.065105–1.228639 | 3.13e-06 |
| baseline_drift_mismatch | 42 | 200 / 0 | 1.067949–1.224237 | 1.79e-06 |
| baseline_drift_mismatch | 73 | 199 / 1 | 1.068257–1.246613 | 2.29e-06 |
| matched_gaussian | 11 | 200 / 0 | 1.075995–1.115492 | 1.04e-07 |
| matched_gaussian | 42 | 200 / 0 | 1.076731–1.112571 | 3.31e-08 |
| matched_gaussian | 73 | 200 / 0 | 1.075874–1.115842 | 9.31e-09 |

All six scheduled runs completed: 1200 replicate comparisons, 2400 model-fit
records, no incomplete rankings and no execution timeouts. First order won all
600 matched-noise rankings and 598/600 drift-case rankings. These fractions are
conditional ranking frequencies, not probabilities of physical mechanisms.
The 200-replicate design detected two drift-case second-order wins; the earlier
100-replicate study had none. This does not by itself isolate whether optimizer
changes or the longer replicate stream caused the difference; compare equal
100-prefixes in comparison.json before attributing causality.

At equal 100-replicate prefixes, drift seed 73 changes from 100/0 to 99/1,
while the other prefixes retain first-order wins throughout. Thus the difference
is not solely the larger replicate count. Separating effects of optimized
reference predictions and candidate local solutions would require a controlled
reference-frozen study; that causal decomposition is not claimed here.
