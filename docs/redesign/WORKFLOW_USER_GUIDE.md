# Three-stage workflow guide — 0.11.0b3 beta

TPD Spectra Studio by **Karol Cieślik**. This guide describes the three-stage
workflow in the `main` branch's 0.11.0b3 beta. It is intended for practical
testing, not as a claim of validated experimental analysis.

## First run with the synthetic example

The desktop opens `synthetic_two_peak_demo.csv` with a prepared 70–210 °C
first-peak interval. Simulate parameters, compare the checked model hypotheses,
then run seeded Monte Carlo. For a quick software check use only first order,
multistart off, 2 replicates and seed 42; parameter uncertainty needs substantially
more refits. Select a converged row to transfer initial guesses to Kinetic Analysis,
then explicitly fit. This single-state approximation does not explain both peaks.
The original spectrum stays visible in Modeling and Kinetic Analysis, including
when no region exists. Arbitrary imports require an explicit named interval:
enter bounds and **Add peak** in Spectra & Preparation. Region selection does not
deconvolve overlapping contributions.

The default observations contain reproducible iid Gaussian detector noise with
standard deviation 2% of the clean maximum (seed 20261026). The adjacent JSON
records the independent physical generating parameters and clean reference.
Files ending `_clean`, `_low_noise`, `_moderate_noise`, `_high_noise` and
`_baseline_drift` offer 0%, 1%, 2%, 5% and offset/drift comparisons. Noise is
added after the physical calculation; negative noisy observations are retained.
Leading-edge logarithms become unreliable near the detector noise floor. Use
the clean first-order chooser example for the numerical walkthrough below.
Markers identify observations, solid/dashed curves identify fitted models,
and residuals show observation minus prediction.

1. Click **Open Example Dataset** and select **first order single peak**. The
   chooser loads a synthetic 801-point spectrum with a 1 K/s ramp and a named
   full-trace interval. The source time unit is milliseconds; temperature is Celsius.
2. In **Spectra & Preparation**, inspect the plot, selected dataset and named
   peak. To define another interval, enter a name and From/To temperatures,
   then click **Add peak**. Inspect both tails before interpreting a peak.
3. In **Kinetic Analysis**, select **Redhead**, confirm the 1 K/s ramp and
   assumed 1e13 s⁻¹ prefactor. The displayed estimate should be approximately
   1.2 eV (within 2.5% of the synthetic input). This is not a confidence interval.
4. Select **Leading edge**, use 90–110 °C, and inspect the transformed plot
   and residuals. Do not fit the full peak as a leading edge. Values update
   after a short pause in typing. The reported energy interval describes
   regression scatter only; the signal does not identify an absolute prefactor.
5. Save results with **Save labeled result…**. Switch to another peak or method
   to create independent runs. Reopen a saved run to restore its method settings.
   An old run is marked stale if peak boundaries or processing have changed;
   reopening does not silently change shared processing or peak definitions.
6. Use **Report / Export…** to review and select saved runs, then choose a
   destination. A new folder receives PDF, parameter CSV, curve CSV, JSON,
   PNG and SVG files. Existing report folders are never overwritten.

## Preparation and provenance

- The imported arrays remain immutable. Temperature cleaning is the existing
  importer behavior; the import report records affected original records.
- Smoothing controls initially preview the plot. **Apply smoothing / baseline
  to analysis** records a dataset-wide recipe. Constant baseline subtraction is
  in detector-signal units. Undo/reset are available.
- Normalization affects display only. It never changes the fitted signal.
- Changing the recipe or peak boundaries marks previous results stale. Saved
  results retain their original recipe, bounds, source hash and effective inputs.
- **Drag interval** enables draggable plot handles; press Add/Update peak to
  retain the selection. Turn off plot pan/zoom first. Numeric limits are also
  available. The selected dataset and peak remain visible across all three tabs.
- **Include** applies to the classic batch workspace. Workflow calculations
  always act on the single selected dataset and peak.

## Modeling and Monte Carlo

**Modeling & Order Identification** exposes the existing numerical engines.
Simulate parameters to overlay a manual hypothesis. Simulation order, initial
coverage, amplitude and baseline are distinct from optimized values. Coverage
must be in (0, 1]; amplitude is a positive detector scale.
Parameter edits trigger a debounced simulation preview when no calculation is
running. **Simulate parameters** also runs it explicitly; edits made during
another calculation can be previewed with this button after that work finishes.

**Compare models** fits the checked zero, first, second and fractional-order
candidates. Fractional order is fitted in the engine's 0.2–3 interval; this is
not a coverage-dependent model. Fits normalize coverage to one at the selected
interval start and optimize signal scale and, optionally, a constant baseline.
Multistart uses the existing deterministic starts. Inspect residuals and each
candidate's convergence/identifiability warnings. Column headings sort the table.

Set a seed and replicate count, then **Run Monte Carlo** after a current model
comparison. This is parametric Monte Carlo refitting: iid Gaussian noise around
the lowest-AICc converged reference, using the reference residual noise estimate.
It is neither microscopic kinetic Monte Carlo nor Bayesian MCMC. Rank counts
measure conditional stability, not probabilities of physical mechanisms.
Parameter ranges are withheld below 100 successful refits and have not been
coverage-validated. Correlated noise, drift, calibration and model uncertainty
are not represented. A two-replicate test only checks the software path.

The Monte Carlo bar and **Run Monte Carlo / Cancel** buttons remain above the
plot while the parameter sidebar scrolls. Feedback shows completed/total
simulations, percentage, elapsed time and an approximate remaining time.
Completion lists successful and failed individual fitting attempts separately
from incomplete model rankings. Cancel shows Cancelling until a numerical
evaluation returns, then preserves the previous successful result. Worker errors
are shown beside the bar and in the status area; calculations can be retried.
All calculation buttons are disabled while one worker is active.

Simulations, comparisons, optimization and Monte Carlo run outside the UI
thread. Cancel takes effect between numerical evaluations. A cancelled or failed
calculation preserves previous successful output. Switching context during work
does not move its result to the newly selected peak. Open projects and dataset
removal wait until work finishes. Classic and workflow numerical workspaces are
used separately because the legacy LSODA integrator is not reentrant.

Select a converged row and choose **Use selected model in Kinetic Analysis**.
This explicitly transfers a hypothesis and initial guesses; it does not create
a final fit. In Stage C press **Calculate / Fit selected peak** to optimize.

## Kinetic interpretation

The parameter panels show the equation for the selected method above its inputs.
Modeling shows the Polanyi–Wigner rate, coverage depletion and detector-signal
relationship; Monte Carlo shows the Gaussian perturbation used to generate each
refit dataset. **Symbols and assumptions** expands the definitions and units.
These explanations are read-only and do not change parameters or run a fit.

- Leading edge estimates an apparent slope energy under rate-proportional
  signal and approximately unchanged coverage. It does not assign zero order.
- Classical Redhead assumes first order, a supplied prefactor and a linear ramp.
  A boundary maximum produces a warning. No confidence interval is fabricated.
- Polanyi–Wigner fitting retains the positive-order numerical engine. Fixed
  zero order uses the [depletion-profile fitter](../ZERO_ORDER_FITTING.md) and
  reports conditional prefactor/scale brackets rather than a unique pair.
  Inspect residuals, convergence and identifiability diagnostics. One spectrum
  can admit competing parameter combinations; a good fit does not prove order.
- The default heating rate of 1 K/s is an editable assumption. Confirm it from
  acquisition conditions. Confirm input units and calibration before analysis.
- Existing multi-state/global, batch, diagnostic and CLI paths remain in the
  **Classic / batch workspace**, `tpd-spectra-classic`, or `--classic` launcher.
  The numerical engine and CLI options are unchanged.

## Projects and reports

Save portable `.tpd.json` projects to retain embedded imported arrays, recipes,
named peaks, method inputs, results, model sessions, Monte Carlo records and
report selections. Schema version 1 has embedded-data checksums. Open verifies
checksums and available source hashes. Missing or changed source files produce
a warning; the original embedded data remains available. Unsupported schema
versions are rejected without replacing the current workspace.

Reports include only selected saved kinetic runs. Associated model comparisons
are identified as separate exploration with their own settings. Full MC records
are in `results.json`; PDF summaries avoid printing hundreds of raw record IDs.
Unavailable metadata and uncertainty are explicit. A `COMPLETE.txt` marker is
written only after all exports succeed; a failed export may leave an incomplete
folder for diagnosis. The report-selection dialog is a content preview; it is
not an interactive PDF viewer.

## Remaining release acceptance

Automated synthetic and regression checks are software verification, not
experimental validation. Publication still requires rights-cleared independent
data benchmarks, scientific review of applicability/uncertainty, and user tests
on target Windows displays/scaling. See `IMPLEMENTATION_CHECKLIST.md` for actual
evidence and remaining checkpoints. Do not infer these are complete from a
successful build.
