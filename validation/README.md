# Published TPD/TDS spectra: literature-validation candidates

This is a **research checklist**, not a repository of downloaded or validated data. The catalog lists 11 verified bibliographic candidates for evaluating TPD Spectra Studio on literature spectra and reported parameters. A DOI and article record do **not** imply that the full text, figure, underlying data or reproduction rights have been checked.

## Suggested workflow

1. Prioritize LIT002 (experiment + stated kinetic orders and parameters), LIT003 (second-order and multiple heating rates), LIT001 (zero-order), LIT010 (energy distributions) and LIT009 (tabular peak-temperature cross-check).
2. Open the original article and confirm exact figure, axes, heating rate, signal scaling, coverage, temperature units and whether the data are experimental or simulated. Update `verification_level` and `candidate_figures_or_tables`.
3. First look for downloadable author/publisher data or supplements. If absent, digitize the *graph*, recording axis calibration, resolution, units, trace/curve identity, human uncertainty and processing choices.
4. Fit each digitized trace with a frozen software release, and record E, prefactor, fitted order, residuals, AICc, intervals, computational failures and any discrepancies from authors' assumptions.
5. Compare appropriately: use reported kinetic parameters only when coverage normalization/prefactor units and model assumptions match. Peak position and shapes may be more defensible than absolute prefactors across dissimilar instrumentation.
6. Maintain a reproducible provenance record per extracted trace: article DOI, figure/panel, underlying experimental conditions, access date, digitizer version, original figure source, plot-calibration points, output CSV hash, software commit and exclusion reasons.
7. Confirm licensing before redistributing figure-derived points. Citation alone is not a redistribution license. Prefer linking to sources and distributing derived benchmark metadata/code where permission is unclear.

## Scientific caveats

An isolated trace often does not uniquely identify kinetic order or energy and prefactor; higher-quality validation uses **coverage series and multiple heating rates**. Multilayer ice spectra, phase changes, subsurface populations, lateral interactions, reactor transport and readsorption may violate a single-state Polanyi–Wigner model. A fit reproducing a published trace does not constitute independent confirmation of the published interpretation.

`digitization_status=not_started` is intentionally assigned to every record. **No source figure has yet been digitized or experimentally benchmarked.** In a manuscript, distinguish *identified literature candidates* from *completed external validation*.

This catalog is meant to be extended and audited. The primary references are linked directly in the CSV; avoid claiming exact figure identifiers where not confirmed.
