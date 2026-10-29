# Focused scientific review package

**Purpose:** assess whether the selected inputs, comparisons and interpretations are scientifically defensible before publication. This is a working review package, not a request to endorse the software or establish external adoption. A focused first pass should take about 20–30 minutes; no rerunning of the historical fitting batch is needed.

Prepared 29 October 2026 from the retained publication-branch assessments. No outreach has been sent. Independent scientific review and Windows acceptance are **pending**.

## Three cases to inspect

| Case | Main result | What needs judgment |
|---|---|---|
| [Ethanol/Au](../experimental/ethanol_2024/README.md) | Fixed literature prefactor: 6435 K versus dominant reported 6450 K. Production free-prefactor/free-baseline fit: 7613 K, with smaller residuals. | The published reference is a mixture dominated by one energy. Is the stated conditional comparison fair, with extraction gaps and single-state limitations adequately disclosed? |
| [Methyl-acetate leading edge](../experimental/methyl_acetate_2024/README.md) | Primary pre-edge-offset result 42.22 kJ/mol versus 42.8 ± 0.7. Other baseline/window settings: 37.81–40.29. | Is the offset physically defensible? Is the uncorrected zero-order approximation clearly distinguished from the paper's coverage-corrected estimate? |
| [Methyl-acetate whole-peak mismatch](../experimental/methyl_acetate_2024/README.md) | Zero-order whole-peak energies 12.65/18.32 kJ/mol, with structured residuals despite numerical completion. | Should the interpretation be restricted further, and do the displayed/exported cautions explain why these are not physical energy recoveries? |

Open the [ethanol extraction overlay](../experimental/ethanol_2024/extraction_check.png) and [comparison/residual plot](../experimental/ethanol_2024/comparison.png), then the [methyl-acetate extraction overlay](../experimental/methyl_acetate_2024/extraction_check.png) and [comparison](../experimental/methyl_acetate_2024/comparison.png). The corrected methyl-acetate extraction is the accepted input; its superseded colour-selection pilot is excluded. A separately extracted transformed plot is reconstruction evidence only.

Each case directory retains its CSV, declared protocol, full results, predictions, source attribution and uncertainties. Degrees kelvin are used in case plots; the native exporter uses degrees Celsius. Reading source figures does not turn their authors into users of this software.

## Three review questions

1. **Are the chosen experimental traces and their extracted coordinates sufficiently reliable for these bounded comparisons?** Identify a mistaken assignment, axis, problematic overlap or uncertainty that changes the conclusion; explicitly mark anything you did not inspect.
2. **Are the compared quantities and assumptions commensurate enough for the claims made?** In particular, assess ethanol's fixed-prefactor/single-state approximation and methyl acetate's baseline, interval and coverage correction. State any scientifically justified change and its reason before new fitting.
3. **Do the residuals, warnings and manuscript wording lead to appropriately limited conclusions?** Identify any blocking error or overclaim, including whether numerical success or small energy differences could still be mistaken for physical validation.

Use [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) for answers. A recorded disagreement is useful evidence; do not mark a question approved if it was not checked. The [manuscript evidence audit](../../docs/JOSS_CLAIM_EVIDENCE_AUDIT.md) and [draft manuscript](../../paper/paper.md) supply context rather than additional required reading for the first pass.

## Export evidence and Windows check

[Headless checks](evidence/headless_checks.json) passed on Linux: the Explorer exporter retained all warnings, prefactor cautions, settings, curves and residuals from the saved mismatch. Presentation helpers retained the same warnings and parameter roles. **No optimizer was called.** Inspect the [exported comparison CSV](evidence/retained_mismatch_export/model_comparison.csv) and [presentation-helper text](evidence/presentation_helper_notes.txt).

This verifies the headless Explorer export path and presentation helpers, not the Windows GUI or its native PDF report. Connecting lines in the exported figure are plotting guides between recovered coordinates, not recovered missing measurements. Export metadata identifies the retained source result and reviewed scientific-code base; the local package identity reports an unrecorded source checkout.

Start with the [exact-build Windows task](PINNED_WINDOWS_TASK.md), which pins the available CI artifact and download/identity checks. The [Windows acceptance checklist](WINDOWS_ACCEPTANCE.md) provides one short measured-data import → apparent fit → save → report → reopen exercise. Its [D2 CSV](evidence/D2_measured_GUI_ms_degC.csv) uses measured time and temperature with explicit unit conversion, not an invented ramp. It is a usability fixture, not an energy reference. Keep the Windows checklist unmarked until actually executed on the recorded build.

## Attribution and reproduction

Ethanol-derived source material retains **CC-BY-NC-3.0** (Perrero et al., DOI 10.1039/D4CP01934B); methyl-acetate-derived materials retain **CC-BY-3.0** (Fulker & Brown, DOI 10.1039/D4RA04466E). The D2 fixture retains **CC-BY-4.0** attribution to Alexandra Becker, Holger Lippold, Jing Liu, Michael Hirscher and Cornelius Fischer, [dataset DOI 10.14278/rodare.4644](https://doi.org/10.14278/rodare.4644). These source licences are separate from the software licence. This package adds coordinate conversions, fit overlays and review annotations; original authors have not endorsed them.

To reproduce only this package's headless checks into a **new** directory:

```sh
python scripts/prepare_scientific_review_package.py --output /path/to/new-review-evidence
```

The existing evidence is preserved; no historical fit is recomputed. Source and output hashes are retained. No broader full-suite rerun or current-head Windows CI success is claimed here.
