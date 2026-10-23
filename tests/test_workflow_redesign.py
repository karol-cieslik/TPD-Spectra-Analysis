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
    app.project.active_region = first.id
    app.refresh_context()
    assert "Peak 1" in app.result_title.cget("text")


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
