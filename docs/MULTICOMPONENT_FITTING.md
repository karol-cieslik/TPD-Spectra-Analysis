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

These truth-informed synthetic checks verify numerical consistency under the
specified model. They do not validate blind decomposition of arbitrary spectra,
physical state assignments, experimental mechanisms or confidence-interval
coverage. The original single-component and legacy two-state engines are
preserved for compatibility.
