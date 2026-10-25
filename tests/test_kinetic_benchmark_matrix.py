import importlib.util
from pathlib import Path

import pytest


def _load():
    path = Path(__file__).resolve().parents[1] / "scripts" / "kinetic_benchmark_matrix.py"
    spec = importlib.util.spec_from_file_location("kinetic_benchmark_matrix", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matrix_smoke_and_determinism():
    module = _load()
    kwargs = dict(seed=43, orders=(1.0,), heating_rates=(1.0,),
                  noise_levels=(0.0,), replicates=1, max_nfev=80)
    a = module.benchmark_matrix(**kwargs)
    b = module.benchmark_matrix(**kwargs)
    assert a == b
    assert len(a) == 1
    assert a[0]["scenario"] == "single_state"
    assert a[0]["success"]


def test_matrix_rejects_invalid_conditions():
    with pytest.raises(ValueError):
        _load().benchmark_matrix(heating_rates=(-1,))


def test_overlap_smoke():
    rows = _load().benchmark_overlap(separations=(0.2,), noise_fraction=0, max_nfev=200)
    assert len(rows) == 1
    assert rows[0]["scenario"] == "two_state"
    assert rows[0]["true_energy2_eV"] == pytest.approx(1.3)


def test_zero_order_benchmark_does_not_score_arbitrary_prefactor():
    row = _load().benchmark_matrix(orders=(0.,), heating_rates=(1.,),
        noise_levels=(0.,), replicates=1)[0]
    assert row['success']
    assert row['log10_prefactor_error'] is None
    lo, hi = row['conditional_prefactor_range_s_inv']
    assert lo <= row['true_prefactor_s_inv'] <= hi
