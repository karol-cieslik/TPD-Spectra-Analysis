"""Parametric Monte Carlo uncertainty for isolated-peak kinetic model comparison.

Replicates are generated under a specified fitted reference model with iid
Gaussian detector noise. Frequencies indicate ranking stability conditional
on that reference and noise model, never probabilities of true mechanisms.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from typing import Callable
import numpy as np

from .kinetics_explorer import compare_desorption_orders


@dataclass
class MonteCarloResult:
    reference_model: str
    seed: int
    replicates_requested: int
    replicates_completed: int
    noise_sigma: float
    winning_counts: dict[str, int]
    failed_rankings: int
    parameter_intervals: dict[str, dict[str, tuple[float, float]]]
    successful_parameter_fits: dict[str, int]
    cancelled: bool


def run_kinetics_monte_carlo(
    temperature_c, signal, beta_k_s: float, *,
    orders=("zero", "first", "second", "fractional"),
    reference_model: str | None = None,
    replicates: int = 500,
    seed: int = 42,
    fit_baseline: bool = True,
    max_nfev: int = 150,
    multistart: bool = False,
    progress: Callable[[int, int], None] | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> MonteCarloResult:
    """Refit selected models to each simulated observation.

    Estimate noise sigma from residuals of the best fitted reference, with
    degrees-of-freedom adjustment. All candidates share each synthetic trace.
    Parameter intervals are percentile intervals of *successful refits* only.
    """
    if isinstance(replicates, bool) or not isinstance(replicates, int) or replicates < 1:
        raise ValueError("replicates must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    temp = np.asarray(temperature_c, dtype=float)
    y = np.asarray(signal, dtype=float)
    initial = compare_desorption_orders(temp, y, beta_k_s, orders=tuple(orders),
                                         fit_baseline=fit_baseline, max_nfev=max_nfev,
                                         multistart=True)
    usable = {c.name: c for c in initial if c.error is None}
    if not usable:
        raise ValueError("No converged model exists for Monte Carlo reference")
    if reference_model is None:
        reference_model = next(iter(usable))
    if reference_model not in usable:
        raise ValueError("Reference model must have a converged fit")
    ref = usable[reference_model]
    residual = y - ref.prediction
    n_params = 3 + int(fit_baseline) + int(reference_model == "fractional")
    sigma = float(np.sqrt(np.sum(residual ** 2) / max(1, y.size - n_params)))
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("Cannot estimate positive residual noise; supply noisy experimental data")
    rng = np.random.default_rng(seed)
    wins = Counter()
    values = {name: {"energy_eV": [], "log10_prefactor": [], "order": []} for name in orders}
    completed = 0
    failed_rankings = 0
    for _ in range(replicates):
        if cancelled is not None and cancelled():
            break
        synthetic = ref.prediction + rng.normal(0.0, sigma, size=y.size)
        comparison = compare_desorption_orders(
            temp, synthetic, beta_k_s, orders=tuple(orders),
            fit_baseline=fit_baseline, max_nfev=max_nfev, multistart=multistart,
            initial_energy_ev=ref.fit.activation_energy_eV,
            initial_prefactor_s_inv=ref.fit.prefactor_s_inv)
        successful = [c for c in comparison if c.error is None]
        if successful:
            wins[successful[0].name] += 1
        else:
            failed_rankings += 1
        for candidate in successful:
            f = candidate.fit
            record = values[candidate.name]
            record["energy_eV"].append(f.activation_energy_eV)
            record["log10_prefactor"].append(float(np.log10(f.prefactor_s_inv)))
            record["order"].append(f.reaction_order)
        completed += 1
        if progress is not None:
            progress(completed, replicates)
    intervals = {}
    for name, series in values.items():
        intervals[name] = {
            parameter: tuple(map(float, np.percentile(samples, [2.5, 97.5])))
            for parameter, samples in series.items() if samples
        }
    return MonteCarloResult(
        reference_model, seed, replicates, completed, sigma,
        {name: wins[name] for name in orders}, failed_rankings, intervals,
        {name: len(series["energy_eV"]) for name, series in values.items()},
        completed < replicates,
    )
