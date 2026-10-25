"""Conservative parametric-bootstrap uncertainty for one-state kinetic fits.

Simulates independent Gaussian detector noise around a *fitted* trace. It is
conditional on the chosen kinetic model, constant heating rate, fixed reaction
order, signal preprocessing, and the chosen temperature window.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np

from .kinetics import fit_polanyi_wigner


@dataclass
class BootstrapResult:
    valid: bool
    method: str
    requested: int
    successful: int
    failed: int
    energy_ci95_eV: tuple[float, float] | None
    prefactor_ci95_s_inv: tuple[float, float] | None
    log10_prefactor_ci95: tuple[float, float] | None
    energy_log10_prefactor_correlation: float | None
    observed_energy_eV: float | None
    observed_prefactor_s_inv: float | None
    warnings: list[str]

    def as_dict(self):
        return asdict(self)


def bootstrap_kinetic_parameters(temperature_c, signal, heating_rate_k_s, *,
                                 reaction_order=1.0, fit_baseline=True,
                                 n_resamples=100, seed=20261019,
                                 initial_energy_ev=1.0,
                                 initial_prefactor_s_inv=1e13,
                                 max_nfev=300,
                                 minimum_success_fraction=0.9):
    """Estimate percentile intervals, or withhold them if fit is unreliable.

    The Gaussian noise sigma is estimated from residuals of the original fit.
    Individual bootstrap fits are reoptimized and only successful, finite
    positive parameter pairs are considered. Requested/failure counts are
    always reported. Low bootstrap convergence or numerical identifiability
    warnings suppress the reported intervals entirely.
    """
    temp = np.asarray(temperature_c, dtype=float)
    observed = np.asarray(signal, dtype=float)
    if temp.ndim != 1 or observed.shape != temp.shape or len(temp) < 12:
        raise ValueError("temperature and signal must be matching 1D arrays with at least 12 points")
    if not np.all(np.isfinite(temp)) or not np.all(np.isfinite(observed)) or np.any(np.diff(temp) <= 0):
        raise ValueError("bootstrap requires finite data and strictly increasing temperature")
    if isinstance(n_resamples, bool) or not isinstance(n_resamples, (int, np.integer)) or n_resamples < 2:
        raise ValueError("n_resamples must be an integer >= 2")
    if reaction_order == 0:
        raise ValueError("Zero-order prefactor/scale are non-unique; use Explorer Monte Carlo for conditional depletion brackets.")
    if not np.isfinite(minimum_success_fraction) or not 0 < minimum_success_fraction <= 1:
        raise ValueError("minimum_success_fraction must be in (0, 1]")
    original, prediction = fit_polanyi_wigner(
        temp, observed, heating_rate_k_s, reaction_order=reaction_order,
        fit_reaction_order=False, fit_baseline=fit_baseline,
        initial_energy_ev=initial_energy_ev,
        initial_prefactor_s_inv=initial_prefactor_s_inv, max_nfev=max_nfev)
    warnings = list(original.identifiability_diagnostics.get("warnings", []))
    if not original.success:
        warnings.append("Original nonlinear optimizer failed; uncertainty is withheld.")
    residuals = observed - prediction
    degrees = len(observed) - (4 if fit_baseline else 3)
    sigma = float(np.sqrt(np.sum(residuals ** 2) / degrees)) if degrees > 0 else float("nan")
    if not np.isfinite(sigma) or sigma <= 0:
        warnings.append("Residual noise estimate is nonpositive or invalid.")
    rng = np.random.default_rng(seed)
    energy, logpref = [], []
    if original.success and np.isfinite(sigma) and sigma > 0:
        for _ in range(n_resamples):
            synthetic = prediction + rng.normal(0.0, sigma, len(prediction))
            try:
                fit, _ = fit_polanyi_wigner(
                    temp, synthetic, heating_rate_k_s,
                    reaction_order=reaction_order, fit_reaction_order=False,
                    fit_baseline=fit_baseline, initial_energy_ev=original.activation_energy_eV,
                    initial_prefactor_s_inv=original.prefactor_s_inv,
                    max_nfev=max_nfev)
                if (fit.success and not fit.identifiability_diagnostics.get("warnings", [])
                        and np.isfinite(fit.activation_energy_eV) and fit.activation_energy_eV > 0
                        and np.isfinite(fit.prefactor_s_inv) and fit.prefactor_s_inv > 0):
                    energy.append(fit.activation_energy_eV)
                    logpref.append(np.log10(fit.prefactor_s_inv))
            except (ValueError, RuntimeError, FloatingPointError, OverflowError):
                pass
    completed = len(energy)
    if completed < n_resamples * minimum_success_fraction:
        warnings.append("Too many bootstrap refits failed; uncertainty is withheld.")
    if completed < 20:
        warnings.append("Fewer than 20 valid bootstrap refits; percentile intervals are withheld.")
    valid = not warnings and completed >= 20
    eci = pci = logci = correlation = None
    if valid:
        eci = tuple(float(x) for x in np.percentile(energy, (2.5, 97.5)))
        logci = tuple(float(x) for x in np.percentile(logpref, (2.5, 97.5)))
        pci = (float(10 ** logci[0]), float(10 ** logci[1]))
        if np.std(energy) > 0 and np.std(logpref) > 0:
            correlation = float(np.corrcoef(energy, logpref)[0, 1])
        if correlation is None or not np.isfinite(correlation):
            valid = False
            warnings.append("Parameter correlation is undefined; uncertainty is withheld.")
            eci = pci = logci = correlation = None
    return BootstrapResult(valid, "parametric_gaussian_percentile_conditional",
                           int(n_resamples), completed, int(n_resamples-completed),
                           eci, pci, logci, correlation,
                           float(original.activation_energy_eV), float(original.prefactor_s_inv), warnings)
