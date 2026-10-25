<div align="center">

<img src="tpd_spectra/assets/studio-mark.svg" width="88" height="88" alt="TPD Spectra Studio spectrum mark">

# TPD Spectra Studio

**An open-source desktop application for exploring and analyzing temperature-programmed desorption spectra.**

Built for surface-science researchers who need transparent fitting methods, reproducible results, and a practical workflow from measurement to figure.

[![Windows beta build](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml/badge.svg?branch=release%2Fexternal-beta-v0.11.0b3)](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-2f855a.svg)](LICENSE)
[![Windows desktop](https://img.shields.io/badge/Desktop-Windows-0078D4?logo=windows&logoColor=white)](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions)
[![Development status](https://img.shields.io/badge/status-beta%20review%20candidate-f59e0b)](https://github.com/karol-cieslik/TPD-Spectra-Analysis/tree/release/external-beta-v0.11.0b3)

[**Download beta**](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml) · [**Quick start**](#-quick-start) · [**User manual**](docs/USER_AND_SCIENTIFIC_MANUAL.md) · [**Scientific methods**](#-scientific-methods-and-limitations) · [**Contributing**](CONTRIBUTING.md)

</div>

---

## External beta 0.11.0b3 - review candidate

Start with [START_HERE](START_HERE.md), the [four-page Quick Start](docs/beta/QUICK_START.pdf)
and the [16 documented synthetic examples](examples/beta_collection/README.md).
Use the successful build for branch **release/external-beta-v0.11.0b3**, artifact
**tpd-spectra-windows-x64-external-beta-0.11.0b3**. This is a separate review
candidate; prior beta downloads remain available. No prerelease is published.

**Zero-order update:** a dedicated depletion-edge fitter replaces the local
zero-order optimization. It passes the original clean-reference residual limit
and reports conditional prefactor/scale ranges rather than a unique pair. Actual GUI screenshots and human display-scaling review
are still pending after native capture failed. See [release notes](docs/beta/RELEASE_NOTES.md)
and [verification record](docs/beta/PREPARATION.md) for the exact scope.

Feedback requires no GitHub account: use **Report a Bug / Send Feedback**, inspect
the report, then copy it or save the diagnostic ZIP. Email **Dr. Karol Cieślik** at
**karol.j.cieslik@gmail.com**. Nothing is sent automatically; no spectra are
attached. Contributions and forks are welcome under the code's MIT license.
Try the [informal colleague checklist](docs/beta/TESTER_CHECKLIST.md).

## Three-stage workflow

This branch adds three connected stages: **Spectra & Preparation**, **Modeling
& Order Identification**, and **Kinetic Analysis**. Named peaks share context;
method-specific results, model comparison and seeded parametric Monte Carlo are
visible in the workspace. Save labeled runs and portable projects, then select
runs and a destination for PDF/CSV/JSON/PNG/SVG reporting.

Start with the [workflow preview guide](docs/redesign/WORKFLOW_USER_GUIDE.md).
The **Classic / batch workspace** retains the previous workflow. This is an
isolated review candidate; the existing beta remains intact.
See the [implementation evidence and remaining gates](docs/redesign/IMPLEMENTATION_CHECKLIST.md).

## 🔬 What is TPD Spectra Studio?

TPD Spectra Studio is a Python desktop application and reusable analysis toolkit for temperature-programmed desorption (TPD) and thermal desorption spectroscopy (TDS). It imports experimental spectra, provides interactive plots and fit-window selection, and supports classical apparent-energy estimates and numerical kinetic fitting.

The software aims to make routine analysis easier to reproduce and inspect without hiding assumptions from the researcher. It offers a graphical application for everyday work, a command-line tool for batch processing, and Python modules that developers can extend.

> **Maturity:** The current beta candidate is under hands-on Windows acceptance testing. Automated tests and a Windows build are available, but real-instrument validation and wider user testing are still underway. Kinetic parameters are model-dependent estimates, not automatically confirmed physical mechanisms.

Created and maintained by **Karol Cieślik**. The product is TPD Spectra Studio; the Python package is `tpd-spectra` and this repository is `TPD-Spectra-Analysis`.

The desktop uses an original spectrum icon and a shared navy/teal identity. See the [identity and visual acceptance notes](docs/BRAND_IDENTITY.md).

[Scientific scope/status](docs/METHOD_STATUS.md) · [Active roadmap](docs/PUBLICATION_ROADMAP.md) · [Checkpoint evidence](docs/CHECKPOINT_LEDGER.md) · [Explorer and Monte Carlo](docs/EXPLORER_MONTE_CARLO.md)

## ✨ Features

- 📂 **Flexible CSV import** — individual files or folders; legacy instrument exports and common delimited formats.
- 📈 **Interactive comparison** — multiple traces, overlay or small multiples, temperature/time axes, zoom and normalization.
- 🎯 **Fit-window selection** — drag temperature intervals on the plot or enter exact boundaries.
- 🧮 **Classical analysis** — heating-rate regression, leading-edge apparent energies and first-order Redhead estimates.
- ⚗️ **Kinetic modeling** — optional single-state and exploratory two-state Polanyi–Wigner fits.
- 🔎 **Fit diagnostics** — quality metrics, residual plots, numerical identifiability warnings and file-level errors.
- 🖼️ **Export and provenance** — high-resolution PNGs, CSV tables and JSON records of analysis settings and input hashes.
- **Reviewed runs** — separate plot visibility and analysis inclusion, setup/computed preview, destination confirmation, unique output folders, live logs/cancel and results review.
- **Experimental Kinetics Explorer** — four-order comparison, multistart diagnostics and seeded conditional Monte Carlo refitting; no claim of validated confidence limits or mechanism probabilities.
- 🧩 **Developer-accessible core** — Python API, command-line workflow, tests and contribution guidelines.

## 🚀 Quick start

### Option A — Windows desktop beta (no Python required)

1. Open [Windows desktop builds](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml).
2. Choose the latest **successful** run for branch `release/external-beta-v0.11.0b3`.
3. Under **Artifacts**, download `tpd-spectra-windows-x64-external-beta-0.11.0b3`. A GitHub login may be needed.
4. Extract the ZIP and double-click `TPD-Spectra-Studio.exe`.
5. Click **Open Example Dataset**, start with the clean first-order reference, and follow [START_HERE](START_HERE.md).

New beta packages include `examples/synthetic_two_peak_demo.csv`: a clearly labeled, noiseless two-population Polanyi–Wigner simulation with known inputs. Follow the [demo walkthrough](examples/README.md) for settings and expected results. Synthetic tests do not replace experimental validation. The executable is currently unsigned; verify the GitHub source and follow institutional security policy.

### Option B — Run from Python source

```bash
git clone https://github.com/karol-cieslik/TPD-Spectra-Analysis.git
cd TPD-Spectra-Analysis
git checkout release/external-beta-v0.11.0b3
python -m pip install -e .
python run_tpd_spectra_gui.py
```

Requires Python 3.10+ with Tkinter available. Using a virtual environment is recommended.

### Command-line analysis

```bash
tpd-spectra --help
tpd-spectra path/to/spectrum.csv --output results
tpd-spectra path/to/spectrum.csv --output results --kinetic-fit --kinetic-order 1
```

## 📦 Inputs and outputs

Legacy CSV columns include `ms` (elapsed time in milliseconds), `DHTA+` (detector signal), and `Temperatura` (temperature in °C). Other common time, signal and temperature column names are recognized; delimiter and decimal conventions vary by instrument. **Check the units and channel assignment** before interpreting results.

| Output | Purpose |
| --- | --- |
| `all_desorption_parameters.csv` | Classical estimates and diagnostic values |
| `batch_summary.csv` | Batch summary and optional numerical fits |
| `all_tds_spectra.png` | Comparison figure |
| `diagnostics/` | Per-spectrum plots and fit inspection |
| `analysis_warnings.csv`, `analysis_errors.csv` | Warnings and recoverable failures, when present |
| `analysis_project.json` | Analysis settings, software version and input file hashes |

The GUI can independently export a comparison PNG at 300 dpi.

## 🧪 Scientific methods and limitations

| Method | Implemented use | Essential limitation |
| --- | --- | --- |
| Heating-rate estimation | Fits temperature against time in a selected region | Nonlinear ramps require care |
| Leading-edge analysis | Fits `ln(signal)` versus `1/T` to obtain an apparent energy | Assumes positive signal proportional to rate and an appropriate leading-edge regime |
| Redhead approximation | Estimates apparent energy from a peak temperature | Implemented for first-order kinetics with an assumed prefactor |
| Polanyi–Wigner model | Numerically integrates depletion and fits selected kinetic parameters | Assumes a nominally constant heating rate and normalized coverage |
| Two-state comparison | Exploratory fitting of overlapping populations | Two components do not prove two physical adsorption sites |
| Identifiability warnings | Detects numerical ill-conditioning and fits near bounds | Does not establish unique mechanism or validated confidence intervals |

All energies require absolute temperature in kelvin in the rate equations. Review residuals, baselines, intervals, heating-rate calibration and fitted-parameter correlation. A high R² alone does not establish the desorption mechanism.

Read the [User and Scientific Methods Manual](docs/USER_AND_SCIENTIFIC_MANUAL.md) for equations, assumptions, interpretation and reproducibility details. Experimental uncertainty and numerical benchmark research remain in separate development work until independently evaluated.

## 📚 Documentation

| Document | Purpose |
| --- | --- |
| [User and scientific manual](docs/USER_AND_SCIENTIFIC_MANUAL.md) | Installation, workflows, equations, interpretation and reproducibility |
| [Beta acceptance checklist](docs/BETA_ACCEPTANCE_CHECKLIST.md) | Hands-on Windows and scientific smoke tests |
| [Example dataset](examples/README.md) | Synthetic CSV origin, units and appropriate use |
| [Contributing](CONTRIBUTING.md) | Setup, architecture, testing and contribution standards |
| [Prioritized roadmap](docs/PRIORITIZED_DEVELOPMENT_ROADMAP.md) | Reliable release, validation and developer-readiness priorities |
| [Release gates](docs/RELEASE_AND_PUBLICATION_GATES.md) | Acceptance, validation, maintenance and release evidence |
| [Asset rights](ASSET-RIGHTS.md) | Limits on redistributing experimental and third-party materials |

## 🛠️ Building and testing from source

Install the Python development tools and editable project:

```bash
python -m pip install -r requirements-build.txt
python -m pip install -e .
python -m pytest -q
```

To reproduce the Windows single-file build, use PyInstaller on Windows:

```bash
pyinstaller --clean --noconfirm --onefile --windowed --name TPD-Spectra-Studio run_tpd_spectra_gui.py
```

| Build artifact | Use |
| --- | --- |
| `dist/TPD-Spectra-Studio.exe` | Portable Windows desktop application |
| Installed command `tpd-spectra` | Batch command-line interface |
| Installed command `tpd-spectra-gui` | Desktop GUI from a Python environment |

## ⚙️ Continuous integration and release process

| Workflow / check | Trigger | Purpose |
| --- | --- | --- |
| [Windows desktop build](.github/workflows/desktop-build.yml) | Selected branch pushes and manual dispatch | Installs dependencies, runs tests, performs startup checks, packages an EXE and uploads a ZIP |
| [Scientific tests (research branch)](https://github.com/karol-cieslik/TPD-Spectra-Analysis/blob/feature/kinetic-identifiability-diagnostics/.github/workflows/scientific-tests.yml) | Scientific research branch changes | Scientific regression and benchmark smoke tests |

The [beta candidate PR](https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/5) is not merged into the stable main branch. A passing build is **not** the same as final release approval.

```text
Source changes → Automated checks → Windows artifact
                                           ↓
                                Hands-on beta testing
                                           ↓
                               Reviewed release decision
                                           ↓
                                 Versioned public release
```

## 🤝 Contributing

Bug reports, independently shareable spectra, documentation improvements and scientifically justified tests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and include reproducible steps, the software version, input format and relevant assumptions.

Use [GitHub Issues](https://github.com/karol-cieslik/TPD-Spectra-Analysis/issues) for bugs and proposals. **Do not upload confidential experimental data or redistributable figures without permission.**

## 📖 Citation and license

The project-authored source code is provided under the [MIT License](LICENSE), subject to the scope explained in [ASSET-RIGHTS.md](ASSET-RIGHTS.md). Citation metadata is maintained in [CITATION.cff](CITATION.cff). A citable tagged release and peer-reviewed software description are future milestones; neither is claimed for this beta candidate.


### Candidate workflow

After importing, select **Include** for the files to analyze (independent of **Show**). Set and inspect the analysis windows, then choose **Run full analysis**. Review assumptions, import changes and Setup preview; explicitly confirm the new results location. You may compute one selected spectrum first as an unsaved preview. **Run and save** retains the submitted settings and creates a new folder. Review results, residuals and failures inside the app. About identifies the author, candidate version and build.

Explorer is explicitly experimental. Select an isolated peak, justify its heating rate, compare models, inspect residuals, then review Monte Carlo assumptions and set a seed/count. Use its guide before interpreting conditional ranges.
