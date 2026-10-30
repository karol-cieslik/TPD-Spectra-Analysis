# 2-propanol/HOPG fractional-order candidate

This is a screened external dataset, not a completed fit or a validation pass.
Ayling et al. report a monolayer desorption order of 1.23 ± 0.03 for
2-propanol on highly oriented pyrolytic graphite (HOPG), as well as an
amorphous multilayer order near zero. Their Fig. 2 plots the 1–10 Lm monolayer
coverage series; experiments were run at 26 K with a linear 0.5 K/s ramp. The
authors interpret the fractional monolayer order as evidence of intermolecular
interactions and island formation, so it is a useful non-integer-order case.

**Source:** S. A. Ayling, D. J. Burke, T. L. Salter and W. A. Brown, “Desorption
and crystallisation of binary 2-propanol and water ices adsorbed on graphite,”
*RSC Advances* 7 (2017), 51621–51631, [DOI 10.1039/C7RA10410C](https://doi.org/10.1039/C7RA10410C).
The article states a Creative Commons Attribution 3.0 Unported licence.

## Status and next step

The article's text, kinetic table and experimental conditions were reviewed.
The publisher PDF and figure-image endpoints returned access errors in this
assessment, and the ResearchGate figure image was also inaccessible. No plot
pixels were read, no digitized curve was created, and no production fitter was
run on this study. Do not count the published order value by itself as a
software validation.

To admit this study as a figure-derived test, digitize the 1–10 Lm traces in
Fig. 2A, record pixel calibration and trace ambiguity, and preserve the
digitizer uncertainty. Then fit the digitized traces with the production
Polanyi–Wigner comparison, using the reported 0.5 K/s ramp and a frozen baseline
and temperature interval. Compare the fitted order with the reported
1.23 ± 0.03 as a model check, not as an identical estimator: the paper derives
its order from a regression of log intensity against log integrated coverage
over several fixed temperatures. Retain fit failures and assess sensitivity to
trace overlap and digitization error. The separately reported near-zero
multilayer order is an additional hypothesis, but the Fig. 2B traces include
amorphous/crystalline phase changes and should not be treated as a simple
single-state zero-order validation.

`protocol.json` records the source details and pending admission criteria. No
source data are redistributed here.
