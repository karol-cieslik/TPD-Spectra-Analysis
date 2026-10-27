# Beta review status — TPD Spectra Studio

**Status:** external research beta under review; not a published software release.
This note distinguishes implemented code, automated checks and evidence still
needed before sending a new executable to colleagues.

## What is in which version?

| Source | What it contains | Status |
| --- | --- | --- |
| `main` | Earlier reviewed development baseline | Not the latest beta |
| [PR #19](https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/19) — `fix/beta-feedback-14-17` | Noisy default examples, first-peak selection, visible Monte Carlo progress, constrained overlapping components | Draft; existing Windows 0.11.0b4 artifact derives from this branch |
| [PR #20](https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/20) — `ux/results-readable-beta` | Structured kinetic Results, fitted/assumed labels, 40-topic offline Help and guided Quick Start | Draft stacked on PR #19; new Windows build and visual acceptance outstanding |

The old `tpd-spectra-windows-x64-beta-0.11.0b4` Actions ZIP does **not**
contain the follow-up PR #20 interface. Always check `VERSION.json` for the
build's exact commit. A successful Linux test run is not proof that a Windows
executable containing these changes was packaged or visually inspected.

## Implemented and covered by regression tests

- Three connected workflow stages and independent dataset/peak/method settings.
- Synthetic first-order, noisy, drift, zero-order and overlapping examples with
  documented generating inputs and caveats.
- Leading-edge/Redhead estimates, single-state Polanyi–Wigner fitting, model
  comparisons, selected Monte Carlo refitting, and constrained joint components.
- Fit cancellation, progress updates, saved-run/project persistence and exports.
- Results parameter roles and submitted-settings provenance (PR #20).
- Offline scientific Help topics and navigable first-run exercises (PR #20).

## Open release gates

- [ ] Build PR #20's executable and portable ZIP from a **single reviewed commit**.
- [ ] Run the frozen-package smoke suite, including the Help catalog, five
      tutorial tabs, result table, example chooser and three-component exports.
- [ ] Open the ZIP on clean Windows 10/11 machines without Python; verify the
      sidebar, help buttons, search, tab navigation and clipboard at different
      DPI scaling and window sizes.
- [ ] Follow the worked examples as a new user, recording incorrect labels,
      missing warnings and steps that cannot actually be completed.
- [ ] Review zero-order identifiability, MC interval interpretation and
      overlapping-component assumptions against independent calculations.
- [ ] Confirm save/reopen/export still preserve source hashes, methods,
      settings, units and warnings.
- [ ] Obtain permission and provenance for any experimental data used in
      benchmark work; keep external data out of the release unless licensed.
- [ ] Review and merge PR #19, then reconcile PR #20 onto `main` after approval.
- [ ] Tag a reviewed version, publish its checksums and provide one stable
      colleague download link.

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

See [the tester checklist](TESTER_CHECKLIST.md),
[the source-level scientific consistency audit](SCIENTIFIC_CONSISTENCY_AUDIT.md)
and [the scientific methods status](../METHOD_STATUS.md). The current maintainers
can review the PRs and CI logs directly; no code or results have been merged
into `main` as part of this note.
