"""Numerical checkpoints for documented teaching examples and scientific roles."""

import json
from pathlib import Path

import numpy as np

from tpd_spectra.analysis import leading_edge_fit, redhead_energy
from tpd_spectra.scientific_help import load_help_catalog


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples' / 'beta_collection'


def test_clean_first_order_tutorial_numbers_come_from_bundled_example():
    metadata = json.loads((EXAMPLES / 'first_order_single_peak.json').read_text(encoding='utf-8'))
    data = np.genfromtxt(EXAMPLES / 'first_order_single_peak.csv', names=True, delimiter=',')
    energy = metadata['states'][0]['energy_eV']
    prefactor = metadata['states'][0]['prefactor_s_inv']
    beta = metadata['beta_K_s']
    assert energy == 1.2 and prefactor == 1e13 and beta == 1.0
    assert len(data) == metadata['points'] == 801
    assert metadata['noise']['model'] == 'none'
    assert metadata['states'][0]['order'] == 1
    assert data['Temperature'][np.argmax(data['Signal'])] == 155.0
    redhead = redhead_energy(155.0, prefactor, beta)
    leading = leading_edge_fit(data['Temperature'], data['Signal'], beta, 90.0, 110.0)
    assert abs(redhead / energy - 1) < 0.025
    assert abs(leading.energy_ev / energy - 1) < 0.025
    assert leading.n_points == 41
    assert leading.r_squared > 0.999
    assert np.isnan(leading.prefactor_s_inv)


def test_help_describes_assumptions_and_limits_without_false_certainty():
    topics = {item['id']: item for item in load_help_catalog()['topics']}
    assert topics['prefactor']['role'] == 'method_dependent'
    assert 'fixed' in topics['simultaneous_components']['detail']
    assert topics['baseline_drift']['role'] == 'method_dependent'
    assert 'not unique' in topics['fixed_zero_order']['detail']
    assert 'not Bayesian MCMC' in topics['mc_noise']['caution']
    assert '100' in topics['mc_intervals']['detail']
    assert 'not a Bayesian posterior' in topics['mc_rank_frequency']['detail']
    assert 'not a completed inverse fit' in topics['simulation']['caution']


def test_overlapping_tutorial_truth_is_explicitly_synthetic():
    metadata = json.loads((EXAMPLES / 'three_overlapping_peaks.json').read_text(encoding='utf-8'))
    states = metadata['states']
    assert metadata['synthetic'] is True and metadata['experimental'] is False
    assert metadata['noise']['model'] == 'none'
    assert len(states) == metadata['number_of_states'] == 3
    assert [item['energy_eV'] for item in states] == [1.18, 1.26, 1.34]
    assert [item['initial_normalized_coverage'] for item in states] == [1.0, 0.7, 0.5]
    assert [item['prefactor_s_inv'] for item in states] == [1e13] * 3
