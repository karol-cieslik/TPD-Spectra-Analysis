"""Uncertainty engine regression tests, using small replicate counts for CI."""
import numpy as np
import pytest

from tpd_spectra.kinetics import simulate_tpd
from tpd_spectra.kinetics_uncertainty import run_kinetics_monte_carlo


def _trace():
    t = np.linspace(80.0, 340.0, 65)
    _, rate = simulate_tpd(t, 1.0, 1.1, 1e12, 1.0)
    rng = np.random.default_rng(12)
    y = 2.0 + 1e4 * rate + rng.normal(0, max(np.max(rate) * 1e4, 1e-6) * 0.015, t.size)
    return t, y


def test_reproducible_mc_counts_and_intervals():
    t, y = _trace()
    kwargs = dict(orders=("first",), replicates=3, seed=42,
                  max_nfev=50, multistart=False)
    a = run_kinetics_monte_carlo(t, y, 1.0, **kwargs)
    b = run_kinetics_monte_carlo(t, y, 1.0, **kwargs)
    assert a.replicates_completed == 3
    assert a.winning_counts == b.winning_counts
    assert a.failed_rankings == b.failed_rankings
    assert a.parameter_intervals == b.parameter_intervals
    assert sum(a.winning_counts.values()) + a.failed_rankings == 3


def test_cancellation_counts_only_completed_replicates():
    t, y = _trace()
    result = run_kinetics_monte_carlo(
        t, y, 1.0, orders=("first",), replicates=500,
        max_nfev=50, cancelled=lambda: True,
    )
    assert result.cancelled
    assert result.replicates_completed == 0


@pytest.mark.parametrize("runs", [0, -1])
def test_rejects_invalid_mc_run_count(runs):
    t, y = _trace()
    with pytest.raises(ValueError, match="replicates"):
        run_kinetics_monte_carlo(t, y, 1.0, replicates=runs)
