# Beta candidate acceptance checklist

## Automated release gates
- [ ] Windows CI passes on the current beta commit.
- [ ] GUI modules import without errors and CLI entry points respond.
- [ ] Portable executable and documentation are included.
- [ ] Preserve successful run URL, SHA, dependency versions and artifact hash.

## Manual Windows smoke tests
- [ ] Launch EXE without a separately installed Python interpreter.
- [ ] Import single CSV, multiple CSVs and folders.
- [ ] Invalid files produce recoverable errors.
- [ ] Show, hide and remove spectra.
- [ ] Compare overlay and small-multiples plots.
- [ ] Change axes, smoothing and normalization.
- [ ] Select leading and peak intervals by dragging with pan/zoom off.
- [ ] Apply exact fractional-temperature limits and check export settings.
- [ ] Resize the layout and switch between control tabs.
- [ ] Run a full analysis; inspect results, warnings and figures.
- [ ] Export publication-quality PNG and open output folder.
- [ ] Test a representative spectrum supplied independently.

## Scientific limits
- [ ] Do not include unvalidated bootstrap intervals in ordinary beta outputs.
- [ ] Treat identifiability diagnostics as warnings, not evidence of a unique mechanism.
- [ ] Check rights before bundling experimental files.
- [ ] Finalize version metadata, release notes and known limitations.

The scientific research branch remains separate. Passing synthetic tests is not independent experimental validation.