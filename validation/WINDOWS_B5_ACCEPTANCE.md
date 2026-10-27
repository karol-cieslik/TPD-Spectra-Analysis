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

Acceptance is in progress. This file will be updated with exact source commit,
test counts, actual frozen-executable results and package checksums. Do not
interpret planned workflows as passes.

Clean-machine Windows 10/11 testing without Python, independent high-DPI display
acceptance and experimental validation remain separate open gates.

## Distribution proposal

Use version `0.11.0b5`. After authorization, upload the verified ZIP and its
SHA-256 file as immutable assets of one GitHub prerelease, identifying its exact
source commit. Use that release page as the stable colleague download method.
No prerelease or public URL has been created by this work.
