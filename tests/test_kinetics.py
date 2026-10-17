import numpy as np
import pytest

from tpd_spectra.kinetics import polanyi_wigner_rate, simulate_tpd, fit_polanyi_wigner


def test_polanyi_wigner_rate_has_expected_first_order_dependence():
    temp = np.array([500.0, 500.0])
    theta = np.array([1.0, 0.5])
    rates = polanyi_wigner_rate(temp, theta, 1.0, 1e13, 1.0)
    assert rates[1] == pytest.approx(rates[0] * 0.5)


def test_zero_order_rate_stops_when_coverage_is_exhausted():
    rates = polanyi_wigner_rate([500, 500], [0, 1], 1.0, 1e13, 0)
    assert rates[0] == 0
    assert rates[1] > 0


def test_simulation_validates_monotonic_temperature():
    with pytest.raises(ValueError, match='strictly increasing'):
        simulate_tpd([100, 101, 100.5], 1.0, 1.0, 1e13, 1)


def test_synthetic_first_order_full_trace_fit_recovers_parameters():
    temp = np.linspace(80, 350, 271)
    _, rate = simulate_tpd(temp, 1.0, 1.2, 1e13, 1.0)
    signal = 4.0 + 1e5 * rate
    result, predicted = fit_polanyi_wigner(
        temp, signal, 1.0, reaction_order=1,
        initial_energy_ev=1.1, initial_prefactor_s_inv=1e13, max_nfev=100)
    assert result.success
    assert result.activation_energy_eV == pytest.approx(1.2, rel=1e-4)
    assert result.prefactor_s_inv == pytest.approx(1e13, rel=1e-3)
    assert result.baseline == pytest.approx(4.0, abs=1e-3)
    assert result.r_squared > 0.999999
    assert np.isfinite(result.aicc)
    assert result.jacobian_condition_number >= 1.0
    assert predicted.shape == signal.shape


def test_fit_rejects_misaligned_or_short_data():
    with pytest.raises(ValueError, match='matching 1D'):
        fit_polanyi_wigner([100, 101], [1], 1.0)


def test_two_state_fit_recovers_synthetic_overlapping_states_and_reports_identifiability():
    from tpd_spectra.kinetics import fit_two_state_polanyi_wigner
    temp = np.linspace(80, 420, 171)
    _, rate1 = simulate_tpd(temp, 1.0, 1.0, 1e13, 1.0)
    _, rate2 = simulate_tpd(temp, 1.0, 1.35, 1e13, 1.0)
    signal = 2.0 + 8e4 * rate1 + 4e4 * rate2
    result, predicted = fit_two_state_polanyi_wigner(
        temp, signal, 1.0, reaction_order=1.0,
        initial_energies_ev=(0.8, 1.4), initial_prefactor_s_inv=1e13, max_nfev=250)
    assert result.success
    assert result.n_states == 2
    assert result.aicc < float('inf')
    assert result.activation_energies_eV[0] < result.activation_energies_eV[1]
    assert predicted.shape == signal.shape
    assert result.normalized_rmse < 0.02


def test_two_state_fit_rejects_invalid_initial_energy_order():
    from tpd_spectra.kinetics import fit_two_state_polanyi_wigner
    with pytest.raises(ValueError, match='increasing energies'):
        fit_two_state_polanyi_wigner(np.linspace(100, 200, 25), np.arange(25), 1.0,
                                     initial_energies_ev=(1.5, 1.0))
