# Reproducing the bounded JOSS preparation checks

This is a working reviewer guide, not a submission-readiness declaration.
See JOSS_CHECKPOINT_PROGRESS.md for all 78 checkpoints and remaining gates.

## Install and verify

From the reviewed source checkout, with Python 3.10+ and Tk available:

```bash
python -m pip install -r requirements-build.txt
python -m pip install -e .
python -m pytest -q
```

The upstream baseline was d85be6bbaeb6b58fce12bf9b7ff2e47c5fd123ac.
The earlier revised headless suite recorded 324 passed and 38 display-dependent
skips in validation/joss_checkpoint_tests.xml. The later optimizer-fix full suite
recorded **328 passed, 38 skipped, zero failures/errors**, retained in
validation/optimizer_fix_full_tests.xml. These are completed historical checks;
they were not rerun for the subsequent documentation/data-only assessments.
GUI skips do not establish Windows acceptance or current-head CI status.

## Read existing results before rerunning experiments

`validation/joss_parameter_stability/assessment.json` contains 36 independent
population-reference cases and two single-model parameter-stability cases.
All numerical cases met the specified 2e-6 population tolerance; maximum error
was 9.645030716876057e-7. Six compressed JSON records retain 1200 completed
refits with no failed refits. Decompress with Python gzip or standard gzip tools.

To reproduce, use a new output directory to preserve these recorded results:

```bash
python -m scripts.joss_assessment --output output/joss-reproduction
python -m scripts.experimental_rodare_check
```

The numerical/MC experiment can be slow. Its single-model frequencies do not
test model-ranking convergence. Percentiles are conditional refit ranges, not
coverage-calibrated confidence intervals. The protocol documents an earlier
uncompleted multi-candidate attempt; no statistical result is claimed from it.

The deposited experimental case contains 289 measured observations with explicit
seconds/K units. Expected sampled D2 maximum: 92.06 K, versus the article's
rounded ~92 K. The full reconstructed ramp fails the default 2 K engineering
screen at 4.17103 K; no kinetic fit is forced. Data attribution, transformations,
license and source hashes are in validation/experimental/rodare_4644/.
This is input/peak reproduction and negative screening, not energy validation.

## Inspect changed interfaces

Python: `load_spectrum(path, time_unit='s', temperature_unit='K')` records source
units and converts internally. Defaults remain ms/degC for backward compatibility;
GUI/CLI import does not infer arbitrary units from generic headers.

CLI: `--kinetic-ramp-tolerance-K` defaults to 2 K. Accepted fits export maximum
and RMS temperature mismatch and chosen threshold. A hold-like ramp regression
verifies that rejection prevents optimizer invocation. Thresholds are not
instrument calibration or evidence of an appropriate physical model.

An installed wheel was checked from an unrelated directory: numerical core and
all 40 offline Help topics loaded. Full examples/tutorial sidecars are not all
included in wheels; source and portable Windows packages remain the documented
full desktop routes.

## Human checks still needed

Use docs/beta/TESTER_CHECKLIST.md on the exact Windows package. Record version,
source SHA, ZIP checksum, Windows version, Python absence/presence and scaling.
Inspect launch, tutorials, Help, Results roles, fitting, MC progress/cancel,
save/reopen and exports. Have an independent domain scientist assess equations,
units and interpretation. Do not mark these complete from automated checks.

## Manuscript

paper/paper.md and paper/paper.bib are working files. A local Pandoc/citeproc
PDF compiled successfully, but the official JOSS-template proof remains open.
Affiliation, funding, final authorship, AI disclosure and genuine research-use
evidence require author confirmation. Public-development history also remains
an unmet time gate. No external adoption, kinetic-energy experimental validation
or mechanism probability is claimed.


## Follow-up: bounded ranking and Windows portability

The first/second-order follow-up is in validation/joss_ranking/. It reuses the
recorded inputs without repeating the numerical or parameter-only assessment.
Run `python -m scripts.joss_ranking_assessment --output output/ranking-new`
to reproduce, with a 120-second wall limit per seed. Its favorable initialization
and conditional-reference/noise assumptions must accompany any reported ranking.
The 81-point multistart replay returned a materially wrong first-order energy
despite convergence; general blind order/parameter recovery remains unvalidated.

The original PR Windows failures were traced to CRLF checkout changing the
experimental CSV hash and a cp1252 test decoder. Data checkout is now LF and
the Help test explicitly uses UTF-8. Review the CI for the corrected commit;
passing Linux tests do not replace it.

## Corrected-fitter reassessment

Read validation/joss_postfix/README.md and comparison.json for the completed
post-fix reassessment. It preserves old results, reuses original inputs, and
retains 1200 complete ranking replicates with 2400 model-fit records. To reproduce
into a new directory: `python -m scripts.joss_postfix_assessment --output output/postfix-new`.
This combined two-candidate run supplies parameter and ranking evidence; no
repeat of the unchanged numerical-reference matrix was necessary.

## External experimental model challenge

See [PTCDA/Au(111) records](../validation/experimental/ptcda_au111/README.md):
original licensed deposited ZIP, checksum/provenance, all 95 inventory entries,
pre-fit protocol and 438 full conditional fits on 73 screened traces. Baseline
sensitivity and optimizer-bound flags prevent an energy-validation claim. The
published zero-coverage complete-analysis estimate is a different quantity from
a constant-energy fit to an unidentified coverage trace. See the README for
unresolved coverage, coordinate-unit and methodological limitations.

The [coverage-mapping review](../validation/experimental/ptcda_au111/COVERAGE_MAPPING_REVIEW.md)
records the completed follow-up: primary method verified, raw coverage identity
unresolved, four detector scales, and unchanged frozen data windows. These
explicit limits prevent treating constant-energy fits as reproduction of a
coverage-dependent zero-coverage intercept.

## Pure-ice external reference comparison

[Ar/CO records](../validation/experimental/ice_2024/README.md) include original
CC-BY CSVs, verified published references, pre-fit protocol, six bound-limited
full-peak results, withheld inputs, baseline-sensitive independent leading-edge
fits and a separately declared application log-regression diagnostic. The
comparison figure shows the full-peak mismatch rather than hiding it. This is
explicitly negative/sensitivity evidence; the draft does not claim experimental
energy accuracy from these outcomes.

## Three-paper figure extraction and source correction

[Digitized spectra](../validation/digitized/README.md) provide four curves from
Zaki et al. (2018), Narayanan et al. (2025; explicitly preprint v1 source), and
Kruczkiewicz et al. (2024). Sources, licences, calibration, absent columns and
engineering extraction bounds are retained. QA is AI-assisted; independent
human coordinate verification and energy validation are not claimed.

The [new source-correspondence check](../validation/digitized/SOURCE_CORRESPONDENCE_UPDATE.md)
finds a close Ar match but substantial CO figure/CSV disagreement. This means
the earlier deposited-CO calculation is not yet a trace-matched replication of
the paper. The draft now records this limit; prior inputs/results remain intact.

## Consolidated claim–evidence review

See [the manuscript evidence audit](JOSS_CLAIM_EVIDENCE_AUDIT.md). It distinguishes
conditional literature agreement, transformed-plot reconstruction and model-limit
findings. Ethanol, methyl acetate and pure MeSH have completed bounded assessments;
none establishes general accuracy, independent adoption or physical confidence
coverage. All three case directories retain protocols, residuals and limitations.

## Focused independent review package

Start with [the review package](../validation/review_package/README.md): three
selected comparisons, three scientific questions, an unfilled response form and
a Windows acceptance checklist. Its headless exporter/helper checks pass on
a retained mismatch without refitting. Independent human review, Windows GUI
execution and native workflow PDF acceptance remain pending.
