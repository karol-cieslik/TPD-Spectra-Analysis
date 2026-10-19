import importlib.util
from pathlib import Path
import pytest


def _module(filename):
    path = Path(__file__).resolve().parents[1] / "scripts" / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_coverage_is_reproducible_and_accounts_for_each_trial():
    mod = _module("leading_edge_interval_coverage.py")
    first = mod.run_coverage(seed=9, repetitions=8, noise_sigmas=(0.02,))
    second = mod.run_coverage(seed=9, repetitions=8, noise_sigmas=(0.02,))
    assert first == second
    trials, summary = first
    assert len(trials) == 8
    assert summary[0]["valid_trials"] + summary[0]["failed_trials"] == 8
    assert 0 <= summary[0]["observed_coverage"] <= 1


def test_coverage_rejects_invalid_inputs():
    mod = _module("leading_edge_interval_coverage.py")
    with pytest.raises(ValueError):
        mod.run_coverage(repetitions=0)
    with pytest.raises(ValueError):
        mod.run_coverage(noise_sigmas=(-0.1,))


def test_summary_counts_failed_fits_in_denominator():
    mod = _module("export_benchmark_matrix.py")
    rows = [
        dict(order=1, success=True, energy_error_eV=.1, log10_prefactor_error=.2),
        dict(order=1, success=False, energy_error_eV=None, log10_prefactor_error=None),
    ]
    summary = mod.summarize(rows, ("order",))
    assert summary[0]["n_failure"] == 1
    assert summary[0]["convergence_fraction"] == .5
    assert summary[0]["energy_error_eV_rmse"] == pytest.approx(.1)
