"""Export round-trip and metadata tests (headless, deterministic)."""
import csv
import json
import numpy as np

from tpd_spectra.explorer_export import export_explorer_bundle
from tpd_spectra.kinetics_explorer import ModelCandidate


def test_export_bundle_handles_failed_model_and_fitted_curve(tmp_path):
    t = np.linspace(90, 180, 20)
    y = np.sin(np.linspace(0, 2, 20))
    fit = ModelCandidate("first", None, y.copy(), None, delta_aicc=0.0)
    failed = ModelCandidate("zero", None, None, "cannot converge")
    dest = export_explorer_bundle(tmp_path / "new-run", t, y, [fit, failed],
                                   beta_k_s=1.0, source="example.csv")
    assert (dest / "fit_overlay_and_residuals.png").is_file()
    assert (dest / "fitted_curves.csv").is_file()
    with (dest / "model_comparison.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert rows[1]["error"] == "cannot converge"
    manifest = json.loads((dest / "explorer_analysis.json").read_text())
    assert manifest["n_points"] == 20
    assert len(manifest["input_arrays_sha256"]) == 64
    assert manifest["source"] == "example.csv"
