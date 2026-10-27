# Final beta cleanup verification - 27 October 2026

## Preserved state

Both local checkouts were clean. Work started on a new focused branch from
`main` at `7a0f6f739835baf4663cea809393bc8d1af28c42`. GitHub confirmed PRs
#19, #20 and #21 merged; no existing work, synced sources or numerical engines
were discarded or changed. No open PR duplicated this cleanup.

The prior successful main Windows run was
[40488914540](https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40488914540),
artifact `12729080251`, version `0.11.0b5`, source `7a0f6f7...`.
Its downloaded ZIP SHA-256 matched GitHub's artifact digest:
`c2ca69e39bb2b3dd8f9954988abbdd5d24aca91447b5a9c5c1541efe1eb28219`.
It included internal review, handoff, audit and acceptance records. This is
historical inspection evidence, not the final cleanup download.

## Changes and verification

- Current onboarding, method status, release notes, citation metadata, worked
  HTML/Markdown and five-page PDF identify b5 on main with PRs #19-21 merged.
  Historical records remain, explicitly marked as snapshots.
- A shared researcher manifest excludes internal release records and checks
  local Markdown/HTML links and README image resources in the assembled tree.
- SHA256SUMS covers all package files; executable and VERSION.json identities
  must agree. Nested upstream licenses retain their directory structure.
- Local real Windows/Python 3.12 full suite: **344 passed, zero failures/skips**,
  215.71 s. One pytest-cache permission warning did not affect tests. The
  subsequently added nested-license regression passed with all **9 targeted
  documentation/package checks**; CI runs the complete final test collection.
- Python wheel build, dependency consistency and CLI entrypoints passed.
- All five regenerated PDF pages were rendered using Poppler and visually
  inspected. This is document review, not application visual acceptance.
- Frozen workflow smoke now exercises **20 Monte Carlo replicates** and real
  cancellation after progress. Packaged Help smoke searches `seed`.
- Existing frozen tests cover raw default trace/first region, Redhead recovery,
  simulation/comparison, projects/reports, three components/sum/residuals,
  offline Help/five tutorials and diagnostic preview/copy/save without upload.

The Windows workflow tests the final source, freezes it, verifies the real
executable, assembles resources and checks hashes/links/frozen identity before
uploading. Its run URL, source SHA and downloadable artifact are authoritative;
do not infer final build identity from an earlier local acceptance record.

## Remaining human acceptance and scientific limits

Automated widgets and numerical tests do not establish visual acceptance.
Review the exact downloaded package at normal/high display scaling, all five
tutorials, Help scrolling, Results readability, warnings, MC progress/Cancel
and feedback. Independently launch it on Windows 10/11 without Python.
These checks remain required before colleague distribution.

No independent experimental validation or uncertainty-coverage calibration is
claimed. Fixed kinetic assumptions, independent populations and nominal linear
ramps remain limitations; component-count rankings are heuristic, zero-order
brackets are conditional, and joint-component Monte Carlo/multicomponent
zero-order fitting remain unavailable. No new scientific method was added.

The existing release-preparation workflow can attach the ZIP and an outer
SHA-256 sidecar to an unpublished prerelease draft when separately authorized.
This cleanup does not create a tag, publish a release or contact colleagues.
