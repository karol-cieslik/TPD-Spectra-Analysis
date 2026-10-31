# One Windows acceptance exercise — NOT RUN

Purpose: verify the current workflow GUI's import, calculation, saved state and native report export. This is an acceptance exercise, not experimental energy validation. Expected time: about 15–20 minutes on an installed working build.

Tester / date:
Windows version:
Executable or source launch:
Software version and exact commit/build identifier:
Executable SHA256 (if packaged):
Result folder / evidence location:

Use [the pinned Windows task](PINNED_WINDOWS_TASK.md) for the exact CI artifact, source commit, archive digest, separate fixture and evidence capture. Record the actual build; the version string alone is insufficient. A source test may use commit `4fbcc159136a31ce5053c0f074b4c6826da51a06` in an isolated environment, launched with `tpd-spectra-gui`, but does not complete the clean-Windows portable-EXE gate. Do not substitute the moving publication branch or an older beta package.

## Import and inspect

- [ ] Launch without an exception or a frozen interface; record launch method.
- [ ] Import [D2_measured_GUI_ms_degC.csv](evidence/D2_measured_GUI_ms_degC.csv). It has **289 rows**, measured time in **ms**, temperature in **°C** and unchanged D2 signal in molecules/s. Do not import the original K/s file under legacy defaults.
- [ ] Confirm temperature axes and sampled maximum: **-181.09 °C = 92.06 K**. Check time scale against the fixture's measured values. No temperature-cleaning changes are expected for this fixture.
- [ ] Keep smoothing `none`, baseline `0`, normalization off. Confirm the selected dataset and record the processing settings shown.

The fixture applies only s → ms and K → °C. [Provenance](evidence/D2_fixture_provenance.json) and hashes retain the source. Its full measured ramp previously failed the default mismatch screen; do not force a full-trace kinetic fit. The following leading-edge calculation exercises the interface and has **no literature-energy acceptance target**.

## Calculate one apparent estimate

- [ ] In **Spectra & Preparation**, add a peak named `D2 usability check` from **-188.15 to -180.15 °C** (85–93 K).
- [ ] In **Kinetic Analysis**, choose **Leading edge**. Set limits **-188.15 to -182.15 °C** (85–91 K), supplied beta **0.1 K/s**. This interval contains seven positive source points. Beta is supplied, not a demonstration of a perfectly linear measured ramp.
- [ ] Click **Calculate / Fit selected peak**. Confirm a finite apparent energy, the selected interval and seven regression points. Record the displayed energy and units below; do not treat its magnitude as validated physics.
- [ ] Inspect **Spectrum & residuals**, **Parameter summary** and **Assumptions & provenance**. Confirm regression-only interval wording, the supplied beta role and unavailable absolute prefactor. Record missing/misleading cautions as issues.

Displayed apparent energy (eV):
Displayed point count:
Observed warnings / role labels:

## Save, export and reopen

- [ ] **Save labeled result…** as `D2 Windows usability check`. Use **Report / Export…**, select that saved run, then **Choose destination and generate report…** into a fresh folder.
- [ ] Open `report.pdf`, `results.json` and the generated curve CSV. Confirm readable axes, the selected interval, supplied beta, processing recipe, warnings and an energy matching the displayed result within displayed rounding. Record any omitted caution or differing value.
- [ ] **Save project…**, close/reopen the app, **Open project…**, and **Reopen saved run**. Confirm data, method, limits and saved values persist.
- [ ] Change an input interval without calculating. Confirm the old result remains identified as stale/original-settings rather than silently becoming a new result.

Exported apparent energy / agreement with screen:
Report warnings actually checked:
Project reopen result:
Any exception, freeze, missing caution or stale-state issue:

## Outcome

**NOT RUN** / PASS / FAIL / PARTIAL

Evidence files/screenshots retained:
Unexecuted steps:

A pass applies only to this exercised path/build. It does not establish all-platform support, a portable-EXE launch without Python, physical model correctness or independent scientific acceptance. Linux headless export/helper checks already recorded in this package do not complete any checkbox above.
