#!/usr/bin/env python3
"""Digitize and assess the published 2-propanol/HOPG monolayer series.

The source image is the Figure 2 raster embedded in the published article PDF.
It is redistributed under the source's stated CC BY licence with attribution
in the adjacent README. The analysis is figure-derived, not raw-data validation.

Run from the repository root:

    python scripts/experimental_2propanol_hopg_check.py

This writes the digitized pixel-coordinate series and conditional fitter results
beside the source image. The paper's log-intensity/log-integrated-area order
estimator is also reconstructed over a declared fixed-temperature window.
That estimator differs from the application's full-trace Polanyi-Wigner fit.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA_DIR = ROOT / "validation" / "experimental" / "fractional_2propanol_hopg"
FIGURE = DATA_DIR / "source_figure.png"
OUTPUT_CSV = DATA_DIR / "digitized_monolayer.csv"
OUTPUT_JSON = DATA_DIR / "results.json"
SOFTWARE_COMMIT = "1542cc6f2a635a575d60e1811b79d8493c7d25c0"

# Pixel coordinates are in the 982 x 1064 raster embedded as Figure 2 in the
# source PDF. Axis ticks are 120..170 K; the horizontal axis is the zero line.
X_LEFT_PX = 76.0
X_RIGHT_PX = 954.0
Y_ZERO_PX = 472.5
PLOT_Y_MIN_PX = 5
PLOT_Y_MAX_PX = 470
EXPOSURES_LM = (1, 2, 5, 10)
COLOR_ORDER = ("black", "green", "red", "blue")
BETA_K_S = 0.5
FIXED_TEMPERATURES_K = np.arange(137.0, 145.0 + 0.001, 0.5)
MIN_SIGNAL_PX_FOR_LOG_SLOPE = 3.0
FIT_WINDOW_K = (130.0, 155.0)
INITIAL_ENERGY_EV = 46.6 / 96.48533212331002
INITIAL_PREFACTOR_S_INV = 10.0**12.9
MAX_NFEV = 300


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _trace_masks(rgb: np.ndarray) -> dict[str, np.ndarray]:
    red, green, blue = (rgb[..., i].astype(float) for i in range(3))
    return {
        "black": (rgb.max(axis=2) < 100)
        & (np.ptp(rgb.astype(float), axis=2) < 30),
        "green": (green > red * 1.35) & (green > blue * 1.25) & (green > 55),
        "red": (red > green * 1.4) & (red > blue * 1.5) & (red > 100),
        "blue": (blue > red * 1.8) & (green > red * 1.7)
        & (blue > green * 1.05) & (blue > 100),
    }


def digitize(figure_path: Path, y_zero_px: float = Y_ZERO_PX,
             x_left_px: float = X_LEFT_PX, x_right_px: float = X_RIGHT_PX):
    image = mpimg.imread(figure_path)
    if image.ndim != 3 or image.shape[2] < 3:
        raise ValueError("source figure must be an RGB PNG")
    rgb = image[..., :3]
    if rgb.dtype.kind == "f":
        rgb = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
    height, width = rgb.shape[:2]
    if (width, height) != (982, 1064):
        raise ValueError(f"unexpected source-figure dimensions: {width} x {height}")
    masks = _trace_masks(rgb)
    x_pixels = np.arange(int(x_left_px), int(x_right_px) + 1)
    temperature_k = 120.0 + (x_pixels - x_left_px) / (x_right_px - x_left_px) * 50.0
    traces: dict[int, np.ndarray] = {}
    for exposure, color in zip(EXPOSURES_LM, COLOR_ORDER):
        signal = np.full(x_pixels.size, np.nan, dtype=float)
        for index, x in enumerate(x_pixels):
            if x <= X_LEFT_PX + 1 or x >= X_RIGHT_PX - 1:
                # Exclude the heavy vertical plot frame from trace detection.
                continue
            if color != "black" and 720 <= x <= 870:
                # The colored legend occupies this x interval. The physical
                # trace is already at baseline here; interpolate across it.
                continue
            y0 = 430 if color == "black" else PLOT_Y_MIN_PX
            ys = np.flatnonzero(masks[color][y0:PLOT_Y_MAX_PX + 1, x]) + y0
            if not ys.size:
                continue
            # Colored legends, labels and tails can share a column. Select the
            # lowest (closest-to-zero) visible trace segment, then its pixel
            # center to avoid a systematic line-thickness choice.
            if color == "black":
                y_center = float(np.median(ys))
            else:
                bottom = int(ys.max())
                y_center = float(np.median(ys[ys >= bottom - 2]))
            signal[index] = max(y_zero_px - y_center, 0.0)
        # Leave absent leading/trailing line pixels at zero. Interpolate only
        # the deliberately masked legend interval, which lies in the tail.
        finite = np.isfinite(signal)
        if not finite.any():
            raise ValueError(f"no pixels matched {color} trace")
        first, last = np.flatnonzero(finite)[[0, -1]]
        missing = ~finite
        signal[missing] = np.interp(x_pixels[missing], x_pixels[finite], signal[finite])
        signal[:first] = 0.0
        signal[last + 1:] = 0.0
        traces[exposure] = signal
    return temperature_k, traces


def order_estimator(temperature_k: np.ndarray, traces: dict[int, np.ndarray],
                    *, baseline_px: float = Y_ZERO_PX) -> dict:
    areas = {exposure: float(np.trapezoid(signal, temperature_k))
             for exposure, signal in traces.items()}
    sampled = {exposure: np.interp(FIXED_TEMPERATURES_K, temperature_k, signal)
               for exposure, signal in traces.items()}
    slopes = []
    used = []
    x = np.log(np.array([areas[e] for e in EXPOSURES_LM]))
    for i, temp in enumerate(FIXED_TEMPERATURES_K):
        intensities = np.array([sampled[e][i] for e in EXPOSURES_LM])
        if np.any(intensities < MIN_SIGNAL_PX_FOR_LOG_SLOPE):
            continue
        slope = float(np.polyfit(x, np.log(intensities), 1)[0])
        slopes.append(slope)
        used.append(float(temp))
    if not slopes:
        raise ValueError("no fixed temperatures satisfy the signal threshold")
    mean = float(np.mean(slopes))
    two_sem = float(2.0 * np.std(slopes, ddof=1) / np.sqrt(len(slopes))) if len(slopes) > 1 else None
    return {
        "estimator": "OLS slope of ln(digitized signal at fixed T) vs ln(full-window integrated figure signal)",
        "fixed_temperature_window_K": [float(FIXED_TEMPERATURES_K[0]), float(FIXED_TEMPERATURES_K[-1])],
        "fixed_temperature_step_K": 0.5,
        "minimum_signal_for_log_fit_pixel_units": MIN_SIGNAL_PX_FOR_LOG_SLOPE,
        "used_temperatures_K": used,
        "slope_by_temperature": slopes,
        "mean_order": mean,
        "two_sem_across_temperature_slopes": two_sem,
        "uncertainty_interpretation": "Descriptive spread over correlated fixed-temperature slopes; the figure pixels and adjacent-temperature estimates are not independent samples, so this is not an independent-sample confidence interval.",
        "integrated_areas_pixel_units_K": {str(k): v for k, v in areas.items()},
        "area_ratios_relative_to_1_Lm": {str(k): areas[k] / areas[1] for k in areas},
        "baseline_sensitivity": _baseline_sensitivity(temperature_k, traces, areas),
        "interpretation": "Figure-derived reconstruction of the paper's estimator; the paper does not report the fixed-temperature interval. The digitized result is conditional on our declared interval, pixel calibration and baseline.",
    }


def _baseline_sensitivity(temperature_k, traces, base_areas):
    results = []
    for offset in (-1.0, 0.0, 1.0):
        shifted = {e: np.maximum(signal + offset, 0.0) for e, signal in traces.items()}
        areas = np.array([np.trapezoid(shifted[e], temperature_k) for e in EXPOSURES_LM])
        slopes = []
        for temp in FIXED_TEMPERATURES_K:
            vals = np.array([np.interp(temp, temperature_k, shifted[e]) for e in EXPOSURES_LM])
            if np.any(vals < MIN_SIGNAL_PX_FOR_LOG_SLOPE):
                continue
            slopes.append(float(np.polyfit(np.log(areas), np.log(vals), 1)[0]))
        results.append({"common_y_zero_shift_px": offset,
                        "mean_order": float(np.mean(slopes)) if slopes else None,
                        "n_temperatures": len(slopes)})
    return results


def fit_single_trace(temperature_k: np.ndarray, signal: np.ndarray, exposure_lm: int) -> list[dict]:
    from tpd_spectra.kinetics import fit_polanyi_wigner

    selected = (temperature_k >= FIT_WINDOW_K[0]) & (temperature_k <= FIT_WINDOW_K[1])
    # Resample at 0.2 K to avoid treating every adjacent raster column as an
    # independent experimental point.
    temp = np.arange(FIT_WINDOW_K[0], FIT_WINDOW_K[1] + 1e-8, 0.2)
    observed = np.interp(temp, temperature_k[selected], signal[selected])
    fits = []
    for label, order, free in (("fixed_order_1", 1.0, False),
                               ("fixed_order_1.23", 1.23, False),
                               ("free_order", 1.23, True)):
        result, _ = fit_polanyi_wigner(
            temp - 273.15, observed, BETA_K_S,
            reaction_order=order, fit_reaction_order=free,
            initial_energy_ev=INITIAL_ENERGY_EV,
            initial_prefactor_s_inv=INITIAL_PREFACTOR_S_INV,
            fit_baseline=False, max_nfev=MAX_NFEV,
        )
        fits.append({
            "candidate": label,
            "reaction_order": float(result.reaction_order),
            "activation_energy_eV": float(result.activation_energy_eV),
            "prefactor_s_inv_numeric_convention": float(result.prefactor_s_inv),
            "normalized_rmse": float(result.normalized_rmse),
            "aicc": float(result.aicc),
            "success": bool(result.success),
            "jacobian_condition_number": float(result.jacobian_condition_number),
            "identifiability_diagnostics": result.identifiability_diagnostics,
            "n_points": int(result.n_points),
        })
    return fits


def main() -> None:
    if not FIGURE.is_file():
        raise SystemExit(f"Missing source figure: {FIGURE}")
    temperature_k, traces = digitize(FIGURE)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["temperature_K", "signal_1_Lm_pixel_units", "signal_2_Lm_pixel_units",
                         "signal_5_Lm_pixel_units", "signal_10_Lm_pixel_units"])
        for i, temp in enumerate(temperature_k):
            writer.writerow([f"{temp:.6f}", *(f"{traces[e][i]:.6f}" for e in EXPOSURES_LM)])

    order = order_estimator(temperature_k, traces)
    fits = {str(e): fit_single_trace(temperature_k, signal, e)
            for e, signal in traces.items()}
    payload = {
        "case_name": "Ayling et al. 2-propanol/HOPG Figure 2A monolayer coverage series",
        "scope": "Figure-derived, raster-digitized experimental challenge; not raw-data validation or an independent energy validation.",
        "source": {
            "article": "S. A. Ayling, D. J. Burke, T. L. Salter, and W. A. Brown, RSC Advances 7 (2017), 51621-51631.",
            "doi": "10.1039/C7RA10410C",
            "figure": "Fig. 2A; 1, 2, 5, and 10 Lm traces only",
            "source_pdf_record": "University of Sussex Figshare item 23450411, file IPA_published.pdf (file ID 41159684)",
            "source_pdf_sha256": "079056826b24d83a98a608a06715526ea2d360e512571f3271447f3ddffe7394",
            "source_figure_sha256": sha256(FIGURE),
            "article_license": "CC BY 3.0 Unported stated in the published article; Sussex Figshare record labels deposited article CC BY 4.0.",
            "data_origin": "Color/black trace pixels digitized from the published figure; no author raw data were available or used.",
        },
        "software_commit": SOFTWARE_COMMIT,
        "digitization": {
            "input_dimensions_px": [982, 1064],
            "x_axis_calibration": {"pixel_left": X_LEFT_PX, "temperature_left_K": 120.0,
                                   "pixel_right": X_RIGHT_PX, "temperature_right_K": 170.0},
            "zero_signal_axis_pixel": Y_ZERO_PX,
            "y_axis": "Rate of desorption / a.u.; no numerical y ticks. The raster pixel height is used as a common arbitrary signal scale.",
            "trace_colors_by_exposure_Lm": {str(e): c for e, c in zip(EXPOSURES_LM, COLOR_ORDER)},
            "figure_pixels_retrieved": True,
            "digitized_traces_created": True,
            "temperature_points_per_trace": int(temperature_k.size),
            "axis_temperature_uncertainty_estimate_K": 0.12,
            "curve_reading_uncertainty_estimate_px": 1.0,
        },
        "protocol": {
            "heating_rate_K_s": BETA_K_S,
            "reported_initial_temperature_K": 26.0,
            "order_estimator": order,
            "production_fitter_window_K": list(FIT_WINDOW_K),
            "production_fitter": "Application fit_polanyi_wigner applied separately to each single-color curve; each fit has normalized initial coverage and free signal scale.",
            "production_fitter_candidates": ["fixed_order_1", "fixed_order_1.23", "free_order in [0.2, 3.0]"],
            "initial_energy_eV": INITIAL_ENERGY_EV,
            "initial_prefactor_s_inv": INITIAL_PREFACTOR_S_INV,
            "fit_baseline": False,
            "max_nfev": MAX_NFEV,
            "sampling_step_K": 0.2,
            "coverage_scaling": "Trace integrated areas are used only in the source-style log-log order reconstruction. Deposition exposure in Lm is not substituted for measured surface coverage in the production kinetic fitter.",
        },
        "source_published_references": {
            "monolayer_order": 1.23,
            "monolayer_order_uncertainty_2sem": 0.03,
            "monolayer_energy_kJ_mol": 46.6,
            "monolayer_energy_uncertainty_kJ_mol": 3.7,
            "prefactor_log10_s_inv": 12.9,
            "prefactor_uncertainty_log10_s_inv": 0.3,
            "paper_order_method": "Mean slope of ln I(T) versus ln relative integrated coverage over a range of fixed temperatures; twice SEM.",
        },
        "figure_order_reconstruction": order,
        "single_trace_production_fits": fits,
        "limitations": [
            "The source's fixed-temperature interval is not specified; the declared 137-145 K window is a reconstruction choice.",
            "The figure has no numerical y-axis ticks, and pixel integration is not calibrated absolute coverage.",
            "The source order is a coverage-series log-log slope; the software fits each normalized full trace separately. These fitted orders are not the same estimand.",
            "The paper reports coverage-dependent monolayer barriers and islanding, so a single-state constant-energy model is a challenge hypothesis, not a faithful physical model.",
            "Rasterized data, especially the low-dose 1 Lm trace, have finite pixel resolution and visible line-thickness uncertainty.",
            "The reported 2 SEM is across adjacent fixed-temperature slopes from one figure and is descriptive, not a confidence interval from independent observations.",
            "No raw author data are included; the source figure is redistributed with attribution under its stated open licence.",
        ],
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Reconstructed source-style order: {order['mean_order']:.3f} +/- {order['two_sem_across_temperature_slopes']:.3f} (2 SEM over {len(order['used_temperatures_K'])} fixed temperatures)")
    for exposure, candidates in fits.items():
        print(f"{exposure} Lm: " + "; ".join(
            f"{fit['candidate']} n={fit['reaction_order']:.3f} NRMSE={fit['normalized_rmse']:.3f} cond={fit['jacobian_condition_number']:.2g}"
            for fit in candidates))


if __name__ == "__main__":
    main()
