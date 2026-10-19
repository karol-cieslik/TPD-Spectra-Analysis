"""Additional synthetic TPD benchmark scenarios.

The data-generating model and inverse fitter share implementation;
these are recovery/robustness checks, not independent model validation.
"""
from __future__ import annotations

import numpy as np
from tpd_spectra.kinetics import (simulate_tpd, fit_polanyi_wigner,
                                 fit_two_state_polanyi_wigner)


def benchmark_matrix(*, seed=20261019, noise_levels=(0.0, 0.003),
                     orders=(0.0, 1.0, 2.0, 1.5),
                     heating_rates=(0.5, 1.0, 2.0), replicates=2,
                     max_nfev=120):
    """Report recovery errors, optimizer failures and warnings per scenario."""
    if replicates < 1 or max_nfev < 1:
        raise ValueError("replicates and max_nfev must be positive")
    if not noise_levels or not orders or not heating_rates:
        raise ValueError("scenario parameter lists cannot be empty")
    if any(not np.isfinite(x) or x < 0 for x in noise_levels):
        raise ValueError("noise fractions must be finite and nonnegative")
    if any(not np.isfinite(x) or x < 0 for x in orders):
        raise ValueError("orders must be finite and nonnegative")
    if any(not np.isfinite(x) or x <= 0 for x in heating_rates):
        raise ValueError("heating rates must be positive and finite")
    rng = np.random.default_rng(seed)
    rows = []
    temp = np.linspace(80, 420, 171)
    true_e, true_nu = 1.2, 1e13
    for order in orders:
        for beta in heating_rates:
            _, rate = simulate_tpd(temp, beta, true_e, true_nu, order)
            clean = 2.0 + 1e5 * rate
            peak = max(float(np.max(clean) - 2.0), 1e-12)
            for noise in noise_levels:
                for repeat in range(replicates):
                    observed = clean + rng.normal(0, noise * peak, len(temp))
                    row = dict(scenario="single_state", order=float(order), heating_rate_K_s=float(beta),
                               noise_fraction=float(noise), replicate=repeat, seed=seed,
                               true_energy_eV=true_e, estimated_energy_eV=None,
                               energy_error_eV=None, true_prefactor_s_inv=true_nu,
                               log10_prefactor_error=None, success=False, warnings=None,
                               normalized_rmse=None, failure_reason="")
                    try:
                        fit, _ = fit_polanyi_wigner(
                            temp, observed, beta, reaction_order=order,
                            initial_energy_ev=true_e, initial_prefactor_s_inv=true_nu,
                            max_nfev=max_nfev)
                        row.update(success=bool(fit.success),
                                   estimated_energy_eV=float(fit.activation_energy_eV),
                                   energy_error_eV=float(fit.activation_energy_eV - true_e),
                                   log10_prefactor_error=float(np.log10(fit.prefactor_s_inv / true_nu)),
                                   warnings=len(fit.identifiability_diagnostics.get("warnings", [])),
                                   normalized_rmse=float(fit.normalized_rmse),
                                   failure_reason="" if fit.success else fit.message)
                    except (ValueError, RuntimeError, FloatingPointError) as exc:
                        row["failure_reason"] = str(exc)
                    rows.append(row)
    return rows


def benchmark_overlap(*, seed=20261019, separations=(0.08, 0.20),
                      noise_fraction=0.003, max_nfev=250):
    """Explore two-state resolution; ordered fitted energies are not a proof of two sites."""
    if not separations or any(not np.isfinite(x) or x <= 0 for x in separations):
        raise ValueError("separations must be positive and finite")
    if not np.isfinite(noise_fraction) or noise_fraction < 0 or max_nfev < 1:
        raise ValueError("invalid noise fraction or fitting evaluation limit")
    temp = np.linspace(80, 440, 181)
    rng = np.random.default_rng(seed)
    rows = []
    for separation in separations:
        e1, e2 = 1.1, 1.1 + separation
        _, rate1 = simulate_tpd(temp, 1.0, e1, 1e13, 1.0)
        _, rate2 = simulate_tpd(temp, 1.0, e2, 1e13, 1.0)
        clean = 2.0 + 1e5 * rate1 + 1e5 * rate2
        observed = clean + rng.normal(0, noise_fraction * (clean.max() - 2.0), len(temp))
        row = dict(scenario="two_state", true_energy1_eV=e1, true_energy2_eV=e2,
                   separation_eV=separation, noise_fraction=noise_fraction, seed=seed,
                   fit_energy1_eV=None, fit_energy2_eV=None,
                   absolute_energy_error_mean_eV=None, success=False, warnings=None,
                   normalized_rmse=None, failure_reason="")
        try:
            fit, _ = fit_two_state_polanyi_wigner(
                temp, observed, 1.0, reaction_order=1.0,
                initial_energies_ev=(e1, e2), initial_prefactor_s_inv=1e13,
                max_nfev=max_nfev)
            energies = fit.activation_energies_eV
            row.update(success=bool(fit.success), fit_energy1_eV=float(energies[0]),
                       fit_energy2_eV=float(energies[1]),
                       absolute_energy_error_mean_eV=float(np.mean(np.abs(np.array(energies) - [e1, e2]))),
                       warnings=len(fit.warnings),
                       normalized_rmse=float(fit.normalized_rmse),
                       failure_reason="" if fit.success else fit.message)
        except (ValueError, RuntimeError, FloatingPointError) as exc:
            row["failure_reason"] = str(exc)
        rows.append(row)
    return rows
