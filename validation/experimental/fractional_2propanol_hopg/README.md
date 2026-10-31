# 2-propanol/HOPG Figure 2A: digitized monolayer coverage series

This case has progressed from a screened candidate to a figure-derived
experimental challenge. It is **not** a raw-data validation or an independent
energy-validation pass.

## Source and reuse

S. A. Ayling, D. J. Burke, T. L. Salter, and W. A. Brown, “Desorption and
crystallisation of binary 2-propanol and water ices adsorbed on graphite,”
*RSC Advances* **7** (2017), 51621–51631, DOI
[10.1039/C7RA10410C](https://doi.org/10.1039/C7RA10410C), Fig. 2A. The article
states a CC BY 3.0 Unported licence. The published version is also deposited at
the University of Sussex Figshare as item [23450411](https://sussex.figshare.com/articles/journal_contribution/Desorption_and_crystallisation_of_binary_2-propanol_and_water_ices_adsorbed_on_graphite/23450411),
file `IPA_published.pdf`; that record labels the item CC BY 4.0.

`source_figure.png` is the Figure 2 raster embedded in that deposited PDF. Its
SHA-256 is `4c44adc3e07490412a091b77dd19490ed6cba8ca210d6ad5776b83da70de4f78`.
The downloaded PDF's SHA-256 was
`079056826b24d83a98a608a06715526ea2d360e512571f3271447f3ddffe7394`.
Attribution: **Adapted by digitization from Ayling et al., RSC Adv. 7,
51621–51631 (2017), Fig. 2A. © The Royal Society of Chemistry 2017. Licensed
under CC BY 3.0.** The published source image is included here under that
licence. No author raw-data files are included.

## What was digitized

Only the four low-exposure traces in Fig. 2A were digitized: 1, 2, 5, and
10 L\(_m\). The paper reports deposition at 26 K and a 0.5 K s\(^{-1}\) ramp.
The x-axis was calibrated from 120 to 170 K. The y-axis has no numerical ticks,
so pixel height above the shared zero line is retained as a common arbitrary
signal unit. Each trace has 879 temperature samples; these are correlated
figure pixels, not 879 independent measurements.

The paper reports a monolayer order of 1.23 ± 0.03, an average monolayer
desorption energy of 46.6 ± 3.7 kJ mol\(^{-1}\), and
\(\log_{10}(\nu / \mathrm{s}^{-1})=12.9\pm0.3\). Its order method is the mean
slope of \(\ln I(T)\) versus \(\ln\theta_{rel}\) over a range of fixed
temperatures; \(\theta_{rel}\) is the corresponding integrated TPD intensity.
The article does not specify the fixed-temperature interval in the reported
text.

## Bounded result

The declared 137–145 K reconstruction, sampled every 0.5 K and using the
full 120–170 K plotted-area integral, gives an average order of **1.14 ± 0.05**
(descriptive 2 SEM across the 17 fixed-temperature slopes). Those slopes and
the underlying raster pixels are correlated, so this spread is not an
independent-sample confidence interval. Moving the common zero-line
calibration by ±1 pixel changes that estimate to 1.113–1.166. This does not
reproduce the paper's 1.23 ± 0.03 under the declared reconstruction. Since
the paper's fixed-temperature interval is unspecified and the input is a
raster figure with an uncalibrated y-axis, the difference is a documented
method/reconstruction discrepancy, not evidence that either value is wrong.

The existing single-trace Polanyi–Wigner fitter was also run separately on
each digitized curve at 0.5 K s\(^{-1}\). With fixed order 1.23, NRMSE was lower
than for fixed first order on all four traces (0.088–0.111 versus
0.106–0.132). Free-order fits reached the upper bound of 3.0 for the 1, 2, and
5 L\(_m\) traces; the 10 L\(_m\) fit returned 2.393. These free-order results
are not estimates of the paper's coverage-series slope. The software fits
each trace with normalized initial coverage and a free signal scale, whereas
the source method compares intensities across integrated coverages. Its
single-state, constant-energy assumptions also omit the source's reported
coverage-dependent energy and islanding behavior. The conditional fit
energies and prefactors must not be presented as recovered physical values.

## Reproduction

From the repository root, run:

```bash
python scripts/experimental_2propanol_hopg_check.py
```

The script reads `source_figure.png` and regenerates
`digitized_monolayer.csv` and `results.json`. It records the pixel calibration,
fixed-temperature slopes, source comparison, and separate production-fitter
results. The settings are frozen in `protocol.json`; do not adjust the primary
temperature window after inspecting the result. Human review of the trace
assignment and scientific interpretation remains necessary before using this
as publication evidence.
