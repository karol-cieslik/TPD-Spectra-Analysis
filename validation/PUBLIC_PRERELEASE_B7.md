# v0.11.0b7 public prerelease preparation

The public research-beta distribution reuses the verified Windows executable
from merged `main` commit `e8a273ae85a5b60ccb22682e3a218b3afdbfe51a`.
No numerical code or executable is rebuilt for this documentation/distribution
checkpoint. The release tag identifies that executable's source commit;
`RELEASE-PROVENANCE.json` in the ZIP separately identifies updated documentation.

## Retained completed checks

- 408 local Windows/Python 3.12 tests passed, with zero failures or skips, for
  the two-peak implementation; scientific CI and frozen Windows CI passed.
- Merged-main Windows workflow `41310487276` completed successfully, including
  the scientific/GUI regression suite, frozen smoke and assembled-package checks.
- Its artifact `13084908744` was downloaded once. Archive SHA-256 matched
  GitHub's digest:
  `708f0ea0032d025d67b0ce9a251442fd0e908ef577b48e9ba02cf5dd30adff9c`.
- The downloaded package's manifest, all shipped file hashes, links and
  `VERSION.json` commit were verified before launch.

## Outstanding work completed after resumption

- The downloaded executable's bundled smoke completed locally: 21 synthetic
  imports, nine publication examples with provenance, 41 Help topics, offline
  feedback, Redhead preview, zero-order fit/project/report/short Monte Carlo,
  three-component fit/sum/residuals/editor/project/export. No callback errors.
- Eleven targeted checks passed for changed documentation, package resources,
  links and Quick Start content. The 408-test suite was not repeated.
- README, download links, feedback/email invitation, beta notes, Help status,
  guides and Quick Start PDF now describe the versioned prerelease.
- The preview is an actual exported synthetic fit from the downloaded executable,
  not a fabricated screenshot. Live window capture timed out; no human visual,
  high-DPI or clean-machine acceptance is inferred from automated checks.
- The changed first PDF page was rendered and visually checked; scientific
  content on the other four pages is retained from the previously reviewed guide.

The repackaged release preserves the executable byte-for-byte, preserves
third-party notices and source numeric data, refreshes sidecar documentation,
records provenance and regenerates full file checksums plus a ZIP checksum.
Publication is explicitly authorized as a research-beta prerelease, with
scientific/model limitations and broader acceptance work disclosed.
