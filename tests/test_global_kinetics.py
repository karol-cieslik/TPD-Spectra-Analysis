import numpy as np
import pytest

from tpd_spectra.kinetics import simulate_tpd, fit_global_polanyi_wigner


def _synthetic_traces(noise_fraction=0.0, seed=12):
    rng = np.random.default_rng(seed)
    traces = []
    for beta in (0.5, 1.5, 4.0):
        temp = np.linspace(80, 400, 121)
        _, rate = simulate_tpd(temp, beta, 1.15, 1e13, 1.0)
        scale = 1000.0 / max(float(np.max(rate)), 1e-30)
        signal = 3.0 + scale * rate
        if noise_fraction:
            signal = signal + rng.normal(0, noise_fraction * np.ptp(signal), size=signal.size)
        traces.append({'temperature_c': temp, 'signal': signal, 'beta_k_s': beta})
    return traces


def test_global_fit_recovers_shared_kinetics_across_heating_rates():
    result, predictions = fit_global_polanyi_wigner(_synthetic_traces(), reaction_order=1.0,
        initial_energy_ev=1.05, initial_prefactor_s_inv=1e13, max_nfev=250)
    assert result.success
    assert result.activation_energy_eV == pytest.approx(1.15, rel=2e-3)
    assert result.prefactor_s_inv == pytest.approx(1e13, rel=5e-2)
    assert len(predictions) == 3
    assert max(result.normalized_rmse_by_trace) < 1e-3
    assert result.heating_rates_K_s == [0.5, 1.5, 4.0]


def test_global_fit_requires_multiple_traces():
    with pytest.raises(ValueError, match='at least two traces'):
        fit_global_polanyi_wigner(_synthetic_traces()[:1])


def test_global_fit_warns_when_heating_rates_are_not_distinct():
    traces = _synthetic_traces()
    for trace in traces:
        trace['beta_k_s'] = 1.5
    result, _ = fit_global_polanyi_wigner(traces, max_nfev=100)
    assert any('same heating rate' in warning for warning in result.warnings)
