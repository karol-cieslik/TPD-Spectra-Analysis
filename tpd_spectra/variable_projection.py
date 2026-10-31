"""Profile linear signal nuisance parameters during nonlinear TPD fitting.

This is a research implementation for the single-state linear-ramp model. At
 each kinetic parameter proposal, signal scale and constant baseline are solved
as a bounded linear least-squares problem, reducing nonlinear optimizer dimension.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.optimize import least_squares

from .kinetics import simulate_tpd


@dataclass
class VariableProjectionResult:
    reaction_order: float
    activation_energy_eV: float
    prefactor_s_inv: float
    signal_scale: float
    baseline: float
    baseline_slope_per_normalized_T: float
    rmse_signal: float
    normalized_rmse: float
    success: bool
    nfev: int
    message: str
    prediction: np.ndarray


def fit_variable_projection(temperature_c, signal, beta_k_s: float, *,
                            reaction_order: float = 1.0,
                            fit_reaction_order: bool = False,
                            fit_baseline: bool = True,
                            baseline_degree: int = 0,
                            baseline_bounds=None,
                            initial_energy_ev: float = 1.0,
                            initial_prefactor_s_inv: float = 1e13,
                            max_nfev: int = 300) -> VariableProjectionResult:
    """Fit kinetics while profiling nonnegative signal scale and baseline.

    Baseline is constant and bounded to observed signal range unless explicit
    bounds are supplied. This intentionally matches the current model family;
    it does not add baseline drift or extra kinetic states.
    """
    t = np.asarray(temperature_c, float)
    y = np.asarray(signal, float)
    if t.ndim != 1 or y.shape != t.shape or t.size < 12:
        raise ValueError('temperature and signal must be matching 1D arrays (n >= 12)')
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)) or np.any(np.diff(t) < 0):
        raise ValueError('inputs must be finite and temperature non-decreasing')
    # Match the production fitter: rounded duplicate temperatures are averaged.
    unique, inverse = np.unique(t, return_inverse=True)
    if unique.size < 12:
        raise ValueError('at least 12 unique temperature points are required')
    if unique.size != t.size:
        sums = np.bincount(inverse, weights=y)
        counts = np.bincount(inverse)
        t, y = unique, sums/counts
    if beta_k_s <= 0 or not np.isfinite(beta_k_s):
        raise ValueError('beta_k_s must be positive and finite')
    if reaction_order < 0 or (fit_reaction_order and not .2 <= reaction_order <= 3):
        raise ValueError('invalid reaction order')
    if baseline_degree not in (0,1):
        raise ValueError('baseline_degree must be 0 or 1')
    lo_b, hi_b = baseline_bounds or (float(np.min(y)-2*np.ptp(y)), float(np.max(y)+np.ptp(y)))
    if not fit_baseline:
        lo_b = hi_b = 0.0
    norm = max(float(np.ptp(y)), np.finfo(float).tiny)
    z=(t-t.mean())/max(float(np.ptp(t)),np.finfo(float).tiny)
    order0 = float(np.clip(reaction_order, .2, 3))
    x0 = [float(initial_energy_ev), np.log10(float(initial_prefactor_s_inv))]
    lower, upper = [0.05, 3.0], [8.0, 30.0]
    if fit_reaction_order:
        x0.append(order0); lower.append(.2); upper.append(3.0)

    def evaluate(p, return_coefs=False):
        e, lognu = p[:2]
        n = p[2] if fit_reaction_order else float(reaction_order)
        _, rate = simulate_tpd(t, beta_k_s, e, 10.**lognu, n)
        peak = max(float(np.max(rate)), np.finfo(float).tiny)
        shape = rate / peak
        slope=0.0
        if fit_baseline and baseline_degree==1:
            design=np.column_stack([shape,np.ones_like(shape),z])
            coef=np.linalg.lstsq(design,y,rcond=None)[0]
            if coef[0]<0:
                bg=np.column_stack([np.ones_like(z),z])
                bc=np.linalg.lstsq(bg,y,rcond=None)[0]
                coef=np.array([0.,bc[0],bc[1]])
            amp,base,slope=map(float,coef)
            pred=amp*shape+base+slope*z
            coefs=np.array([amp/peak,base,slope])
        elif fit_baseline:
            # Exact two-column bounded least squares by checking the interior
            # stationary point and all active boundaries.
            candidates = []
            centered_shape = shape-shape.mean()
            centered_y = y-y.mean()
            amp = float(centered_shape@centered_y / max(centered_shape@centered_shape, np.finfo(float).tiny))
            base = float(y.mean()-amp*shape.mean())
            if amp >= 0 and lo_b <= base <= hi_b:
                candidates.append((amp, base))
            for bound in (lo_b, hi_b):
                amp_b = max(0., float(shape@(y-bound)/max(shape@shape, np.finfo(float).tiny)))
                candidates.append((amp_b, bound))
            candidates.append((0., float(np.clip(y.mean(), lo_b, hi_b))))
            amp, base = min(candidates, key=lambda pair: float(np.sum((pair[0]*shape+pair[1]-y)**2)))
            pred = amp*shape+base
            coefs = np.array([amp/peak, base])
        else:
            amp = max(0., float(shape@y/max(shape@shape, np.finfo(float).tiny)))
            pred = amp*shape
            coefs = np.array([amp/peak, 0.0])
        return (pred, coefs, n) if return_coefs else (pred-y)/norm

    # A bad E/nu start can leave the simulated peak outside the observed window,
    # making the profiled objective locally flat. Keep a small deterministic
    # seed grid and retain the best converged solution.
    starts = [np.asarray(x0, float)]
    if not fit_reaction_order:
        tpeak = float(t[np.argmax(y)] + 273.15)
        for nu in (1e12, 1e16, 1e20, 1e24, 1e28):
            # First-order Redhead estimate is only an optimizer seed.
            e = 8.617333262e-5*tpeak*(np.log(nu*tpeak/beta_k_s)-3.64)
            starts.append(np.asarray([np.clip(e, .0501, 7.99), np.log10(nu)]))
    opts = [least_squares(lambda p: evaluate(p), np.clip(s, np.asarray(lower)+1e-9,
                        np.asarray(upper)-1e-9), bounds=(lower, upper),
                        max_nfev=max_nfev, x_scale='jac', loss='linear') for s in starts]
    opt = min(opts, key=lambda result: float(np.dot(result.fun, result.fun)))
    pred, coef, n = evaluate(opt.x, True)
    rmse = float(np.sqrt(np.mean((pred-y)**2)))
    return VariableProjectionResult(n, float(opt.x[0]), float(10.**opt.x[1]),
                                    float(coef[0]), float(coef[1]) if fit_baseline else 0.0,
                                    float(coef[2]) if fit_baseline and baseline_degree==1 else 0.0,
                                    rmse, rmse/norm, bool(opt.success), int(opt.nfev),
                                    str(opt.message), pred)
