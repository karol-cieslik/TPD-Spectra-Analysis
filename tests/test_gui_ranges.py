import pytest
from tpd_spectra.gui_ranges import validate_temperature_window, window_from_drag


def test_reverse_drag_is_sorted():
    assert window_from_drag(250, 120) == (120.0, 250.0)


def test_drag_clips_to_supported_range():
    assert window_from_drag(-50, 800) == (0.0, 700.0)


def test_subdegree_manual_interval():
    assert validate_temperature_window("130.25", "170.75") == (130.25, 170.75)


@pytest.mark.parametrize("start,end", [(1, 1), (float("nan"), 100), (100, float("inf"))])
def test_invalid_drag_rejected(start, end):
    with pytest.raises(ValueError):
        window_from_drag(start, end)


@pytest.mark.parametrize("start,end", [(-1, 20), (100, 701), (200, 100)])
def test_invalid_manual_range_rejected(start, end):
    with pytest.raises(ValueError):
        validate_temperature_window(start, end)
