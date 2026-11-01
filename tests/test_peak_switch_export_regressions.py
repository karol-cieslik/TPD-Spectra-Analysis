"""Regression coverage for beta export feedback and peak switching."""
from pathlib import Path

import numpy as np
import pytest

from tpd_spectra.workflow_analysis import selected_arrays
from tpd_spectra.workflow_gui import WorkflowApp
from tpd_spectra.workflow_state import WorkflowProject

DEMO = Path(__file__).resolve().parents[1] / "examples/synthetic_two_peak_demo.csv"


def test_updating_peak_rebases_invalid_leading_edge_interval_without_losing_saved_provenance():
    project = WorkflowProject()
    dataset = project.add_dataset(DEMO)
    region = project.add_region("First", 70, 210)
    settings = project.method_settings("Leading edge")
    assert (settings["lower"], settings["upper"]) == (70, 210)

    project.update_region(region.id, "Second", 223.435, 323.217)
    assert (settings["lower"], settings["upper"]) == (223.435, 323.217)
    assert project.snapshot("Leading edge")["region"] == [223.435, 323.217]

    settings.update(lower=240, upper=260)
    project.update_region(region.id, "Second refined", 230, 320)
    assert (settings["lower"], settings["upper"]) == (240, 260)

    result = {"snapshot": project.snapshot("Leading edge"), "status": "preview"}
    original = project.save_result(result, "Second peak")
    project.update_region(region.id, "Second shifted", 270, 330)
    assert (settings["lower"], settings["upper"]) == (270, 330)
    assert original["snapshot"]["region"] == [230, 320]
    assert dataset.spectrum.signal.size > 0


def test_empty_report_button_explains_prerequisites_and_updates_count(root, monkeypatch):
    app = WorkflowApp(root)
    messages = []
    monkeypatch.setattr("tpd_spectra.workflow_project_gui.messagebox.showinfo",
                        lambda title, text, **kwargs: messages.append((title, text)))
    assert "(0 saved)" in app.report_button.cget("text")
    app.report_button.invoke()
    assert len(messages) == 1
    assert "Save labeled result" in messages[0][1]

    app._load_paths([DEMO])
    app.preview_selected()
    assert app.displayed_result is not None
    app.project.save_result(app.displayed_result, "Demo estimate")
    app.refresh_saved_runs()
    assert "(1 saved)" in app.report_button.cget("text")
    app.report_button.invoke()
    dialogs = [widget for widget in root.winfo_children()
               if widget.winfo_class() == "Toplevel"]
    assert any(dialog.title() == "Review report selection and export destination"
               for dialog in dialogs)
    for dialog in dialogs:
        dialog.destroy()


def test_peak_change_hides_stale_comparison_and_scales_current_models(root):
    app = WorkflowApp(root)
    app._load_paths([DEMO])
    panel = app.modeling_panel
    dataset, region = app.project.context()
    session = panel.session()
    previous = panel.snapshot()
    old_t, old_y = selected_arrays(dataset, previous)
    session["comparison"] = {
        "snapshot": previous,
        "temperature": old_t.tolist(),
        "signal": old_y.tolist(),
        "candidates": [],
    }
    session["display_mode"] = "comparison"

    app.project.update_region(region.id, "Second peak", 223.435, 323.217)
    app.refresh_context()
    xlo, xhi = panel.fig.axes[0].get_xlim()
    assert 210 < xlo < 230 and 320 < xhi < 340
    assert "STALE comparison" in panel.notes.get("1.0", "end")
    assert panel.table.get_children() == ()

    current = panel.snapshot()
    t, y = selected_arrays(dataset, current)
    session["comparison"] = {
        "snapshot": current,
        "temperature": t.tolist(),
        "signal": y.tolist(),
        "candidates": [{
            "name": "first",
            "fit": {"reaction_order": 1.0, "activation_energy_eV": 1.0,
                    "prefactor_s_inv": 1e13, "rmse_signal": .001},
            "prediction": (y * 1.01).tolist(),
            "error": None,
            "delta_aicc": 0.0,
            "warnings": [],
        }],
    }
    # This deliberately oversized manual simulation used to make fitted
    # curves nearly invisible in the single shared autoscaled plot.
    session["simulation"] = {
        "snapshot": current,
        "temperature": t.tolist(),
        "prediction": np.full_like(t, 50.0).tolist(),
    }
    session["display_mode"] = "comparison"
    panel.render()
    axis = panel.fig.axes[0]
    assert axis.get_ylim()[1] < 1.0
    assert not any("Manual simulation" in line.get_label() for line in axis.lines)
    assert len(panel.table.get_children()) == 1

    session["display_mode"] = "simulation"
    panel.render()
    assert panel.fig.axes[0].get_ylim()[1] > 50.0
    assert "adjust Simulation signal scale" in panel.notes.get("1.0", "end")
