"""Conditional simultaneous fitting of up to three independent PW populations.

Each component uses the existing coverage ODE. Orders, prefactors and initial
coverages are supplied hypotheses, not additional estimates from one spectrum.
The optimizer fits every energy and nonnegative detector scale simultaneously.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from scipy.optimize import least_squares, lsq_linear
from scipy.stats import t as student_t

from .kinetics import simulate_tpd, _fit_information_criteria


@dataclass(frozen=True)
class ComponentDefinition:
    label: str
    order: float = 1.0
    energy_eV: float = 1.2
    prefactor_s_inv: float = 1e13
    initial_coverage: float = 1.0
    energy_bounds: tuple[float, float] = (0.05, 8.0)


@dataclass
class ComponentFitResult:
    success: bool
    message: str
    components: list[dict]
    temperature_c: np.ndarray
    observed: np.ndarray
    prediction: np.ndarray
    component_predictions: list[np.ndarray]
    baseline_prediction: np.ndarray
    residuals: np.ndarray
    beta_k_s: float
    baseline: float
    drift_per_K: float
    baseline_reference_c: float
    rmse: float
    normalized_rmse: float
    aic: float
    aicc: float
    bic: float
    n_points: int
    n_parameters: int
    starts_attempted: int
    starts_converged: int
    diagnostics: dict
    warnings: list[str]
    uncertainty_note: str


@dataclass
class ComponentCountCandidate:
    count: int
    fit: ComponentFitResult | None
    error: str | None
    delta_aicc: float | None = None
    akaike_weight: float | None = None


def _definitions(components):
    definitions = tuple(c if isinstance(c, ComponentDefinition) else ComponentDefinition(**c)
                        for c in components)
    if not 1 <= len(definitions) <= 3:
        raise ValueError('Define one to three kinetic components.')
    labels = [c.label for c in definitions]
    if any(not isinstance(s, str) or not s.strip() for s in labels) or len(set(labels)) != len(labels):
        raise ValueError('Component labels must be nonempty and distinct.')
    for c in definitions:
        if not np.isfinite([c.order, c.energy_eV, c.prefactor_s_inv, c.initial_coverage]).all():
            raise ValueError(f'{c.label}: kinetic parameters must be finite.')
        if c.order <= 0:
            raise ValueError('Multicomponent orders must be positive. Use the single-state depletion-edge method for zero order.')
        if c.prefactor_s_inv <= 0 or not 0 < c.initial_coverage <= 1:
            raise ValueError(f'{c.label}: prefactor must be positive and coverage in (0, 1].')
        bounds = np.asarray(c.energy_bounds, dtype=float)
        if bounds.shape != (2,) or not np.isfinite(bounds).all() or not 0 < bounds[0] < bounds[1]:
            raise ValueError(f'{c.label}: energy bounds must be positive, finite and increasing.')
        if not bounds[0] <= c.energy_eV <= bounds[1]:
            raise ValueError(f'{c.label}: initial energy must lie within its energy bounds.')
    return definitions


def _nuisance_bounds(bounds, unit, label):
    if bounds is None:
        return -np.inf, np.inf
    values = np.asarray(bounds, dtype=float)
    if values.shape != (2,) or not np.isfinite(values).all() or values[0] >= values[1]:
        raise ValueError(f'{label} bounds must be finite and increasing.')
    return tuple(values / unit)


def _jacobian_information(jacobian):
    """Local information without squaring badly scaled raw coordinates.

    Normalize columns before the SVD, construct covariance/correlations there,
    then undo that normalization. A raw pinv(J.T@J) can silently discard small
    but independently identifiable directions when parameter units differ.
    """
    jac = np.asarray(jacobian, dtype=float)
    if jac.ndim != 2 or not np.isfinite(jac).all():
        raise ValueError('The joint residual Jacobian must be finite.')
    norms = np.linalg.norm(jac, axis=0)
    normalized = np.divide(jac, norms, out=np.zeros_like(jac), where=norms > 0)
    _, singular, right = np.linalg.svd(normalized, full_matrices=False)
    tolerance = max(normalized.shape) * np.finfo(float).eps * singular[0]
    resolved = singular > tolerance
    rank = int(np.count_nonzero(resolved))
    condition = float(singular[0] / singular[-1]) if singular[-1] > 0 else float('inf')
    inverse_squares = np.zeros_like(singular)
    inverse_squares[resolved] = 1.0 / singular[resolved] ** 2
    covariance_normalized = (right.T * inverse_squares) @ right
    variances = np.maximum(np.diag(covariance_normalized), 0.0)
    denominators = np.sqrt(np.outer(variances, variances))
    correlation = np.divide(covariance_normalized, denominators,
                            out=np.zeros_like(covariance_normalized), where=denominators > 0)
    off_diagonal = correlation.copy()
    np.fill_diagonal(off_diagonal, 0.0)
    maximum_correlation = float(np.max(np.abs(off_diagonal)))
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        inverse_norms = np.divide(1.0, norms, out=np.zeros_like(norms), where=norms > 0)
        covariance_unit = covariance_normalized * inverse_norms[:, None] * inverse_norms[None, :]
    return covariance_unit, correlation, rank, condition, maximum_correlation


def fit_components(temperature_c, signal, beta_k_s: float, components, *,
                   fit_baseline: bool = True, fit_drift: bool = False,
                   baseline_bounds=None, drift_bounds=None,
                   max_nfev: int = 300, multistart: bool = True,
                   cancelled=None) -> ComponentFitResult:
    """Fit the sum of 1–3 independent physical desorption rates to one trace.

    Temperatures are Celsius; beta is K/s. At the first supplied temperature,
    component coverage equals its supplied fixed ``initial_coverage``. Include
    the complete relevant desorption interval: cropping does not deconvolve it.
    Constant offset and drift are in detector units and detector units/K; the
    intercept is referenced to the mean supplied temperature. Optional nuisance
    bounds have these physical units. A cancelled or nonconverged calculation
    raises rather than returning an apparently valid result.
    """
    definitions = _definitions(components)
    temp = np.asarray(temperature_c, dtype=float)
    sig = np.asarray(signal, dtype=float)
    if temp.ndim != 1 or sig.shape != temp.shape or temp.size < 20:
        raise ValueError('Use matching one-dimensional temperature/signal arrays with at least 20 points.')
    if not np.isfinite(temp).all() or not np.isfinite(sig).all():
        raise ValueError('Remove non-finite measurements explicitly before fitting components.')
    if np.any(np.diff(temp) <= 0) or temp.min() <= -273.15:
        raise ValueError('Use a strictly increasing temperature grid above absolute zero.')
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError('Heating rate must be positive and finite.')
    if isinstance(max_nfev, bool) or not isinstance(max_nfev, (int, np.integer)) or max_nfev < 1:
        raise ValueError('max_nfev must be a positive integer.')
    if fit_drift and not fit_baseline:
        raise ValueError('Fit the shared offset when fitting baseline drift.')
    if baseline_bounds is not None and not fit_baseline or drift_bounds is not None and not fit_drift:
        raise ValueError('Nuisance bounds require the corresponding fitted baseline/drift.')
    span = float(np.ptp(sig))
    # Detector units are arbitrary (for example amperes versus picoamperes).
    # Resolve variation relative to this signal's own floating-point scale;
    # a one-unit floor would reject perfectly valid small-current spectra.
    resolution = max(16 * np.finfo(float).eps * float(np.max(np.abs(sig))),
                     np.finfo(float).tiny)
    if not np.isfinite(span) or span <= resolution:
        raise ValueError('Signal must have a nonzero dynamic range.')
    count = len(definitions)
    reference = float(np.mean(temp))
    temperature_span = float(np.ptp(temp))
    drift_unit = span / temperature_span
    x = (temp - reference) / temperature_span
    baseline_limits = _nuisance_bounds(baseline_bounds, span, 'Baseline')
    drift_limits = _nuisance_bounds(drift_bounds, drift_unit, 'Drift')

    def check_cancel():
        if cancelled is not None and cancelled():
            raise InterruptedError('Simultaneous component fitting cancelled.')

    @lru_cache(maxsize=256)
    def rate(index, energy):
        check_cancel()
        c = definitions[index]
        _, values = simulate_tpd(temp, beta_k_s, float(energy), c.prefactor_s_inv,
                                  c.order, c.initial_coverage)
        if not np.isfinite(values).all():
            raise ValueError(f'{c.label}: non-finite physical rate.')
        return values

    initial_energies = np.array([c.energy_eV for c in definitions], dtype=float)
    scale_units = []
    for i, energy in enumerate(initial_energies):
        peak = float(np.max(rate(i, float(energy))))
        if peak <= np.finfo(float).tiny:
            raise ValueError(f'{definitions[i].label}: initial kinetics produce no signal in this interval; change the energy guess.')
        scale_units.append(span / peak)
    scale_units = np.asarray(scale_units)
    if not np.isfinite(scale_units).all():
        raise ValueError('Initial component rates are too small to scale reliably; change the energy guesses.')

    lower = [c.energy_bounds[0] for c in definitions] + [0.0] * count
    upper = [c.energy_bounds[1] for c in definitions] + [np.inf] * count
    linear_lower, linear_upper = [0.0] * count, [np.inf] * count
    if fit_baseline:
        lower.append(baseline_limits[0]); upper.append(baseline_limits[1])
        linear_lower.append(baseline_limits[0]); linear_upper.append(baseline_limits[1])
    if fit_drift:
        lower.append(drift_limits[0]); upper.append(drift_limits[1])
        linear_lower.append(drift_limits[0]); linear_upper.append(drift_limits[1])
    lower, upper = np.asarray(lower), np.asarray(upper)

    def basis(energies):
        columns = [rate(i, float(e)) * scale_units[i] / span for i, e in enumerate(energies)]
        if fit_baseline:
            columns.append(np.ones(temp.size))
        if fit_drift:
            columns.append(x)
        return np.column_stack(columns)

    def residual(parameters):
        check_cancel()
        prediction = basis(parameters[:count]) @ parameters[count:]
        return prediction - sig / span

    def jacobian(parameters):
        check_cancel()
        columns = []
        for i in range(count):
            energy = parameters[i]
            # Central differences larger than the coverage ODE tolerance avoid
            # false derivatives from default machine-epsilon perturbations.
            step = 2e-5 * max(1.0, abs(float(energy)))
            left, right = max(lower[i], energy - step), min(upper[i], energy + step)
            derivative = (rate(i, float(right)) - rate(i, float(left))) / (right - left)
            columns.append(derivative * scale_units[i] * parameters[count + i] / span)
        return np.column_stack(columns + [basis(parameters[:count])[:, j]
                                           for j in range(count + int(fit_baseline) + int(fit_drift))])

    starts = [initial_energies]
    if multistart:
        offsets = np.linspace(-0.025, 0.025, count) if count > 1 else np.array([0.025])
        for perturbation in (offsets, -offsets):
            start = np.clip(initial_energies + perturbation,
                            lower[:count] + 1e-9, upper[:count] - 1e-9)
            if not any(np.array_equal(start, existing) for existing in starts):
                starts.append(start)
    successful, errors = [], []
    for energies in starts:
        check_cancel()
        try:
            linear = lsq_linear(basis(energies), sig / span,
                                bounds=(linear_lower, linear_upper))
            parameters = np.concatenate((energies, linear.x))
            opt = least_squares(residual, parameters, jac=jacobian, bounds=(lower, upper),
                                max_nfev=int(max_nfev), x_scale='jac', loss='linear')
            if opt.success and np.isfinite(opt.x).all() and np.isfinite(opt.fun).all():
                successful.append(opt)
            else:
                errors.append(str(opt.message))
        except (ValueError, RuntimeError, FloatingPointError, OverflowError) as exc:
            errors.append(str(exc))
    if not successful:
        raise RuntimeError('Simultaneous fit did not converge: ' + '; '.join(dict.fromkeys(errors)))
    opt = min(successful, key=lambda attempt: float(attempt.fun @ attempt.fun))
    parameters = opt.x
    scales = parameters[count:2 * count] * scale_units
    curves = [scales[i] * rate(i, float(parameters[i])) for i in range(count)]
    cursor = 2 * count
    baseline = float(parameters[cursor] * span) if fit_baseline else 0.0
    cursor += int(fit_baseline)
    drift = float(parameters[cursor] * drift_unit) if fit_drift else 0.0
    baseline_curve = baseline + drift * (temp - reference)
    prediction = np.sum(curves, axis=0) + baseline_curve
    residuals = sig - prediction
    rss = float(residuals @ residuals)
    rmse = float(np.sqrt(rss / temp.size))
    n_parameters = int(parameters.size)
    aic, aicc, bic = _fit_information_criteria(rss, temp.size, n_parameters)
    jac = jacobian(parameters)
    covariance_unit, correlation, rank, condition, maximum_correlation = _jacobian_information(jac)
    energy_bound_indices = [i for i in range(count)
                            if min(parameters[i] - lower[i], upper[i] - parameters[i])
                            <= 1e-4 * (upper[i] - lower[i])]
    active_indices = sorted(set(np.flatnonzero(opt.active_mask).tolist() + energy_bound_indices))
    integrals = np.array([np.trapezoid(c, temp) if hasattr(np, 'trapezoid') else np.trapz(c, temp)
                          for c in curves])
    fractions = integrals / max(float(integrals.sum()), np.finfo(float).tiny)
    similarities = []
    exchangeable_labels = []
    for i in range(count):
        for j in range(i + 1, count):
            denom = float(np.linalg.norm(curves[i]) * np.linalg.norm(curves[j]))
            similarity = float(curves[i] @ curves[j] / denom) if denom else 1.0
            similarities.append(dict(labels=[definitions[i].label, definitions[j].label], cosine_similarity=similarity))
            left, right = definitions[i], definitions[j]
            # Under theta=theta0*phi the shape depends on nu*theta0**(n-1),
            # while the remaining theta0 factor can be absorbed by free scale.
            # Separated peaks can therefore have well-conditioned *local*
            # covariance while still permitting an exact label permutation.
            same_order = np.isclose(left.order, right.order, rtol=0, atol=1e-12)
            log_effective_left = np.log(left.prefactor_s_inv) + (left.order - 1) * np.log(left.initial_coverage)
            log_effective_right = np.log(right.prefactor_s_inv) + (right.order - 1) * np.log(right.initial_coverage)
            same_shape_family = same_order and np.isclose(log_effective_left, log_effective_right, rtol=0, atol=1e-8)
            swap_allowed = (right.energy_bounds[0] <= parameters[i] <= right.energy_bounds[1]
                            and left.energy_bounds[0] <= parameters[j] <= left.energy_bounds[1])
            if same_shape_family and swap_allowed:
                exchangeable_labels.append([left.label, right.label])
    lag1 = 0.0
    if np.std(residuals[:-1]) > 0 and np.std(residuals[1:]) > 0:
        lag1 = float(np.corrcoef(residuals[:-1], residuals[1:])[0, 1])
    warnings = ['Independent additive populations are a hypothesis; visible features and rankings do not establish distinct physical states.',
                'Orders, prefactors and initial coverages are fixed assumptions; energy/scale uncertainty is conditional on them.',
                'Component-count AICc/BIC and relative weights are heuristic for constrained mixtures, not mechanism probabilities.']
    withheld = []
    if rank < n_parameters or not np.isfinite(condition) or condition > 1e8:
        withheld.append('The joint Jacobian is rank deficient or poorly conditioned; component parameters are not reliably identifiable.')
    if not np.isfinite(covariance_unit).all():
        withheld.append('Local covariance cannot be resolved finitely in the supplied parameter coordinates.')
    if maximum_correlation > 0.95:
        withheld.append('Strong parameter correlation (absolute correlation > 0.95); component parameters are ambiguous.')
    if active_indices:
        withheld.append('One or more fitted parameters are at or near bounds; local symmetric intervals are invalid.')
    if np.any(fractions < 0.01):
        withheld.append('A component contributes less than 1% of integrated fitted desorption signal; its parameters may be unsupported.')
    if any(item['cosine_similarity'] > 0.995 for item in similarities):
        withheld.append('Two fitted component profiles are nearly indistinguishable; their individual contributions are ambiguous.')
    if exchangeable_labels:
        pairs = ', '.join(' / '.join(labels) for labels in exchangeable_labels)
        withheld.append('Component labels are exchangeable under the fixed kinetics and energy bounds (' + pairs
                        + '); distinct local peaks do not identify the labels. Labeled parameter intervals are withheld.')
    if abs(lag1) > 0.4:
        withheld.append('Residuals are strongly serially correlated; the iid-noise uncertainty approximation is inappropriate.')
    if rmse / span > 0.15:
        withheld.append('Large normalized residual error; the assumed component/baseline model does not describe this spectrum adequately.')
    if rmse / span < 1e-8:
        withheld.append('Residual variance is effectively zero; uncertainty cannot be inferred from this clean reference.')
    if any(c.order < 1 for c in definitions):
        withheld.append('A sub-first-order component has a finite depletion edge; local smooth-model intervals are withheld.')
    if len(successful) != len(starts):
        warnings.append('Some deterministic optimizer starts failed; inspect the supplied guesses and evaluation budget.')
    warnings.extend(withheld)
    covariance = None
    uncertainty_note = ('Approximate 95% local-linear Student-t intervals, conditional on fixed kinetics and iid homoscedastic Gaussian residual noise; '
                        'coverage is not experimentally calibrated and model-selection uncertainty is excluded.')
    multiplier = float(student_t.ppf(0.975, temp.size - n_parameters))
    if not withheld:
        covariance = covariance_unit * float(opt.fun @ opt.fun) / (temp.size - n_parameters)
        half_widths = multiplier * np.sqrt(np.maximum(np.diag(covariance), 0.0))
        if np.any(parameters - half_widths <= lower) or np.any(parameters + half_widths >= upper):
            reason = 'A local symmetric interval would cross a parameter constraint; its smooth-model approximation is unreliable.'
            withheld.append(reason)
            warnings.append(reason)
            covariance = None
    if withheld:
        uncertainty_note = 'Local parameter intervals withheld: ' + ' '.join(withheld)
    estimates = []
    for i, c in enumerate(definitions):
        energy_se = float(np.sqrt(max(0.0, covariance[i, i]))) if covariance is not None else None
        scale_se = float(np.sqrt(max(0.0, covariance[count + i, count + i])) * scale_units[i]) if covariance is not None else None
        estimates.append(dict(label=c.label, order=float(c.order), energy_eV=float(parameters[i]),
            prefactor_s_inv=float(c.prefactor_s_inv), initial_coverage=float(c.initial_coverage),
            energy_bounds=list(map(float, c.energy_bounds)), signal_scale=float(scales[i]),
            energy_standard_error_eV=energy_se, signal_scale_standard_error=scale_se,
            energy_interval_95_eV=[float(parameters[i] - multiplier * energy_se), float(parameters[i] + multiplier * energy_se)] if energy_se is not None else None,
            signal_scale_interval_95=[float(scales[i] - multiplier * scale_se), float(scales[i] + multiplier * scale_se)] if scale_se is not None else None,
            integrated_signal_fraction=float(fractions[i]), fixed_parameters=['order', 'prefactor_s_inv', 'initial_coverage']))
    diagnostics = dict(jacobian_rank=rank, n_parameters=n_parameters,
        normalized_jacobian_condition_number=condition, maximum_absolute_parameter_correlation=maximum_correlation,
        parameter_correlation=correlation.tolist(), near_bound_parameter_indices=active_indices,
        component_profile_similarities=similarities, exchangeable_component_labels=exchangeable_labels,
        residual_lag1_correlation=lag1,
        uncertainty_available=covariance is not None, uncertainty_withheld_reasons=withheld,
        parameter_order=[f'{c.label}:energy_eV' for c in definitions] + [f'{c.label}:scaled_signal_scale' for c in definitions]
            + (['scaled_baseline'] if fit_baseline else []) + (['scaled_drift'] if fit_drift else []),
        baseline_bounds=list(baseline_bounds) if baseline_bounds is not None else None,
        drift_bounds=list(drift_bounds) if drift_bounds is not None else None,
        fit_baseline=bool(fit_baseline), fit_drift=bool(fit_drift))
    return ComponentFitResult(True, str(opt.message), estimates, temp.copy(), sig.copy(), prediction.copy(),
        [c.copy() for c in curves], np.asarray(baseline_curve).copy(), residuals.copy(), float(beta_k_s),
        baseline, drift, reference, rmse, rmse / span, aic, aicc, bic, int(temp.size), n_parameters,
        len(starts), len(successful), diagnostics, warnings, uncertainty_note)


def compare_component_counts(temperature_c, signal, beta_k_s, components, *,
                             counts=(1, 2, 3), cancelled=None, **fit_settings):
    """Compare explicit prefix hypotheses on the same data and baseline model.

    Candidate ``n`` uses the first ``n`` supplied definitions. Their fixed
    parameters are retained in each result; reorder/edit definitions to compare
    other physical hypotheses. No component count is inferred from local maxima.
    """
    definitions = _definitions(components)
    counts = tuple(counts)
    if (not counts or len(set(counts)) != len(counts)
            or any(isinstance(n, bool) or not isinstance(n, (int, np.integer)) or not 1 <= n <= len(definitions) for n in counts)):
        raise ValueError('Choose distinct component counts supported by the supplied definitions.')
    candidates = []
    for count in counts:
        if cancelled is not None and cancelled():
            raise InterruptedError('Component-count comparison cancelled.')
        try:
            result = fit_components(temperature_c, signal, beta_k_s, definitions[:count],
                                    cancelled=cancelled, **fit_settings)
            candidates.append(ComponentCountCandidate(int(count), result, None))
        except (ValueError, RuntimeError, FloatingPointError, OverflowError) as exc:
            candidates.append(ComponentCountCandidate(int(count), None, str(exc)))
    successful = [candidate for candidate in candidates if candidate.fit is not None and np.isfinite(candidate.fit.aicc)]
    if successful:
        best = min(candidate.fit.aicc for candidate in successful)
        relative = np.array([np.exp(-0.5 * max(0.0, candidate.fit.aicc - best)) for candidate in successful])
        weights = relative / relative.sum()
        for candidate, weight in zip(successful, weights):
            candidate.delta_aicc = float(candidate.fit.aicc - best)
            candidate.akaike_weight = float(weight)
    return sorted(candidates, key=lambda candidate: candidate.delta_aicc if candidate.delta_aicc is not None else float('inf'))
