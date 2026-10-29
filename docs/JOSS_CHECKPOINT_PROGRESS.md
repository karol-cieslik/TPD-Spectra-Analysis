# JOSS checkpoint progress — 28 October 2026

This is an evidence update to the 78-checkpoint readiness audit. It records
completed work and explicit limits, not journal eligibility or acceptance.
Upstream baseline: `d85be6bbaeb6b58fce12bf9b7ff2e47c5fd123ac` (0.11.0b5).
Changes are proposed for review; no release, merge or external outreach occurred.

## Completed in this work block

- Executed baseline headless tests (307 passed, 38 GUI/display-dependent skips).
- Added explicit Python import time units ms/s/min and temperatures degC/K,
  preserving legacy defaults and exporting source/conversion metadata.
- Added a quantified CLI constant-ramp mismatch screen and regression that
  prevents optimizer invocation for a rejected ramp. The default 2 K is an
  engineering threshold; it is not experimental uncertainty.
- Fixed missing scientific Help in installed wheels and tested all 40 topics.
- Corrected stale source installation instructions and narrowed citation wording.
- Executed 36 independent reference cases; all passed the specified 2e-6
  normalized-population tolerance, worst error 9.645030716876057e-7.
- Executed 1200 conditional single-model MC refits: 2 cases × 3 seeds × 200.
  All completed without failed refits. Full records are compressed alongside
  the summary; no experiment/coverage/model-selection claim follows.
- Acquired original CC-BY-4.0 external TDS data, verified source checksum,
  documented attribution, reproduced a sampled 92.06 K D2 maximum versus the
  article's rounded ~92 K description, and documented a 4.17103 K full-ramp
  mismatch. No kinetic fit was forced.
- Prepared a working JOSS manuscript, bibliography and assessment figure.
  Affiliation, authorship, funding, actual research-use evidence and historical
  AI disclosure remain explicit author-confirmation items.

## Results and limits

For the matched Gaussian case, 200-refit energy percentile endpoints across
three seeds span about 0.000858 eV (lower) and 0.003271 eV (upper). The largest
100→200 endpoint change is about 0.002692 eV. For the drift-mismatch case the
endpoint spans are about 0.003152 and 0.022376 eV, with a largest prefix change
of 0.011386 eV. These are measured sensitivities of this bounded design, not
universal convergence or coverage guarantees. The first fitted energies are
1.094779 eV (matched case) and 1.144674 eV (drift case), with input 1.1 eV.
One fixed dataset per case does not estimate frequentist bias.

A first two-candidate/multistart assessment attempt did not return its initial
comparison in the observation period. It produced no completed MC evidence.
The protocol documents narrowing to single-model parameter stability before
those results were generated. Multi-model ranking convergence is still open.

The installed wheel now provides its core and offline Help from an unrelated
working directory. It does not include every repository example/tutorial
sidecar. Full desktop distribution remains source/portable-Windows based.
The local Pandoc PDF is a draft rendering, not an official JOSS-template proof.

## Next work in order

1. Finish a suitable full-peak experimental kinetic comparison. Current external
   input/peak reproduction is deliberately narrower and cannot replace it.
2. Investigate the slow multistart/candidate comparison and finish bounded
   multi-model ranking stability. Do not interpret parameter-only results as
   completed model-comparison validation.
3. Have Karol/tester perform the exact-package clean-Windows visual/DPI checklist,
   and a domain scientist review equations, units and experimental interpretation.
4. Confirm manuscript metadata/AI disclosure, genuine research use and final
   software comparison; compile using the official JOSS preview workflow.
5. Continue genuine open development; after 17 April 2027 is only a theoretical
   earliest submission window if public from creation and all other gates pass.

## All checkpoints

E=evidenced for the bounded task; P=partial; G=gap; H=human action;
D=conditional/deferred; F=later submission/review. No percentage readiness is inferred.

| # | Checkpoint | Status | Evidence / remaining action |
|---:|---|:---:|---|
| 1 | Record the exact source commit and version to audit. | E | Pinned upstream d85be6b; working changes isolated for a draft PR, no merge/release. |
| 2 | Inventory user-facing methods, experimental APIs, export formats and supported environments. | E | README, method status, packaging metadata and source give an inventory; supported environment claims remain bounded. [R3–R5] |
| 3 | Classify each capability as supported, experimental or excluded from publication claims. | E | METHOD_STATUS explicitly distinguishes experimental methods and unsupported scientific claims. Use this as the manuscript scope baseline. [R4] |
| 4 | Write the central contribution in two sentences: intended users, research task, and the practical gap addressed. | E | Proposed central contribution supplied in this report, grounded in README/manual; uniqueness remains unproven. [R3, R6] |
| 5 | Separate established kinetic methods from original software/workflow contributions. Do not claim a new physical theory without evidence. | E | Established equations separated from software/workflow contribution in the proposed scope below. [R4] |
| 6 | Make a claim–evidence table: proposed sentence, implementation location, verifying test, dataset, citation and limitation. | P | Initial manuscript claim map and 78-row progress ledger created; final sentence audit still required. |
| 7 | Resolve or narrow claims affected by ambiguous units and temperature-ramp reconstruction. | P | Explicit Python source-unit conversions and quantified CLI ramp rejection implemented/tested. GUI unit mapping remains absent. |
| 8 | Freeze the feature scope. Add features only when needed to fix a demonstrated defect or support a retained claim. | H | Approve a bounded publication feature scope; no evidence of a final feature freeze. Do not add unsupported methods to enlarge the paper. |
| 9 | Establish when the repository first became public using available historical evidence; distinguish this from repository creation and earliest commit. | P | Creation date 17 October 2026 establishes a hard upper bound on age. Exact first-public date is not exposed by the inspected metadata. [R1] |
| 10 | Inspect whether meaningful development spans more than six public months. | G | Cannot pass today: repository was created only 11 days before audit. More than six months of active public development is required. [R1, J1] |
| 11 | Record releases, fixes, documentation changes and feedback-driven iteration. | E | Issues/PRs and successive beta corrections document iteration; releases endpoint returns none. Long-term sustained development is not yet demonstrated. [R2, R7] |
| 12 | Identify an actual research workflow using the software; a demo download or intention to use it is insufficient by itself. | G | No completed actual research-use case established by inspected materials. Synthetic demos and a literature catalog do not by themselves establish this gate. [R8] |
| 13 | Preserve shareable evidence of that use, with permission where needed. | G | No completed research-use evidence package found. Preserve an authentic workflow/application when it exists. |
| 14 | Check the actual plain-text OSI-approved licence and third-party/data licensing boundaries. | P | LICENSE contains MIT grant text plus a custom scope preamble; GitHub reports NOASSERTION. ASSET-RIGHTS separates code/data. Clarify standard license presentation and confirm ownership. [R1, R9] |
| 15 | Confirm public source browsing, cloning, readable issues and contribution pathways. | P | Metadata says public and issues/PRs are available. Anonymous clone/browse/issue access was not independently tested; authenticated connector access alone does not prove it. [R1, R7] |
| 16 | Record truthful software contributions and decide authorship accordingly. | H | CITATION.cff identifies Karol; final author list, contribution account and approvals require humans. [R10] |
| 17 | Record AI tools/models and versions where known, their roles, and human verification. Do not invent unavailable historical version details. | P | Codex assistance is mentioned for assets, but no consolidated manuscript-level AI tools/roles/human-verification disclosure was found. Reconstruct it truthfully. [R9, J1] |
| 18 | Inspect existing test coverage by scientific claim, not total number of tests. | E | Existing central tests mapped and baseline executed: 307 passed/38 display-dependent skips. |
| 19 | Implement or retain independent reference calculations that do not simply call the production simulator again. | E | Independent separable/quadrature references exist for six orders and three ramps, plus zero-order and component references. Reuse them. [R12–R14] |
| 20 | Define a small benchmark matrix covering the published scope. | E | Frozen bounded protocol and 36-case independent numerical matrix executed; output retained. |
| 21 | Fix acceptance tolerances and exclusions before evaluating results. | E | Reuse existing 2e-6 normalized-population tolerance; report explicitly limits its scientific meaning. CLI 2 K screen is engineering, not calibration. |
| 22 | Record absolute/relative parameter error, prediction error, bias and failure rate where relevant. | P | Numerical errors, fit results, conditional ranges and 1200 records retained. No repeated-dataset bias or coverage claim. |
| 23 | Include difficult cases and publish failures; do not select only favorable spectra. | E | Tests explicitly include coincident/exchangeable components, failed competitors, withheld intervals and cancellation. This verifies tested behavior, not all experimental failure rates. [R13, R14, R17] |
| 24 | Confirm parameter labels distinguish fitted, assumed, derived and unavailable values. | E | Result-view tests distinguish assumed, derived, regression, fixed and non-unique quantities. [R18] |
| 25 | Have a domain scientist inspect equations, units and interpretation independently of the implementation. | H | No independent human scientific sign-off is claimed by current method status. Arrange a bounded equation/unit/interpretation review. [R4] |
| 26 | Specify the reference model, noise estimate, perturbation distribution, refit settings and output statistics. | E | Monte Carlo implementation and guide specify fitted reference, residual sigma, iid Gaussian noise, settings and conditional percentiles. [R17, R19] |
| 27 | Verify seeded reproducibility and stability across independent seeds. | P | Three seeds and nested 100/200-count prefixes assessed for two single-model cases. Endpoint differences quantified; no universal convergence established. |
| 28 | Check convergence with replicate count using representative easy and difficult cases. A fixed count such as 500 is not inherently sufficient. | P | 100/200-prefix parameter sensitivity assessed; high-noise drift sensitivity remains. Multi-model ranking convergence is still open. |
| 29 | Audit accounting: requested, attempted, successful, failed, cancelled and ranking-eligible replicates. | E | Code/tests retain completed replicates, per-model success/failure and incomplete-ranking accounting; cancellation behavior is tested. [R17] |
| 30 | Check that candidate models receive the same generated observations in each comparison replicate. | E | Synthetic observations are generated once per replicate outside candidate comparison; each candidate uses that realization. [R17] |
| 31 | Examine how boundary solutions, degeneracy and failed competitors affect reported ranges and rankings. | P | Boundary/degeneracy safeguards and failed-competitor withholding exist; quantify their selection effects on ranges/rankings in a small assessment. [R13, R17] |
| 32 | Confirm exports retain seed, noise assumptions, settings and failure counts. | P | All 1200 refit records archived with seeds/noise/success counts plus executable assessment script; final GUI export audit remains. |
| 33 | Choose the claim: conditional stability ranges, or statistically calibrated intervals. | E | Existing docs explicitly choose conditional refit ranges and reject calibrated-CI/mechanism-probability interpretations. Keep this scope. [R4, R19] |
| 34 | If claiming nominal confidence coverage, run an outer repeated-dataset experiment: generate independent datasets with known parameters, construct an interval for each, and measure coverage with Monte Carlo sampling uncertainty. | D | Defer for the initial paper: no general confidence-coverage claim is proposed. Separate bootstrap tools do not validate Explorer intervals. [R16] |
| 35 | Assess noise-model mismatch if robustness to correlated/heteroscedastic noise is claimed; otherwise state the exclusion explicitly. | E | Gaussian-noise assumptions and excluded drift/correlation/calibration/model uncertainty are explicit. No robustness claim is supported. [R4, R19] |
| 36 | Select an isolated, well-characterized desorption case compatible with the implemented physics. | P | First catalog lead inspected and unsuitable for a simple unqualified energy comparison; CC-BY raw external dataset selected for a narrower input/peak test. |
| 37 | Prefer raw deposited data or author-provided data over extracting a printed curve. | E | Original RODARE workbook acquired and MD5 matched; selected measured columns preserved with SHA256 provenance. |
| 38 | Record DOI, dataset identity, figure/trace if applicable, acquisition conditions, heating rate, units and sample context. | E | Dataset/article DOIs, sheet, signal, source units, measured time, heating rate and transformations recorded. |
| 39 | Confirm redistribution rights separately for data, digitized coordinates and source images. | E | RODARE file license CC-BY-4.0 verified; attribution and changes included with derived CSV. No rights inference for Brown/Bolina figure. |
| 40 | For digitization, record axis calibration, log/linear scales, line thickness/resolution, overlaps, extraction method and uncertainty. | D | No digitization required for the selected deposited numerical dataset. Catalog digitizations remain not started. |
| 41 | Distinguish measured time from an assumed linear-ramp time reconstruction; document any missing inputs. | E | Actual measured seconds and kelvin retained; explicit conversion verified against source numeric arrays. |
| 42 | Reproduce the original analysis assumptions before comparing reported parameters. | P | Published heating program and approximate D2 peak confirmed. Kinetic-energy reproduction has not been completed. |
| 43 | Prespecify baseline, fit interval, fixed prefactor/order and comparison criterion. | P | No smoothing/baseline processing used for input/peak check; full trace rejected by specified ramp screen. Suitable energy-fit design still required. |
| 44 | Compare predicted spectra/residuals and parameters, accounting for digitization, approximation and methodological differences. | P | 92.06 K sampled peak agrees with rounded ~92 K article description; no experimental energy/parameter-fit validation claimed. |
| 45 | Examine sensitivity to baseline, fit window, prefactor and heating-rate assumptions. | P | PTCDA deposited-data study evaluates 73 traces with three starting prefactors and both baseline hypotheses (438 fits); window/heating-rate sensitivity and commensurate energy comparison remain unfinished. See validation/experimental/ptcda_au111/. |
| 46 | Explain disagreement rather than tuning settings until the published energy is matched. | P | Full-trace 4.17103 K mismatch recorded rather than relaxing tolerance to force a kinetic result. |
| 47 | Add one challenging case if it tests a retained claim, such as overlapping populations or a coverage series. | D | Second challenging experimental case is deferred until the first is complete; add only for a retained publication claim. |
| 48 | Obtain an independent scientific reading of what the case does and does not validate. | H | Independent reading of the completed experimental result remains future human work. [R4] |
| 49 | Install from source in a clean supported environment using documented instructions. | P | Wheel built and installed into isolated target from unrelated cwd. Core and 40 Help topics verified after a packaging fix; full desktop sidecars/clean Windows remain separate. |
| 50 | Test the exact packaged Windows build on a clean machine without Python. | H | Clean Windows 10/11 without Python on the exact ZIP explicitly remains untested. [R21] |
| 51 | Complete human display/DPI acceptance on the supported configurations. | H | Human display/DPI/first-run acceptance explicitly remains unverified; widget geometry tests are not this check. [R21] |
| 52 | Run a documented import → preparation → analysis → save/load → export workflow. | P | Current frozen CI exercises workflow/project/report export. Complete the human documented workflow on the final ZIP. [R2, R21] |
| 53 | Confirm cancellation, malformed input, unavailable outputs and recoverable errors behave honestly. | E | Added meaningful CLI regression: hold-like ramp rejected and kinetic optimizer never called. Existing failure/cancel tests retained. |
| 54 | Check GUI, CLI and Python results agree where they expose equivalent calculations/settings. | P | Adapter-vs-engine tests and CLI export tests exist; no complete equivalent-settings GUI/CLI/API comparison matrix. [R15, R20] |
| 55 | Confirm exported units, assumptions, settings, input hashes, version and Monte Carlo provenance match the displayed analysis. | P | Source/snapshot/hash/role tests are strong; a final end-to-end audit of exported results against submitted settings is still needed. [R18, R20] |
| 56 | Document core API, examples with expected outputs, scientific assumptions and supported environments. | P | Fixed stale checkout command and documented explicit API units/ramp screen; wheel offline Help fixed. Comprehensive core API reviewer guide remains partial. |
| 57 | Supply a concise reviewer verification command plus a manual GUI checklist. | E | Reviewer verification commands and expected bounded results added; manual acceptance clearly separate. |
| 58 | Check CONTRIBUTING, support routes, changelog and citation metadata. | E | CONTRIBUTING, changelog, README support routes and CITATION.cff exist; final DOI/author metadata are separate unfinished work. [R3, R5, R10] |
| 59 | Publish a tagged beta/release with durable downloads; expiring Actions artifacts are not the final distribution plan. | G | No published releases returned by GitHub; README confirms no tagged prerelease. Tags collection request was unsupported, so tag absence was not independently established. [R2, R3] |
| 60 | Ask one or two relevant colleagues to perform a specific workflow and record authentic feedback and fixes. This is a recommendation, not a required user quota. | H | A checklist/feedback form is prepared; authentic external completed workflow/feedback is not established by inspected public records. [R7, R21] |
| 61 | Verify alternatives from their primary publications, repositories and documentation; do not infer missing features from a quick search. | P | Primary descriptions verified for TPD Calculator, tpd-analyse and TDS Simulator; wider equivalent-workflow alternatives and author rationale still need review. |
| 62 | Build a compact comparison using task-relevant dimensions: kinetic laws, interface, uncertainty, reproducibility and extensibility. | P | Source-backed comparison and limited build rationale drafted without claiming absent features or superiority; final author assessment pending. |
| 63 | Verify primary references for each retained physical method and approximation, including exact bibliographic metadata. | P | Method/reference identifiers verified and bibliography drafted. Complete primary-source review of all retained methods remains open. |
| 64 | Cite datasets, methodological sources, relevant software and dependencies that materially support the work. | P | paper.bib now cites method, tools and dataset/article; dependency citations and final completeness check remain. |
| 65 | Verify author names, affiliations, ORCIDs where supplied, contributions and funding. | H | Final affiliations, ORCIDs, contributions, funding and author approval require confirmation; do not infer from profile. [R10] |
| 66 | Draft paper.md and paper.bib with explicit unresolved placeholders; never turn a planned benchmark into a completed result. | E | ~1000-word working paper.md and bibliography created with explicit human-confirmation placeholders; not submission-ready. |
| 67 | Generate at most one initial overview figure combining a real software workflow and a reproducible analysis result. Additional figures need a clear purpose. | E | Reproducible two-panel numerical/experimental assessment figure generated and visually inspected. No fabricated GUI screenshot. |
| 68 | Link detailed validation, equations, test commands and tutorials from the repository. | E | Draft and reviewer guide link detailed methods, assessment conditions, source data/provenance and code. |
| 69 | Audit every factual sentence against the claim–evidence table. | P | Draft avoids unsupported adoption, energy validation and confidence-coverage claims; final human/claim audit remains. |
| 70 | Compile using the journal's current supported preview workflow; inspect citations, metadata, figure readability and word length. | P | Local Pandoc/citeproc PDF compilation succeeded. Official JOSS-template preview and final layout verification remain open. |
| 71 | Recheck live journal requirements immediately before submission. | F | Guidelines rechecked for this audit; repeat immediately before actual submission. [J1] |
| 72 | Confirm all screening gates, exact version, source access, licence and research-use evidence. | F | Submission gate cannot be completed now: public age, research-use evidence and other preparation remain incomplete. [J1] |
| 73 | Complete the official reviewer checklist against the actual release. | F | Official checklist audit must target the final reviewed release; this report supplies a preliminary evidence map. |
| 74 | Reserve time for iterative review and fixes; publication timing cannot be guaranteed. | H | Reserve review time when a real submission window is chosen. |
| 75 | Conduct author–editor/reviewer conversation personally. Current JOSS policy prohibits AI for those conversational interactions except translation. | F | Current JOSS policy requires human author–editor/reviewer conversational interactions, except translation. [J1] |
| 76 | Track reviewer issues to fixes/tests and maintain an accurate human-authored response record. | F | No active JOSS review exists in the inspected evidence; track technical fixes when review occurs, with human-authored conversations. |
| 77 | At successful review completion, tag the reviewed version, archive the software with a DOI, and provide the version and archive DOI as directed. | F | Archive the reviewed tagged release and provide DOI/version at successful review completion; do not invent DOI now. [J1] |
| 78 | Update citation metadata and documentation with the accepted paper and archived software identifiers. | F | Update accepted-paper/archive identifiers after they actually exist. [R10] |

## Local evidence and reproduction

- `docs/JOSS_ASSESSMENT_PROTOCOL.md`: conditions, tolerances and amendment.
- `validation/joss_parameter_stability/assessment.json`: 36-case matrix, fits,
  seed/count summaries, environment and script hash.
- `validation/joss_parameter_stability/*seed*.json.gz`: full 1200 records;
  standard gzip JSON, preserving requested/completed counts and warnings.
- `validation/experimental/rodare_4644/`: measured input, attribution,
  provenance and result. DOI 10.14278/rodare.4644, article 10.1038/s41467-026-75930-9.
- `validation/joss_checkpoint_tests.xml`: current headless test run.
- `paper/`: working manuscript, bibliography and inspected assessment figure.
- `docs/JOSS_REVIEWER_GUIDE.md`: commands and remaining human checks.

Official requirements: https://joss.readthedocs.io/en/latest/submitting.html,
https://joss.readthedocs.io/en/latest/paper.html and
https://joss.readthedocs.io/en/latest/review_checklist.html.
Earlier evidence IDs R1–R21 refer to the original readiness audit; new status
updates above point to the new repository evidence explicitly.

## Follow-up: first/second ranking stability and portability

Completed a separate bounded two-model study on the existing inputs: six seed
runs, 600 complete rankings and 1200 individual fits; no failed rankings or
120-second seed-run timeouts. First order won all 50/100 prefixes. Full records,
protocol/input hashes and initialization profiles are in validation/joss_ranking/.
Checkpoints 27/28/31 gain this limited evidence but remain partial for general
model comparison: initialization was favorable, only two orders were compared,
and no population-level selection accuracy or confidence coverage was assessed.

The old 81-point multistart replay completed quickly but returned 1.464739 eV
for a first-order synthetic signal generated at 1.1 eV. The previous stall was
not reproduced, and no solver fix is claimed. Investigating initialization and
false convergence is now the next technical checkpoint before generalizing
order-identification or experimental-energy claims.

PR Windows CI exposed CSV CRLF/hash and cp1252 Help-test issues; LF checkout and
explicit UTF-8 correct those paths. Targeted tests: 34 passed, 2 GUI skips.
A Windows-style Git checkout-filter check preserves the exact source CSV bytes.
Corrected scientific CI passed; full rebuilt Windows acceptance remains tracked
by CI and still does not replace human visual/clean-machine acceptance.

## Optimizer correction

Peak-informed kinetic initialization with profiled linear scale/baseline now recovers the formerly failed 81-point case at 1.09463537 eV, NRMSE 0.01273470. Independent noisy first/second/fractional regressions passed. Full headless suite: 328 passed, 38 display skips. See validation/optimizer_investigation/FIX.md. Historical MC/ranking records remain pre-correction evidence and require reassessment; no universal optimization or experimental validation claim is made.

## Post-fix Monte Carlo reassessment

Source 39c9d7a96d00e40ca5d7ee777f89ea37155e3d7b passed scientific CI and the
full Windows build. Reused the original two spectra and three seeds, with 200
replicates per run and both first/second candidates. All six runs completed:
1200 full rankings, 2400 individual fit records, no failed rankings or timeouts.
First order won 600/600 matched-noise and 598/600 drift rankings. Maximum
first-order percentile endpoint change from historical parameter-only outputs
was 3.13e-6 eV. Equal-100 prefixes differ for drift seed 73 (99/1 versus 100/0),
so changes are not solely due to increasing the count. This limited evidence
advances checkpoints 27/28/31/32; general noise/model robustness, blind recovery
and confidence coverage remain unvalidated. See validation/joss_postfix/.

Next scientific task: acquire/evaluate a suitable full-peak experimental energy
comparison. Existing deposited D2 input/peak reproduction remains a deliberately
limited negative-ramp-screening example, not an energy-validation result.

## Deposited PTCDA/Au(111) model challenge — 29 October 2026

Latest saved source fa534d7 passed both scientific CI and the Windows build.
Acquired unchanged CC-BY-4.0 experimental TPD ZIP from Jülich DATA,
DOI 10.26165/JUELICH-DATA/HQXCXC, linked by Ruiz et al. (2023),
DOI 10.1038/s42004-023-00925-2; deposited SHA-256 matches. Inventoried all
95 files, with 73 passing frozen pre-fit engineering screens in 550–740 K.
Completed 438 first-order conditional fits (three starting prefactors, two
baseline hypotheses): all optimizer-success, 201 prefactor-bound flags,
NRMSE 0.03023–0.16638, maximum baseline-dependent energy shift 2.9891 eV.
Archive, exclusions, settings and every result are retained in
validation/experimental/ptcda_au111/. Acquisition/provenance and baseline/start
sensitivity advance checkpoints 36–46. This does not complete energy validation:
the article's 1.74 ± 0.10 eV is a zero-coverage complete-analysis intercept;
archive coverage labels remain unmapped and the fitted constant-E quantity is
different. Coordinate units are inferred and explicitly documented. No
experimental-fit or manuscript claims were upgraded to external validation.

Next scientific step: establish trace-to-coverage mapping and a commensurate
coverage-dependent analysis, or obtain an isolated constant-energy reference.
Do not repeat the 438 fits; use the retained archive and outputs. Human Windows
visual acceptance and independent scientific review also remain open.

## PTCDA coverage-mapping investigation — 29 October 2026

Completed primary article/supplement review and header-aware audit of all 95
raw files. The article's saturation-integral calibration and supplement's equal
remaining-coverage complete analysis are verified, but raw filenames could not
be assigned to coverage labels or a unique saturation reference. Four detector
scales occur. No guessed assignment or complete-analysis reproduction was run.
See validation/experimental/ptcda_au111/COVERAGE_MAPPING_REVIEW.md and the
reproducible metadata audit. All original 550–740 K arrays match exactly despite
variable header length; the 438 retained fits remain unchanged. Experimental
energy reproduction remains partial, not completed. This closes the source
mapping investigation with a documented metadata blocker; next scientific
checkpoint is a commensurate isolated constant-energy reference. Do not repeat
PTCDA fits unless the missing source calibration/mapping becomes available.

## Accessible pure-ice reference and comparison — 29 October 2026

Acquired checksum-verified CC-BY-4.0 data from Zenodo 10912815, linked to
Kruczkiewicz et al. A&A 686 A236 (2024), DOI 10.1051/0004-6361/202346948.
Verified the final article's Table 3 and leading-edge cutoffs. Original Ar/CO
CSV units and chemical headers are explicit. Pre-fit protocol retains primary
and sensitivity windows and baseline cases. Six completed full-peak fits hit
0.05 eV with NRMSE 0.2191–0.3243; two Ar interval/method combinations were
withheld for non-increasing temperatures. Independent CO nonlinear leading-edge
results are 1069.87 K (zero baseline) and 718.74 K (free baseline), versus
1040 ± 104 K published. An explicitly later application log-regression check
gives 1336.50 K using 26/78 positive points, matching independent NumPy OLS
numerically. All outcomes are retained without interval/bound tuning.

See validation/experimental/ice_2024/ for inputs, exclusions, protocols,
results and comparison figure. This advances acquisition, comparable-source
inspection and negative/sensitivity comparisons (36–46), not a positive
experimental energy-accuracy gate. Manuscript now cites and states the negative
result. Next publication task: complete the manuscript claim/evidence audit
against retained positive and negative results; independent scientific review
and positive experimental accuracy evidence remain open. Do not rerun the
completed PTCDA or pure-ice assessments without a changed hypothesis or input.

## Diagnosis and targeted data-expansion plan — 29 October 2026

Verified that the branch already contains the exact Ar/CO compressed originals,
fit records, log diagnostic, figure, and PTCDA source archive. Added directly
inspectable original Ar/CO CSV copies, preserving source bytes and line endings.
validation/experimental/FINDINGS_AND_NEXT_STUDIES.md separates observed model
mismatch/baseline sensitivity from unproven instrument and physical explanations.
The existing zero-order core has bound/large-residual warnings; visibility in
GUI/exports requires inspection, not an invented missing-feature claim.

Recommended scope is two new independent studies: isolated first-order and
resolved zero-order depletion. A third rate/coverage series is optional and must
test a retained claim. next_study_plan.csv records unstarted/lead-only status;
no extra acquisitions or new validation passes are claimed. Do not count MC
refits as independent data. The manuscript claim/evidence audit remains the
next publication checkpoint; targeted acquisition can proceed with frozen
admission and stopping rules, without repeating completed assessments.

## Figure digitization from three papers — 29 October 2026

Completed four figure-derived experimental traces: purple D2O/Fe3O4 from Zaki
et al. (2018), light-pink 11 ± 2.1 ML pure MeSH from Narayanan et al. (2025,
preprint v1 explicitly identified), and pure Ar/CO from Kruczkiewicz et al.
(2024). Two papers extend the collection; the previously acquired ice paper is
used for independent source-to-figure QA. Total 2071 recovered coordinates,
with 68 water and 16 MeSH raster columns blank. These are not independent
experimental samples or raw instrument data. Sources, licences, calibration,
source hashes, extraction code and QA overlays are retained in
validation/digitized/. No digitization or prior kinetic fits were repeated on
resuming this work; only documentation and verification remained.

The new vector check confirms Ar correspondence (peak difference -0.059 K,
NRMSE 0.00589) but reveals CO correspondence uncertainty (28.967 K published
figure versus 38.155 K deposited CSV; height ratio 3.441). This updates the
previous diagnosis: original deposited-CO fits are preserved, but cannot yet
stand as trace-matched reproduction or justify attribution of the literature
disagreement mainly to model mismatch. Paper and assessment notes now carry
this correction. No source error or physical cause is asserted without evidence.

Advances trace extraction/provenance/uncertainty checkpoints 36–44 and handling
of disagreements (46). Positive experimental energy validation and independent
human scientific review remain open. Next: freeze suitable analysis settings
for the new digitized cases, with gaps/uncertainty respected, and finish the
manuscript claim/evidence audit. Do not refit historical datasets simply to
recover a published number.


## 29 October 2026 — three additional literature studies screened

Added `validation/experimental/additional_studies_2026_10_29/`: Perrero et al.
2024 (ethanol/ethylamine), Fulker & Brown 2024 (two esters), and Martín-Doménech
et al. 2014 (five pure ices). Nine molecular-system targets across three additional
papers; no additional digitization or kinetic fits claimed. Existing fits were
not repeated. Five source figure images from the first two papers were acquired
and hash checked; reproducible retrieval retains their separate licences outside
the checkout. The third source PDF is accessible but figure reuse rights remain
unverified. Raw Sussex archive access failed and is recorded.

The new CSV separates trace-specific from aggregate references, fixed prefactors
from unidentified intensity scales, and single-energy approximations from energy
distributions. Fig. 6C methyl acetate is 42.8 +/- 0.7 kJ/mol, distinct from Table 2.
Next admission work: permissions, exact experimental-curve extraction and QA,
then frozen fit protocols and matched-estimand comparisons. These candidates
expand source screening; they do not close experimental-accuracy checkpoints.


## 29 October 2026 — ethanol conditional comparison completed

`validation/experimental/ethanol_2024/` retains Fig. 7 experimental-only raster
extraction, 32 unrecovered columns, frozen protocol, 20 completed fits, full
predictions/diagnostics and source licences. No existing fits were repeated.
At the published 3.31e18 s^-1 prefactor, production simulation plus an assessment
profile gives 6434.54 K (free baseline), versus the dominant published 6450 K
population. Production free-prefactor fitting instead gives 7612.90 K and
1.61e22 s^-1 with smaller residuals. Baseline/window dependence and structured
residuals remain. This is conditional correspondence, not independent population
recovery or general accuracy. The production fitter has no fixed-prefactor option.

Four engineering pixel scenarios span 6416.99–6452.07 K, not a confidence interval.
Independent quadrature agrees with production rate to 3.20e-6 of peak. All 20
fits complete without exceptions or identified bound hits; no MC or GUI tests
were performed. AI-assisted visual checks complete; independent human scientific
review remains pending. Next: review this extraction/interpretation, then one
commensurate case from another study, rather than expand the literature list.


## 29 October 2026 — methyl-acetate comparison completed

`validation/experimental/methyl_acetate_2024/` adds the labelled 50 Lm Fig4B
spectrum and a separate Fig6C corrected-ordinate reconstruction. Initial hue
selection and axis errors were found by enlarged-image QA; the invalid pilot
is retained but excluded. Corrected-input settings retain the original windows,
after exploratory energies were known; no blinded/preregistered claim.

Primary leading-edge energies are 38.86 without offset and 42.22 kJ/mol after
the declared pre-edge median, versus published 42.8 +/- 0.7. Alternate window
gives 37.81/40.29. Missingness is substantial (112/213 columns); baseline and
nonzero-order correction differ from the published analysis. Whole-peak
zero-order fits give 12.65/18.32 kJ/mol with NRMSE .1681/.1327: completed
optimizations, not accurate physical energies. Fig6C reconstruction is 42.63,
not independent raw-spectrum validation. All 11 accepted assessment records,
residuals, sources, licences and superseded pilot are retained. No production
code change, old dataset rerun or MC. Human scientific review remains open.
Next useful publication task: consolidate claim/evidence limits across ethanol,
methyl acetate and earlier negative cases before expanding the dataset list.


## 29 October 2026 — manuscript evidence consolidation and next paper

Completed `docs/JOSS_CLAIM_EVIDENCE_AUDIT.md`, mapping numerical, Monte Carlo
and experimental evidence to allowed claims and remaining gates. The manuscript
now cites ethanol and methyl-acetate studies, includes favourable and alternative
results, and retains adoption/human-review/history gaps. Prior fits were not rerun.

Then assessed the already-digitized pure-MeSH curve from arXiv:2504.01102v1,
without repeating extraction. `validation/experimental/mesh_2025/` retains 12
declared cases: four leading edges (4849–5492 K), four whole-peak zero-order
fits (2496–2717 K; NRMSE .1199–.1518), and four engineering pixel scenarios
(4161–5988 K, not a confidence interval). All cases complete; independent OLS
agrees with production to 2.82e-11 K. Structured whole-peak residuals and
method/window dependence remain; 4610 +/- 110 K is a TST-conditioned literature
recommendation, not an identical estimand. Absolute-prefactor reproduction is
withheld without verified conversion/calibration. No source error or physical
cause is inferred. Production code unchanged; no MC or GUI acceptance claimed.

The audit and manuscript now include MeSH as method-limit evidence. Three-paper
assessment batch complete at this bounded level. Remaining high-value gates:
independent human scientific/Windows acceptance, actual research-use evidence,
author/disclosure confirmation and public-development-history eligibility.


## 29 October 2026 — focused scientific review package prepared

`validation/review_package/README.md` selects ethanol, methyl-acetate leading
edge and its whole-peak mismatch, with three scientific questions, an unfilled
response template and one bounded Windows acceptance exercise. No reviewer was
contacted and no endorsement/adoption/acceptance is recorded.

Prepared a GUI-compatible D2 CSV using measured time s->ms and temperature
K->degC, with provenance and no reconstructed ramp. Import retains 289 points,
peak -181.09 degC/92.06 K and zero temperature-cleaning changes. Signal parsing
difference is 1.01e-16 of peak. The initially overly strict bitwise signal
comparison was replaced by an explicit 1e-14 relative tolerance; this is float64
CSV parsing, not a numerical-method change. No historical fit was repeated.

Using a retained methyl-acetate mismatch, the Explorer exporter preserves all
warnings, conditional prefactor cautions, settings, curves and residuals.
Presentation helpers preserve warning text and representative-parameter roles.
These are headless checks on Linux with no display, not rendered GUI acceptance.
Native workflow PDF export and all Windows checklist steps remain NOT RUN.
`scripts/prepare_scientific_review_package.py` reproduces these checks into a
fresh directory without calling a fitter. Production code unchanged.

Next external gate: obtain an actual independent scientific response and execute
the bounded Windows exercise on a recorded build. Do not replace these gates
with additional automated fits or mark the response template completed.
