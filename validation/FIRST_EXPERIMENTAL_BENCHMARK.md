# First experimental TPD benchmark: practical handoff

The [candidate catalog](literature_tpd_candidates.csv) contains **26 literature leads** and the matching [extraction notes](literature_extraction_notes.csv). On the October 2026 source review, **all 26 remain `not_started`**. None is a digitized or validated experimental benchmark yet. This is an acquisition and analysis procedure; it does not reproduce external paper figures or assert permission to redistribute them.

## Which papers to try first

| Order | Catalog ID | What to look for | Why / stop condition |
| --- | --- | --- | --- |
| 1 | `LIT002` — Brown and Bolina (2007) | Water-ice coverage series in Figure 1; ammonia experimental/simulation distinction in Figure 2; Table 1 parameters | Full publisher text and reported parameters have been checked in the bibliography. **Do not** count adapted or simulated curves as separate experimental observations; check units and coverage convention before comparing reported prefactors. |
| 2 | `LIT001` — Fraser et al. (2001) | Experimental water-ice coverage series in Figure 1, by original curve/coverage | Candidate zero-order depletion-edge check. Keep Figure 2 theoretical curves separate from experimental validation. Record each full trace and whether its depletion tail is visible. |
| 3 | `LIT003` — Genger, Hinrichsen and Muhler (1999) | Hydrogen spectra by heating rate and exposure | Candidate second-order/multi-ramp challenge. **Stop at source inspection** if the full text or β for each curve is unavailable; figure identifiers are not yet verified. |

These are *acquisition priorities*, not verified high-quality benchmarks. Move to another catalog entry if source rights, raw data, curve visibility or heating-rate metadata block a candidate.

## One-trace protocol

1. **Verify the primary experiment.** Open the publisher's primary paper, identify DOI or persistent record, exact figure/panel/trace, experimental versus theoretical origin, sample/substrate/adsorbate, reported heating rate and coverage series. Mark any unverified field **unknown**, not zero. Seek supporting CSV data before digitizing a printed figure.
2. **Record data provenance and rights.** Keep the source URL, date accessed, article license, figure reuse status, digitization software/version, calibration points and original image/vector source **outside the public repository when rights are uncertain**. A citation does not grant republication rights.
3. **Extract without changing the source.** If only a graph exists, digitize every plotted experimental curve separately. Calibrate at least two well-separated ticks per axis, verify whether either axis is logarithmic, cross-check 10–20 manually chosen anchors and record their largest deviation. Preserve raw extracted coordinates unchanged and mark obscured sections as missing.
4. **Prepare an explicitly derived import copy.** The application expects `Time_ms,Signal,Temperature` in a simple CSV; `Temperature` means °C. Convert a published K axis by subtracting 273.15. If the paper supplies a constant β in K/s but no time channel, a **constructed** monotonically increasing time coordinate may be calculated for import as `Time_ms = 1000 * (Temperature_C - Temperature_C[0]) / beta_K_s`. Label this field **derived from an assumed linear heating program**, never measured acquisition time. Do not construct it if β is missing or the heating program is known to be nonlinear. Record that the importer's legacy spike-correction heuristics must be inspected for an otherwise valid curve.
5. **Freeze the inputs.** Record exact input file hash, digitization edits, heating rate, temperature range, signal units, point count, software commit/version, selected interval, baseline/smoothing recipe, initial guesses, bounds and model hypotheses. Retain raw and working copies separately. Never silently change a literature heating rate to the app's 1 K/s default.
6. **Run comparable calculations.** Start with peak temperature and displayed shape. Fit an isolated full peak using only suitable order hypotheses. Use the fixed-zero-order depletion-edge method only if the exhaustion region is present. For overlapping experimental features, compare explicitly specified 1–3 positive-order component hypotheses on the same **full** trace; component orders, prefactors and initial coverages remain fixed assumptions. Record *failed* and non-identifiable fits.
7. **Quantify the discrepancy.** Record peak-temperature deviation in K, RMSE in original signal units, normalized RMSE with its denominator, residual structure, fitted energies/orders under stated assumptions and sensitivity to interval/baseline/initial guesses. Compare reported energies or prefactors numerically **only** when the published kinetic law, coverage convention and units are commensurate. Document disagreements and excluded traces.
8. **Classify the evidence.** Use the stages below. Do not call a fit an externally validated result merely because it converges or recovers values from synthetic examples.

## Evidence stages for the manuscript and release notes

| Stage | Minimum evidence | Honest phrasing |
| --- | --- | --- |
| Literature lead | Article URL/DOI, title, intended TPD role | “Identified candidate” |
| Primary source inspected | Exact original figure/panel and experimental origin confirmed | “Figure inspected” |
| Trace acquired | Raw numeric data or digitized curve, extraction notes, hash, source rights | “Experimental trace extracted” |
| Kinetic inputs complete | β and units, sample context, full relevant temperature interval, export permission status | “Usable for a stated quantitative test” |
| Reproduced analysis | Frozen software commit/settings, residual metrics, failures and author comparison where meaningful | “Evaluated on an external experimental trace” |
| Independent validation | Predeclared acceptance criteria and independent reference calculations across appropriate systems, with positive and negative cases | “Externally validated **for the stated test only**” |

## Minimal per-trace result record

Keep one private/reviewable record with the following labeled fields (no empty value should be interpreted as zero):

```text
trace_id; catalog_id; DOI_or_source; original_figure_panel; published_curve_label
experimental_or_simulated; adsorbate; substrate; reported_coverage_and_units
beta_K_s_and_source; temperature_axis_original_unit; signal_axis_unit
raw_coordinates_sha256; import_csv_sha256; time_axis_measured_or_derived
digitizer_and_version; axis_calibration_points; anchor_check_error
permission_or_license; analysis_commit; fit_interval_C; processing_recipe
model_and_assumptions; initial_guesses_and_bounds; convergence_and_warnings
peak_T_source_K; peak_T_reproduced_K; delta_peak_T_K
RMSE_signal; NRMSE_and_denominator; fitted_parameters_and_units
author_reported_parameters_if_comparable; limitations; exclusion_reason
```

Store these records alongside locally retained source data. Publish only metadata and numerical curves for which rights and permissions permit redistribution. If an author later supplies raw spectra, preserve that original delivery separately and record the permission terms.

## Next human action

**Start with `LIT002`:** locate the publisher's Figure 1 and supplemental data, write down each available heating rate and the exact experimental trace labels, and confirm rights before exporting coordinates. If that cannot be established, try `LIT001`. Only after one trace has source provenance and known β should numerical fitting begin.

See the [general digitization guide](DIGITIZATION_GUIDE.md), [literature tracker](README.md) and the [software method limitations](../docs/METHOD_STATUS.md).
