"""Workflow adapters. Equations and optimizers remain in the existing engine."""
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from uuid import uuid4
import math
from importlib.metadata import version
import numpy as np
from . import __version__
from .analysis import leading_edge_fit, redhead_energy, smooth_signal
from .kinetics import fit_polanyi_wigner


def serial(value):
    """Strict JSON representation: unavailable numeric quantities are null."""
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [serial(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def processed_signal(dataset, recipe=None):
    recipe = recipe or dataset.processing
    y = smooth_signal(dataset.spectrum.signal, int(recipe['window']), recipe['smoothing'])
    return np.asarray(y) - float(recipe['baseline'])


def selected_arrays(dataset, snapshot):
    t = dataset.spectrum.temperature_clean_c
    y = processed_signal(dataset, snapshot['processing'])
    lo, hi = snapshot['region']
    keep = (t >= lo) & (t <= hi) & np.isfinite(t) & np.isfinite(y)
    return t[keep].copy(), y[keep].copy()


def calculate(dataset, snapshot, cancelled=lambda: False):
    """Compute only the submitted snapshot; never consult live UI/project state."""
    t, y = selected_arrays(dataset, snapshot)
    settings, method = snapshot['settings'], snapshot['method']
    if cancelled():
        raise InterruptedError('Cancelled')
    beta = float(settings['beta'])
    if not np.isfinite(beta) or beta <= 0:
        raise ValueError('Heating rate must be positive and finite (K/s).')
    warnings = ['Signal must be proportional to desorption rate; calibration and acquisition metadata are not available.',
                'Temperature uses the existing heuristic cleaning recorded in the import report.',
                'Heating rate is supplied by the user (default 1 K/s), not inferred from acquisition metadata. Verify the ramp and units.']
    plots = {'temperature_c': t, 'signal': y}
    if method == 'Leading edge':
        low, high = float(settings['lower']), float(settings['upper'])
        if low < snapshot['region'][0] or high > snapshot['region'][1] or low >= high:
            raise ValueError('Leading-edge interval must lie inside the selected peak.')
        fit = leading_edge_fit(t, y, beta, low, high)
        values = asdict(fit)
        keep = (t >= low) & (t <= high) & (y > 0)
        x = 1 / (t[keep] + 273.15)
        plots.update(x=x, observed=np.log(y[keep]), predicted=fit.slope*x+fit.intercept,
                     x_label='1 / T (K⁻¹)', y_label='ln(signal)')
        warnings += ['Apparent energy assumes negligible coverage change over the chosen leading edge; this is not an order assignment.',
                     'Energy interval is regression-only. Absolute prefactor is unavailable for uncalibrated signal.']
        if fit.energy_ev <= 0:
            warnings.append('Non-positive apparent activation energy: inspect the selected interval, baseline and applicability.')
    elif method == 'Redhead':
        if len(t) < 3 or np.ptp(y) <= 0:
            raise ValueError('Select a varying peak with at least three points.')
        peak = int(np.argmax(y))
        energy = redhead_energy(float(t[peak]), float(settings['prefactor']), beta)
        values = {'energy_ev': energy, 'peak_temperature_c': float(t[peak]), 'beta_k_s': beta,
                  'assumed_prefactor_s_inv': float(settings['prefactor']), 'energy_interval': None}
        plots.update(x=t, observed=y, x_label='Temperature (°C)', y_label='Signal (instrument units)')
        warnings += ['Classical first-order Redhead approximation, constant assumed prefactor and linear heating ramp. No confidence interval is inferred.']
        if peak in (0, len(t)-1):
            warnings.append('Peak maximum lies at a region boundary; the selected interval may not contain the peak.')
    elif method == 'Polanyi–Wigner':
        fit, prediction = fit_polanyi_wigner(t, y, beta, reaction_order=float(settings['order']),
            fit_reaction_order=bool(settings['free_order']), initial_energy_ev=float(settings['energy']),
            initial_prefactor_s_inv=float(settings['prefactor']), fit_baseline=bool(settings['fit_baseline']),
            max_nfev=int(settings['max_nfev']), cancelled=cancelled)
        if not fit.success:
            raise ValueError('Optimizer did not converge: ' + fit.message)
        values = asdict(fit)
        plots.update(x=t, observed=y, predicted=prediction, x_label='Temperature (°C)', y_label='Signal (instrument units)')
        warnings += ['Single initially populated state, normalized initial coverage one at the selected interval start, linear ramp.',
                     'Energy and prefactor may be non-identifiable; numerical order does not establish mechanism. No parameter confidence interval is inferred.']
        if fit.reaction_order == 0:
            warnings.append('Known beta limitation: the zero-order optimizer can converge with biased amplitude near the depletion edge. Convergence is not an accuracy check; inspect residuals. This path failed the external-beta clean-reference residual tolerance.')
    else:
        raise ValueError('Unsupported analysis method')
    if cancelled():
        raise InterruptedError('Cancelled')
    return serial({'id': uuid4().hex, 'snapshot': snapshot, 'status': 'fitted' if method == 'Polanyi–Wigner' else 'preview',
                   'values': values, 'plots': plots, 'warnings': warnings, 'version': __version__,
                   'dependencies': {n: version(n) for n in ('numpy','scipy','pandas','matplotlib')},
                   'created_utc': datetime.now(timezone.utc).isoformat(), 'import_report': dataset.spectrum.import_report})


def draw_result(figure, result):
    figure.clear()
    p = result['plots']
    predicted = p.get('predicted')
    ax = figure.add_subplot(211 if predicted is not None else 111)
    ax.plot(p['x'], p['observed'], label='Selected processed signal')
    if predicted is not None:
        ax.plot(p['x'], predicted, label='Fitted curve')
        residual = figure.add_subplot(212)
        residual.plot(p['x'], np.asarray(p['observed'])-np.asarray(predicted))
        residual.axhline(0, color='gray', linewidth=.7)
        residual.set(xlabel=p['x_label'], ylabel='Residual')
    if 'peak_temperature_c' in result['values']:
        ax.axvline(result['values']['peak_temperature_c'], color='teal', label='Selected maximum')
    ax.set(xlabel=p['x_label'], ylabel=p['y_label'])
    ax.legend(fontsize=8)
