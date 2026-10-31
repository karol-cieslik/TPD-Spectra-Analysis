# Experimental order and multipeak challenge — 29 October 2026

**Result: the current core runs these bounded comparisons, but reliable experimental order identification and peak separation are not established.** No application code changed. All historical assessments elsewhere remain unchanged. This is not an acceptance pass or independent adoption.

## Source and rights

F. Kruczkiewicz, F. Dulieu, A. V. Ivlev, P. Caselli, B. M. Giuliano, C. Ceccarelli and P. Theulé (2024), *Comprehensive laboratory constraints on thermal desorption of interstellar ice analogues*, A&A 686 A236, https://doi.org/10.1051/0004-6361/202346948. Dataset: Franciele Kruczkiewicz, https://doi.org/10.5281/zenodo.10912815, CC-BY-4.0, https://creativecommons.org/licenses/by/4.0/. Source-derived CSVs and plots retain that attribution/licence separately from the MIT software.

The ZIP was downloaded again and its MD5 matched the deposited `b34951fedd9bbaabfb6589606f0f0bbd`. These are **new traces from an already-used study**, not three new independent publications. Protocols record archive/member hashes. Source bytes and line endings are preserved. Preparation selected intervals and viewed curves before fitting; no blind/preregistered claim. No fitting settings were tuned after the results.

Native K and ML/K were converted to °C and ML/s (`rate × 0.2 K/s`) for the existing Python kinetic functions. There is no measured time axis; no time data or ramp-validation result is invented. Finite selected native points were used, except the explicitly declared adjacent-temperature pooling below. This is direct numerical-core assessment, not importer/GUI/Windows acceptance.

## Cases and results

NRMSE is RMSE divided by the observed signal range on each case's same selected points. Different cases have different ranges and counts. Smaller values indicate better curve approximation, not correct physics.

| Case | Single n=0 | Single n=1 | Single n=2 | Two n=1 states, two starts |
|---|---:|---:|---:|---:|
| Pure NH3, 60–120 K, 255 points | 0.08481 | 0.02226 | 0.05483 | Not run |
| CH3OH in water, file 28, 120–180 K, 532 points | Rejected: incompatible depletion/prefactor/scale bounds | 0.13810 | 0.15619 | 0.34010 / 0.13810 |
| CO in water, file 18, 25–170 K, 1871 unique temperatures | 0.10562 | 0.11130 | 0.12869 | 0.11130 / 0.11130 |

**18 total attempts: 17 returned fits, all reporting numerical success; one zero-order rejection; no timeout.** Thirteen initial attempts are retained in `assessment/`; five separate CO18 follow-up attempts in `separated_assessment/`. The count includes five **source-correspondence-unresolved CO12 pilot** fits, which are excluded from the table and positive validation claims. Twelve of the returned fits belong to the table's three cases.

- **NH3:** first order fits the *whole curve* better despite the article using zero order for the multilayer *leading edge below 87 K*. This is not recovery of the correct order. The native peak is 94.021 K; the article text describes approximately 90 K. Exact figure-to-deposited-trace correspondence has not been established. Table 2 and Fig. 5 also give differing NH3 amounts. Do not claim trace-matched energy reproduction or use the full-peak result as a refutation of the published leading-edge analysis.
- **Overlapping CH3OH:** broad features peak near 138.79 and 157.85 K. One two-state start converges to an effectively flat prediction (R² approximately zero); the other behaves like a single broad peak. Both show identifiability warnings; the flat fit also warns of large residuals. The published discussion of surface/co-desorption is context, not proof that two independent constant-energy states describe this trace. File 28 maps by dataset numbering to Table 2's 90 K deposition series, not the Fig. 6b experiment-27 curve. No independent component-energy or order truth is supplied.
- **Separated CO18:** low-temperature release near 40.97 K and high-temperature release near 155.81 K are visibly distinct, yet both frozen two-state starts miss the low-temperature feature. Residual lag-one correlations are about 0.98–0.999. The small change between two-state starts is **not convergence evidence**: both are poor solutions. Trapped release during water crystallisation is outside a pair of simple independent constant-energy desorption states. These data therefore challenge the model/optimizer; they do not validate unique adsorption energies.

The declared starts were (0.35, 0.50) and (0.45, 0.65) eV with initial prefactor 1e13 and 100 evaluations. They were not designed as favourable low-energy starts for CO's low-temperature feature. These two starts do not exhaust optimization possibilities; failures cannot establish that no useful fit exists. No multistart search, MC, fractional-order recovery or mechanistic probabilities were attempted.

## Source-correspondence correction and follow-up

The first protocol labelled file 12 a separated-peak target based on its binary-CO assignment. Its selected header-labelled CO signal actually has high-temperature structure with no substantial expected low-temperature release (20–60 K maximum is only 0.000467 ML/s, versus overall 0.289154 ML/s). One two-state fit lowers NRMSE from 0.03872 to 0.01061, while the other collapses to a single-state result. That apparent improvement is **quarantined**: channel/trace correspondence is unresolved. Original protocol, all five records, logs and the initial figure remain unchanged; the corrected main `comparison.png` uses CO18 instead. No source error is asserted.

File 18 is the experiment referenced by Fig. 2c and has the expected two-feature morphology. Its 20–170 K input fails a strict monotonic-temperature screen, with reversals below 25 K. The separately frozen `separated_protocol.json` excludes 20–25 K **before fitting**, retains 25–170 K without sorting, and pools nine adjacent repeated-temperature pairs by arithmetic mean, matching the core's duplicate policy. Original `raw/18_binary_CO.csv` and derived `raw/18_binary_CO_adjacent_mean.csv` are both retained. The first 25 K screen also failed because of these duplicates; it produced no kinetic result. Missing low-temperature coordinates are not interpolated or claimed recovered.

`assessment/input_qa.json` records 127 incomplete trailing NH3 rows excluded at parsing; no selected point is silently synthesized. Other initial traces had no incomplete rows. The selected primary inputs are strictly increasing. All transformations are assessment-specific, not a new importer feature.

## Evidence and reproduction

Verification: 24 focused kinetic/zero-order/global tests passed; all 17 saved curves passed independent arithmetic checks; every archived member hash was checked. No full-suite or Windows test was run in this batch. Archive SHA256: `d2e6439b3fae1b4216950b443ecad0765861f536856b053c3bc924be60374a6a`.

The full evidence is stored losslessly in `evidence.tar.gz` to keep the repository compact. Extract it once into this directory before inspection/reproduction (it creates the case files, not application files):

```sh
tar -xzf validation/experimental/multipeak_ice_2024/evidence.tar.gz -C validation/experimental/multipeak_ice_2024
```

Extract only into a fresh checkout/copy, not over modified assessment files. `evidence_manifest.json` inside the archive records every member SHA256. Inspect `comparison.png`, then protocols, raw files, every fit JSON, predicted curves/residuals and rejection logs. `verification.json` independently recomputes saved residual arithmetic and NRMSE for all 17 returned records without calling a fitter. NaN/infinity diagnostics are serialized as JSON null; null is not evidence of a finite/well-conditioned Jacobian. `runner_at_execution.py` files and environment records preserve execution provenance. The reusable runner later gained only a protocol-selection option; existing fits were not repeated.

To reproduce into **new** folders, from the source checkout:

```sh
python -m scripts.experimental_multipeak_check --output output/ice-primary-new
python -m scripts.experimental_multipeak_check --protocol validation/experimental/multipeak_ice_2024/separated_protocol.json --output output/ice-separated-new
```

The runner refuses an existing output directory. Each fit has a 60-second wall limit. Native and assessment information criteria are retained as working numerical diagnostics only: residuals are strongly correlated, ordinary iid likelihood assumptions are unverified, and the zero-order edge model is nonregular. Assessment AICc counts mean parameters only; it is not a calibrated probability or the same convention as production's unknown-variance count. Conclusions here use curves, NRMSE and warnings, not AICc selection probabilities.

## What this leaves open

Human scientific assessment of source correspondence, assumptions, residuals and warning visibility; clean-Windows execution; a commensurate positive experimental energy comparison; genuine research use; author metadata/AI disclosure; and public-history eligibility. These tests add concrete negative/limitation evidence. They do not close those gates.

A second independent publication lead is *Isolation of Peaks in TDS Spectra of Deuterium from Ion Irradiated Tungsten*, https://doi.org/10.1016/j.phpro.2015.08.318, whose abstract reports three overlapping peaks. It is **screened only, not acquired or tested here**. Diffusion/trapping kinetics must be checked before fitting a surface-only model; second-order experimental validation is still open. Fitting n=2 to the present controls does not create a known second-order reference.
