import numpy as np
import pytest

from tpd_spectra.bootstrap import bootstrap_kinetic_parameters
from tpd_spectra.kinetics import simulate_tpd


def _synthetic():
    temperature = np.linspace(90, 345, 101)
    _, rate = simulate_tpd(temperature, 1.0, 1.2, 1e13, 1.0)
    signal = 4.0 + 1e5 * rate
    rng = np.random.default_rng(222)
    signal += rng.normal(0, max(np.max(signal)-4, 1e-12)*0.003, len(signal))
    return temperature, signal


def test_bootstrap_reports_all_trials_and_is_seed_reproducible():
    temp, signal = _synthetic()
    kwargs = dict(reaction_order=1.0, n_resamples=3, seed=7,
                  initial_energy_ev=1.2, initial_prefactor_s_inv=1e13,
                  max_nfev=70)
    first = bootstrap_kinetic_parameters(temp, signal, 1.0, **kwargs)
    second = bootstrap_kinetic_parameters(temp, signal, 1.0, **kwargs)
    assert first.as_dict() == second.as_dict()
    assert first.requested == first.successful + first.failed == 3
    assert not first.valid
    assert first.energy_ci95_eV is None
    assert first.prefactor_ci95_s_inv is None
    assert any("Fewer than 20" in warning for warning in first.warnings)


def test_bootstrap_rejects_invalid_inputs():
    temp, signal = _synthetic()
    with pytest.raises(ValueError, match="n_resamples"):
        bootstrap_kinetic_parameters(temp, signal, 1.0, n_resamples=1)
    with pytest.raises(ValueError, match="strictly increasing"):
        bootstrap_kinetic_parameters(temp[::-1], signal[::-1], 1.0)
    with pytest.raises(ValueError, match="minimum_success_fraction"):
        bootstrap_kinetic_parameters(temp, signal, 1.0, minimum_success_fraction=0.0)
