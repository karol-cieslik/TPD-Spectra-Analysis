#!/usr/bin/env python3
"""Reproduce a bounded second-order TPD challenge from published O2/Pt(111) data.

The source data are intentionally not copied into this repository. Clone the
author's supporting-information repository and pass its root directory:

    python scripts/experimental_o2_pt111_check.py /path/to/kitchingroup-43

Inputs use the source paper's published processing: subtract each trace's mean
signal over 400 < T < 500 K, retain 500 <= T <= 1000 K, and fit at beta=2 K/s.
The input temperatures are Kelvin; this application's fitter accepts Celsius.
"Initial energy" and prefactor are optimizer starting values, not fixed values.
"Free order" is a descriptive phenomenological estimate, not a mechanism.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import xlrd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tpd_spectra.kinetics import fit_polanyi_wigner


SOURCE_REPOSITORY = "https://github.com/KitchinHUB/kitchingroup-43"
SOURCE_COMMIT = "f6283ff07df32f982542809b1ab3c2344b24f1d3"
SOURCE_DOI = "10.1007/s11244-013-0166-3"
SOFTWARE_COMMIT = "4dcbd3ad56689a6a326ac99baed26c9ee2902fcb"
BETA_K_S = 2.0
FIT_RANGE_K = [500.0, 1000.0]
BASELINE_RANGE_K = [400.0, 500.0]
INITIAL_ENERGY_EV = 1.9
INITIAL_PREFACTOR_S_INV = 1e12
MAX_NFEV = 300

# Source SI's leading-edge estimates. Indices match its printed "Spectra i"
# and are also the Python index into the source's coverage-normalized series.
LEADING_EDGE_REFERENCES = {
    2: (1.905, 1.640, 2.170),
    3: (1.884, 1.769, 1.998),
    4: (1.911, 1.809, 2.014),
    5: (1.847, 1.764, 1.930),
    6: (1.840, 1.760, 1.919),
    7: (1.885, 1.802, 1.968),
    8: (1.858, 1.735, 1.982),
    9: (1.861, 1.770, 1.951),
    10: (1.873, 1.772, 1.975),
    11: (1.804, 1.723, 1.885),
    12: (1.875, 1.788, 1.963),
    13: (1.858, 1.809, 1.907),
    14: (1.904, 1.815, 1.993),
    15: (1.875, 1.797, 1.952),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_spectrum(path: Path) -> tuple[np.ndarray, np.ndarray]:
    sheet = xlrd.open_workbook(str(path)).sheet_by_index(0)
    rows = np.asarray(
        [[sheet.cell_value(i, 0), sheet.cell_value(i, 1)] for i in range(1, sheet.nrows)],
        dtype=float,
    )
    temperature_k, signal = rows.T
    background = float(signal[(temperature_k > 400.0) & (temperature_k < 500.0)].mean())
    selected = (temperature_k >= FIT_RANGE_K[0]) & (temperature_k <= FIT_RANGE_K[1])
    return temperature_k[selected], signal[selected] - background


def fit_case(temperature_k: np.ndarray, signal: np.ndarray, order: float, free: bool) -> dict:
    result, _ = fit_polanyi_wigner(
        temperature_k - 273.15,
        signal,
        BETA_K_S,
        reaction_order=order,
        fit_reaction_order=free,
        initial_energy_ev=INITIAL_ENERGY_EV,
        initial_prefactor_s_inv=INITIAL_PREFACTOR_S_INV,
        fit_baseline=False,
        max_nfev=MAX_NFEV,
    )
    return {
        "candidate": "free_order" if free else f"fixed_order_{order:g}",
        "reaction_order": float(result.reaction_order),
        "activation_energy_eV": float(result.activation_energy_eV),
        "prefactor_numeric_s_inv_convention": float(result.prefactor_s_inv),
        "normalized_rmse": float(result.normalized_rmse),
        "aicc": float(result.aicc),
        "success": bool(result.success),
        "jacobian_condition_number": float(result.jacobian_condition_number),
        "n_points": int(result.n_points),
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    source_root = Path(sys.argv[1]).expanduser().resolve()
    if not (source_root / "xls").is_dir():
        raise SystemExit(f"Expected source repository containing xls/: {source_root}")
    cases = []
    for source_index, (reference_ev, low_ev, high_ev) in LEADING_EDGE_REFERENCES.items():
        workbook_number = source_index + 1
        path = source_root / "xls" / f"tpd{workbook_number}.xls"
        if not path.is_file():
            raise SystemExit(f"Missing source spectrum: {path}")
        temperature_k, signal = read_spectrum(path)
        sheet = xlrd.open_workbook(str(path)).sheet_by_index(0)
        exposure_l = float(sheet.cell_value(0, 1))
        fits = [
            fit_case(temperature_k, signal, 1.0, False),
            fit_case(temperature_k, signal, 2.0, False),
            fit_case(temperature_k, signal, 1.0, True),
        ]
        cases.append({
            "source_spectrum_index": source_index,
            "source_workbook": path.name,
            "source_workbook_sha256": sha256(path),
            "exposure_L": exposure_l,
            "n_points": int(temperature_k.size),
            "temperature_min_K": float(temperature_k.min()),
            "temperature_max_K": 