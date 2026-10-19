# Development roadmap — reliable, reusable TPD research software

**Status:** active single-source development plan · 2026-10-19  
**Guiding objective:** Build reliable, scientifically defensible TPD/TDS software that experimental researchers can install, understand, reproduce, and extend. A peer-reviewed software article should document a real contribution supported by evidence. The public product exists to solve researchers' problems, not to obtain a paper.

This roadmap supersedes the *priority order* of the exploratory GUI and scientific planning documents. It does not erase their technical backlogs. Plans indicate intent, not completed validation.

## Decision filter (apply to every issue or PR)

1. Does it correct an actual defect, scientific risk, or reproducibility gap?
2. Does a representative researcher need it for the documented analysis workflow?
3. Can its behavior be tested independently and explained scientifically?
4. Does it reduce or increase maintenance and portability burdens?
5. Is it essential before the next release, or safely deferrable?

Avoid new functionality during the beta stabilization window unless needed to fix a blocking problem.

## Priority 0 — Stop release blockers / beta acceptance

**Target:** v0.11 public beta once acceptance gates pass. **Branch:** `release/beta-v0.11-candidate` (PR #5).

| Priority | Task | Done when |
| --- | --- | --- |
| P0 | Verify exact candidate build and version | GitHub CI green for final commit, artifact downloadable, package/metadata/release label consistent |
| P0 | Windows acceptance on real machine | Import, view, plot selection, kinetic fit, errors, PNG/results, restart all pass |
| P0 | Scientific output sanity | At least one known spectrum gives coherent heating rate, fit windows, results and diagnostics |
| P0 | Fix integration defects | Reproducible bug fixed with regression test, no unintended changes in core calculations |
| P0 | Reproducible demo | Freely redistributable synthetic dataset, expected values, step-by-step example and output verification |
| P0 | Distribution compliance | License, asset-rights and third-party notices checked; no protected spectra bundled |
| P0 | Finalize release version | Bump project metadata only when release is approved, add release notes, tag and archive final artifact |

**Do not merge to main** solely because CI passes. Manual Windows review is still mandatory. A CI success on an earlier commit does not validate subsequent commits.

## Priority 1 — Colleague-ready, developer-ready tool

**Target:** a researcher unfamiliar with the project can complete the core workflow; a new contributor can reproduce tests and fix a bug.

- [ ] Give 2–3 colleagues a small redistributable test package and a five-minute Quick Start.
- [ ] Capture their success/failure, workflow confusion and reproducible issues.
- [ ] Resolve critical UX defects; defer cosmetic redesign and Qt migration.
- [ ] Keep parser, scientific engine and GUI concerns separated, with stable documented inputs/outputs.
- [ ] Confirm a clean Python environment and Windows standalone packaging; add cross-platform CI where practical.
- [ ] Add issue templates, contribution examples, and a short programmatic API tutorial.
- [ ] Establish deprecation and backward-compatibility policy for CSV, CLI, API and exported metadata.

**Exit criterion:** two independent users complete an analysis, and an external developer can run tests without private data.

## Priority 2 — Scientific evidence (work separately; promote only validated changes)

**Target:** error characterization, reproducibility and clearly bounded claims.

- [ ] Complete a physical-units and solver audit: temperature and heating rates, zero-order depletion, prefactor dimensions, integration accuracy, preprocessing.
- [ ] Generate and archive numerical benchmark tables for zero/first/second/noninteger orders, different ramps, peak overlap, signal noise and baseline drift.
- [ ] Include independent analytic/numerical reference cases so results are not validated exclusively against the same software.
- [ ] Establish trial denominators, convergence/failure accounting, parameter-recovery bias/RMSE and residual diagnostics.
- [ ] Curate a small independent experimental dataset with provenance, permissions, digitization effects and measured-data limitations.
- [ ] Record fit-window, baseline, assumed-prefactor and calibration sensitivity.
- [ ] Evaluate nonlinear confidence-interval coverage *and issuance/withholding rates* before adding bootstrap intervals to standard GUI outputs.

**Boundary:** experimental bootstrap, broad new models, uncertainty variants and research scripts remain on PR #2 or later research branches until independent evaluation. No unvalidated uncertainty estimates in default beta outputs.

## Priority 3 — Citable, maintainable software and scientific communication

- [ ] Issue a tagged, reproducible and archived version with accurate citation metadata.
- [ ] Document the architecture, assumptions, data schemas, example workflow, limitations and test strategy.
- [ ] Write an evidence-based statement of need and comparison to alternative workflows/software.
- [ ] Track real user feedback, scientific examples and maintainer contributions.
- [ ] Verify journal eligibility and prepare a concise article describing a finished research software contribution; cite released results and primary methods.

**Publication is downstream of software quality** and should not dictate inappropriate features or premature scientific claims.

## Branch consolidation policy

- `main` — current stable release, protected from unfinished work.
- PR #5 / `release/beta-v0.11-candidate` — only release fixes, developer readiness, tests and documentation.
- PR #3 / `feature/gui-usability` — upstream GUI history; core Phase 1–3 improvements already included in PR #5; avoid merging it a second time.
- PR #2 / `feature/kinetic-identifiability-diagnostics` — ongoing scientific research; only tested identifiability pieces transferred to beta; bootstrap/coverage research excluded.
- PR #1 and PR #4 — audits and reference material; selectively reconcile documentation into the beta, avoiding duplicate conflicting sources.
- After acceptance: merge beta via reviewed PR, then rebase/close obsolete overlapping PRs deliberately. No automatic mass merge.

## Deferred feature parking lot (not pre-beta)

Qt/PySide migration; kinetic-model wizard; complex baseline correction; real-time fit/residual dashboard; additional kinetic mechanisms; Bayesian fit; advanced uncertainty displays; extensive plot redesign. Reconsider only in response to demonstrated user needs or validation requirements.

## Weekly maintenance rhythm

1. Review CI, actual user defects and scientific red flags.
2. Choose at most 1–2 high-impact, independently testable changes.
3. Require regression tests, documentation and release note impact for merged changes.
4. Keep one demonstrable, working candidate; no speculative integration.
5. Record benchmark results as datasets/files, not only descriptions in chat.

## Reference documents

- [User and Scientific Methods Manual](USER_AND_SCIENTIFIC_MANUAL.md)
- [Beta Acceptance Checklist](BETA_ACCEPTANCE_CHECKLIST.md)
- [Release and Publication Gates](RELEASE_AND_PUBLICATION_GATES.md)
- [Contributor Guide](../CONTRIBUTING.md)

The scientific roadmap and GUI roadmap document possible *future* improvements; this file controls their priority and release timing.
