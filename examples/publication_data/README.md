# Publication-derived example spectra

This folder is a **curated teaching and stress-test subset**, separate from the
known-ground-truth simulations in `examples/beta_collection/`. Open it through
**Examples → Publication-derived spectra…** in TPD Spectra Studio.

The original numeric coordinates are preserved under `originals/`. The adjacent
import-ready CSVs contain the source **temperature and intensity**, converted to
the application's `ms,DHTA+,Temperatura` internal format. Their first column is:

- **Deposited measurement (Becker et al.)**: original measured time, seconds to ms.
- **Figure digitizations (all other entries)**: a *constructed nominal-ramp
  coordinate* `(T_K - T_first_K)/beta_K_s`, converted to ms, solely to satisfy
  the instrument-style importer. This is **not measured time**, and must never
  be described as such. Temperature is converted from K to °C; signal amplitudes
  retain their source units/normalization (the GUI treats them as generic signal).

The `catalog.json` records each published citation, DOI, exact figure or source,
licence, heating rate, original columns, accepted/omitted points, and important
scientific limitations. `scripts/generate_publication_examples.py` regenerates
import-ready CSVs without smoothing, interpolating, filling missing figure
coordinates, or altering source files. The original image/axis-calibration QA,
protocols and detailed limitations remain under `validation/` in the source
repository and are **not bundled**.

**Data reuse and attribution.** Each source remains under its own Creative
Commons licence, independent of the software MIT licence:

- Zaki et al. (2018), *Phys. Chem. Chem. Phys.* 20, 15764–15774,
  [DOI 10.1039/C8CP02333F](https://doi.org/10.1039/C8CP02333F),
  Fig. 1a: [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
- Narayanan, Piacentino, Öberg and Rajappan (2025), *Astrophys. J.* 986, 10,
  [DOI 10.3847/1538-4357/adc7b6](https://doi.org/10.3847/1538-4357/adc7b6).
  Digits from **arXiv:2504.01102v1**, not final layout:
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Kruczkiewicz et al. (2024), *Astron. Astrophys.* 686, A236,
  [DOI 10.1051/0004-6361/202346948](https://doi.org/10.1051/0004-6361/202346948),
  Figs. 2b/3a: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Fulker & Brown (2024), *RSC Advances* 14, 35373–35385,
  [DOI 10.1039/D4RA04466E](https://doi.org/10.1039/D4RA04466E),
  Fig. 4B: [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
- Ayling, Burke, Salter & Brown (2017), *RSC Advances* 7, 51621–51631,
  [DOI 10.1039/C7RA10410C](https://doi.org/10.1039/C7RA10410C),
  Fig. 2A (four exposure traces): [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
- Becker et al. (2026), RODARE deposition
  [DOI 10.14278/rodare.4644](https://doi.org/10.14278/rodare.4644),
  H2 D2 worksheet: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

All derived numeric exports are adaptations of the cited works. We have
reformatted their columns and (for image-derived data) digitized plotted
coordinates. The original authors have not endorsed TPD Spectra Studio.

**Scientific caveats:** These are not independent experimental validation
passes, and figure pixels are not independent observations. The fit methods
have known limits for multistate desorption, varying coverage, missing data,
non-constant ramps, uncalibrated amplitudes, and ambiguous pre-exponentials.
Review residuals, provenance and source papers before interpreting energies.

**Not included in the public example bundle:** the Perrero et al. ethanol
figure-derived dataset (CC BY-NC restriction), the CO ice curve with an unresolved
paper/deposit mismatch, source material with missing licences, and candidate
studies without adequately reviewed numeric traces. These remain documented
separately under `validation/publication_data/`.
