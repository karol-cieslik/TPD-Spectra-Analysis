# Manuscript claim–evidence audit

Updated 29 October 2026. This audit consolidates retained results; it does not rerun fits or turn author-led reanalysis into independent adoption. Start with the source-case READMEs for protocols, licences, gaps and limitations.

| Claim or evidence | Verified scope | Manuscript treatment |
|---|---|---|
| Numerical implementation | 36 independent quadrature cases over six orders, three ramps and two grids; worst population error about 9.65e-7 against a 2e-6 target | Supported within tested synthetic conditions; not physical calibration |
| Conditional Monte Carlo | Saved single-model/ranking/post-fix experiments retain failures and successful refits | Conditional iid Gaussian parametric refitting; no demonstrated confidence coverage or mechanism probabilities |
| Unit handling and ramp screen | Explicit Python source units; CLI compares measured/reconstructed ramp and can reject | Engineering safeguards; not instrument calibration or a verified GUI unit-mapping workflow |
| Retained full-suite check | Optimizer-fix XML records 328 passed/38 skipped, zero failures/errors | Historical headless verification; subsequent documentation/data work did not rerun it; no current-head CI or human Windows acceptance implied |
| Warning/export presentation check | Headless Explorer export of retained methyl-acetate mismatch preserves warnings, prefactor cautions, settings, predictions/residuals; presentation helpers preserve roles | One export/helper path, without refitting; not a Windows GUI/native PDF acceptance check. Focused review package and unfilled human response are prepared |
| AgY D2 experimental input | Peak 92.06 K, explicit unit conversion, full trace rejected by ramp screen | Import/peak/negative-screen example, not energy validation |
| PTCDA/Au111 deposited series | 73 screened traces, 438 conditional first-order fits; strong baseline/start/bound dependence | Retained model-sensitivity evidence; do not equate whole-trace energies with published zero-coverage intercept |
| Pure Ar/CO | Full-peak model-limit results; Ar graph matches deposition; CO graph/CSV correspondence unresolved | Negative results and source QA; no trace-matched CO reproduction |
| Ethanol/Au | Fixed literature-prefactor harness: 6434.54 K with free baseline versus dominant 6450 K; production free-prefactor fit: 7612.90 K | Conditional correspondence and parameter sensitivity, not recovery of the published mixture; fixed-prefactor harness is not a GUI feature |
| Methyl acetate/HOPG | Primary offset-subtracted leading edge 42.22 versus 42.8 ± 0.7 kJ/mol; alternatives 37.81–40.29; whole-peak mismatch | Baseline/window-sensitive approximation, with incomplete raster input; corrected-ordinate reconstruction 42.63 is not independent validation |
| D2O/magnetite | Figure extraction only; mixed desorption regimes; exposure mapping not assigned | Not an admitted single-state energy validation |
| Pure methyl mercaptan | Existing preprint extraction reused; 12 records. Apparent leading edges 4849–5492 K; whole-peak energies 2496–2717 K versus TST-conditioned 4610 ± 110 K | Method/window/baseline sensitivity and structured residuals; different estimands, no robust reproduction or absolute-prefactor validation |
| O₂/Pt(111) coverage series | 14 author-published spectra; fixed second order has lower AICc than fixed first order on all traces; free-order estimates 2.35–2.73; whole-window fixed-second-order energies 1.07–1.67 eV versus same-source leading-edge estimates about 1.80–1.91 eV | Order-discrimination/model-challenge evidence under a constant-energy single-state model, not energy validation or a universal classifier; source reports coverage-dependent barriers, exposure is not calibrated coverage, leading-edge reference is not independent, and workbooks are not redistributed (no explicit reuse licence identified) |
| Outside adoption/research impact | No independently verified external adoption or software-enabled publication in this work | Remains an author evidence gate; literature reanalysis is not use by the original authors |
| Human acceptance and eligibility | Independent scientific/clean-Windows acceptance, actual research workflow, author metadata/disclosure and public-history eligibility remain open | Preserve explicit draft placeholders; not submission-ready |

## Claims that must not be made

- General experimental accuracy, calibrated error bars, recovery of unique physical prefactors, or universal discrimination of fractional desorption order. AICc preference for second order on the O₂/Pt(111) cases does not establish a universal order classifier or validate whole-window energies.
- Monte Carlo percentages as physical mechanism probabilities, or successful-refit percentiles as demonstrated confidence coverage.
- A benchmark built from already transformed published fit coordinates as an independent experimental validation.
- Optimizer success, high regression R², a small percentage difference or absence of a warning as proof of model adequacy.
- All data freely reusable under the software licence: ethanol-derived materials retain CC-BY-NC-3.0; other source licences remain separately attributed.

## Current defensible conclusion

The software provides numerical TPD analysis with reproducible conditional assessments and explicit diagnostics. Some literature values are closely reproduced under matched assumptions, while alternate assumptions and model mismatch change the estimates. Existing evidence supports transparent bounded comparisons, not general physical accuracy. Figure-derived inputs require human scientific review; superseded methyl-acetate extraction results are explicitly excluded.

The paper now cites the ethanol, methyl-acetate, methyl-mercaptan and O₂/Pt(111) primary articles and reports both favourable and unfavourable alternatives. Its Research impact section still distinguishes software assessment from demonstrated adoption. The three-paper assessment batch is complete at this bounded level. The remaining publication gates are human scientific/Windows acceptance, actual research-use evidence, author/disclosure confirmation and development-history eligibility.

## Evidence locations

- `validation/joss_parameter_stability/`, `validation/joss_ranking/`, `validation/joss_postfix/`
- `validation/experimental/rodare_4644/`, `ptcda_au111/`, `ice_2024/`
- `validation/experimental/ethanol_2024/`, `methyl_acetate_2024/`, `mesh_2025/`, `oxygen_pt111_2014/`
- `validation/digitized/` and `docs/JOSS_CHECKPOINT_PROGRESS.md`
