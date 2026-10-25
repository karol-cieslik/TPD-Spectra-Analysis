"""Monte Carlo evaluation of nonlinear bootstrap interval coverage.

Run as an optional, computationally expensive experiment:
python scripts/nonlinear_bootstrap_coverage.py --repetitions 30 --resamples 40
Coverage is conditional on intervals being issued; abstention is reported
separately, so apparently good conditional coverage cannot conceal failures.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from tpd_spectra.bootstrap import bootstrap_kinetic_parameters
from tpd_spectra.kinetics import simulate_tpd


def evaluate_coverage(*, seed=20261019, repetitions=30, resamples=40,
                      noise_fractions=(0.003, 0.01), max_nfev=120,
                      n_points=121):
    if not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError("repetitions must be a positive integer")
    if not isinstance(resamples, int) or resamples < 2:
        raise ValueError("resamples must be an integer >= 2")
    if not isinstance(n_points, int) or n_points < 12:
        raise ValueError("n_points must be an integer >= 12")
    if not isinstance(max_nfev, int) or max_nfev < 1:
        raise ValueError("max_nfev must be positive")
    if not noise_fractions or any(not np.isfinite(x) or x <= 0 for x in noise_fractions):
        raise ValueError("noise fractions must be finite and positive")

    temp = np.linspace(90.0, 345.0, n_points)
    energy_true, prefactor_true, beta = 1.2, 1e13, 1.0
    baseline, scale = 4.0, 1e5
    _, rate = simulate_tpd(temp, beta, energy_true, prefactor_true, 1.0)
    clean = baseline + scale * rate
    peak = float(np.max(clean) - baseline)
    rng = np.random.default_rng(seed)
    trials, summary = [], []

    for fraction in noise_fractions:
        group = []
        for replicate in range(repetitions):
            noisy = clean + rng.normal(0, fraction * peak, size=len(clean))
            fit_seed = int(rng.integers(0, 2**32 - 1))
            row = dict(noise_fraction=float(fraction), replicate=replicate,
                       true_energy_eV=energy_true, true_prefactor_s_inv=prefactor_true,
                       interval_issued=False, energy_covered=None, prefactor_covered=None,
                       bootstrap_successes=0, bootstrap_failures=resamples,
                       warning_count=None, warnings="", error="")
            try:
                result = bootstrap_kinetic_parameters(
                    temp, noisy, beta, reaction_order=1.0, fit_baseline=True,
                    n_resamples=resamples, seed=fit_seed,
                    initial_energy_ev=energy_true,
                    initial_prefactor_s_inv=prefactor_true, max_nfev=max_nfev)
                row.update(interval_issued=bool(result.valid),
                           bootstrap_successes=result.successful,
                           bootstrap_failures=result.failed,
                           warning_count=len(result.warnings),
                           warnings=" | ".join(result.warnings))
                if result.valid:
                    lo, hi = result.energy_ci95_eV
                    pl, ph = result.prefactor_ci95_s_inv
                    row["energy_covered"] = bool(lo <= energy_true <= hi)
                    row["prefactor_covered"] = bool(pl <= prefactor_true <= ph)
            except (ValueError, RuntimeError, FloatingPointError, OverflowError) as exc:
                row["error"] = str(exc)
            group.append(row)
            trials.append(row)
        issued = [r for r in group if r["interval_issued"]]
        n = len(issued)
        ne = sum(r["energy_covered"] for r in issued)
        npref = sum(r["prefactor_covered"] for r in issued)
        def exact_ci(k):
            if not n:
                return None, None
            c = binomtest(k, n).proportion_ci(confidence_level=0.95, method="exact")
            return float(c.low), float(c.high)
        el, eh = exact_ci(ne)
        pl, ph = exact_ci(npref)
        summary.append(dict(noise_fraction=float(fraction), total_trials=repetitions,
                            intervals_issued=n, intervals_withheld=repetitions - n,
                            issuance_fraction=n / repetitions,
                            nominal_coverage=0.95,
                            conditional_energy_coverage=ne / n if n else None,
                            energy_coverage_ci_lower=el, energy_coverage_ci_upper=eh,
                            conditional_prefactor_coverage=npref / n if n else None,
                            prefactor_coverage_ci_lower=pl, prefactor_coverage_ci_upper=ph,
                            energy_covered_out_of_all=ne / repetitions,
                            prefactor_covered_out_of_all=npref / repetitions))
    return trials, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("nonlinear-coverage-output"))
    parser.add_argument("--seed", type=int, default=20261019)
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--resamples", type=int, default=40)
    parser.add_argument("--max-nfev", type=int, default=120)
    args = parser.parse_args(argv)
    trials, summary = evaluate_coverage(seed=args.seed, repetitions=args.repetitions,
                                        resamples=args.resamples, max_nfev=args.max_nfev)
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, rows in (("trials.csv", trials), ("coverage_summary.csv", summary)):
        with (args.output / filename).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    from tpd_spectra import __version__
    metadata = dict(version=__version__, random_seed=args.seed,
                    repetitions_per_noise=args.repetitions,
                    bootstrap_resamples=args.resamples,
                    max_optimizer_evaluations=args.max_nfev,
                    model="one-state first-order Polanyi-Wigner with constant beta",
                    noise="independent additive Gaussian noise, fraction of clean peak height",
                    interpretation="conditional coverage among issued intervals; withholding rate is essential",
                    limitations=["same simulator used for generation and fitting",
                                 "fixed heating rate and temperature calibration",
                                 "no drift or correlated noise",
                                 "percentile bootstrap with empirical residual sigma",
                                 "not independent experimental validation"])
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
