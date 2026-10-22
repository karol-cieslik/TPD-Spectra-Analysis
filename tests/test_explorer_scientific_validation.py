"""Scientific sanity checks using generated Polanyi–Wigner reference traces.

These tests are intentionally independent of private historical instrument data.
They assess physics and recovery; they do not prove universal classification.
"""
import numpy as np
import pytest

from tpd_spectra.kinetics import simulate_tpd, fit_polanyi_wigner
from tpd_spectra.kinetics_explorer import compare_desorption_orders


@pytest.mark.parametrize("n", [0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
def test_integrated_desorption_never_exceeds_initial_coverage(n):
    temperatures = np.linspace(50.0, 420.0, 200)
    theta, r = simulate_tpd(temperatures, 1.0, 1.0, 1e12, n)
    assert theta.shape == r.shape == temperatures.shape
    assert np.all(theta >= 0)
    assert np.all(theta <= 1.0 + 1e-12)
    assert np.all(np.diff(theta) <= 1e-7)
    assert np.all(np.isfinite(r)) and np.all(r >= 0)


def test_first_order_parameter_recovery_with_correct_seed():
    temperature = np.linspace(60, 340, 141)
    true_energy = 1.15
    true_nu = 1e12
    _, r = simulate_tpd(temperature, 1.0, true_energy, true_nu, 1.0)
    result, prediction = fit_polanyi_wigner(
        temperature, 1.5 + r * 2e4, 1.0,
        reaction_order=1.0, initial_energy_ev=true_energy,
        initial_prefactor_s_inv=true_nu, max_nfev=150)
    assert result.success
    assert result.activation_energy_eV == pytest.approx(true_energy, rel=0.02)
    assert result.prefactor_s_inv == pytest.approx(true_nu, rel=0.15)
    assert result.normalized_rmse < 0.01
    assert np.all(np.isfinite(prediction))


def test_model_comparison_reports_all_candidates():
    temperature = np.linspace(60, 340, 91)
    _, r = simulate_tpd(temperature, 1.0, 1.1, 1e12, 1.0)
    candidates = compare_desorption_orders(
        temperature, 2 + 1e4 * r, 1.0, max_nfev=80, multistart=False,
        initial_energy_ev=1.1, initial_prefactor_s_inv=1e12)
    assert {c.name for c in candidates} == {"zero", "first", "second", "fractional"}
    assert all(c.starts_attempted == 1 for c in candidates)
    assert all(c.error or c.fit for c in candidates)
