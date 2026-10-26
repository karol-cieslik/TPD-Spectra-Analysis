"""Synthetic CSV inputs for public tests; no experimental measurements required."""
import numpy as np
import pytest
import sys
import tkinter as tk


@pytest.fixture
def root():
    """Fresh real interpreter; drain/cancel callbacks before destroying it."""
    try:
        value = tk.Tk()
    except tk.TclError:
        if sys.platform == "win32":
            raise
        pytest.skip("Tk display unavailable")
    # Tk scaling is process-wide on Windows, even across destroyed roots.
    # High-DPI tests must not alter subsequent tests' native display settings.
    original_scaling=value.tk.call('tk','scaling')
    yield value
    value.update_idletasks()
    for callback in value.tk.call("after", "info"):
        value.after_cancel(callback)
    value.tk.call('tk','scaling',original_scaling)
    value.destroy()


@pytest.fixture
def example_spectra(tmp_path):
    """Create nine deterministic traces in the legacy instrument CSV format."""
    folder = tmp_path / "input"
    folder.mkdir()
    paths = []
    temp = np.linspace(120.0, 680.0, 701)
    time_ms = np.linspace(0.0, 600000.0, temp.size)
    for idx in range(9):
        peak = 290.0 + 5.0 * idx
        # Positive synthetic rising edge and resolved peak, baseline-free.
        signal = (0.05 + np.exp(-0.5 * ((temp - peak) / 38.0) ** 2)
                  + 0.2 * np.exp(-0.5 * ((temp - 155.0) / 32.0) ** 2))
        path = folder / f"synthetic_{idx:02d}.csv"
        with path.open("w", encoding="utf-8") as handle:
            for _ in range(29):
                handle.write("instrument metadata\n")
            handle.write("ms;DHTA+;Temperatura\n")
            for t, y, c in zip(time_ms, signal, temp):
                handle.write(f"{t:.3f};{y:.8f};{c:.4f}\n")
        paths.append(path)
    return paths
