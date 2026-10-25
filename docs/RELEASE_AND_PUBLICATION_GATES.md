> **Archived release-gate plan.** This captures the development state before the 0.11.0b3 consolidation into `main`. For the current beta, consult [METHOD_STATUS.md](METHOD_STATUS.md) and [the release notes](beta/RELEASE_NOTES.md). Unchecked items here are not necessarily outstanding in the current version.

# Release and publication gates

This document records the project priority: **a reliable working program, usable by other scientists and maintainable by external developers, with evidence sufficient to support a software paper**.

## Phase A — Beta acceptance (current)

- [x] Assemble GUI changes and selected scientific diagnostics on a separate candidate branch.
- [x] Automated regression tests and Windows packaging completed successfully at least once.
- [ ] Confirm the most recent beta commit's CI results and downloadable artifact.
- [ ] Test Windows executable on a real computer, including launch, CSV import, plot interaction, fitting, output export and restart.
- [ ] Confirm the artifact and effective `__version__` / `pyproject.toml` version agree with any release label.
- [ ] Resolve release-blocking crashes or incorrect scientific outputs.
- [ ] Produce at least one fully reproducible worked example using redistributable synthetic data.
- [ ] Confirm distribution notices and third-party rights.

## Phase B — Developer-ready open source

- [x] Add project architecture and contribution instructions.
- [ ] Add a small documented programmatic example of model fitting, with pinned assumptions.
- [ ] Add CI for at least two operating-system environments where practicable, plus packaging smoke checks.
- [ ] Establish regression performance tolerances and test warnings and exports.
- [ ] Create issue templates and triage labels for bug reports, scientific concerns and new features.
- [ ] Release a versioned tag after acceptance; retain build logs and immutable reference.
- [ ] Run a clean-room setup and contribution test by someone other than the maintainer.

## Phase C — Scientific evidence

- [ ] Verify analytical benchmark results against independent numerical calculations, not only the software's own simulator.
- [ ] Archive parameter-recovery cases spanning zero/first/second/non-integer order, heating rates, overlaps, noise and drift.
- [ ] Document accuracy, reproducibility, failures and physical identifiability limits.
- [ ] Collect representative real spectra with DOI/source, permission, digitization methodology and uncertainty.
- [ ] Compare results to published or independently reproduced reference calculations.
- [ ] Document sensitivity to fit window, heating rate, assumed prefactor and baseline.
- [ ] Evaluate nonlinear uncertainty calibration before turning on bootstrap confidence intervals for users.

## Phase D — Paper readiness

- [ ] Verify journal scope/eligibility and repository public history at submission time.
- [ ] Write an accurate statement of need and comparison with existing tools.
- [ ] Check all cited primary sources and mathematical claims.
- [ ] Include evidence of real-world use and independent feedback.
- [ ] Create a versioned release/archived DOI and update `CITATION.cff`.
- [ ] Prepare a JOSS-length manuscript referencing the tagged source, technical manual and archived benchmarks.
- [ ] Resolve contributor and paper-author details, acknowledgments and institution affiliations.

## Development policy

Until Phase A passes, make only test, documentation, reproducibility and release-blocker changes in the beta branch. Keep experimental nonlinear bootstrap and new scientific models separate; promote them only after independent evidence. Do not merge draft PRs into `main` without review, checks and release acceptance.

## Definition of done

**Working beta:** researcher can install, import, analyze, inspect warnings and export without assistance.  
**Reusable scientific tool:** another developer can reproduce the environment, tests and sample analysis and contribute a verified fix.  
**Publishable software:** public, citable release supported by real usage, independent scientific validation, complete limitations and a defensible manuscript. Passing unit tests is necessary but not sufficient.
