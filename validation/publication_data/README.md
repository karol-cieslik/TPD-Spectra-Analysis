# Publication-derived data for later TPD tests

This is the central index for publication-derived experimental inputs. Numeric
files remain in their study-specific canonical folders so the source image,
extraction QA, protocol, fit results, and rights record stay together. Use the
relative paths below; do not copy or normalize an input without preserving the
original and updating its provenance record.

“Ready” means a tracked numeric trace exists and can be loaded for a future
analysis. It does not mean the trace is raw data, independently validated, or
suitable for every kinetic model. Figure digitization introduces correlated
uncertainty. “External reference only” means a cited/referenced source exists
but is not redistributed in this repository.

| Dataset | Readiness | Canonical data | Source / limitations |
|---|---|---|---|
| Ethanol/Au(111), figure-derived rate trace | Ready | `../experimental/ethanol_2024/digitized.csv` | Perrero et al. (2024), Fig. 7; CC BY-NC-3.0; protocol and QA in `../experimental/ethanol_2024/`. Multiple populations; not single-state ground truth. |
| Methyl acetate/Au(111) | Ready | `../experimental/methyl_acetate_2024/spectrum.csv` and `published_transformed.csv` | Fulker & Brown (2024); figure-derived; inspect protocol/license and extraction QA before reuse. |
| Pure Ar and CO ice | Ready, with CO correspondence caveat | `../digitized/ice_2024/Ar_digitized.csv`, `CO_digitized.csv`; raw deposited input at `../experimental/ice_2024/raw/` | Kruczkiewicz et al. (2024), CC BY-4.0. CO figure/deposit mismatch is unresolved; do not call it a trace-matched replication. |
| D₂O/Fe₃O₄(111) | Ready for stress checks | `../digitized/water_2018/digitized.csv` | Zaki et al. (2018), CC BY-3.0; normalized signal; multiple populations; not a single-state success case. |
| Pure methyl mercaptan ice | Ready for challenge | `../digitized/mesh_2025/digitized.csv` | Narayanan et al. (2025), digitized from CC BY-4.0 preprint v1; broad energy distribution and source-specific limitations. |
| O₂/Pt(111) coverage series | Reproducible by source checkout; not redistributed | `../experimental/oxygen_pt111_2014/` contains protocol/results; source workbook path and hashes are recorded there | Miller et al. (2014); retrieve the authors' supporting-information repository using the study README. Coverage-dependent barrier; order-discrimination challenge, not clean energy validation. |
| AgY zeolite D₂ | Ready for input/peak check; kinetic fit screened out | `../experimental/rodare_4644/H2_D2_D2_source_units.csv` | Open RODARE dataset, CC BY-4.0; source units preserved and ramp mismatch documented. |
| PTCDA/Au(111) series | Ready for conditional multi-component stress | `../experimental/ptcda_au111/` inventory and compressed fit records | Study-level source audit and limitations are mandatory; 73 traces/438 conditional fits are not independent studies. |
| Methanol/HOPG | Not ready | No numeric curve file | Thesis figures have faded/bleed-through and a 200/300 L label conflict. Candidate record only. |
| 2-propanol/HOPG | Not ready | No numeric curve file | Literature table is useful and article is CC BY-3.0; authorized readable figure/pixels still needed. |
| Ethanol/HOPG | Not ready | No numeric curve file | Cached PDF text is available; graph pixels not inspected and reuse terms unresolved. |
| Coronene/ovalene graphite; O₂/Ag(111) | Not ready | No numeric curve file | Literature candidates; inspect source data/supplements, ramp, licensing and model compatibility first. |

## Reproduction rules

1. Begin from the source-specific README and `protocol.json` when present.
2. Read the source-provenance and rights statement before copying any source
   image or numeric file into a derivative.
3. Use a frozen trace/window/baseline/order protocol and retain failed fits.
4. Store new digitized arrays, extraction scripts, overlays, uncertainty bounds,
   metadata, and hashes together in a new study folder under
   `validation/experimental/` or `validation/digitized/`.
5. Update this index and the manuscript only after source admission and QA. Keep
   candidate sources separate from completed tests.
