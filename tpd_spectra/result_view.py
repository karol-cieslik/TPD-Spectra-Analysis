"""Method-aware, read-only presentation of submitted kinetic results.

This module changes no analysis values or scientific calculations. It only
classifies reported numbers so fitted parameters cannot be mistaken for
assumptions, regression estimates, or diagnostics.
"""

import json
import math


LABELS = {
    'energy_ev': 'Apparent / estimated energy',
    'activation_energy_eV': 'Activation energy',
    'prefactor_s_inv': 'Arrhenius prefactor',
    'assumed_prefactor_s_inv': 'Assumed Arrhenius prefactor',
    'reaction_order': 'Reaction order',
    'reaction_order_fitted': 'Reaction order optimized',
    'peak_temperature_c': 'Peak maximum temperature',
    'beta_k_s': 'Heating rate',
    'signal_scale': 'Detector signal scale',
    'baseline': 'Fitted constant baseline',
    'r_squared': 'R²',
    'rmse_signal': 'Signal RMSE',
    'residual_rmse': 'Regression residual RMSE',
    'normalized_rmse': 'Normalized RMSE',
    'n_points': 'Points used',
    'energy_ci95_lower_ev': 'Regression-only energy interval (lower)',
    'energy_ci95_upper_ev': 'Regression-only energy interval (upper)',
    'lower_c': 'Leading-edge interval (lower)',
    'upper_c': 'Leading-edge interval (upper)',
    'temperature_min_C': 'Fitted interval (lower)',
    'temperature_max_C': 'Fitted interval (upper)',
    'jacobian_condition_number': 'Jacobian condition number',
    'aic': 'AIC', 'aicc': 'AICc', 'bic': 'BIC',
    'slope': 'Leading-edge regression slope',
    'intercept': 'Leading-edge regression intercept',
    'slope_stderr': 'Regression slope standard error',
    'depletion_bracket_c': 'Depletion edge bracket',
    'conditional_prefactor_range_s_inv': 'Conditional prefactor range',
    'conditional_signal_scale_range': 'Conditional signal scale range',
    'prefactor_interpretation': 'Prefactor interpretation',
    'energy_interval': 'Energy interval',
}

UNITS = {
    'energy_ev': 'eV', 'activation_energy_eV': 'eV',
    'energy_ci95_lower_ev': 'eV', 'energy_ci95_upper_ev': 'eV',
    'prefactor_s_inv': 's⁻¹', 'assumed_prefactor_s_inv': 's⁻¹',
    'beta_k_s': 'K/s', 'peak_temperature_c': '°C',
    'lower_c': '°C', 'upper_c': '°C',
    'temperature_min_C': '°C', 'temperature_max_C': '°C',
    'depletion_bracket_c': '°C', 'conditional_prefactor_range_s_inv': 's⁻¹',
}

HIDDEN_KEYS = {'identifiability_diagnostics'}
DIAGNOSTICS = {'r_squared', 'rmse_signal', 'residual_rmse', 'normalized_rmse',
               'n_points', 'success', 'message', 'jacobian_condition_number',
               'aic', 'aicc', 'bic'}


def classify(key, result):
    """Return a conservative role, never implying more certainty than the method."""
    method = result['snapshot']['method']
    values = result['values']
    if key in DIAGNOSTICS:
        return 'Diagnostic'
    if key in {'energy_ci95_lower_ev', 'energy_ci95_upper_ev', 'energy_interval',
               'slope_stderr', 'depletion_bracket_c',
               'conditional_prefactor_range_s_inv', 'conditional_signal_scale_range'}:
        return 'Conditional / derived'
    if key in {'beta_k_s', 'assumed_prefactor_s_inv'}:
        return 'Assumed input'
    if method == 'Leading edge':
        if key == 'prefactor_s_inv' and values.get(key) is None:
            return 'Not identified'
        return 'Regression estimate' if key in {'energy_ev', 'slope', 'intercept'} else 'Derived / input'
    if method == 'Redhead':
        return 'Derived estimate' if key in {'energy_ev', 'peak_temperature_c'} else 'Derived / input'
    if method == 'Polanyi–Wigner':
        if key == 'reaction_order_fitted':
            return 'Fit configuration'
        if key == 'reaction_order':
            return 'Fitted' if values.get('reaction_order_fitted') else 'Fixed assumption'
        if key in {'activation_energy_eV', 'prefactor_s_inv', 'signal_scale', 'baseline'}:
            if key == 'baseline' and not result['snapshot'].get('settings', {}).get('fit_baseline', False):
                return 'Fixed assumption'
            if values.get('reaction_order') == 0 and key in {'prefactor_s_inv', 'signal_scale'}:
                return 'Representative; not unique'
            return 'Fitted'
    return 'Reported'


def value_text(value):
    if value is None:
        return 'Not available'
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, float):
        return f'{value:.6g}' if math.isfinite(value) else 'Not available'
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def parameter_rows(result):
    """Rows for the GUI table, retaining input order and all scalar values."""
    rows = []
    for key, value in result['values'].items():
        if key in HIDDEN_KEYS:
            continue
        label = LABELS.get(key, key.replace('_', ' ').capitalize())
        unit = UNITS.get(key, '')
        rows.append((label, value_text(value), unit, classify(key, result)))
    return rows


def scientific_notes(result, is_current):
    snap = result['snapshot']
    method = snap['method']
    state = result.get('status', 'calculated').upper() if is_current else 'STALE'
    lines = [f'{state} — {method}',
             'STALE results show their original submitted settings. Recalculate before using current inputs.'
             if not is_current else 'Results correspond to the submitted settings.', '']
    if method == 'Leading edge':
        lines.append('Apparent slope energy: the regression interval is not a full kinetic-model fit; reported intervals are regression-only.')
    elif method == 'Redhead':
        lines.append('First-order Redhead approximation: energy uses an assumed prefactor, not an optimized prefactor.')
    elif method == 'Polanyi–Wigner':
        lines.append('Single-state fit: normalized coverage and linear heating are assumptions. A fitted reaction order does not establish a mechanism.')
    lines += ['', 'Scientific cautions:']
    lines += [f'• {warning}' for warning in result.get('warnings', [])]
    lines += ['', 'Submitted analysis context:',
              f'Dataset: {snap.get("dataset", "Unknown")}',
              f'Peak: {snap.get("peak", "Unknown")}',
              f'Region (°C): {value_text(snap.get("region"))}',
              'Settings: ' + json.dumps(snap.get('settings', {}), ensure_ascii=False, indent=2, sort_keys=True),
              'Processing: ' + json.dumps(snap.get('processing', {}), ensure_ascii=False, indent=2, sort_keys=True)]
    diagnostics = result.get('values', {}).get('identifiability_diagnostics')
    if diagnostics:
        lines += ['', 'Identifiability diagnostics:', json.dumps(diagnostics, ensure_ascii=False, indent=2, sort_keys=True)]
    return '\n'.join(lines)
