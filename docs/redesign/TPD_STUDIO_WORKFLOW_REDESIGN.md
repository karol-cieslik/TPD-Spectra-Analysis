# TPD Spectra Studio — Workflow and UI Redesign Specification

**Status:** Proposed redesign, for implementation by Codex  
**Date:** 2026-10-22  
**Priority:** High — UX architecture and interactive scientific results  
**Scope:** Desktop GUI and reporting; preserve and reuse the existing numerical engine, CLI, imports, and exports.

> **Instruction for Codex:** Read this document before changing the GUI. Audit the latest code and tests, write a short implementation checklist, then implement incrementally on a feature branch. Preserve existing working functions. The UI examples below are intended behavior, not evidence that the corresponding functionality is already implemented.

## 1. Problem and intended user experience

The present interface exposes several methods/settings at once (including leading-edge and Redhead sections close together), but it is unclear where their results appear. It gives the impression that all methods run simultaneously on the same spectrum. The Monte Carlo / order-exploration capability is no longer sufficiently visible. Results should be immediately accessible, update after parameters change, and remain associated with the specific spectrum, peak, region, and method.

**Core principle: organize the software around a scientist's workflow, not around a list of available algorithms.**

**Target workflow:**
1. Import and inspect one or many spectra.
2. Prepare/compare the spectra and select a peak or region.
3. Explore physical models / likely desorption orders (including Monte Carlo).
4. Choose an analysis method and fit one selected peak/region at a time.
5. Inspect live results, curves, residuals, and uncertainties.
6. Retain multiple analyses per spectrum/peak and export a reproducible PDF/report.

Three primary workspace tabs:
- **Spectra & Preparation**
- **Modeling & Order Identification**
- **Kinetic Analysis**

A persistent **Results** area and an optional **Report / Export** action are accessible from the relevant stages. Avoid a fourth overloaded settings tab that shows all analysis controls at once. Context-specific controls belong to the selected stage and method.

## 2. Stage A — Spectra & Preparation

- Import CSV/TXT where currently supported; keep legacy column/header parsing and multiple-spectrum overlays.
- Display the raw spectrum prominently. Allow processed traces as overlays, with clear legends and colors.
- Select a spectrum and define one or more named peak regions (Peak 1, Peak 2, etc.) using numeric inputs and draggable plot boundaries.
- Surface temperature/time axis choices, overlays, visibility, normalization, smoothing and baseline controls here. Show whether a transformation is **display-only** or affects the calculation.
- Never silently modify raw data. Allow undo/reset and record processing provenance.
- Show the currently selected dataset/peak/interval persistently as the user switches tabs.
- Peak boundaries/regions are reusable for modeling and kinetics; changing a region invalidates or marks stale the downstream results that depend on it.

## 3. Stage B — Modeling & Order Identification

This is the exploratory/model-comparison workspace, separate from final kinetic analysis.

- Restore or expose the existing Monte Carlo capability. First inspect whether it actually exists in the current branch; do not claim restoration if it needs implementation.
- Show measured data and multiple candidate simulated traces overlaid on the same plot; optionally show residuals below.
- Candidate orders: 0, 1, 2 and flexible/non-integer/coverage-dependent models **only to the extent the engine supports and validates them**.
- Offer physically documented initial guesses/bounds for activation energy, prefactor, initial coverage/amplitude, heating rate, baseline and selected interval as appropriate to each model.
- Let the user vary model parameters interactively and see simulation updates. Debounce fast updates; send expensive Monte Carlo searches/optimization to a cancellable worker, with progress and a reproducible random seed.
- Provide explicit buttons such as **Simulate**, **Run Monte Carlo / Search**, **Compare Models**, and **Use This Model in Kinetic Analysis**.
- Show a sortable candidate-model comparison: model/order, fitted or assumed parameters with units, fit-window, residual metric, information criterion when statistically justified, numerical validity/warnings and uncertainty/identifiability notes.
- A ranking is evidence for comparative fit, **not proof** of desorption mechanism/order. One spectrum may not identify order uniquely; multi-coverage and multi-heating-rate evidence should be supported where possible.
- Store the selected hypothesis and starting parameter guesses for transfer into Stage C. Do not automatically overwrite user-selected final analysis settings.

## 4. Stage C — Kinetic Analysis

**One active method panel at a time.** A method selector must determine which controls and results are visible. The chosen method is applied to the selected spectrum/peak/temperature region, not implicitly to every peak.

Initial method choices (subject to what is implemented and scientifically sound):
- **Leading-edge analysis**: choose start/end temperature and valid leading-edge subregion; display transformed diagnostic plot, apparent activation energy, fit statistics/interval/assumptions.
- **Redhead analysis**: display peak maximum, heating rate, prefactor and kinetic assumptions; calculate its corresponding estimate. The classical Redhead expression commonly assumes first-order desorption; do not label it a general-purpose arbitrary-order fit.
- **Polanyi–Wigner model fitting**: choose/order model, starting parameters, bounds, fitting interval, baseline options and optimizer; show overlay, residuals, parameter uncertainties/limitations and diagnostics.
- Other existing supported methods may be surfaced individually without cluttering the screen.

Scientific precision:
- Do **not** hard-code “leading-edge = zero order” or “Redhead = first order” as if the two methods are exhaustive order-specific alternatives. Leading-edge analysis has assumptions about rate signal and coverage changes; Redhead's common closed-form formula assumes first-order kinetics and an assumed prefactor. Expose applicability and warnings.
- A numerical fit must never be equated with a proven mechanistic order.
- Distinguish manual parameter preview from an optimizer's fitted values, and distinguish fixed values from fitted values.

### Live results behavior

- A visible **Results for [dataset] / [peak] / [method]** card/table sits below or beside the graph. Optionally overlay a small Origin-style parameter box on the plot, with a show/hide toggle.
- When the user changes lightweight parameters or fit-window controls, update the preview and derived outputs in real time (debounced). Heavy optimization runs explicitly, with a progress indicator and cancel action; its results replace the current result only on successful completion.
- Results should include parameters, units, estimates, uncertainties when defensible, fit quality, fit range, warnings, and status (preview / fitted / stale / failed).
- Always show resulting fitted/simulated curves on the selected data, plus residuals for numerical fits.
- Save multiple labeled analysis runs, e.g. “Spectrum A → Peak 1 → leading edge” and “Spectrum A → Peak 2 → Polanyi–Wigner (n=1)”. Let users compare/reopen/delete runs without losing unrelated results.
- Switching method or peak restores that run's own settings and results; never leave values from another method deceptively on screen.
- Each result carries provenance: source file/hash, preprocessing, selected interval, model/assumptions, settings, software version, date, warnings.

## 5. Report & Export

Add **Generate PDF Report** and keep existing PNG/CSV/batch/JSON exports. A report should support selecting specific datasets and saved analysis runs rather than blindly dumping every trial.

Suggested structure:
1. Title, software/version, timestamp, input references.
2. Acquisition and metadata, including heating rate when known.
3. Raw/preprocessed spectra and recorded preprocessing.
4. Peak definitions and chosen ranges.
5. Order-model comparison with candidate curves, diagnostics, and limitations.
6. Per-run kinetic analysis, plots/fit residuals, parameter tables with units, uncertainties, assumptions and warnings.
7. Reproducibility appendix: complete effective settings, input hashes, numerical engine versions, seeds and optimization configuration.

Do not invent missing metadata or confidence intervals. Clearly show “not available” and relevant caveats. Allow PNG/SVG plot and CSV/JSON table export alongside PDF. Ensure PDF layout does not cut off plots/tables.

## 6. Proposed layout and interaction details

**Top bar:** Open / Save project, import, active dataset and selected peak, Generate Report.

**Tab A:** left spectrum list and preprocessing controls; central large plot; below plot compact region table.

**Tab B:** left candidate-model and adjustable parameter controls; central overlay plot (experimental vs simulations); bottom residual plot; right/bottom model comparison table and Monte Carlo progress/results.

**Tab C:** left method selector followed by ONLY method-specific controls; central plot with selected region, fitted curve and optional Origin-like result annotation; bottom/right persistent Results table and fit warnings; saved-analysis selector.

Use resizable splitters, sensible minimum sizes, large plots, scrollable side panels and uncluttered labels/tooltips. Avoid showing three unrelated method panels stacked vertically. Explain variables and units in method-specific help dialogs, including constraints and interpretations. Ensure controls/plots remain usable on common Windows laptop displays.

## 7. State/data architecture

Model the state explicitly, e.g.:

- Project: datasets, processing recipes, regions, candidate modeling sessions, saved kinetic analysis runs, report selections.
- Dataset: immutable raw data + metadata + provenance.
- Region: stable ID, dataset ID, bounds, optional peak label.
- Modeling session: dataset/region IDs, candidate models, guesses, run settings/results, selected hypothesis.
- Analysis run: stable ID, dataset/region IDs, method, method-specific inputs, status, outputs, units, uncertainties, diagnostics, warnings, provenance.

Separate UI state from numerical computation. Provide adapters to the existing engine instead of duplicating equations in widgets. Make the project save/load schema versioned and backward-compatible where feasible. Keep CLI behavior and batch exports stable.

## 8. Phased implementation tasks for Codex

**Phase 0 — Audit and baseline**
- Identify current GUI framework/widgets, analysis methods, Monte Carlo implementation, result propagation, existing tests and branch status.
- Run tests and record current working behavior. Confirm what “Monte Carlo” means in the existing code.
- Add a focused GUI/workflow test strategy.

**Phase 1 — Restructure GUI**
- Implement the three-stage navigation and shared dataset/peak selection.
- Move preprocessing controls into Stage A.
- Replace stacked analysis method settings with an exclusive method selector in Stage C.
- Preserve every currently functioning analysis path.

**Phase 2 — Results-first interactive analysis**
- Connect each method to an immediately visible, method-scoped results panel.
- Implement reliable result invalidation, debounced previews, plots/residuals and per-peak saved runs.
- Ensure control changes lead to clear displayed changes and never silently reuse stale results.

**Phase 3 — Modeling/Monte Carlo**
- Restore or integrate existing functionality into Stage B, with parameter initialization, progress/cancel, reproducible seeds, overlays and model comparison.
- Add transfer of selected candidate settings to Stage C without conflating exploration and final fitting.

**Phase 4 — Report and project persistence**
- Implement selectable PDF reporting with export tests and complete provenance.
- Save/load workspaces and saved analysis runs.

**Phase 5 — UX polish and scientific validation**
- Validate each analysis method against synthetic analytical reference cases and documented experimental/literature benchmarks where data rights allow.
- Test zero/first/second order, overlaps, baselines, noise, multiple heating rates, invalid inputs and optimizer failures.
- Update user documentation and screenshots; collect usability feedback.

## 9. Acceptance criteria

- [ ] Main GUI has exactly the three clearly labeled workflow stages above (report/export may be a dialog or action).
- [ ] Uploading a spectrum shows it clearly and allows defining Peak 1 / Peak 2.
- [ ] The active dataset/peak is preserved and visibly identified across stages.
- [ ] Only the selected analysis method's controls are shown.
- [ ] Leading-edge and Redhead controls no longer look like one continuous method.
- [ ] For a selected method, results are clearly visible without needing batch export.
- [ ] A valid parameter/window edit updates the appropriate preview and displayed result, or marks expensive fitted results stale pending explicit recomputation.
- [ ] Distinct peaks can have different methods/orders and saved result sets.
- [ ] Modeling has visible candidate curves, parameters and Monte Carlo/model-search access, if supported by the engine.
- [ ] Users can inspect fitted curves and residuals and distinguish hypotheses from confirmed data.
- [ ] PDF report contains selected results, plots, assumptions and reproducibility metadata.
- [ ] Existing CLI, CSV exports, core analyses and tests remain functional.
- [ ] GUI integration tests verify switching methods/peaks never displays another run's stale result.
- [ ] Scientific limitations are stated clearly and no result is described as proving a unique desorption order.

## 10. Prompt for the future Codex session

> Read `docs/redesign/TPD_STUDIO_WORKFLOW_REDESIGN.md` from the latest `main` branch of `karol-cieslik/TPD-Spectra-Analysis`. Treat it as the target UX/product specification. First inspect the latest application architecture and existing tests, then implement the phases sequentially on a new branch with tests and screenshots. Preserve current capabilities and avoid changing validated numerical methods merely to satisfy the new layout. Start with Phase 0 and Phase 1, report what is complete, and proceed to the next phase only when the current one is verified.
