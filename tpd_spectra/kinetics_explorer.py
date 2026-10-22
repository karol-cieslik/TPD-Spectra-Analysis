"""Exploratory comparison of single-state Polanyi–Wigner desorption orders.

This module reuses the validated fitter without changing existing CLI or GUI
behavior. Model rankings reflect fit quality under explicit assumptions, not
proof of a physical mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .kinetics import KineticFitResult, fit_polanyi_wigner


@dataclass
class ModelCandidate:
    """One fit attempt, including explicit failure reporting."""

    name: str
    fit: KineticFitResult | None
    prediction: np.ndarray | None
    error: str | None
    delta_aicc: float | None = None
    akaike_weight: float | None = None
    warnings: tuple[str, ...] = ()
    starts_attempted: int = 0
    starts_converged: int = 0


def compare_desorption_orders(
    temperature_c,
    signal,
    beta_k_s: float,
    *,
    orders: tuple[str, ...] = ("zero", "first", "second", "fractional"),
    initial_energy_ev: float = 1.0,
    initial_prefactor_s_inv: float = 1e13,
    fit_baseline: bool = True,
    max_nfev: int = 300,
    multistart: bool = True,
) -> list[ModelCandidate]:
    """Fit candidates to a single isolated peak using the existing kinetic fitter.

    Temperature is in Celsius, beta in K/s, and signal in arbitrary instrument
    units. The fitter assumes an isolated initially populated state, normalized
    initial coverage of one, and a linear temperature ramp.

    Candidate fits are independent and use deterministic multistart guesses.\n    Failed fits are returned with their error,
    never silently counted as successful comparisons. AICc weights are relative
    weights under the fitted candidate set, *not* probabilities of a mechanism.
    """
    names = {"zero": (0.0, False), "first": (1.0, False),
             "second": (2.0, False), "fractional": (1.2, True)}
    if not orders or len(set(orders)) != len(orders):
        raise ValueError("Choose at least one distinct model")
    unknown = set(orders) - set(names)
    if unknown:
        raise ValueError(f"Unknown desorption order model(s): {sorted(unknown)}")
    temp = np.asarray(temperature_c, dtype=float)
    sig = np.asarray(signal, dtype=float)
    if temp.ndim != 1 or sig.shape != temp.shape or temp.size < 12:
        raise ValueError("Temperature and signal must be matching arrays of at least 12 points")
    if not np.all(np.isfinite(temp)) or not np.all(np.isfinite(sig)):
        raise ValueError("Remove non-finite experimental points before model comparison")
    if np.any(np.diff(temp) <= 0):
        raise ValueError("Use a strictly increasing temperature grid")
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError("Heating rate must be positive and finite")

    if not np.isfinite(initial_energy_ev) or initial_energy_ev <= 0:
        raise ValueError("Initial activation energy must be positive")
    if not np.isfinite(initial_prefactor_s_inv) or initial_prefactor_s_inv <= 0:
        raise ValueError("Initial prefactor must be positive")
    if not isinstance(max_nfev, int) or max_nfev <= 0:
        raise ValueError("max_nfev must be a positive integer")
    # Different guesses help diagnose local minima. Preserve the caller's
    # preferred guess, then try conservative alternatives; this is not a
    # guarantee of locating a global minimum.
    starts = [(initial_energy_ev, initial_prefactor_s_inv)]
    if multistart:
        starts.extend([(0.8, 1e10), (1.4, 1e13)])

    candidates: list[ModelCandidate] = []
    for name in orders:
        n, free_n = names[name]
        attempts = []
        errors = []
        for energy, prefactor in starts:
            try:
                fit, predicted = fit_polanyi_wigner(
                    temp, sig, beta_k_s, reaction_order=n,
                    fit_reaction_order=free_n,
                    initial_energy_ev=energy,
                    initial_prefactor_s_inv=prefactor,
                    fit_baseline=fit_baseline, max_nfev=max_nfev,
                )
                if fit.success and np.isfinite(fit.aicc) and np.all(np.isfinite(predicted)):
                    attempts.append((fit, predicted))
                else:
                    errors.append("Non-converged or non-finite fit")
            except (ValueError, RuntimeError, OverflowError, FloatingPointError) as exc:
                errors.append(str(exc))
        if not attempts:
            candidates.append(ModelCandidate(
                name, None, None, "; ".join(dict.fromkeys(errors)) or "No valid fit",
                starts_attempted=len(starts), starts_converged=0))
            continue
        fit, predicted = min(attempts, key=lambda item: item[0].aicc)
        warnings = []
        if not np.isfinite(fit.jacobian_condition_number) or fit.jacobian_condition_number > 1e8:
            warnings.append("Ill-conditioned Jacobian: kinetic parameters may not be identifiable.")
        if fit.normalized_rmse > 0.15:
            warnings.append("Large fit residual: the single-state model may be inadequate.")
        if name == "fractional" and min(abs(fit.reaction_order - integer) for integer in (1, 2)) < 0.05:
            warnings.append("Free-order estimate is near an integer; do not interpret as a distinct fractional mechanism.")
        if fit.reaction_order_fitted and (
            fit.reaction_order <= 0.21 or fit.reaction_order >= 2.99
        ):
            warnings.append("Estimated order is near the fitting boundary.")
        if len(attempts) != len(starts):
            warnings.append("Some multistart optimization attempts failed.")
        candidates.append(ModelCandidate(
            name, fit, predicted, None, warnings=tuple(warnings),
            starts_attempted=len(starts), starts_converged=len(attempts)))

    successful = [c for c in candidates if c.error is None]
    if successful:
        best = min(c.fit.aicc for c in successful)
        relative = np.array([np.exp(-0.5 * max(0.0, c.fit.aicc - best)) for c in successful])
        weights = relative / relative.sum()
        for candidate, weight in zip(successful, weights):
            candidate.delta_aicc = float(candidate.fit.aicc - best)
            candidate.akaike_weight = float(weight)
    return sorted(candidates, key=lambda c: float("inf") if c.delta_aicc is None else c.delta_aicc)
