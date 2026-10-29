# PTCDA/Au(111): raw-data acquisition and conditional model challenge

## Sources and rights

Ruiz, Wagner, Maaß, Arefi, Stremlau, Tegeder, Tautz and Tkatchenko (2023),
*Accurate quantification of the stability of the perylene-tetracarboxylic dianhydride on Au(111) molecule–surface interface*, Communications Chemistry 6, 136.
Article: https://doi.org/10.1038/s42004-023-00925-2
Data: https://doi.org/10.26165/JUELICH-DATA/HQXCXC (version 2.1).
The repository landing page explicitly identifies CC-BY-4.0:
https://creativecommons.org/licenses/by/4.0/ . Attribute the original authors
above when reusing their data. This directory's `source.zip` is the unchanged
original TPD archive (file ID 11413); its SHA-256 matches the deposited checksum.
The archive spelling “mesurements” is original. Newly derived inventory and
conditional fits are changes made for TPD Spectra Studio's assessment; the
original researchers did not perform or endorse these fits.

## Scope and protocol

The article reports molecular PTCDA/Au(111), QMS mass 124, and a 1 K/s ramp.
It describes coverage-dependent first-order submonolayer desorption and reports
1.74 ± 0.10 eV as an extrapolation of complete-analysis energies to zero coverage.
This is **not** a constant-energy whole-trace estimate. Coverage labels have not
been mapped to individual archive filenames. The raw headers do not explicitly
spell out coordinate units; K and seconds are inferred from numeric ranges and
agreement with the published ramp. Detector numbers retain their original scale;
no physical current unit is asserted from the header alone.

`protocol.json` was written before the first fit, after exploratory inspection
of archive structure, temperature ranges and ramp behavior. It is not blind or
preregistered. Every eligible three-column file is considered, without selecting
by energy agreement. The 550–740 K window brackets the relevant approximately
680–720 K peaks and avoids acquisition startup and later cooling/holds. For each
file require >=100 points, coverage of the window within 2 K, strictly increasing
measured time and temperature, maximum anchored 1 K/s discrepancy <=2 K, and both
10-point endpoint means <=15% of the observed dynamic range above its minimum.
These are engineering suitability screens, not calibrated uncertainty estimates.
No temperature sorting, smoothing, digitization, resampling or replacement of
measured time is applied. Exclusions and hashes are retained for all files.

Selected spectra use the existing first-order normalized-coverage PW fitter,
with free energy, prefactor and positive signal scale. Compare constant-baseline
and zero-baseline fits at three initial prefactors (1e12, 1e16, 1e20 /s), initial
energy 2 eV and maximum 300 evaluations. Bounds remain the existing fitter's
0.05–8 eV and log10(prefactor) 3–30. NRMSE divides RMSE by the selected trace's
signal range. Small residuals or optimizer success are not acceptance criteria
for energy reproduction. Predictions are evaluated against measured temperature
assuming the published constant ramp; this screen does not measure calibration.

## Reproduce

From the repository root:

```sh
python scripts/experimental_ptcda_check.py
```

The script checks the original ZIP hash, inventories every file, and writes full
fit records. It uses the numerical source at the commit in `provenance.json`.
The source archive includes all measurements, including excluded acquisitions;
none is silently replaced with synthetic data. This evidence advances external
data acquisition and baseline/initialization sensitivity. A commensurate energy
comparison still requires coverage mapping and a coverage-dependent complete
analysis or a justified constant-energy reference. No confidence coverage,
external adoption, or general experimental validation is established.

## Observed outcome

All 95 original files were inventoried; 73 passed the fixed screens and 22 were
excluded (7 channel-mapping, 9 interval, 3 endpoint and 3 ramp exclusions).
All 438 conditional fits reported optimizer success. Of these, 201 had prefactor
index 1 flagged near its upper bound by the fitter's existing diagnostics.
NRMSE ranged from 0.03023 to 0.16638; fitted energies ranged from 0.6284 to
4.3563 eV. Across traces, the largest energy change between best-of-three
constant-baseline and zero-baseline fits was 2.9891 eV. These are descriptions of
conditional outputs, not experimental energy uncertainty. Best-of-three means
lowest residual on the same observations within each baseline hypothesis.
All individual records and diagnostic flags are in `fits.json.gz`;
`summary.json` gives counts and ranges. No failed fits were discarded.

The main lesson is that convergence and an apparently small residual can coexist
with bounds and baseline dependence. Neither this disagreement nor proximity of
any fitted value to 1.74 eV establishes a quantitative comparison to the published
zero-coverage intercept. Heating-rate and fit-window sensitivity, source-trace
coverage assignments, calibrated units, and an independent domain review remain
unfinished. Do not tune these settings to recover the published number.

## Coverage mapping follow-up

[The completed investigation](COVERAGE_MAPPING_REVIEW.md) found no verified
raw-filename-to-coverage or saturation-reference mapping in the inspected
primary sources. All 95 headers and their detector scales are indexed in
`metadata_inventory.csv`. Header-aware parsing preserves every frozen fit
window exactly, so no prior fits were repeated. This source remains a model
challenge; a comparable energy reference is still required.
