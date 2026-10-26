# Synthetic two-peak TPD examples

**Generated observations, not experimental measurements.** The default
`synthetic_two_peak_demo.csv` now includes reproducible detector noise with a
standard deviation of **2% of the maximum clean signal**. It retains the same
two physical first-order populations and 601-point temperature ramp.

## Try the complete default workflow

1. Extract the full beta ZIP and open `TPD-Spectra-Studio.exe`. The bundled
   default opens with **Demo — first peak (single-state approximation)**
   selected over 70–210 °C.
2. Switch to **Modeling & Order Identification**. The full measured trace stays
   visible; the named interval selects the first component for single-state
   exploration. Confirm **1 K/s** and an initial energy of **1.25 eV**.
3. For a short first test, select only **First** order and turn off
   **Multistart**. Click **Compare models**. Inspect the residuals as well as
   the fitted curve. A single-state fit of both peaks is inappropriate.
4. Set **Monte Carlo replicates** to **20**, keep seed **42**, and click
   **Run Monte Carlo**. Progress and cancellation are shown beside the
   controls. This short demonstration intentionally withholds parameter
   intervals: at least 100 successful refits are required for those ranges.
5. Select the converged candidate row and click **Use selected model in
   Kinetic Analysis**, then calculate the explicit fit. Save the project or
   an analysis run and export its report from Kinetic Analysis.

The separate **Open Example Dataset** chooser retains the clean isolated
first-order reference for a first check of method equations. It also offers
low-, moderate- and high-noise first-order examples and noisy overlap examples.

## Observation variants and exact reference

| File suffix after `synthetic_two_peak_demo` | Detector standard deviation / clean maximum | Baseline |
| --- | --- | --- |
| `.csv` (default), `_moderate_noise.csv` | 2% | Zero |
| `_clean.csv` | Zero | Zero |
| `_low_noise.csv` | 1% | Zero |
| `_high_noise.csv` | 5% | Zero |
| `_baseline_drift.csv` | 2% | 2.5% offset, plus 0.015% of clean maximum per kelvin |

All variants use seed **20261026**. The same Gaussian draw is scaled between
noise levels to make controlled comparisons possible. Noise is additive iid
Gaussian detector noise applied **after** the clean kinetic calculation.
Negative background-subtracted observations are retained; clipping would bias
the noise model. The baseline reference is 70 °C. This is a pedagogical detector
model, not a claim that real detector noise is Gaussian or independent.

Each CSV has adjacent JSON metadata recording physical truth, noise and
baseline parameters, seed, units, clean-reference filename and SHA256 hashes.
`synthetic_two_peak_demo_clean.csv` preserves the former noiseless numerical
reference. Existing tests of exact rates, integrated coverage and peak count use
that file; import, default workflow and export tests use the noisy default.
The clean physical validation thresholds have not been relaxed.

## Model and reference inputs

Two independent first-order Polanyi–Wigner populations obey
`r_i = nu_i theta_i exp(-E_i/(k_B T))` and `dtheta_i/dt = -r_i`.
The clean signal is `r_1 + r_2`; Kelvin is used in the rate law.

| Input | Value |
| --- | --- |
| Heating rate | 1 K/s, strictly linear |
| Temperature | 70–370 °C, 0.5 °C per sample |
| Sampling | 0–300000 ms, every 500 ms (601 rows) |
| Activation energies | 1.25 eV and 1.55 eV |
| Prefactors | 1e13 s⁻¹ for each population |
| Initial coverages | 1.0 and 0.65, independent normalized populations |
| Clean component maxima | 172.5 °C and 276.0 °C |

Columns are `Time_ms`, `Signal` and `Temperature` (°C). The imported ramp
requires zero corrected temperatures. The **clean** time integral is
approximately 1.65 in the chosen coverage units. Noise changes observed maxima
and integrated signals. In particular, logarithmic leading-edge regression
becomes biased or unstable when the tail signal is comparable with detector
noise; use the clean reference to check numerical equations and inspect the
chosen interval on noisy observations.

Regenerate with `python scripts/generate_demo.py`. The clean first-order
solution uses independent quadrature on a 0.01 K grid, then samples every 0.5 K;
it does not call the application's ODE solver. The detector-effects helper is
shared with `scripts/generate_beta_examples.py`. The latter preserves the
existing clean and noisy beta reference files and appends additional variants.

## Scientific limits

These examples omit readsorption, interactions, mass transport and instrument
response. Known generating parameters verify numerical behavior under the
stated assumptions; they do not establish unique parameter identifiability or
experimental validity. Baseline drift and correlated noise violate the basic
constant-baseline/iid-noise uncertainty assumptions. The leading-edge result is
an apparent slope; Redhead assumes a prefactor and first-order kinetics.
Numerical agreement does not establish a physical mechanism.

These newly authored examples and generators are distributed under the
repository's MIT license. No rights to unrelated experimental data are implied.
