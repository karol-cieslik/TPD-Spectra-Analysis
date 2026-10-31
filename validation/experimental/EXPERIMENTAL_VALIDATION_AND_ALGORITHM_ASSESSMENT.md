# Experimental TPD validation and algorithm assessment

**Status: evidence review and research plan. Research-only profile and variable-projection modules are included; the default fitting path is unchanged.**

This report consolidates completed experimental comparisons, known failure modes,
newly identified fractional-order literature, and algorithm options. Synthetic
recovery tests remain software checks; they are not counted as experimental
validation. Individual spectra from one paper are repeated observations within a
study, not independent studies.

## Executive assessment

The current package has useful numerical and workflow coverage: it can fit
single-state Polanyi–Wigner traces at fixed integer orders, estimate a bounded
free order, profile zero-order exhaustion, compare selected orders, and jointly
fit user-defined overlapping components. Experimental results show it can
distinguish some order hypotheses and can reproduce a literature energy under
explicitly compatible conditions. They also show that a converged, visually
plausible fit can be badly biased when the peak contains a coverage-dependent
barrier, multiple populations, broad energy distributions, an uncertain
baseline, or a detector/transport response not represented by the model.

**Supported claim:** the software is a transparent exploratory fitting and
comparison tool for explicitly selected kinetic models, with useful diagnostics
and known operating limits.

**Not supported:** universal automatic peak decomposition, mechanism
identification from a lowest AICc score, or generally accurate desorption
energies across experimental systems. The empirical evidence remains uneven:
some conditions have strong stress tests, and the 2-propanol/HOPG case now has
a bounded figure-derived comparison; other fractional-order and clean isolated
first-order cases still need full-trace numerical reanalysis.

## Experimental evidence ledger

| Study / dataset | Test performed | Evidence | Interpretation |
|---|---|---|---|
| Ar and CO pure ices, Kruczkiewicz et al. (2024), CC BY 4.0 | Zero-order whole-peak fits; separate leading-edge calculations | Ar/CO full-peak fits reached the 0.05 eV lower bound with NRMSE 0.219–0.324. CO leading-edge energy varied from 718.7 to 1336.5 K with baseline/objective choices against a published 1040 ± 104 K estimate. A source-figure/CSV mismatch is unresolved. | Strong negative/model-scope challenge. The broad measured tails do not match ideal abrupt zero-order exhaustion. CO is not a confirmed trace replication until correspondence is resolved. Details: [assessment](ice_2024/README.md). |
| Methyl acetate on Au(111), 2024 | Figure-derived spectra; zero-order and overlapping-component comparisons | Retains an observed mismatch and sensitivity to selected source trace/colour, window and model. | Useful overlap and digitization challenge; not a clean order-validation pass. Details: [assessment](methyl_acetate_2024/README.md). |
| Ethanol on Au, 2024 | Figure-derived rate trace, fixed/free prefactor and baseline comparisons | Fixed-prefactor fit reproduced dominant literature energy (6435 vs 6450 K); free-prefactor estimates shifted with baseline/window, reaching 7613 K in a primary case. | Conditional positive benchmark and direct identifiability/sensitivity evidence, not proof of general accuracy. Details: [assessment](ethanol_2024/README.md). |
| Methyl mercaptan pure ice, Narayanan et al. (2025), CC BY 4.0 | Digitized leading edge and full-peak zero-order fits | Leading-edge settings gave 4849–5492 K; whole-peak zero-order fits gave 2496–2717 K with structured residuals; source recommends a TST-conditioned reference of 4610 ± 110 K. | Negative case; energy distribution and source uncertainty make it unsuitable as a simple fixed-energy positive control. Details: [assessment](mesh_2025/README.md). |
| O₂/Pt(111), Miller et al. (2014) | 14 author-published coverage spectra; fixed first, fixed second and free order whole-window fits | Fixed second order beat fixed first order in AICc and NRMSE on all 14 traces. Free order estimates 2.35–2.73. Fixed-energy fits drift below source leading-edge energies as coverage rises. | Useful experimental second-order discrimination, but source explicitly has coverage-dependent barriers; not an energy-accuracy pass. Details: [assessment](oxygen_pt111_2014/README.md). |
| 2-propanol/HOPG, Ayling et al. (2017) | Digitized Fig. 2A 1/2/5/10 Lm traces; source-style coverage-series slope and separate single-trace fits | Reconstructed order 1.14 ± 0.05 over declared 137–145 K versus reported 1.23 ± 0.03; ±1-pixel baseline gives 1.111–1.165. Fixed 1.23 fits have lower NRMSE than fixed 1 on all four traces; three free-order fits reach the upper bound. | Figure-derived method challenge only. The source temperature interval is unspecified; the two estimators differ, and no raw-data or energy validation is claimed. Details: [assessment](fractional_2propanol_hopg/README.md). |
| PTCDA/Au(111), 73 spectra | Conditional multi-peak fits and metadata/coverage audit | 438 conditional fits are retained, with source trace mapping limitations and non-unique component decompositions. | Large within-study stress set, not 438 independent validations; do not equate component count with physical state count. Details: [assessment](ptcda_au111/README.md). |
| Ar/CO adsorbed on AgY zeolite, RODARE 4644 | Source-unit and desorption analysis | Independent original-data audit and fit records retained. | Different porous material and adsorption regime; useful external diversity, but inference remains conditional on source and kinetic model. Details: [assessment](rodare_4644/README.md). |

The existing dataset manifests also include several figure-derived or
screened cases. They must be read individually before treating a plotted input
as an executed kinetic comparison. Repository files, source hashes, protocols,
and limitations are authoritative over a count of spectra or fits.

## Newly identified fractional-order experimental set: methanol/HOPG

Bolina, Wolff & Brown, *J. Chem. Phys.* 122, 044713 (2005), DOI
[10.1063/1.1839554](https://doi.org/10.1063/1.1839554), report TPD at β =
0.5 K/s and coverage series at 105 K and 130 K dosing. The article gives
coverage-regression orders at multiple fixed temperatures: methanol Peak A
(monolayer) is approximately 1.23, while Peak B (multilayer) spans 0.17–0.46
and is reported as 0.35 ± 0.21. The authors assign fractional multilayer
behavior to intermolecular hydrogen bonding. This supplies both a near-first
fractional monolayer and a substantially sub-first-order multilayer target.

Karol Cieślik's accessible UCL thesis chapter, “Methanol Adsorption on HOPG: A
TPD Study” in *Adsorption of Astrochemically Relevant Molecules on Model
Surfaces*, contains Fig. 6.2–6.5 coverage-series plots, reports the same
0.5 K/s ramp, and tabulates the fixed-temperature order estimates. It describes
the low-exposure monolayer, emerging overlapping multilayer shoulder, and a
higher-temperature Peak C attributed to a phase change. The source reports
2–15 L low-dose traces and 15–300 L high-dose traces. Source links:
[UCL thesis PDF](https://discovery.ucl.ac.uk/id/eprint/1445324/1/U592644.pdf) and
[journal PDF hosted by UCL](https://www.chem.ucl.ac.uk/astrosurf/pubs/JChemPhys_122_044713-1.pdf).

**Admission status:** the primary article and thesis text/table were inspected;
the scanned figure pages are now visually accessible, but the scan has faded
lines and bleed-through, and one high-dose label conflicts with its caption.
No numeric pixels or Studio fit have been admitted. Do not count the literature
order numbers as software results. The study remains the best documented next
fractional-order benchmark because trace identities, ramp, multiple dose
levels, reported order and peak assignments are available in the thesis.

One source detail needs visual resolution before data admission: the thesis
figure's extracted curve labels include 300 L, while its Fig. 6.3 caption says
the highest plotted exposure is 200 L. Retain this mismatch in provenance and
identify the label from the page image before naming that trace.

**Frozen next protocol:** digitize Fig. 6.2 at 2, 3, 5, 7, 10 and 15 L and Fig.
6.3 at 15, 20, 50, 100 and 300 L only where the source curve labels and peak
identity are unambiguous; retain overlap uncertainty and duplicated 15 L only
as separate traces if they are separate acquisitions. Analyze the same 100 K
dosing series first. Use β = 0.5 K/s, preserve the source's detector signal,
and do not infer absolute initial coverage from exposure in Langmuir. Compare:
(a) Peak A low-coverage subset, (b) isolated Peak B region at intermediate
coverage, and (c) the full overlapping trace as a deliberate single-state
misspecification challenge. Record digitization perturbations, background
choices, bounds, residual autocorrelation and energy–prefactor profiles. The
paper's order estimator regresses log intensity against log integrated relative
coverage at fixed T; a whole-trace Polanyi–Wigner fit is a distinct estimator,
so agreement is a model check rather than exact replication.

Other verified fractional-order leads:

| System | Published evidence | Priority / caveat |
|---|---|---|
| Ethanol/HOPG, Burke et al. (2008), DOI [10.1063/1.2888556](https://doi.org/10.1063/1.2888556) | One coverage series includes near-first-order monolayer (n = 0.98 ± 0.13), greater-than-first-order bilayer (1.52 ± 0.21), and near-zero/fractional multilayer (0.08 ± 0.07); Fig. 5 also shows crystallization/overlap. | Strong mixed-regime candidate. Full-text PDF text is accessible from an alternate cached copy, but figure pixels were not inspected and reuse rights remain unresolved. See [candidate record](fractional_ethanol_hopg_2008/README.md). |
| 2-propanol/HOPG, Ayling et al. (2017), DOI [10.1039/C7RA10410C](https://doi.org/10.1039/C7RA10410C) | CC BY 3.0; monolayer n = 1.23 ± 0.03 and amorphous multilayer near zero; 1/2/5/10 Lm traces at 0.5 K/s digitized from Fig. 2A. | Completed bounded figure-derived challenge; declared-window reconstruction and fit comparisons are retained in [the assessment](fractional_2propanol_hopg/README.md). Not raw-data or energy validation. |
| Coronene/ovalene on graphite, Zacharia et al. (2004), DOI [10.1103/PhysRevB.69.155406](https://doi.org/10.1103/PhysRevB.69.155406) | First-order benzene/naphthalene contrasted with fractional-order coronene/ovalene attributed to stable 2D islands. | Mechanistically distinct size-series candidate; inspect trace availability, ramp and reuse before admission. See [candidate record](fractional_pah_graphite/README.md). |
| Water/Rh(111), Beniya et al. (2008), DOI [10.1063/1.2945873](https://doi.org/10.1063/1.2945873) | Apparent fractional-order spectra; later interpretation allows first-order desorption from coexisting phases with different sticking probabilities. | Model-discrimination challenge, not ground truth for a fractional Polanyi–Wigner law. |
| O₂/Ag(111), Günther et al. (2014), DOI [10.1038/ncomms4853](https://doi.org/10.1038/ncomms4853) | Simultaneous LEEM/TPD; supplementary movies include TPD and LEEM-derived coverage; island-perimeter desorption model. | Mechanistic stress case; morphology/history produces non-mean-field kinetics, so a single fitted n is only descriptive. |

| O₂/Ag(111), Günther et al. (2014), DOI [10.1038/ncomms4853](https://doi.org/10.1038/ncomms4853) | Coupled LEEM/TPD directly measures coverage/island perimeter; published morphology model includes a half-order small-island term. | Mechanistic challenge, not a single-state control. Prioritize supplementary arrays and reproduce morphology model before using a fitted effective order as a misspecification diagnostic. See [candidate record](fractional_o2_ag111/README.md). |

## Strengths shown by the tests

1. **Transparent assumptions and provenance.** Current records generally
   preserve source, preprocessing, selected interval, unit conversions, ramp,
   code/input hashes and limitations. This makes negative results reviewable.
2. **Useful candidate-order discrimination.** The O₂/Pt(111) series shows a
   consistent second-versus-first order ranking on all 14 selected traces.
3. **Sensitivity is visible rather than hidden.** Ethanol/Au and Ar/CO expose
   how baseline and prefactor choices shift estimates; the software records
   bounds, residual warnings and identifiability diagnostics.
4. **More than ideal single peaks are represented.** Methyl acetate, PTCDA and
   pure-ice cases stress overlap, shoulders, heterogeneous states, broad tails,
   and uncertain source-curve interpretation.
5. **Negative cases are retained.** Bound-hitting, structured-residual and
   incompatible-reference outcomes are documented rather than tuned away.

## Weak points and failure modes

1. **Model mismatch dominates optimizer quality.** The main rate fitter assumes
   one initially populated state, linear ramp, a Polanyi–Wigner law with one
   energy and prefactor, signal proportional to rate, and at most a constant
   baseline. Coverage-dependent barriers, energy distributions, phase changes,
   islanding, multilayer/nonzero fractional orders and multiple site families
   violate that model.
2. **Energy and prefactor are strongly correlated.** Free scale and normalized
   initial coverage create further ambiguity. A good curve fit may not yield
   unique physical parameters; identical or compensating kinetic curves can
   produce different E and ν.
3. **Background and objective choices materially affect estimates.** A free
   constant offset is not a substitute for sloped background or instrument
   response. Log fitting discards nonpositive points and changes the error
   model; signal-space least squares gives high-signal points more influence.
4. **Peak overlap and automated state count remain weak.** Manual component
   inputs are possible, but a shoulder, a broad asymmetric peak or a low AICc
   does not establish a number of physical states. Weak components are poorly
   identifiable and standard information criteria can mislead in singular
   mixture models.
5. **Digitized curves are not raw instrument data.** Pixel resolution,
   line thickness, trace overlap, axis calibration, scan conversion and missing
   pixels create correlated uncertainty. Treating every digitized pixel as an
   independent observation makes conventional standard errors too small.
6. **Metadata mismatch blocks some comparisons.** Ramp linearity, temperature
   calibration, pumping/re-adsorption, detector sensitivity, coverage and
   absolute signal calibration are often not published. Source-derived
   exposure in L is not measured initial coverage.
7. **Experimental order classes are not a finite checklist.** Fractional
   order can be empirical, coverage-dependent, phase-dependent or an effective
   signature of island geometry/sticking coexistence. “Test every order” is
   meaningful as a software-generated range of synthetic cases, but experimental
   studies need to be grouped by physical model and observable assumptions.

## Algorithm options from the literature

| Method | What it could add | Main risks | Recommendation |
|---|---|---|---|
| **Variable projection / separable nonlinear least squares** | For each trial E, ν and n, solve detector scale and baseline/drift coefficients analytically (linear least squares or bounded NNLS), leaving only kinetic parameters for nonlinear optimization. Reduces nuisance dimensions and improves conditioning. | Baseline terms can absorb real low-temperature tails; profiled objective still may be multimodal. | **Implement first.** Low-risk optimizer improvement within existing physical model. Compare against current method on reference and empirical traces. |
| **Profile likelihood and bootstrap/model uncertainty** | Profile E against log ν, n and baseline; retain near-optimal parameter ridges. Bootstrap residual blocks or digitization perturbations to estimate sensitivity. | IID bootstrap falsely narrows intervals when residuals/autocorrelation or digitization dominate. | **Implement alongside variable projection.** Label conditional uncertainty and use block/parametric variants only when assumptions are justified. |
| **Energy/site distribution inversion with second-derivative regularization** | Reconstruct nonnegative adsorption-energy distribution instead of forcing one E. Barrie recommends a curvature penalty selected with an L-curve for noisy first-order site-distribution problems. | Ill-posed; resolution limited; order/site assumptions required; regularization can erase narrow populations or invent smooth structure. | **Best scientific extension after baseline model.** Separate experimental mode, report resolution and regularization sensitivity; do not call peaks unique sites. |
| **Richardson–Lucy energy-distribution recovery** | Iteratively estimates nonnegative energy distributions; Schmid et al. apply it to TPD under equilibrium-thermodynamic transforms and discuss finite resolution. | Needs the right forward kernel and count/noise model. The cited transform is approximate and assumptions differ from generic Polanyi–Wigner rate fitting. | **Prototype as a separate method with synthetic resolution tests**, not a drop-in replacement for current fitter. |
| **Global multi-trace fitting across coverage and heating rates** | Share physically justified E/order across traces, allow trace-specific signal scales/backgrounds, and test coverage/rate effects explicitly. Reduces per-trace ambiguity and makes consistency testable. | Wrong shared-parameter assumptions create overconfident bias; absolute coverage and ramp metadata may be unknown. | **High priority for the experimental workflow.** Make shared/free parameters explicit and compare constant-energy vs coverage-dependent models. |
| **Robust loss / correlated-error models** | Huber/Student-t losses reduce sensitivity to isolated artifacts; AR/response models account for correlated detector noise and pumping/thermal lag. | Robust losses can conceal real peak features; response parameters need calibration or multi-rate evidence. | Sensitivity options only; retain ordinary least squares as reference and diagnose residual autocorrelation. |
| **Kinetic Monte Carlo + evolution strategies** | Can represent lateral interactions, island formation and mechanisms beyond mean-field; Jansen demonstrates fitting dynamic MC TPD simulations with evolution strategies for CO/Rh(100). | Expensive, mechanism-specific, parameter-rich; identifiability and computational cost rise rapidly. | **Research-grade extension, not the next product feature.** Only use after a specific mechanistic dataset and collaborators justify the model. |
| **Automatic peak finding / model selection** | Propose candidate components using smoothed derivatives, change points or reversible-jump/Bayesian model comparison. | Overfitting and unstable component counts; smoothing changes shoulders; mixture models have singular likelihoods. | Start with **candidate generation plus user review**, not unattended automatic physical assignments. Use residual structure and minimum separation/area checks. |

Key primary method references: Barrie, PCCP 10, 1688 (2008),
[10.1039/B717430F](https://doi.org/10.1039/B717430F); Schmid, Parkinson &
Diebold, ACS Phys. Chem. Au 3, 44–62 (2023),
[10.1021/acsphyschemau.2c00031](https://doi.org/10.1021/acsphyschemau.2c00031);
Jansen, Phys. Rev. B 69, 035414 (2004),
[10.1103/PhysRevB.69.035414](https://doi.org/10.1103/PhysRevB.69.035414); Xu &
Deng, ACS Omega 5, 4148–4157 (2020),
[10.1021/acsomega.9b03867](https://doi.org/10.1021/acsomega.9b03867). These
methods solve different inverse problems and should not be combined into one
“automatic fit” button without model selection, identifiability and provenance
controls.

### Initial variable-projection comparison

A research prototype is available in `tpd_spectra/variable_projection.py`.
It profiles a nonnegative signal scale and bounded constant offset at each
kinetic proposal, reducing the nonlinear parameter vector from four to two
for fixed order (E and log ν). The implementation includes peak-informed
initial seeds because a poor E–ν start can leave the simulated peak outside
the measured window and produce a flat objective.

On the existing digitized ethanol/Au(111) primary-window trace (195 samples,
first-order model, 0.15 K/s), current and profiled fits agree to numerical
precision: E differs by 2.1×10⁻⁷ eV, prefactor by 1.8×10⁻⁵ relative, and NRMSE
by 2.7×10⁻¹⁴. On this runtime the current fitter took 0.82 s and the prototype
2.47 s; these timings are environment-specific and the prototype pays for a
larger deterministic seed grid. The current fit's Jacobian condition number
was 1.06×10⁴, but the prototype does not yet provide a comparable full
identifiability covariance diagnostic. This is numerical equivalence on one
existing digitized trace, not new independent experimental validation, and
shows no accuracy or speed gain yet. Reproduce with
`python scripts/experimental_variable_projection_check.py`; saved metrics are
in `ethanol_2024/variable_projection_comparison.json`.

The prototype is intentionally not wired into the GUI or default fitting path.
Its default profiles a constant offset; the optional linear baseline is
research-only. Detector response remains outside this model.

The six-start ethanol comparison found all six current-fitter runs converged
to effectively the same solution; the profiled version also converged to the
same solution from every start but took 2.9–4.9 s per run versus 0.8–1.4 s for
the current fitter. A second optimizer-only check on the D₂O/Fe₃O₄(111)
digitization produced the same fit from both implementations, but both hit the
prefactor lower bound and retained NRMSE 0.106. That trace is a known
multi-population challenge and is not a kinetic validation success. These two
comparisons argue against replacing the default fitter with variable
projection at this stage.

A separate energy–prefactor profile has now been computed for the ethanol/Au
trace. The best grid point is E = 0.655 eV, log₁₀ν = 22.17; the energy and
prefactor move together along a shallow objective valley. An arbitrary 1% RSS
description spans 0.640–0.673 eV on the chosen grid. This is **not** a
confidence interval: pointwise variances are uncalibrated and digitization
errors are correlated. The profile is a useful diagnostic of parameter
tradeoff, not a statistical uncertainty claim. Files:
`ethanol_2024/energy_prefactor_profile.csv`,
`ethanol_2024/energy_prefactor_profile_summary.json`, and the profile plot.

The profile routine recovered exact synthetic parameters for fixed n = 1.23
and n = 2 traces with known E, ν, scale and constant baseline. A separate
synthetic drift challenge showed that omitting a sloped background equal to
4.3% of the signal range shifted E by 0.01 eV and raised NRMSE to 0.0117.
Extending the research fitter to profile a linear baseline recovered that
synthetic generating curve to numerical precision. This supports adding a
linear background as an explicit sensitivity option for later experimental
checks; it does not show that a sloped background is physically correct or
that the experimental energy estimate improves. A sloped baseline can absorb
real tails and must be constrained to predeclared fit windows and reviewed
against residuals.

On the existing ethanol/Au trace, the sloped-baseline variant changed the
best-fit energy from 0.65603 to 0.65563 eV and lowered NRMSE from 0.03123 to
0.03070 (about a 1.7% relative reduction). The fitted slope is small and the
energy shift is also small. This is one trace-derived sensitivity result; a
slightly lower residual does not identify the true detector background.
Reproduce with `python scripts/experimental_baseline_degree_check.py` and see
`ethanol_2024/baseline_degree_comparison.json`.

The 2-propanol/HOPG source is more nuanced than a single “fractional-order”
label: it reports n = 1.23 ± 0.03 for the monolayer, approximately zero-order
amorphous multilayer desorption, and a separate crystalline multilayer energy.
Fig. 2A's 1, 2, 5 and 10 Lm monolayer traces are now digitized. The declared
137–145 K reconstruction gives 1.14 ± 0.05; the source does not state its
fixed-temperature interval, and a ±1-pixel zero-line shift gives 1.111–1.165.
Separate full-trace fits favor fixed n = 1.23 over n = 1 by NRMSE on all four
traces, while free order reaches its upper bound on three. These are distinct
estimators and a bounded figure-derived challenge, not raw-data or energy
validation. Full provenance and outputs are in `fractional_2propanol_hopg/`.

Another high-value source is ethanol/HOPG. Burke et al. report a 0.98 ± 0.13
monolayer order, 1.52 ± 0.21 bilayer order, and 0.08 ± 0.07 multilayer order;
the series also contains a crystalline shoulder and overlapping peaks. The
reported multilayer energy is 56.3 ± 1.7 kJ/mol. Its heating ramp is
0.50 ± 0.01 K/s. Fig. 5 is a useful mixed-order challenge, but the available
copy has unresolved copyright terms and the image endpoint is currently
inaccessible. No digitization or fit has been performed; see
`fractional_ethanol_hopg_2008/README.md`.

## Recommended work order

1. **Extend fractional-order comparison to an independent source.** The
   figure-derived 2-propanol/HOPG challenge is complete at its bounded scope.
   Next assess ethanol/HOPG only after resolving reuse rights; methanol/HOPG
   remains blocked by scan quality and its 200/300 L label conflict. Keep the
   source's coverage-slope estimator distinct from whole-trace fits.
2. **Treat ethanol/HOPG as a high-value, rights-limited stress candidate.** Its
   same study spans near-first, greater-than-first and near-zero/fractional
   orders with overlap and crystallization. Proceed to digitization only after
   confirming lawful reuse of the graph data or obtaining authorized pixels.
3. **Keep variable projection as a research diagnostic, not the default.** It
   did not improve convergence on tested starts and was slower. Retain the code
   for controlled comparisons, and do not invest in GUI integration unless a
   later case shows a measurable benefit.
4. **Extend profile diagnostic validation to noisy/correlated synthetic traces
   and parameter-bound cases.** Report conditional objective landscapes until
   uncertainty calibration accounts for correlated digitization and model
   mismatch.
5. **Prototype energy-distribution inversion separately** on synthetic known
   distributions plus at least one multi-rate experimental source. Include
   resolution limits, nonnegativity and regularization sensitivity.
6. **Do not implement broad automatic decomposition yet.** First quantify
   false component detection on single broad peaks, shoulders, noise, baseline
   drift and true known overlaps. Keep humans in the loop until that benchmark
   shows reliable component-count calibration.

This sequencing prioritizes usable experimental evidence over further code
labels. The 2-propanol figure-derived challenge is recorded, but clean
independent scientific review and additional trace sets remain useful next
steps. Variable projection currently offers no demonstrated improvement,
while baseline and profile diagnostics remain research tools until broader
validation.
