# Redesign implementation record

Target: TPD_STUDIO_WORKFLOW_REDESIGN.md, main commit
473ad4e175b08fdfb7d87919b2cde93e85502bce. Application baseline:
450c5c25597a0d567b8ca35076eca5eddb07c83f (working branded beta).
Implementation branch: feature/workflow-redesign, separate checkout.
Neither main nor the existing beta checkout is changed by this work.

## Phase 0 — audit

- Framework: Tk/ttk, Matplotlib embedded canvases. Existing GUI combines view
  controls and batch settings; reviewed batch runs use a child CLI process.
- Numerical paths: analysis.py (import, cleaning, heating ramp, leading edge,
  first-order Redhead); kinetics.py (single-state numerical fitting/simulation);
  existing CLI also exposes two-state/global and diagnostic paths.
- Monte Carlo exists: kinetics_uncertainty.py performs seeded iid Gaussian
  parametric refitting around a fitted reference; it is not microscopic kinetic
  Monte Carlo or Bayesian MCMC. Explorer is currently a separate Toplevel.
- Existing exports: batch CSV/JSON/PNG, Explorer CSV/JSON/PNG/SVG, frozen CLI.
- Results are snapshot-based but lack a project-wide dataset/region/run model.
- Preserve numerical modules and existing GUI as a classic/batch workspace.
  Add a workflow state layer and adapters; do not duplicate solver equations.

## Ordered implementation gates

- [x] 0: baseline: 171 passed (130.51 s), no failures; output/redesign-baseline.xml.
- [x] 1: real Tk verification: 2 passed (10.49 s). Three stages, shared dataset/region IDs, named reusable regions,
  exclusive method controls, existing batch/Explorer access retained. Verify
  real-widget navigation and two regions before starting Phase 2.
- [x] 2: seven workflow tests passed (12.48 s). Method adapters, debounced light previews, explicit cancellable fit,
  immutable result snapshots and per-context saved runs. Verify context switches,
  stale completion, failure/cancel preservation and engine equivalence.
- [x] 3: eight workflow tests passed (15.40 s), including seeded MC through embedded controls. Embedded modeling with simulation/comparison/Monte Carlo, seed/progress,
  candidate transfer and recorded context. Verify restored session state,
  cancellation and deliberate transfer without automatic setting changes.
- [x] 4: 11 workflow/persistence/export tests passed (22.70 s); six-page sample PDF rendered with Poppler and all pages visually inspected after fixing long titles. Versioned project save/load and selected-run PDF/CSV/JSON/PNG/SVG export.
  Verify round trips, changed/missing sources, safe writes and report layout.
- [ ] 5: release acceptance remains partial; software verification is recorded
  below, independently of experimental-data and human acceptance.

## Test strategy

Keep all baseline tests. Add pure state/adapter tests for region identity,
processing, revision invalidation, method isolation, source hashes and run
history. Use real Tk on Windows for exactly three stages, one method panel,
cross-stage context, async-result isolation, project/report selection and
visible Monte Carlo access. Run small deterministic numerical references and
frozen executable smoke; do not equate these with uncertainty coverage or
experimental validation. Screenshots must be actual app captures, not mockups.

## Integration evidence

- Full local regression after core implementation: **182 passed**, 135.65 s.
  Additional final workflow tests were then added; the completed Windows run
  below includes them.
- Commit `5897943d14ce3c13ddc103f2f3d227fdf6b6be90`: **185 Windows tests passed**.
  [Windows run 40031596606](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40031596606)
  built the one-file executable and verified all nine icon sizes, demo analysis,
  classic real-Tk dialogs/Explorer/MC, and the new frozen workflow.
- The frozen workflow exercised three stages, peak/method isolation, comparison,
  two seeded Monte Carlo replicates, explicit kinetic fitting, portable project
  round-trip, and selected PDF/CSV/JSON/PNG/SVG exports. Two replicates verify
  execution only; they do not validate uncertainty intervals.
- [Python 3.10/3.11/3.12 run 40031635499](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40031635499)
  passed on Linux. Headless Tk tests are skipped there and required on Windows.
- Final presentation/debounce changes are in `d97b8f3f8604a003b6faa3475873e89f475f53e7`.
  Changed-context/result tests passed locally; the new debounce test passed
  after draining the initial notebook/map events before simulating user edits.
  [Final Windows run 40080837020](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40080837020)
  passed **186 tests** and the complete frozen classic + workflow verification.
  [Final Python matrix 40080840002](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40080840002)
  passed **169 tests with 17 headless GUI skips** on each of Python 3.10, 3.11
  and 3.12. Windows required and passed those GUI tests.
  [Download the workflow preview](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40080837020/artifacts/12555167380).
  This artifact contains code commit `d97b8f3`; later evidence-only commits do
  not change its application code. ZIP SHA-256:
  `2d39fdedc7f913c5995a98c366528e6d5337793cf1d4a9b3d78dfbc880351210`.
  Three Matplotlib layout warnings were emitted during GUI tests; they are
  retained as evidence for the open visual/scaling acceptance gate.
- Existing `analysis.py`, `kinetics.py`, `kinetics_explorer.py`,
  `kinetics_uncertainty.py`, and `cli.py` have no diff against the working beta.
- The original beta checkout is clean. Main and beta branch references were not
  changed; [draft PR #10](https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/10)
  targets beta from the isolated feature branch.

## Remaining publication gates

- [ ] Rights-cleared independent experimental/literature benchmark datasets,
  with acquisition conditions, expected behavior and scientific review.
- [ ] Uncertainty-coverage validation across realistic noise, drift and model
  misspecification. Existing MC remains explicitly conditional/exploratory.
- [ ] Human workflow acceptance, including keyboard navigation and supported
  Windows display scaling. Automated real-widget geometry checks at 1100×720
  pass, but are not equivalent to visual/usability acceptance.
- [ ] Actual GUI screenshots for the guide. The interactive test window was
  found, but capture failed with `FrameArrived timed out: timed out waiting on
  channel`, then `window capture timed out: timed out waiting on channel` after
  fresh window selection. No GUI screenshots or visual acceptance are claimed.
- [ ] Release review and explicit decision to merge/publish. This branch remains
  a development preview; no stable release or merge has been performed.




