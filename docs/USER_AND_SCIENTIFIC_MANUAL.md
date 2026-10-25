# TPD Spectra Studio — User and Scientific Methods Manual

**Document status:** beta user and scientific manual · **Software source:** `main` · **Current beta version:** 0.11.0b3 (not yet tagged as a public release)
**Audience:** experimental surface scientists, TPD/TDS users, students, and developers.  
**Scope:** current application behavior and defensible model assumptions. This is documentation, not a claim of experimental validation. Please open an issue for any discrepancy between this manual and the executable.

## 1. Purpose and scope

TPD Spectra Studio provides a reproducible workflow for importing temperature-programmed desorption or thermal desorption spectroscopy (TPD/TDS) measurements, comparing measured traces, estimating apparent desorption parameters, performing model-dependent numerical fits, and exporting figures and diagnostics. It combines a Tkinter desktop GUI with a command-line interface and reusable Python analysis functions.

The principal motivation is to reduce repetitive manual plotting and fitting while keeping assumptions, data choices, and diagnostic warnings visible. It is **not** an automatic chemical-mechanism identifier. A visually excellent fit does not demonstrate that a single desorption process, a specific reaction order, or a particular adsorption-site population is physically unique.

### Features in the beta candidate

- CSV import, multiple-trace overlay and small-multiple views; hide/remove traces.
- Smoothing/normalization **for visual comparison** and selection of leading-edge / peak-search intervals.
- GUI temperature intervals set by sliders, exact numeric entry, or horizontal dragging (temperature-axis mode only).
- Heating-rate regression, leading-edge apparent activation energy, first-order Redhead estimate, signal-quality diagnostics.
- Optional one-state and two-state Polanyi–Wigner fitting and exploratory model comparison.
- Batch output with settings/provenance and warnings.
- Numerical Jacobian rank, bounds, and conditioning warnings for the single-state fit.

**Not in this beta's default outputs:** validated nonlinear confidence intervals, coverage-calibration studies, independent digitized literature benchmarks, nonlinear heating-ramp fitting, automated mechanistic assignment. These belong to separate research/development work.

## 2. Installation and launching

### Portable Windows application

1. Open [Windows beta builds](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml).
2. Choose the latest **successful** build on `main`.
3. Under **Artifacts**, download `tpd-spectra-windows-x64-beta-0.11.0b3`. GitHub sign-in may be required.
4. Extract the archive completely, then launch `TPD-Spectra-Studio.exe`. No separate Python installation should be required.
5. Keep the package contents together, including licenses and documentation. The executable is not digitally signed; verify its GitHub origin and follow your institution's software policy.

A GitHub Actions green check confirms CI and packaging steps, **not** successful execution on every Windows machine. Confirm launch, imports, fits and export locally before distributing to colleagues.

### Developer / Python installation

Requirements: Python 3.10+, NumPy, pandas, SciPy, Matplotlib; Tkinter must be present for the GUI.

```bash
git clone https://github.com/karol-cieslik/TPD-Spectra-Analysis.git
cd TPD-Spectra-Analysis
git checkout main
python -m pip install -e .
python run_tpd_spectra_gui.py
```

For tests, install `requirements-build.txt` and run `python -m pytest -q`. The console command `tpd-spectra --help` lists supported options. On Windows, source/installation procedures may depend on PowerShell and the selected Python environment.

## 3. Preparing and importing measurements

### Expected CSV formats

The original instrument exports contain a 29-row metadata block and typically use:

| Physical channel | Legacy column | Expected content |
| --- | --- | --- |
| Time | `ms` | Elapsed time in milliseconds |
| Signal | `DHTA+` | Detector signal in instrument-dependent arbitrary units |
| Temperature | `Temperatura` | Sample temperature in degrees Celsius |

The importer also attempts conventional CSV headers (`Time`, `Signal`, `Temperature`, etc.), semicolon/comma/tab separators, and decimal comma/dot conventions. **Check the detected channels and units manually.** Time expressed in seconds but labeled `ms` can produce a wrong heating rate; detection does not substitute for instrument metadata.

Before import, preserve the raw file, document detector channel and background correction, and verify whether the temperature represents the sample rather than a heater setpoint. Prefer one measurement per CSV with monotonically increasing nominal ramp temperature. Files with damaged columns or insufficient usable points may be rejected.

### Loading spectra in the GUI

1. Choose **Import CSV files** or **Add folder** on the toolbar.
2. In **Spectra & view**, confirm the file list, point counts, and visibility checkmarks.
3. Use **Show all**, **Hide all**, or **Remove** as appropriate; repeat imports should not intentionally duplicate the same path.
4. Select overlay or small multiples, temperature or time on the horizontal axis, and optional smoothing/normalization.

The visual comparison settings are not all identical to the batch analysis settings. In particular, normalization is intended to compare shapes and must not be interpreted as changing measured detector calibration.

### Suggested first datasets

Start with one familiar, well-behaved experimental spectrum and the [documented synthetic demo](../examples/README.md). Keep first tests small. Do not redistribute your own or another author's experimental spectra without verifying permissions.

Temperature cleaning is a screening heuristic, not calibration. It retains
steady ramps even when adjacent samples differ by more than 1.5 °C. Interior
spikes must show an upward/downward reversal exceeding the 1.5/0.5 °C thresholds;
the stronger excursion is corrected while its recovery neighbor is retained.
Nonfinite temperatures, values at or below absolute zero, and values above
800 °C are invalid. Corrections interpolate on elapsed time; invalid endpoints
use the nearest valid value. Fewer than two valid anchors cause an error.
Finite endpoint jumps, sustained steps, and genuine ramp changes remain for
user review. Inspect the raw/cleaned temperatures and correction fraction;
these rules cannot identify every sensor fault or distinguish all real reversals.

## 4. Graph exploration and fit-window selection

Use the plot navigation toolbar for zooming, panning and view reset. The **Analysis settings** tab contains leading-edge and peak-search windows.

- **Leading edge:** the temperature interval used for a regression of `ln(signal)` against reciprocal absolute temperature. Choose an interval where the intended physical approximation applies, not simply where the straight-line fit has maximum R².
- **Peak-search region:** the interval within which the desorption maximum is found for the Redhead-style estimate. If the maximum lies at a boundary, widen the region or reconsider which feature is being measured.
- **Exact entry:** type increasing lower/upper temperatures in °C; fractional-degree values are permitted.
- **Plot selection:** switch to the **Temperature** X axis; turn off toolbar pan/zoom; select **Select leading edge on plot** or **Select peak interval on plot**, then drag horizontally.

Shaded bands are *analysis-window guides*, not baseline estimates. After adjusting boundaries, check exported settings and diagnostics. For overlapping peaks, a single peak maximum and a single leading edge can be physically ambiguous.

## 5. Standard analysis workflow

1. Import one or more CSV files and visually inspect the temperature ramp and signal shape.
2. Select a plausible heating-rate fit region and time limit; exclude holds, ramps with changing slopes, or obvious temperature artifacts where possible.
3. Set a leading-edge interval and peak-search interval.
4. Choose a smoothing method/window conservatively. Smoothing can shift peak maxima, change fitted slopes and introduce artificial structures; record the chosen settings.
5. Enter the assumed Redhead prefactor and optional kinetic-model settings only when the assumptions are defensible.
6. Choose a results directory; use **Run full analysis**.
7. Review tables, diagnostic plots, messages, fit residuals and method limitations before reporting parameters.
8. Rerun with alternative windows/prefactors as a sensitivity check when scientific conclusions depend on the result.

## 6. Physical model and calculations

### 6.1 Heating rate

For a nominally linear heating ramp, the heating rate is `beta = dT/dt`, expressed in K s⁻¹. Temperature differences in kelvin and Celsius are equal, but **absolute temperatures in Arrhenius factors must be kelvin**: `T_K = T_°C + 273.15`. If the ramp is in °C min⁻¹, divide by 60 to obtain K s⁻¹. A fitted straight ramp, its R² and chosen interval are diagnostic; ramp nonlinearity is not automatically modeled in the kinetic integration.

### 6.2 Leading-edge approximation

In a selected, positive-signal leading-edge region, the program fits

```text
ln(S) = a + b / T_K
E_app = -b * k_B
```

where `S` is signal (assumed proportional to desorption rate), `k_B` is Boltzmann's constant in eV K⁻¹, and `E_app` is an apparent energy in eV. The slope-derived estimate requires a region with an approximately constant effective population and applicable kinetic assumptions. In heterogeneous or coverage-dependent systems it can be an apparent, window-dependent quantity rather than a unique barrier.

The software calculates conventional ordinary least-squares residual statistics and a slope-based 95% confidence interval transformed into energy units. **This interval reflects regression scatter only** and excludes uncertainty in baseline, heating-rate calibration, temperature, choice of window, correlated errors and kinetic model.

### 6.3 First-order Redhead-style estimate

With `T_p` the peak temperature in kelvin, prefactor `nu` in s⁻¹, and `beta` in K s⁻¹:

```text
E_R = k_B * T_p * [ ln(nu * T_p / beta) - 3.64 ]
```

This is the implemented **first-order** approximation with the conventional constant 3.64; it is not a universal formula for zero- or second-order reactions. It is sensitive to the supplied prefactor, peak assignment, peak overlap, baseline and ramp conditions. The report includes estimates for prefactor divided/multiplied by ten to illustrate sensitivity.

### 6.4 Polanyi–Wigner numerical fitting

The modeled desorption rate is

```text
r(T, theta) = nu * theta^n * exp[-E / (k_B * T)]
d(theta)/dT = -r / beta
```

where `theta` is a normalized adsorbed population, `n` the selected kinetic order, `E` an activation energy, and `nu` a rate coefficient. Numerical integration uses a strictly increasing temperature grid and constant positive heating rate (SciPy `solve_ivp`, LSODA).

The detector model applies an optimized signal scaling factor and optionally a constant baseline. Parameters are obtained using bounded nonlinear least squares; logarithmic parameterization is used for the prefactor and signal scale. Reaction order is fixed by default, or may be fitted under bounded optimization in the Python fitting API.

**Units caveat:** for general coverage expressed in physical rather than dimensionless units, the kinetic coefficient's dimensions depend on reaction order. The present implementation uses normalized dimensionless coverage, with `s⁻¹` as a computational convention. It must not be mistaken for a universally dimensioned physical pre-exponential factor for arbitrary order.

### 6.5 Multiple populations and multiple heating rates

The two-state fit represents two independent populations with separate energies, prefactors and scales. Two fitted components do **not** prove two real adsorption sites. The Python API also includes a global fitting method for several nominally linear ramps with shared kinetic parameters and trace-specific signal scales/baselines. These models can be highly correlated and should be compared under consistent data and residual assumptions.

### 6.6 Model comparison and diagnostics

Outputs may include R², RMSE, normalized RMSE, AIC/AICc/BIC, Jacobian conditioning and flags for insufficiently constrained parameters. AIC/AICc/BIC comparisons should be interpreted only for fits to the same observations using compatible likelihood/error assumptions. Residual patterns, boundary solutions and parameter correlation can make nominal optimization success misleading.

The beta candidate includes singular-value-based **numerical identifiability warnings** for one-state fits. These are screening metrics, not confidence intervals and not proof of structural identifiability.

## 7. Outputs and reproducibility

A complete batch run may produce:

| Artifact | Use |
| --- | --- |
| `all_desorption_parameters.csv` | Classical per-spectrum apparent estimates, fit-window settings and diagnostics |
| `batch_summary.csv` | Combined batch and optional kinetic fit results |
| `all_tds_spectra.png` | Comparison of spectra |
| `diagnostics/*_diagnostics.png` | Per-spectrum plots for inspection |
| `analysis_warnings.csv`, `analysis_errors.csv` | File-level flags and failures, when present |
| `analysis_project.json` | Software version, effective parameters, input file identities and SHA-256 hashes |

The **Export plot PNG** button saves the current view as a 300 dpi image, independent of a complete batch analysis.

For a publishable study preserve: unchanged raw inputs, source/instrument metadata, ramp calibration, all settings, complete warnings, fitted model/order, software commit/version, numerical outputs, and scripts used for figure preparation. Do not label a smoothed or normalized visualization as raw data.

## 8. Interpretation guidance and failure modes

| Symptom | Likely issue / next step |
| --- | --- |
| Missing/incorrect curves | Verify column headers, separators, units, and the visible-trace flags |
| Negative signal values | Inspect detector offset and experimental baseline before log-regression |
| Leading-edge fit unavailable | Check that the interval contains at least five positive, finite signal points |
| Poor heating-rate linearity | Reassess ramp fitting region; avoid interpreting a nonlinear ramp under constant-beta kinetics |
| Peak exactly at search boundary | Adjust peak-search window or identify which feature is being evaluated |
| Strongly varying energy across windows | Report sensitivity and reconsider the assumed leading-edge regime |
| Optimizer converges but warnings remain | Inspect bounds, condition number and residuals; do not claim uniquely recovered parameters |
| Overlapping peaks | Compare simpler/complex models cautiously; do not infer a site count from components alone |

## 9. Validation strategy and current evidence

**Verified in source and CI:** test suite covers file-import handling using synthetic public fixtures, selected kinetic integration and parameter-recovery cases, GUI structure/range logic, and identifiability diagnostics. The integrated beta build is checked through GitHub Actions; personal Windows acceptance testing is still necessary.

**In a separate scientific research branch (not automatically part of this beta):** broader synthetic benchmark matrices, statistical interval coverage scripts, and an experimental nonlinear parametric-bootstrap API. Those results are not independent experimental validation and should not be cited as such until experiments, artifacts and interpretation are reviewed.

A practical independent-validation dataset should span: zero-, first-, second- and non-integer order; overlapping states; multiple heating rates; baseline drift and noise; authentic instrument data. Record the originating DOI, figure, licensing status, extraction/digitization uncertainty, original axis units, preprocessing and reference method. Prefer raw author-provided data whenever obtainable.

**Suggested benchmark metrics:** fit success, activation-energy bias/RMSE, prefactor log error, peak temperature error, numerical mass balance, residual correlations, interval coverage (when intervals are issued), and interval withholding frequency. Do not cherry-pick failed runs out of denominators.

## 10. Reproducing example analyses

```bash
# Supported CLI options should always be confirmed for the checked-out version:
tpd-spectra --help

# Analyze a CSV and write results to a new folder:
python -m tpd_spectra path/to/spectrum.csv --output tpd-results

# Explicitly request a first-order kinetic fit:
python -m tpd_spectra path/to/spectrum.csv --output tpd-results --kinetic-fit --kinetic-order 1

# Run the repository regression tests:
python -m pytest -q
```

The beta bundle deliberately includes no experimental sample spectra. Review `ASSET-RIGHTS.md` before distributing examples. Data from open-access papers can carry different figure licensing and attribution requirements; record and comply with each specific license.

## 11. Known limitations and release boundary

- Beta-stage Windows GUI; screen scaling, standalone launch, and UI interaction require hands-on testing.
- Constant-heating-rate numerical model and normalized coverage convention.
- Signal calibration and temperature uncertainty not propagated into standard energy estimates.
- No automatic deconvolution or physically verified mechanistic classification.
- Baseline handling is limited; effects of drift and correlated residuals need further work.
- Full experimental evidence supporting uncertainty calibration is not yet established.
- Software results must be verified against raw spectra and independent scientific knowledge.

See `docs/BETA_ACCEPTANCE_CHECKLIST.md` for release checks. Users should report reproducible issues with file format, screen/window state, exact operations, expected and observed outcomes, and software version; share measurement data only when permitted.

## 12. How this manual maps to a future JOSS paper

The user manual is intentionally more detailed than a JOSS article. A paper should **summarize** the independently verifiable contribution, not simply reproduce usage instructions:

| Manuscript section | Evidence to develop from this manual |
| --- | --- |
| Summary | Section 1: problem, audience, purpose, and scope |
| Statement of need | Section 1 plus documented comparison to existing workflows/tools, with properly cited literature |
| Software design | Sections 2–4 and architecture details supported by source code |
| Scientific methods | Section 6 equations, assumptions and numerical implementation |
| Validation and limitations | Sections 8–11 plus archived numerical and external experimental benchmark results |
| Availability | Versioned source, tagged release/DOI, license, installation and reproducible example |
| References | Primary desorption-method papers, TPD methods literature and relevant software citations |

**Do not turn this into a paper prematurely:** fill in a comparison to existing software, actual benchmark figures, experimental provenance, public-use evidence, contributor acknowledgments, and checked bibliographic citations first. Publishing claims must reflect the tested tagged commit, not a development branch.

## 13. Contributors and maintenance

Project repository: [TPD-Spectra-Analysis](https://github.com/karol-cieslik/TPD-Spectra-Analysis). Citation details: `CITATION.cff`. Scope of code license: `LICENSE` and `ASSET-RIGHTS.md`. Please submit reproducible issues and suggested improvements through GitHub. The manuscript author list and affiliations are separate from code contribution history and must be confirmed with the relevant researchers.


## Reviewed runs and experimental Explorer (0.11.0b3 beta)

Show and Include are independent. Run full analysis opens review with import reports and raw/processed setup previews. Confirm the included inputs, assumed prefactor and a new output folder; Compute selected preview runs one spectrum without final saved output. Run and save starts the reviewed snapshot with live log/cancel and opens results/warnings afterward. Reruns use different folders. Closing during execution cancels and waits for the child.

The leading-edge intercept is exported separately; a physical prefactor is unavailable for arbitrary-unit detector signal. The legacy prefactor field is empty/NaN to prevent interpretation as a calibrated rate constant. Kinetic information criteria now count estimated noise variance. Prior rankings can therefore change.

The [Explorer guide](EXPLORER_MONTE_CARLO.md) covers four-order comparison and explicitly experimental seeded Monte Carlo. Conditional refit percentile ranges are not coverage-validated confidence limits. See [method status](METHOD_STATUS.md) for the current scientific scope.
