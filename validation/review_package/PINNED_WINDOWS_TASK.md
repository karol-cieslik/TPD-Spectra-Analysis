# Pinned clean-Windows acceptance task — NOT RUN

Prepared 29 October 2026. This is the next single acceptance task, not a new experimental assessment. PR #23 was merged as `4dcbd3ad56689a6a326ac99baed26c9ee2902fcb`; its final tested source was `4fbcc159136a31ce5053c0f074b4c6826da51a06`. Existing experimental comparisons and post-fix ranking results are retained unchanged.

## Exact candidate

| Item | Recorded evidence |
|---|---|
| Version | 0.11.0b5; version alone does not identify the build |
| Source commit | `4fbcc159136a31ce5053c0f074b4c6826da51a06` |
| Windows run | [40869536465](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40869536465), completed/success |
| Scientific run | [40869535950](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40869535950), completed/success |
| Download | [Windows artifact 12894894418](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40869536465/artifacts/12894894418) |
| Artifact name | `tpd-spectra-windows-x64-beta-0.11.0b5` |
| GitHub-recorded archive digest | `sha256:4ba136323427613b2d08abf0b8c97f012cc87c53f36a228029bae10dea9690d6` |
| Archive size | 86,690,980 bytes |
| Expiry reported at inspection | 27 January 2027, 11:58:44 UTC; do not silently substitute another build |

Run status and artifact metadata were fetched through the GitHub API on 29 October 2026. The artifact was not downloaded or executed in this preparation. The recorded digest identifies the Actions artifact archive, **not** the executable or a later release ZIP. If unavailable, rebuild the pinned source and record the new run/artifact/hash separately; never claim it is this artifact.

## Execute on Windows

Use a clean Windows machine or fresh Windows VM with no separately installed Python. Record Windows version, display scaling and whether Python is present. A source installation can exercise the workflow but cannot pass this portable acceptance gate. Allow approximately 20 minutes; stop on an identity/hash mismatch before interpreting application results.

1. Download the linked artifact (GitHub sign-in may be required). Keep the downloaded ZIP and original filename. In PowerShell run `Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\path\downloaded-artifact.zip'`. Compare with the archive digest above. Record the actual value; if it differs, retain the file and investigate rather than declare a pass.
2. Extract the entire package into a new writable folder. Open `VERSION.json` and verify version and full commit against the table. Hash `TPD-Spectra-Studio.exe` with `Get-FileHash` and retain the result alongside `VERSION.json`. That executable hash is measured by the tester, not supplied by this task. Retain the packaged checksum file too.
3. Obtain the separate [D2 fixture](https://github.com/karol-cieslik/TPD-Spectra-Analysis/blob/4fbcc159136a31ce5053c0f074b4c6826da51a06/validation/review_package/evidence/D2_measured_GUI_ms_degC.csv) using Download raw file. Its SHA256 must be `92d937e5f621673123e02b015aa68ab5d21c554f660e12dee71c6c6160d8c03f`. This external measured-data fixture is not assumed to be bundled in the portable package. Preserve its [provenance and attribution](https://github.com/karol-cieslik/TPD-Spectra-Analysis/blob/4fbcc159136a31ce5053c0f074b4c6826da51a06/validation/review_package/evidence/D2_fixture_provenance.json).
4. Double-click the extracted executable and carry out [WINDOWS_ACCEPTANCE.md](WINDOWS_ACCEPTANCE.md), including the seven-point leading edge, native report, saved project reopening and stale-result check. Do not force full-trace kinetic fitting or target a literature energy. Record every unexecuted step.
5. Save a **copy** of the completed checklist in a new evidence folder. Retain ZIP/EXE hashes, VERSION.json, screenshots of result/assumptions and reopened run, report.pdf, results.json, curve CSV and project. Record whether the PDF preserves interval, supplied beta, processing settings and cautions. Attach an exact reproducible failure description for each missing item. Do not overwrite historical evidence or the unfilled template.

## Decision and limits

Current result: **NOT RUN**. Tester, environment, measured hashes and output evidence: **not supplied**.

PASS requires verified identity, no separately installed Python, and every checklist step completed successfully with retained evidence. FAIL records an observed blocking defect; PARTIAL records incomplete steps or an environment that does not test the clean-machine condition. No result is inferred from CI. A passed exercise covers only this build and path; it is not full desktop acceptance, independent scientific approval or experimental energy validation.

Independent scientific review remains a separate human gate: use [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md), leaving it unfilled until an actual scientist responds. Actual research use, author metadata/AI disclosure and public-history eligibility remain open. No outreach, release, new fits or expanded scientific claims are part of this task.
