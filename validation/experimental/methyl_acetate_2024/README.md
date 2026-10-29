# Methyl acetate/HOPG: completed leading-edge comparison

**The primary leading-edge result is 42.22 kJ/mol with the declared pre-edge offset, versus the paper's 42.8 +/- 0.7 kJ/mol. Without that offset it is 38.86; the alternate window gives 40.29 and 37.81 respectively.** This is baseline/window-sensitive correspondence, not robust independent recovery. A whole-peak zero-order model does not reproduce the reference.

## Source and attribution

Jack E. Fulker and Wendy A. Brown, *Surface science studies of the coverage dependent adsorption of methyl acetate and methyl propanoate on graphite*, RSC Advances 14 (2024), 35373–35385. [DOI 10.1039/D4RA04466E](https://doi.org/10.1039/D4RA04466E); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11537193/).

Source figures and their derived CSVs/overlays retain **[CC-BY-3.0](https://creativecommons.org/licenses/by/3.0/)** attribution to the authors. The new digitization, plotted fits and annotations are modifications for this assessment; author endorsement is not implied. Code remains under the repository's code licence. Exact source URLs/hashes are retained in the linked screening manifest and `provenance.json`.

The selected spectrum is the explicitly labelled **50 Lm** royal-blue curve in Fig. 4B, dosed at 28 K on HOPG. Fig. 6A has no colour legend, so its colour order was not assumed. Fig. 6C is identified by the paper as a 50 Lm example, with 42.8 +/- 0.7 kJ/mol. Its ordinate includes a relative-coverage correction using the measured multilayer order 0.02 +/- 0.04. Acquisition identity across the two figures is not independently established from raw records. The aggregate table value 43.5 +/- 0.9 is a different reference. Heating is 0.5 +/- 0.01 K/s.

## Extraction, corrections and declared settings

`spectrum.csv` retains 101 of 213 graphical columns; 112 remain blank, including substantial overlap/steep regions. These are correlated raster coordinates, not instrument samples. Intensity has no numeric ticks: normalization uses the curve's visible graphical height, with the panel's lower edge as the display origin. It does not establish a physical background or absolute coverage. No interpolation, smoothing, measured time or absolute prefactor is invented.

An initial colour mask admitted neighbouring 20 Lm pixels. Enlarged-source QA identified this error; the mask was corrected to distinguish the 50 Lm hue by its red-minus-green difference. Tick-stem inspection also corrected the initial axis calibration. The invalid extraction, protocol and exploratory results are retained in `superseded_colour_selection/` and excluded from the accepted comparison. `execution_recovery.json` records an earlier assessment-wrapper field-name error and the subsequent source corrections. Production numerical code was unchanged.

The corrected-input protocol was declared before corrected-input fitting, **after exploratory energies had already been seen**. It is not blinded or independently preregistered. The originally declared windows and model cases were retained, rather than optimized to recover the reference.

Primary leading edge: 120–124 K, 13 recovered positive columns. Sensitivity: 121–125 K, 16 columns. Compare graphical zero with subtraction of the median recovered signal at 112–116 K (0.03346 of graphical height). That median is an assumption, not calibrated instrument background. `leading_edge_fit` performs ln(signal) versus 1/T; this neglects the small published nonzero-order correction and is not an exact reproduction of their estimand. The whole-peak stress test uses 112–145 K with zero/free constant baseline and fixed order zero.

## Retained results

| Spectrum-derived leading edge | No offset | Pre-edge median subtracted |
|---|---:|---:|
| 120–124 K | 38.86 kJ/mol | 42.22 kJ/mol |
| 121–125 K | 37.81 kJ/mol | 40.29 kJ/mol |

The primary offset-subtracted result is about 1.35% below 42.8. The paper's error bar is not a pre-established pass criterion for this digitized approximation. Regression R² is 0.993–0.996; high linearity does not establish an accurate physical energy. Independent NumPy OLS agrees with the software to within 7.32e-13 kJ/mol on the same inputs: a numerical consistency check, not independent experimental evidence.

Four engineering perturbations of axis placement and extracted stroke bounds give 38.16–39.51 kJ/mol for the primary **no-offset** case. They are not a confidence interval and do not cover all missing-column, baseline or colour-selection uncertainty.

The point-sampled whole-peak fits give **12.65 and 18.32 kJ/mol**, NRMSE **0.1681 and 0.1327**, for zero and fitted baseline. Both optimizers complete, but residuals are structured and the energies disagree substantially with the rising-edge reference. Phase contributions, broad trailing shape, missing pixels and model assumptions limit interpretation; no single cause is established. Prefactor/scale remain nonunique as the production diagnostics state. The zero-baseline case also triggers the existing large-residual warning. Absence of that warning in the other case is not evidence of model adequacy.

The separate reconstruction of the published **already coverage-corrected Fig. 6C ordinate** gives **42.63 kJ/mol**. It confirms approximate axis/slope correspondence only. It is not a new raw spectrum or an independent measurement: extracted black symbols can also overlap the authors' dotted fitted line and error bars. Its 92 recovered columns are not 92 independent measurements.

All **11 corrected-input assessment records** are retained: four spectrum leading-edge cases, four engineering perturbations, two whole-peak diagnostics and one transformed-plot reconstruction. No Monte Carlo, coverage-distribution fit, GUI acceptance or statistical coverage claim is made. AI-assisted visual QA is complete; independent human scientific review remains pending. The final assessment supports a cautious literature comparison and exposes sensitivity rather than establishing general software accuracy.

## Reproduction

From the source checkout with NumPy, SciPy, Pillow and Matplotlib:

```sh
python scripts/digitize_methyl_acetate_2024.py
python scripts/experimental_methyl_acetate_check.py
```

These recompute completed work and are for reproduction only. No network is needed. `protocol.json` and input hashes are checked by the assessment; `results.json` retains the settings, software results and source-code hashes. `predictions.csv` includes ordinate labels to separate log/intensity/transformed cases. Original source figures, QA overlay, comparison/residual plot and recursive file hashes are retained. Do not use the superseded pilot as validation evidence.
