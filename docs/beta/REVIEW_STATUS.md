# Beta review status — TPD Spectra Studio

**Status:** external research beta under review; not a published software release.
This note distinguishes implemented code, automated checks and evidence still
needed before sending a new executable to colleagues.

## Current source and completed integration

Current beta: **0.11.0b7 on main**. PR #19 (noisy demo/progress/components),
PR #20 (Results/Help/tutorials) and PR #21 (b5 identity/frozen acceptance) were
merged on 27 October 2026. Historical PR descriptions and acceptance records
describe their original development state, not current download instructions.

The latest successful main Windows build before this cleanup was
[run 40488914540](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40488914540),
source `7a0f6f739835baf4663cea809393bc8d1af28c42`. It includes all three PRs.
For the current package, follow [START_HERE](../../START_HERE.md) and record
the run and exact commit; do not reuse older b4 evidence for a later build.

## Implemented and covered by regression tests

- Three connected workflow stages and independent dataset/peak/method settings.
- Synthetic first-order, noisy, drift, zero-order and overlapping examples with
  documented generating inputs and caveats; nine separate CC BY-licensed
  publication-derived traces retain citations, source coordinate files and
  explicit caveats, without claiming independent energy validation.
- Compact File / Examples / View / Help menus leave scientific controls and plot
  space visible; examples are browsed by provenance category.
- Leading-edge/Redhead estimates, single-state Polanyi–Wigner fitting, model
  comparisons, selected Monte Carlo refitting, and constrained joint components.
- Fit cancellation, progress updates, saved-run/project persistence and exports.
- Results parameter roles and submitted-settings provenance (PR #20).
- Offline scientific Help topics and navigable first-run exercises (PR #20).

## Completed automated checks and remaining gates

- [x] PRs #19–21 merged; b5 Windows CI and frozen-package smoke succeeded.
- [x] Save/reopen/report, synthetic imports, Help/tutorials, component exports,
      Monte Carlo progress and cancellation have automated coverage.
- Automated release gate: the Windows workflow builds and verifies each final
  source commit, frozen executable, portable resources, hashes and links before
  uploading its artifact. Follow the latest successful main run in START_HERE.
- [ ] Human visual first-run, published/simulated library and source descriptions, all five tutorials, Help scrolling, Results labels
      and Monte Carlo controls at ordinary and high display scaling.
- [ ] Independent Windows 10/11 acceptance without Python on the exact ZIP.
- [ ] Independent scientific review, experimental benchmarks with permission
      and uncertainty-coverage validation (not prerequisites for synthetic pilot use).
- [ ] Publish a stable GitHub prerelease download only after separate approval.

Automated widget/layout checks are not visual acceptance. Source audits and
synthetic recovery are not independent experimental validation.

## Scientific boundaries

Synthetic truth recovery primarily checks numerical consistency when the
forward and inverse models are related. It does not demonstrate blind
mechanism identification, instrument calibration or realistic uncertainty
coverage. AICc preferences are conditional on compared models. Seeded
parametric Monte Carlo assumes iid Gaussian residual noise. Component counts
and fitted reaction orders are hypotheses; fixed prefactors and coverages must
not be reported as fitted measurements. Non-unique zero-order prefactor/scale
brackets are not confidence intervals.

## Suggested first colleague test

1. Download and extract the **new** reviewed Windows package (not the older b4
   artifact); open `START_HERE.md` or `docs/beta/WORKED_EXAMPLES.html`.
2. Open the clean first-order example and inspect the Redhead energy near
   1.2 eV together with its **assumed** prefactor.
3. In Scientific Help, search for **seed**; then complete a short Monte Carlo
   exercise on the noisy first peak, observing progress and failure counts.
4. Optionally fit the three synthetic overlapping components and export curves.
5. Send a brief note about clarity, suspected numerical issues and Windows
   behavior. Experimental data are optional and require separate permission.

See [the colleague handoff and release gate](SHARE_WITH_COLLEAGUES.md),
[the tester checklist](TESTER_CHECKLIST.md),
[the source-level scientific consistency audit](SCIENTIFIC_CONSISTENCY_AUDIT.md)
and [the scientific methods status](../METHOD_STATUS.md). Internal release records stay in GitHub and are excluded from the colleague ZIP.
