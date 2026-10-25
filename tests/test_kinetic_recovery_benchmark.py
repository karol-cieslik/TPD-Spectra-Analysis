import importlib.util
from pathlib import Path

import pytest


def _benchmark():
    path = Path(__file__).resolve().parents[1] / "scripts" / "kinetic_recovery_benchmark.py"
    spec = importlib.util.spec_from_file_location("kinetic_benchmark", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_benchmark_is_deterministic_and_reports_failures():
    benchmark = _benchmark()
    rows1, summary1 = benchmark.run_benchmark(seed=42, replicates=1, noise_levels=(0.0,), max_nfev=80)
    rows2, summary2 = benchmark.run_benchmark(seed=42, replicates=1, noise_levels=(0.0,), max_nfev=80)
    assert rows1 == rows2
    assert summary1 == summary2
    assert summary1[0]["total_trials"] == 1
    assert summary1[0]["successful_trials"] + summary1[0]["failed_trials"] == 1
    assert rows1[0]["true_energy_eV"] == pytest.approx(1.2)


def test_invalid_benchmark_configuration_is_rejected():
    benchmark = _benchmark()
    with pytest.raises(ValueError):
        benchmark.run_benchmark(replicates=0)
    with pytest.raises(ValueError):
        benchmark.run_benchmark(noise_levels=(-0.01,))
