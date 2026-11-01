# Welcome to TPD Spectra Studio 0.11.0b7

**Informal research beta** by **Karol Cieślik**. Please try the synthetic
example first; no experimental data is needed. Use a build whose exact main
commit has a successful Windows desktop workflow. Experimental validation and
testing on different Windows displays are still in progress.

The current main source includes PR #32's reviewed CSV/TSV/TXT import preview.
Download the latest successful **main** artifact from
[Windows beta builds](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml?query=branch%3Amain).
Check `VERSION.json` for its exact source commit and `SHA256SUMS.txt` for checksums.
No public prerelease has been published. Human visual/DPI and clean-machine
Windows acceptance remain outstanding; see [release notes](docs/beta/RELEASE_NOTES.md).

1. Extract the **whole ZIP** to a writable folder. Keep the executable, `docs`
   and `examples` together. No Python installation is needed for the Windows build.
2. Double-click **TPD-Spectra-Studio.exe**. The application is unsigned; follow
   your institution's software policy. Do not disable security protections.
   The bundled noisy two-peak demo opens with its first peak (70–210 °C) selected.
   Keep this example for the later model-comparison and Monte Carlo exercise.
3. Click **Browse examples…**, stay in **Simulated**, select **first order single peak**, and click **Open selected spectrum**.
   This supplies a synthetic 801-point trace, a named interval and a 1 K/s ramp.
4. Open **Kinetic Analysis**, select **Redhead**, and check the assumed prefactor
   is **1e13 s⁻¹**. The preview should be about **1.2 eV** (within 2.5% of the
   synthetic input). Open **Parameter summary** to distinguish the calculated
   energy from assumed inputs, then **Assumptions & provenance** for warnings.
   This is an approximation, not a measured confidence interval.
5. Click **Save labeled result…**, then **Report / Export…**. Select your saved
   run, click **Choose destination and generate report…**, and choose a folder.
   Open its PDF; CSV, JSON, PNG and SVG exports accompany it.
6. **File → Save project…** retains your data, settings and results for reopening.

For a measured spectrum, choose CSV, TSV or TXT and review the preview before importing. Check the detected delimiter and header, correct channel mappings if needed, explicitly confirm time and temperature units when headers do not specify them, and inspect accepted/rejected row counts. Some older 0.11.0b5 artifacts lack this preview; use the latest successful main artifact and verify `VERSION.json`.

Then try the noisy two-peak example. In Modeling, compare First order for the
first named interval; set Monte Carlo replicates to 20 and seed to 42 for a
short tutorial. To analyze the second demo peak, return to **Spectra & Preparation**, drag a new interval around the second peak, give it a distinct name and click **Add peak**. Use **Update peak** only if you intend to change the selected peak; previous results then become stale and must be recalculated. Watch progress and inspect failures. This demonstrates the
workflow, not uncertainty coverage; conditional ranges require at least 100
successful refits. Use **Help → Quick start** for guided exercises and **Help → Scientific Help / Parameters**
or the **?** buttons for units, roles and limitations.

After the synthetic exercises, use **Examples → Publication-derived spectra…**
to explore curated curves from Zaki, Narayanan, Kruczkiewicz, Fulker & Brown,
Ayling et al., and Becker et al. Each entry shows its citation, figure, source
units and limitations. Most are *digitized figure coordinates* with an artificial
nominal-ramp time column for compatibility, not original measured time. The
Becker deposited trace retains measured time but has a nonconstant ramp.
See [the publication-example provenance](examples/publication_data/README.md).
None is a known-ground-truth energy validation.

Read [the full worked guide](docs/beta/WORKED_EXAMPLES.html) (offline HTML),
[the brief Quick Start PDF](docs/beta/QUICK_START.pdf),
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

Use **Help → Report a bug / Send feedback** to inspect, copy or save a diagnostic report.
Email drafts are addressed to **Dr. Karol Cieślik**, **karol.j.cieslik@gmail.com**.
Nothing is automatically sent; attach the ZIP manually if desired. No spectra
are automatically attached. Projects and analysis reports *do* contain data;
share those only intentionally and with permission.

Source: https://github.com/karol-cieslik/TPD-Spectra-Analysis

Code license: MIT. See LICENSE and ASSET-RIGHTS.md for scope and separate assets.
