# A short, informal colleague test

Thank you for trying this early beta. Ten to twenty minutes is useful; there is
no need to complete every item or produce a formal review.

Use the revised [worked examples](WORKED_EXAMPLES.html) for exact button names
and settings, or the **Workflow quick start** tabs in the program. A separate
[short feedback form](FEEDBACK_FORM.md) is available if you prefer written
questions. Use a fresh Windows desktop build for current `main`, not an older 0.11.0b5 artifact; record its exact source commit from `VERSION.json`. Results, Help and five tutorials are included.

- [ ] Extract the whole package and launch on Windows without Python.
- [ ] Import CSV, TSV and TXT samples; check the detected layout, correct a channel mapping, confirm source units, and review accepted/rejected row counts.
- [ ] Check that the default demo has a selected first-peak region and retains its
  raw trace in Modeling, including during simulation and cancellation.
- [ ] Check that **File / Examples / View / Help** menus are accessible,
  while the top row shows only Open spectrum, Browse examples and Report / Export.
  Test at 1100×720 and 125–150% Windows display scaling.
- [ ] In **Browse examples…**, switch between **Simulated** and **Publication-derived**.
  Open a Zaki or Ayling figure-derived trace; confirm DOI, citation, licence,
  original Kelvin units, limitations and artificial nominal-ramp time warning.
  Open the Becker/AgY deposited trace and check that the nonconstant ramp is flagged.
- [ ] Find About, the developer contact, Quick Start and feedback under **Help**.
- [ ] Open **Scientific Help / Parameters**, search for `seed`, and try a
  field-level **?** button. Does it explain units, roles and scientific cautions?
- [ ] Open the clean first-order example and obtain an approximately 1.2 eV
  Redhead estimate using the supplied 1 K/s ramp and assumed 1e13 s⁻¹ prefactor.
- [ ] In **Parameter summary**, confirm that Redhead energy is shown as a
  calculated estimate and the prefactor as an assumed input. Check
  **Assumptions & provenance** for the submitted settings and warnings.
- [ ] Switch peaks/methods and verify the visible settings belong to your selection.
- [ ] Try a first-order model comparison, inspect residuals and run 20 seeded
  Monte Carlo replicates (seed 42). A short run tests usability, not uncertainty coverage.
- [ ] Watch the progress bar/count, elapsed time and Cancel state; check completion
  separates fitting failures from incomplete rankings and preserves prior output.
- [ ] For the versioned prerelease, record the source commit from VERSION.json. Use **Fit Multiple Peaks…**, select 2 components and both positions, fit and inspect both styled components, sum, baseline and residuals. Switch 2 → 3 → 1 → 3 and verify surviving/cached row edits. At minimum dialog size/high DPI check footer actions, scrolling and Advanced controls.
- [ ] Open Zaki, reject the 3 K/s suggestion and confirm the current rate is retained; accept it and confirm Modeling changes explicitly. Kinetic Analysis remains separate. Check flat/poor/collapsed diagnostics and withheld intervals; the digitized curve does not establish two first-order states.
- [ ] Optional: use the documented three-state synthetic exercise in
  `docs/MULTICOMPONENT_FITTING.md`, inspect individual curves/sum/residuals and
  export component parameters. Fixed assumptions do not establish physical states.
- [ ] Save a labeled result; choose the report destination; inspect the PDF and CSV.
- [ ] Save/reopen a project. Check the selected data, interval and settings.
- [ ] Resize the window and try your usual display scaling. Note clipped controls,
  confusing names, unexpected waits or any step needing explanation.
- [ ] Check that the five Quick Start tabs can be navigated and the offline
  detailed guide opens without needing an internet connection.
- [ ] Inspect a diagnostic report, copy it or save the ZIP. Nothing needs to be sent
  unless you choose. No GitHub account is needed to email feedback.
- [ ] Optional: try one spectrum you are permitted to use and check against an
  independent calculation. Report units, assumptions and discrepancies.

For zero order, inspect the depletion edge and conditional prefactor/scale
ranges. The displayed representative pair is not unique; brackets are not
confidence intervals. Model selection and Monte Carlo
outputs remain conditional on the implemented model/noise assumptions.

Email **Dr. Karol Cieślik**, **karol.j.cieslik@gmail.com**, with the version from
About, what you expected, what happened, and optional steps/screenshots. Inspect
screenshots and reports for private information first. The feedback ZIP excludes
spectral files, but text you type yourself is included.

## Optional experimental benchmark contribution

If you have a suitable spectrum, first confirm ownership and permission to share.
Describe temperature/time/signal units, heating rate, preprocessing, calibration
and the independent reference result. Sharing for private debugging does **not**
grant permission to publish, redistribute, train on or bundle the data. Agree
separately on storage, access, attribution, license and deletion before any reuse.
Confidential or unpublished data are not required for this beta test.

## Suggested personal invitation (not sent)

Hi, I've prepared an early beta of TPD Spectra Studio and would appreciate a
quick informal try if you have time. It includes synthetic examples and a short
guide, so you don't need to share any data. I'm especially interested in whether
the workflow is clear and whether results and assumptions are presented usefully.
Scientific assumptions and limitations are listed in START_HERE.
Even a few comments by email would help. No pressure to do a full review!
