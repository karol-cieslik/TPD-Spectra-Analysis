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
The completed revised headless suite recorded 324 passed and 38 display-dependent
skips; a subsequently added CLI ramp-rejection integration test passed with
all eight ramp tests. GUI skips do not establish Windows acceptance.
The full XML record is validation/joss_checkpoint_tests.xml.

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
