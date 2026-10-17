import math
import numpy as np
import pytest
from tpd_spectra.analysis import (K_B_EV, leading_edge_fit, redhead_energy,
                                  smooth_signal, clean_temperature, heating_rate)


def test_redhead_uses_kelvin_in_logarithm():
    t_c, nu, beta = 250.0, 1e13, 1.0
    t_k = t_c + 273.15
    expected = K_B_EV * t_k * (math.log(nu * t_k / beta) - 3.64)
    assert redhead_energy(t_c, nu, beta) == pytest.approx(expected, rel=1e-12)


def test_leading_edge_recovers_known_slope_and_uses_same_mask():
    temp = np.linspace(100, 220, 121)
    slope, intercept = -5000.0, 12.0
    signal = np.exp(intercept + slope / (temp + 273.15))
    fit = leading_edge_fit(temp, signal, beta_k_s=1.2, lower_c=130, upper_c=170)
    assert fit.slope == pytest.approx(slope, rel=1e-10)
    assert fit.energy_ev == pytest.approx(-slope*K_B_EV, rel=1e-10)
    assert fit.n_points == 41
    assert fit.r_squared == pytest.approx(1.0, abs=1e-10)


def test_leading_edge_rejects_misaligned_arrays():
    with pytest.raises(ValueError, match='identical shapes'):
        leading_edge_fit([130, 140], [1], 1, 130, 150)


@pytest.mark.parametrize('method', ['mean', 'median'])
def test_smoothing_preserves_length_and_handles_edges(method):
    values = np.array([1., 2., 3., 100.])
    result = smooth_signal(values, window=3, method=method)
    assert len(result) == len(values)
    assert np.all(np.isfinite(result))
    assert result[0] > 0


def test_smoothing_window_validation():
    with pytest.raises(ValueError):
        smooth_signal([1, 2], 0)


def test_clean_temperature_handles_last_point():
    raw = np.array([100., 100.2, 100.4, 120., 100.8])
    clean = clean_temperature(raw)
    assert len(clean) == len(raw)
    assert np.all(np.isfinite(clean))
    assert clean[3] != 120.


def test_heating_rate_linear_synthetic_data():
    t = np.linspace(0, 10, 101)
    temp = 100 + 30*t
    beta, r2, slope = heating_rate(t, temp, lower_c=100, upper_c=500, max_time_min=10)
    assert beta == pytest.approx(0.5)
    assert slope == pytest.approx(30)
    assert r2 == pytest.approx(1.0)

def test_all_included_example_csv_files_import():
    from pathlib import Path
    from tpd_spectra.analysis import load_spectrum
    files = sorted(Path('input').glob('*.csv'))
    assert len(files) == 9
    for path in files:
        spectrum = load_spectrum(path)
        assert len(spectrum.time_min) > 100
        assert spectrum.time_min.shape == spectrum.signal.shape == spectrum.temperature_clean_c.shape
        assert np.all(np.isfinite(spectrum.temperature_clean_c))


def test_leading_edge_reports_regression_uncertainty_and_residuals():
    rng = np.random.default_rng(42)
    temp = np.linspace(120, 190, 100)
    x = 1.0 / (temp + 273.15)
    signal = np.exp(10.0 - 4200.0 * x + rng.normal(0, 0.015, size=x.size))
    fit = leading_edge_fit(temp, signal, beta_k_s=1.0, lower_c=130, upper_c=180)
    assert np.isfinite(fit.residual_rmse)
    assert fit.residual_rmse > 0
    assert fit.slope_stderr > 0
    assert fit.energy_ci95_lower_ev < fit.energy_ev < fit.energy_ci95_upper_ev


def test_quality_diagnostics_are_screening_metrics_not_correction():
    from tpd_spectra.analysis import spectrum_quality_diagnostics
    signal = np.array([-0.2, 0.0, 1.0, 3.0, 8.0])
    temp = np.arange(5.0) + 100
    before = signal.copy()
    result = spectrum_quality_diagnostics(signal, temp, corrected_points=1)
    assert result['signal_negative_fraction'] == pytest.approx(0.2)
    assert result['temperature_corrected_fraction'] == pytest.approx(0.2)
    assert np.array_equal(signal, before)


def test_analysis_reports_prefactor_sensitivity_and_warnings():
    from pathlib import Path
    from tpd_spectra.analysis import analyze_file
    path = sorted(Path('input').glob('*.csv'))[1]
    result = analyze_file(path)
    assert result['redhead_energy_prefactor_0.1x_eV'] < result['redhead_energy_eV']
    assert result['redhead_energy_prefactor_10x_eV'] > result['redhead_energy_eV']
    assert result['redhead_energy_change_for_prefactor_decade_eV'] > 0
    assert 'diagnostic_warnings' in result
    assert 'leading_edge_energy_CI95_lower_eV_regression_only' in result


def test_cli_exports_diagnostic_artifacts(tmp_path):
    from pathlib import Path
    from tpd_spectra.cli import main
    source = sorted(Path('input').glob('*.csv'))[1]
    out = tmp_path / 'results'
    assert main([str(source), '--output', str(out)]) == 0
    assert (out / 'all_desorption_parameters.csv').is_file()
    assert (out / 'all_tds_spectra.png').is_file()
    assert list((out / 'diagnostics').glob('*_diagnostics.png'))
    import pandas as pd
    result = pd.read_csv(out / 'all_desorption_parameters.csv')
    assert 'redhead_energy_prefactor_10x_eV' in result.columns
    assert 'diagnostic_warnings' in result.columns


def test_cli_saves_reproducible_project_manifest_and_config(tmp_path):
    import json
    from pathlib import Path
    from tpd_spectra.cli import main
    source = sorted(Path('input').glob('*.csv'))[1]
    out = tmp_path / 'project-output'
    config = tmp_path / 'saved-config.json'
    assert main([str(source), '--output', str(out), '--window', '7',
                 '--save-config', str(config)]) == 0
    manifest = json.loads((out / 'analysis_project.json').read_text(encoding='utf-8'))
    saved_config = json.loads(config.read_text(encoding='utf-8'))
    assert manifest['software_version'] == '0.9.1'
    assert manifest['parameters']['window'] == 7
    assert len(manifest['inputs_processed']) == 1
    assert len(manifest['inputs_processed'][0]['sha256']) == 64
    assert 'batch_summary.csv' in manifest['outputs']
    assert saved_config['window'] == 7
    assert (out / 'batch_summary.csv').is_file()


def test_cli_config_and_explicit_cli_override(tmp_path):
    import json
    from pathlib import Path
    from tpd_spectra.cli import main
    source = sorted(Path('input').glob('*.csv'))[1]
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'window': 4, 'filter': 'mean'}), encoding='utf-8')
    out = tmp_path / 'configured-output'
    assert main([str(source), '--config', str(config), '--window', '6',
                 '--output', str(out)]) == 0
    import json as json_module
    manifest = json_module.loads((out / 'analysis_project.json').read_text(encoding='utf-8'))
    assert manifest['parameters']['window'] == 6
    assert manifest['parameters']['filter'] == 'mean'
