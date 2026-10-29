# Pure methyl mercaptan: completed bounded assessment

**The declared leading-edge settings give 4849–5492 K, while ideal zero-order whole-peak fits give 2496–2717 K with structured residuals. This is not a robust reproduction of the paper's TST-conditioned recommendation, 4610 +/- 110 K.** These are different estimands and the comparison does not establish a software error or a physical cause for disagreement.

## Input and reference

Suchitra Narayanan, Elettra L. Piacentino, Karin I. Öberg and Mahesh Rajappan (2025), *Thermal Desorption Kinetics, Binding Energies, and Entrapment of Methyl Mercaptan Ices*. [Article DOI](https://doi.org/10.3847/1538-4357/adc7b6). The assessed source is [arXiv:2504.01102v1](https://arxiv.org/html/2504.01102v1), Fig. 2, rather than the publisher final-layout PDF. Source and derived data retain [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) attribution; new fits and plots are modifications, with no author endorsement implied.

The existing [digitized input](../../digitized/mesh_2025/digitized.csv) is the light-pink pure-ice curve labelled 11 +/- 2.1 ML. It retains 908 recovered columns and 16 gaps. Its source image, axes, extraction bounds and overlay remain in `validation/digitized/mesh_2025/`; extraction was **not repeated**. The published heating rate is converted from 2 K/min to 0.0333333 K/s. No measured time channel, original calibrated raw trace or surface-area conversion is invented.

The recommended pure-ice energy uses a TST prefactor of 5.2e17 ML/s. We do not reconstruct that absolute fit from the figure axis alone (printed 10^15 molecules/K). The paper also describes energy/prefactor degeneracy. Absolute temperature accuracy is reported as about 2 K; the much smaller pixel allowance is not a substitute for experimental calibration uncertainty.

## Declared protocol

`protocol.json` was written and hashed after primary-source review and existing extraction QA, before these MeSH fits. This is not blinded or independently preregistered. Input hash checking canonicalizes line endings only, allowing cross-platform reproduction without modifying the retained source file.

Leading edges: 100–104 K primary and 99–103 K sensitivity, each with 37 recovered positive columns. Compare zero offset and subtraction of the median 80–90 K figure level (0.01362 in printed signal units). The latter is an assumed pre-edge background, not a calibrated correction. Production `leading_edge_fit` fits ln(signal) against 1/T. Its slope is an apparent energy, with a free intercept; it is not a fixed-TST-prefactor estimate.

Whole-peak diagnostics use 90–120 K and 95–115 K, each with zero/free constant baseline. Production `fit_polanyi_wigner` uses fixed order zero. Missing coordinates remain omitted, with no interpolation or smoothing; every recovered raster column has equal weight. Columns are correlated rather than independent measurements. The software normalizes initial coverage internally; returned zero-order prefactor/scale representatives are not absolute ML/s estimates for the original ice.

## Results

| Leading-edge window | Zero offset | Pre-edge median subtracted |
|---|---:|---:|
| 100–104 K | 4849.26 K | 5014.37 K |
| 99–103 K | 5212.27 K | 5491.68 K |

Regression R² ranges from 0.9890 to 0.9952. Independent NumPy OLS agrees on the same inputs to within 2.82e-11 K. High linearity and numerical consistency do not establish a unique or accurate physical energy. Regression confidence intervals retained in the raw API result represent scatter only and are not interpreted as physical confidence coverage.

| Whole-peak window | Baseline | Energy (K) | NRMSE |
|---|---|---:|---:|
| 90–120 K | Zero | 2516.91 | 0.12117 |
| 90–120 K | Fitted | 2647.70 | 0.11987 |
| 95–115 K | Zero | 2496.49 | 0.15180 |
| 95–115 K | Fitted | 2716.90 | 0.14880 |

All four optimizers complete, with no reported energy bound hit, but the broad rounded peak does not follow the ideal abrupt-depletion model. The zero-baseline sensitivity case triggers the existing large-residual warning. The other cases still have structured residuals; absence of that warning is not evidence of model adequacy. Depletion/prefactor brackets are conditional on the fitted energy and sampled edge, not confidence intervals. No single response, calibration or microscopic mechanism is identified as the cause.

Four primary zero-baseline engineering perturbations of pixel/threshold bounds and axis placement give 4161–5988 K. These are scenarios, not a confidence interval, and do not include every experimental or missing-data uncertainty. None requires omitting nonpositive signal in its selected interval. They show why small point-estimate differences alone cannot establish accuracy.

All **12 assessment records** are retained: four leading edges, four whole-peak fits and four engineering perturbations. No Monte Carlo, simultaneous coverage-series fit or TST calculation was added. Production code and prior assessments were unchanged. The original-source QA and new plot were inspected with AI assistance; independent human scientific review remains pending.

## Files and reproduction

`results.json` records every result, diagnostics, protocol/input/code hashes and runtime versions. `predictions.csv` labels intensity and log-signal ordinates. `checkpoint.json` preserves progressive completed records. `summary.json`, `comparison.png`, `visual_review.json` and `file_manifest.json` provide the bounded interpretation and provenance checks.

```sh
python scripts/experimental_mesh_check.py
```

Run from the source checkout with NumPy, SciPy and Matplotlib. This recomputes completed fits and is supplied for reproduction only; no network or redigitization is needed. No new validation success is asserted by this case.
