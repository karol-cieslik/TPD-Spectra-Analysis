"""Basic tests for the phase-one Desorption Kinetics Explorer engine."""
import numpy as np
import pytest

from tpd_spectra.kinetics import simulate_tpd
from tpd_spectra.kinetics_explorer import compare_desorption_orders


def test_models_fit_and_rank_synthetic_first_order():
    temp = np.linspace(80, 240, 65)
    _, rate = simulate_tpd(temp, 1.0, 0.9, 1e10, 1.0)
    result = compare_desorption_orders(temp, rate, 1.0, max_nfev=75)
    assert {x.name for x in result} == {"zero", "first", "second", "fractional"}
    assert any(x.error is None for x in result)
    valid = [x for x in result if x.error is None]
    assert np.isclose(sum(x.akaike_weight for x in valid), 1.0)
    assert valid[0].delta_aicc == pytest.approx(0.0)


@pytest.mark.parametrize("order", [0.0, 1.0, 2.0, 0.5, 1.5])
def test_simulator_produces_finite_spectra(order):
    temp = np.linspace(60, 300, 90)
    coverage, rate = simulate_tpd(temp, 1.0, 0.85, 1e10, order)
    assert np.all(np.isfinite(coverage))
    assert np.all(rate >= 0)


def test_rejects_duplicate_models():
    temp = np.linspace(70, 260, 30)
    with pytest.raises(ValueError, match="distinct"):
        compare_desorption_orders(temp, np.ones_like(temp), 1.0,
                                  orders=("first", "first"))


def test_rejects_invalid_ramp():
    temp = np.linspace(70, 260, 30)[::-1]
    with pytest.raises(ValueError, match="strictly increasing"):
        compare_desorption_orders(temp, np.ones_like(temp), 1.0)


def test_multistart_accounting_and_model_selection():
    temp = np.linspace(70, 320, 110)
    _, rate = simulate_tpd(temp, 1.0, 1.0, 1e12, 1.0)
    result = compare_desorption_orders(
        temp, 3.0 + 2e4 * rate, 1.0, orders=("first",),
        max_nfev=100, multistart=True,
    )
    assert len(result) == 1
    assert result[0].starts_attempted == 3
    assert 0 <= result[0].starts_converged <= 3
    if result[0].error is None:
        assert result[0].akaike_weight == pytest.approx(1.0)


def test_multistart_can_be_disabled():
    temp = np.linspace(70, 320, 75)
    _, rate = simulate_tpd(temp, 1.0, 1.0, 1e12, 1.0)
    result = compare_desorption_orders(
        temp, rate, 1.0, orders=("first",),
        max_nfev=50, multistart=False,
    )
    assert result[0].starts_attempted == 1


@pytest.mark.parametrize("bad_energy,bad_prefactor", [
    (0, 1e13), (1.0, 0), (float("nan"), 1e13),
])
def test_invalid_initial_guess_is_rejected(bad_energy, bad_prefactor):
    temp = np.linspace(100, 300, 30)
    with pytest.raises(ValueError):
        compare_desorption_orders(
            temp, np.ones_like(temp), 1.0,
            initial_energy_ev=bad_energy,
            initial_prefactor_s_inv=bad_prefactor,
        )


def test_zero_order_depletion_has_no_persistent_post_exhaustion_rate():
    temp = np.linspace(20, 600, 581)
    coverage, rate = simulate_tpd(temp, 1.0, 0.9, 1e13, 0.0)
    assert np.all(coverage >= 0)
    assert np.all(coverage <= 1)
    assert np.all(np.diff(coverage) <= 1e-8)
    depleted = np.flatnonzero(coverage < 1e-8)
    assert depleted.size > 0
    assert np.all(rate[depleted] == 0.0)


@pytest.mark.parametrize("order", [0.0, 1.0, 2.0, 0.5, 1.5, 2.5])
def test_known_order_generates_physically_finite_rate(order):
    temp = np.linspace(60, 400, 171)
    theta, rate = simulate_tpd(temp, 1.0, 1.1, 1e12, order)
    assert np.all(np.isfinite(rate))
    assert np.all(rate >= 0)
    assert theta[0] == pytest.approx(1.0)
    assert theta[-1] <= theta[0]


def test_model_comparison_is_deterministic_given_same_input():
    temp = np.linspace(70, 330, 91)
    _, rate = simulate_tpd(temp, 1.0, 1.05, 1e12, 1.0)
    a = compare_desorption_orders(temp, rate, 1.0, orders=("first",), max_nfev=75, multistart=False)
    b = compare_desorption_orders(temp, rate, 1.0, orders=("first",), max_nfev=75, multistart=False)
    assert a[0].error == b[0].error
    if a[0].error is None:
        assert a[0].fit.aicc == pytest.approx(b[0].fit.aicc, abs=1e-8)
