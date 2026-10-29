# Three additional studies for external comparison

Checked 29 October 2026. This expands the **candidate** collection by three papers and nine molecular systems; it adds no completed digitization or kinetic validation. Existing extractions and fits were not repeated. Values in `reference_targets.csv` are literature references, not measured samples or software outputs.

## 1. Perrero et al. (2024): ethanol and ethylamine

*Binding energies of ethanol and ethylamine on interstellar water ices: synergy between theory and experiments*, PCCP 26, 18205–18222. [DOI](https://doi.org/10.1039/D4CP01934B); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11221575/).

Prioritize **0.7 ML ethanol on gold**, Fig. 7 top-right: experimental black points, not the red simulation. Heating is 0.15 K/s; the dominant published population is 6450 K, with a TST prefactor of 3.31e18 s^-1. More than 80% belongs to the main population; a single-energy fit is only an approximation. Ethylamine (0.4 ML, bottom-right) has a broader distribution and is a model-limit case. Fig. 4 offers an experimental-only cross-check. Publisher licence is **CC-BY-NC-3.0**, requiring separate noncommercial attribution; do not apply the software licence to these materials. Raw experimental numerical data have not been acquired.

## 2. Fulker and Brown (2024): two esters on graphite

*Surface science studies of the coverage dependent adsorption of methyl acetate and methyl propanoate on graphite*, RSC Advances 14, 35373–35385. [DOI](https://doi.org/10.1039/D4RA04466E); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11537193/). **CC-BY-3.0**.

Heating is 0.5 +/- 0.01 K/s. Prefer multilayer leading edges first. Fig. 6C reports **42.8 +/- 0.7 kJ/mol** for the 50 Lm methyl-acetate example; Table 2 instead summarizes 43.5 +/- 0.9. These are distinct references and must not be substituted. Table 3 gives 45.7 +/- 0.9 for crystalline multilayer methyl propanoate. Submonolayers have coverage-dependent parameters; a constant-energy fit cannot reproduce that analysis directly. The paper links [raw data](https://doi.org/10.25377/sussex.26058322), but acquisition failed (API 404, landing page 403). Three figure images were successfully retrieved; exact trace identification is still required.

## 3. Martín-Doménech et al. (2014): five pure ices

*Thermal desorption of circumstellar and cometary ice analogs*, A&A 564, A8. [DOI](https://doi.org/10.1051/0004-6361/201322824); [accessible preprint](https://arxiv.org/abs/1406.0425).

Fig. 1a contains pure H2O, CO, CO2, CH3OH and NH3 on KBr at 1 K/min. Table 4 gives zero-order energies and prefactors, transcribed separately in the CSV. Begin with a resolved bulk feature, avoiding phase-change regions. CO also has substrate desorption, so its complete curve is not one bulk peak. The ordinate is logarithmic. The downloaded source is preprint v1, not a verified final layout; its header dates are inconsistent. **Figure-reuse rights remain unverified**, so this candidate is held before redistribution/digitization. Accessible reading alone does not establish a reusable benchmark dataset.

## Admission and comparison sequence

1. Resolve the remaining licence and raw-data access issues. Prefer deposited numerical spectra where available. The supplied retrieval script checks the five already-observed image hashes and saves them outside the repository.
2. Identify experimental traces, coverage, phase and axis units. Inspect overlapping experimental symbols and simulation lines; do not extract the simulation as experimental evidence.
3. Digitize each admitted trace with retained calibration, gaps, pixel uncertainty and source overlay; independently review trace correspondence. No invented time column: published beta is an assumed ramp, not measured ramp evidence.
4. Freeze windows, baseline alternatives, kinetic order, prefactor treatment and scoring before fitting. Keep initial optimization independent of the published energy.
5. Compare identical estimands: fixed-prefactor energy separately from free-prefactor sensitivity; leading-edge estimates separately from whole-peak fits. Absolute zero-order prefactors require coverage/area calibration; arbitrary figure intensity cannot supply it.
6. Retain every result, boundary hit and residual. Report digitization and model mismatch separately from conditional Monte Carlo variability. Paper error bars are not automatically a statistical acceptance interval.

Recommended first comparison: ethanol/gold, then an admitted pure-ice bulk leading edge, then ester multilayers. Ethylamine and ester submonolayers broaden the challenge set but do not establish single-energy accuracy. Nine systems from three papers are not nine independent studies. The earlier 2024 CO source-to-figure discrepancy remains unresolved and is not repaired by these additions.

`source_manifest.json` records source URLs, licences, download hashes and access failures. No new result is claimed in the manuscript. Human scientific acceptance remains open.

## Subsequent completed comparison

[Ethanol/Au assessment](../ethanol_2024/README.md) now contains an extraction and
20 conditional fits. The screening CSV above preserves its original candidate
status as recorded before analysis. It is not the current result register.
