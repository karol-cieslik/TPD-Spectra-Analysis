"""Scientific Help is packaged, deterministic, offline and read-only."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from tpd_spectra.scientific_help import CATALOG_RESOURCE, load_help_catalog, topic_heading


DEMO = Path(__file__).resolve().parents[1] / 'examples/synthetic_two_peak_demo.csv'


def test_catalog_contains_all_40_scientific_topics():
    catalog = load_help_catalog()
    topics = catalog['topics']
    assert len(topics) == 40
    ids = [topic['id'] for topic in topics]
    assert len(set(ids)) == len(ids)
    assert {'mc_seed', 'mc_replicates', 'heating_rate', 'reaction_order',
            'prefactor', 'fixed_zero_order', 'simultaneous_components',
            'identifiability', 'stale_result', 'feedback_privacy'} <= set(ids)
    assert len(set(topic['group'] for topic in topics)) == 6
    assert CATALOG_RESOURCE == 'docs/beta/SCIENTIFIC_HELP_TOPICS.json'
    seed = next(item for item in topics if item['id'] == 'mc_seed')
    assert 'random' in (seed['title'] + ' ' + seed['detail']).lower()
    assert 'reproduc' in (seed['short'] + ' ' + seed['detail']).lower()
    assert 'not a fit parameter' in seed['caution']


def test_catalog_rejects_duplicate_and_incomplete_topics(tmp_path):
    catalog = load_help_catalog()
    bad = deepcopy(catalog)
    bad['topics'].append(deepcopy(bad['topics'][0]))
    path = tmp_path / 'duplicate.json'
    path.write_text(json.dumps(bad), encoding='utf-8')
    with pytest.raises(ValueError, match='Duplicate'):
        load_help_catalog(path)
    bad = deepcopy(catalog)
    bad['topics'][0].pop('caution')
    path.write_text(json.dumps(bad), encoding='utf-8')
    with pytest.raises(ValueError, match='missing required fields'):
        load_help_catalog(path)


def test_scientific_help_title_and_optional_drift_do_not_imply_missing_or_fitted_values():
    topics = {topic['id']: topic for topic in load_help_catalog()['topics']}
    assert topic_heading(topics['mc_seed']) == 'Random seed'
    assert topic_heading(topics['activation_energy']) == 'Activation (desorption) energy  (E)'
    assert topics['baseline_drift']['role'] == 'method_dependent'
    assert 'only when' in topics['baseline_drift']['role_notes']


def test_help_browser_is_searchable_reusable_and_read_only(root):
    from tpd_spectra.workflow_gui import WorkflowApp

    app = WorkflowApp(root)
    app._load_paths([DEMO])
    before = deepcopy(app.project.snapshot('Polanyi–Wigner'))
    dialog = app.open_scientific_help('mc_seed')
    root.update()
    assert dialog is not None
    assert dialog._current_id() == 'mc_seed'
    assert '42' in dialog.detail.get('1.0', 'end')
    assert dialog.count.get() == '40 / 40 topics'
    dialog.query.set('energy')
    root.update()
    assert ' / 40 topics' in dialog.count.get()
    assert dialog.count.get() != '40 / 40 topics'
    assert app.open_scientific_help('prefactor') is dialog
    assert dialog._current_id() == 'prefactor'
    assert dialog.query.get() == ''
    dialog.query.set('not-an-existing-scientific-topic')
    assert dialog.count.get() == '0 / 40 topics'
    assert 'No matching topics' in dialog.detail.get('1.0', 'end')
    dialog.select_topic('mc_seed')
    assert dialog._current_id() == 'mc_seed'
    assert app.project.snapshot('Polanyi–Wigner') == before
    assert app.job_busy is False
    dialog.close()
    assert app.scientific_help_dialog is None
