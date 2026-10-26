"""Detector effects belong to example observations, never the kinetic engine."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from scripts.generate_demo import generate, VARIANTS, SEED
from scripts.generate_beta_examples import add_observation_effects
from tpd_spectra.analysis import load_spectrum

EXAMPLES=Path(__file__).resolve().parents[1]/'examples'


def test_demo_generation_is_byte_reproducible_and_default_is_moderate(tmp_path):
    first,second=tmp_path/'first',tmp_path/'second'
    generate(first)
    generate(second)
    assert {p.name for p in first.iterdir()}=={p.name for p in second.iterdir()}
    for path in first.iterdir():
        assert path.read_bytes()==(second/path.name).read_bytes()
    assert (first/'synthetic_two_peak_demo.csv').read_bytes()==(first/'synthetic_two_peak_demo_moderate_noise.csv').read_bytes()


@pytest.mark.parametrize('variant',VARIANTS)
def test_shipped_demo_metadata_reconstructs_detector_noise_and_baseline(variant):
    stem='synthetic_two_peak_demo_'+variant
    meta=json.loads((EXAMPLES/(stem+'.json')).read_text(encoding='utf-8'))
    clean=load_spectrum(EXAMPLES/meta['clean_reference_file'])
    observed=load_spectrum(EXAMPLES/(stem+'.csv'))
    sigma=meta['noise']['sigma_signal_units']
    baseline=meta['baseline']
    expected=clean.signal+np.random.default_rng(meta['random_seed']).normal(0,sigma,len(clean.signal))
    expected+=baseline['offset_signal_units']+baseline['slope_signal_units_per_K']*(clean.temperature_clean_c-baseline['reference_temperature_c'])
    # Both the clean and observed CSVs are rounded to %.12e on export.
    np.testing.assert_allclose(observed.signal,expected,rtol=0,atol=1e-12*clean.signal.max())
    assert meta['random_seed']==SEED
    assert sigma==pytest.approx(meta['noise_fraction_of_clean_maximum']*clean.signal.max(),rel=1e-12,abs=1e-18)
    assert hashlib.sha256((EXAMPLES/(stem+'.csv')).read_bytes()).hexdigest()==meta['csv_sha256']
    assert hashlib.sha256((EXAMPLES/meta['clean_reference_file']).read_bytes()).hexdigest()==meta['clean_reference_sha256']
    assert observed.points_temperature_corrected==0


def test_observation_helper_preserves_clean_input_and_does_not_clip_noise():
    clean=np.array([0.,1.,0.,0.])
    original=clean.copy()
    temperature=np.arange(len(clean),dtype=float)+70
    observed,noise,baseline=add_observation_effects(clean,temperature,seed=20261026,noise_fraction=.05)
    np.testing.assert_array_equal(clean,original)
    expected=clean+np.random.default_rng(20261026).normal(0,.05,len(clean))
    np.testing.assert_array_equal(observed,expected)
    assert (observed<0).any()
    assert noise['model']=='iid Gaussian'
    assert baseline['offset_signal_units']==baseline['slope_signal_units_per_K']==0.


def test_noisy_default_keeps_known_clean_truth_and_theoretical_reference():
    clean=load_spectrum(EXAMPLES/'synthetic_two_peak_demo_clean.csv')
    observed=load_spectrum(EXAMPLES/'synthetic_two_peak_demo.csv')
    meta=json.loads((EXAMPLES/'synthetic_two_peak_demo.json').read_text())
    assert meta['noise_fraction_of_clean_maximum']==.02
    assert meta['observational_variant']=='moderate_noise'
    assert [state['energy_eV'] for state in meta['populations']]==[1.25,1.55]
    assert not np.array_equal(clean.signal,observed.signal)
    assert np.std(observed.signal-clean.signal)/clean.signal.max()==pytest.approx(.02,rel=.1)
