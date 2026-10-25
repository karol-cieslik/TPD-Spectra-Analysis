# Fixed single-state zero-order fitting (0.11.0b3)

The fixed-zero-order path now profiles the sampled depletion edge rather than
asking a local finite-difference optimizer to cross its discontinuity. Positive
orders retain the existing numerical integrator and least-squares algorithms.
Fixed-order initialization respects the requested order; only free-order initial
guesses are clipped to the free-order search interval.

For candidate last-occupied sample j, the signal is

`S_i = H exp[-E/k_B (1/T_i - 1/T_j)] + b` for `i <= j`, and `S_i = b` afterwards.

Every boundary with at least three rising-side samples is profiled, including a
no-depletion candidate. A bounded scalar energy search over 0.05–8 eV solves H
and optional constant b by linear least squares at each trial. The lowest
residual candidate is selected. Initial E/nu guesses do not choose the zero-order
solution. Maximum fit evaluations applies per boundary, plus endpoint checks.
Cancellation is checked at every trial. A failed energy search is not returned
as a successful fit.

The selected edge needs at least three post-depletion samples and fitted height
above three residual standard deviations. This is a screening heuristic, not
statistical proof of a resolved physical edge. Missing/truncated or unresolved
edges are rejected. High residuals and energy bounds generate warnings.

With normalized coverage one at the selected interval start, let
`I(T) = integral exp[-E/(k_B u)] du` from that start to T. Then
`beta/I(T_next) <= nu < beta/I(T_j)`. The corresponding detector-scale bounds
follow from `A*nu = H exp[E/(k_B T_j)]`. The displayed pair uses the geometric
midpoint of the compatible prefactor range. Existing prefactor (1e3–1e30 s^-1)
and scale (1e-30–1e30) bounds restrict these ranges; incompatible optimal shapes
are rejected. The forward physical curve is unchanged by this representation.

These are **conditional sampling brackets at fixed fitted energy**, not
confidence intervals. They exclude energy, baseline, calibration, model and
coverage uncertainty. They persist in projects, reports and Explorer CSV/JSON.
Monte Carlo records each refit's brackets but withholds percentiles of arbitrary
representative zero-order prefactors. Successful energy-refit ranges remain
conditional on the same assumptions and the existing minimum-success rule.

Information criteria count energy, height and the searched edge, plus baseline
when fitted. The usual AICc correction is heuristic for this nonregular edge
model: rankings/weights are exploratory, not mechanism probabilities.

Older zero-order results and modeling sessions remain readable but become stale
for new calculations. Recompare before Monte Carlo or transfer. The change covers
single-state fixed zero order, including its Explorer/MC reuse. Legacy multi-state
and global zero-order optimizers are not corrected or validated by this change;
their results carry an explicit warning.

Validation includes independent quadrature references over energies, prefactors,
ramps, coverages and sampling intervals; noise/baseline recovery; start and signal
scale invariance; duplicate temperatures; truncation, bounds, evaluation limits
and cancellation; project/report/export and conditional Monte Carlo handling.
The original example's 0.02 normalized residual tolerance is unchanged. These
checks do not replace independent scientific or experimental validation.
