# TPD Spectra Studio — User and Scientific Methods Manual

**Document status:** beta user and scientific manual · **Software source:** `main`, including merged PR #37 · **Current beta version:** 0.11.0b7 research-beta prerelease
**Audience:** experimental surface scientists, TPD/TDS users, students, and developers.  
**Scope:** current application behavior and defensible model assumptions. This is documentation, not a claim of experimental validation. Please open an issue for any discrepancy between this manual and the executable.

For the default three-stage desktop, follow the [workflow guide](redesign/WORKFLOW_USER_GUIDE.md).
Classic/batch controls described below remain available in **View → Classic / batch workspace**. File, Examples, View and Help menus keep less-frequent commands out of the analysis space.
The current beta opens a seeded noisy demo with a prepared region, provides visible
Monte Carlo progress/cancellation and adds [simultaneous component fitting](MULTICOMPONENT_FITTING.md).

## 1. Purpose and scope

TPD Spectra Studio provides a reproducible workflow for importing temperature-programmed desorption or thermal desorption spectroscopy (TPD/TDS) measurements, comparing measured traces, estimating apparent desorption parameters, performing model-dependent numerical fits, and exporting figures and diagnostics. It combines a Tkinter desktop GUI with a command-line interface and reusable Python analysis functions.

The principal motivation is to reduce repetitive manual plotting and fitting while keeping assumptions, data choices, and diagnostic warnings visible. It is **not** an automatic chemical-mechanism identifier. A visually excellent fit does not demonstrate that a single desorption process, a specific reaction order, or a particular adsorption-site population is physically unique.

### Features in the research beta

- CSV/TSV/TXT delimited-text import with preview, channel/unit confirmation and row checks; multiple-trace overlay and small-multiple views.
- Smoothing/normalization **for visual comparison** and selection of leading-edge / peak-search intervals.
- GUI temperature intervals set by sliders, exact numeric entry, or horizontal dragging (temperature-axis mode only).
- Heating-rate regression, leading-edge apparent activation energy, first-order Redhead estimate, signal-quality diagnostics.
- Optional one-state and two-state Polanyi–Wigner fitting and exploratory model comparison.
- Simultaneous 1–3 positive-order physical components in Modeling, with fixed
  per-component order/prefactor/coverage, joint energies/scales, optional shared
  offset/drift, individual curves, summed residuals, conditional uncertainty and exports.
- Batch output with settings/provenance and warnings.
- Numerical Jacobian rank, bounds, and conditioning warnings for the single-state fit.

**Not in this beta's default outputs:** experimentally validated nonlinear confidence intervals, coverage-calibration studies, nonlinear heating-ramp fitting, or automated mechanistic assignment. Some optional workflows provide model-conditional uncertainty ranges described below; none is validated for general experimental coverage.

## 2. Installation and launching

### Portable Windows application

1. Open [Windows beta builds](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml).
2. Choose the latest successful **main** run in the Windows desktop workflow.
3. Under **Artifacts**, download `tpd-spectra-windows-x64-beta-0.11.0b7`. GitHub sign-in may be required.
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

### Supported spectrum files

The desktop and CLI accept **CSV, TSV, and TXT files when they contain delimited text**. The importer recognizes common comma, semicolon, and tab separators and decimal comma/dot layouts. Excel workbooks (`.xls`/`.xlsx`), PDFs, images, and instrument-specific binary files are not spectrum inputs. Portable `.tpd.json` files store a Studio project; they are reopened as projects, not imported as raw spectra.

The original instrument exports contain a 29-row metadata block and typically use:

| Physical channel | Legacy column | Expected content |
| --- | --- | --- |
| Time | `ms` | Elapsed time in milliseconds |
| Signal | `DHTA+` | Detector signal in instrument-dependent arbitrary units |
| Temperature | `Temperatura` | Sample temperature in degrees Celsius |

The importer also recognizes common headers such as `Time`, `Signal`, and `Temperature`. The **Import preview** shows detected columns, separator, decimal mark, skipped metadata rows, and the first data rows. Confirm or change the time, signal, and temperature column mapping. Units explicitly named in headers may be suggested; generic headers require you to choose source time units (`ms`, `s`, or `min`) and temperature units (`degC` or `K`). A suggestion is not instrument metadata: verify units against the instrument export before continuing.

The preview reports total, accepted, and rejected rows, any time sorting, and temperature points adjusted by the cleaning heuristic. Rejected rows are excluded and their row numbers/reasons remain in the import report. Correct the mapping or units in the preview and inspect the sample rows before adding the data to the workspace. The source file is never rewritten.

Before import, preserve the raw file, document detector channel and background correction, and verify whether the temperature represents the sample rather than a heater setpoint. Prefer one measurement per file with monotonically increasing nominal ramp temperature. Files with damaged columns or insufficient usable points may be rejected.

### Loading spectra in the GUI

1. Choose **Import spectra** or **Add folder** on the toolbar. Folder import searches recursively for `.csv`, `.tsv`, and `.txt` files.
2. Review each file's detected layout and channel/unit choices. Choose **Import ready files** only after the row counts and sample values look correct.
3. In **Spectra & view**, confirm the file list, point counts, and visibility checkmarks.
4. Use **Show all**, **Hide all**, or **Remove** as appropriate; repeat imports should not intentionally duplicate the same path.
5. Select overlay or small multiples, temperature or time on the horizontal axis, and optional smoothing/normalization.

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

1. Import one or more delimited-text files and visually inspect the temperature ramp and signal shape.
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

For the current workflow, **Modeling → Fit 2 Peaks…** opens two rows with
clickable and numeric approximate positions. Verify the rate and explicitly
accept a source suggestion before using it (Zaki D₂O/Fe₃O₄: 3 K/s). Modeling
confirmation applies only to that dataset/region; Kinetic Analysis settings
remain separate. Published examples no longer silently set analysis rates.
New first-order rows use Redhead position-based energy guesses and ±30%
heuristic search bounds, not uncertainty limits. Advanced settings preserves
control of fixed orders/prefactors/coverages, energies, bounds and baseline.
**Fit Both Peaks** fits the full processed spectrum. Components differ in
color and line style; the complete sum includes the separately drawn baseline.
The residual is observation minus that sum. Read prominent baseline-only,
poor-fit or collapsed-component diagnostics even when the optimizer converges.
Temperature-informed multistart reduces initialization failures without
establishing a global optimum or a physical state count. The Zaki digitization
remains a model-limit stress test with correlated residuals, not energy truth.
See [the detailed workflow and numerical screens](MULTICOMPONENT_FITTING.md).

The two-state fit represents two independent populations with separate energies, prefactors and scales. Two fitted components do **not** prove two real adsorption sites. The Python API also includes a global fitting method for several nominally linear ramps with shared kinetic parameters and trace-specific signal scales/baselines. These models can be highly correlated and should be compared under consistent data and residual assumptions.

### 6.6 Model comparison and diagnostics

Outputs may include R², RMSE, normalized RMSE, AIC/AICc/BIC, Jacobian conditioning and flags for insufficiently constrained parameters. AIC/AICc/BIC comparisons should be interpreted only for fits to the same observations using compatible likelihood/error assumptions. Residual patterns, boundary solutions and parameter correlation can make nominal optimization success misleading.

The research beta includes singular-value-based **numerical identifiability warnings** for one-state fits. These are screening metrics, not confidence intervals and not proof of structural identifiability.

### 6.7 Which reported parameters have uncertainty estimates?

Uncertainty is method-specific; the program does **not** automatically calculate an uncertainty for every reported number. Fixed inputs and assumptions (for example, selected kinetic order, prefactor, coverage, heating rate, and component count) have no fitted uncertainty. Fit diagnostics such as a condition number are warnings, not parameter intervals.

| Method or result | What the program reports | What is not covered |
| --- | --- | --- |
| Leading-edge estimate | A 95% OLS interval for apparent energy | Regression scatter only; excludes baseline, window, calibration, correlated-noise, and model uncertainty |
| Redhead estimate | Energy plus sensitivity to prefactor divided/multiplied by ten | No statistical interval; prefactor is supplied |
| Ordinary one-state, two-state, and global nonlinear fits | Point estimates and fit/identifiability diagnostics | No parameter confidence intervals in standard reports |
| Zero-order fit | Profile-based energy estimate and conditional prefactor/scale brackets | Brackets are not statistical intervals; prefactor and scale are non-unique under normalized coverage |
| Optional Explorer Monte Carlo | Conditional 2.5th–97.5th percentile refit ranges for estimated energy, log-prefactor and signal scale; fitted baseline when enabled; free order for the fractional-order model | Fixed order has no order interval. Zero-order prefactor/scale ranges are withheld. Ranges require enough successful refits (100 by default), assume the selected reference and iid Gaussian noise, and are not experimentally coverage-calibrated |
| Simultaneous component fit | Conditional local-linear 95% intervals for fitted component energies and signal scales when diagnostics permit | Component order, prefactor and coverage are fixed. Shared baseline/drift terms do not get intervals. Intervals are withheld for diagnosed ambiguity and are not experimentally calibrated |

The Explorer Monte Carlo extension estimates intervals for every **free parameter it refits** in eligible positive-order models. These are conditional simulated-refit ranges, not a universal uncertainty calculation. No available method propagates all statistical, structural, calibration, heating-rate, preprocessing and model-selection uncertainty into every output parameter.

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

**Present in this `main` source:** broader synthetic benchmark matrices, statistical interval-coverage scripts, and an opt-in experimental nonlinear parametric-bootstrap API. The bootstrap API remains disconnected from routine desktop reports; its intervals are conditional and are not independent experimental validation. The repository source includes `docs/NONLINEAR_BOOTSTRAP_UNCERTAINTY.md` and `validation/experimental/EXPERIMENTAL_VALIDATION_AND_ALGORITHM_ASSESSMENT.md` for researchers using these tools.

A practical independent-validation dataset should span: zero-, first-, second- and non-integer order; overlapping states; multiple heating rates; baseline drift and noise; authentic instrument data. Record the originating DOI, figure, licensing status, extraction/digitization uncertainty, original axis units, preprocessing and reference method. Prefer raw author-provided data whenever obtainable.

**Suggested benchmark metrics:** fit success, activation-energy bias/RMSE, prefactor log error, peak temperature error, numerical mass balance, residual correlations, interval coverage (when intervals are issued), and interval withholding frequency. Do not cherry-pick failed runs out of denominators.

## 10. Reproducing example analyses

```bash
# Supported CLI options should always be confirmed for the checked-out version:
tpd-spectra --help

# Analyze a delimited-text spectrum and write results to a new folder:
python -m tpd_spectra path/to/spectrum.csv --output tpd-results

# Example with a generic tab-separated source in seconds and kelvin:
tpd-spectra path/to/spectrum.tsv --output tpd-results --delimiter tab --decimal . --skiprows 0 --time-column Time --signal-column Signal --temperature-column Temperature --time-unit s --temperature-unit K

# Explicitly request a first-order kinetic fit:
python -m tpd_spectra path/to/spectrum.csv --output tpd-results --kinetic-fit --kinetic-order 1

# Run the repository regression tests:
python -m pytest -q
```

The beta now ships a *curated, separately attributed* collection of nine
publication-derived spectra and the source numeric coordinates under
[`examples/publication_data/`](../examples/publication_data/README.md).
Most are figure digitizations (not original acquisition traces); the AgY D₂
dataset is sourced from a deposited numeric workbook. The import-ready view
retains original temperature and signal but, for figure extractions, constructs
an explicitly artificial time coordinate from the cited nominal ramp.
Neither source type is known-ground-truth kinetic validation. Rights remain
per-study Creative Commons licences, not the code's MIT licence; restricted,
unverified and CO-mismatched assets are not in the public bundle.
Review `ASSET-RIGHTS.md` before redistributing or repurposing any data.

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


## Explicit units and constant-ramp screening

The Python importer accepts explicit `time_column`, `signal_column`,
`temperature_column`, `time_unit`, and `temperature_unit` arguments.
The GUI provides the same column/unit choices in Import preview. CLI batch
users can pass `--time-column`, `--signal-column`, `--temperature-column`,
`--time-unit`, `--temperature-unit`, `--delimiter`, `--decimal`, and
`--skiprows`. Defaults remain ms/degC for backward compatibility; check the
import report and source metadata. Do not rely on magnitude-based unit guesses.

CLI kinetic fitting compares measured/cleaned temperatures with its anchored
constant-ramp coordinate. `--kinetic-ramp-tolerance-K` defaults to 2 K and must
be positive and finite. Fits exceeding the threshold are withheld with a warning.
Accepted fits export maximum/RMS deviation and the chosen tolerance. Two kelvin
is an engineering screen, not experimental uncertainty; justify the tolerance
for each experiment. Do not raise it just to force a fit to nonlinear ramps.

Source and Windows portable installs remain the documented full desktop routes.
Python wheels contain the computational modules and offline scientific Help;
repository-level example/tutorial sidecars are not all included in a wheel.

Publication preparation records, assessment protocols and the working manuscript
are maintained separately in the source repository.
