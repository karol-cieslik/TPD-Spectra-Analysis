# TPD Spectra Studio: development and publication roadmap

Active development plan • 22 October 2026 • Based on beta commit `ad2667ad486f2f9404159feeb528dad992de608c`

Implementation is authorized on the beta branch. This document does not authorize a public release or claim completed scientific validation. Status and evidence are maintained in [CHECKPOINT_LEDGER.md](CHECKPOINT_LEDGER.md); the unchecked list below defines the acceptance criteria. All unchecked items require evidence. Version numbers below are provisional milestones rather than promised dates.

## 1. Product objective and release levels

Build an approachable desktop workspace in which a researcher can import TPD/TDS measurements, inspect what the software changed, select an appropriate analysis, examine its limitations, and export a reproducible research record.

The primary audience is experimental researchers who understand their measurements but should not need to program. A second audience is researchers who need a scriptable, inspectable scientific engine. Preserve both the GUI and command-line/API workflows.

| Milestone | Meaning | Required evidence |
| --- | --- | --- |
| Public beta | Other researchers can try the defined workflow safely, with clear limits | Packaged application works; core scientific methods audited; recoverable errors; guided workflow; independent usability test |
| Stable research release | The supported methods and workflows have reproducible scientific and operational evidence | Independent numerical references, documented experimental cases, reproducibility checks, maintained documentation, resolved critical defects |
| Citable software release | A particular version can be identified and retrieved | Tagged source, archived version, citation metadata, persistent identifier and release assets |
| Software paper | There is a defensible research-software contribution and demonstrated use | State-of-field comparison, scientific evidence, public development history, research use, responsible authorship and venue eligibility |

A DOI is an identifier and archive, not certification of scientific accuracy. Likewise, a successful build or large test count does not validate every scientific method.

## 2. Starting point: verified strengths and observed gaps

The previous verification recorded 78 passing local tests, a successful Windows build, and a smoke test that ran the frozen executable on the shipped demo. The synthetic example has 601 points, a 1 K/s ramp, no temperature corrections, and independently generated first-order populations. Its first-peak Redhead estimate was about 1.244 eV for a 1.25 eV input. This is a narrow demonstrated case, not general experimental validation. Evidence: [verified build](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/39672954423) and [PR #5](https://github.com/karol-cieslik/TPD-Spectra-Analysis/pull/5).

Source inspection identifies these priorities:

- The GUI offers a results-folder field, but Run full analysis immediately uses its current value, initially a default folder. There is no pre-run review.
- Plot visibility also determines which files are analyzed. That is easy to misunderstand.
- Repeated runs use a shared destination and familiar filenames. Separate run folders and explicit collision handling are needed.
- Completion messages read the current folder control instead of an immutable record of the submitted run; changing controls during execution can make the reported destination misleading.
- Worker output is collected when the subprocess finishes; there is no durable, live progress view or user cancellation workflow.
- Results are principally external tables and images. The app needs a review workspace.
- Import currently sorts times and removes duplicate timestamps. Users need to see and approve scientifically consequential data handling.
- Numerical kinetics reconstructs a linear temperature coordinate from fitted heating rate and time. That transformation needs visibility and explicit validity checks.
- A 1e20 s⁻¹ Redhead prefactor is the GUI default. Any default must be clearly identified as an assumption, with provenance or a user decision; it must never imply a universal value.
- Branding/version metadata still needs a consistent release strategy. An About section is missing.
- Quick Start widget tests passed, but its desktop screenshot review was not completed because capture failed. Manual visual acceptance remains open.

## 3. Lessons from comparable projects

These are references for design and positioning, not claims that their scientific models are interchangeable with TPD Spectra Studio.

| Reference | Relevant practice | Application here |
| --- | --- | --- |
| [Origin analysis controls](https://docs.originlab.com/origin-help/common-analysis-feature/) | Explicit input ranges, output controls, reusable analysis settings | Review the inputs and destination before a run; reuse named settings with their assumptions visible |
| [Fityk](https://fityk.nieto.pl/getstarted.html) and its [fitting documentation](https://fityk.nieto.pl/fit.html) | Residual inspection, parameter interaction and fitting history | Put fitted curves and residuals together; make revision and comparison possible |
| [SasView documentation](https://www.sasview.org/documentation/) | User instructions, model equations/references, tutorials and developer documentation | Give every supported method a readable explanation plus a technical reference |
| [BChemXtract](https://github.com/Beilstein-Institut/BChemXtract) | Clear purpose and navigation to installation, quick start, contributions and releases | Use a similar clarity of presentation, with an original identity and real app screenshots |
| [tpd-analyse](https://pypi.org/project/tpd-analyse/) | A domain-specific first-order TPD analysis package | Include it in the scientific landscape review; compare scope and assumptions before comparing outputs |
| [Abdelrahman Lab TPD tools](https://abdel.chee.uh.edu/analytical-tools/) | A published lab implementation for Polanyi–Wigner predictions | Investigate as an independent comparison candidate after verifying equations, units and usage rights |

The proposed differentiator is a transparent, reproducible desktop TPD workflow: understandable import, visible assumptions, scientific diagnostics, and traceable results. A claim of superiority needs a measured comparison on relevant tasks.

## 4. Target workflow: import → inspect → configure → review → run → results

### Proposed Run analysis interaction

The main button should open **Review analysis**, rather than immediately creating files.

| Review area | What the researcher sees |
| --- | --- |
| Inputs | Explicit list/count of included spectra, with names and temperature/time ranges |
| Processing | Raw versus processed signal; smoothing, corrections, masks and normalization status |
| Methods | Selected methods, fit windows and number of usable points; fixed/free parameters and units |
| Assumptions | Heating-ramp assessment, reaction order, baseline treatment and assumed prefactor |
| Destination | Run name, full folder path, Browse button, and proposed new subfolder |
| Outputs | Tables, diagnostic figures, settings, provenance and run log to be written |
| Readiness | Blocking errors separately from reviewable warnings, each with a concrete action |

Use **Back**, **Preview selected spectrum**, **Run and save**, and **Cancel**. The first run should require an explicit destination choice or confirmation. Later runs may suggest the last folder while still displaying the full destination.

There are two distinct previews:

1. **Setup preview:** inexpensive visualization of data, transformations, ranges and settings; no fit results are implied.
2. **Computed preview:** an explicitly requested calculation for one selected spectrum, using the same engine and settings as the full run, with fitted curve, residuals and warnings. It is labeled as an unsaved preview. Computational work may use a temporary workspace, but creates no final output and never modifies input files.

A settings change marks the computed preview stale. Running must use the exact reviewed settings snapshot. A preview of one spectrum must not be presented as validation of a batch.

Default output organization: one uniquely named run folder per execution, such as `sample-series/run-2026-10-22-001/`. Users can open previous runs without overwriting them. If overwriting is offered at all, enumerate the files affected and require a deliberate decision.

## 5. Checkpoint roadmap

Each checkpoint should have an issue, an owner role, a verification method and a link to evidence. Suggested roles: maintainer, scientific reviewer, independent researcher, and release tester. One person can hold several roles, but an independent check should actually be independent.

### Gate A — Define a trustworthy baseline

Primary owners: maintainer and scientific reviewer. Required before public beta.

- [ ] A01 — Record the supported scientific scope: methods, data types, temperature/time units, ramp assumptions and known exclusions.
- [ ] A02 — Create a method-status table: supported within stated bounds, exploratory, or not supported. Apply it consistently in GUI, README and exports.
- [ ] A03 — Freeze a reproducible baseline with exact commit, build hash, dependency versions, test report and known defects.
- [ ] A04 — Make version/channel/build identifiers agree across executable, About, Python package, citation metadata and output manifests.
- [ ] A05 — Define release-blocking defects: wrong units, misleading scientific claims, silent data/output loss, irreproducible results, core workflow failure.
- [ ] A06 — Consolidate overlapping roadmaps into one maintained priority list; keep old research plans as clearly labeled background.
- [ ] A07 — Maintain an evidence ledger with status, reviewer, date, dataset hash, expected result, observed result and limitations.

**Exit:** someone unfamiliar with development can identify exactly what the candidate supports and what evidence backs it.

### Gate B — Safe, understandable import and data handling

Primary owners: maintainer and scientific reviewer. Essential controls before public beta; wider format coverage can follow.

- [ ] B01 — Preview detected columns, delimiter, decimal notation and units; allow correction when detection is ambiguous.
- [ ] B02 — Require explicit units for ambiguous time/temperature headers. Do not silently treat seconds as milliseconds or kelvin as Celsius.
- [ ] B03 — Show original row count, accepted rows, rejected rows and reasons. Preserve original file and row identity.
- [ ] B04 — Report sorting, duplicate timestamps, missing values and nonfinite values. Make the chosen policy visible and reproducible.
- [ ] B05 — Show raw versus cleaned temperatures and highlight corrected points; provide a controlled way to review or disable heuristic correction.
- [ ] B06 — Separate “Show in plot” from “Include in analysis.” Display both states and the final included count.
- [ ] B07 — Make trimming, masks and processing reversible. Saving a project must preserve those choices without rewriting input CSVs.
- [ ] B08 — Test decimal commas, Unicode filenames, repeated filenames in different directories, sparse sampling, holds, cooling segments and corrupt inputs.

**Exit:** users can explain which measurements were included, excluded or changed and why. Ordinary invalid files produce an actionable error without losing the workspace.

### Gate C — Review, destination choice and safe execution

Primary owners: maintainer and release tester. Required before public beta.

- [ ] C01 — Implement the Review analysis screen described above, with explicit destination confirmation.
- [ ] C02 — Validate settings and destination before creating the final run folder; cancelling leaves no final results behind.
- [ ] C03 — Create unique run folders; test duplicate run names, locked files, read-only folders and interrupted writes.
- [ ] C04 — Snapshot the reviewed datasets, settings and output path when a run starts. Later UI edits cannot change that run's records or completion message.
- [ ] C05 — Add live progress by spectrum and phase, a persistent run log, and a working cancel control. Do not fabricate precise progress percentages for unknown-duration fits.
- [ ] C06 — Distinguish completed, completed with warnings, partially failed, failed and cancelled. Retain useful partial results with their state clearly recorded.
- [ ] C07 — Keep the interface responsive; define close-during-run behavior and ensure child processes do not continue unnoticed.
- [ ] C08 — Add a computed preview for one selected spectrum, with stale-preview detection and tested equivalence to the corresponding full-run result.
- [ ] C09 — Test a mixed batch with valid and invalid spectra, an interrupted run and a rerun. Successful completion must never conceal failed files or unavailable methods.

**Exit:** a user knows what will run and where results will go; cancellation, failures and repeat runs have predictable outcomes.

### Gate D — Scientific equations, assumptions and numerical verification

Primary owners: scientific reviewer and maintainer. Audit each method before presenting it as supported.

- [ ] D01 — Trace every reported quantity to an equation, primary reference, code path, units and applicability conditions.
- [ ] D02 — Audit Celsius/kelvin and minute/second conversions, energy units, reaction-order conventions, coverage definitions and prefactor dimensions.
- [ ] D03 — Resolve the distinction between signal proportional to rate per second and signal per kelvin. Check the role of heating rate in leading-edge intercepts and prefactors.
- [ ] D04 — Do not label an amplitude/intercept-derived value from an uncalibrated arbitrary-unit signal as an absolute physical prefactor unless justified. Relabel or suppress unsupported interpretations.
- [ ] D05 — Present assumed Redhead prefactors explicitly, record their source/user choice, and show sensitivity. A plausible-looking default is not evidence.
- [ ] D06 — Audit leading-edge window validity, depletion and overlap effects, baseline sensitivity, positive-signal masking and reported regression uncertainty.
- [ ] D07 — Show measured temperature versus any fitted linear ramp used in kinetics; quantify deviations and flag unsupported ramps using documented, scientifically justified criteria.
- [ ] D08 — Independently verify integration accuracy, sampling convergence, coverage depletion and conservation for each advertised kinetic model/order.
- [ ] D09 — Test parameter bounds, initialization sensitivity, multiple starts, parameter correlation and non-identifiability. A converged optimizer is not proof of a unique physical answer.
- [ ] D10 — Compare GUI, CLI and API results for identical inputs/settings. Presentation choices such as display normalization must not silently change scientific calculations.
- [ ] D11 — Separate numerical error, regression scatter, parameter uncertainty and experimental/model uncertainty. Never relabel a narrow regression interval as total uncertainty.
- [ ] D12 — Keep exploratory two-state fits, new mechanisms and unvalidated bootstrap intervals clearly separated from supported claims; disable or limit any method whose audit fails.

**Exit:** each supported method has a signed-off evidence record and defined limits. Unresolved scientific defects cannot be waived by attractive plots or successful packaging.

### Gate E — Validation with independent references and measurements

Primary owners: scientific reviewer and independent researchers. A small core set precedes public beta; the full supported-domain matrix precedes stable release.

- [ ] E01 — Define benchmark cases and accuracy criteria before observing results; justify tolerances separately for exact identities, numerical solvers and approximate formulas.
- [ ] E02 — Include independent analytic/numerical implementations, rather than only testing a fitter against its own simulator.
- [ ] E03 — Span the claimed operating domain: isolated and overlapping peaks, heating rates, coarse/irregular sampling, noise, offsets, drift and truncated traces.
- [ ] E04 — Include deliberately unsupported cases and check that warnings or refusal occur; honest failure is an expected result.
- [ ] E05 — Report all attempts, failures and withheld estimates. Summarize bias/error and convergence rates instead of showcasing only successful fits.
- [ ] E06 — Obtain permissioned experimental cases with instrument conditions, calibration, acquisition settings, provenance and uncertainty information.
- [ ] E07 — Reproduce an independent analysis on experimental data with matched assumptions. Explain differences rather than treating agreement as automatically correct.
- [ ] E08 — Repeat analyses with reasonable changes to fitting windows, smoothing, baseline and prefactor. Archive the sensitivity results.
- [ ] E09 — For any future nonlinear intervals, evaluate coverage and issuance rates under the stated conditions before adding them to routine GUI outputs.
- [ ] E10 — Publish a validation report that names the tested version, supported domain, failed cases and remaining limitations.

**Exit:** another researcher can reproduce the benchmark report and understand where the methods work, fail or remain untested.

### Gate F — Results review, export and reproducibility

Primary owners: maintainer and independent researcher. Basic review before public beta; project round-trip and richer comparisons before stable release.

- [ ] F01 — Add a Results workspace with a per-spectrum status table, parameter units, method labels, warnings and links to details.
- [ ] F02 — Place raw/processed signal, model curve and residuals together; distinguish an initial model, a computed preview and a completed fit.
- [ ] F03 — Make warnings actionable: what happened, affected quantity, likely consequence and next check. Use text/icons as well as color.
- [ ] F04 — Show unavailable or unreliable parameters explicitly. Blank cells, zeros and excessive decimal places must not imply certainty.
- [ ] F05 — Save and reopen projects with settings, selections, masks, results, relative input references and hashes. Detect changed or missing source data.
- [ ] F06 — Record software/build version, dependency/solver settings, random seeds when relevant, parameter bounds, fixed/free choices and processing history.
- [ ] F07 — Export readable tables, machine-readable settings/provenance and publication-ready figures with units, legend control and vector output where supported.
- [ ] F08 — Keep logos and promotional text out of scientific figures by default. Put software credit and citation information in the report/metadata.
- [ ] F09 — Compare two runs without overwriting either; display changed settings alongside changed results.
- [ ] F10 — Verify a project can be reopened on another machine and rerun within predefined tolerances. An exported CSV alone is not a reproducible project.

**Exit:** a colleague can follow the path from the measurement to every exported result without relying on the original user's memory.

### Gate G — User experience, accessibility and branding

Primary owners: maintainer and representative users. A coherent minimum before beta; polish based on testing before stable release.

- [ ] G01 — Use one public name: **TPD Spectra Studio**. Retain the repository/package names where useful, and explain the relationship once.
- [ ] G02 — Adopt a restrained palette, consistent spacing, readable type and a small original spectrum/ramp icon. Check the name and identity for confusing similarity before final adoption.
- [ ] G03 — Provide Welcome actions: Open spectra, Open project, Try synthetic demo and Quick start. The demo opens inside the application and remains unmistakably labeled synthetic.
- [ ] G04 — Give each workspace a clear purpose and primary next action; expose advanced settings progressively without concealing assumptions that affect interpretation.
- [ ] G05 — Add contextual explanations, units and examples beside fields; invalid values identify the exact field and fix. Avoid making essential help hover-only.
- [ ] G06 — Implement About, citation, documentation, release notes and issue-report links. Avoid unverified affiliations, institutional logos or contributor credits.
- [ ] G07 — Test keyboard-only operation, focus order, screen-reader access where supported, contrast and non-color warning cues.
- [ ] G08 — Test a smaller laptop display and 100%, 150% and 200% Windows scaling. Check dialogs, long paths, mathematical symbols and overflowing text.
- [ ] G09 — Observe at least 3–5 representative users completing predefined tasks without coaching. Treat this as formative testing, not a statistically representative study.
- [ ] G10 — Record completion, errors, requests for help and misunderstandings. Fix every observed critical misunderstanding about inputs, methods, processing or saved results, then retest.

**Proposed usability targets:** a new user can open the demo and export a plot within five minutes using the supplied guide, and complete a reviewed analysis within ten minutes without verbal assistance. These are product goals to test, not current measured performance.

**Exit:** users can find results and correctly explain which data/method/settings produced them. A polished appearance must not imply stronger scientific validation than exists.

### Gate H — Distribution, maintenance and public presentation

Primary owners: maintainer and release tester. Required for a supported public release.

- [ ] H01 — Provide a stable GitHub Releases download path and plainly labeled stable/beta channels. Do not make expiring CI artifacts the permanent public download system.
- [ ] H02 — Test the release on a clean Windows machine without Python, administrator access or network access during analysis, including a non-English username and path with spaces.
- [ ] H03 — Pin/record the tested build environment, retain checksums and dependency information, and run automated tests against the packaged executable.
- [ ] H04 — Review code/data/example/icon licenses and bundled dependency notices. Keep clear software licensing and separate asset-provenance records.
- [ ] H05 — Assess executable signing for a professional Windows distribution; if unsigned, state this clearly and never instruct users to disable security protections.
- [ ] H06 — Supply installation, first analysis, method reference, troubleshooting and developer documentation with screenshots of the actual release.
- [ ] H07 — Add issue templates for import bugs, crashes and scientific concerns. A diagnostic bundle should be previewable and exclude raw data and personal paths unless the user chooses to include them.
- [ ] H08 — Document support expectations, supported platforms, compatibility policy and how scientific-output corrections are announced.
- [ ] H09 — Add versioned project schemas and migration tests; keep a way to inspect older results without silently recalculating them under new assumptions.
- [ ] H10 — Establish a release checklist, critical-fix process and known-issues page. Protect stable releases from speculative integrations.

**Exit:** a new user can obtain a specific release, verify which build they have, get started, report a problem and recover prior work.

### Gate I — Citable release and software-paper readiness

Primary owners: maintainer, scientific reviewer and human authors.

- [ ] I01 — Archive an accepted tagged release and its source, release notes and validation materials; distinguish the software DOI from any paper DOI.
- [ ] I02 — Synchronize `CITATION.cff`, archive metadata, author spelling, release version and dates. Add ORCID/affiliation only after confirmation.
- [ ] I03 — Write an evidence-based statement of need and comparison with relevant existing tools. Document why a separate project is justified.
- [ ] I04 — Preserve actual research-use evidence and feedback-driven development. Do not manufacture community engagement or development history to meet publication criteria.
- [ ] I05 — Document architectural decisions, scientific review, contributor roles and unresolved limitations.
- [ ] I06 — Check the target venue's current eligibility and submission rules at the time of submission.
- [ ] I07 — Prepare the manuscript from the released, evaluated functionality; clearly separate future plans from current capabilities.
- [ ] I08 — Record AI assistance accurately and obtain genuine human review of the scientific claims, code and manuscript before making any review assertion.

**Current JOSS planning constraint:** its submission guidance requires more than six months of active public repository history, demonstrated research use and responsible disclosure of AI assistance. Eligibility is not guaranteed by meeting a checklist. Its policy also limits AI use in author–editor/reviewer conversational exchanges. Re-check before submission. [JOSS submission guidance](https://joss.readthedocs.io/en/latest/submitting.html)

JOSS also examines licensing, documentation, tests, installation and contribution/support pathways. [JOSS review criteria](https://joss.readthedocs.io/en/latest/review_criteria.html)

A versioned archive can make the software citable before a journal paper; Zenodo supports software version records and GitHub release archiving. [Zenodo software archiving](https://blog.zenodo.org/2024/10/21/2024-10-21-swh/)

**Exit:** a specific software contribution is supported by inspectable evidence and sustained use; the selected venue's requirements are satisfied.

## 6. Proposed About and brand presentation

The public-facing name should remain **TPD Spectra Studio**, with the descriptor **Reproducible analysis of temperature-programmed desorption spectra**. This is a proposed positioning statement; reproducibility must be demonstrated through the project/export workflow.

About should contain:

- App name, small icon, exact version, release channel and build identifier populated automatically.
- Purpose in one sentence and a concise description of supported methods.
- Creator/maintainer credit: **Karol Cieślik**, using the maintainer’s preferred public name, with contributor acknowledgments reviewed before release.
- GitHub repository, documentation, report-an-issue and release-note links.
- Copy citation and copy diagnostic/build information actions.
- License and third-party acknowledgments.
- A short statement that outputs depend on selected models, assumptions and input quality.

Suggested body copy:

> TPD Spectra Studio helps researchers inspect, compare and analyze temperature-programmed desorption spectra. Review data processing, model assumptions and diagnostic warnings before interpreting kinetic parameters.
>
> Created and maintained by Karol Cieślik.
>
> Source code, documentation and issue reporting: github.com/karol-cieslik/TPD-Spectra-Analysis
>
> If you use this software in research, cite the version used and report your analysis settings.

The About window should be accessible through Help → About, with a compact version link in the footer. It should not interrupt normal analysis. Exported scientific plots should remain clean by default.

For the repository front page, use this order: purpose and audience; one real screenshot; download; five-minute demo; supported methods and limitations; examples of outputs; validation evidence; citation; support/contributing; release history. Avoid decorative badges or claims that do not help a researcher decide whether the tool fits their work.

## 7. Execution sequence and definition of done

Start with small, reviewable changes rather than a large redesign:

1. **Review and save workflow:** explicit analysis selection, settings snapshot, destination choice, unique run folder and cancellation-without-output tests.
2. **Execution and results:** live log, progress/cancel, partial-failure summary and a minimal Results workspace.
3. **Scientific audit:** equations/units, prefactors, processing and ramp reconstruction; repair or restrict questionable outputs before adding methods.
4. **Project reproducibility:** save/reopen, source hashes, versioned settings and run comparisons.
5. **Onboarding and About:** built-in demo, concise help, consistent version/branding and actual screenshots.
6. **Independent testing:** benchmark evidence plus researcher usability sessions; use observed problems to set the next iteration.
7. **Release preparation:** clean-machine test, licensing/signing decisions, versioned assets, citation and documentation checks.
8. **Research adoption and publication:** accumulate genuine use, maintenance history and independent feedback; submit a software paper when evidence and eligibility permit.

The first workflow prototype can be organized as one short iteration, followed by testing and refinement. Scientific review and access to experimental data may take longer than interface work; no release date should be promised until those dependencies are known.

For every change, define: user problem; scientific implications; acceptance criteria; test evidence; documentation update; release-note impact; and the reviewer. Keep the known working beta available. Separate experimental science from release maintenance. Update the evidence ledger whenever behavior or dependencies change.

Defer a Qt rewrite, cloud accounts, automatic model selection, advanced baseline algorithms, new kinetic mechanisms, Bayesian fitting and a large marketing site until evidence shows they are needed. Revisit the UI framework only after measuring accessibility, responsiveness or maintainability limits in the current one.

The release decision should answer three questions with evidence: can an unfamiliar researcher use it, can another scientist audit its results, and can someone else reproduce and maintain the workflow?


## 8. Added Explorer / Monte Carlo work

The user requested integration of the work in PR #8 on 22 October 2026. See [the Explorer guide and M01–M10 checkpoints](EXPLORER_MONTE_CARLO.md), [method status](METHOD_STATUS.md) and the evidence ledger. This is parametric refitting under an iid Gaussian noise model, not microscopic kinetic Monte Carlo or Bayesian MCMC. Implementation does not establish interval coverage, physical mechanism probabilities or external experimental validity.
