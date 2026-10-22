"""Headless validation of the GUI peak-selection data boundary."""
import numpy as np
import pytest

from tpd_spectra.explorer_gui import select_peak_window


def test_peak_window_extracts_only_requested_interval():
    temp = np.arange(50.0, 150.0)
    signal = np.exp(-0.5 * ((temp - 100) / 15) ** 2)
    x, y = select_peak_window(temp, signal, 80, 120)
    assert len(x) == 41
    assert x[0] == 80
    assert x[-1] == 120
    assert np.array_equal(y, signal[30:71])


def test_peak_window_rejects_too_short_region():
    temp = np.arange(50.0, 150.0)
    with pytest.raises(ValueError, match="12"):
        select_peak_window(temp, np.sin(temp), 90, 94)


def test_peak_window_rejects_nonmonotonic_region():
    temp = np.array([*range(50, 100), 75, *range(101, 150)], dtype=float)
    with pytest.raises(ValueError, match="strictly"):
        select_peak_window(temp, np.sin(temp), 50, 149)
