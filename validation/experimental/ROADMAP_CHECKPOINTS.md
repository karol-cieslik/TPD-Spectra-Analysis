# Experimental-validation and fitting roadmap checkpoints

Use this file to keep completed evidence separate from blocked work. A
checkpoint is complete only when its artifact and interpretation are recorded.
Do not turn a source lead or a numerical optimizer result into experimental
validation.

| Gate | Status | Checkpoint / artifact | Decision |
|---|---|---|---|
| A. Prior validation ledger | Complete | [Experimental assessment](EXPERIMENTAL_VALIDATION_AND_ALGORITHM_ASSESSMENT.md) and study-specific records | Preserve positive and negative results with their source/model limits. |
| B. Fractional candidate: methanol/HOPG | Blocked on trace quality | [Methanol admission record](methanol_hopg_2005/README.md); thesis scan inspected | No digitized arrays admitted: faded lines, bleed-through, and 200/300 L caption-label conflict. Seek a clean author/repository copy before fitting. |
| C. Variable projection: controlled comparison | Complete, no adoption | [Ethanol single-start](ethanol_2024/variable_projection_comparison.json), [six-start results](ethanol_2024/variable_projection_multistart.json), [D₂O stress result](../../digitized/water_2018/variable_projection_stress.json) | Same optima as current fitter; all ethanol starts converged already; variable projection was slower. Keep experimental/opt-in, do not replace default. |
| D. E–ν profile diagnostic | Prototype complete; statistical calibration open | [Profile CSV](ethanol_2024/energy_prefactor_profile.csv), [summary](ethanol_2024/energy_prefactor_profile_summary.json), [plot](ethanol_2024/energy_prefactor_profile.png) | Reveals conditional parameter tradeoff. No confidence interval or calibrated uncertainty claim. |
| E. Profile implementation recovery | Complete on exact synthetic cases | [Recovery record](../synthetic/profile_recovery_checkpoint.json) | Recovered known E, ν, scale and constant baseline for n=1.23 and n=2 synthetic signals. Numerical verification only. |
| F. Baseline-drift stress and optional slope | Synthetic recovery complete; one empirical sensitivity comparison | [Synthetic drift stress](../synthetic/profile_linear_drift_stress.json), [synthetic degree check](../synthetic/baseline_degree_checkpoint.json), [ethanol/Au comparison](ethanol_2024/baseline_degree_comparison.json) | At 4.3% synthetic drift the constant-baseline fit shifted E by 0.01 eV. On ethanol/Au, adding a slope modestly lowered NRMSE and shifted E by only 0.00040 eV; neither proves physical accuracy. |
| G. Additional order-diverse series | Four sources screened; trace admission pending | [Ethanol/HOPG](fractional_ethanol_hopg_2008/README.md), [2-propanol/HOPG](fractional_2propanol_hopg/README.md), [PAHs/graphite](fractional_pah_graphite/README.md), [O₂/Ag(111)](fractional_o2_ag111/README.md) | Alcohol papers offer within-study order classes; PAHs test islanding by molecular size; O₂/Ag(111) adds direct morphology evidence. None has been digitized/fitted here. |
| H. Distribution-of-energies model | Later | Separate nonnegative, regularized inversion; needs synthetic known distributions and a suitable multi-ramp experimental source. | No current product integration until resolution/regularization sensitivity is demonstrated. |
| I. Automatic peak proposal | Deferred | Candidate generation plus human review only after false-positive calibration on broad peaks, shoulders, noise and known overlaps. | No unattended physical peak-count assignments. |

## Numerical checkpoints completed this iteration

1. The six-start ethanol/Au comparison used the same frozen 110–165 K
   digitized window, first-order model, 0.15 K/s ramp and fitted constant
   baseline. Both fitters converged for all six starts. The current fitter's
   NRMSE stayed at approximately 0.0312311; the profile prototype matched it
   to numerical precision and was slower in every recorded run.
2. The D₂O/Fe₃O₄(111) comparison used all 644 recovered points from the existing
   figure-derived trace at 3 K/s. Both methods converged to the same result,
   but both placed the prefactor at its 10³ s⁻¹ lower bound and retained NRMSE
   approximately 0.1057. The source describes a multiple-population process;
   this is an optimizer/model-scope stress check, not a single-state validation.
3. The ethanol/Au energy–prefactor profile used 49 fixed energies from 0.60 to
   0.72 eV and profiled log₁₀ν plus linear scale and constant offset. Its best
   grid point was 0.655 eV and log₁₀ν≈22.17. The E–ν ridge is visible. The
   summary's 1% RSS range is purely descriptive and is not a confidence
   interval because digitization errors are correlated and lack calibrated
   pointwise variances.
4. Exact synthetic profile recovery succeeded for near-first-order fractional
   n=1.23 and second-order n=2 traces with known E, ν, scale and baseline. A
   controlled linear-drift challenge shifted the fitted energy by 0.01 eV when
   drift equaled 4.3% of signal range and only a constant baseline was allowed.
   An optional linear baseline recovered the generating curve in that exact
   synthetic case; this does not prove it is physically appropriate on real
   spectra.

## Immediate next actions

1. Keep the sloped-baseline option research-only until it is evaluated on more
   experimental traces with frozen windows and residual review. The one ethanol
   result lowered NRMSE modestly but does not establish a physical background.
2. Prioritize source-data recovery in this order: (a) O₂/Ag(111) LEEM/TPD
   supplementary arrays, if available; (b) author/institutional data for
   coronene/ovalene; (c) authorized alcohol figure files. The morphology dataset
   is more informative for mechanism, while the PAH and alcohol series provide
   cleaner order-class comparisons.
3. Identify and acquire a multi-heating-rate experimental series before
   prototyping energy-distribution inversion. Keep it separate from the product
   and defer broad automatic peak decomposition.
