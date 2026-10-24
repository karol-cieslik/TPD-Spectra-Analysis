# Welcome to TPD Spectra Studio 0.11.0b2

**External beta review candidate** by **Karol Cieślik**. Please try the synthetic
example first. This package is for review; experimental validation and visual
acceptance on colleagues' Windows displays remain open.

1. Extract the **whole ZIP** to a writable folder. Keep the executable, `docs`
   and `examples` together. No Python installation is needed for the Windows build.
2. Double-click **TPD-Spectra-Studio.exe**. The application is unsigned; follow
   your institution's software policy. Do not disable security protections.
3. Click **Open Example Dataset**, keep **first order single peak**, and open it.
   This supplies a synthetic 801-point trace, a named interval and a 1 K/s ramp.
4. Open **Kinetic Analysis**, select **Redhead**, and check the assumed prefactor
   is **1e13 s⁻¹**. The preview should be about **1.2 eV** (within 2.5% of the
   synthetic input). This is an approximation, not a measured confidence interval.
5. Click **Save labeled result…**, then **Report / Export…**. Select your saved
   run, click **Choose destination and generate report…**, and choose a folder.
   Open its PDF; CSV, JSON, PNG and SVG exports accompany it.
6. **Save project…** retains your data, settings and results for reopening.

Read [the four-page Quick Start](docs/beta/QUICK_START.pdf),
[example truth and limitations](examples/beta_collection/README.md), and the
[informal tester checklist](docs/beta/TESTER_CHECKLIST.md).

**Known scientific issue:** zero-order fits may report convergence with biased
amplitude and poor residuals. The clean reference currently fails its preset
residual tolerance. Do not use this beta to report quantitative zero-order fits.
Monte Carlo is conditional parametric refitting, not microscopic kinetic MC or
a validated confidence procedure. Overlap, drift and correlated noise require
additional scrutiny. A good fit does not establish a physical mechanism.

Use **Report a Bug / Send Feedback** to inspect, copy or save a diagnostic report.
Email drafts are addressed to **Dr. Karol Cieślik**, **karol.j.cieslik@gmail.com**.
Nothing is automatically sent; attach the ZIP manually if desired. No spectra
are automatically attached. Projects and analysis reports *do* contain data;
share those only intentionally and with permission.

Source: https://github.com/karol-cieslik/TPD-Spectra-Analysis

Code license: MIT. See LICENSE and ASSET-RIGHTS.md for scope and separate assets.
