"""Exercise shipped data and parser/cleaner failures seen in the Windows beta."""
from pathlib import Path
import json

import numpy as np
import pandas as pd
import pytest
from scipy.integrate import trapezoid
from scipy.signal import find_peaks

from tpd_spectra.analysis import clean_temperature, heating_rate, load_spectrum, redhead_energy

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


@pytest.mark.parametrize("sep,decimal,metadata", [
    (",", ".", 0), (";", ".", 0), (";", ",", 0), ("\t", ".", 0),
    (";", ",", 29), (";", ".", 29),
])
def test_header_layout_and_decimal_are_validated_before_accepting(tmp_path, sep, decimal, metadata):
    # More than 29 rows catches a false header inferred from the 29th data row.
    expected = pd.DataFrame({"Time_ms": np.arange(60) * 2000,
                             "Signal": np.linspace(.012345, .034567, 60),
                             "Temperature": 70.25 + np.arange(60) * 2})
    path = tmp_path / "ramp.csv"
    path.write_text("metadata\n" * metadata + expected.to_csv(index=False, sep=sep, decimal=decimal),
                    encoding="utf-8")
    spectrum = load_spectrum(path)
    np.testing.assert_allclose(spectrum.time_min, expected.Time_ms / 60000)
    np.testing.assert_allclose(spectrum.signal, expected.Signal)
    np.testing.assert_array_equal(spectrum.temperature_clean_c, expected.Temperature)
    assert spectrum.points_temperature_corrected == 0


def test_explicit_column_typo_is_not_silently_ignored():
    with pytest.raises(ValueError, match="Requested signal column"):
        load_spectrum(EXAMPLES / "synthetic_two_peak_demo.csv", signal_column="missing")


@pytest.mark.parametrize("step", [.2, 1.5, 2., 5.])
def test_cleaner_preserves_regular_heating_ramps(step):
    temp = 70 + np.arange(100) * step
    np.testing.assert_array_equal(clean_temperature(temp), temp)


@pytest.mark.parametrize("offset", [-20., 20.])
def test_cleaner_corrects_only_isolated_spike_on_coarse_ramp(offset):
    temp = 70 + np.arange(20) * 2.
    raw = temp.copy()
    raw[8] += offset
    np.testing.assert_allclose(clean_temperature(raw), temp)
    assert raw[8] == temp[8] + offset  # caller's raw data retained


def test_cleaner_interpolates_in_time_and_retains_irregular_ramp():
    time = np.array([0., 1., 3., 8., 9., 10.])
    temp = 70 + time
    np.testing.assert_array_equal(clean_temperature(temp, time=time), temp)
    raw = temp.copy()
    raw[2] += 40
    np.testing.assert_allclose(clean_temperature(raw, time=time), temp)


def test_cleaner_invalid_bounds_and_insufficient_anchors():
    np.testing.assert_allclose(clean_temperature([np.nan, 100, 101, 900]), [100, 100, 101, 101])
    with pytest.raises(ValueError, match="expected °C"):
        clean_temperature([900, 901, -300])
    with pytest.raises(ValueError, match="strictly increasing"):
        clean_temperature([100, 101, 102], time=[0, 0, 1])


def test_shipped_demo_import_and_independent_physical_reference():
    from tpd_spectra.kinetics import simulate_tpd
    # Keep deterministic numerical validation separate from noisy observations.
    spectrum = load_spectrum(EXAMPLES / "synthetic_two_peak_demo_clean.csv")
    meta = json.loads((EXAMPLES / "synthetic_two_peak_demo_clean.json").read_text())
    assert meta["synthetic"] is True
    assert len(spectrum.signal) == meta["points"] == 601
    assert spectrum.temperature_c[[0, -1]].tolist() == [70., 370.]
    np.testing.assert_array_equal(spectrum.temperature_c, spectrum.temperature_clean_c)
    assert spectrum.points_temperature_corrected == 0
    beta, r2, _ = heating_rate(spectrum.time_min, spectrum.temperature_clean_c)
    assert beta == pytest.approx(1., abs=1e-12)
    assert r2 == pytest.approx(1.)
    reference = np.zeros_like(spectrum.signal)
    for pop in meta["populations"]:
        _, rate = simulate_tpd(spectrum.temperature_c, beta, pop["energy_eV"],
                               pop["prefactor_s_inv"], 1., pop["initial_coverage"])
        reference += rate
        # Redhead is approximate, even for an isolated first-order population.
        assert redhead_energy(pop["component_peak_C"], pop["prefactor_s_inv"], beta) == pytest.approx(
            pop["energy_eV"], rel=.02)
    np.testing.assert_allclose(spectrum.signal, reference, rtol=3e-4, atol=2e-8)
    assert trapezoid(spectrum.signal, spectrum.time_min * 60) == pytest.approx(1.65, rel=1e-4)
    peaks, _ = find_peaks(spectrum.signal, prominence=.003)
    assert len(peaks) == 2


def test_shipped_demo_completes_documented_analysis_and_exports(tmp_path):
    from tpd_spectra.cli import main
    assert main([str(EXAMPLES / "synthetic_two_peak_demo.csv"), "--output", str(tmp_path),
                 "--leading-edge", "110", "140", "--redhead-region", "150", "210",
                 "--prefactor", "1e13", "--filter", "none"]) == 0
    rows = pd.read_csv(tmp_path / "all_desorption_parameters.csv")
    assert len(rows) == 1
    assert rows.loc[0, "redhead_energy_eV"] == pytest.approx(1.25, rel=.02)
    assert (tmp_path / "all_tds_spectra.png").stat().st_size > 1000
    assert (tmp_path / "analysis_project.json").is_file()
    assert list((tmp_path / "diagnostics").glob("*.png"))
    assert not (tmp_path / "analysis_errors.csv").exists()
