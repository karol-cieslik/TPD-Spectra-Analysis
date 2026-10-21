"""Smoke-test the actual frozen executable against the shipped demo."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    executable = Path(sys.argv[1]).resolve()
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "TCL_LIBRARY", "TK_LIBRARY"):
        env.pop(key, None)
    with tempfile.TemporaryDirectory(prefix="tpd-frozen-smoke-") as folder:
        output = Path(folder)
        completed = subprocess.run([
            str(executable), "--tpd-cli", str(root / "examples/synthetic_two_peak_demo.csv"),
            "--output", str(output), "--leading-edge", "110", "140",
            "--redhead-region", "150", "210", "--prefactor", "1e13", "--filter", "none",
        ], env=env, timeout=180, check=True)
        assert completed.returncode == 0
        with (output / "all_desorption_parameters.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 1
        assert abs(float(rows[0]["redhead_energy_eV"]) - 1.25) / 1.25 < .02
        assert (output / "all_tds_spectra.png").stat().st_size > 1000
        assert list((output / "diagnostics").glob("*.png"))
        assert not (output / "analysis_errors.csv").exists()
        manifest = json.loads((output / "analysis_project.json").read_text(encoding="utf-8"))
        assert len(manifest["inputs_processed"]) == 1
        print("Frozen Windows executable: shipped demo analysis and exports passed")


if __name__ == "__main__":
    main()
