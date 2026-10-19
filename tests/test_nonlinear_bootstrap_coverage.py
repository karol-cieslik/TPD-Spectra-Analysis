import importlib.util
from pathlib import Path
import pytest


def _coverage_module():
    p = Path(__file__).resolve().parents[1] / "scripts" / "nonlinear_bootstrap_coverage.py"
    spec = importlib.util.spec_from_file_location("nonlinear_coverage", p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_coverage_accounts_for_withheld_intervals_and_is_reproducible():
    module = _coverage_module()
    kwargs = dict(seed=11, repetitions=2, resamples=2, noise_fractions=(0.003,),
                  max_nfev=60, n_points=61)
    trials_a, summaries_a = module.evaluate_coverage(**kwargs)
    trials_b, summaries_b = module.evaluate_coverage(**kwargs)
    assert trials_a == trials_b
    assert summaries_a == summaries_b
    summary = summaries_a[0]
    assert summary["total_trials"] == 2
    assert summary["intervals_issued"] + summary["intervals_withheld"] == 2
    assert summary["intervals_issued"] == 0  # Fewer than 20 refits: mandatory abstention.
    assert summary["conditional_energy_coverage"] is None
    assert summary["energy_covered_out_of_all"] == 0


@pytest.mark.parametrize("options", [
    {"repetitions": 0}, {"resamples": 1}, {"noise_fractions": (-0.1,)},
    {"n_points": 5}, {"max_nfev": 0},
])
def test_invalid_coverage_design(options):
    with pytest.raises(ValueError):
        _coverage_module().evaluate_coverage(**options)
