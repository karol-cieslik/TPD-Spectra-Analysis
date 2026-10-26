"""Portable, reproducible Explorer export bundle.

No recomputation occurs during export; outputs capture the displayed fits and
Monte Carlo summary. Physical interpretation remains model-dependent.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import csv
import json

import numpy as np
from matplotlib.figure import Figure
from .identity import build_identity
from .workflow_analysis import plot_observations


def export_explorer_bundle(folder, temperature_c, signal, comparison, *,
                           beta_k_s, monte_carlo=None, source=None, settings=None):
    """Save fits, residuals, model ranking, uncertainty summary and metadata."""
    destination = Path(folder)
    temp, y = np.asarray(temperature_c, dtype=float), np.asarray(signal, dtype=float)
    if temp.ndim != 1 or y.shape != temp.shape or temp.size == 0:
        raise ValueError("Export requires matching nonempty one-dimensional data")
    if not np.all(np.isfinite(temp)) or not np.all(np.isfinite(y)):
        raise ValueError("Export requires finite data")
    if not comparison:
        raise ValueError("There are no model fits to export")
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError("Heating rate must be positive and finite")

    def table(name, fields, rows):
        with (destination / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    fit_rows, trace_rows = [], []
    curves = []
    for model in comparison:
        fit = model.fit
        profile = getattr(fit,'identifiability_diagnostics',{}).get('zero_order_profile',{}) if fit else {}
        valid = model.error is None and model.prediction is not None
        fit_rows.append({
            "model": model.name, "success": valid, "error": model.error or "",
            "order": fit.reaction_order if fit else "",
            "energy_eV": fit.activation_energy_eV if fit else "",
            "prefactor_s_inv": fit.prefactor_s_inv if fit else "",
            "prefactor_interpretation": 'Representative, not unique; conditional ranges are not confidence intervals' if profile else '',
            "conditional_prefactor_range_s_inv": profile.get('conditional_prefactor_range_s_inv',''),
            "conditional_signal_scale_range": profile.get('conditional_signal_scale_range',''),
            "depletion_bracket_c": profile.get('depletion_bracket_c',''),
            "signal_scale": fit.signal_scale if fit else "",
            "baseline": fit.baseline if fit else "",
            "rmse": fit.rmse_signal if fit else "",
            "aicc": fit.aicc if fit else "", "bic": fit.bic if fit else "",
            "delta_aicc": model.delta_aicc if model.delta_aicc is not None else "",
            "akaike_weight": model.akaike_weight if model.akaike_weight is not None else "",
            "warnings": "; ".join(model.warnings),
            "starts_attempted": model.starts_attempted, "starts_converged": model.starts_converged,
        })
        if valid:
            pred = np.asarray(model.prediction, dtype=float)
            if pred.shape != y.shape:
                raise ValueError(f"Prediction grid does not match input: {model.name}")
            if not np.all(np.isfinite(pred)):
                raise ValueError(f"Prediction contains nonfinite values: {model.name}")
            curves.append((model.name, pred))
    destination.mkdir(parents=False, exist_ok=False)
    table("model_comparison.csv", list(fit_rows[0]), fit_rows)
    for idx, (t, s) in enumerate(zip(temp, y)):
        row = {"temperature_c": float(t), "experimental_signal": float(s)}
        for name, pred in curves:
            row[f"{name}_fit"] = float(pred[idx])
            row[f"{name}_residual"] = float(s - pred[idx])
        trace_rows.append(row)
    table("fitted_curves.csv", list(trace_rows[0]), trace_rows)

    fig = Figure(figsize=(9, 6))
    ax = fig.add_subplot(211)
    plot_observations(ax,temp,y,label='Input signal')
    residual_ax = fig.add_subplot(212, sharex=ax)
    for index,(name, pred) in enumerate(curves):
        ax.plot(temp, pred, label=name,linestyle=('-', '--', '-.', ':')[index%4],linewidth=1.5)
        residual_ax.plot(temp, y - pred, label=name)
    ax.set_ylabel("Signal (a.u.)")
    ax.legend(fontsize=8)
    residual_ax.axhline(0, color="gray", linewidth=.8)
    residual_ax.set_xlabel("Temperature (°C)")
    residual_ax.set_ylabel("Residual")
    fig.tight_layout()
    fig.savefig(destination / "fit_overlay_and_residuals.png", dpi=300)
    fig.savefig(destination / "fit_overlay_and_residuals.svg")

    if monte_carlo is not None:
        summary = []
        for name, wins in monte_carlo.winning_counts.items():
            row = {"model": name, "wins": wins,
                   "completed_replicates": monte_carlo.replicates_completed,
                   "valid_parameter_refits": monte_carlo.successful_parameter_fits[name],
                   "failed_or_incomplete_rankings": monte_carlo.failed_rankings,
                   "range_status": "conditional percentile range" if monte_carlo.parameter_intervals.get(name) else "withheld: insufficient successful refits"}
            for parameter, bounds in monte_carlo.parameter_intervals.get(name, {}).items():
                row[parameter + "_p2_5_successful_refits"] = bounds[0]
                row[parameter + "_p97_5_successful_refits"] = bounds[1]
            summary.append(row)
        fields = ["model", "wins", "completed_replicates", "valid_parameter_refits", "failed_or_incomplete_rankings", "range_status"]
        fields += sorted(set().union(*(set(row) - set(fields) for row in summary)))
        table("uncertainty_summary.csv", fields, summary)
        if monte_carlo.replicate_records:
            table("monte_carlo_replicates.csv", list(monte_carlo.replicate_records[0]), monte_carlo.replicate_records)
        mc_fig = Figure(figsize=(8, 4.5))
        mc_ax = mc_fig.add_subplot(111)
        names = list(monte_carlo.winning_counts)
        mc_ax.bar(names, [monte_carlo.winning_counts[n] for n in names])
        mc_ax.set_ylabel("AICc wins (conditional on reference model)")
        mc_ax.set_title("Monte Carlo model-ranking stability")
        mc_fig.tight_layout()
        mc_fig.savefig(destination / "model_ranking_stability.png", dpi=300)
    manifest = {
        "schema_version": 2,
        "software": build_identity(),
        "source": str(source) if source is not None else None,
        "input_arrays_sha256": sha256(
            np.ascontiguousarray(np.column_stack((temp, y)), dtype="<f8").tobytes()
        ).hexdigest(),
        "temperature_min_c": float(temp.min()),
        "temperature_max_c": float(temp.max()),
        "n_points": int(temp.size),
        "heating_rate_k_s": float(beta_k_s),
        "settings": settings or {},
        "models": [r["model"] for r in fit_rows],
        "monte_carlo": asdict(monte_carlo) if monte_carlo is not None else None,
        "warning": "Model ranking is not proof of a physical desorption mechanism.",
    }
    (destination / "explorer_analysis.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    return destination
