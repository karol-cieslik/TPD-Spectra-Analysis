"""Generate a noiseless, baseline-free two-population first-order TPD demo.

Independent quadrature of theta(T) = theta0 exp(-integral(k(T)/beta dT));
does not call the application's ODE simulator or fitting implementation.
Run from the repository root: python scripts/generate_demo.py
"""
from pathlib import Path
import json

import numpy as np
from scipy.constants import Boltzmann, elementary_charge
from scipy.integrate import cumulative_trapezoid


def generate(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    beta = 1.0
    populations = [
        {"energy_eV": 1.25, "prefactor_s_inv": 1e13, "initial_coverage": 1.0},
        {"energy_eV": 1.55, "prefactor_s_inv": 1e13, "initial_coverage": 0.65},
    ]
    dense_c = np.linspace(70.0, 370.0, 30001)  # 0.01 K integration grid
    temperature_c = dense_c[::50]  # 0.5 K / 0.5 s export sampling
    signal = np.zeros(temperature_c.size)
    for population in populations:
        k = population["prefactor_s_inv"] * np.exp(
            -population["energy_eV"] / ((Boltzmann / elementary_charge) * (dense_c + 273.15)))
        theta = population["initial_coverage"] * np.exp(
            -cumulative_trapezoid(k / beta, dense_c, initial=0))
        rate = (k * theta)[::50]
        signal += rate
        population["component_peak_C"] = float(temperature_c[np.argmax(rate)])
    time_ms = (temperature_c - temperature_c[0]) / beta * 1000.0
    np.savetxt(output / "synthetic_two_peak_demo.csv",
               np.column_stack((time_ms, signal, temperature_c)), delimiter=",",
               header="Time_ms,Signal,Temperature", comments="", fmt=["%.0f", "%.12e", "%.2f"])
    metadata = {
        "synthetic": True, "model": "two independent first-order Polanyi-Wigner populations",
        "beta_K_s": beta, "temperature_unit": "degC", "time_unit": "ms",
        "signal_unit": "arbitrary units, numerically total initial-population coverage/s",
        "baseline": 0.0, "noise": "none", "points": int(signal.size),
        "integration_step_K": 0.01, "sampling_step_K": 0.5,
        "populations": populations,
        "limitations": "No interactions, readsorption, transport effects, or instrument response. "
                        "Not experimental evidence or a test of unique parameter identifiability.",
    }
    (output / "synthetic_two_peak_demo.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "examples")
