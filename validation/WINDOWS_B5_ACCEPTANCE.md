# Windows research beta b5 acceptance — 27 October 2026

## Preserved source and integration review

Both existing local repositories were clean before work. No synced `sources/`
files or historical output artifacts were changed. A new local branch,
`release/windows-research-beta-b5`, starts at the exact pushed PR #20 commit
`9df4a990626a604269f91a3068395384d25e3716`.

- PR #19: draft/open, `fix/beta-feedback-14-17`,
  `7139c46596b1cebd6adddbdae7ca7cf18972d13b`, base `main`.
- PR #20: draft/open, `ux/results-readable-beta`,
  `9df4a990626a604269f91a3068395384d25e3716`, base PR #19's branch.
- Main: `f44bc4d72aa76e60669a9cf44bee9f6abbd4c40c`.
- GitHub reports both mergeable. Local `git merge-tree --write-tree origin/main`
  against PR #20 succeeds with tree `02f9eb15392167a49aa3291bc3f0651a9b874ec3`.
- PR #20 adds presentation/help/tutorial modules and extends the existing smoke
  path. It does not alter the numerical engine, fit serialization or ranking.
  The five tutorial tabs replace the old popup; the brief PDF remains a separate
  compact guide. Model-component and Monte Carlo results remain in Modeling.

Proposed merge sequence, requiring Karol's approval: merge #19 into main with a
merge commit, preserving ancestry; retarget #20 to main, check its diff contains
only the follow-up work, rerun checks, then merge #20. Apply/review the b5
packaging follow-up afterward (or first fast-forward it into #20 and rerun CI).
Squashing #19 changes ancestry and requires additional care rebasing #20.
No merges, branch rewrites, release publication or colleague messages occurred.

## Confirmed corrections in b5

- Removed the worked tutorial's obsolete b4 artifact download instruction in
  both Markdown and HTML; b5 explicitly includes PR #20.
- Added missing handoff and scientific-audit documents to the portable ZIP.
- Enabled Windows frozen-build checks for PRs targeting the stacked #19 branch.
- Added Windows PE version/commit metadata and a clean-source build identity
  guard. CI-generated test XML is excluded from that source-cleanliness guard.
- Scientific algorithms, kinetic assumptions and uncertainty definitions are
  unchanged. Regression tests guard the tutorial, package links and CI wiring.

## Acceptance evidence

Executable source: `07f59afebe95111386fa2945d5fac79db9b70b59` (includes
`5a094ea32e23df0cd6dc7ec7ae88861fc06fc119` packaging follow-up). Version:
`0.11.0b5`. Built locally on Windows with Python 3.12.14 / PyInstaller 6.22.3.
PE machine `0x8664` (AMD64); FileVersion and ProductVersion `0.11.0b5`;
PE Comments and portable VERSION.json both identify that exact source commit.
Executable size: 86,671,426 bytes. Executable SHA-256:
`dc6b51e69eda1f7afc03bfd960d8b5a7e0ccde3d379600a7aa309e61ab1968d5`.

### Tests actually executed

- Full real Windows/Python 3.12 suite: **343 passed**, no failures/errors/skips,
  272.60 s. `output/b5-final-tests.xml` and `.log` record the final source run.
- Targeted component-editor suite: **5 passed**, including 1.333 and 2.0 Tk
  scaling, scroll-to-Help invocation, visible primary actions and context guards.
- `scripts/verify_windows_build.py`: **PASS** against the new frozen executable:
  embedded six-size Studio icon, CLI analysis/reference energy and plots;
  real Tk dialogs, Explorer fits/short MC/exports; three-stage workflow,
  simulation, comparison, two completed MC refits and cancellation of a real
  500-replicate worker after progress begins, retaining previous results;
  explicit PW fit, saved results/project roundtrip and PDF/CSV/JSON/PNG/SVG.
- `scripts/verify_beta_package.py`: **PASS** from an unrelated working directory,
  with Python/Tcl path overrides removed; 21 synthetic imports, 40 Help topics,
  five Quick Start tabs, Redhead example, zero-order fit/conditional ranges,
  three-component fit, summed curves/residuals, editor, project and individual
  parameter exports. No Tk callback errors. Privacy preview/copy/ZIP passed;
  no external drafts opened, no report sent, no spectra attached.
- GitHub's existing PR #20 checks at `9df4a990...`: Python 3.10, 3.11 and 3.12
  **success**, [run 40462151732](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40462151732).
  Those are prior-source checks, not claims that b5 was rerun on those versions.

Earlier failed attempts are preserved in `output/`: sandbox Tcl access failed;
unsandboxed tests initially reused a sandbox-owned pytest temp directory;
then 341 passed / 2 failed on the pre-existing all-buttons-visible assertion,
which incorrectly included new Help buttons inside a scrollable area. The
corrected test retains primary-action bounds checks and additionally scrolls
and invokes Help at both scaling settings. The first isolated build used a
relative version-resource path interpreted relative to the spec directory;
that attempt failed and was never distributed. The final build used absolute
resource paths. Assembly's final console print hit cp1252 on the author's name;
all files were already written, and package checks subsequently passed.

### Actual executable acceptance matrix

| Requested workflow | Automated frozen result | Interactive/visual result |
|---|---|---|
| First launch/default spectrum/70–210 °C first region | PASS; raw trace retained | Process/window launched and title identified; appearance unverified |
| Peak selection; Selection → Modeling → Results | PASS; context isolation and two regions | Unverified |
| Redhead example and fitted/assumed/derived labels | PASS Redhead; semantic/clipboard tests pass in source GUI | Visual readability unverified |
| Polanyi–Wigner example | PASS first-order and zero-order fits | Unverified |
| Simulation and model comparison | PASS | Unverified |
| Monte Carlo progress, completion and cancellation | PASS real worker; previous result retained | Visual progress/readability unverified |
| Three overlapping physical components | PASS entire-spectrum fit, sum/residuals, project and exports | Unverified |
| Scientific Help/parameter explanations/Quick Start | PASS 40 topics/search/field Help and five tabs | Visual layout/navigation unverified |
| Results tables and residual plots | PASS source GUI table roles and frozen plots/exports | Readability unverified |
| Saving/reopening projects and report exports | PASS actual executable | Export-dialog interaction unverified |
| Feedback preview/privacy | PASS copy/ZIP, redaction and no spectra; no submission | Dialog readability unverified |
| Resize/display scaling | PASS source Tk layout at tested sizes and 1.333/2.0 | Actual executable on different DPI displays unverified |

Visual automation was attempted on the actual b5 window. Windows Computer Use
returned `FrameArrived timed out: timed out waiting on channel`; refreshed
window selection and the permitted retry returned `window capture timed out:
timed out waiting on channel`. No screenshot or interactive workflow was
successfully inspected. **Visual Windows acceptance did not pass.** This is a
capture limitation, not evidence of an application failure.

### Readiness and remaining limits

No first-run application blocker is known from automated frozen checks. The
package is a candidate for a controlled colleague pilot, **conditional on a
human visual first-run/DPI check**; it is not acceptance-complete for general
circulation. Clean-machine Windows 10/11 without Python remains untested. This
host has Python installed, although the frozen package runs without source CWD
or Python/Tcl path overrides. Unsigned-executable handling remains subject to
the tester's institution policy; no security settings were altered.

No scientific algorithms, kinetic assumptions, fitted parameters or uncertainty
interpretation changed in this follow-up. Synthetic recovery does not establish
experimental validity. Fixed component order/prefactor/coverage, independent
populations and linear ramps remain assumptions; local intervals are conditional
and can be withheld. Joint component MC and multicomponent zero-order fitting
remain unavailable; count ranking is heuristic, not mechanism probability.
Independent experimental validation and uncertainty-coverage validation remain
later milestones.

Highest priorities: (1) a human clean-machine Windows 10/11 first-run and DPI
acceptance pass using this exact ZIP; (2) review/approve the stacked merge and
b5 follow-up, then authorize one immutable GitHub prerelease asset upload.

## Distribution proposal

Use version `0.11.0b5`. After authorization, upload the verified ZIP and its
SHA-256 file as immutable assets of one GitHub prerelease, identifying its exact
source commit. Use that release page as the stable colleague download method.
No prerelease or public URL has been created by this work.
