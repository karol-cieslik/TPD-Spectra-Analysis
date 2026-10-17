"""Synthetic multi-heating-rate recovery benchmark for Phase 6.

Run from the repository root: python scripts/phase6_validation.py
This is a numerical stress test, not validation against certified experimental data.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tpd_spectra.kinetics import simulate_tpd, fit_global_polanyi_wigner  # noqa: E402

TRUE_E = 1.15
TRUE_NU = 1e13
BETAS = (0.5, 1.5, 4.0)
NOISE_LEVELS = (0.0, 0.01, 0.03, 0.05)
REPLICATES = 2


def make_traces(noise_fraction: float, seed: int):
    rng = np.random.default_rng(seed)
    traces = []
    for beta in BETAS:
        temp = np.linspace(80, 400, 81)
        _, rate = simulate_tpd(temp, beta, TRUE_E, TRUE_NU, 1.0)
        scale = 1000.0 / max(float(np.max(rate)), 1e-30)
        signal = 3.0 + scale * rate
        if noise_fraction:
            signal = signal + rng.normal(0.0, noise_fraction * np.ptp(signal), size=signal.size)
        traces.append({'temperature_c': temp, 'signal': signal, 'beta_k_s': beta})
    return traces


def main():
    rows = []
    for noise in NOISE_LEVELS:
        for replicate in range(REPLICATES):
            try:
                fit, _ = fit_global_polanyi_wigner(
                    make_traces(noise, seed=6000 + int(noise * 10000) * 10 + replicate),
                    reaction_order=1.0, initial_energy_ev=1.05,
                    initial_prefactor_s_inv=1e13, max_nfev=80)
                rows.append({
                    'noise_fraction_of_trace_range': noise, 'replicate': replicate + 1,
                    'success': fit.success, 'true_energy_eV': TRUE_E,
                    'fitted_energy_eV': fit.activation_energy_eV,
                    'energy_error_eV': fit.activation_energy_eV - TRUE_E,
                    'true_prefactor_s_inv': TRUE_NU, 'fitted_prefactor_s_inv': fit.prefactor_s_inv,
                    'log10_prefactor_error': np.log10(fit.prefactor_s_inv / TRUE_NU),
                    'max_normalized_rmse': max(fit.normalized_rmse_by_trace),
                    'energy_log10_prefactor_correlation': fit.energy_log10_prefactor_correlation,
                    'jacobian_condition_number': fit.jacobian_condition_number,
                    'warnings': ' | '.join(fit.warnings),
                })
            except Exception as exc:
                rows.append({'noise_fraction_of_trace_range': noise, 'replicate': replicate + 1,
                             'success': False, 'error': str(exc)})
    out = ROOT / 'output' / 'phase6_validation'
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / 'global_fit_noise_recovery.csv', index=False)
    successful = df[df.get('success', False) == True] if 'success' in df else df.iloc[0:0]
    summary = {
        'purpose': 'Synthetic recovery benchmark; not experimental validation',
        'true_activation_energy_eV': TRUE_E,
        'true_prefactor_s_inv': TRUE_NU,
        'heating_rates_K_s': list(BETAS),
        'noise_levels_fraction_of_each_trace_range': list(NOISE_LEVELS),
        'replicates_per_level': REPLICATES,
        'runs': int(len(df)),
        'successful_runs': int(len(successful)),
        'median_absolute_energy_error_eV': float(successful['energy_error_eV'].abs().median()) if len(successful) else None,
        'median_absolute_log10_prefactor_error': float(successful['log10_prefactor_error'].abs().median()) if len(successful) else None,
        'interpretation': 'Review per-run errors, correlation, conditioning and warnings. Successful optimisation alone is not evidence of parameter identifiability.'
    }
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    print(f'Wrote {out / "global_fit_noise_recovery.csv"}')


if __name__ == '__main__':
    main()
