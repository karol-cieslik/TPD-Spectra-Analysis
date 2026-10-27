"""Scientific semantics and GUI presentation without modifying the engine."""

from pathlib import Path

from tpd_spectra.result_view import classify, parameter_rows, scientific_notes, value_text
from tpd_spectra.workflow_analysis import calculate
from tpd_spectra.workflow_state import WorkflowProject


DEMO = Path(__file__).resolve().parents[1] / 'examples/synthetic_two_peak_demo.csv'


def _result(method):
    project = WorkflowProject()
    dataset = project.add_dataset(DEMO)
    project.add_region('First peak', 100, 210)
    if method == 'Leading edge':
        project.method_settings(method).update(lower=110, upper=130)
    return calculate(dataset, project.snapshot(method))


def test_redhead_energy_is_derived_and_prefactor_is_assumed():
    result = _result('Redhead')
    assert classify('energy_ev', result) == 'Derived estimate'
    assert classify('assumed_prefactor_s_inv', result) == 'Assumed input'
    assert ('Apparent / estimated energy', value_text(result['values']['energy_ev']),
            'eV', 'Derived estimate') in parameter_rows(result)
    assert 'First-order Redhead approximation' in scientific_notes(result, True)


def test_leading_edge_does_not_report_calibrated_prefactor():
    result = _result('Leading edge')
    assert classify('energy_ev', result) == 'Regression estimate'
    assert result['values']['prefactor_s_inv'] is None
    assert ('Arrhenius prefactor', 'Not available', 's⁻¹', 'Not identified') in parameter_rows(result)
    assert 'regression-only' in scientific_notes(result, True)


def test_zero_order_requires_distinct_representation_and_no_false_ci():
    result = {'snapshot': {'method': 'Polanyi–Wigner', 'settings': {'fit_baseline': False},
                           'region': [100, 210]},
              'values': {'reaction_order': 0., 'reaction_order_fitted': False,
                         'activation_energy_eV': 1.2, 'prefactor_s_inv': 1e13,
                         'signal_scale': 1e-3, 'baseline': 0.,
                         'energy_interval': None, 'identifiability_diagnostics': {'note': 'ill-conditioned'}},
              'warnings': ['Prefactor and scale not individually identified.'],
              'status': 'fitted'}
    assert classify('reaction_order', result) == 'Fixed assumption'
    assert classify('prefactor_s_inv', result) == 'Representative; not unique'
    assert classify('signal_scale', result) == 'Representative; not unique'
    assert classify('baseline', result) == 'Fixed assumption'
    assert all(row[0] != 'Identifiability diagnostics' for row in parameter_rows(result))
    notes = scientific_notes(result, False)
    assert 'STALE' in notes and 'submitted settings' in notes
    assert 'ill-conditioned' in notes
    assert 'not individually identified' in notes


def test_boolean_and_nonfinite_are_human_readable():
    assert value_text(True) == 'Yes'
    assert value_text(False) == 'No'
    assert value_text(float('nan')) == 'Not available'
    assert value_text(None) == 'Not available'


def test_results_screen_contains_separate_views_and_copy_action(root):
    from tpd_spectra.workflow_gui import WorkflowApp

    app = WorkflowApp(root)
    app._load_paths([DEMO])
    app.project.add_region('First peak', 100, 210)
    app.refresh_context()
    result = calculate(app.project.context()[0], app.project.snapshot('Leading edge',
        {**app.project.method_settings('Leading edge'), 'lower': 110, 'upper': 130}))
    app.project.accept_result(result)
    app.method.set('Leading edge')
    app.refresh_method()
    assert [app.result_views.tab(tab, 'text') for tab in app.result_views.tabs()] == [
        'Spectrum & residuals', 'Parameter summary', 'Assumptions & provenance']
    assert len(app.result_table.get_children()) == len(parameter_rows(result))
    assert 'Regression estimate' in [app.result_table.item(i, 'values')[-1]
                                     for i in app.result_table.get_children()]
    app.copy_result_summary()
    assert 'scientific cautions' in root.clipboard_get().lower()
    app.method_values['upper'].set('129')
    assert 'STALE' in app.result_state.get()
    assert 'STALE' in app.result_text.get('1.0', 'end')
