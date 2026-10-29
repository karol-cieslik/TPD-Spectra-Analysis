# Figure-derived experimental spectra from three papers

Completed 29 October 2026. Four experimental curves from three distinct papers
are retained here as **digitized figure coordinates, not raw acquisition data**.
No kinetic fits were run in this extraction step. The 2071 recovered coordinates
are not 2071 independent experimental observations. The 2024 ice paper is an
existing source reused for a new source-to-figure check; the other two papers
extend the collection.

| Paper and figure | Retained curve | Recovered coordinates | Signal scale | Heating rate |
| --- | --- | ---: | --- | --- |
| Zaki et al. (2018), [DOI](https://doi.org/10.1039/C8CP02333F), Fig. 1a | Purple D2O/Fe3O4(111) trace | 644 | Visible-peak normalized; source arbitrary units | 3 K/s |
| Narayanan et al. (2025), [DOI](https://doi.org/10.3847/1538-4357/adc7b6), Fig. 2 | Light-pink pure MeSH, 11 ± 2.1 ML legend | 908 | 10^15 molecules/K | 2 K/min |
| Kruczkiewicz et al. (2024), [DOI](https://doi.org/10.1051/0004-6361/202346948), Figs. 2b and 3a | Pure CO and Ar | 328 + 191 | ML/K | 0.2 K/s |

## Files and provenance

- [Water on magnetite](water_2018/README.md), [CSV](water_2018/digitized.csv).
- [Methyl-mercaptan ice](mesh_2025/README.md), [CSV](mesh_2025/digitized.csv).
- [Pure-ice study](ice_2024/README.md), [CO CSV](ice_2024/CO_digitized.csv),
  [Ar CSV](ice_2024/Ar_digitized.csv).

Each folder retains the source figure or PDF path vertices, axis calibration,
source URL/version and PDF hash, licence/attribution, extraction settings,
quality record and source-overlay figure. `extraction_summary.json` records
counts; `file_manifest.json` fixes the delivered file hashes. DOI identifies the
paper, while `source_version` specifies the actual extracted version where
applicable. The MeSH input is the explicitly CC-BY-4.0 arXiv preprint v1, not the
publisher's final layout. Curve identities are based on the retained figures;
the water exposure remains unassigned because its numeric legend is not an
explicit colour key.

## Extraction method and uncertainty

Two plots are embedded raster images. Their colour-selected centerlines are
converted using linear axis anchors. Columns with invisible colour or a vertical
span above 12 pixels are left blank, including occluded/steep sections. No gap
interpolation, smoothing, invented zero signal or constructed measured time is
used. Axis labels were read from the figure; OCR is not used to infer data.

Raster signal bounds combine line width and sensitivity to colour thresholds.
Temperature pixel size and a separate axis-placement allowance are reported.
These engineering bounds exclude instrument calibration, plotting/smoothing
choices and original experimental uncertainty. They are not confidence
intervals. The water plot has no numerical signal ticks; only normalized shape
can be recovered without inventing a calibrated amplitude.

The pure-ice PDF preserves line paths. Plot coordinates are mapped using panel
axis ticks; unused ticks cross-check the calibration. A 0.25 PDF-point axis
placement allowance is recorded (about 0.19 K). The plotted vertices are not the
instrument's original sampling grid. All source overlays were visually inspected
with the listed gaps retained. This is AI-assisted QA, not independent human
validation; `visual_review.json` records that distinction.

## Important source discrepancy

The vector-derived Ar peak is 29.718 K versus 29.777 K in the deposited CSV;
its comparison NRMSE over 22–60 K is 0.00589. In contrast, the published CO curve
peaks at 28.967 K and 0.33194 ML/K, while the deposited CO CSV peaks at
38.155 K and 0.09646 ML/K. This is much larger than the axis-reading allowance.
The cause is unresolved. See [the interpretation correction](SOURCE_CORRESPONDENCE_UPDATE.md)
before using the earlier CO fit assessment. Neither file has been replaced,
relabelled as the other, or blamed on an author error without evidence.

## Reproduce

From the repository root:

```sh
python scripts/digitize_published_figures.py
```

This regenerates coordinates and QA from the retained source images/paths,
without network access or kinetic fitting. File hashes identify this delivered
snapshot; rerendered PNG bytes may differ with plotting-library versions.
Source-image hashes must remain unchanged. Coordinate-level output can be
checked independently against the displayed source and calibration records.

## Attribution and reuse

Original material retains its own licence rather than the repository software
licence. Reproduced/adapted from E. Zaki et al., PCCP 20 (2018) 15764–15774,
Royal Society of Chemistry, under [CC-BY-3.0](https://creativecommons.org/licenses/by/3.0/);
S. Narayanan, E. L. Piacentino, K. I. Öberg and M. Rajappan, arXiv:2504.01102v1
and ApJ 986 (2025) 10, under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/);
and F. Kruczkiewicz et al., A&A 686 (2024) A236, under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
Changes comprise figure extraction/cropping, coordinate digitization and QA
annotations. The original researchers did not perform or endorse these analyses.
