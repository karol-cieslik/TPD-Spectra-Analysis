# Correction to the deposited-CO interpretation

29 October 2026. A new graph-to-source check changes how the earlier CO
assessment must be interpreted. This does not alter its numerical results.

| Quantity | Published Fig. 2b, digitized | Deposited `2_CO_pure.csv` |
| --- | ---: | ---: |
| Sampled peak temperature | 28.967 K | 38.155 K |
| Peak signal | 0.33194 ML/K | 0.09646 ML/K |

The 9.187 K peak discrepancy and 3.441 height ratio exceed the digitization's
approximately 0.19 K axis-placement allowance. A control from the same page,
Ar Fig. 3a, matches the deposited Ar curve closely: peaks 29.718 versus
29.777 K, height ratio 0.9998, and NRMSE 0.00589 over the stated comparison
interval. Calibration is checked against additional unused axis ticks and source
image overlays. These controls support a real correspondence problem for CO,
rather than a simple global digitization-axis error.

The earlier CO fits were performed on the unchanged, checksum-verified deposited
CSV. Those fits and their baseline sensitivity remain valid descriptions of that
input. However, we had not independently established that this CSV reproduces
the published panel. It cannot yet serve as a trace-matched replication of the
paper's CO energy analysis. The previous impression that the full CO discrepancy
could be explained mainly by model mismatch was premature. Model mismatch is
still directly observable for the selected CSV, but its relation to the
published CO trace is unresolved.

This does **not** prove a wrong label, changed experiment, author mistake,
calibration error, detector artifact or software-wide defect. Do not translate,
stretch or rescale either curve to force agreement. Retain both the original
CSV and the figure-derived curve with separate hashes and provenance.

All earlier files are preserved. No original fits were rerun or replaced.
Before a new quantitative CO comparison, freeze settings on the explicitly
figure-derived input and account for digitization uncertainty, or establish the
deposited CSV's correspondence from additional source metadata. No source
clarification has been requested from the authors. Existing Ar and other
experimental limitations remain independently documented.
