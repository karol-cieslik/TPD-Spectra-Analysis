# Consolidation into main — 0.11.0b3 beta

The integration baseline is `8cda380b6869d58505d9d560ddbd7f53fa26b864`,
the verified external-beta branch. Current main (`01ebb4749c5ba3810f9eb53b171ee10686e20592`)
is its ancestor. This consolidation preserves the existing application,
synthetic references and numerical engines, including the corrected fixed-zero-order
path. It does not declare a stable release or complete experimental validation.

## Disposition of existing pull requests

| PR | Contribution | Consolidation treatment |
| --- | --- | --- |
| #1 | Scientific uncertainty audit | Original dated audit retained in `SCIENTIFIC_AUDIT_UNCERTAINTY.md`; historical observations are not current feature claims. |
| #2 | Identifiability and research uncertainty/benchmarks | Existing diagnostics retained unchanged. Unique benchmark scripts, tests and opt-in bootstrap API imported. Bootstrap rejects zero order and excludes warned refits; benchmark exports retain zero-order brackets rather than scoring an arbitrary prefactor. |
| #3 | Guided GUI | Already an ancestor of the baseline; current GUI retained. |
| #4 | Living scientific reference and roadmap | Both documents retained; technical status reconciled with current zero-order and diagnostics implementation. |
| #5 | Reviewed beta analysis workflow | Already contained in the baseline, with subsequent fixes preserved. |
| #7, #8 | Original Explorer and integration | Already ported and improved in the baseline. Older variants omit cancellation, failed-ranking accounting and uncertainty safeguards; current implementation and tests retained. Existing order-example files retained. |
| #9 | Literature validation candidates | Catalog, extraction notes, digitization guide and README imported from `95fc44f941d197bf60912341b2afac769e601c88`. These are 26 candidate publications, not completed external validation. No outreach is performed. |
| #10 | Three-stage workflow | Already contained in the baseline. |
| #11 | External beta package and equations | Already contained in the baseline. |
| #12 | Zero-order correction | Baseline includes correction and verified build evidence. |

Original branches remain available. Superseded PRs can be closed after successful
integration; their discussions and commit histories remain accessible. Unique
files were imported selectively so older versions cannot overwrite later fixes.

## One build path

`desktop-build.yml` is the reusable test/build/package/verification workflow.
Both main builds and release preparation call that path. Artifacts retain the
explicit `beta` label and application version; branch name never implies stability.
Tagged release preparation requires an exact `v<application version>` match,
then creates only an unpublished prerelease draft using the verified package.
This consolidation creates no release tag and publishes no release.

Main is the default development branch. Start future changes in short-lived
branches and merge reviewed, tested PRs. Keep the current working beta branches
as recovery references. The main README directs users to main's successful build.

## Validation and remaining gates

The combined tree must pass the full Windows scientific/GUI suite, Python
3.10–3.12 tests and packaged CLI/GUI/workflow/Monte Carlo/zero-order/resource checks
before merge. Exact build evidence is recorded separately after completion.
The post-merge main build must also pass before its download is recommended.

Manual clean-machine Windows layout/scaling acceptance, independent experimental
validation and uncertainty-coverage studies remain open. Legacy multi-state/global
zero-order fitting remains experimental. Research tools in
[RESEARCH_TOOLS.md](RESEARCH_TOOLS.md) do not expand the desktop's validation claims.
