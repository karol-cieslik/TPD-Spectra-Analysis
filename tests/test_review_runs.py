"""Behavioral regressions for reviewed runs, lifecycle and scientific reporting."""
import json
from pathlib import Path
import queue
import shutil
import sys
import threading
import tkinter as tk

import numpy as np
import pandas as pd
import pytest

from tpd_spectra.analysis import load_spectrum, leading_edge_fit, K_B_EV
from tpd_spectra.gui import TpdSpectraApp, build_cli_arguments
from tpd_spectra.gui_review import ReviewDialog, ResultsDialog
from tpd_spectra.run_session import RunPlan, execute, result_state

DEMO = Path(__file__).resolve().parents[1] / "examples/synthetic_two_peak_demo.csv"


def settings_for(folder, inputs=None):
    return dict(input_files=[str(p) for p in (inputs or [DEMO])], output_path=str(folder),
                leading_low=110., leading_high=140., redhead_low=150., redhead_high=210.,
                prefactor="1e13", window=1, filter="none", max_time_min="10",
                kinetic_fit=False, kinetic_model="single", kinetic_order="1",
                kinetic_initial_energy="1.0", kinetic_initial_prefactor="1e13", kinetic_no_baseline=False)


def plan_for(folder, inputs=None, preview=False):
    settings = settings_for(folder, inputs)
    return RunPlan.create(settings, build_cli_arguments(settings), preview=preview)


def drain(messages):
    result = []
    while not messages.empty():
        result.append(messages.get_nowait())
    return result


@pytest.fixture
def root():
    try:
        value = tk.Tk()
    except tk.TclError:
        if sys.platform == "win32":
            raise
        pytest.skip("Tk display unavailable")
    yield value
    value.destroy()


def test_plan_is_immutable_and_rejects_duplicate_names_and_existing_output(tmp_path):
    settings = settings_for(tmp_path / "new")
    plan = RunPlan.create(settings, build_cli_arguments(settings))
    settings["prefactor"] = "1e30"
    settings["input_files"].clear()
    assert json.loads(plan.settings_json)["prefactor"] == "1e13"
    assert len(plan.inputs) == 1
    plan.output.mkdir()
    marker = plan.output / "keep.txt"
    marker.write_text("previous results")
    with pytest.raises(ValueError, match="already exists"):
        plan_for(plan.output)
    assert marker.read_text() == "previous results"
    other = tmp_path / DEMO.name
    shutil.copyfile(DEMO, other)
    with pytest.raises(ValueError, match="identical names"):
        plan_for(tmp_path / "duplicates", [DEMO, other])


def test_changed_input_and_collision_never_write_results(tmp_path):
    source = tmp_path / "changed.csv"
    shutil.copyfile(DEMO, source)
    plan = plan_for(tmp_path / "run", [source])
    source.write_text("changed after review")
    messages = queue.Queue()
    execute(plan, messages, threading.Event())
    assert "changed since review" in drain(messages)[0][1]
    assert not plan.output.exists()
    plan = plan_for(tmp_path / "collision")
    plan.output.mkdir()
    execute(plan, messages, threading.Event())
    assert drain(messages)[0][0] == "error"
    assert list(plan.output.iterdir()) == []


def test_real_preview_and_saved_run_have_identical_results(tmp_path):
    for name, preview in (("preview", True), ("saved", False)):
        plan = plan_for(tmp_path / name, preview=preview)
        messages = queue.Queue()
        execute(plan, messages, threading.Event())
        events = drain(messages)
        assert events[-1] == ("finished", "completed")
        assert any(kind == "log" and "[1/1]" in text for kind, text in events)
        record = json.loads((plan.output / "run_status.json").read_text())
        assert record["preview"] == preview
        assert record["settings"]["prefactor"] == "1e13"
        assert len(record["inputs"][0]["sha256"]) == 64
    pd.testing.assert_frame_equal(pd.read_csv(tmp_path / "preview/all_desorption_parameters.csv"),
                                  pd.read_csv(tmp_path / "saved/all_desorption_parameters.csv"))


def test_mixed_batch_preserves_success_but_reports_partial_failure(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("not a spectrum")
    plan = plan_for(tmp_path / "mixed", [DEMO, bad])
    messages = queue.Queue()
    execute(plan, messages, threading.Event())
    assert drain(messages)[-1] == ("finished", "partially failed")
    assert (plan.output / "all_desorption_parameters.csv").exists()
    assert "bad.csv" in (plan.output / "analysis_errors.csv").read_text()


def test_cancel_stops_child_and_records_partial_output(tmp_path):
    script = tmp_path / "slow.py"
    script.write_text("import time\nprint('ready', flush=True)\ntime.sleep(60)\n")
    plan = plan_for(tmp_path / "cancel")
    messages, cancel = queue.Queue(), threading.Event()
    worker = threading.Thread(target=execute, args=(plan, messages, cancel),
                              kwargs={"command_prefix": [sys.executable, "-u", str(script)]})
    worker.start()
    assert messages.get(timeout=20) == ("log", "ready")
    cancel.set()
    worker.join(timeout=10)
    assert not worker.is_alive()
    assert messages.get(timeout=2) == ("finished", "cancelled")
    assert json.loads((plan.output / "run_status.json").read_text())["state"] == "cancelled"
    assert "ready" in (plan.output / "run.log").read_text()


@pytest.mark.parametrize("key", ["prefactor", "leading_low", "max_time_min", "kinetic_initial_energy"])
@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
def test_nonfinite_settings_are_blocked_before_output(tmp_path, key, value):
    settings = settings_for(tmp_path / "bad")
    settings[key] = value
    with pytest.raises(ValueError, match="finite"):
        build_cli_arguments(settings)
    assert not (tmp_path / "bad").exists()


def test_import_report_preserves_record_identity_and_reasons(tmp_path):
    path = tmp_path / "audit.csv"
    path.write_text("ms,Signal,Temperature\n2000,3,102\n0,1,100\n1000,2,101\n1000,9,130\n3000,bad,103\n4000,5,104\n")
    report = load_spectrum(path).import_report
    assert report["original_data_records"] == 6
    assert report["accepted_original_records"] == [2, 3, 1, 6]
    assert report["sorted_by_time"]
    assert {item["data_record"] for item in report["rejected_records"]} == {4, 5}
    assert path.read_text().startswith("ms,Signal,Temperature")


def test_uncalibrated_signal_cannot_identify_a_physical_prefactor():
    temperature = np.linspace(100., 180., 100)
    signal = np.exp(20 - 1.2 / (K_B_EV * (temperature + 273.15)))
    original = leading_edge_fit(temperature, signal, 1., 110, 170)
    scaled = leading_edge_fit(temperature, signal * 1000, 5., 110, 170)
    assert original.energy_ev == pytest.approx(1.2, abs=1e-12)
    assert scaled.energy_ev == pytest.approx(original.energy_ev, abs=1e-12)
    assert scaled.intercept - original.intercept == pytest.approx(np.log(1000))
    assert np.isnan(original.prefactor_s_inv) and np.isnan(scaled.prefactor_s_inv)


def test_review_cancellation_has_no_output_and_visibility_does_not_select_analysis(root, tmp_path):
    app = TpdSpectraApp(root)
    app._load_paths([DEMO])
    app._set_visible(False)
    assert next(iter(app.spectra.values()))["included"]
    settings = settings_for(tmp_path)
    calls = []
    dialog = ReviewDialog(root, settings, list(app.spectra.values()), lambda *args: calls.append(args))
    root.update()
    assert "1e13" in dialog.summary.get("1.0", "end")
    assert "no fit calculated" in dialog.figure.axes[0].get_title()
    dialog.destroy()
    assert calls == []
    assert list(tmp_path.iterdir()) == []


def test_review_passes_snapshot_and_resets_confirmation_on_destination_edit(root, tmp_path):
    row = dict(path=DEMO, spec=load_spectrum(DEMO))
    settings = settings_for(tmp_path)
    calls = []
    dialog = ReviewDialog(root, settings, [row], lambda *args: calls.append(args) or True)
    settings["prefactor"] = "1e30"
    dialog.confirmed.set(True)
    dialog.destination.set(str(tmp_path / "new"))
    assert not dialog.confirmed.get()
    dialog.confirmed.set(True)
    dialog.start(False)
    assert calls[0][0]["prefactor"] == "1e13"
    assert not (tmp_path / "new").exists()


def test_terminal_status_uses_run_snapshot_not_current_output(root, tmp_path, monkeypatch):
    from tpd_spectra import gui
    app = TpdSpectraApp(root)
    plan = plan_for(tmp_path / "actual")
    app.active_plan = plan
    app.running = True
    app.output_path.set(str(tmp_path / "edited"))
    shown = []
    monkeypatch.setattr(gui, "ResultsDialog", lambda *args, **kwargs: shown.append((args, kwargs)))
    app.worker_messages.put(("finished", "completed"))
    app._poll_worker()
    assert str(plan.output) in app.status.get()
    assert app.last_output == plan.output
    assert shown[0][0][1] == plan.output


def test_results_failures_and_preview_staleness_are_visible(root, tmp_path):
    (tmp_path / "analysis_errors.csv").write_text("file_name,error\nbad.csv,invalid input\n")
    dialog = ResultsDialog(root, tmp_path, "partially failed", preview=True, stale=True)
    root.update()
    assert "bad.csv" in dialog.summary.get("1.0", "end")
    assert "invalid input" in dialog.summary.get("1.0", "end")
    dialog.destroy()
