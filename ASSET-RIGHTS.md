# Asset provenance and redistribution checklist

The project code and its bundled research materials may have different rights holders.
The MIT license in `LICENSE` applies only to project-authored software code as described
there; it does not automatically license the assets listed below.

| Asset | Current handling | Required check before public redistribution |
|---|---|---|
| `tpd_spectra/`, project entry points and project-authored scripts | Covered by the scoped MIT license, subject to ownership confirmation | Confirm no employer, university, collaborator, or third-party code is included without permission |
| Curated publication-derived numeric examples in `examples/publication_data/` | Nine CC BY-licensed figure-digitized/author-deposited CSV views, source coordinates and dataset-specific citation/limitations manifest are bundled under their original licenses, not MIT | Retain original attribution, figure/version references, licence notices, source values and explicit artificial-time warnings when redistributing adaptations |
| Other experimental TPD/TDS data, proprietary or restricted sources | Not bundled as researcher-facing examples; validation-only records may remain in source | Confirm ownership, collaborator permissions, instrument metadata, matching figure/source identity, and explicit redistribution rights before promoting any further data |
| Historical notebook | Omitted from this code-only repository | Review authorship, thesis-derived text, embedded figures, and third-party content before distributing it separately |
| Schematic image | Omitted from this code-only repository | Confirm authorship or permission and check any third-party figure elements before adding it |
| `output/` analysis artifacts | Generated locally; excluded from the release archive because they can contain stale results and machine-specific absolute paths | Regenerate from approved input data if sample outputs are desired |
| Dependencies | Installed separately from declared package requirements | Preserve third-party license notices for any bundled dependencies in binary distributions; review PyInstaller notices and transitive licenses |
| `tpd_spectra/assets/studio-*`, `studio.ico` and their generator | Original project spectrum mark created with Codex assistance; offered under the repository's MIT license | No external artwork, fonts or institutional marks used; trademark/name clearance is not asserted |

This inventory is a reminder, not a legal determination. Do not make a public repository or release containing an asset until its redistribution rights are clear.
