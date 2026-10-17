# TPD Spectra Analysis

A research prototype for processing temperature-programmed desorption / thermal desorption spectroscopy (TPD/TDS) data. It provides a modular Python analysis core, desktop interface, and command-line batch workflow.

## Status and scientific scope

The `tpd_spectra` package fixes known implementation defects (including the Redhead Celsius/Kelvin inconsistency, leading-edge x/y alignment, rolling-filter edge behavior, and portable output paths) and records analysis assumptions and fit diagnostics. Experimental spectra, the historical notebook, and figures are not included in this source repository.

**Important:** energies are model-dependent apparent estimates, not automatically validated intrinsic adsorption energies. The leading-edge calculation assumes signal is proportional to desorption rate and that the selected interval follows the stated zero-order-style relationship. The Redhead calculation is first-order and uses an assumed prefactor. Inspect spectra and fit intervals and validate assumptions for each experiment.

## Desktop GUI (Phase 7)

An optional desktop interface is available using Tkinter, which is included with many standard Python installations. It reuses the same analysis pipeline as the CLI and supports selecting a single CSV or a folder, choosing an output folder, setting classical analysis parameters, and optionally enabling single-state or exploratory two-state kinetic fits. Long analyses run in a worker thread so the interface remains responsive.

Run from the repository root:

```bash
python run_tpd_spectra_gui.py
# or, after installing the package:
tpd-spectra-gui
```

The GUI is a convenience layer, not a separate analysis implementation. Results and scientific caveats are the same as for the CLI. A standalone Windows GUI executable is built by the Windows release workflow; it has not been independently verified on a clean Windows machine in this development environment.

## Installation

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run your data

From the repository root:

```bash
python -m tpd_spectra path\to\your\csv-folder --output output
```

The defaults are intentionally visible and configurable: leading-edge interval 130–170 °C, second-peak search interval 230–400 °C, median smoothing over 10 points, linear heating fit from 125 to 700 °C restricted to the first 10 minutes, and a Redhead prefactor of `1e20 s^-1` (retained from the historical notebook, not claimed to be universal).

```bash
python -m tpd_spectra path\to\your\csv-folder \
  --leading-edge 130 170 \
  --redhead-region 230 400 \
  --prefactor 1e20 \
  --window 10 --filter median \
  --output output
```

Use `--max-time-min -1` to remove the 10-minute cutoff from the heating-rate fit. The CLI processes CSV files in sorted order and writes:

- `output/all_desorption_parameters.csv` — one row per successful spectrum, including units, fit range, R² diagnostics, smoothing configuration and assumed Redhead prefactor.
- `output/all_tds_spectra.png` — overlaid spectra.
- `output/analysis_errors.csv` — per-file errors, if any files fail.

Legacy input format: semicolon-delimited CSV with decimal commas, 29 metadata rows, and channels named `ms`, `DHTA+`, and `Temperatura`. The importer also recognizes common English alternatives for the signal and temperature columns. Bring your own CSV files; example experimental datasets are not distributed in this repository.

## Phase 1: scientific diagnostics and limitations

The batch workflow now exports additional diagnostics alongside the existing results:

- `leading_edge_residual_RMSE_ln_signal`, slope standard error, and a 95% confidence interval for the leading-edge energy derived from ordinary least-squares regression. The interval captures regression scatter only; it does **not** include systematic uncertainty, prefactor uncertainty, calibration uncertainty, baseline uncertainty, or model uncertainty.
- Redhead energies recalculated with the assumed prefactor divided and multiplied by ten, plus the corresponding per-decade sensitivity. These are sensitivity scenarios, not a probability interval.
- Signal screening metrics (negative-signal fraction, dynamic range, and a 10th-percentile low-signal proxy), and the fraction of temperature points changed by heuristic cleaning. The low-signal proxy is deliberately **not** treated as a baseline estimate and no automatic baseline correction is applied.
- `diagnostic_warnings` in the results table and `analysis_warnings.csv` for checks such as a low heating-rate/leading-edge R², a peak at the edge of its search interval, substantial temperature interpolation, or potentially problematic signal levels. Warnings are screening prompts, not automatic proof that a dataset or model is invalid.
- One PNG per input spectrum under `output/diagnostics/`, showing raw and smoothed signal, selected analysis intervals, the chosen peak maximum, and leading-edge regression residuals where enough positive data are available.

## Phase 3: reproducible batch projects and presets

The batch workflow now supports repeatable parameter sets and a machine-readable project record:

- `--preset standard` retains the default settings. `--preset broad-peak` widens the leading-edge and Redhead search intervals for exploratory review; `--preset unsmoothed` uses a one-point window and no filter. Presets are conveniences, not scientifically validated universal settings.
- `--config settings.json` loads analysis parameters from JSON. Explicit command-line options override loaded settings. `--save-config settings.json` saves the effective parameter values for reuse.
- `batch_summary.csv` provides the combined per-spectrum analysis table and includes numerical-fit fields when `--kinetic-fit` is enabled.
- `analysis_project.json` records software version, UTC creation time, effective parameters, each input file's absolute path, size and SHA-256 hash, success/failure lists, and output filenames. Hashes support checking input identity; they do not establish calibration or scientific validity.
- `analysis_errors.csv` and `analysis_warnings.csv` are refreshed on each run so files from an older run are not mistaken for current results.

Example:

```bash
python -m tpd_spectra C:/data/tpd --output results --preset standard \
  --kinetic-fit --kinetic-order fit --save-config results/settings.json

# Re-run with the saved parameters (command-line flags can still override them)
python -m tpd_spectra C:/data/tpd --output repeat-results --config results/settings.json
```

The diagnostic thresholds (for example R² < 0.98) are configurable review conventions in spirit, not universal scientific acceptance criteria. Inspect residual structure and experimental context; high R² alone does not establish kinetic-model validity. The leading-edge fit assumes signal is proportional to desorption rate and uses the implemented linearised relationship. The Redhead sensitivity calculation retains the first-order assumption.

## Tests

```bash
python -m pytest -q
```

The tests cover reproducible project manifests, JSON config precedence, synthetic Polanyi–Wigner simulation and parameter recovery as well as the Redhead Kelvin conversion, a synthetic leading-edge slope, matched temperature/signal masking, smoothing edge behavior, temperature cleaning, heating-rate regression, regression uncertainty diagnostics, screening metrics, and prefactor sensitivity. No experimental files are distributed; passing tests does not validate the physical model for a given experiment.

## Project layout

- `tpd_spectra/analysis.py` — import, cleaning, smoothing, heating-rate fit and classical kinetic estimates.
- `tpd_spectra/kinetics.py` — numerical Polanyi–Wigner simulation, single-state fit, exploratory two-state fit, and identifiability/model-comparison diagnostics.
- `tpd_spectra/cli.py` — batch command-line interface, parameter presets, project manifest and exports.
- `tests/` — automated regression tests, including independent numerical cross-checks.
- `.github/workflows/windows-release.yml` — Windows executable build and release workflow.
- Experimental spectra, the historical notebook, and images are excluded from this code repository.

## Method notes

The leading-edge regression fits `ln(signal)` against `1/T` with temperature converted from °C to K and calculates `E = -slope × k_B`. Its prefactor estimate is `beta × exp(intercept)`. The Redhead implementation calculates `E = k_B T_p [ln(nu T_p / beta) - 3.64]` with `T_p` in kelvin and both `nu` and heating rate `beta` in inverse seconds. Results depend on peak order, prefactor, calibration, baseline, selected fit region, signal-rate proportionality and overlapping desorption contributions.

## Citation and license

Citation metadata is provided in `CITATION.cff`; keep its version aligned with releases. The project source code authored for this repository is released under the MIT License; see `LICENSE`. Before publishing or accepting external contributions, confirm that you have the rights to license all code and review any employer, university, or collaborator ownership obligations.

**Important: the MIT license applies to project-authored software code only.** Experimental spectra, the historical notebook, schematic image, and thesis-derived or third-party material are omitted because they may have separate rights. See `ASSET-RIGHTS.md` before adding any of those assets.


## Phase 5: exploratory overlapping-state fits and model diagnostics

Phase 5 adds an optional two-state Polanyi–Wigner model for asking whether a sum of two independent desorption populations describes a trace better than a single state. Each state has its own activation energy, prefactor and signal scale; the two-state implementation shares reaction order and additive baseline. State energies are ordered to avoid simple label swapping. Use `--kinetic-model compare` to export single-state and two-state fits in `polanyi_wigner_fits.csv`, with a separate `*_two_state_fit.png` plot. `--kinetic-model two-state` also runs the single-state baseline so the results remain directly comparable. This option requires `--kinetic-fit`.

Example:

```bash
python -m tpd_spectra path\to\your\csv-folder --output output --kinetic-fit \
  --kinetic-model compare --kinetic-order 1
```

The two-state result includes AIC, AICc and BIC (only compare values fitted to the same trace and data points), the Jacobian condition number, component signal scales, and explicit warnings for ill-conditioning, weak components, close activation energies and large residuals. A lower information criterion can support relative model comparison; it does not establish that two microscopic states physically exist. Activation energies and prefactors can be highly correlated, and a second state can overfit noise, background drift, calibration effects or an unsuitable heating-ramp assumption. Review residuals and experiment context, and validate with multiple heating rates / coverage series where possible. The two-state model currently uses a fixed shared reaction order; if `--kinetic-order fit` is selected, the single-state model fits order but the two-state comparison remains fixed at first order, so that comparison is not strictly like-for-like.


## Phase 4: validation and Windows beta packaging

Phase 4 added an independent numerical validation script and a Windows build workflow.
The development-time reference check compared the first-order coverage solution against
an independently evaluated analytical integral. Experimental example files are not
distributed here, so that reference script is not included in this code-only repository.

Run validation locally:

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

### Build a standalone Windows beta

A Windows executable must be built on Windows (PyInstaller does not cross-compile a
Windows `.exe` from Linux). The workflow `.github/workflows/windows-release.yml` runs
on Windows, executes tests, builds `tpd-spectra.exe` and the desktop GUI executable, and
packages them with documentation and a quick-start note. Run it manually from the GitHub
Actions tab, or push a version tag such as `v0.6.0` to attach the ZIP to a GitHub Release.
The generated beta package can be used from PowerShell:

```powershell
.\tpd-spectra.exe C:\data\tpd --output results
.\tpd-spectra.exe C:\data\tpd --output results --kinetic-fit --kinetic-order 1
```

### Validation scope and limitations

- The first-order closed-form cross-check is independent of the ODE integration routine,
  but it validates only that mathematical case and the implemented rate law.
- The development archive includes nine spectra used as integration examples; they are not certified reference data. Confirm redistribution rights before publishing them.
- A converged kinetic fit is not proof of a unique mechanism; activation energy and
  prefactor can be strongly correlated. Inspect warnings, residuals, assumptions, and
  calibration before interpreting fitted parameters.
- The project archive supplied for this update had no license file. Add and review an
  explicit software/data license before public redistribution; the workflow includes a
  distribution note rather than assuming a license on the author's behalf.

## Phase 6: global multi-heating-rate fitting and noise-recovery benchmark

Phase 6 adds `fit_global_polanyi_wigner()` for jointly fitting two or more traces
collected at different heating rates. Activation energy and prefactor are shared
between traces; each trace has its own signal scale and optional constant baseline.
Residuals are normalised by each trace's signal range so detector amplitude does not
alone determine the fit. The result reports per-trace RMSE, normalised RMSE and R²,
plus an approximate covariance-derived correlation between activation energy and
`log10(prefactor)`, Jacobian conditioning, information criteria and warnings.

This global fit is currently an API-level feature rather than a CLI option. Example:

```python
from tpd_spectra.kinetics import fit_global_polanyi_wigner

traces = [
    {"temperature_c": temperature_1, "signal": signal_1, "beta_k_s": 0.5},
    {"temperature_c": temperature_2, "signal": signal_2, "beta_k_s": 1.5},
    {"temperature_c": temperature_3, "signal": signal_3, "beta_k_s": 4.0},
]
fit, predictions = fit_global_polanyi_wigner(
    traces, reaction_order=1.0, initial_energy_ev=1.0,
    initial_prefactor_s_inv=1e13,
)
print(fit.as_dict())
```

All temperatures must be strictly increasing for each trace and beta is the
heating rate in K/s. Use spectra measured at genuinely distinct heating rates with
consistent chemistry and acquisition calibration. The shared-kinetics assumption
can fail if coverage, surface preparation, readsorption, instrument response or the
adsorbate population differs between runs. Different heating rates help constrain
kinetics but do not guarantee uniqueness; inspect energy–prefactor correlation,
condition number, residuals and warnings.

Run the synthetic noise-recovery benchmark with:

```bash
python scripts/phase6_validation.py
```

It writes `output/phase6_validation/global_fit_noise_recovery.csv` and
`summary.json`, testing a known single-state model across 0%, 1%, 3% and 5% noise
(relative to each trace's signal range) and three heating rates. These are synthetic
recovery checks only, not proof that the model describes any particular experiment.
The uncertainty/correlation calculation is a local linear approximation and may be
misleading for strongly nonlinear or ill-conditioned fits.


## Phase 7: desktop interface and release metadata

- Added an optional Tkinter GUI for choosing input/output paths and configuring the existing classical and numerical batch-analysis options. The GUI delegates to the CLI analysis pipeline rather than duplicating the scientific calculations.
- Added unit-tested translation/validation of GUI settings into CLI arguments. The GUI runs analysis in a worker thread and streams status messages into the run log.
- Added `tpd-spectra-gui` entry point, a standalone GUI build step in the Windows workflow, `CITATION.cff`, and a conservative public-release checklist.
- The Windows workflow packages both command-line and GUI executables. A release artifact must still be smoke-tested on a clean Windows machine before being treated as a supported binary.
- No software license was selected automatically; ownership and redistribution rights must be reviewed before public release.
