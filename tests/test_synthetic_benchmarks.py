"""Deterministic kinetic simulation benchmarks using known input parameters.

These tests check numerical invariants and noise reproducibility. They do
not validate experimental mechanisms or calibrate confidence intervals.
"""
import numpy as np
import pytest
from scipy.integrate import trapezoid

from tpd_spectra.kinetics import simulate_tpd, fit_polanyi_wigner


@pytest.mark.parametrize("order", [0.0, 1.0, 2.0, 1.5])
def test_simulated_desorption_obeys_coverage_balance(order):
    temperature = np.linspace(80, 420, 3401)
    beta = 1.0
    theta, rate = simulate_tpd(temperature, beta, 1.1, 1e13, order)
    assert np.all(np.isfinite(rate))
    assert np.all(rate >= 0)
    assert np.all(np.diff(theta) <= 1e-8)
    assert theta.min() >= 0
    # Trapezoidal quadrature converges toward the coverage decrease.
    released = trapezoid(rate, temperature) / beta
    assert released == pytest.approx(theta[0] - theta[-1], abs=0.02)


def test_synthetic_noise_is_repeatable_and_fit_is_physical():
    temperature = np.linspace(80, 350, 181)
    _, rate = simulate_tpd(temperature, 1.0, 1.2, 1e13, 1.0)
    rng = np.random.default_rng(20261019)
    noise = rng.normal(0.0, 0.003 * np.max(rate), size=rate.size)
    signal = 3.0 + 1e5 * (rate + noise)
    result, predicted = fit_polanyi_wigner(
        temperature, signal, 1.0, reaction_order=1.0,
        initial_energy_ev=1.2, initial_prefactor_s_inv=1e13,
        max_nfev=120,
    )
    assert result.success
    assert predicted.shape == signal.shape
    assert np.all(np.isfinite(predicted))
    assert result.activation_energy_eV > 0
    assert result.prefactor_s_inv > 0
    assert result.normalized_rmse < 0.05
