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
