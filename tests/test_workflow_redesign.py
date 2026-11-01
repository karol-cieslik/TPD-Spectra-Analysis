from pathlib import Path
import pytest
from tpd_spectra.workflow_state import WorkflowProject, METHODS, STAGES
from tpd_spectra.workflow_gui import WorkflowApp
from tpd_spectra.workflow_analysis import calculate, processed_signal
from tpd_spectra.analysis import leading_edge_fit, redhead_energy
import numpy as np

DEMO = Path(__file__).resolve().parents[1] / "examples/synthetic_two_peak_demo.csv"


def test_regions_have_stable_identity_and_independent_method_settings():
    project = WorkflowProject()
    dataset = project.add_dataset(DEMO)
    first = project.add_region("Peak 1", 100, 210)
    project.method_settings("Redhead")["prefactor"] = 1e12
    second = project.add_region("Peak 2", 220, 350)
    assert project.method_settings("Redhead")["prefactor"] == 1e13
    project.active_region = first.id
    assert project.method_settings("Redhead")["prefactor"] == 1e12
    project.update_region(first.id, "Updated peak", 110, 200)
    assert first.id in project.regions and second.id in project.regions
    assert not dataset.spectrum.signal.flags.writeable
    with pytest.raises(ValueError):
        project.add_region("invalid", 400, 500)


def test_three_stages_share_peak_and_show_only_one_method_panel(root):
    app = WorkflowApp(root)
    app._load_paths([DEMO])
    first = app.project.add_region("Peak 1", 110, 210)
    second = app.project.add_region("Peak 2", 230, 350)
    app.refresh_context()
    assert tuple(app.stages.tab(tab, "text") for tab in app.stages.tabs()) == STAGES
    for stage in range(3):
        app.stages.select(stage)
        root.update()
        assert app.project.active_region == second.id
        assert "Peak 2" in app.context_label.cget("text")
    for method in METHODS:
        app.method.set(method)
        app.refresh_method()
        root.update()
        assert [name for name, panel in app.method_panels.items() if panel.winfo_ismapped()] == [method]
        assert app.method_equations[method].winfo_ismapped()
        assert app.method_panels[method].pack_slaves()[0] is app.method_equations[method]
    app.project.active_region = first.id
    app.refresh_context()
    assert "Peak 1" in app.result_title.cget("text")


def test_equation_legends_do_not_change_analysis_settings(root):
    from copy import deepcopy
    app = WorkflowApp(root)
    app._load_paths([DEMO])
    app.project.add_region('First peak',100,210)
    app.refresh_context()
    app.stages.select(1)
    root.update()
    panel=app.modeling_panel
    before=deepcopy(panel.snapshot())
    for card in (panel.model_equation,panel.mc_equation):
        card.toggle_button.invoke()
        root.update()
        assert card.details.winfo_ismapped()
        assert card.details.cget('wraplength') <= card.winfo_width()
        card.toggle_button.invoke()
        assert not card.details.winfo_ismapped()
    assert panel.snapshot()==before
    assert not app.job_busy


def test_old_model_comparisons_are_stale_after_zero_order_engine_update(root):
    from copy import deepcopy
    app=WorkflowApp(root)
    app._load_paths([DEMO])
    app.project.add_region('First peak',100,210)
    app.refresh_context()
    panel=app.modeling_panel
    current={'snapshot':panel.snapshot()}
    assert panel.current(current)
    legacy=deepcopy(current)
    legacy['snapshot'].pop('modeling_engine_revision')
    assert not panel.current(legacy)
    app.project.method_settings('Polanyi–Wigner')['order']=0.
    assert panel.current(current)


def prepared():
    project = WorkflowProject()
    dataset = project.add_dataset(DEMO)
    region = project.add_region('First peak', 100, 210)
    return project, dataset, region


def test_adapters_match_existing_engine_and_do_not_invent_prefactor():
    project, dataset, _ = prepared()
    project.method_settings('Leading edge').update(lower=110, upper=130)
    result = calculate(dataset, project.snapshot('Leading edge'))
    direct = leading_edge_fit(dataset.spectrum.temperature_clean_c, dataset.spectrum.signal, 1, 110, 130)
    assert result['values']['energy_ev'] == direct.energy_ev
    assert result['values']['prefactor_s_inv'] is None
    redhead = calculate(dataset, project.snapshot('Redhead'))
    values = redhead['values']
    assert values['energy_ev'] == redhead_energy(values['peak_temperature_c'], 1e13, 1)


def test_processing_undo_and_snapshot_staleness_preserve_raw_and_saved_runs():
    project, dataset, region = prepared()
    raw = dataset.spectrum.signal.copy()
    result = calculate(dataset, project.snapshot('Redhead'))
    project.accept_result(result)
    saved = project.save_result(result, 'Baseline estimate')
    project.set_processing({'smoothing': 'mean', 'window': 5, 'baseline': .001})
    assert not project.result_is_current(result)
    assert not np.array_equal(processed_signal(dataset), raw)
    np.testing.assert_array_equal(dataset.spectrum.signal, raw)
    project.undo_processing()
    assert project.result_is_current(result)
    project.update_region(region.id, region.label, 110, 200)
    assert not project.result_is_current(result)
    assert saved['snapshot']['region'] == [100, 210]


def test_completed_background_result_never_crosses_context(root):
    app = WorkflowApp(root)
    app._load_paths([DEMO])
    first = app.project.add_region('First', 100, 210)
    app.method.set('Redhead')
    result = calculate(app.project.context()[0], app.project.snapshot('Redhead'))
    second = app.project.add_region('Second', 230, 350)
    app.refresh_context()
    app.complete_fit(result)
    assert app.displayed_result is None
    app.project.active_region = first.id
    app.refresh_context()
    assert app.displayed_result['snapshot']['region_id'] == first.id
    app.method_values['prefactor'].set('1e12')
    assert 'STALE' in app.result_text.get('1.0', 'end')
    app.method.set('Polanyi–Wigner')
    app.refresh_method()
    assert app.displayed_result is None
    app.project.active_region = second.id
    app.refresh_context()
    assert app.displayed_result is None


def test_cancel_and_failed_optimizer_do_not_produce_success(monkeypatch):
    project, dataset, _ = prepared()
    with pytest.raises(InterruptedError):
        calculate(dataset, project.snapshot('Polanyi–Wigner'), lambda: True)
    class Failure:
        success = False
        message = 'budget exhausted'
    monkeypatch.setattr('tpd_spectra.workflow_analysis.fit_polanyi_wigner', lambda *a, **k: (Failure(), []))
    with pytest.raises(ValueError, match='did not converge'):
        calculate(dataset, project.snapshot('Polanyi–Wigner'))


def test_leading_edge_cannot_escape_selected_peak():
    project, dataset, _ = prepared()
    project.method_settings('Leading edge')['lower'] = 90
    with pytest.raises(ValueError, match='inside'):
        calculate(dataset, project.snapshot('Leading edge'))


def test_monte_carlo_medians_transfer_only_as_initial_guesses():
    from tpd_spectra.workflow_modeling import transfer_starting_values
    candidate = {'name': 'fractional', 'error': None,
                 'fit': {'activation_energy_eV': 1.1, 'prefactor_s_inv': 1e13,
                         'reaction_order': 1.5}}
    mc = {'seed': 42, 'reference_model': 'fractional', 'cancelled': False,
          'replicates_requested': 100, 'replicates_completed': 100,
          'minimum_successful_refits': 100,
          'replicate_records': [
              {'model': 'fractional', 'error': None, 'energy_eV': energy,
               'log10_prefactor': lognu, 'order': order}
              for energy, lognu, order in
              ([(1.18, 12., 1.4)] * 49 + [(1.20, 13., 1.6)] * 2
               + [(1.25, 14., 1.8)] * 49)]}
    values, description = transfer_starting_values(candidate, mc)
    assert values['energy'] == 1.20
    assert values['prefactor'] == pytest.approx(1e13)
    assert values['order'] == 1.6
    assert values['free_order'] is True
    assert 'heuristic initial guesses' in description
    assert 'joint fit' in description
    mc['minimum_successful_refits'] = 101
    with pytest.raises(ValueError, match='at least 101'):
        transfer_starting_values(candidate, mc)
    mc['minimum_successful_refits'] = 100
    mc['cancelled'] = True
    with pytest.raises(ValueError, match='completed Monte Carlo'):
        transfer_starting_values(candidate, mc)


def test_zero_order_monte_carlo_never_invents_unique_prefactor():
    from tpd_spectra.workflow_modeling import transfer_starting_values
    candidate = {'name': 'zero', 'error': None,
                 'fit': {'activation_energy_eV': 0.9, 'prefactor_s_inv': 2e10,
                         'reaction_order': 0.0}}
    mc = {'seed': 9, 'reference_model': 'zero', 'cancelled': False,
          'replicates_requested': 100, 'replicates_completed': 100,
          'minimum_successful_refits': 100,
          'replicate_records': [
              {'model': 'zero', 'error': None, 'energy_eV': energy,
               'log10_prefactor': None, 'order': 0.0}
              for energy in ([0.8] * 50 + [1.0] * 50)]}
    values, note = transfer_starting_values(candidate, mc)
    assert values['energy'] == pytest.approx(0.9)
    assert values['prefactor'] == 2e10
    assert not values['free_order']
    assert 'not separately identifiable' in note


def test_modeling_comparison_transfer_and_monte_carlo_route(root, monkeypatch):
    from tpd_spectra.workflow_modeling import comparison
    app = WorkflowApp(root)
    app._load_paths([DEMO])
    first = app.project.add_region('First', 100, 210)
    app.refresh_context()
    panel = app.modeling_panel
    for key in ('zero','second','fractional','multistart'):
        panel.variables[key].set(False)
    snap = panel.snapshot()
    result = comparison(app.project.context()[0],snap,lambda:False)
    assert result['candidates'][0]['error'] is None
    panel.complete('comparison',result)
    # MC count/seed edits must not invalidate the underlying fit comparison.
    panel.variables['replicates'].set('2')
    panel.variables['seed'].set('17')
    assert panel.current(result)
    old = app.project.method_settings('Polanyi–Wigner').copy()
    assert old['energy'] == 1
    panel.table.selection_set('0')
    panel.transfer()
    assert app.project.method_settings('Polanyi–Wigner')['energy'] == result['candidates'][0]['fit']['activation_energy_eV']
    assert app.project.current_results == {}
    # Exercise the real MC engine through the UI's submitted worker function.
    def inline(work,done):
        done(work())
        return True
    monkeypatch.setattr(app,'start_job',inline)
    panel.monte_carlo()
    mc = panel.session()['monte_carlo']['result']
    assert mc['seed'] == 17 and mc['replicates_completed'] == 2
    assert mc['parameter_intervals'] == {'first': {}}
    # The user does not need to pick a row: current Monte Carlo reference is selected.
    panel.table.selection_remove(panel.table.selection())
    # A two-refit smoke run cannot masquerade as a precise parameter estimate.
    panel.transfer(monte_carlo=True)
    assert 'at least 100' in app.status.get()
    # Exercising the new one-click transfer with sufficient successful samples.
    # Supply a completed, 100-replicate fixture to exercise transfer UI.
    panel.variables['replicates'].set('100')
    panel.session()['monte_carlo']['snapshot'] = panel.snapshot()
    mc['replicates_requested'] = 100
    mc['replicates_completed'] = 100
    mc['minimum_successful_refits'] = 100
    mc['replicate_records'] = (
        [{'model': 'first', 'error': None, 'energy_eV': 1.1,
          'log10_prefactor': 12., 'order': 1.0}] * 50
        + [{'model': 'first', 'error': None, 'energy_eV': 1.3,
            'log10_prefactor': 14., 'order': 1.0}] * 50)
    panel.mc_transfer.invoke()
    transferred = app.project.method_settings('Polanyi–Wigner')
    assert transferred['energy'] == pytest.approx(1.2)
    assert transferred['prefactor'] == pytest.approx(1e13)
    assert 'Transferred starting guesses' in app.transfer_summary.get()
    assert app.project.current_results == {}
    # Point-fit transfer is still available with no selected row.
    panel.transfer()
    assert app.project.method_settings('Polanyi–Wigner')['energy'] == result['candidates'][0]['fit']['activation_energy_eV']
    app.project.add_region('Second',230,350)
    app.refresh_context()
    assert panel.table.get_children() == ()
    app.project.active_region = first.id
    app.refresh_context()
    assert len(panel.table.get_children()) == 1
    assert panel.variables['seed'].get() == '17'
    panel.variables['beta'].set('2')
    assert not panel.current(result)
    panel.transfer()
    assert 'Compare current settings' in app.status.get()


def test_live_preview_and_saved_runs_restore_their_own_settings(root):
    app=WorkflowApp(root)
    app._load_paths([DEMO])
    first=app.project.add_region('First',100,210)
    app.method.set('Redhead')
    app.refresh_context()
    app.preview_selected()
    first_energy=app.displayed_result['values']['energy_ev']
    saved=app.project.save_result(app.displayed_result,'First original')
    app.method_values['prefactor'].set('1e12')
    app.preview_selected()
    assert app.displayed_result['values']['energy_ev']<first_energy
    app.project.add_region('Second',230,350)
    app.refresh_context()
    app.preview_selected()
    assert app.displayed_result['snapshot']['region_id']!=first.id
    method=app.project.reopen_run(saved['id'])
    app.method.set(method)
    app.refresh_context()
    assert app.displayed_result['values']['energy_ev']==first_energy
    assert app.project.result_is_current(app.displayed_result)


def test_async_worker_failure_preserves_previous_success(root,monkeypatch):
    import time
    app=WorkflowApp(root)
    app._load_paths([DEMO])
    app.project.add_region('First',100,210)
    app.method.set('Redhead')
    app.refresh_context()
    app.preview_selected()
    existing=app.displayed_result.copy()
    app.method.set('Polanyi–Wigner')
    app.refresh_method()
    def fail():
        raise ValueError('deliberate optimizer failure')
    app.start_job(fail,lambda _:pytest.fail('Failure invoked success callback'))
    deadline=time.monotonic()+5
    while app.job_busy and time.monotonic()<deadline:
        root.update()
        time.sleep(.01)
    assert not app.job_busy
    assert 'deliberate optimizer failure' in app.status.get()
    app.method.set('Redhead')
    app.refresh_method()
    assert app.displayed_result==existing


def test_project_install_and_small_window_controls(root,tmp_path):
    from tpd_spectra.workflow_io import save_project,load_project
    app=WorkflowApp(root)
    app._load_paths([DEMO])
    app.project.add_region('First',100,210)
    path=save_project(app.project,tmp_path/'roundtrip.tpd.json')
    app.install_project(load_project(path))
    root.state('normal')
    root.geometry('1100x720')
    for stage in range(3):
        app.stages.select(stage)
        root.update()
        assert app.stages.winfo_width()>1000
        assert app.stage_frames[stage].winfo_height()>300
        assert app.dataset_combo.winfo_ismapped()
        assert app.region_combo.winfo_ismapped()
    assert app.result_canvas.get_tk_widget().winfo_height()>150


def test_model_parameter_edits_debounce_and_context_switch_cancels_preview(root,monkeypatch):
    import time
    app=WorkflowApp(root)
    app._load_paths([DEMO])
    first=app.project.add_region('First',100,210)
    app.refresh_context()
    # Drain initial notebook/map events before simulating user edits.
    root.update()
    panel=app.modeling_panel
    calls=[]
    monkeypatch.setattr(panel,'simulate',lambda:calls.append(panel.variables['energy'].get()))
    panel.variables['energy'].set('1.1')
    panel.variables['energy'].set('1.2')
    deadline=time.monotonic()+2
    while not calls and time.monotonic()<deadline:
        root.update()
        time.sleep(.01)
    assert calls==['1.2']
    panel.variables['energy'].set('1.3')
    app.project.add_region('Second',230,350)
    app.refresh_context()
    assert panel.preview_after is None
    assert panel.variables['energy'].get()=='1.25'
