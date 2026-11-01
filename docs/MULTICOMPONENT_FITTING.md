# Simultaneous overlapping-component fitting

The Modeling workspace can fit one, two or three **independent kinetic
populations simultaneously to the same measured spectrum**. The GUI uses the
entire selected dataset for this operation; named regions remain useful for
navigation and single-component methods, and do not crop the simultaneous fit.
Fitting separate cropped regions is not a decomposition of overlapping contributions.

This is an exploratory inverse model. Three visible features do not establish
three physical adsorption states or identify three desorption mechanisms.

## Physical model and supplied assumptions

For each component, the existing Polanyi–Wigner coverage solver evaluates

\[
\frac{d\theta_i}{dT}=-\frac{\nu_i}{\beta}\theta_i^{n_i}
 \exp[-E_i/(k_BT)],\quad \theta_i(T_{\rm start})=\theta_{0i},
\]

\[
I(T)=\sum_i A_i\nu_i\theta_i(T)^{n_i}\exp[-E_i/(k_BT)]
 +b_0+b_1(T-T_{\rm ref}).
\]

`T` is kelvin inside the equation; the interface accepts degrees Celsius.
`beta` is the positive constant heating rate in K/s. `T_ref` is the mean
temperature of the supplied interval. Scales `A_i` are nonnegative detector
factors. The residual is **observation minus the complete sum including the
shared baseline**, never observation minus one component.

The model assumes independent populations, no transfer or exchange between
them, no readsorption, constant component energies/prefactors/orders, a linear
temperature ramp and a signal proportional to desorption rate. Sequential
reaction steps, lateral interactions, transport limitations and instrument
response are not represented. The single-path limitation of ordinary PW
analysis and the consequences of exchange are discussed by
[Dickbreder, Bechstein and Kühnle, *Crucial impact of exchange between layers on temperature
programmed desorption* (2021)](https://doi.org/10.1039/D1CP01924D).
Adding independent rates is the explicitly chosen model here, not a claim that
that paper validates this implementation.

The initial implementation fits **each energy and detector scale jointly**.
Each component's order, prefactor and initial normalized coverage are supplied
and held fixed. Different positive fixed orders are allowed. A fractional order
is a phenomenological hypothesis; a good fit does not identify a microscopic
mechanism. The classical dependence on heating schedule and supplied kinetic
assumptions is described by
[Redhead, *Thermal desorption of gases* (1962)](https://doi.org/10.1016/0042-207X(62)90978-8).

Holding these parameters fixed deliberately limits an otherwise weakly
constrained single-spectrum problem. It does **not** establish the true
prefactor or order. Test alternative physically justified assumptions and
seek independent coverage/heating-rate measurements before physical inference.

Coverage is dimensionless under the existing normalized convention, with
`0 < theta0 <= 1`; prefactors are expressed in s⁻¹ under that convention.
Coverage must be defined at the **first supplied temperature**. Include the
full relevant low-temperature onset and high-temperature tail. Changing
coverage normalization while keeping the same numerical prefactor is generally
incorrect for non-first-order kinetics: writing `theta = theta0*phi` changes
the normalized prefactor to `nu*theta0**(n-1)`. The fitter preserves each
supplied coverage explicitly.

Zero-order multicomponent fitting is unavailable in this first increment.
Its moving depletion boundaries need a separate validated search; the existing
single-state zero-order depletion-edge workflow remains available. Positive
orders below one are supported, but their finite depletion edges prevent
reporting smooth local-linear intervals in this implementation.

## Workflow and numerical safeguards

### Quick two-peak workflow (v0.11.0b7 candidate)

1. Open a spectrum, select its dataset and a named navigation region, then use
   **Modeling → Fit 2 Peaks…**. Two rows are created; this button opens a
   configuration dialog and does not start fitting automatically.
2. Verify the heating rate in K/s. For recognized publication examples, review
   **Confirm source suggestion…** and explicitly accept or reject it. Opening
   published data never silently applies the rate. Confirmation changes Modeling
   for this dataset/region only; Kinetic Analysis has separate settings. Exact
   bundled CSV bytes or attached publication metadata identify the suggestion;
   a familiar filename alone is insufficient. Unknown rates require user input.
3. Click approximate positions on the dialog spectrum (clicks cycle Peak 1,
   Peak 2), or type the positions in °C. **Re-estimate from positions** refreshes
   the energy guesses and bounds; Fit also applies pending position edits.
   New rows fix first order, prefactor `1e13 s^-1` and coverage one. Existing
   definitions are retained and their fixed assumptions are displayed.
4. **Fit Both Peaks** fits the entire processed dataset. Inspect the individual
   blue dashed / green dash-dot components, orange complete sum, separate dotted
   baseline and observation-minus-sum residual panel. Colors and line styles
   both distinguish components in live and exported plots.
5. Read the quality title/status and **Assumptions & warnings**. Convergence is
   not model adequacy. Export the fit or save the project to retain the source
   rate confirmation, settings, individual curves, multistart seeds and diagnostics.

**Advanced settings** reveals fixed kinetic parameters, energy bounds, component
count, offset/drift, evaluation budget and multistart. Use **Overlapping
components…** for an existing one- or three-row hypothesis. The two-peak shortcut
replaces the dialog's row count only when needed; it does not overwrite stored
results. Apply/refit to record new definitions. Named single-peak regions do not
crop a simultaneous fit. **Single-state view** retains the original workflow.

For each selected position, the seed uses the existing *first-order* Redhead
approximation `E = k_B T_p [ln(nu T_p / beta) - 3.64]`, with `T_p` in kelvin.
The ±30% energy bounds are heuristic search limits, **not confidence intervals**
or physical prior evidence. At −20 °C, `nu=1e13 s^-1`, `beta=3 K/s`, the guess
is about 0.67 eV, rather than the 1.25/1.55 eV synthetic-demo inputs. Change
bounds if scientifically justified. Position re-estimation refuses non-first-order
rows; edit their energies in Advanced. Automatic maxima/shoulder hints are
numerical aids, never a state-count or mechanism determination. Hint smoothing
does not alter the fitted observations.

### Advanced truth-informed exercise

1. Open `three_overlapping_peaks.csv` or its moderate-noise variant from
   **Open Example Dataset**. Inspect the full signal and known synthetic truth.
2. Inspect the entire selected dataset: this is the common grid used by the
   simultaneous GUI fit, regardless of the selected named region. The Python
   API can instead be supplied an explicit complete common interval.
3. Define the component labels, fixed orders/prefactors/coverages, initial
   energies and energy bounds. The bundled three-state reference uses
   `E = 1.18, 1.26, 1.34 eV`, `nu = 1e13 s^-1`, order one and generating
   coverages `1, .7, .5` at 50 °C. Alternatively use coverage one and
   detector scales `10000, 7000, 5000` for this **first-order** example only.
4. Run the simultaneous fit. Inspect observations, individual components,
   their sum, residuals and the warnings before interpreting parameter values.
5. Compare justified component-count hypotheses and export the supplied
   settings, individual parameters and complete fitted curves.

The solver uses bounded least squares with nonnegative scales, energy bounds
and optional bounds on the common offset/drift. Initial scale/baseline estimates
come from constrained linear least squares at the initial energies. This only
initializes the **joint nonlinear fit**; it does not fit each component to a
separate experimental region. Residuals are scaled by the measured signal range.
Cached physical rate calculations and central energy differences larger than
ODE numerical noise improve derivative reliability. Deterministic alternative
energy starts reduce sensitivity to a single guess, without guaranteeing a
global optimum. Failed starts are counted; if none converges, the calculation
raises a clear error and supplies no successful result. Cancellation is checked
during residuals, derivatives and physical rate evaluations.

For two/three components, multistart now adds first-order thermal seeds from
visible features, the measured temperature span, and the maximum plus its
high-temperature tail, with ±8% energy perturbations. Seeds are clipped to each
supplied component's bounds; no bounds are silently relaxed. For non-first-order
rows these are only numerical starts, not Redhead energy estimates for that order.
Scale coordinates are normalized at a temperature-informed reference rather than
an exponentially vanishing demo-parameter rate. The best finite, successfully
converged result is selected by residual sum of squares. Attempts and seeds are
exported. Turning multistart off retains the supplied energy start. The existing
one-component starts and the separate single-state kinetic engines are unchanged.

### Failure screening and Zaki stress test

`success` records optimizer convergence. `diagnostics.fit_quality` separately
reports `baseline_only`, `poor_fit`, `collapsed_components` or `review_required`.
Baseline-only means fitted kinetic variation is below 5% of observed range or
the relative RSS improvement over the same allowed baseline-only model is below
1%. A component is collapsed if its integrated fraction is below 1% or its peak
height is below 1% of observed range. Normalized RMSE above 0.15 flags poor fit.
Bounds, correlations, indistinguishable/exchangeable profiles and residual
autocorrelation remain separately diagnosed. These are engineering screens;
`review_required` is not a scientific acceptance certificate. Failed/cancelled
optimization preserves prior results. Converged but inadequate fits remain
inspectable/exportable with warnings; they must not be reported as supported
decompositions merely because count-ranking weights exist.

The bundled [Zaki et al. (2018)](https://doi.org/10.1039/C8CP02333F) D₂O/Fe₃O₄(111)
digitization has a measured graphical maximum at −17.65 °C and source catalog
heating rate 3 K/s. Supplying demo guesses 1.25/1.55 eV to the old narrow search
reproduces a nearly constant baseline ≈0.212, negligible components and normalized
RMSE ≈0.261. New thermal multistart gives ≈0.126 on this retained trace. Residuals
remain strongly serially correlated and labeled uncertainty is withheld. This
is a numerical regression/stress test, **not experimental energy truth or proof
of two independent first-order populations**. Digitized time is constructed
from the nominal ramp, not measured acquisition time. Normalized figure height,
multiple populations and recombination limit physical interpretation.

Labels remain in the supplied order. There is no energy sorting that could
silently exchange a first-order component with a second-order component.
Well justified separate energy bounds can help preserve interpretation, but
the bounds themselves are part of the conditional hypothesis and are exported.
Components with the same fixed order and effective normalized prefactor
`nu*theta0**(n-1)` have the same family of kinetic shapes. When their energy
bounds allow both fitted energies to be exchanged, their user labels are
globally exchangeable even if the peaks are separated and the local Jacobian
looks well conditioned. The fitter explicitly warns and withholds labeled
intervals in this case. This detects exact shape-family permutations; it is
not a complete search for all global ambiguities.

## Conditional uncertainty and model comparison

The full joint residual Jacobian includes cross-component correlations. When
the fit is locally well conditioned and residual assumptions are plausible,
approximate local-linear Student-t 95% intervals use
`cov = (J.T @ J)^-1 * RSS/(N-p)` in the scaled optimizer coordinates and are
converted back to physical energy/scale units. Covariance and correlation are
constructed from an SVD after normalizing Jacobian columns, then transformed
back; this avoids silently discarding directions merely because parameter
coordinates have different units. These intervals condition on
fixed orders, prefactors, initial coverages, baseline choice, number of
components and iid homoscedastic Gaussian errors. They exclude uncertainty in
those assumptions, instrument calibration and temperature/heating rate.
They are **not experimentally calibrated confidence intervals**. SciPy's
[covariance documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html)
explains the local-linear approximation and why rank or conditioning problems
make it unreliable.

Intervals are withheld for deficient/ill-conditioned Jacobians, strong
parameter correlation, exchangeable labels, active or near bounds or intervals crossing constraints, negligible or nearly identical
components, substantial residual serial correlation, poor residual fit,
effectively zero residual variance and sub-first-order depletion edges.
Thresholds in the implementation are conservative screening rules, not formal
identifiability tests. Passing them does not prove global identifiability or
correct interval coverage. Fixed parameters have no estimated uncertainties.

Count comparisons use the same temperature points, observations, error model
and baseline settings. Parameter counts include all fitted energies/scales
and shared nuisance parameters; the existing AIC/AICc/BIC helper also counts
the estimated residual variance. The Python convenience function compares
the first `n` definitions for each requested count; inspect each candidate's
retained fixed definitions and reorder/edit them to compare other hypotheses.
Failed candidates retain explicit errors and receive no ranking weight.
If any candidate fails, the reported relative weights are conditional on the
converged subset; they do not establish the preferred count among all requested
hypotheses. Resolve the failed fits or disclose their exclusion before using
the ranking.

AICc/BIC differences and relative Akaike weights are **heuristics**, not state
counts or mechanism probabilities. Coincident components and vanishing
amplitudes create nonregular cases analogous to singular mixture models.
[Watanabe (2013)](https://www.jmlr.org/papers/v14/watanabe13a.html) explains why
ordinary BIC's regular-model approximation fails for singular models. This is
a caution applicable by analogy, not a theorem establishing a corrected
criterion for this kinetic model. No singular-model correction or Bayesian
evidence calculation is implemented.

Multicomponent Monte Carlo is not implemented. The existing single-component
Monte Carlo must not be interpreted as uncertainty for a simultaneous fit.
Future resampling must jointly refit all populations and handle weak components,
convergence failures and label ambiguity before offering calibrated intervals.

## Validation scope

`tests/test_multicomponent.py` compares the new inverse model with an independent
separable PW solution using cumulative trapezoidal quadrature on a 0.005 K
grid. Three-state first-order and mixed-order/nonunit-coverage tests require
energy recovery within 0.002 eV, detector scales within 2% and normalized RMSE
below 0.001 for identifiable clean examples. Tests also cover noisy offset/drift,
conditional interval availability, ambiguous components, sub-first-order edges,
model-count consistency, nonconvergence, cancellation, deterministic starts,
invalid input, exchangeable-label ambiguity, parameter/detector-unit scaling
and strict JSON serialization.

`tests/test_two_peak_fitting.py` adds independent low-temperature quadrature
recovery (0.002 eV / 2% tolerances), the retained Zaki failure/rescue, excluded-peak
bounds, baseline-only data, invalid guesses, and source-rate identity checks.
`tests/test_two_peak_workflow.py` checks real Matplotlib click dispatch, explicit
accept/reject, rate-confirmation persistence, invalid/coincident positions,
non-first-order protection and the original single-state view. Existing tests
cover worker failure/cancellation, count comparison, project round trips and exports.

These truth-informed synthetic checks verify numerical consistency under the
specified model. They do not validate blind decomposition of arbitrary spectra,
physical state assignments, experimental mechanisms or confidence-interval
coverage. The original single-component and legacy two-state engines are
preserved for compatibility.
