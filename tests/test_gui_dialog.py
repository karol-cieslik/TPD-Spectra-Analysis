"""Real Tk widget regressions; Windows CI must execute these, not skip them."""
from pathlib import Path

import pytest

from tpd_spectra.gui import QuickStartDialog, TpdSpectraApp, QUICK_START_STEPS


def test_quick_start_has_real_paragraphs_and_scrolls_at_small_size(root):
    dialog = QuickStartDialog(root)
    root.update()
    text = dialog.text.get("1.0", "end-1c")
    assert r"\n" not in text
    for heading, body in QUICK_START_STEPS:
        assert heading + "\n" + body + "\n" in text
    assert len(dialog.text.tag_ranges("heading")) == 10
    assert str(dialog.text.cget("state")) == "disabled"
    assert str(dialog.text.cget("wrap")) == "word"
    dialog.geometry("440x340")
    root.update()
    assert dialog.text.yview()[1] < 1.
    dialog.text.yview_moveto(1)
    root.update()
    assert dialog.text.yview()[1] == pytest.approx(1.)
    assert dialog.close_button.winfo_y() + dialog.close_button.winfo_height() <= dialog.winfo_height()
    dialog.close_button.invoke()
    root.update()
    assert not dialog.winfo_exists()
    assert root.grab_current() is None


def test_gui_imports_the_shipped_demo_and_draws_it(root, monkeypatch, tmp_path):
    from tpd_spectra import gui
    warnings = []
    monkeypatch.setattr(gui.messagebox, "showwarning", lambda *args, **kw: warnings.append(args))
    app = TpdSpectraApp(root)
    path = Path(__file__).resolve().parents[1] / "examples" / "synthetic_two_peak_demo.csv"
    app._load_paths([path])
    root.update()
    assert warnings == []
    assert len(app.spectra) == len(app.file_table.get_children()) == 1
    assert next(iter(app.spectra.values()))["spec"].signal.size == 601
    assert "1 visible of 1 imported" in app.status.get()
    app.figure.savefig(tmp_path / "demo.png")
    assert (tmp_path / "demo.png").stat().st_size > 1000


def test_import_preview_allows_column_and_unit_correction_and_reports_rejected_rows(root, tmp_path):
    import numpy as np
    import pandas as pd
    from tpd_spectra.import_preview_gui import ImportPreviewDialog

    seconds = np.arange(60.)
    seconds[10] = seconds[9]  # duplicate timestamp is explicitly rejected
    frame = pd.DataFrame({"Clock": seconds, "Detector": np.linspace(1, 2, 60),
                          "Sample": 300. + np.arange(60) * .5})
    frame.loc[len(frame)] = ["invalid", 2.0, 400.0]
    path = tmp_path / "custom.txt"
    frame.to_csv(path, sep="\t", index=False)

    app = TpdSpectraApp(root)
    dialog = ImportPreviewDialog(app, [path], app._load_previewed_spectra)
    assert dialog.records[0]["status"] == "Needs unit choice"
    for name, column in (("time", "Clock"), ("signal", "Detector"), ("temperature", "Sample")):
        dialog.column_vars[name].set(column)
    dialog.time_unit.set("s")
    dialog.temperature_unit.set("K")
    dialog._settings_changed()
    assert dialog.records[0]["status"] == "Ready with rejected rows"
    assert "accepted: 59" in dialog.count_label.cget("text")
    assert "rejected: 2" in dialog.count_label.cget("text")
    dialog.import_button.invoke()
    root.update()
    assert len(app.spectra) == 1
    imported = next(iter(app.spectra.values()))["spec"]
    assert imported.signal.size == 59
    assert len(imported.import_report["rejected_records"]) == 2
