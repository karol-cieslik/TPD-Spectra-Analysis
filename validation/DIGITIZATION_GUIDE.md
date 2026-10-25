# Extracting published TPD/TDS curves for external validation

Start from `literature_tpd_candidates.csv` (bibliography and eligibility), then use `literature_extraction_notes.csv` (one row per literature ID with paper-specific extraction guidance). These instructions are **plans**, not evidence that a figure or its raw numerical data have been accessed.

## Preferred data sources, in order

1. Check the article landing page for **Supporting Information**, supplementary tables, data repository links (Zenodo/Figshare/Dryad/institutional), or author-provided CSV.
2. If no numerical file exists, download the permitted PDF at native resolution. Check whether the target figure uses vector curves rather than a low-resolution raster.
3. If necessary, digitize with WebPlotDigitizer or equivalent. For XY plots: choose 2D X-Y, calibrate each axis using at least two well-separated ticks per axis, select **linear/logarithmic axes correctly**, and digitize each curve separately with unique legend labels. Retain a screenshot or working project of axis calibration where allowed.
4. Prefer manually validating 10–20 anchor coordinates in addition to any automated curve detection. Exclude legend lines and text; mark overlapping/occluded portions as missing rather than hallucinating points.
5. Save the original extracted coordinates separately from any resampled, smoothed, baseline-corrected or normalized versions. Never alter raw extracted coordinates in-place.
6. Inspect for unit conversion: x may be Kelvin (convert to Celsius only at the software input boundary), y may represent a mass-spectrometer channel, QMS signal, ion current, intensity or normalized arbitrary units.
7. Retrieve `β=dT/dt` from the figure caption, methods or supplementary information. If absent, record **unknown**; do not infer it from a graph. Never fit kinetics by guessing the heating rate.
8. Record full-peak coverage: onset, apex and tail. A cropped window may bias kinetics and model comparisons. Determine whether the curve includes one adsorption state, overlapping states, readsorption, diffusion or chemical reaction.
9. Before quantitative comparison, reproduce at least the author-reported peak temperature, heating rate, order assumption and calibration units. Keep the experiment's physical interpretation distinct from the software's best fit.

## Per-extracted-trace metadata template

For each extracted trace, create an entry in a local extraction log with:

`trace_id,publication_id,doi,figure_panel,series_label,spectrum_origin,source_url,accessed_on,license_or_permission,temperature_original_unit,signal_unit,heating_rate_K_s,coverage_original,substrate,adsorbate,sample_prep,extraction_method,digitizer_version,axis_type,calibration_points,raw_csv_path,sha256,excluded_regions,estimated_digitization_error,software_commit,fit_model,fit_status,comparison_to_published_result,notes`.

Mark `spectrum_origin` as **experimental**, **simulation**, **review reproduction**, or **unknown**. Never count a simulation or duplicated review reproduction as an independent experimental validation case.

## Digitization quality-control checklist

- [ ] DOI/title and original figure/panel confirmed from full text.
- [ ] Spectrum is truly experimental; instrument and adsorbate channel understood.
- [ ] Raw supporting numeric data sought before digitization.
- [ ] Both axes and units calibrated and verified against printed ticks.
- [ ] Heating rate and adsorption coverage (if available) recovered from methods.
- [ ] Multiple curves/panels individually labeled and non-overlapping sections cross-checked.
- [ ] Raw extraction retained without smoothing; original figure and image rights recorded.
- [ ] 10–20 manually checked anchor points agree within estimated graphical precision.
- [ ] Output CSV loads into TPD Spectra Studio with the expected temperature direction.
- [ ] Any failed or invalid fit is reported rather than silently excluded.

## Reporting in the manuscript

Distinguish **bibliographic candidates**, **figures inspected**, **spectra extracted**, **curves with usable experimental metadata**, and **curves quantitatively validated**. Present independent error metrics (peak-temperature deviation, normalized RMSE, fitted parameters and deviations from author-reported values where commensurable), negative results and model inadequacy, not only representative successes.

**Important rights distinction:** the ability to view or digitize a figure for analysis does not automatically grant rights to redistribute its image or traced curve in a public benchmark dataset. Inspect the relevant article license and reuse conditions. If uncertain, distribute your extraction log and a link, not the figure or extracted coordinates.

## Limitations

Strong fit quality does not identify the mechanism uniquely. Models generated from or fit to the same equation are not independent experimental validation. Coverage-series and multi-rate datasets are particularly valuable for kinetic identifiability. Some catalog entries are reviews or non-TPD modalities and may be unsuitable after inspection.
