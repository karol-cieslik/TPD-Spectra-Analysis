# Published TPD/TDS spectra: literature-validation candidates

This is a **research checklist**, not a repository of downloaded or validated data. The catalog lists 26 bibliographically verified candidates for evaluating TPD Spectra Studio on literature spectra and reported parameters. A DOI and article record do **not** imply that the full text, figure, underlying data or reproduction rights have been checked.

## Extraction resources

- [`literature_tpd_candidates.csv`](literature_tpd_candidates.csv): bibliography, prioritization and validation status.
- [`literature_extraction_notes.csv`](literature_extraction_notes.csv): paper-by-paper instructions for all 26 candidates, keyed by `id`.
- [`DIGITIZATION_GUIDE.md`](DIGITIZATION_GUIDE.md): step-by-step source retrieval, calibration, quality controls and manuscript reporting.
- [`FIRST_EXPERIMENTAL_BENCHMARK.md`](FIRST_EXPERIMENTAL_BENCHMARK.md): a concrete three-paper starting order, application import columns, evidence stages and a complete per-trace record for the first external test.

## Suggested workflow

1. Prioritize LIT002 (experiment + stated kinetic orders and parameters), LIT003 (second-order and multiple heating rates), LIT001 (zero-order), LIT010 (energy distributions) and LIT009 (tabular peak-temperature cross-check).
2. Open the original article and confirm exact figure, axes, heating rate, signal scaling, coverage, temperature units and whether the data are experimental or simulated. Update `verification_level` and `candidate_figures_or_tables`.
3. First look for downloadable author/publisher data or supplements. If absent, digitize the *graph*, recording axis calibration, resolution, units, trace/curve identity, human uncertainty and processing choices.
4. Fit each digitized trace with a frozen software release, and record E, prefactor, fitted order, residuals, AICc, intervals, computational failures and any discrepancies from authors' assumptions.
5. Compare appropriately: use reported kinetic parameters only when coverage normalization/prefactor units and model assumptions match. Peak position and shapes may be more defensible than absolute prefactors across dissimilar instrumentation.
6. Maintain a reproducible provenance record per extracted trace: article DOI, figure/panel, underlying experimental conditions, access date, digitizer version, original figure source, plot-calibration points, output CSV hash, software commit and exclusion reasons.
7. Confirm licensing before redistributing figure-derived points. Citation alone is not a redistribution license. Prefer linking to sources and distributing derived benchmark metadata/code where permission is unclear.

## Scientific caveats

An isolated trace often does not uniquely identify kinetic order or energy and prefactor; higher-quality validation uses **coverage series and multiple heating rates**. Multilayer ice spectra, phase changes, subsurface populations, lateral interactions, reactor transport and readsorption may violate a single-state Polanyi–Wigner model. A fit reproducing a published trace does not constitute independent confirmation of the published interpretation.

`digitization_status=not_started` is intentionally assigned to every record. **No source figure has yet been digitized or experimentally benchmarked.** In a manuscript, distinguish *identified literature candidates* from *completed external validation*.

This catalog is meant to be extended and audited. The primary references are linked directly in the CSV; avoid claiming exact figure identifiers where not confirmed.

## Author outreach after validation

The main CSV includes `contact_author`, `contact_email`, `contact_role`, `contact_source_url`, `contact_verification_status`, and `outreach_status`. Email addresses are **publicly listed professional contact details** only; empty cells mean unverified, not that no contact exists. Some are coauthors, not designated corresponding authors, and older papers may have changed affiliations. Recheck each institutional page just before writing.

Suggested sequence: complete the digitization and independent validation first; then send one personalized professional message to the identified author, explain specifically which published spectrum and figure were used, identify the article citation, provide a link to the software and validation protocol, invite bug reports/usability comments, and avoid implying endorsement or collaboration without the author's agreement. If you want the original numerical data, request them explicitly and ask about permission for public redistribution.

Use `outreach_status` to track `not_contacted`, `sent`, `replied`, `declined`, or `bounced`. Do not publish private email responses or third-party confidential datasets in this public GitHub repository.

## Acquired external numerical input case

A separate deposited CC-BY-4.0 dataset now supports a limited experimental
input/conversion/peak and negative ramp-screening check. See
[the RODARE case](experimental/rodare_4644/README.md). It is outside the 26
figure-digitization leads above and does not change their not_started status.
It is not a completed desorption-energy validation or external-adoption claim.

### PTCDA/Au(111) deposited-data model challenge

[Records and limitations](experimental/ptcda_au111/README.md) retain the original
CC-BY-4.0 archive (95 files), frozen screens and 438 conditional first-order fits
on 73 selected traces. Frequent prefactor-bound flags and baseline-dependent
energies make this a model challenge, not reproduction of the published
zero-coverage energy. The existing 26-entry literature catalog is unchanged;
this acquired source is tracked separately.

### Deposited pure-Ar and CO energy comparison

[Source and outcomes](experimental/ice_2024/README.md): explicit deposited units,
checksum provenance, fixed protocols, six bound-limited full-peak fits, withheld
Ar intervals, and baseline-sensitive leading-edge results. An independent
nonlinear CO estimate lies within the published band only for one baseline
hypothesis; this does not validate Studio's full-peak estimates. All results are
retained. The existing literature catalog remains unchanged.

### Diagnosis and next experimental studies

[Findings and next studies](experimental/FINDINGS_AND_NEXT_STUDIES.md) separates
observed failures from possible causes, links original readable data, and fixes
a small next panel: two independent studies plus an optional discriminating
series. [Study plan](experimental/next_study_plan.csv) explicitly distinguishes
leads from acquired evidence. No additional validation pass is claimed.

### Three-paper figure digitization

[Four curves from three papers](digitized/README.md) retain figure-derived CSVs,
source images/path coordinates, licences, axis calibration, missing segments and
QA overlays. Two papers extend the collection; the existing pure-ice study is
also checked independently against its published figures. No kinetic fits were
performed. The [CO correspondence correction](digitized/SOURCE_CORRESPONDENCE_UPDATE.md)
qualifies earlier deposited-data interpretations while preserving all originals.

### Three additional candidate studies

[Additional-study screening](experimental/additional_studies_2026_10_29/README.md)
records nine molecular-system targets from three more papers, published energy
references, source hashes, rights/access limits and a comparison sequence.
These are candidates, not nine completed validation datasets. No new fits.

### Ethanol/Au conditional comparison

[Completed comparison](experimental/ethanol_2024/README.md): 20 declared fits to
figure-derived experimental marks. Fixed literature-prefactor energy is 6435 K
versus dominant published 6450 K; free-prefactor fitting gives 7613 K with a
fitted baseline. Extraction gaps, residuals and model differences remain explicit.
Source-derived materials carry CC-BY-NC-3.0, separately from software code.

### Methyl-acetate/HOPG comparison

[Completed leading-edge assessment](experimental/methyl_acetate_2024/README.md)
gives 42.22 kJ/mol with the declared offset versus published 42.8 +/- 0.7;
other baseline/window settings give 37.81–40.29. Whole-peak mismatch and
substantial extraction gaps remain explicit. The separate 42.63 reconstruction
uses an already corrected published ordinate and is not independent validation.

### Pure MeSH and manuscript evidence audit

[Pure-MeSH assessment](experimental/mesh_2025/README.md) reuses the existing
preprint extraction: 12 records, method-sensitive leading edges and whole-peak
residuals, no robust reproduction of the TST-conditioned reference.
[Claim–evidence audit](../docs/JOSS_CLAIM_EVIDENCE_AUDIT.md) consolidates these
results with ethanol, methyl acetate and earlier numerical/negative cases.

### Focused review package

[Review entry point](review_package/README.md) provides three selected cases,
three questions, a response template and a measured-coordinate Windows import
fixture. Headless export/helper checks preserve warnings/settings without
refitting; Windows GUI and independent scientific acceptance remain pending.
