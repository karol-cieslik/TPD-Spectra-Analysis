"""Parametric Monte Carlo uncertainty for isolated-peak kinetic model comparison.

Replicates are generated under a specified fitted reference model with iid
Gaussian detector noise. Frequencies indicate ranking stability conditional
on that reference and noise model, never probabilities of true mechanisms.
"""
from __future__ import annotations

from dataclasses import dataclass, field
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
    replicate_records: list[dict] = field(default_factory=list)
    interval_note: str = "2.5–97.5 percentile range of successful conditional refits; not a coverage-validated confidence interval."
    minimum_successful_refits: int = 100


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
    reference_comparison=None,
    minimum_successful_refits: int = 100,
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
    if not isinstance(minimum_successful_refits, int) or minimum_successful_refits < 2:
        raise ValueError("minimum_successful_refits must be at least 2")
    temp = np.asarray(temperature_c, dtype=float)
    y = np.asarray(signal, dtype=float)
    initial = reference_comparison if reference_comparison is not None else compare_desorption_orders(temp, y, beta_k_s, orders=tuple(orders),
                                         fit_baseline=fit_baseline, max_nfev=max_nfev,
                                         multistart=True)
    if {c.name for c in initial} != set(orders):
        raise ValueError("Reference comparison must contain exactly the selected models")
    usable = {c.name: c for c in initial if c.error is None}
    if not usable:
        raise ValueError("No converged model exists for Monte Carlo reference")
    if reference_model is None:
        reference_model = next(iter(usable))
    if reference_model not in usable:
        raise ValueError("Reference model must have a converged fit")
    ref = usable[reference_model]
    if np.asarray(ref.prediction).shape != y.shape or not np.all(np.isfinite(ref.prediction)):
        raise ValueError("Reference prediction must match the selected finite signal")
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
    records = []
    for _ in range(replicates):
        if cancelled is not None and cancelled():
            break
        synthetic = ref.prediction + rng.normal(0.0, sigma, size=y.size)
        try:
            comparison = compare_desorption_orders(
                temp, synthetic, beta_k_s, orders=tuple(orders),
                fit_baseline=fit_baseline, max_nfev=max_nfev, multistart=multistart,
                initial_energy_ev=ref.fit.activation_energy_eV,
                initial_prefactor_s_inv=ref.fit.prefactor_s_inv, cancelled=cancelled)
        except InterruptedError:
            break
        successful = [c for c in comparison if c.error is None]
        # Do not award a winner when a requested competitor failed to fit.
        if len(successful) == len(orders):
            wins[successful[0].name] += 1
        else:
            failed_rankings += 1
        for candidate in comparison:
            f = candidate.fit
            records.append({"replicate": completed + 1, "model": candidate.name,
                            "error": candidate.error, "ranking_complete": len(successful) == len(orders),
                            "energy_eV": f.activation_energy_eV if f else None,
                            "log10_prefactor": float(np.log10(f.prefactor_s_inv)) if f else None,
                            "order": f.reaction_order if f else None,
                            "aicc": f.aicc if f else None,
                            "warnings": list(candidate.warnings)})
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
            for parameter, samples in series.items() if len(samples) >= minimum_successful_refits
        }
    return MonteCarloResult(
        reference_model, seed, replicates, completed, sigma,
        {name: wins[name] for name in orders}, failed_rankings, intervals,
        {name: len(series["energy_eV"]) for name, series in values.items()},
        completed < replicates,
        replicate_records=records, minimum_successful_refits=minimum_successful_refits,
    )
