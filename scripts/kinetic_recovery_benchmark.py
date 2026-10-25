"""Reproducible quantitative Polanyi-Wigner parameter-recovery benchmark.

Run: python scripts/kinetic_recovery_benchmark.py --output benchmark-output
Outputs CSV and JSON; input spectra are synthetic, never experimental.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from tpd_spectra.kinetics import fit_polanyi_wigner, simulate_tpd


def run_benchmark(*, seed: int = 20261019, replicates: int = 3,
                  noise_levels=(0.0, 0.003, 0.01), max_nfev: int = 120):
    """Return individual trial rows and summaries with explicit failure counts.

    Noise is iid Gaussian, expressed as a fraction of the *clean peak height*.
    A single synthetic first-order trace is fitted with a free E and prefactor.
    This deliberately does not establish experimental validity or CI coverage.
    """
    if replicates < 1 or max_nfev < 1:
        raise ValueError("replicates and max_nfev must be positive")
    levels = [float(v) for v in noise_levels]
    if not levels or any(not np.isfinite(v) or v < 0 for v in levels):
        raise ValueError("noise levels must be finite and nonnegative")
    rng = np.random.default_rng(seed)
    temperature = np.linspace(80.0, 350.0, 136)
    energy_true, prefactor_true, beta, scale, baseline = 1.2, 1e13, 1.0, 1e5, 4.0
    _, clean_rate = simulate_tpd(temperature, beta, energy_true, prefactor_true, 1.0)
    clean_signal = baseline + scale * clean_rate
    peak_height = float(np.max(clean_signal - baseline))
    rows = []
    for noise in levels:
        for repetition in range(replicates):
            observed = clean_signal + rng.normal(0.0, noise * peak_height, temperature.size)
            row = {"seed": seed, "noise_fraction_of_peak": noise, "replicate": repetition,
                   "true_energy_eV": energy_true, "true_prefactor_s_inv": prefactor_true,
                   "fit_success": False, "fit_energy_eV": None, "fit_prefactor_s_inv": None,
                   "energy_error_eV": None, "log10_prefactor_error": None,
                   "normalized_rmse": None, "jacobian_condition_number": None,
                   "warning_count": None, "error": ""}
            try:
                fit, _ = fit_polanyi_wigner(
                    temperature, observed, beta, reaction_order=1.0,
                    initial_energy_ev=1.2, initial_prefactor_s_inv=1e13,
                    max_nfev=max_nfev)
                row.update(fit_success=bool(fit.success),
                           fit_energy_eV=float(fit.activation_energy_eV),
                           fit_prefactor_s_inv=float(fit.prefactor_s_inv),
                           energy_error_eV=float(fit.activation_energy_eV - energy_true),
                           log10_prefactor_error=float(np.log10(fit.prefactor_s_inv / prefactor_true)),
                           normalized_rmse=float(fit.normalized_rmse),
                           jacobian_condition_number=float(fit.jacobian_condition_number),
                           warning_count=len(fit.identifiability_diagnostics.get("warnings", [])),
                           error="" if fit.success else fit.message)
            except (ValueError, RuntimeError, FloatingPointError) as exc:
                row["error"] = str(exc)
            rows.append(row)
    summaries = []
    for noise in levels:
        subset = [r for r in rows if r["noise_fraction_of_peak"] == noise]
        good = [r for r in subset if r["fit_success"]]
        summaries.append({
            "noise_fraction_of_peak": noise, "total_trials": len(subset),
            "successful_trials": len(good), "failed_trials": len(subset) - len(good),
            "convergence_fraction": len(good) / len(subset),
            "energy_bias_eV": float(np.mean([r["energy_error_eV"] for r in good])) if good else None,
            "energy_rmse_eV": float(np.sqrt(np.mean([r["energy_error_eV"]**2 for r in good]))) if good else None,
            "log10_prefactor_rmse": float(np.sqrt(np.mean([r["log10_prefactor_error"]**2 for r in good]))) if good else None,
        })
    return rows, summaries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("benchmark-output"))
    parser.add_argument("--seed", type=int, default=20261019)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--max-nfev", type=int, default=120)
    args = parser.parse_args(argv)
    rows, summaries = run_benchmark(seed=args.seed, replicates=args.replicates,
                                    max_nfev=args.max_nfev)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in (("trials.csv", rows), ("summary.csv", summaries)):
        with (args.output / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    from tpd_spectra import __version__
    metadata = {"software_version": __version__, "seed": args.seed, "replicates": args.replicates,
                "max_nfev": args.max_nfev, "model": "first-order Polanyi-Wigner",
                "noise_model": "independent Gaussian, standard deviation fraction of clean peak height",
                "parameterization": "energy and log10 prefactor free; scale and baseline free",
                "limitations": "Synthetic internal-model recovery, not independent verification, confidence-interval coverage, or experimental validation"}
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(summaries, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
