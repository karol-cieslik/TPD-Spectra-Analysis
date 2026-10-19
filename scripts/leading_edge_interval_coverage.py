"""Monte Carlo calibration check of leading-edge regression-only intervals.

Coverage applies solely to iid Gaussian errors *in log(signal)*, with a fixed,
predeclared fitting window. It excludes temperature, heating-rate, baseline,
model-form and nonlinear optimization uncertainty.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from tpd_spectra.analysis import K_B_EV, leading_edge_fit


def run_coverage(*, seed=20261019, repetitions=200, noise_sigmas=(0.01, 0.04),
                 energy_ev=0.55):
    if repetitions < 1 or not np.isfinite(energy_ev) or energy_ev <= 0:
        raise ValueError("repetitions and energy must be positive")
    if not noise_sigmas or any(not np.isfinite(x) or x < 0 for x in noise_sigmas):
        raise ValueError("noise standard deviations must be finite and nonnegative")
    rng = np.random.default_rng(seed)
    temp = np.linspace(120.0, 185.0, 131)
    log_signal = 12.0 - (energy_ev/K_B_EV)/(temp+273.15)
    trials = []
    summaries = []
    for sigma in noise_sigmas:
        start = len(trials)
        for repeat in range(repetitions):
            observed = np.exp(log_signal + rng.normal(0.0, sigma, temp.size))
            row = dict(seed=seed, sigma_log_signal=float(sigma), replicate=repeat,
                       true_energy_eV=float(energy_ev), fitted_energy_eV=None,
                       interval_lower_eV=None, interval_upper_eV=None,
                       covers_true_energy=None, failed=False, error="")
            try:
                fit = leading_edge_fit(temp, observed, beta_k_s=1.0,
                                       lower_c=130.0, upper_c=175.0)
                row.update(fitted_energy_eV=float(fit.energy_ev),
                           interval_lower_eV=float(fit.energy_ci95_lower_ev),
                           interval_upper_eV=float(fit.energy_ci95_upper_ev),
                           covers_true_energy=bool(
                               fit.energy_ci95_lower_ev <= energy_ev <= fit.energy_ci95_upper_ev))
            except (ValueError, RuntimeError, FloatingPointError) as exc:
                row.update(failed=True, error=str(exc))
            trials.append(row)
        group = trials[start:]
        valid = [t for t in group if not t["failed"]]
        count = sum(bool(t["covers_true_energy"]) for t in valid)
        n = len(valid)
        ci = binomtest(count, n).proportion_ci(confidence_level=0.95, method="exact") if n else None
        summaries.append(dict(sigma_log_signal=float(sigma), requested_trials=repetitions,
                              valid_trials=n, failed_trials=repetitions-n,
                              intervals_covering_truth=count,
                              observed_coverage=count/n if n else None,
                              binomial_ci95_lower=ci.low if ci else None,
                              binomial_ci95_upper=ci.high if ci else None,
                              nominal_coverage=0.95))
    return trials, summaries


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("coverage-output"))
    p.add_argument("--seed", type=int, default=20261019)
    p.add_argument("--repetitions", type=int, default=200)
    args = p.parse_args(argv)
    trials, summary = run_coverage(seed=args.seed, repetitions=args.repetitions)
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, data in (("coverage_trials.csv", trials), ("coverage_summary.csv", summary)):
        with (args.output/filename).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    metadata = dict(seed=args.seed, repetitions=args.repetitions,
                    nominal_coverage=0.95, data_generation="exact linear model in reciprocal temperature",
                    uncertainty_model="iid Gaussian residuals in log(signal); Student-t linear regression interval",
                    excludes=["baseline", "temperature calibration", "heating-rate uncertainty",
                              "fit-window selection", "correlated noise", "kinetic-model mismatch"],
                    warning="This is not coverage of nonlinear Polanyi-Wigner fit parameters.")
    (args.output/"metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
