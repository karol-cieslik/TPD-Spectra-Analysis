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
- [ ] 5: full regression and frozen workflow checks; document actual behavior,
  limitations and unverified external-data/human/scaling acceptance.

## Test strategy

Keep all baseline tests. Add pure state/adapter tests for region identity,
processing, revision invalidation, method isolation, source hashes and run
history. Use real Tk on Windows for exactly three stages, one method panel,
cross-stage context, async-result isolation, project/report selection and
visible Monte Carlo access. Run small deterministic numerical references and
frozen executable smoke; do not equate these with uncertainty coverage or
experimental validation. Screenshots must be actual app captures, not mockups.




