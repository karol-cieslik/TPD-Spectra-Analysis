import numpy as np
import pytest
from scipy.integrate import quad

from tpd_spectra.analysis import K_B_EV

K_B_EV_REFERENCE = 8.617333262145e-5
from tpd_spectra.kinetics import polanyi_wigner_rate, simulate_tpd, fit_polanyi_wigner


def test_first_order_coverage_matches_independent_quadrature():
    temp_c = np.linspace(80, 260, 61)
    beta, energy, nu, theta0 = 1.4, 1.05, 2e12, 0.83
    coverage, rate = simulate_tpd(temp_c, beta, energy, nu, 1, theta0)
    assert K_B_EV == pytest.approx(K_B_EV_REFERENCE, rel=1e-10)
    temp_k = temp_c + 273.15
    for i in (5, 20, 40, 60):
        integral, _ = quad(lambda t: np.exp(-energy / (K_B_EV_REFERENCE*t)), temp_k[0], temp_k[i], epsabs=1e-13, epsrel=1e-11)
        expected = theta0 * np.exp(-(nu / beta) * integral)
        assert coverage[i] == pytest.approx(expected, rel=4e-4, abs=2e-7)
    assert np.allclose(rate, polanyi_wigner_rate(temp_k, coverage, energy, nu, 1))


def test_simulation_coverage_is_bounded_and_monotonic():
    coverage, rate = simulate_tpd(np.linspace(80, 350, 300), 1.0, 1.1, 1e13, 1, 0.7)
    assert np.all(coverage >= 0)
    assert np.all(coverage <= 0.7)
    assert np.all(np.diff(coverage) <= 1e-9)
    assert np.all(rate >= 0)


def test_rate_rejects_nonfinite_coverage():
    with pytest.raises(ValueError, match="coverage must be finite"):
        polanyi_wigner_rate([500], [np.nan], 1, 1e13, 1)


def test_fit_rejects_constant_signal():
    temp = np.linspace(100, 250, 30)
    with pytest.raises(ValueError, match="nonzero dynamic range"):
        fit_polanyi_wigner(temp, np.ones_like(temp), 1.0)


def test_fit_rejects_invalid_evaluation_limit():
    temp = np.linspace(100, 250, 30)
    signal = np.linspace(1, 5, 30)
    with pytest.raises(ValueError, match="max_nfev"):
        fit_polanyi_wigner(temp, signal, 1.0, max_nfev=0)


def test_fit_preserves_original_shape_with_duplicate_temperatures():
    temp = np.linspace(80, 330, 80)
    temp[20] = temp[19]
    # Restore non-decreasing sequence while retaining a duplicate sample.
    temp[21:] += temp[19] - temp[20]
    _, rate = simulate_tpd(np.unique(temp), 1.0, 1.0, 1e13, 1)
    unique_temp, inverse = np.unique(temp, return_inverse=True)
    signal = (3 + 1e4 * rate)[inverse]
    result, prediction = fit_polanyi_wigner(temp, signal, 1.0, reaction_order=1,
        initial_energy_ev=1.0, initial_prefactor_s_inv=1e13, max_nfev=50)
    assert result.success
    assert prediction.shape == signal.shape
