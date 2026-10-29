# Ethanol on gold: completed conditional literature comparison

**At the published fixed prefactor, the single-state calculation gives 6435 K versus the reported dominant population at 6450 K (about -0.24%). The production free-prefactor fit gives 7613 K with a free baseline (+18.0%), despite smaller residuals.** This is conditional correspondence, not independent recovery of the published population model or general experimental accuracy.

## Source and rights

Perrero, Vitorino, Congiu, Ugliengo, Rimola and Dulieu (2024), *Binding energies of ethanol and ethylamine on interstellar water ices: synergy between theory and experiments*, PCCP 26, 18205–18222, [DOI 10.1039/D4CP01934B](https://doi.org/10.1039/D4CP01934B). [Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11221575/).

The input is Fig. 7 top-right, experimental black marks for 0.7 ML ethanol on gold. Heating is 0.15 K/s; the reference prefactor is 3.31e18 s^-1. The paper models multiple populations, with more than 80% at 6450 K (53.6 kJ/mol). That dominant energy is not exact single-state ground truth. The red published simulation is excluded from extraction. Fig. 4 is not treated as an independent numerical reference.

**Separate source licence: [CC-BY-NC-3.0](https://creativecommons.org/licenses/by-nc/3.0/).** Copyright remains with the source rights holders. The retained source JPEG, extracted CSV and plots derived from it retain attribution and noncommercial restrictions; the repository's software licence does not replace these terms. New code remains subject to the repository's code licence. Figure extraction, overlays and new model curves are modifications made for this research comparison; the source authors do not endorse the software.

## Frozen settings and extraction

`protocol.json` was written and hashed after literature/figure inspection and extraction QA, before the ethanol fits. This is not a blinded or independently preregistered study. Its hash is recorded in `results.json`.

The raster method retains 292 of 324 columns and leaves 32 blank, including steep/overlapping portions. Coordinates represent black-symbol pixels, not original instrument samples. A 14-pixel ambiguity cutoff, exclusion of legend/frame and achromatic thresholds avoid following the red curve. Threshold sensitivity and stroke width supply engineering bounds, not statistical confidence intervals. No gap interpolation, invented time column, baseline subtraction or smoothing is applied. Symbol overlap and missing-column selection can bias the reconstructed shape; pixel perturbations do not exhaust that uncertainty.

Primary interval: 110–165 K (195 recovered columns). Sensitivity: 120–155 K (115). First-order single-state kinetics, uniform weight per recovered column, zero/free constant baseline. Columns are correlated, so sample count is not an independent observation count. The sampled raster maximum is 142.08 K; the text's approximate 141 K peak is not used to shift the axes. Axis placement allowance is about 0.36 K, separately from the 0.12 K half-pixel width.

## Results

| Window | Baseline | Fixed-prefactor energy (K) | Fixed NRMSE | Production free-prefactor energy (K) | Free NRMSE |
|---|---|---:|---:|---:|---:|
| 110–165 K | Zero | 6435.47 | 0.04628 | 6764.80 | 0.04591 |
| 110–165 K | Fitted | 6434.54 | 0.03647 | 7612.90 | 0.03123 |
| 120–155 K | Zero | 6435.48 | 0.05579 | 6767.30 | 0.05527 |
| 120–155 K | Fitted | 6434.43 | 0.04709 | 7873.78 | 0.03791 |

NRMSE is RMSE divided by the selected observed signal range. It is a descriptive metric, not a pre-established physical acceptance threshold. Residual structure remains, especially near the peak/tail.

The fixed-prefactor calculations use production `simulate_tpd` with an assessment-only energy/scale/baseline profile. The current `fit_polanyi_wigner` API has no fixed-prefactor argument; do not present these results as an existing fixed-prefactor GUI feature. Production fitting optimizes energy, prefactor and scale. Its primary free-baseline prefactor is about 1.61e22 s^-1, rather than the literature TST value. Three prefactor starts (1e12, 1e18, 1e24) lead to closely similar solutions within each setting. That supports numerical consistency, not physical uniqueness.

All 20 declared fits completed: 16 main/window cases plus four engineering pixel/axis perturbations. The latter give 6416.99–6452.07 K at fixed prefactor/free baseline; this range is **not** an uncertainty interval. Fixed energies do not hit the declared search boundaries; production diagnostics report no bound hits. Independent first-order quadrature differs from the production rate by 3.20e-6 relative to its peak, below the declared 2e-5 numerical tolerance. This verifies numerical consistency for this case, not the experimental model.

No Monte Carlo, order ranking, multistate fitting, GUI acceptance or physical confidence-coverage assessment was performed. Production numerical code was unchanged. Human scientific review of extraction and interpretation remains open.

## Files and reproduction

`digitized.csv`, `extraction_quality.json`, `extraction_check.png` and `provenance.json` preserve extraction evidence. `results.json` retains every fit and diagnostics; `predictions.csv` retains observations/perturbations, predictions and residuals. `summary.json` tabulates the retained results. `comparison.png` uses dense model evaluation from saved parameters, with missing columns marked and residuals shown as points. `file_manifest.json` records hashes.

From a source checkout with NumPy, SciPy, Pillow and Matplotlib:

```sh
python scripts/digitize_ethanol_2024.py
python scripts/experimental_ethanol_check.py
python scripts/plot_ethanol_comparison.py
```

The first two commands recompute completed work and are for reproduction only. The final command redraws the comparison without refitting. No network is needed. Future changes should preserve this protocol and these original results rather than tune them to the published answer.
