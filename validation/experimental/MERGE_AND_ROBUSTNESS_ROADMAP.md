# Merge and robustness roadmap for TPD Spectra Studio

**Current state (31 October 2026):** PR #27 is open against `main`; its latest
published head is `d251f18`. The local tree is synchronized with that remote
snapshot. The PR includes the O₂/Pt(111) challenge, literature assessments,
research-only variable projection/profile diagnostics, and the fractional-order
candidate ledger. This roadmap does not authorize merging by itself.

The goal is to merge a reviewable, scientifically bounded change, then improve
robustness using evidence that can be reproduced from retained inputs. A passing
software test is not a successful experimental validation.

## Checkpoints

| Gate | Checkpoint and evidence required | Merge decision |
|---|---|---|
| 0. Snapshot | Record the PR head, target branch, clean working tree, CI state, and complete changed-file list. Confirm no unrelated work is included. | Stop if the target branch advanced or the diff includes unexplained files. |
| 1. Scientific scope | Keep current production behavior unchanged unless a specific production defect is reproduced. Label variable projection, profiled E–ν diagnostics, and linear baseline as research-only. Preserve limitations and negative results. | No production/default fitter replacement in this PR. |
| 2. Provenance and rights | Review `validation/publication_data/README.md` and its manifest. Every retained trace must identify DOI, figure or source table, units, heating rate, license/reuse status, extraction method, uncertainty, and canonical path. Unavailable traces remain source leads, not datasets. | Remove or quarantine any item with unresolved provenance or rights; do not redistribute source workbooks without permission. |
| 3. Reproducibility | Run the exact commands listed in each study protocol in a clean environment. Verify input hashes, output hashes where stable, and that no script downloads or silently modifies source files. | Require reproducible results for every claimed completed case. |
| 4. Regression and packaging | Run the project's full existing CI/test matrix, package/build checks, and CLI/API smoke tests. Compare default fitter outputs before and after this branch on frozen reference inputs. | Require no regression; document platform-specific gaps. |
| 5. Data-readiness review | Confirm the catalog's “ready” files are tracked and scripts can load them from repository-relative paths. Confirm external licensed/restricted inputs are fetch/refer-only and their absent status is explicit. | Do not claim every order class is tested while candidate traces are unavailable. |
| 6. Manuscript audit | Align `paper/paper.md`, `paper/paper.bib`, dataset catalog, study records, and PR description. State what was measured, what was digitized, what was only screened, and what the optimizer did not establish. | Require author review of claims, citations, AI disclosure, affiliation, and actual research-use statement. |
| 7. Independent review | Ask one surface-science reader to check kinetic assumptions and one clean-machine reviewer to check install/open/import/fit/export. Record names/roles only with consent and capture the exact build/commit. | Human scientific and Windows acceptance remain separate gates. |
| 8. Merge | Review CI and conversations, confirm no unresolved blocking review, then merge PR #27 using the repository's normal process. | Merge only after Gates 0–7 pass or gaps are explicitly accepted as non-blocking. |
| 9. Post-merge release | Tag only after clean-install, GUI/CLI/Python workflow, provenance, and changelog checks. Publish a stable release and reviewer reproduction command. | Do not describe the merge as a validated release until the release checks pass. |

## Recommended sequence after this PR

1. **Finish the merge review first.** Run existing CI and the frozen-input
   regression comparison. Do not add more model features to resolve empirical
   disagreement.
2. **Acquire one usable fractional-order trace series.** First try authorized
   ethanol/HOPG or the openly licensed 2-propanol/HOPG source; methanol/HOPG
   remains blocked by scan quality. Digitize only after visual trace review,
   preserving every calibration and uncertainty artifact. Compare fixed-order,
   free-order and the paper's own coverage-slope estimator as different methods.
3. **Add one positive full-peak reference and one resolved zero-order edge.**
   Freeze expected conditions and comparison tolerances before fitting. Keep
   mismatches as results rather than tuning them away.
4. **Test baseline/window sensitivity on at least three distinct experimental
   sources.** Keep linear baseline research-only unless residual inspection and
   source physics support it; lower residual alone is insufficient.
5. **Evaluate identifiability before adding automatic fitting.** Profile order,
   energy and prefactor; quantify digitization perturbations and correlated
   residual effects. Do not turn profile ranges into confidence intervals
   without calibration.
6. **Only then consider broader algorithms.** Multi-trace shared-parameter fits
   are the next high-value extension if matched coverage/heating-rate series
   are acquired. Energy-distribution inversion and automatic peak proposals
   stay out of the production path until synthetic resolution, uncertainty,
   and false-positive performance are demonstrated.

## Definitions of ready-to-test data

A publication is “ready for later tests” only when the catalog points to a local,
tracked numeric file that has passed a source-overlay review. A paper summary,
reported order, or inaccessible graph is not ready data. Digitized curves remain
figure-derived data with correlated pixel uncertainty, not raw instrument
samples. Keep raw public/reuse-permitted data unchanged; place processed arrays,
QA overlays, and protocols beside them. For restricted data, keep a script and
instructions to acquire it from its source, not a copied workbook.
