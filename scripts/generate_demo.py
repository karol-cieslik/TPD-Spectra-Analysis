"""Generate physical two-population TPD references and seeded observations.

Independent quadrature of theta(T) = theta0 exp(-integral(k(T)/beta dT));
does not call the application's ODE simulator or fitting implementation.
Run from the repository root: python scripts/generate_demo.py
"""
from pathlib import Path
import json
import hashlib

import numpy as np
from scipy.constants import Boltzmann, elementary_charge
from scipy.integrate import cumulative_trapezoid

try:  # Support both module imports and ``python scripts/generate_demo.py``.
    from .generate_beta_examples import add_observation_effects
except ImportError:
    from generate_beta_examples import add_observation_effects

SEED = 20261026
VARIANTS = {
    'clean': (0., 0., 0.),
    'low_noise': (.01, 0., 0.),
    'moderate_noise': (.02, 0., 0.),
    'high_noise': (.05, 0., 0.),
    'baseline_drift': (.02, .025, .00015),
}


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
    metadata = {
        "schema_version": 2, "synthetic": True, "experimental": False,
        "model": "two independent first-order Polanyi-Wigner populations",
        "beta_K_s": beta, "temperature_unit": "degC", "time_unit": "ms",
        "signal_unit": "arbitrary units, numerically total initial-population coverage/s",
        "points": int(signal.size),
        "integration_step_K": 0.01, "sampling_step_K": 0.5,
        "populations": populations,
        "limitations": "Additive detector noise is simulated after the clean kinetic calculation. "
                        "No interactions, readsorption, transport effects, or instrument response. "
                        "Not experimental evidence or a test of unique parameter identifiability.",
    }
    clean_path=output/'synthetic_two_peak_demo_clean.csv'
    for name,(noise_fraction,offset,slope) in VARIANTS.items():
        observed,noise,baseline=add_observation_effects(signal,temperature_c,seed=SEED,
            noise_fraction=noise_fraction,offset_fraction=offset,slope_fraction_per_K=slope)
        stem='synthetic_two_peak_demo_'+name
        csv=output/(stem+'.csv')
        with csv.open('w',encoding='utf-8',newline='') as handle:
            np.savetxt(handle,np.column_stack((time_ms,observed,temperature_c)),delimiter=',',
                header='Time_ms,Signal,Temperature',comments='',fmt=['%.0f','%.12e','%.2f'],newline='\n')
        meta=dict(metadata,observational_variant=name,noise=noise,baseline=baseline,
            noise_fraction_of_clean_maximum=noise_fraction,random_seed=SEED,
            clean_reference_file=clean_path.name,
            clean_reference_sha256=hashlib.sha256(clean_path.read_bytes()).hexdigest(),
            csv_sha256=hashlib.sha256(csv.read_bytes()).hexdigest())
        (output/(stem+'.json')).write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')
        if name=='moderate_noise':
            # The first-run filename remains stable and contains the 2% variant.
            (output/'synthetic_two_peak_demo.csv').write_bytes(csv.read_bytes())
            (output/'synthetic_two_peak_demo.json').write_text(
                json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "examples")
