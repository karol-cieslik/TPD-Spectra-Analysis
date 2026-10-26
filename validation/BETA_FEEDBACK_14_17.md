# 0.11.0b4 candidate: beta feedback verification

Separate branch: `fix/beta-feedback-14-17`, based on fetched `main` f44bc4d.
PR: https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/19
No merge or release publication was performed.

## Changes and root causes

- #14: Modeling cleared its figure before requiring a region, so a missing
  selection left a blank canvas. Viewing raw data is now independent of region
  validation. The desktop opens the bundled demo with a prepared first region;
  the raw trace remains visible in Modeling and Kinetic Analysis.
- #16: Numerical work already ran in a worker thread; feedback was confined to
  the general status line. A fixed progress interface now reports completed
  replicates, percentage, elapsed/estimated time and fitting/ranking failures.
  Main-thread cancellation also rejects success already waiting in the queue.
- #17: Physical clean generators already existed, but demonstration observations
  were mostly noiseless. Shared detector-noise generation now supplies seeded
  1/2/5% examples and offset/drift while retaining independent clean truth.
  All 16 original beta CSV files retain their exact bytes; five variants were added.
- #15: The existing GUI compared single-state hypotheses against a composite.
  The new 1–3 component path fits the complete sum of independent physical PW
  rates, with fixed per-component order/prefactor/coverage and joint energy/scale
  estimates. It preserves individual curves, baseline, sum and residuals, compares
  explicit component-count hypotheses and saves/exports all submitted assumptions.

Parameter and warning views prevent the canvas from pushing scientific results
off smaller windows. The component editor keeps action buttons fixed and offers
horizontal/vertical scrolling; explicit Tk scaling 1.333 and 2.0 tests are included.

## Local checks actually executed

Windows 10, Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1, pandas 3.1.0,
Matplotlib 3.11.2. Tk tests used a real Windows display, with an isolated venv
and workspace-local pytest temporary folders. Counts below overlap; do not add them.

- Phase 1: 57 passed (`phase1-tests.xml`), including the complete default GUI
  simulation/comparison/seeded Monte Carlo/transfer/explicit-fit path.
- Phase 2: 27 passed (`phase2-tests.xml`); duplicate dispatch, progress on the
  GUI thread, responsiveness, cancel/error/retry and queued-success cancellation.
- Physical examples/reference checks: 61 passed, one Tk test deselected in that
  focused run (`phase3-tests.xml`); real Tk coverage appears in other runs.
- Noisy default workflow: 24 passed (`phase3-workflow-tests.xml`);
  plot/export styling: 8 passed (`phase3-style-tests.xml`).
- Component engine: 24 passed (`phase4-engine-tests.xml`), using independent
  quadrature truth, mixed positive orders/nonunit coverage, SVD uncertainty,
  detector/parameter-unit scaling, degeneracy, label permutations and cancellation.
- Source package workflow passed from an unrelated working directory
  (`source-beta-feedback.json`): 21 imports, default selection/raw plot, zero-order
  fitting/project/report/short MC, three-component editor/fitting/project/export,
  offline feedback and no callback errors. This is explicitly a source run.
- Five-page Quick Start rendered with Poppler and every page visually inspected.
- Final full suite: **318 passed, zero failures/errors/skips in 242.841 seconds**
  (`beta-feedback-all-tests.xml`). The high-DPI/GUI isolation checks also passed
  together: 14 tests (`final-dpi-tests.xml`).

Actual 500-replicate worker runs, first-order hypothesis only, seed 42,
multistart off and 150 evaluations:

| Input | Completed fits | Fit/ranking failures | Elapsed | GUI heartbeats | Evidence |
| --- | --- | --- | --- | --- | --- |
| Pre-update clean default | 500 | 0 / 0 | 141.578 s | 1,782 | phase2-500-run.json |
| Seeded 2% noisy default | 500 | 0 / 0 | 180.203 s | 2,314 | phase3-500-run.json |

Both runs retained the raw trace and immutable observations, with monotonic
progress to 100%. Input hashes/settings are recorded. These are software-path
checks, not validation of an uncertainty procedure or a mechanism assignment.
Reproduce with `python scripts/validate_monte_carlo_gui.py --output <new-json>`.

## Failures found and corrected during development

An initial test used a string where the private import adapter expects a Path;
it was corrected. Shared Windows temporary-folder permissions were avoided with
workspace-local pytest temp folders. New exact-noise checks were adjusted only
for the documented `%.12e` CSV quantization; existing scientific tolerances were
preserved. A prior preview/save test assumed noiseless, warning-free input: it now
checks clean completion and noisy completion-with-warnings explicitly. Source
smoke testing caught an empty Tk wrap-length resize callback, which was fixed.
Full-suite runs exposed process-wide Tk scaling leaking from branding tests;
fixtures restore it, and component scrolling/actions are tested at both scales.
No scientific warning was suppressed to make a test pass.

The first CI run exposed one additional generator-test assumption on all
platforms/Python versions: mathematical libraries can change the final printed
signal digit. The test now demands exact CSV/JSON regeneration twice in the
same environment, and tight export-precision agreement with shipped fixtures
across environments. Seeds, physical inputs, grids, units and recovery limits
remain exact; each artifact's own recorded hashes are verified. The focused
portability/reference suite passed 61 tests with one GUI test deselected
(`ci-portability-tests.xml`). Shipped CSV bytes and scientific recovery tolerances
were unchanged by this correction.

Independent code review also led to SVD covariance instead of normal equations,
valid exported correlation diagonals, detector-unit invariance and withholding
of labeled intervals when equivalent components can exchange identities.

## Scientific limits and remaining acceptance

The overlapping-component feature is an initial constrained increment. Orders,
prefactors and initial normalized coverages are assumed, not inferred; independent
populations exclude exchange, readsorption, interactions, nonlinear ramps and
instrument response. Local Student-t intervals are conditional approximations,
not experimentally calibrated confidence limits. Count comparisons use explicit
prefix definitions and heuristic AICc/BIC; failed counts remain visible and their
exclusion conditions relative weights. Three features do not establish three states.

No multicomponent zero-order depletion search or joint component Monte Carlo is
provided. Legacy single-component methods remain available. Further real-data,
blind-recovery, model-misspecification and interval-coverage studies are needed
before publication-grade physical claims.

The Windows CI workflow builds the executable and smoke-tests the frozen package,
including the new three-component path, from an unrelated working directory.
Its result is reported separately on the PR. Automated Tk checks do not substitute
for manual clean-machine Windows 10/11 testing, additional display scaling,
keyboard/accessibility review or independent human scientific sign-off.
