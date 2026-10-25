# Living technical reference (development draft)

This reference is maintained alongside the implementation. It is **not** a user manual or a statement that every model has been experimentally validated. Check formulas against the linked source modules when reviewing changes.

## Architecture and dependencies

- **Python >=3.10**. Package metadata and runtime dependencies: `pyproject.toml`.
- **NumPy**: arrays, linear algebra, numerical operations.
- **Pandas**: CSV parsing, cleaning, tabular output.
- **SciPy**: physical constants and statistical distributions (`analysis.py`), ODE integration and nonlinear least squares (`kinetics.py`).
- **Matplotlib**: spectra and diagnostic plotting.
- **Tkinter / ttk** (Python standard library): desktop GUI; embedded Matplotlib canvas (`gui.py`).
- **pytest**: tests; **PyInstaller**: Windows distributable (development/build requirements).
- Analysis is exposed via the CLI (`cli.py`) and desktop workflow (`workflow_gui.py`) and classic GUI (`gui.py`); avoid reimplementing scientific formulas in UI code.

## Fundamental model

Polanyi–Wigner rate: `r(T, θ) = ν θ^n exp[-E/(k_B T)]`, with `dθ/dT = -r/β` for constant heating rate `β = dT/dt`. The implementation uses `E` in eV, `T` in kelvin after converting inputs from Celsius, `β` in K/s, and desorption rate in fractional coverage per second. The interpretation of `ν` and its units depends on the reaction order and coverage normalization; the code currently names the fitted prefactor `prefactor_s_inv`, which should not be assumed dimensionally general for arbitrary coverage units.

The single-state fit estimates `E`, `log10(ν)`, `log10(signal scale)`, optional constant baseline, and optional order. It uses bounded nonlinear least squares on the chosen data under a constant heating-ramp model. See `tpd_spectra/kinetics.py`. Fixed zero order instead profiles the depletion boundary and reports conditional prefactor/scale brackets; see [ZERO_ORDER_FITTING.md](ZERO_ORDER_FITTING.md). The two-state model is exploratory; multiple states can be difficult to resolve uniquely.

## Classical estimates and uncertainties

- **Leading-edge**: fit `ln(signal)` as a function of `1/T` over a user-selected interval. Reported activation energy is `E = -k_B × slope`. The OLS 95% interval is formed using the Student-t critical value for the slope and then transformed to energy. Assumes positive signal and the chosen leading-edge approximation; the interval covers *regression noise only*, not calibration, baseline, correlated residuals, or model uncertainty.
- **Redhead**: a first-order peak-temperature energy estimate with an assumed prefactor and constant heating rate. Sensitivity to prefactor is not a statistical confidence interval.
- **Full-trace kinetic fits**: current releases report fit statistics and Jacobian condition diagnostics but do **not** provide independently validated parameter confidence intervals. Rank and bound-proximity diagnostics are integrated; the optional research bootstrap is described in NONLINEAR_BOOTSTRAP_UNCERTAINTY.md and is not a validated uncertainty procedure. Singular matrices, strong correlations, bounds, and poor model adequacy make naive covariance formulas misleading.

## Scientific reporting principles

1. Clearly distinguish measured quantities, fitted parameters, user assumptions, and derived estimates.
2. Record units, preprocessing settings, fit windows, initial guesses, solver bounds, and fit diagnostics.
3. Never label local Gaussian linearized confidence intervals as full experimental uncertainty.
4. Check model adequacy, residual autocorrelation, parameter identifiability and sensitivity to calibration and heating-rate errors.
5. Literature digitization and laboratory-data comparisons require datasets with provenance and are a separate validation workstream.

## Planned reference chapters

1. Data formats, units, CSV handling, temperature cleaning and smoothing.
2. Classical methods (leading-edge, Redhead), assumptions and uncertainty.
3. Polanyi–Wigner first/zero/second/noninteger-order and two-state fitting.
4. Numerical solvers, optimization, initial conditions, bounds, identifiability and limitations.
5. Uncertainty estimation method, covariance/bootstrap, measurement and systematic errors (write only when implemented).
6. Reproducible analysis output, metadata, warnings and versioning.
7. Package inventory, licenses and links to source declarations.

## Documentation workflow

Update the relevant section in the same PR as every scientific algorithm change; add a worked, synthetic example when feasible. The final beginner-friendly manual, annotated GUI screenshots and publication-facing methods section should be polished only after the interface and uncertainty APIs stabilize.
