"""Numerical Polanyi–Wigner TPD kinetics and constrained full-trace fitting.

The model assumes a single initially populated site/state, a linear heating ramp,
and a signal proportional to the desorption rate plus an optional constant offset.
These assumptions are intentionally explicit; good fit quality does not establish
that the selected physical model is unique.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from .analysis import K_B_EV
from .identifiability import jacobian_diagnostics


@dataclass
class KineticFitResult:
    reaction_order: float
    reaction_order_fitted: bool
    activation_energy_eV: float
    prefactor_s_inv: float
    signal_scale: float
    baseline: float
    rmse_signal: float
    normalized_rmse: float
    r_squared: float
    n_points: int
    success: bool
    message: str
    temperature_min_C: float
    temperature_max_C: float
    aic: float
    aicc: float
    bic: float
    jacobian_condition_number: float
    identifiability_diagnostics: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)


def polanyi_wigner_rate(temperature_k, coverage, activation_energy_ev: float,
                        prefactor_s_inv: float, reaction_order: float):
    """Return desorption rate nu*theta**n*exp(-E/kBT), in coverage/s."""
    temp = np.asarray(temperature_k, dtype=float)
    theta = np.asarray(coverage, dtype=float)
    if np.any(~np.isfinite(theta)):
        raise ValueError("coverage must be finite")
    if np.any(~np.isfinite(temp)) or np.any(temp <= 0):
        raise ValueError("temperature must be positive kelvin and finite")
    if not np.isfinite(activation_energy_ev) or activation_energy_ev <= 0:
        raise ValueError("activation_energy_ev must be positive and finite")
    if not np.isfinite(prefactor_s_inv) or prefactor_s_inv <= 0:
        raise ValueError("prefactor_s_inv must be positive and finite")
    if not np.isfinite(reaction_order) or reaction_order < 0:
        raise ValueError("reaction_order must be non-negative and finite")
    theta_safe = np.clip(theta, 0.0, 1.0)
    coverage_term = np.ones_like(theta_safe) if reaction_order == 0 else theta_safe ** reaction_order
    rate = prefactor_s_inv * coverage_term * np.exp(-activation_energy_ev / (K_B_EV * temp))
    # Even a zero-order rate terminates when the adsorbed population is exhausted.
    return np.where(theta_safe > 0.0, rate, 0.0)


def simulate_tpd(temperature_c, beta_k_s: float, activation_energy_ev: float,
                 prefactor_s_inv: float, reaction_order: float = 1.0,
                 initial_coverage: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Simulate coverage and desorption rate along a measured temperature grid.

    Temperature is the independent variable, with d(theta)/dT = -rate/beta.
    The returned rate is in coverage/s. A strictly increasing temperature grid
    is required; measured non-linear ramps should be handled by a time-based model.
    """
    temp_c = np.asarray(temperature_c, dtype=float)
    if temp_c.ndim != 1 or temp_c.size < 3 or not np.all(np.isfinite(temp_c)):
        raise ValueError("temperature_c must be a finite 1D array with at least 3 points")
    if np.any(np.diff(temp_c) <= 0):
        raise ValueError("temperature_c must be strictly increasing for a linear-ramp simulation")
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError("beta_k_s must be positive and finite")
    if not np.isfinite(initial_coverage) or not 0 < initial_coverage <= 1:
        raise ValueError("initial_coverage must be in (0, 1]")
    # Validate kinetics before entering the solver.
    polanyi_wigner_rate(temp_c + 273.15, np.array([initial_coverage]), activation_energy_ev,
                        prefactor_s_inv, reaction_order)

    def derivative(t_c, y):
        rate = polanyi_wigner_rate(np.array([t_c + 273.15]), np.array([max(0.0, y[0])]),
                                   activation_energy_ev, prefactor_s_inv, reaction_order)[0]
        return [-rate / beta_k_s]

    solution = solve_ivp(derivative, (float(temp_c[0]), float(temp_c[-1])),
                         [float(initial_coverage)], t_eval=temp_c, method="LSODA",
                         rtol=2e-7, atol=1e-10)
    if not solution.success or solution.y.shape[1] != temp_c.size:
        raise RuntimeError(f"Coverage integration failed: {solution.message}")
    coverage = np.clip(solution.y[0], 0.0, initial_coverage)
    rate = polanyi_wigner_rate(temp_c + 273.15, coverage, activation_energy_ev,
                               prefactor_s_inv, reaction_order)
    return coverage, rate


def fit_polanyi_wigner(temperature_c, signal, beta_k_s: float, *,
                       reaction_order: float = 1.0, fit_reaction_order: bool = False,
                       initial_energy_ev: float = 1.0, initial_prefactor_s_inv: float = 1e13,
                       fit_baseline: bool = True, max_nfev: int = 300,
                       cancelled=None) -> tuple[KineticFitResult, np.ndarray]:
    """Fit a full TPD trace by bounded nonlinear least squares.

    The scale factor and (optionally) constant baseline are nuisance parameters.
    Prefactor is optimised in log10 space. The reaction order is fixed by default;
    setting fit_reaction_order=True estimates it within [0.2, 3]. Fits can be
    non-identifiable, especially when both energy and prefactor are free.
    Fixed zero order instead profiles every sampled depletion boundary. Its
    max_nfev limits energy optimization per boundary (plus endpoint checks),
    and the returned prefactor/scale represent conditional compatible ranges.
    """
    temp = np.asarray(temperature_c, dtype=float)
    sig = np.asarray(signal, dtype=float)
    if temp.ndim != 1 or sig.shape != temp.shape or temp.size < 12:
        raise ValueError("temperature and signal must be matching 1D arrays with at least 12 points")
    valid = np.isfinite(temp) & np.isfinite(sig)
    temp, sig = temp[valid], sig[valid]
    if temp.size < 12 or np.any(np.diff(temp) < 0):
        raise ValueError("fit requires at least 12 finite points on a non-decreasing temperature ramp")
    if not np.isfinite(max_nfev) or int(max_nfev) != max_nfev or max_nfev < 1:
        raise ValueError("max_nfev must be a positive integer")
    # Instrument temperatures are often rounded, producing repeated adjacent
    # values. Average their signals for integration, then expand predictions
    # back onto the original valid sample grid for plotting.
    original_temp = temp.copy()
    unique_temp, inverse = np.unique(temp, return_inverse=True)
    if unique_temp.size < 12:
        raise ValueError("fit requires at least 12 unique temperature points")
    if unique_temp.size != temp.size:
        sums = np.bincount(inverse, weights=sig)
        counts = np.bincount(inverse)
        sig = sums / counts
        temp = unique_temp
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError("beta_k_s must be positive and finite")
    if not np.isfinite(reaction_order) or reaction_order < 0:
        raise ValueError("reaction_order must be non-negative and finite")
    if not np.isfinite(initial_energy_ev) or initial_energy_ev <= 0:
        raise ValueError("initial_energy_ev must be positive and finite")
    if not np.isfinite(initial_prefactor_s_inv) or initial_prefactor_s_inv <= 0:
        raise ValueError("initial_prefactor_s_inv must be positive and finite")

    signal_range = float(np.ptp(sig))
    signal_scale_floor = max(float(np.max(np.abs(sig))), 1.0) * 1e-12
    if not np.isfinite(signal_range) or signal_range <= signal_scale_floor:
        raise ValueError("signal must have nonzero dynamic range for kinetic fitting")
    if reaction_order == 0 and not fit_reaction_order:
        from .zero_order import fit_zero_order
        result, prediction = fit_zero_order(temp, sig, beta_k_s, fit_baseline=fit_baseline,
                                             max_nfev=max_nfev, cancelled=cancelled)
        if original_temp.size != temp.size:
            prediction = prediction[inverse]
        return result, prediction
    span = max(signal_range, np.finfo(float).eps)
    base0 = float(np.percentile(sig, 5)) if fit_baseline else 0.0
    order0 = float(np.clip(reaction_order, 0.2, 3.0)) if fit_reaction_order else float(reaction_order)
    # Parameter vector: E, log10(nu), log10(scale), [baseline], [order].
    initial = [float(initial_energy_ev), float(np.log10(initial_prefactor_s_inv)), 0.0]
    lower, upper = [0.05, 3.0, -30.0], [8.0, 30.0, 30.0]
    if fit_baseline:
        initial.append(base0)
        lower.append(float(np.min(sig) - 2 * span))
        upper.append(float(np.max(sig) + span))
    if fit_reaction_order:
        initial.append(order0)
        lower.append(0.2)
        upper.append(3.0)
    initial = np.asarray(initial, dtype=float)
    lower, upper = np.asarray(lower), np.asarray(upper)
    # Initialise the signal-scale nuisance parameter against the rate generated
    # by the initial kinetic guesses; a raw signal-range guess is dimensionally poor.
    try:
        _, initial_rate = simulate_tpd(temp, beta_k_s, initial_energy_ev,
                                       initial_prefactor_s_inv, order0)
        rate_peak = float(np.max(initial_rate))
    except (ValueError, RuntimeError):
        rate_peak = 0.0
    scale0 = span / max(rate_peak, np.finfo(float).tiny)
    initial[2] = np.log10(np.clip(scale0, 1e-30, 1e30))

    # A peak outside the observations leaves a flat objective: scale can vanish
    # while a baseline alone satisfies ftol. Compare the supplied start with a
    # peak-informed start, profiling the linear scale/offset for initialization.
    # This is a numerical seed, not a first-order physical interpretation.
    peak_kelvin = float(temp[np.argmax(sig)] + 273.15)
    peak_energy = K_B_EV * peak_kelvin * (
        np.log(initial_prefactor_s_inv * peak_kelvin / beta_k_s) - 3.64)
    seed_candidates = []
    for seed_energy in (initial_energy_ev, float(np.clip(peak_energy, .050001, 7.999999))):
        if cancelled is not None and cancelled():
            raise InterruptedError('Kinetic fit cancelled')
        try:
            _, seed_rate = simulate_tpd(temp, beta_k_s, seed_energy, initial_prefactor_s_inv, order0)
            peak_rate = float(np.max(seed_rate))
            if not np.isfinite(peak_rate) or peak_rate <= 0:
                continue
            shape = seed_rate / peak_rate
            centered_shape = shape - shape.mean() if fit_baseline else shape
            centered_signal = sig - sig.mean() if fit_baseline else sig
            amplitude = max(0., float(centered_shape @ centered_signal) /
                            max(float(centered_shape @ centered_shape), np.finfo(float).tiny))
            offset = float(np.clip(np.mean(sig-amplitude*shape), lower[3], upper[3])) if fit_baseline else 0.
            amplitude = max(0., float(shape @ (sig-offset)) / max(float(shape @ shape), np.finfo(float).tiny))
            seed = initial.copy()
            seed[0] = seed_energy
            seed[2] = np.log10(np.clip(amplitude / peak_rate, 1e-30, 1e30))
            if fit_baseline:
                seed[3] = offset
            score = float(np.sum(((offset + 10.**seed[2]*seed_rate - sig)/span)**2))
            seed_candidates.append((score, seed))
        except (ValueError, RuntimeError, FloatingPointError):
            continue
    if seed_candidates:
        initial = min(seed_candidates, key=lambda item: item[0])[1]

    def unpack(p):
        i = 3
        baseline = p[i] if fit_baseline else 0.0
        i += int(fit_baseline)
        order = p[i] if fit_reaction_order else float(reaction_order)
        return p[0], 10.0 ** p[1], 10.0 ** p[2], baseline, order

    # Scale residuals to signal range for stable optimisation across detector units.
    def residual(p):
        if cancelled is not None and cancelled():
            raise InterruptedError("Kinetic fit cancelled")
        energy, prefactor, scale, baseline, order = unpack(p)
        try:
            _, rate = simulate_tpd(temp, beta_k_s, energy, prefactor, order)
            prediction = baseline + scale * rate
            if not np.all(np.isfinite(prediction)):
                return np.full(temp.size, 1e6)
            return (prediction - sig) / span
        except (ValueError, RuntimeError, FloatingPointError):
            return np.full(temp.size, 1e6)

    opt = least_squares(residual, initial, bounds=(lower, upper), max_nfev=max_nfev,
                        x_scale="jac", loss="linear")
    energy, prefactor, scale, baseline, order = unpack(opt.x)
    _, rate = simulate_tpd(temp, beta_k_s, energy, prefactor, order)
    prediction = baseline + scale * rate
    errors = prediction - sig
    ss_res = float(np.sum(errors**2))
    ss_tot = float(np.sum((sig - sig.mean())**2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rmse = float(np.sqrt(np.mean(errors**2)))
    aic, aicc, bic = _fit_information_criteria(ss_res, int(temp.size), int(opt.x.size))
    try:
        singular_values = np.linalg.svd(opt.jac, compute_uv=False)
        condition = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0 else float('inf')
    except (np.linalg.LinAlgError, IndexError):
        condition = float('inf')
    diagnostics = jacobian_diagnostics(opt.jac, opt.x, lower, upper)
    result = KineticFitResult(float(order), bool(fit_reaction_order), float(energy),
        float(prefactor), float(scale), float(baseline), rmse, rmse / span, float(r2),
        int(temp.size), bool(opt.success), str(opt.message), float(temp.min()), float(temp.max()),
        aic, aicc, bic, condition, diagnostics)
    if original_temp.size != temp.size:
        prediction = np.interp(original_temp, temp, prediction)
    return result, prediction


@dataclass
class MultiStateFitResult:
    """Two independent desorption populations fitted to one measured trace."""
    n_states: int
    reaction_order: float
    activation_energies_eV: list[float]
    prefactors_s_inv: list[float]
    signal_scales: list[float]
    baseline: float
    rmse_signal: float
    normalized_rmse: float
    r_squared: float
    aic: float
    aicc: float
    bic: float
    jacobian_condition_number: float
    n_points: int
    n_parameters: int
    success: bool
    message: str
    temperature_min_C: float
    temperature_max_C: float
    warnings: list[str]

    def as_dict(self):
        return asdict(self)


def _fit_information_criteria(residual_sum_squares: float, n: int, k: int):
    """Gaussian unknown-variance criteria, with common likelihood constants omitted.

    k counts fitted mean-model parameters; estimating residual variance adds
    one parameter. Compare only fits to the same observations and error model.
    The usual AICc correction is approximate for nonlinear constrained fits.
    """
    n = int(n); k = int(k) + 1
    rss = max(float(residual_sum_squares), np.finfo(float).tiny)
    aic = n * np.log(rss / n) + 2 * k
    aicc = aic + (2 * k * (k + 1) / (n - k - 1)) if n > k + 1 else float('inf')
    bic = n * np.log(rss / n) + k * np.log(n)
    return float(aic), float(aicc), float(bic)


def fit_two_state_polanyi_wigner(temperature_c, signal, beta_k_s: float, *,
                                 reaction_order: float = 1.0,
                                 initial_energies_ev=(0.8, 1.4),
                                 initial_prefactor_s_inv: float = 1e13,
                                 fit_baseline: bool = True,
                                 max_nfev: int = 500) -> tuple[MultiStateFitResult, np.ndarray]:
    """Fit two independent Polanyi–Wigner states to a single trace.

    Each state has its own activation energy, prefactor and signal scale; the
    states share reaction order and additive baseline. This is an exploratory
    model, not proof that two physical adsorption states exist. E2 is
    parameterised as E1 + positive_delta to avoid label swapping.
    """
    temp = np.asarray(temperature_c, dtype=float)
    sig = np.asarray(signal, dtype=float)
    if temp.ndim != 1 or sig.shape != temp.shape or temp.size < 20:
        raise ValueError('temperature and signal must be matching 1D arrays with at least 20 points')
    valid = np.isfinite(temp) & np.isfinite(sig)
    temp, sig = temp[valid], sig[valid]
    if temp.size < 20 or np.any(np.diff(temp) < 0):
        raise ValueError('fit requires at least 20 finite points on a non-decreasing temperature ramp')
    unique_temp, inverse = np.unique(temp, return_inverse=True)
    original_temp = temp.copy()
    if unique_temp.size < 20:
        raise ValueError('fit requires at least 20 unique temperature points')
    if unique_temp.size != temp.size:
        sig = np.bincount(inverse, weights=sig) / np.bincount(inverse)
        temp = unique_temp
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError('beta_k_s must be positive and finite')
    if not np.isfinite(reaction_order) or reaction_order < 0:
        raise ValueError('reaction_order must be non-negative and finite')
    energies = np.asarray(initial_energies_ev, dtype=float)
    if energies.shape != (2,) or np.any(~np.isfinite(energies)) or np.any(energies <= 0) or energies[1] <= energies[0]:
        raise ValueError('initial_energies_ev must contain two positive increasing energies')
    if not np.isfinite(initial_prefactor_s_inv) or initial_prefactor_s_inv <= 0:
        raise ValueError('initial_prefactor_s_inv must be positive and finite')
    if not np.isfinite(max_nfev) or int(max_nfev) != max_nfev or max_nfev < 1:
        raise ValueError('max_nfev must be a positive integer')
    span = float(np.ptp(sig))
    if not np.isfinite(span) or span <= max(float(np.max(np.abs(sig))), 1.0) * 1e-12:
        raise ValueError('signal must have nonzero dynamic range for kinetic fitting')

    # Parameters: E1, deltaE, log10(nu1), log10(nu2), log10(scale1), log10(scale2), [baseline].
    base = float(np.percentile(sig, 5)) if fit_baseline else 0.0
    # E2 = E1 + fraction * (8 eV - E1), guaranteeing E1 < E2 <= 8 eV.
    delta_fraction = (energies[1] - energies[0]) / (8.0 - energies[0])
    p0 = [energies[0], delta_fraction,
          np.log10(initial_prefactor_s_inv), np.log10(initial_prefactor_s_inv), 0.0, 0.0]
    lower = [0.05, 0.001, 3.0, 3.0, -30.0, -30.0]
    upper = [7.99, 1.0, 30.0, 30.0, 30.0, 30.0]
    if fit_baseline:
        p0.append(base); lower.append(float(np.min(sig) - 2 * span)); upper.append(float(np.max(sig) + span))
    p0 = np.asarray(p0, dtype=float); lower = np.asarray(lower); upper = np.asarray(upper)
    # Starting amplitude scales based on initial state rates.
    for idx, energy, scale_index in ((4, energies[0], 0), (5, energies[1], 1)):
        _, rate0 = simulate_tpd(temp, beta_k_s, float(energy), initial_prefactor_s_inv, reaction_order)
        p0[idx] = np.log10(np.clip((span * 0.5) / max(float(np.max(rate0)), 1e-300), 1e-30, 1e30))

    def unpack(p):
        e1 = float(p[0]); e2 = e1 + float(p[1]) * (8.0 - e1)
        nu1, nu2 = 10.0 ** p[2], 10.0 ** p[3]
        s1, s2 = 10.0 ** p[4], 10.0 ** p[5]
        baseline = float(p[6]) if fit_baseline else 0.0
        return (e1, e2), (nu1, nu2), (s1, s2), baseline

    def predict(p):
        es, nus, scales, baseline = unpack(p)
        _, r1 = simulate_tpd(temp, beta_k_s, es[0], nus[0], reaction_order)
        _, r2 = simulate_tpd(temp, beta_k_s, es[1], nus[1], reaction_order)
        return baseline + scales[0] * r1 + scales[1] * r2

    def residual(p):
        try:
            pred = predict(p)
            return (pred - sig) / span if np.all(np.isfinite(pred)) else np.full(temp.size, 1e6)
        except (ValueError, RuntimeError, FloatingPointError, OverflowError):
            return np.full(temp.size, 1e6)

    opt = least_squares(residual, p0, bounds=(lower, upper), max_nfev=int(max_nfev), x_scale='jac')
    prediction = predict(opt.x)
    errors = prediction - sig
    rss = float(np.sum(errors ** 2)); n = int(temp.size); k = int(opt.x.size)
    r2 = 1.0 - rss / float(np.sum((sig - np.mean(sig)) ** 2))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    aic, aicc, bic = _fit_information_criteria(rss, n, k)
    try:
        singular_values = np.linalg.svd(opt.jac, compute_uv=False)
        condition = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0 else float('inf')
    except (np.linalg.LinAlgError, IndexError):
        condition = float('inf')
    es, nus, scales, baseline = unpack(opt.x)
    warnings = []
    if reaction_order == 0:
        warnings.append('Two-state zero-order fitting still uses the legacy local optimizer; the single-state depletion-profile correction does not validate this path.')
    if not opt.success:
        warnings.append('Optimizer did not converge.')
    if condition > 1e8 or not np.isfinite(condition):
        warnings.append('Poor parameter identifiability: Jacobian is ill-conditioned; parameters may be strongly correlated.')
    if min(scales) < max(scales) * 1e-5:
        warnings.append('One state has a very small fitted contribution; the second state may not be supported by the data.')
    if es[1] - es[0] < 0.03:
        warnings.append('Fitted activation energies are very close; the two states may not be distinguishable.')
    if rmse / span > 0.15:
        warnings.append('Large normalized residual error; this model does not adequately explain the trace under the current assumptions.')
    result = MultiStateFitResult(2, float(reaction_order), list(map(float, es)), list(map(float, nus)),
        list(map(float, scales)), float(baseline), rmse, rmse / span, float(r2), aic, aicc, bic,
        condition, n, k, bool(opt.success), str(opt.message), float(temp.min()), float(temp.max()), warnings)
    if original_temp.size != temp.size:
        prediction = np.interp(original_temp, temp, prediction)
    return result, prediction


@dataclass
class GlobalKineticFitResult:
    """Shared activation energy/prefactor fit across multiple heating rates."""
    activation_energy_eV: float
    prefactor_s_inv: float
    reaction_order: float
    rmse_by_trace: list[float]
    normalized_rmse_by_trace: list[float]
    r_squared_by_trace: list[float]
    heating_rates_K_s: list[float]
    signal_scales: list[float]
    baselines: list[float]
    energy_log10_prefactor_correlation: float
    jacobian_condition_number: float
    aic: float
    aicc: float
    bic: float
    n_points: int
    n_parameters: int
    success: bool
    message: str
    warnings: list[str]

    def as_dict(self):
        return asdict(self)


def fit_global_polanyi_wigner(traces, *, reaction_order: float = 1.0,
                               initial_energy_ev: float = 1.0,
                               initial_prefactor_s_inv: float = 1e13,
                               fit_baseline: bool = True,
                               max_nfev: int = 500) -> tuple[GlobalKineticFitResult, list[np.ndarray]]:
    """Jointly fit traces collected at different heating rates.

    ``traces`` is an iterable of dictionaries with ``temperature_c``, ``signal``
    and ``beta_k_s`` fields. Activation energy and prefactor are shared globally;
    each trace has its own signal scale and optional constant baseline. Residuals
    are normalized by each trace's dynamic range so a high-amplitude trace does
    not dominate solely due to detector units.

    The model assumes each trace is a linear temperature ramp, identical kinetics
    across runs, and a signal proportional to rate. It does not model coverage
    dependent initial populations or instrument response functions.
    """
    prepared = []
    for index, trace in enumerate(traces):
        try:
            temp = np.asarray(trace['temperature_c'], dtype=float)
            signal = np.asarray(trace['signal'], dtype=float)
            beta = float(trace['beta_k_s'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'trace {index + 1} must provide temperature_c, signal and beta_k_s') from exc
        if temp.ndim != 1 or signal.shape != temp.shape or temp.size < 12:
            raise ValueError(f'trace {index + 1} needs matching 1D arrays with at least 12 points')
        valid = np.isfinite(temp) & np.isfinite(signal)
        temp, signal = temp[valid], signal[valid]
        if temp.size < 12 or np.any(np.diff(temp) <= 0):
            raise ValueError(f'trace {index + 1} requires at least 12 finite points and strictly increasing temperature')
        if not np.isfinite(beta) or beta <= 0:
            raise ValueError(f'trace {index + 1} heating rate must be positive and finite')
        span = float(np.ptp(signal))
        if not np.isfinite(span) or span <= max(float(np.max(np.abs(signal))), 1.0) * 1e-12:
            raise ValueError(f'trace {index + 1} signal must have nonzero dynamic range')
        prepared.append({'temperature_c': temp, 'signal': signal, 'beta_k_s': beta, 'span': span})
    if len(prepared) < 2:
        raise ValueError('global fitting requires at least two traces, preferably at distinct heating rates')
    betas = [item['beta_k_s'] for item in prepared]
    warnings = []
    if len(set(np.round(betas, 8))) < 2:
        warnings.append('All traces have the same heating rate; multi-rate constraints are absent.')
    if not np.isfinite(reaction_order) or reaction_order < 0:
        raise ValueError('reaction_order must be non-negative and finite')
    if not np.isfinite(initial_energy_ev) or initial_energy_ev <= 0:
        raise ValueError('initial_energy_ev must be positive and finite')
    if not np.isfinite(initial_prefactor_s_inv) or initial_prefactor_s_inv <= 0:
        raise ValueError('initial_prefactor_s_inv must be positive and finite')
    if not np.isfinite(max_nfev) or int(max_nfev) != max_nfev or max_nfev < 1:
        raise ValueError('max_nfev must be a positive integer')

    # Shared E, log10(nu), followed by per-trace log10(scale), [baseline].
    p0 = [initial_energy_ev, np.log10(initial_prefactor_s_inv)]
    # Broad but finite bounds avoid pathological stiff ODE evaluations during
    # global optimisation. They are numerical safeguards, not universal physics.
    lower = [0.05, 5.0]
    upper = [5.0, 22.0]
    for item in prepared:
        base = float(np.percentile(item['signal'], 5)) if fit_baseline else 0.0
        try:
            _, rate0 = simulate_tpd(item['temperature_c'], item['beta_k_s'],
                                    initial_energy_ev, initial_prefactor_s_inv, reaction_order)
            rate_peak = float(np.max(rate0))
        except (ValueError, RuntimeError):
            rate_peak = 0.0
        scale0 = item['span'] / max(rate_peak, np.finfo(float).tiny)
        p0.append(float(np.log10(np.clip(scale0, 1e-30, 1e30))))
        lower.append(-30.0); upper.append(30.0)
        if fit_baseline:
            p0.append(base)
            lower.append(float(np.min(item['signal']) - 2 * item['span']))
            upper.append(float(np.max(item['signal']) + item['span']))
    p0, lower, upper = np.asarray(p0), np.asarray(lower), np.asarray(upper)

    def unpack(p, index):
        cursor = 2
        for i in range(index):
            cursor += 1 + int(fit_baseline)
        scale = 10.0 ** p[cursor]
        baseline = float(p[cursor + 1]) if fit_baseline else 0.0
        return scale, baseline

    def predictions(p):
        e, nu = float(p[0]), 10.0 ** float(p[1])
        out = []
        for i, item in enumerate(prepared):
            scale, baseline = unpack(p, i)
            _, rate = simulate_tpd(item['temperature_c'], item['beta_k_s'], e, nu, reaction_order)
            out.append(baseline + scale * rate)
        return out

    def residual(p):
        try:
            preds = predictions(p)
            if any(not np.all(np.isfinite(pred)) for pred in preds):
                return np.full(sum(len(x['signal']) for x in prepared), 1e6)
            return np.concatenate([(pred - item['signal']) / item['span']
                                   for pred, item in zip(preds, prepared)])
        except (ValueError, RuntimeError, FloatingPointError, OverflowError):
            return np.full(sum(len(x['signal']) for x in prepared), 1e6)

    opt = least_squares(residual, p0, bounds=(lower, upper), max_nfev=int(max_nfev), x_scale='jac')
    pred_list = predictions(opt.x)
    rmse_values, nrmse_values, r2_values = [], [], []
    rss = 0.0
    normalized_rss = 0.0
    for pred, item in zip(pred_list, prepared):
        errors = pred - item['signal']
        rss += float(np.sum(errors ** 2))
        normalized_rss += float(np.sum((errors / item['span']) ** 2))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        total = float(np.sum((item['signal'] - np.mean(item['signal'])) ** 2))
        rmse_values.append(rmse)
        nrmse_values.append(rmse / item['span'])
        r2_values.append(1.0 - float(np.sum(errors ** 2)) / total if total > 0 else float('nan'))
    n_points = sum(len(item['signal']) for item in prepared)
    n_parameters = int(opt.x.size)
    # The objective weights each trace by its own dynamic range; use the same
    # normalized residual sum of squares for information criteria.
    aic, aicc, bic = _fit_information_criteria(normalized_rss, n_points, n_parameters)
    try:
        singular = np.linalg.svd(opt.jac, compute_uv=False)
        condition = float(singular[0] / singular[-1]) if singular[-1] > 0 else float('inf')
        covariance = np.linalg.pinv(opt.jac.T @ opt.jac)
        denom = np.sqrt(max(covariance[0, 0], 0) * max(covariance[1, 1], 0))
        correlation = float(covariance[0, 1] / denom) if denom > 0 else float('nan')
    except (np.linalg.LinAlgError, IndexError, FloatingPointError):
        condition, correlation = float('inf'), float('nan')
    if not opt.success:
        warnings.append('Optimizer did not converge.')
    if condition > 1e8 or not np.isfinite(condition):
        warnings.append('Global fit Jacobian is ill-conditioned; fitted parameters may not be identifiable.')
    if np.isfinite(correlation) and abs(correlation) > 0.95:
        warnings.append('Activation energy and log10(prefactor) are strongly correlated (absolute correlation > 0.95).')
    if max(nrmse_values) > 0.15:
        warnings.append('At least one trace has normalized RMSE > 0.15; the shared model does not adequately describe every trace.')
    scales, baselines = zip(*(unpack(opt.x, i) for i in range(len(prepared))))
    if reaction_order == 0:
        warnings.append('Global zero-order fitting still uses the legacy local optimizer; the single-state depletion-profile correction does not validate this path.')
    result = GlobalKineticFitResult(float(opt.x[0]), float(10.0 ** opt.x[1]), float(reaction_order),
        rmse_values, nrmse_values, r2_values, betas, list(map(float, scales)), list(map(float, baselines)),
        correlation, condition, aic, aicc, bic, n_points, n_parameters, bool(opt.success), str(opt.message), warnings)
    return result, pred_list
