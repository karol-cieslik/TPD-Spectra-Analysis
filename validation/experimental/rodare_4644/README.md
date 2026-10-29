# External experimental input and negative ramp-screening case

**Attribution:** Alexandra Becker, Holger Lippold, Jing Liu, Michael Hirscher,
Cornelius Fischer (2026), Data files for article: Tritium separation from gaseous
1,2,3H isotopologue mixtures by selective adsorption on Ag-exchanged zeolite type Y.
RODARE, version DOI https://doi.org/10.14278/rodare.4644.
Files licensed CC-BY-4.0: https://creativecommons.org/licenses/by/4.0/.
Related article: https://doi.org/10.1038/s41467-026-75930-9.

Source inspected/downloaded 28 October 2026. Original workbook MD5 was verified
against the repository record. `provenance.json` records full source/CSV hashes.
The CSV contains measured relative time (seconds), measured temperature (K),
and calibrated D2 desorption signal (molecules/s) from worksheet **H2 D2**.
Changes: three columns selected and headers renamed; no digitization, smoothing,
normalization, baseline subtraction or time reconstruction. The source signal
unit is molecules/s; the importer treats its numerical values as a detector
channel and does not verify the original calibration.

The publication discusses a D2 maximum near 92 K in Figure 2a; the deposited
sample maximum is compared with that rounded description. A 1 K comparison band
is a practical rounded-text check chosen after inspecting the source, not a
preregistered blind validation criterion or experimental uncertainty.

Run `python -m scripts.experimental_rodare_check` and inspect `results.json`.
Conversion checks use the original stored numbers as references. The engineering
ramp screen is also evaluated at its documented 2 K threshold. **No kinetic fit
is forced if the full measured ramp fails that screen.** An initial ramp transient
and a model fitted on the entire trace need different treatment; this case must
not be advertised as experimental desorption-energy validation.

This completes an external input/provenance/peak check and supplies a negative
test of the new ramp guard. A scientifically appropriate isolated full-peak
energy comparison remains an open checkpoint. Do not count these data as
independent external adoption of TPD Spectra Studio or endorsement by the authors.
