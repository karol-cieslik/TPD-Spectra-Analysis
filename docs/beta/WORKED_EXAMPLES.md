# TPD Spectra Studio

**Practical Quick Start and worked examples**  
**External beta candidate | updated 1 November 2026**  
Dr. Karol Cieślik

> **Research beta 0.11.0b7.** Current source is `main`, including merged PRs #19–21 and the Results, Help and guided exercises. Confirm the exact build in `VERSION.json`. Human Windows visual/DPI acceptance, independent installation without Python and experimental validation remain incomplete. The exercises here use synthetic data; the separately labeled publication-derived examples are not known-ground-truth validation.

## Start here: your first result in five minutes

1. Use the newly supplied `tpd-spectra-windows-x64-beta-0.11.0b7` ZIP. Check `VERSION.json` for the exact source commit and `SHA256SUMS.txt` for the executable checksum. Get the latest successful **main** run from [Windows beta builds](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml?query=branch%3Amain). Extract **the entire archive** into a writable folder; leave `docs` and `examples` beside the executable. No tagged prerelease has been published; Actions artifacts expire and may require GitHub sign-in.
2. Double-click **TPD-Spectra-Studio.exe**. No Python installation is needed. This development executable is unsigned: follow your institution's software-security policy.
3. Click **Browse examples…**, choose **first order single peak**, then **Open selected spectrum**. This loads 801 simulated points from 50 to 450 °C, with an already selected full-trace interval and a heating rate of 1 K/s.
4. Go to **Kinetic Analysis** and select **Redhead**. Check **Heating rate = 1 K/s** and **Assumed prefactor = 1e13 s⁻¹**. An energy estimate should appear after the preview updates; if needed click **Calculate / Fit selected peak**.
5. In the updated interface, open **Parameter summary** to find the estimate with its units and scientific role; use **Spectrum & residuals** to inspect the plotted signal. The expected Redhead estimate is **approximately 1.2 eV, within 2.5% of the synthetic input**. This is an approximate first-order estimate, not an independently measured activation energy or confidence interval.
6. Click **Save labeled result...**, enter a descriptive run name, then **Report / Export...**. Select the saved run, click **Choose destination and generate report...**, choose a new folder, and inspect the PDF and associated CSV/JSON/figure files.

**You have now completed one useful analysis.** To preserve the data, intervals, settings and results for another session, use **Save project...** to create a `.tpd.json` project file.




## Exploring cited publication-derived examples

Open **Examples → Publication-derived spectra…**. Inspect the citation, DOI,
specific figure, original signal units, licence and limitations before loading.
The 9 curated spectra span five figure-digitized study groups and one deposited
numeric record (including four 2-propanol exposure traces). Most source
temperatures are in kelvin and are explicitly converted to °C. The figure
versions use an *artificial nominal-ramp time coordinate* for importer
compatibility; it must not be treated as measured acquisition time. The
deposited AgY D₂ data retain their measured time but violate a single constant
ramp over the full trace. Read [publication example provenance](../../examples/publication_data/README.md)
for usage limits. Figure fits are model-conditioned explorations, not recovered
physical truth.

## Using Help inside the program

Use **Help → Scientific Help / Parameters** or **Help → Quick start** from the compact menu. It opens an offline searchable reference covering 40 topics. Focus a **?** button next to a field to read its definition, unit, whether it is assumed or fitted, a numerical example and scientific limitations. Start with **Monte Carlo seed**, **Replicates** and **Activation energy** if those terms are unfamiliar. Help does not change any inputs or run calculations.

## Understand the three-stage workspace

The normal desktop workflow uses three connected stages. The selected dataset and named peak stay associated with subsequent calculations.

| Stage | What to do | What to check before continuing |
|:---|:---|:---|
| **Spectra & Preparation** | Open/import data; inspect units, cleaning, baseline and named peak intervals | Correct spectrum, temperature range and peak selection |
| **Modeling & Order Identification** | Simulate a physical hypothesis, compare candidate orders, optionally run Monte Carlo or fit overlapping components | Heating rate, starting assumptions, residuals and warnings |
| **Kinetic Analysis** | Perform an explicit analysis on a selected region; save and export a labeled result | Method assumptions, fitted versus assumed quantities and current/stale status |

**Four distinct operations:**

- **Simulate parameters** plots the prediction from values you enter. It does **not** recover those parameters from the data.
- **Compare models** optimizes candidate single-state kinetic models and compares their fits for the selected peak interval.
- **Run Monte Carlo** perturbs a fitted reference with assumed Gaussian noise and refits selected candidates. It is not microscopic kinetic Monte Carlo or Bayesian MCMC.
- **Calculate / Fit selected peak** performs the chosen Kinetic Analysis method. Transferring a model from Modeling supplies a starting hypothesis; it does not replace this explicit calculation.

You can inspect a curve that visually fits well and still have an underdetermined kinetic model. Always review **Spectrum & residuals**, **Parameters & models** and **Assumptions & warnings**, not merely the energy value.

### How to select a peak

1. In **Spectra & Preparation**, inspect the complete signal and confirm the correct dataset in the selector.
2. Enter a short peak name plus the **From** and **To** temperatures in °C. Click **Add peak**. To change an existing interval, select it, adjust its bounds and use **Update peak**.
3. Alternatively enable **Drag interval**, with the plot's pan/zoom modes off, and drag the interval handles. Save the selected bounds with **Add peak** or **Update peak**.
4. Check both sides of the selected feature. A one-peak method needs enough onset and high-temperature tail to describe the chosen population; the named interval alone does not separate overlapping contributions.

The default two-peak demonstration begins with **Demo - first peak (single-state approximation)** selected from **70 to 210 °C**. Its raw noisy trace remains visible even when you change stages or cancel a calculation.




## Exercise 1: one peak, two simple kinetic methods

**Purpose:** Learn where a parameter comes from, where it appears and how to save it.

**Dataset:** **Browse examples…** → **first order single peak**. Source truth: first order, (E=1.2 eV), (ν=10^{13} s⁻¹), (β=1 K/s), normalized initial coverage 1, no noise or baseline. All 801 points cover 50-450 °C.

### A. First-order Redhead estimate

1. Confirm the full-trace peak interval is selected.
2. In **Kinetic Analysis**, choose **Redhead**.
3. Confirm `Heating rate (K/s)` = `1` and `Assumed prefactor (s⁻¹)` = `1e13`.
4. Inspect the estimated energy and the original spectrum. If no estimate has appeared, click **Calculate / Fit selected peak**.
5. Save it as `Tutorial A - Redhead - clean first order` via **Save labeled result...**.

**Check:** An estimate near **1.2 eV** is expected (the reference guide allows 2.5% deviation). Redhead requires an *assumed* prefactor and first-order kinetics. It is a useful approximate check, not a fitted determination of the prefactor.

### B. Leading-edge estimate

1. Keep the same dataset and switch to **Leading edge**.
2. Use the **90 to 110 °C** leading-edge interval and inspect the transformation and residuals.
3. Save the result under a different label, such as `Tutorial A - leading edge`.

**Check:** The apparent energy should also be around **1.2 eV** on the clean generated example. A leading-edge fit assumes that coverage has changed little over the selected rising segment. Do not use the whole desorption peak as a leading edge. Its intercept does not identify an absolute physical prefactor.

### Export and inspect the parameters

1. Click **Report / Export...** in Kinetic Analysis.
2. Select one or both labeled runs; use Ctrl/Shift if you want multiple rows.
3. Click **Choose destination and generate report...** and select a folder.
4. Open the generated PDF and parameter CSV. Compare method, energy, assumed values, units, interval, source and warnings.

**If you cannot find a result:** Check that **Kinetic Analysis** still has the intended dataset, named peak and method selected. A result from another peak or earlier settings may be marked **STALE**; re-run the current analysis rather than interpreting it as a fresh fit.


## Exercise 2: simulation, model comparison and Monte Carlo

**Purpose:** Complete the default first-run workflow without silently treating two peaks as one state.

**Dataset:** `synthetic_two_peak_demo.csv`, automatically opened at startup. It contains two generated first-order populations, (E_1=1.25 eV) and (E_2=1.55 eV), with a 1 K/s ramp, 601 points over 70-370 °C, and seeded 2% iid Gaussian detector noise. The initial region is 70-210 °C, a **single-state approximation to the first peak only**.

### A. Explore a manually chosen hypothesis

1. Go to **Modeling & Order Identification** and verify that the dataset and **Demo - first peak** region remain selected.
2. Enter `Heating rate = 1`, `Initial energy = 1.25`, `Initial prefactor = 1e13`, `Simulation order = 1`, and `Simulation initial coverage = 1`.
3. Leave the amplitude/baseline as editable detector-signal choices; they can change the vertical comparison without changing the kinetic energy. Click **Simulate parameters**.
4. Inspect the simulated curve against the noisy observations. This is an overlay from *input* values, not an optimized fit.

### B. Compare a candidate order

1. Enable only the **First** order candidate; deselect Zero, Second and Fractional for this introductory check.
2. Turn **Multistart** off and click **Compare models**.
3. Open **Parameters & models**. Identify the converged first-order row, then inspect **Spectrum & residuals** and **Assumptions & warnings**.
4. Select the converged row and click **Use selected model in Kinetic Analysis**.
5. In **Kinetic Analysis**, review the transferred hypothesis and click **Calculate / Fit selected peak**. Save the result under a descriptive label.

**Check:** The raw two-peak spectrum must stay visible. The fitted single-state prediction applies only to the selected first-peak interval. Its residuals and warning messages matter more than visually matching the complete two-feature signal.

### C. Run a short Monte Carlo software check

1. Return to Modeling. A **current completed comparison** must exist for the same settings; otherwise compare again.
2. Set **Monte Carlo replicates = 20** and **Monte Carlo seed = 42**. Keep First order only and Multistart off for this introductory exercise.
3. Click **Run Monte Carlo**. Watch the completed/total count, percent, elapsed/estimated time and failure summary. The window should remain responsive; **Cancel** is available.
4. Inspect the final summary, the number of successful/failed fits, the rank count and any withheld intervals.

**Important:** A seed is the initial state of the pseudo-random number generator. Using the same seed and settings reproduces the random sequence in the same computational environment. It is **not** a fitted TPD parameter. Twenty replicates are only a workflow demonstration; this implementation withholds parameter ranges below **100 successful refits**. Even ranges from 500 refits are conditional on the assumed reference model and iid Gaussian noise - they are not validated experimental confidence intervals. A previously recorded 500-run test took about three minutes on one Windows environment; your machine may differ.


## Exercise 3: fit three overlapping populations together

**Purpose:** Learn the difference between selecting a named peak and decomposing a complete overlapping spectrum.

**Dataset:** **Browse examples…** → **three overlapping peaks**. It is a clean, synthetic 801-point trace between 50 and 450 °C. Its generating model has three independent additive first-order populations with the inputs below. A moderate-noise variant is also available for a harder test.



1. In **Modeling & Order Identification**, click **Overlapping components...**.
2. Define **three component rows**. Use the following trial inputs for this truth-informed numerical exercise:

| Component | Fixed order | Fixed prefactor | Fixed initial coverage | Initial energy | Energy bounds |
|:---|---:|---:|---:|---:|:---|
| 1 | 1 | `1e13 s⁻¹` | 1.0 | 1.185 eV | 1.14-1.22 eV |
| 2 | 1 | `1e13 s⁻¹` | 0.7 | 1.265 eV | 1.22-1.30 eV |
| 3 | 1 | `1e13 s⁻¹` | 0.5 | 1.345 eV | 1.30-1.38 eV |

3. Confirm **Heating rate = 1 K/s**, turn Multistart off and use **Maximum evaluations = 300** in Modeling. For this clean reference the generating baseline is zero; do not add an arbitrary drift term.
4. Click **Fit components together**. The energies and nonnegative detector scales are optimized jointly against the **whole selected dataset**, regardless of the named single-peak navigation region.
5. In **Spectrum & residuals**, inspect each fitted component, their sum, the observations and the observation-minus-sum residuals.
6. In **Parameters & models**, compare estimated energies with the generating values **1.18, 1.26, 1.34 eV**. Inspect scales and any withheld local uncertainty intervals.
7. Optionally click **Compare component counts**. This compares the first 1, 2 and 3 defined component hypotheses. Inspect errors, convergence and the relevant fixed assumptions; AICc/BIC results are **heuristics**, not probabilities of physical state counts.
8. Click **Export component fit...** and choose a destination for component parameters, curves, residuals, provenance and figures. Save the project if you want to restore this configuration.

**Interpretation:** Here the order, prefactor and coverage are *fixed*; only energy, nonnegative signal scale and optional common baseline parameters are fitted. The example has known generating truth and deliberately helpful initial guesses/bounds, so it tests numerical consistency, not blind identification. Actual overlapping TPD signals may involve readsorption, interactions, exchange, coverage-dependent energies or instrument response. Three visible shoulders do **not** establish three physical states. This beta does not offer multicomponent Monte Carlo or multicomponent zero-order depletion fitting.


## Exercise 4: noise, baselines and what uncertainty does not tell you

Open **first order single peak** and compare it with **first order low noise**, **first order moderate noise** and **first order high noise**. The deliberately generated standard deviations are 0%, 1%, 2% and 5% of the clean peak maximum. Each adjacent JSON records the seed and generating truth. For the default two-peak example there are also clean, noisy and baseline-drift variants.

1. Observe how the points become less smooth while the underlying physical inputs stay constant.
2. Compare a candidate model and inspect residuals, especially around the low-signal tails.
3. Run a short seeded Monte Carlo check, then consider more replicates if you are studying numerical stability.
4. Repeat after loading a drift example and ask whether a constant-baseline, iid-noise model still describes the residuals.

**Do not interpret every reported interval as a calibrated confidence interval.** The current Monte Carlo algorithm simulates independent Gaussian perturbations around a fitted reference and refits the specified candidates. It does not account for unknown order, incorrect model structure, correlated drift, temperature calibration or instrument response. Ranking frequency is not the probability that a mechanism is physically true.

### Bring your own spectrum

When you are comfortable with the synthetic examples:

1. Use **Open Spectrum...** and select your CSV. The documented example convention is `Time_ms, Signal, Temperature` (temperature in °C). Inspect the import report and verify how your file's columns and units were interpreted.
2. Confirm the heating program from the experiment, not from the default 1 K/s example assumption. The standard kinetic calculations assume a positive constant linear heating rate.
3. In **Spectra & Preparation**, select a useful physically motivated interval. If necessary preview smoothing/baseline corrections, then explicitly use **Apply smoothing / baseline to analysis**. Display normalization alone does not alter fitted signal values.
4. Choose a method suitable for your experimental question. Save the project and results with metadata and any warnings.

Do not send unpublished or third-party data to anyone without permission. **Report a Bug / Send Feedback** creates a reviewable diagnostic report; it does not automatically attach your spectral files or send anything. Analysis projects and full reports, unlike diagnostic ZIPs, can contain scientific data.


## Parameters at a glance

| Display term | Meaning | What the program does with it |
|:---|:---|:---|
| **Heating rate** \(β\) (K/s) | Rate of temperature increase; verify from experiment | Supplied physical input, not inferred from a fit |
| **Energy** \(E\) (eV) | Activation/desorption barrier in chosen model | Simulation input, fit initialization or fitted output depending on action |
| **Prefactor** \(ν\) (s⁻¹) | Kinetic attempt frequency under normalized-coverage convention | Assumed for Redhead/components; initial guess or fitted/conditional quantity in other methods |
| **Order** \(n\) | Exponent of normalized coverage | Can be fixed or selected/fitted according to method; not proof of mechanism |
| **Initial coverage** \(\theta_0\) | Dimensionless normalized population at first included temperature | Supplied for simulation/components; may be normalized to 1 for single-state fitting |
| **Signal scale** \(A\) | Conversion from calculated rate to detector signal | Optimized in full fits; may absorb unknown detection sensitivity |
| **Baseline / drift** | Constant signal offset and optional linear trend | Selected/fitted as specified; cannot repair every instrument artifact |
| **Multistart** | Tries several starting guesses in optimization | Can reduce sensitivity to initialization, not guarantee global optimum |
| **Maximum evaluations** | Budget for a numerical optimization | Not the number of Monte Carlo replicates |
| **Seed** | Starting state for reproducible pseudo-random draws | Does not change the physical kinetic model |
| **Replicates** | Number of noisy datasets refitted | More usually costs more time; ranges require at least 100 successful refits here |
| **RMSE / residual** | Size/pattern of observation-minus-prediction error | Quality diagnostics; a small value is not mechanism proof |
| **AICc / BIC** | Criteria for comparing fitted candidate descriptions | Heuristic rankings under stated assumptions, not mechanism probabilities |
| **Stale result** | Stored result no longer corresponds to current settings | Preserved for inspection; recalculate for current inputs |

For the actual Polanyi-Wigner independent-population model, the code uses temperature in Kelvin internally:

\[
r_i(T)=ν_i\theta_i(T)^{n_i}\exp\left(-\frac{E_i}{k_B T}\right),\qquad
\frac{d\theta_i}{dT}=-\frac{r_i(T)}{β}.
\]

In a simultaneous fit, the detected signal is a sum of independent rates multiplied by detector scales, plus a shared baseline. Not every physical process can be represented this way.

## If something goes wrong

| Symptom | First check |
|:---|:---|
| The program does not open | Did you extract the **complete** ZIP? Check Windows/institution security policy; this beta is unsigned. |
| Modeling shows no useful fit | Confirm a dataset and named peak region; verify candidate selection; inspect **Assumptions & warnings**. |
| **Run Monte Carlo** is unavailable | Complete a model comparison for the **current** settings first; let another running job finish or cancel. |
| No Monte Carlo parameter intervals appear | Fewer than 100 successful refits, failed fits, or numerical/identifiability restrictions can suppress them. |
| The first peak fit does not explain both peaks | The default region is a single-state approximation. Use **Overlapping components...** for a justified joint hypothesis. |
| Parameters appear different after switching methods | Check the selected dataset, named peak, method and **STALE** status; previous sessions retain their original snapshots. |
| Dragging a region does nothing | Turn off the plot toolbar's pan/zoom mode, enable **Drag interval**, and save with Add/Update peak. |
| Your exported report is missing | Select and label a completed run, choose a new destination, and check export status; do not assume the preview is the rendered PDF. |
| You want to report a bug | Use **Report a Bug / Send Feedback**; inspect the diagnostic text/ZIP before sharing. No spectra are automatically attached. |

### Scientific and compatibility scope

The beta is for informal evaluation, teaching-style demonstrations and exploratory research. Independent experimental benchmarks, uncertainty-coverage studies and external scientific review remain necessary before quantitative method claims or publication. Read [`docs/MULTICOMPONENT_FITTING.md`](../MULTICOMPONENT_FITTING.md) and [`docs/METHOD_STATUS.md`](../METHOD_STATUS.md) before interpreting advanced fits.

**Feedback:** In the program choose **Report a Bug / Send Feedback**, or email **Dr. Karol Cieślik** at **karol.j.cieslik@gmail.com**. State the version/build, chosen example, what you expected and what happened. A screenshot helps, but check it for confidential data first. No account or experimental dataset is required to send useful comments.

**Source:** [github.com/karol-cieslik/TPD-Spectra-Analysis](https://github.com/karol-cieslik/TPD-Spectra-Analysis). Code is MIT licensed; see the repository's `LICENSE` and `ASSET-RIGHTS.md`.

---

*Tutorial instructions and synthetic truth are covered by source and frozen-package checks. Human first-run, visual/DPI and clean-machine acceptance of the exact final ZIP remain necessary before external distribution.*
