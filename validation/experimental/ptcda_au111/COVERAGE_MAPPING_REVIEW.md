# Coverage mapping investigation: completed, reproduction blocked

Reviewed 29 October 2026. This investigation does not repeat or replace the
438 conditional fits. `metadata_audit.json` and `metadata_inventory.csv` record
the new audit; `source_review.json` identifies the inspected primary sources
and their hashes.

## What is established

The main article defines 1 ML from the integrated saturated alpha3 spectrum,
the dark-blue trace in Figure 1a's inset. Other initial coverages use that
integral as the reference. The supplement's Methods (printed pp. 7–8, equation
4) specifies a complete analysis at equal remaining coverage across spectra
with different starting coverages. Fitting logarithmic desorption rate against
inverse temperature gives a coverage-dependent energy; extrapolation to zero
coverage gives the reported intercept. The original reference is King (1975),
https://doi.org/10.1016/0039-6028(75)90302-7 . This is a multi-spectrum analysis,
not the existing software's independent constant-E whole-peak fitting path.

Primary sources: article https://doi.org/10.1038/s42004-023-00925-2 ;
[supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs42004-023-00925-2/MediaObjects/42004_2023_925_MOESM2_ESM.pdf);
data https://doi.org/10.26165/JUELICH-DATA/HQXCXC .

## What remains unverified

No raw-filename-to-coverage mapping, published curve labels, or uniquely
identified saturation-reference filename was located in the inspected article,
supplement, deposited metadata or raw headers. All 95 files therefore retain
`unknown` coverage and curve-label fields. Dates, sequence numbers, peak
positions and integrated signal sizes do not independently establish those
identities. The header audit found detector scales E-10, E-11, E-12 and E-13;
raw numeric areas cannot be compared across scales without accounting for that
notation and establishing the response convention. The frozen independent
fits each have a free signal scale, so this does not invalidate their retained
within-trace residual metrics. It does prevent treating those numeric areas as
an already calibrated coverage series.

A shared unknown proportional coverage scale can cancel from some slope
calculations. That fact alone does not identify the authors' selected curves,
saturation reference, integration windows, baseline or extrapolation domain.
An exploratory reconstruction could be performed under additional assumptions,
but it would not establish reproduction of the reported result or validate the
current single-state constant-E fitter against a commensurate reference.

## Parsing check and preserved work

Nineteen files put channel labels on line 1; 76 put them on line 3. The earlier
fixed three-line skip discarded two startup samples in those 19 files. The new
header-aware audit checks **all 95 files** and confirms that every retained
550–740 K analysis window is numerically identical. The
omitted startup rows are outside that interval. Existing trace hashes,
selection results and all 438 fits remain unchanged; no refitting is required.
The new script reads headers explicitly and preserves the source ZIP.

## Decision and next checkpoint

This source remains an external experimental model challenge. Do not mark
experimental energy reproduction complete, assign coverage by visual guess,
raise bounds to chase 1.74 eV, or add an unvalidated complete-analysis capability
to the application merely to make this benchmark work.

Before reconsidering a reproduction, establish:

1. Saturated alpha3 reference filename and the exact raw-file subset used in
   the published inset and energy regressions.
2. Initial coverages or an explicit calibrated integration recipe, with signal
   scale/response convention and any temperature correction.
3. Baseline and integration endpoints, common remaining-coverage values,
   point exclusions, regression weighting and extrapolation range.
4. A distinction between validating a new complete-analysis implementation and
   evaluating the existing constant-E fitter on a suitable independent reference.

No author was contacted. Those items can be resolved if source metadata later
becomes available. The next autonomous scientific checkpoint is to identify a
commensurate isolated constant-energy experimental reference with complete
provenance. Do not spend another fitting cycle on the unresolved PTCDA mapping.
