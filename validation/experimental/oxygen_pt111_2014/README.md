# O₂/Pt(111): second-order coverage-series stress test

This is a new external experimental comparison, not a clean validation of one
constant-energy kinetic model. The source is Miller, Pushkarev, Gellman and
Kitchin, *Simulating Temperature Programmed Desorption of Oxygen on Pt(111)
Using DFT Derived Coverage Dependent Desorption Barriers*, *Topics in Catalysis*
57 (2014), 106–117, [DOI 10.1007/s11244-013-0166-3](https://doi.org/10.1007/s11244-013-0166-3).
The authors' [supporting-information repository](https://github.com/KitchinHUB/kitchingroup-43)
contains the measured `xls/tpd1.xls`–`tpd20.xls` spectra and the full analysis.
The tested source snapshot is commit `f6283ff07df32f982542809b1ab3c2344b24f1d3`.

The source explicitly identifies O₂ desorption as associative and second-order,
with a coverage-dependent desorption barrier. Its raw measurements span 20 O₂
exposures; the source SI baseline-corrects each signal using 400–500 K and
analyzes the chemisorption region over 500–1000 K. The source heating rate is
2 K/s. Its leading-edge procedure reports energy estimates and confidence
intervals for spectra 2–15, which we compare with the Studio's full-window
single-state fit on those same traces.

## Protocol

`protocol.json` freezes the selected preprocessing and fitting settings. The
script `scripts/experimental_o2_pt111_check.py` reads the authors' workbooks
without copying them into this repository. Reproduce it by cloning the linked
source repository and running:

```sh
python scripts/experimental_o2_pt111_check.py /path/to/kitchingroup-43
```

The script subtracts the source's 400–500 K mean, retains 500–1000 K, converts
the workbook's Kelvin temperatures to Celsius for the fitter, and fits at
2 K/s. For each trace it compares fixed first order, fixed second order, and a
free order fit. Energy and prefactor are optimized; 1.9 eV and 1e12 are starting
values. The baseline is fixed at zero after the source subtraction. The
production fitter's normalized initial coverage is 1 and its signal-scale
parameter is free; exposure in L is not misrepresented as a calibrated
coverage. Full results and input workbook hashes are in `results.json`.

## Observations

Across the 14 source spectra with a published leading-edge estimate, fixed
second-order fits consistently beat fixed first-order fits by AICc and NRMSE.
The free-order estimates range from 2.35 to 2.73 for these same traces. This is
consistent with second-order behavior while also showing that a free fitted
order can absorb model departures; it is not evidence for a microscopic order
above two.

The fixed second-order whole-window energy estimates fall from about 1.67 eV at
0.75 L to 1.07 eV at 5 L, whereas the source's leading-edge estimates remain
about 1.80–1.91 eV over that range. That difference is not an energy-recovery
success: the source explicitly models coverage dependence, while the Studio
fit holds energy constant across each whole-peak trace. It demonstrates that
the software favors the expected order over first order on these cases, but its
simple fixed-energy model does not reproduce the published coverage-dependent
analysis. Residual structure, model scope and coverage/prefactor conventions
matter more than optimizer convergence.

| Exposure | Source leading-edge energy | Studio fixed-second-order whole-window energy | ΔAICc (second − first) |
|---:|---:|---:|---:|
| 0.75 L | 1.905 eV | 1.666 eV | −378 |
| 1.50 L | 1.847 eV | 1.276 eV | −241 |
| 2.50 L | 1.861 eV | 1.121 eV | −231 |
| 5.00 L | 1.875 eV | 1.065 eV | −216 |

The source's leading-edge 95% interval for the 0.75 L spectrum is 1.640–2.170
eV; at 5 L it is 1.797–1.952 eV. ΔAICc is descriptive support for one candidate
model on a trace, not a calibrated probability that its order is correct.

The results are conditional on the source's processed data and fit window.
Source leading-edge confidence limits are from the same experiments and are
not independent ground truth; the leading-edge and whole-window estimands are
different. No raw acquisition uncertainty, temperature calibration
uncertainty, order probability, or general accuracy claim is added here.

The source repository does not identify a data reuse licence. Its workbook
files are therefore referenced and hashed in the generated results but are not
redistributed here. This new analysis does not imply author endorsement.
