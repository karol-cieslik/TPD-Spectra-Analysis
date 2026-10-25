"""Export synthetic kinetic benchmark trials and honest summary statistics."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from scripts.kinetic_benchmark_matrix import benchmark_matrix, benchmark_overlap


def summarize(rows, group_keys):
    groups = {}
    for row in rows:
        key = tuple(row[k] for k in group_keys)
        groups.setdefault(key, []).append(row)
    result = []
    for key, trials in groups.items():
        good = [r for r in trials if r["success"]]
        d = dict(zip(group_keys, key))
        d.update(n_trials=len(trials), n_success=len(good),
                 n_failure=len(trials)-len(good),
                 convergence_fraction=len(good)/len(trials))
        for column in ("energy_error_eV", "log10_prefactor_error",
                       "absolute_energy_error_mean_eV"):
            values = [r[column] for r in good if r.get(column) is not None
                      and np.isfinite(r[column])]
            d[column+"_bias"] = float(np.mean(values)) if values else None
            d[column+"_rmse"] = float(np.sqrt(np.mean(np.square(values)))) if values else None
        result.append(d)
    return result


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("benchmark-matrix-output"))
    p.add_argument("--seed", type=int, default=20261019)
    p.add_argument("--replicates", type=int, default=2)
    p.add_argument("--max-nfev", type=int, default=120)
    args = p.parse_args(argv)
    single = benchmark_matrix(seed=args.seed, replicates=args.replicates,
                              max_nfev=args.max_nfev)
    overlap = benchmark_overlap(seed=args.seed)
    summary = summarize(single, ("order", "heating_rate_K_s", "noise_fraction"))
    overlap_summary = summarize(overlap, ("separation_eV", "noise_fraction"))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in (("single_trials.csv", single), ("single_summary.csv", summary),
                       ("overlap_trials.csv", overlap), ("overlap_summary.csv", overlap_summary)):
        write_csv(args.output/name, rows)
    from tpd_spectra import __version__
    metadata = {"software_version": __version__, "seed": args.seed,
                "replicates_per_single_scenario": args.replicates,
                "max_nfev": args.max_nfev,
                "noise": "iid Gaussian noise; amplitude relative to clean peak height",
                "limitation": "Internal synthetic model recovery, not external validation or calibrated uncertainty.",
                "single_scenarios": len(single), "overlap_scenarios": len(overlap)}
    (args.output/"metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
