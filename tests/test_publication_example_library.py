"""Publication-data provenance, unit conversion and compact desktop navigation."""
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.generate_publication_examples import BASE, transform
from tpd_spectra.analysis import load_spectrum
from tpd_spectra.workflow_state import WorkflowProject

CATALOG = json.loads((BASE / "catalog.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("item", CATALOG, ids=lambda r: r["file"])
def test_publication_examples_preserve_source_trace_and_license(item):
    assert item["license"].startswith("CC BY")
    assert item["doi"] and item["citation"] and item["figure"]
    assert item["source_repo_path"].startswith("validation/")
    assert item["accepted_records"] >= 3
    assert item["omitted_records"] >= 0
    assert "ground truth" not in item["description"].lower()

    original = pd.read_csv(BASE / item["source_csv"])
    compat = pd.read_csv(BASE / item["file"])
    expected = np.asarray(transform(item))
    assert len(original) == item["original_records"]
    assert compat.shape == (item["accepted_records"], 3)
    np.testing.assert_allclose(compat["ms"], expected[:, 0], rtol=1e-12, atol=1e-6)
    np.testing.assert_allclose(compat["DHTA+"], expected[:, 1], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(compat["Temperatura"], expected[:, 2], rtol=1e-12, atol=1e-9)
    assert np.all(np.diff(compat["ms"]) > 0)

    spectrum = load_spectrum(BASE / item["file"])
    np.testing.assert_allclose(spectrum.temperature_c, compat["Temperatura"].to_numpy())
    np.testing.assert_allclose(spectrum.signal, compat["DHTA+"].to_numpy())
    project = WorkflowProject()
    data = project.add_dataset(BASE / item["file"])
    lo, hi = item["region_K"]
    region = project.add_region("Published", lo - 273.15, hi - 273.15)
    assert region.lower < region.upper
    assert data.spectrum.signal.size == item["accepted_records"]


def test_publication_catalog_withholds_unresolved_or_restricted_sources():
    listed = {r["source_repo_path"] for r in CATALOG}
    assert not any("ethanol_2024/digitized" in name for name in listed)
    assert not any("CO_digitized" in name for name in listed)
    assert {r["source_time_column"] for r in CATALOG} == {None, "Time"}
    for row in CATALOG:
        assert "not measured time" in row["time_coordinate"].lower() or "measured time" in row["time_coordinate"].lower()


def test_menu_is_compact_and_publishable_examples_are_separate(root):
    from tpd_spectra.workflow_gui import WorkflowApp
    from tpd_spectra.beta_onboarding import ExampleDialog

    app = WorkflowApp(root)
    menu = root.nametowidget(root["menu"])
    labels = [menu.entrycget(i, "label") for i in range(menu.index("end") + 1)]
    assert labels == ["File", "Examples", "View", "Help"]
    assert len(app.project_actions.winfo_children()) == 1
    assert app.report_button.winfo_exists()

    dialog = ExampleDialog(app, section="publication")
    assert dialog.tabs.index(dialog.tabs.select()) == 1
    assert len(dialog.trees["publication"].get_children()) == len(CATALOG)
    assert len(dialog.trees["synthetic"].get_children()) > len(CATALOG)
    description = dialog.details.get("1.0", "end")
    assert "DOI:" in description and "LIMITATION:" in description
    dialog.open()
    assert app.project.active_region is not None
    dataset, region = app.project.context()
    assert dataset.path.endswith(CATALOG[0]["file"])
    assert dataset.spectrum.temperature_c.min() < 0
    assert region.label == CATALOG[0]["peak_label"]
    assert "Published data opened" in app.status.get()
    root.update_idletasks()
    assert "Zaki" in app.example_source_note.cget("text")
    assert app.example_source_note.grid_info()  # root mapping varies in CI
    assert sum(row["visible"] for row in app.spectra.values()) == 1
    xlo, xhi = app.axis.get_xlim()
    assert xlo < dataset.spectrum.temperature_clean_c.min()
    assert xhi > dataset.spectrum.temperature_clean_c.max()
    assert xhi - xlo < 1.1 * np.ptp(dataset.spectrum.temperature_clean_c)
    publication = dataset.spectrum.import_report["publication_example"]
    assert publication["doi"] == CATALOG[0]["doi"]
    assert publication["time_coordinate"] == CATALOG[0]["time_coordinate"]
    from tpd_spectra.workflow_io import project_payload
    saved = project_payload(app.project)["datasets"][0]["spectrum"]["import_report"]
    assert saved["publication_example"]["citation"] == CATALOG[0]["citation"]


def test_figure_example_uses_nominal_time_not_measured_time():
    row = next(r for r in CATALOG if r["file"].startswith("zaki_"))
    assert row["source_time_column"] is None
    assert "NOT measured time" in row["time_coordinate"]
    original = pd.read_csv(BASE / row["source_csv"])
    imported = pd.read_csv(BASE / row["file"])
    first = imported["Temperatura"].iloc[0] + 273.15
    expected_ms = (imported["Temperatura"] + 273.15 - first) / row["beta_K_s"] * 1000
    np.testing.assert_allclose(imported["ms"], expected_ms, atol=1e-6)

def test_clean_synthetic_example_keeps_documented_leading_edge(root):
    from tpd_spectra.workflow_gui import WorkflowApp
    app = WorkflowApp(root)
    dialog = app.open_example()
    dialog.open()
    settings = app.project.method_settings("Leading edge")
    assert (settings["lower"], settings["upper"]) == (90., 110.)
