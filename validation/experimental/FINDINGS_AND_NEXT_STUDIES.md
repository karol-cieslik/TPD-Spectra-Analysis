# Experimental findings and focused follow-up

Recorded 29 October 2026, after the pure-ice assessment. This is an interpretation
and work plan, not a declaration that any new validation has passed. Existing
inputs and outputs remain unchanged. No production numerical code is changed.

**Subsequent source check:** [the figure-to-CSV correction](../digitized/SOURCE_CORRESPONDENCE_UPDATE.md)
finds an unresolved CO correspondence discrepancy. Earlier results describe the
deposited input, not yet a replication of the paper's CO trace. Ar matches its
published curve closely. Read this correction before attributing the CO
literature disagreement to a physical or software cause.

**Subsequent positive conditional comparison:** [ethanol on gold](ethanol_2024/README.md)
closely reproduces the dominant literature energy when its prefactor is fixed
(6435 versus 6450 K). Free-prefactor results depend on baseline/window and reach
7613 K for the primary free-baseline case. This advances experimental comparison
without establishing general accuracy or a unique parameter interpretation.

**Subsequent second-order case:** [O₂/Pt(111)](oxygen_pt111_2014/README.md)
uses an author-published coverage series. Across the 14 source spectra with
leading-edge estimates, the fitted fixed second-order model beats fixed first
order by AICc and NRMSE. Free-order estimates are 2.35–2.73. Whole-window
constant-energy results drift increasingly below the source's leading-edge
energies with coverage, consistent with the paper's explicitly
coverage-dependent-barrier model being outside the software's single-state
constant-energy hypothesis. Treat this as a useful order-discrimination/model
challenge, not a clean energy-accuracy pass.

**Fractional-order literature candidate:** [2-propanol/HOPG](fractional_2propanol_hopg/README.md)
reports a monolayer order of 1.23 ± 0.03 and an amorphous multilayer order near
zero, with coverage-series TPD traces and a stated 0.5 K/s ramp. The published
article is CC BY 3.0, but its figure/PDF image endpoint could not be retrieved
in this assessment. This is a screened, promising digitization target, not a
completed software fit or an experimental validation result.

**Expanded experimental review and algorithm research:** [assessment](EXPERIMENTAL_VALIDATION_AND_ALGORITHM_ASSESSMENT.md)
consolidates the completed positive and negative comparisons, limits on current
claims, the newly reviewed methanol/HOPG fractional-order benchmark, and a
ranked algorithm roadmap. [Methanol/HOPG admission record](methanol_hopg_2005/README.md)
documents its published order values and the figure-access/label-resolution
steps required before it can count as a software test.

## Established observations

- Six completed ideal zero-order full-peak fits to deposited Ar/CO data reached
  the 0.05 eV lower bound. NRMSE was 0.2191–0.3243. Numerical completion does
  not make these energies reliable physical estimates.
- The retained CO figure shows a broad measured trailing tail versus the model's
  abrupt depletion cutoff. The published energy estimates instead use the rising
  leading edge, with upper cutoffs 27 K for Ar and 28 K for CO.
- CO nonlinear leading-edge fits gave 1069.87 K with zero baseline and 718.74 K
  with a fitted constant baseline. The published reference is 1040 ± 104 K.
  Agreement of one setting is not a demonstration of general accuracy.
- The application's log-signal regression gave 1336.50 K on the same 20–28 K
  interval. Its positive-signal mask retained 26/78 observations. Independent
  NumPy OLS agrees numerically; signal-space and log-space fits weight errors
  differently. Neither numerical agreement nor a regression interval resolves
  baseline or physical-model uncertainty.
- Ar's primary and leading-edge intervals were withheld for small temperature
  reversals/duplicates. The prespecified alternative interval was retained.

Data, protocols, source hashes, excluded inputs, all calculations and figures:
[Ar/CO assessment](ice_2024/README.md). The original semicolon-delimited data
are directly accessible as [Ar](ice_2024/raw/4_Ar_pure.csv) and
[CO](ice_2024/raw/2_CO_pure.csv), with K and ML/K headers. Original gzip files
are retained too. Their deposited parent archive checksum was verified.
[PTCDA](ptcda_au111/README.md) and [AgY D2](rodare_4644/README.md) remain
separate assessments with their original limitations.

## Diagnosis: evidence versus hypotheses

| Explanation | Current support | Discriminating next check |
| --- | --- | --- |
| Ideal zero-order full-peak shape is unsuitable for these selected observations | Direct mismatch between broad tails and the implemented cutoff; bound-limited energies and large residuals | Test the unchanged fitter on a measured case with a resolved depletion edge; compare full peak and source-matched leading edge |
| Baseline/error weighting affects the leading-edge result | Directly observed dependence on baseline and log/signal-space objective; positive-signal filtering is recorded | Freeze baseline rules and intervals before fitting a fresh independent spectrum; retain all outcomes |
| Detector response, pumping, thermal lag or temperature gradients broaden the peak | Plausible mechanisms; none established for these particular traces | Seek documented response/calibration and heating-rate series; independently simulate known response distortions to diagnose possible signatures, not to claim an instrument correction |
| Multiple populations, energy distributions or interactions broaden the peak | Plausible alternatives; no physical mechanism identified here | Prefer a characterized reference, then compare rate/coverage trends against its stated model; do not infer mechanism from curve quality alone |
| Numerical implementation or restricted energy range contributes | Synthetic regressions support specific numerical paths, not all experimental cases; lower bound is active | Use an independent forward reference and inspect objective/profile behavior for a specified hypothesis; do not lower the bound to manufacture agreement |

These explanations can coexist. The current evidence does not identify the
physical origin of the tails, prove a software-wide defect, or justify adding
more fitted components. The existing zero-order core already warns about energy
bounds and large residuals (`tpd_spectra/zero_order.py`); the remaining product
check is whether users can clearly see those warnings in GUI and exports.
Do not describe that visibility check as a confirmed missing feature.

## Recommended small external panel

Start with **two additional independent experimental studies**. Add a third
only if it tests a retained manuscript claim or separates an unresolved cause.
This is a practical scope choice, not a statistical sample-size calculation.

1. **Isolated first-order desorption:** a well-characterized surface and stable
   coverage regime, full peak and baseline on both sides, reported heating rate
   and compatible energy/prefactor conventions. This targets positive-order
   fitting rather than repeating the current zero-order challenge.
2. **Resolved zero-order depletion:** a full measured exhaustion edge, adequate
   samples after it, and source-reported model assumptions. This targets the
   model feature absent from the broad Ar/CO traces.
3. **Optional rate/coverage series:** measurements of the same system at several
   rates or coverages, with response/calibration metadata. This helps distinguish
   kinetic changes from measurement response. A series from one study remains
   one experimental source, not several independent studies.

The Ayling et al. 2-propanol/HOPG series is a targeted fractional-order
candidate for a later digitization pass. Its reported fractional order is
derived from a coverage-series regression, while a whole-trace Polanyi–Wigner
fit would be a distinct estimator; compare them as a model check and do not
expect exact parameter equivalence.

The 73 PTCDA spectra and 438 conditional fits do not equal 438 independent
experiments or 438 confirmations. Increasing Monte Carlo replicates estimates
conditional variability; it cannot fix a mismatched forward model.

A screened lead for item 1 is Smith & Kay, *Desorption Kinetics of Benzene and
Cyclohexane from a Graphene Surface*, DOI 10.1021/acs.jpcb.7b05102. Its abstract
reports a first-order benzene regime above approximately 0.1 ML. It is a lead,
not an acquired benchmark: raw/full-peak access, reuse rights, exact trace and
heating rate still need verification. Submonolayer methyl-mercaptan data from
DOI 10.3847/1538-4357/adc7b6 should not be treated as a single-energy positive
control: the authors explicitly use an energy distribution. Keep that as an
optional model challenge rather than a substitute for item 1.

## Admission and stopping rules

For each new study, acquire experimental numeric data first where available;
otherwise establish figure rights and a documented digitization uncertainty.
Record DOI/version/license, raw hashes, exact trace identity, units and heating
rate. Do not use simulated curves as external measurements or invent measured
time from temperature. A derived time coordinate must be explicitly labeled.

Before fitting, freeze the baseline recipe, main and sensitivity intervals,
physical hypotheses, bounds and comparison criteria. Record energy differences,
residual structure, NRMSE denominator, failures, bound flags, identifiability and
sensitivity. Compare published quantities only when kinetic law, coverage and
prefactor conventions are commensurate. A published distribution mean or
zero-coverage extrapolation is not a single-state fitted energy reference.

Retain negative cases. Do not search only for a matching number or retune
settings until agreement appears. Once these two targeted studies are evaluated,
review the claim/evidence table before widening the data search. If no admissible
positive case can be acquired, state the limit and complete other publication
checkpoints; do not expand the scientific model merely to obtain a pass.

## Primary references supporting the plan

- Kruczkiewicz et al. (2024), DOI 10.1051/0004-6361/202346948; deposited data
  DOI 10.5281/zenodo.10912815. Original evidence for the retained Ar/CO comparison.
- Schmid, Parkinson & Diebold (2023), DOI 10.1021/acsphyschemau.2c00031,
  Introduction. Discusses limitations of peak-shape inference, coverage and
  heating-rate dependence, and finite pumping/temperature-gradient constraints.
  These general mechanisms are not an attribution for the current data.
- Smith & Kay (2018), DOI 10.1021/acs.jpcb.7b05102. Primary experimental lead
  for a first-order regime; access and benchmark metadata still unverified.
