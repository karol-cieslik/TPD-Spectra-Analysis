# Welcome to TPD Spectra Studio 0.11.0b4

**Informal research beta** by **Karol Cieślik**. Please try the synthetic
example first; no experimental data is needed. This version has passed automated
tests, but experimental validation and testing on different Windows displays
are still in progress.

This candidate is developed in [PR #19](https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/19)
on `fix/beta-feedback-14-17`. Open its latest successful **Windows desktop build**
check, then download `tpd-spectra-windows-x64-beta-0.11.0b4` under **Artifacts**
(GitHub sign-in may be required). Check `VERSION.json` for the build commit.
This temporary build is for review; no public release has been published.

1. Extract the **whole ZIP** to a writable folder. Keep the executable, `docs`
   and `examples` together. No Python installation is needed for the Windows build.
2. Double-click **TPD-Spectra-Studio.exe**. The application is unsigned; follow
   your institution's software policy. Do not disable security protections.
   The bundled two-peak demo opens with its first peak (70–210 °C) selected.
   In **Modeling & Order Identification**, click **Simulate parameters**, then
   **Compare models**. For a short first software check, select only first order,
   disable multistart and use 2 Monte Carlo replicates, seed 42; then **Run Monte Carlo**.
   Two replicates exercise the workflow; they do not estimate uncertainty.
   Select the first-order result row, transfer it to Kinetic Analysis, and fit.
   This fits one approximate isolated peak, not the entire two-state spectrum.
3. Click **Open Example Dataset**, keep **first order single peak**, and open it.
   This supplies a synthetic 801-point trace, a named interval and a 1 K/s ramp.
4. Open **Kinetic Analysis**, select **Redhead**, and check the assumed prefactor
   is **1e13 s⁻¹**. The preview should be about **1.2 eV** (within 2.5% of the
   synthetic input). This is an approximation, not a measured confidence interval.
5. Click **Save labeled result…**, then **Report / Export…**. Select your saved
   run, click **Choose destination and generate report…**, and choose a folder.
   Open its PDF; CSV, JSON, PNG and SVG exports accompany it.
6. **Save project…** retains your data, settings and results for reopening.

Read [the Quick Start](docs/beta/QUICK_START.pdf),
[example truth and limitations](examples/beta_collection/README.md), and the
[informal tester checklist](docs/beta/TESTER_CHECKLIST.md).

**Zero-order interpretation:** select a complete depletion edge with rising
signal and at least three samples after exhaustion. The new fitter reports
conditional prefactor/scale ranges at fitted energy and normalized coverage one.
These are not confidence intervals or proof of a unique physical mechanism.
Monte Carlo is conditional parametric refitting, not microscopic kinetic MC or
a validated confidence procedure. Overlap, drift and correlated noise require
additional scrutiny. A good fit does not establish a physical mechanism.

For overlap, use **Overlapping components…** in Modeling to fit up to three
independent physical populations together on the full spectrum. Orders,
prefactors and coverages are fixed hypotheses; energies/scales are fitted.
Read [the component workflow and limits](docs/MULTICOMPONENT_FITTING.md).

Use **Report a Bug / Send Feedback** to inspect, copy or save a diagnostic report.
Email drafts are addressed to **Dr. Karol Cieślik**, **karol.j.cieslik@gmail.com**.
Nothing is automatically sent; attach the ZIP manually if desired. No spectra
are automatically attached. Projects and analysis reports *do* contain data;
share those only intentionally and with permission.

Source: https://github.com/karol-cieslik/TPD-Spectra-Analysis

Code license: MIT. See LICENSE and ASSET-RIGHTS.md for scope and separate assets.
