# Merge and robustness roadmap for TPD Spectra Studio

**Checkpoint context (31 October 2026):** This roadmap was prepared while PR #27
was under review. Its branch included the O₂/Pt(111) challenge, literature
assessments, research-only variable-projection/profile diagnostics, and the
fractional-order candidate ledger. The work has since been consolidated into
`main` for integrated user testing. This merge is not a scientific acceptance
or release claim.

The original goal was to merge a reviewable, scientifically bounded change,
then improve robustness using evidence that can be reproduced from retained
inputs. A passing software test is not a successful experimental validation.

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
| 8. Merge | Consolidate the bounded assessment and research-only diagnostics into `main` for integrated user testing. | Merged for testing; independent scientific review and clean-machine Windows acceptance remain open and are not implied by the merge. |
| 9. Post-merge release | Tag only after clean-install, GUI/CLI/Python workflow, provenance, and changelog checks. Publish a stable release and reviewer reproduction command. | Do not describe the merge as a validated release until the release checks pass. |

## Recommended sequence after integration

1. **Test the integrated main branch.** Run existing CI and frozen-input
   regression checks. Do not add model features to resolve empirical
   disagreement before reviewing the resulting diagnostics.
2. **Acquire another usable fractional-order trace series.** The 2-propanol/HOPG
   Fig. 2A comparison is now retained as figure-derived evidence. Consider
   ethanol/HOPG after resolving reuse rights; methanol/HOPG remains blocked by
   scan quality. Compare source and whole-trace estimators as distinct methods.
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


## Progress record — 31 October 2026

| Gate | Result | Evidence / remaining condition |
|---|---|---|
| 0. Snapshot | Passed at the recorded pre-merge checkpoint | PR #27's recorded head was `e3e640f7a214e2190511b27aea8d67ae1b8c3b48`; the local tree was clean and matched the remote tree. Its 41-file diff covered the O₂/Pt(111) study, research prototypes, validation records/catalog and manuscript updates. |
| 1. Scientific scope | Passed with boundary | Variable projection, E–ν profiling and sloped baseline are isolated research prototypes; no `tpd_spectra` production path imports them. The default fitter is unchanged. |
| 2. Provenance and rights | Passed for catalog labeling | The central manifest has 14 entries and every canonical path exists. Candidate figures with unavailable pixels remain `not_ready`; external O₂/Pt(111) workbooks are not copied because reuse permission is not recorded. |
| 3. Reproducibility | Passed for CI; local full suite unavailable | On head `da983ef`, GitHub “Kinetics Explorer scientific tests” run 128 and “Windows desktop build” run 81 both completed successfully. Local compile checks, catalog-path validation and `git diff --check` passed. Full local pytest could not start because this runtime has no `pytest` module. |
| 4. Data readiness | Passed for inventory, not universal coverage | Tracked datasets are discoverable through `validation/publication_data/README.md` and `dataset_manifest.csv`. Four fractional-order leads still have no admitted numeric arrays; uniform empirical coverage is not achieved. |
| 5. Manuscript audit | Partial | `paper.md` now records the bounded O₂/Pt(111), variable-projection and profile/baseline findings; citation rendering with Pandoc and `paper.bib` succeeded. Human author/citation review and full submission checks remain. |
| 6. Independent review | Open | CI Windows build passed, but no independent surface-science review or clean-machine Windows acceptance is recorded. CI packaging is not equivalent to human acceptance on a clean Windows machine. |
| 7. Merge | Merged for integrated user testing | The bounded work is consolidated into `main`; no independent scientific review or clean-machine Windows acceptance is claimed. |
| 8. Release | Not started | Requires post-merge package, clean-install, GUI/CLI/Python workflow, provenance and release checks. |

A mergeable flag only means GitHub sees no merge conflict. The merge supports
integrated testing; human scientific review and Windows acceptance remain
separate project gates.
