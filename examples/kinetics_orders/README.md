# Synthetic kinetic-order examples

These **seven artificial reference datasets** are generated from the Polanyi–Wigner desorption model. They are not experimental spectra and must not be used to validate scientific accuracy independently of the forward model. Their purpose is to help users learn the Explorer interface and test order discrimination.

## Open in TPD Spectra Studio

Import an individual CSV from this folder using **Import CSV files** (or import the folder). Open **Kinetics Explorer** from the toolbar. Choose the trace, use two clicks to select its peak, and enter a **heating rate of 1 K/s**. For full-peak fits, choose a range spanning most of the desorption feature, including its rising edge and trailing side. Compare zero, first, second and free fractional order. Clean files use a constant signal baseline of 2 (arbitrary units).

## File guide

| File | Synthetic scenario | True generating order(s) |
| --- | --- | --- |
| `01_zero_order_clean.csv` | Single-state zero-order, coverage-depletion edge | 0 |
| `02_first_order_clean.csv` | Single-state first-order | 1 |
| `03_second_order_clean.csv` | Single-state second-order | 2 |
| `04_fractional_order_0p5_clean.csv` | Single-state fractional order | 0.5 |
| `05_fractional_order_1p5_clean.csv` | Single-state fractional order | 1.5 |
| `06_first_order_with_noise_baseline.csv` | First-order with deterministic pseudo-noise and rising baseline | 1 |
| `07_two_overlapping_first_order_peaks.csv` | Two additive desorption states; single-state fitting is deliberately inappropriate | 1 + 1 |

## Generating assumptions

- All grids: temperature 80–360 °C in increments of 1 °C; 281 samples.
- Columns: `Time_ms` (0 to 280000 ms), `Temperature_C`, `Signal`. These are recognized by the existing instrument CSV importer.
- Heating rate: **1 K/s**; linear ramp.
- Normalized initial coverage: `theta(0) = 1` for each state.
- Forward law: `r = nu * theta^n * exp(-E/(k_B*T))`, `dtheta/dT = -r/beta`.
- Approximate forward solution: classical fourth-order Runge–Kutta with 0.1 K internal steps and coverage clipped to the physical non-negative region.
- Single-state examples: `E = 0.90 eV`, `nu = 1e10 s^-1` for normalized coverage, detector scale `1e5`, constant baseline `2`.
- Overlapping states: `E = 0.86 eV` and `0.98 eV`, each `nu = 1e10`, detector scales `6e4` and `8e4`, respectively.
- Noise/drift file: deterministic bounded trigonometric perturbation with nominal magnitude up to 1.2% of the largest kinetic signal and a linear additive baseline of `2 + 0.008 * index`. It is **not random Gaussian noise**.
- Signal is arbitrary detector units; kinetics are not calibrated to a physical surface coverage.

**Scientific limitations:** Many models fit similar trace shapes; successful fitting does not prove the mechanism. The synthetic generator is closely related to the fitted model, so high recovery accuracy on these files is an expected internal consistency check, not experimental validation. For the two-state spectrum, use a multi-state model and do not force a single order assignment. Clean numerical data have nearly zero noise, making Monte Carlo residual-noise estimation unreliable; use noisy experimental spectra for realistic uncertainty analysis.
