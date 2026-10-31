# Methanol/HOPG: fractional-order coverage-series benchmark candidate

**Status: source review and visual page inspection complete; quantitative digitization and fitting pending.**

## Source and published values

Bolina, Wolff & Brown, “Reflection absorption infrared spectroscopy and
temperature programmed desorption investigations of the interaction of
methanol with a graphite surface,” *J. Chem. Phys.* 122, 044713 (2005), DOI
[10.1063/1.1839554](https://doi.org/10.1063/1.1839554). The journal PDF is hosted
by [UCL](https://www.chem.ucl.ac.uk/astrosurf/pubs/JChemPhys_122_044713-1.pdf).
The experiment reports β = 0.5 K/s and TPD at methanol dosing temperatures of
105 K and 130 K.

The article's Table II reports orders at fixed temperatures 140, 142.5 and
145 K. Peak A (monolayer) gives 1.28, 1.09 and 1.31, respectively. Peak B
(multilayer) gives 0.17, 0.46 and 0.41. Their means are 1.23 and 0.35,
consistent with the thesis values 1.23 ± 0.14 and 0.35 ± 0.21. This arithmetic
cross-check is not a reproduction of the underlying regression or a Studio
fit.

The freely accessible UCL thesis chapter “Methanol Adsorption on HOPG: A TPD
Study” includes Fig. 6.2–6.5, peak assignment discussion and the order table.
The low-dose series (2, 3, 5, 7, 10, 15 L) separates a monolayer peak from an
emerging lower-temperature multilayer peak. The high-dose series (15, 20, 50,
100, 300 L) increasingly overlaps those species and develops a higher
temperature feature associated with phase change. Both the non-integer
multilayer order and overlap/phase behavior make this a high-value stress
dataset.

## Current admission limit

The source PDF is a low-quality scanned copy. Its plot lines are faded, with
visible bleed-through and overlap; the 300 L trace label also conflicts with
the Fig. 6.3 caption, which says 200 L. The page images are now accessible, but
that does not make the graph sufficiently reliable for unattended color
extraction. No numeric trace arrays or fits have been admitted. Do not count
the published order values as a software result. A quantitative result requires
an independently checked manual or semi-automatic trace extraction with
uncertainty bounds and a frozen mapping for each trace.

## Frozen digitization and fitting plan

1. Digitize figures 6.2 and 6.3 for the 100 K dosing series. Preserve original
   trace samples where line separation allows; record ambiguous/overlapped
   segments as uncertain or exclude them under a written rule.
2. Record axis calibration, image/page checksum, color/line assignment,
   digitizer tolerance, temperature units, signal units, exposure labels and
   the stated 0.5 K/s ramp. Do not infer initial coverage directly from L.
3. Analyze Peak A at low exposures, Peak B in the partially separated region,
   then the full 15 L overlapped trace as a deliberate model-mismatch case.
4. Compare fixed first order, fixed second order, free order, and—only for
   overlapping regions—the documented multi-component fitter. Freeze baseline,
   intervals and parameter bounds before seeing outcomes.
5. Compare software estimates with the paper's fixed-temperature log-intensity
   versus log-relative-coverage order regression. They are different
   estimators; retain residuals, parameter profiles, sensitivity to digitized
   points and all failures.

See the consolidated [experimental validation and algorithm assessment](../EXPERIMENTAL_VALIDATION_AND_ALGORITHM_ASSESSMENT.md).
