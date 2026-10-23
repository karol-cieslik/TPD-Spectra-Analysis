from pathlib import Path
import pytest
from tpd_spectra.workflow_state import WorkflowProject, METHODS, STAGES
from tpd_spectra.workflow_gui import WorkflowApp

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
