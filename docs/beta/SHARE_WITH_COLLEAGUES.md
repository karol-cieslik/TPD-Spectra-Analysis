# Sharing the next Windows research beta

This maintainer handoff describes the current **0.11.0b6 research beta on main**.
PRs #19, #20 and #21 are merged. Results, scientific Help and guided exercises
are included. Historical b4 artifacts **do not contain** that interface:
**Do not send that old ZIP as the updated colleague beta.**
Download instructions live in [START_HERE](../../START_HERE.md).

## Before sending the first email

- [x] PRs #19–21 merged into main on 27 October 2026. Preserve their historical evidence.
- [ ] Run all automated scientific tests and Windows packaging checks on one **specified reviewed commit**. Confirm their outcomes and link the CI job. Do not treat the older b4 build as evidence for a new commit.
- [ ] Check that the new ZIP includes `TPD-Spectra-Studio.exe`, `VERSION.json`, `SHA256SUMS.txt`, `START_HERE.md`, `docs/beta/WORKED_EXAMPLES.html`, `docs/beta/SCIENTIFIC_HELP_TOPICS.json`, `docs/beta/FEEDBACK_FORM.md` and the synthetic examples. Compare the executable SHA-256 digest with the checksum file.
- [ ] On a clean Windows machine without Python, **run the actual executable**: startup default two-peak example, switch Selection → Modeling → Results, choose a named peak, compute a first-order Redhead example near 1.2 eV, open Help and search for `seed`, run a short Monte Carlo and observe progress/Cancel, test an overlapping three-component fit, inspect residual/assumed-versus-fitted values, save/reopen a project, and export one report.
- [ ] Open offline worked examples from the package. Inspect the user interface at normal and high display scaling for clipped text, inaccessible buttons or frozen windows. Verify feedback can be previewed without automatic submission or spectral attachments.
- [ ] Resolve any blocker found above, rebuilding and repeating the acceptance checks as needed. Preserve failing logs and the earlier working artifact.
- [ ] Provide one **verified, stable download URL** (ideally a reviewed GitHub pre-release asset) and identify its commit. Do not circulate an unreviewed action artifact or a guessed URL. Public pre-release publication requires separate approval.

The more detailed acceptance checklist is [beta review status](REVIEW_STATUS.md), and the full [tester's checklist](TESTER_CHECKLIST.md) goes in the package. Human visual/DPI and independent Windows acceptance remain **unchecked**; successful automated frozen checks alone do not complete those gates.

## Informal email to a colleague (send only after verification)

**Subject:** A small TPD analysis program — would you like to try the beta?

Hi [Name],

I've been working on a small Windows program for TPD/TDS analysis and have a beta ready for informal testing. It lets you select peaks, explore kinetic models, run simulated spectra and Monte Carlo checks, and inspect fitted parameters and assumptions.

If you have 10–15 minutes at some point, would you mind giving it a try? There are synthetic examples and a short walkthrough included, so you don't need to prepare or share any measurements. I'm mainly interested in whether the steps are understandable and if anything breaks or seems scientifically questionable.

Here's the download: **[insert link to the verified new Windows beta]**. The instructions are in `START_HERE.md`; the program also has a Quick Start and a feedback button. Even a few comments by email would be very helpful. No pressure to do a thorough review.

If you later have a TPD trace you're allowed to share, I'd be happy to test it separately, but that is entirely optional.

Best,
Karol

## Shorter message for someone you know well

Hi [Name], I've put together a beta of a little TPD analysis program and thought you might find it interesting. If you have 10 minutes, would you mind trying one of the example datasets and telling me what is confusing or what doesn't work? It has a short guide, and no real data are needed. [Verified download link]. Any comments welcome, no pressure!

## What to request after the first reply

Ask for the build commit from About/`VERSION.json`, Windows version/scaling, the example tried, the control settings, and the expected versus actual behavior. The [optional feedback form](FEEDBACK_FORM.md) is an aid, not a questionnaire that must be completed. If a colleague reports a bug, reproduce it on the *same build* first and log the steps and whether it affects scientific results.

For personal or unpublished data, agree separately on permission, access, attribution, retention, redistribution and publication. Private troubleshooting does not establish permission to include spectra in a public example or manuscript. Do not send a mass email or assume colleagues endorse the program simply because they tried it.

## Suggested two-round pilot

1. **First round:** one trusted colleague, informal 10–15-minute synthetic-example test. Correct confusing labels and any blocking workflows before widening distribution.
2. **Second round:** a few surface-science colleagues with different analysis experience. Ask whether peak selection, modeling assumptions and parameter interpretation remain clear. Invite independent spectra only after confirming permission and the reference calculation.

The goal of these rounds is usability and initial issue discovery; publication claims will still require independent experimental benchmarks and uncertainty validation.
