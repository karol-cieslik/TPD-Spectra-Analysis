"""Numerical core for TPD/TDS spectra analysis.

Temperatures are accepted in degrees Celsius at the I/O boundary. Kinetic
calculations explicitly convert to kelvin. Signal is assumed proportional to
desorption rate only where the user selects a physically appropriate region.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import math
import re

import numpy as np
import pandas as pd
from scipy.constants import Boltzmann, elementary_charge
from scipy.stats import t as student_t

K_B_EV = Boltzmann / elementary_charge


@dataclass
class Spectrum:
    source: str
    time_min: np.ndarray
    temperature_c: np.ndarray
    signal: np.ndarray
    temperature_clean_c: np.ndarray
    points_temperature_corrected: int = 0


@dataclass
class FitResult:
    slope: float
    intercept: float
    r_squared: float
    n_points: int
    energy_ev: float
    prefactor_s_inv: float
    beta_k_s: float
    lower_c: float
    upper_c: float
    residual_rmse: float = float("nan")
    slope_stderr: float = float("nan")
    energy_ci95_lower_ev: float = float("nan")
    energy_ci95_upper_ev: float = float("nan")

    def as_dict(self):
        return asdict(self)


def _numeric_column(df: pd.DataFrame, requested: str | None, alternatives: Iterable[str], role: str) -> str:
    if requested and requested in df.columns:
        return requested
    for name in alternatives:
        if name in df.columns:
            return name
    raise ValueError(f"Could not identify {role} column. Available columns: {list(df.columns)}")


def load_spectrum(path: str | Path, *, skiprows: int = 29,
                  time_column: str | None = None, signal_column: str | None = None,
                  temperature_column: str | None = None,
                  delimiter: str = ';', decimal: str = ',') -> Spectrum:
    """Load the legacy instrument CSV schema or a compatible delimited file.

    The legacy format has 29 metadata rows and columns `ms`, `DHTA+`, and
    `Temperatura`. Required channels are detected by name; empty trailing
    columns and the human-readable Time column are ignored.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    errors = []
    df = None
    # Prefer the documented legacy export, then accept ordinary comma/tab CSVs
    # with either decimal style and a conventional header row.
    layouts = [(skiprows, delimiter, decimal), (0, delimiter, decimal),
               (0, ',', '.'), (0, '\t', '.'), (0, ';', '.')]
    seen = set()
    for rows, sep, decimal_mark in layouts:
        if (rows, sep, decimal_mark) in seen:
            continue
        seen.add((rows, sep, decimal_mark))
        try:
            candidate = pd.read_csv(path, skiprows=rows, sep=sep, decimal=decimal_mark)
            if len(candidate.columns) > 1:
                df = candidate
                break
        except Exception as exc:  # surfaced below as an actionable import error
            errors.append(str(exc))
    if df is None:
        raise ValueError(f"Could not parse {path.name} as a delimited instrument export. {errors}")
    df.columns = [str(c).strip() for c in df.columns]
    tcol = _numeric_column(df, time_column, ('ms', 'Time_ms', 'time_ms', 'Time (ms)', 'Time', 'time'), 'time (ms)')
    scol = _numeric_column(df, signal_column, ('DHTA+', 'Signal', 'signal', 'Intensity', 'intensity', 'Signal (a.u.)'), 'signal')
    tempcol = _numeric_column(df, temperature_column, ('Temperatura', 'Temperature', 'temperature', 'Temp', 'temp',
                                                       'Temperature (°C)', 'Temperature_C', 'Temp_C'), 'temperature')
    frame = pd.DataFrame({
        'time_ms': pd.to_numeric(df[tcol], errors='coerce'),
        'signal': pd.to_numeric(df[scol], errors='coerce'),
        'temperature_c': pd.to_numeric(df[tempcol], errors='coerce'),
    }).dropna()
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    frame = frame.sort_values('time_ms', kind='stable').drop_duplicates('time_ms', keep='first')
    if len(frame) < 3:
        raise ValueError(f"{path.name}: fewer than 3 valid rows after parsing required channels")
    time_min = (frame.time_ms.to_numpy(float) - float(frame.time_ms.iloc[0])) / 60_000.0
    signal = frame.signal.to_numpy(float)
    raw_temp = frame.temperature_c.to_numpy(float)
    clean_temp = clean_temperature(raw_temp)
    return Spectrum(path.name, time_min, raw_temp, signal, clean_temp,
                    int(np.count_nonzero(~np.isclose(raw_temp, clean_temp, equal_nan=True))))


def clean_temperature(temperature_c: Iterable[float], *, upward_jump_c: float = 1.5,
                      downward_jump_c: float = 0.5, max_temperature_c: float = 800.0) -> np.ndarray:
    """Conservatively flag abrupt jumps and implausible high values, then interpolate.

    The thresholds preserve the original notebook's heuristic defaults, but
    are explicit parameters. Both endpoints are treated consistently.
    """
    temp = np.asarray(temperature_c, dtype=float).copy()
    if temp.ndim != 1 or temp.size < 2:
        raise ValueError('temperature must be a one-dimensional array with at least two values')
    bad = ~np.isfinite(temp) | (temp > max_temperature_c)
    delta = np.diff(temp)
    # Flag the sample after an abrupt jump. This is a heuristic, not a physical model.
    jump_idx = np.where((delta > upward_jump_c) | (delta < -downward_jump_c))[0] + 1
    bad[jump_idx] = True
    temp[bad] = np.nan
    valid = np.isfinite(temp)
    if valid.sum() < 2:
        raise ValueError('Temperature cleaning left fewer than two valid points; review thresholds/data')
    idx = np.arange(temp.size)
    temp[~valid] = np.interp(idx[~valid], idx[valid], temp[valid])
    return temp


def smooth_signal(signal: Iterable[float], window: int = 10, method: str = 'median') -> np.ndarray:
    """Centered rolling average/median with explicit, non-biased edge handling."""
    values = np.asarray(signal, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError('signal must be a non-empty one-dimensional array')
    if not isinstance(window, (int, np.integer)) or window < 1:
        raise ValueError('window must be a positive integer')
    if method not in {'median', 'mean', 'none'}:
        raise ValueError("method must be 'median', 'mean', or 'none'")
    if method == 'none' or window == 1:
        return values.copy()
    if method == 'median':
        return pd.Series(values).rolling(window=window, center=True, min_periods=1).median().to_numpy()
    return pd.Series(values).rolling(window=window, center=True, min_periods=1).mean().to_numpy()


def _linear_regression_diagnostics(x: np.ndarray, y: np.ndarray) -> dict:
    """OLS diagnostics for a straight-line fit; intervals describe regression noise only."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape or x.size < 3:
        raise ValueError("linear regression diagnostics require matching 1D arrays with >=3 points")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("linear regression inputs must be finite")
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    residuals = y - predicted
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y - y.mean())**2))
    r2 = 1.0 if ss_tot == 0 and ss_res == 0 else (float("nan") if ss_tot == 0 else 1.0 - ss_res / ss_tot)
    rmse = float(np.sqrt(np.mean(residuals**2)))
    dof = x.size - 2
    sxx = float(np.sum((x - x.mean())**2))
    if dof > 0 and sxx > 0:
        residual_variance = ss_res / dof
        slope_se = float(np.sqrt(residual_variance / sxx))
        intercept_se = float(np.sqrt(residual_variance * (1.0 / x.size + x.mean()**2 / sxx)))
        critical = float(student_t.ppf(0.975, dof))
    else:
        slope_se = intercept_se = critical = float("nan")
    return {
        "slope": float(slope), "intercept": float(intercept), "r_squared": float(r2),
        "residual_rmse": rmse, "slope_stderr": slope_se, "intercept_stderr": intercept_se,
        "slope_ci95_lower": float(slope - critical * slope_se),
        "slope_ci95_upper": float(slope + critical * slope_se),
        "residuals": residuals, "predicted": predicted,
    }


def spectrum_quality_diagnostics(signal: Iterable[float], temperature_c: Iterable[float],
                                 corrected_points: int = 0) -> dict:
    """Return transparent screening metrics; do not silently baseline-correct data.

    The 10th-percentile level is only a low-signal proxy, not a baseline estimate.
    Thresholds are pragmatic warnings and must be reviewed for each instrument.
    """
    sig = np.asarray(signal, dtype=float)
    temp = np.asarray(temperature_c, dtype=float)
    if sig.ndim != 1 or temp.shape != sig.shape or sig.size == 0:
        raise ValueError("signal and temperature must be non-empty matching 1D arrays")
    finite = np.isfinite(sig) & np.isfinite(temp)
    if not finite.any():
        raise ValueError("spectrum has no finite signal/temperature pairs")
    s = sig[finite]
    low_proxy = float(np.percentile(s, 10))
    dynamic_range = float(np.max(s) - np.min(s))
    low_proxy_fraction = low_proxy / dynamic_range if dynamic_range > 0 else float("nan")
    return {
        "signal_negative_fraction": float(np.mean(s < 0)),
        "signal_dynamic_range": dynamic_range,
        "signal_p10_low_level_proxy": low_proxy,
        "signal_p10_proxy_over_range": low_proxy_fraction,
        "temperature_corrected_fraction": float(corrected_points / sig.size),
        "finite_pair_fraction": float(np.mean(finite)),
    }


def heating_rate(time_min: Iterable[float], temperature_c: Iterable[float], *,
                 lower_c: float = 125.0, upper_c: float = 700.0,
                 max_time_min: float | None = 10.0) -> tuple[float, float, float]:
    """Linear regression of temperature against time; returns beta (K/s), R², slope (K/min)."""
    t = np.asarray(time_min, dtype=float)
    temp = np.asarray(temperature_c, dtype=float)
    if t.shape != temp.shape:
        raise ValueError('time and temperature arrays must have identical shapes')
    mask = np.isfinite(t) & np.isfinite(temp) & (temp >= lower_c) & (temp < upper_c)
    if max_time_min is not None:
        mask &= t <= max_time_min
    if mask.sum() < 3:
        raise ValueError(f'Only {mask.sum()} points in heating-rate fit; widen the interval or inspect data')
    x, y = t[mask], temp[mask]
    reg = _linear_regression_diagnostics(x, y)
    slope = reg["slope"]
    if slope <= 0:
        raise ValueError(f'Heating-rate fit has non-positive slope ({slope:g} °C/min)')
    return float(slope/60.0), float(reg["r_squared"]), float(slope)


def leading_edge_fit(temperature_c: Iterable[float], signal: Iterable[float], beta_k_s: float,
                     lower_c: float, upper_c: float, *, min_points: int = 5) -> FitResult:
    """Fit ln(signal) vs 1/T for the selected leading-edge interval.

    Implements ln(r) = ln(nu/beta) - E/(k_B T), assuming signal is proportional
    to rate and the selected region follows the stated zero-order-style model.
    """
    temp = np.asarray(temperature_c, dtype=float)
    sig = np.asarray(signal, dtype=float)
    if temp.shape != sig.shape:
        raise ValueError('temperature and signal arrays must have identical shapes')
    if not (lower_c < upper_c):
        raise ValueError('lower_c must be smaller than upper_c')
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError('heating rate beta_k_s must be positive and finite')
    # One mask is applied to both arrays: no x/y index misalignment.
    mask = np.isfinite(temp) & np.isfinite(sig) & (temp >= lower_c) & (temp <= upper_c) & (sig > 0)
    x = 1.0 / (temp[mask] + 273.15)
    y = np.log(sig[mask])
    if x.size < min_points:
        raise ValueError(f'Leading-edge fit has {x.size} positive-signal points; need at least {min_points}')
    reg = _linear_regression_diagnostics(x, y)
    slope, intercept = reg["slope"], reg["intercept"]
    energy = -float(slope) * K_B_EV
    prefactor = float(beta_k_s * np.exp(np.clip(intercept, -700, 700)))
    # Transform the slope's OLS confidence interval into energy. This captures
    # regression scatter only; it excludes systematic/model uncertainty.
    ci_low = -reg["slope_ci95_upper"] * K_B_EV
    ci_high = -reg["slope_ci95_lower"] * K_B_EV
    return FitResult(float(slope), float(intercept), reg["r_squared"], int(x.size), energy, prefactor,
                     float(beta_k_s), float(lower_c), float(upper_c), reg["residual_rmse"],
                     reg["slope_stderr"], float(ci_low), float(ci_high))


def redhead_energy(t_peak_c: float, prefactor_s_inv: float, beta_k_s: float,
                   *, peak_order: int = 1, redhead_constant: float = 3.64) -> float:
    """Return Redhead apparent energy in eV using peak temperature in kelvin.

    Uses E = k_B*T_p*[ln(nu*T_p/beta) - 3.64] for first-order desorption.
    `prefactor_s_inv` and `beta_k_s` must both use inverse seconds.
    """
    if peak_order != 1:
        raise ValueError('This Redhead implementation is for first-order desorption only')
    t_k = float(t_peak_c) + 273.15
    if not np.isfinite(t_k) or t_k <= 0:
        raise ValueError('peak temperature must correspond to a positive kelvin temperature')
    if not np.isfinite(prefactor_s_inv) or prefactor_s_inv <= 0:
        raise ValueError('prefactor_s_inv must be positive and finite')
    if not np.isfinite(beta_k_s) or beta_k_s <= 0:
        raise ValueError('beta_k_s must be positive and finite')
    log_arg = prefactor_s_inv * t_k / beta_k_s
    if log_arg <= 0 or not np.isfinite(log_arg):
        raise ValueError('invalid Redhead logarithm argument')
    return float(K_B_EV * t_k * (math.log(log_arg) - redhead_constant))


def short_label(filename: str) -> str:
    """Use the historical 6CC label when available; otherwise use the stem."""
    match = re.search(r'6CC_(.*?)_2xPID', filename)
    return match.group(1) if match else Path(filename).stem


def analyze_file(path: str | Path, *, leading_edge_c: tuple[float, float] = (130.0, 170.0),
                 redhead_region_c: tuple[float, float] = (230.0, 400.0),
                 prefactor_s_inv: float = 1e20, smoothing_window: int = 10,
                 smoothing_method: str = 'median', heating_region_c: tuple[float, float] = (125.0, 700.0),
                 max_time_min: float | None = 10.0) -> dict:
    spec = load_spectrum(path)
    beta, beta_r2, beta_slope = heating_rate(spec.time_min, spec.temperature_clean_c,
        lower_c=heating_region_c[0], upper_c=heating_region_c[1], max_time_min=max_time_min)
    smooth = smooth_signal(spec.signal, smoothing_window, smoothing_method)
    fit0 = None
    leading_error = ''
    try:
        fit0 = leading_edge_fit(spec.temperature_clean_c, smooth, beta, *leading_edge_c)
    except ValueError as exc:
        # Keep independent analyses available; never fabricate a fit for an empty/invalid region.
        leading_error = str(exc)
    mask = (spec.temperature_clean_c >= redhead_region_c[0]) & (spec.temperature_clean_c <= redhead_region_c[1])
    mask &= np.isfinite(smooth)
    if not mask.any():
        raise ValueError(f'{spec.source}: no data in Redhead peak-search interval {redhead_region_c}')
    peak_index = np.flatnonzero(mask)[np.argmax(smooth[mask])]
    peak_temp_c = float(spec.temperature_clean_c[peak_index])
    energy1 = redhead_energy(peak_temp_c, prefactor_s_inv, beta)
    energy_nu_low = redhead_energy(peak_temp_c, prefactor_s_inv / 10.0, beta)
    energy_nu_high = redhead_energy(peak_temp_c, prefactor_s_inv * 10.0, beta)
    quality = spectrum_quality_diagnostics(spec.signal, spec.temperature_clean_c, spec.points_temperature_corrected)
    warnings = []
    if beta_r2 < 0.98:
        warnings.append("Heating-rate regression R² is below 0.98; inspect the selected ramp interval.")
    if spec.points_temperature_corrected / max(1, spec.signal.size) > 0.02:
        warnings.append("More than 2% of temperature points were interpolated by heuristic cleaning.")
    if quality["signal_negative_fraction"] > 0:
        warnings.append("Signal contains negative values; inspect baseline and detector offset before kinetic analysis.")
    if fit0 is None:
        warnings.append("Leading-edge fit unavailable: " + leading_error)
    else:
        if fit0.r_squared < 0.98:
            warnings.append("Leading-edge regression R² is below 0.98; inspect residual structure and fit interval.")
        if fit0.energy_ev <= 0:
            warnings.append("Leading-edge slope implies a non-positive apparent energy; check interval, baseline and model suitability.")
    if peak_index == np.flatnonzero(mask)[0] or peak_index == np.flatnonzero(mask)[-1]:
        warnings.append("Maximum in the Redhead search interval lies at its boundary; widen the interval or inspect the peak.")
    if not np.isfinite(quality["signal_p10_proxy_over_range"]) or quality["signal_p10_proxy_over_range"] > 0.1:
        warnings.append("Low-signal level is appreciable relative to signal range; this is a screening flag, not an automatic baseline estimate.")
    return {
        'file_name': spec.source, 'short_name': short_label(spec.source),
        'n_points': int(spec.signal.size), 'temperature_points_corrected': spec.points_temperature_corrected,
        'heating_rate_K_s': beta, 'heating_rate_fit_R2': beta_r2, 'heating_rate_slope_C_min': beta_slope,
        'leading_edge_lower_C': leading_edge_c[0], 'leading_edge_upper_C': leading_edge_c[1],
        'leading_edge_energy_eV': fit0.energy_ev if fit0 else float('nan'),
        'leading_edge_prefactor_s_inv': fit0.prefactor_s_inv if fit0 else float('nan'),
        'leading_edge_fit_R2': fit0.r_squared if fit0 else float('nan'),
        'leading_edge_fit_points': fit0.n_points if fit0 else 0, 'leading_edge_error': leading_error,
        'leading_edge_residual_RMSE_ln_signal': fit0.residual_rmse if fit0 else float('nan'),
        'leading_edge_slope_stderr': fit0.slope_stderr if fit0 else float('nan'),
        'leading_edge_energy_CI95_lower_eV_regression_only': fit0.energy_ci95_lower_ev if fit0 else float('nan'),
        'leading_edge_energy_CI95_upper_eV_regression_only': fit0.energy_ci95_upper_ev if fit0 else float('nan'),
        'redhead_region_lower_C': redhead_region_c[0], 'redhead_region_upper_C': redhead_region_c[1],
        'second_peak_temperature_C': peak_temp_c, 'redhead_energy_eV': energy1,
        'redhead_prefactor_assumed_s_inv': prefactor_s_inv,
        'redhead_energy_prefactor_0.1x_eV': energy_nu_low,
        'redhead_energy_prefactor_10x_eV': energy_nu_high,
        'redhead_energy_change_for_prefactor_decade_eV': (energy_nu_high - energy_nu_low) / 2.0,
        **quality,
        'diagnostic_warnings': ' | '.join(warnings),
        'smoothing_method': smoothing_method, 'smoothing_window_points': smoothing_window,
        'method_note': 'Apparent model-dependent estimate; inspect fits and validate assumptions.'
    }
