# Synthetic two-peak TPD demo

**Generated data, not an experimental measurement.** This project-authored
example is distributed under the repository's MIT license. It replaces the
earlier 151-row Gaussian illustration, which failed the legacy temperature
cleaner. The CSV, model metadata, and this guide are bundled in new beta builds.

## Try it in the desktop app

1. Extract the beta ZIP. Open `TPD-Spectra-Studio.exe`.
2. Select **Import CSV files**, then `examples/synthetic_two_peak_demo.csv`.
   Expect **601 points**, two resolved peaks, and no import warning.
3. In **Spectra & view**, set smoothing to **none** for this noiseless demo.
4. In **Analysis settings**, set leading edge to **110–140 °C**, peak search
   to **150–210 °C**, and Redhead prefactor to **1e13 s⁻¹**. These windows
   describe the first peak. Leave optional kinetic fitting off for this run.
5. Choose a results folder and click **Run full analysis**. Review the CSV
   tables, comparison PNG, diagnostic plot, and `analysis_project.json`.
   **Export plot PNG** separately saves the current preview.

Command-line equivalent:

```bash
python -m tpd_spectra examples/synthetic_two_peak_demo.csv --output demo-results --leading-edge 110 140 --redhead-region 150 210 --prefactor 1e13 --filter none
```

## Model and reference inputs

Two independent first-order Polanyi–Wigner populations, with
`r_i = nu_i theta_i exp(-E_i/(k_B T))` and `dtheta_i/dt = -r_i`.
The signal is `r_1 + r_2`. Kelvin is used in the rate law.

| Input | Value |
| --- | --- |
| Heating rate | 1 K/s, strictly linear |
| Temperature | 70–370 °C, 0.5 °C per sample |
| Sampling | 0–300000 ms, every 500 ms (601 rows) |
| Activation energies | 1.25 eV and 1.55 eV |
| Prefactors | 1e13 s⁻¹ for each population |
| Initial coverages | 1.0 and 0.65, independent normalized populations |
| Baseline / noise | Zero / none |
| Component peak temperatures on the export grid | 172.5 °C and 276.0 °C |

Columns are `Time_ms` (milliseconds), `Signal` (arbitrary units, proportional
to summed coverage loss per second), and `Temperature` (°C).
The imported ramp should be unchanged: **zero corrected temperatures**.
Heating-rate regression should give 1 K/s. Integrated signal over time is
approximately 1.65 in the chosen coverage units. With the stated first-peak
window and prefactor, the approximate Redhead energy is within 2% of 1.25 eV.

Reproduce with `python scripts/generate_demo.py`. The generator evaluates the
first-order integrated solution by trapezoidal quadrature on a 0.01 K grid,
then samples every 0.5 K. It does not call the application's ODE solver.
`synthetic_two_peak_demo.json` records the inputs. Regression tests compare
the CSV against the independent ODE implementation and check import, signal
area, two peaks, heating rate, GUI drawing, and analysis exports.

## Scientific limits

This idealized simulation excludes interactions, readsorption, mass transport,
instrument response, drift, and noise. It tests software behavior under known
assumptions; it does not validate an experimental mechanism or uncertainty.
The leading-edge result is an apparent slope over the chosen interval, and
Redhead is an approximation with an assumed prefactor. A single-state fit of
both peaks is inappropriate. Two-state fitting remains exploratory; numerical
agreement alone does not establish unique parameter recovery.
