---
title: 'TPD Spectra Studio: Reproducible analysis of temperature-programmed desorption spectra'
tags:
  - Python
  - surface science
  - temperature-programmed desorption
authors:
  - name: Karol Cieślik
    affiliation: 1
affiliations:
  - name: 'AUTHOR CONFIRMATION REQUIRED: affiliation'
    index: 1
date: 31 October 2026
bibliography: paper.bib
---

# Summary

Temperature-programmed desorption measures the release of adsorbed material as
a sample is heated. Researchers use the resulting signals to investigate
surface binding and desorption behavior. Extracted quantities depend on the
physical model, temperature program and analysis choices. TPD Spectra Studio
is an open-source Python desktop application and analysis toolkit that brings
data preparation, apparent-energy estimates, numerical kinetic fitting and
traceable reporting into a connected workflow. It exposes graphical,
command-line and Python interfaces. The software emphasizes inspectable
assumptions, diagnostic warnings and retention of the settings used to obtain
a result. It supports model-dependent interpretation rather than automatic
identification of a physical desorption mechanism.

# Statement of need

A reproducible TPD analysis requires more than a fitted curve. Temperature and
time units, heating-rate estimates, baseline treatment, fit windows, fixed
prefactors and the assumed kinetic law affect interpretation. Classical
peak-temperature estimates and full-spectrum inverse fits answer related but
different questions. The Redhead approximation, for example, provides an
apparent desorption energy under specified kinetic assumptions [@redhead1962].
More general treatments also illustrate the importance of prefactors, entropy
and the physical description of the adsorbed layer [@schmid2023].

The intended users are surface-science researchers who need to compare spectra
and analysis hypotheses while retaining a record of their choices. TPD Spectra
Studio organizes selected peaks, method settings, computed results and exported
records in one workspace. It distinguishes fixed assumptions from fitted or
derived quantities and marks results stale when their input context changes.
The contribution is software organization and implementation of an inspectable
analysis workflow; no new desorption theory is claimed.

# State of the field

Existing tools address different scientific descriptions and workflows.
The TPD Calculator associated with Schmid and colleagues implements a
lattice-gas thermodynamic approach, including analysis of adsorption-energy
distributions [@schmid2023; @schmidcalculator]. The Python package tpd-analyse
documents first-order analysis of adsorption energies, configurational entropy
and adsorbate interactions [@tpdanalyse]. TDS Simulator addresses hydrogen
transport and trapping with Oriani and McNabb–Foster models [@tdssimulator].
These are relevant alternatives, but their physical models should not be
treated as interchangeable with independent-population surface-desorption fits.

The proposed rationale for a separate application is a shared workflow for
classical estimates, exploratory Polanyi–Wigner order comparisons, constrained
component fitting and provenance-aware desktop reporting. It builds on NumPy,
pandas, SciPy and Matplotlib rather than replacing numerical or plotting
infrastructure. This is a targeted design rationale, not an assertion that
other tools lack equivalent features. Before submission, the author must
confirm this rationale against direct experience and the completed comparison
in the repository; no speed or accuracy advantage is currently claimed.

# Software design

Computational modules are separated from graphical controllers. The desktop
workflow connects spectrum preparation, modeling and kinetic analysis while
retaining dataset and peak context. Analysis snapshots preserve the settings
submitted to a calculation; subsequent interface edits do not relabel an old
result as a new calculation. Saved projects and machine-readable exports
support inspection and repetition of an analysis.

The kinetic model integrates normalized population depletion under an assumed
constant heating rate. Single-state fitting may estimate energy, prefactor
and detector scale, with optional baseline and reaction order. Constrained
simultaneous-component fitting instead retains specified component orders,
prefactors and initial populations while fitting component energies and
signal scales. Explicit fixed parameters reduce the scope of the inverse
problem but must remain assumptions in scientific interpretation. Coincident
or exchangeable components can prevent unique parameter attribution.

Fixed zero-order analysis uses a depletion-edge profile procedure. Compatible
prefactor/scale combinations are retained as conditional brackets rather than
reported as a uniquely measured prefactor. Leading-edge output similarly does
not interpret an arbitrary-unit signal intercept as a calibrated physical
prefactor. The Results interface assigns parameter roles so that fitted,
assumed, derived and unavailable values remain distinguishable.

Parametric Monte Carlo generates iid Gaussian-noise realizations around a
fitted reference and refits the requested candidates. All candidates receive
the same realization within a replicate. Incomplete rankings and failed fits
are retained; sparse parameter ranges are withheld. Resulting percentiles
describe successful conditional refits. They are neither demonstrated
confidence coverage nor probabilities of physical mechanisms. Correlated noise,
calibration uncertainty and reference-model inadequacy are not resolved by
increasing the replicate count.

For positive-order candidates, these optional refit ranges cover the free
parameters estimated in each replicate: energy, log-prefactor, signal scale,
optional fitted baseline and, for the free-order model, reaction order. Fixed
orders are assumptions rather than estimated values; zero-order prefactor and
scale ranges are withheld because the pair is non-unique under normalized
coverage. Standard single-state, two-state and global fit reports do not
provide parameter intervals. Simultaneous component fits use a separate
conditional local-linear approximation for fitted energies and signal scales,
which can be withheld by identifiability and residual checks. No interval
method is experimentally coverage-validated or propagated across every model
and source of uncertainty.

The Python importer now accepts explicit source time and temperature units,
retaining the historical millisecond/Celsius defaults for existing callers.
The command-line kinetic workflow measures discrepancy between observed
temperatures and its reconstructed linear coordinate. A configurable mismatch
screen can reject the kinetic calculation; its threshold is an engineering
check, not evidence of instrument calibration or physical model adequacy.

# Research impact statement

The repository supplies synthetic examples, independent quadrature references,
regression tests, automated packaging checks and documented research workflows.
The bounded numerical assessment evaluates six kinetic orders at three heating
rates and two sampling densities. Detailed conditions, tolerances and results
are retained with the software rather than substituted for experimental evidence.

An external input example uses measured time, temperature and calibrated D2
signal from the openly deposited AgY-zeolite dataset [@beckerdata2026]. The
sampled maximum is 92.06 K, compared with the related article's approximate
92 K description [@beckerarticle2026]. Explicit source-unit conversion preserves
the numerical trace. The full trace fails the default ramp-mismatch screen,
and no kinetic-energy fit is forced. This demonstrates a limited experimental
input/peak check and a negative screening example; it does not validate
desorption energies or constitute outside adoption of this software.

A further assessment uses deposited pure-Ar and CO spectra associated with
published zero-order leading-edge estimates [@kruczkiewicz2024]. Full-peak
fits reach an energy bound with substantial residuals. Subsequent figure
extraction closely matches the deposited Ar curve but reveals an unresolved
CO source-to-figure discrepancy. Deposited-CO fit results therefore cannot yet
constitute a trace-matched reproduction of the published analysis. Experimental
energy accuracy is not established by those cases.

Figure-derived assessments further distinguish conditional agreement from
parameter recovery. For ethanol on gold [@perrero2024], fixing the literature
prefactor gives 6435 K versus a dominant reported population at 6450 K;
optimizing the prefactor and baseline gives 7613 K with smaller residuals.
For multilayer methyl acetate [@fulker2024], the primary leading-edge estimate
is 42.22 kJ/mol versus 42.8 ± 0.7 kJ/mol, while baseline/window alternatives
give 37.81–40.29 kJ/mol. Extraction gaps, differing estimands and structured
whole-peak residuals preclude a general experimental-accuracy claim.
An additional pure-methyl-mercaptan figure assessment [@narayanan2025] gives
apparent leading-edge energies of 4849–5492 K across declared settings, compared
with the paper's TST-conditioned recommendation of 4610 ± 110 K. These are
different estimands; ideal whole-peak fits also retain structured residuals.

A coverage-series stress test analyzed 14 author-published O₂/Pt(111)
spectra [@miller2014]. Under the source's baseline and fitting window, fixed
second-order fits had lower AICc than fixed first-order fits for all 14 traces;
free-order estimates ranged from 2.35 to 2.73. Yet fixed-second-order
whole-window energies were 1.07–1.67 eV and lay below the same source's
leading-edge estimates (about 1.80–1.91 eV), with the whole-window values
falling overall as source exposure increased. This is order-discrimination and
model-challenge evidence: the paper describes coverage-dependent barriers,
whereas the Studio fit assumes one constant energy per trace. The source's
leading-edge estimates are not independent ground truth, and exposure in L is
not treated as calibrated surface coverage. The source workbooks are not
redistributed because no explicit reuse licence was identified; reproduction
requires a local checkout of the authors' supporting-information repository.
This result does not establish energy accuracy, mechanism identification or
general order-discrimination performance.

The 2-propanol/HOPG study by Ayling et al. [@ayling2017] is now a
figure-derived challenge based on the 1, 2, 5, and 10 L\(_m\) traces in
Fig. 2A. Reconstructing the source's log-intensity/log-integrated-area order
estimator over a declared 137–145 K window gives 1.14 ± 0.05 (descriptive
2 SEM across fixed-temperature slopes; the slopes and raster pixels are
correlated), compared with the paper's 1.23 ± 0.03. The source
does not report its fixed-temperature interval, and a ±1-pixel zero-line shift
changes the reconstruction to 1.113–1.166; the difference therefore remains
a method and digitization discrepancy rather than a contradiction. Separately,
the production single-trace fitter gives lower NRMSE for fixed order 1.23 than
for first order on each trace, while free-order fits reach the upper bound of
3.0 for three traces and return 2.393 for the fourth. The software fits each
normalized trace independently, so these fitted orders are not the same
quantity as the source's coverage-series slope. The result is a bounded
order/model-challenge example, not raw-data validation or energy validation.
The source reports coverage-dependent barriers and islanding; its high-dose
amorphous and crystalline multilayers remain outside this single-state
comparison. Figure pixels are retained with attribution under the source's
CC BY licence; author raw data were not available.

## Experimental comparison and interpretation

The literature cases are deliberately heterogeneous: they test numerical input
handling, isolated and mixed populations, nominal zero- and first-order
descriptions, leading-edge estimates, and failures of ideal full-peak models.
They are not a balanced sample of all adsorbate--surface systems, nor do the
authors' reported kinetic orders become independently known ground truth.

| Input and source | Model or comparison | Selected result | Interpretation and limit |
| --- | --- | --- | --- |
| D2 on AgY zeolite [@beckerdata2026; @beckerarticle2026] | Measured-temperature import and ramp screen | Sampled peak 92.06 K versus approximately 92 K in the article; full-trace ramp screen rejects | Input/peak check only; no kinetic energy is estimated |
| Pure Ar/CO in ice-related experiments [@kruczkiewicz2024] | Published zero-order leading edge versus ideal full-peak fits | Full-peak energies encounter a bound and substantial residuals | Ar source trace agrees with its figure; CO source-to-figure correspondence remains unresolved |
| Ethanol on Au, 0.7 ML [@perrero2024] | Assumed first-order single-state fit versus published dominant component | 6434.54 K with literature-fixed prefactor; 7612.90 K when prefactor and baseline are free, versus reported dominant 6450 K | Matched assumptions yield close correspondence; lower residuals with a free prefactor do not establish unique recovery of a multistate system |
| Multilayer methyl acetate on HOPG [@fulker2024] | Approximate leading edge versus published coverage-corrected analysis | 42.22 kJ/mol versus 42.8 ± 0.7 kJ/mol; alternative windows/baselines 37.81–40.29 kJ/mol | Figure gaps, different estimands and whole-peak mismatch prevent an experimental-accuracy claim |
| Pure methyl mercaptan ice [@narayanan2025] | Apparent leading edges and ideal zero-order full-peak fits versus TST-conditioned reference | 4849–5492 K leading edge and 2496–2717 K whole peak, versus 4610 ± 110 K | Distinct estimands, structured residuals and uncalibrated graphical input prevent physical parameter recovery |
| O₂/Pt(111) coverage series [@miller2014] | Fixed first- versus second-order fits on 14 author-published spectra; same-source leading-edge comparison | Fixed second order has lower AICc on all 14; free-order estimates 2.35–2.73; whole-window fixed-second-order energies are 1.07–1.67 eV and below source leading-edge estimates | Order-discrimination and model-challenge evidence only: constant-energy fits do not reproduce the paper's coverage-dependent barrier model; same-source estimates are not independent ground truth; source workbooks are not redistributed because no explicit reuse licence was identified |
| 2-propanol/HOPG Fig. 2A [@ayling2017] | Digitized 1, 2, 5 and 10 L\(_m\) traces; source-style fixed-temperature log-log slope and separate full-trace fits | Reconstructed order 1.14 ± 0.05 over 137–145 K versus reported 1.23 ± 0.03; fixed 1.23 gives lower NRMSE than fixed 1 on all traces; free order hits 3.0 on three | Figure-derived challenge only: source temperature interval is unspecified, ±1-pixel zero-line sensitivity is material, and the production fitter's per-trace normalized model does not estimate the source's coverage-series slope; not energy validation |

The source-specific protocols, transformation histories, fit settings, original
and corrected extraction versions, residuals and reuse restrictions are retained
under `validation/experimental/`. For 2-propanol, the source raster and
digitized traces are reproducible but remain figure-derived, correlated
observations; the unreported temperature interval in the source's order
estimator prevents an exact reconstruction claim. In particular, the fixed-prefactor ethanol
profile is an assessment harness, not a fixed-prefactor control in the present
production fitting API; methyl-acetate results from the superseded colour
selection are excluded. Figure-derived coordinates are correlated graphical
observations rather than original, independently sampled instrument records.
The PTCDA/Au(111) deposited series additionally contains 73 screened traces
and 438 conditional first-order fits; its sensitivity to baseline, starts and
bounds is supporting diagnostic evidence, **not** 438 independent experimental
validations or reproduction of a published zero-coverage energy.

## Discussion: what the comparisons establish

These cases separate **implementation agreement** from **physical model
adequacy**. Independent quadrature checks address whether the forward numerical
solver agrees with an independently calculated reference under specified
kinetics. Agreement with a literature energy after fixing a prefactor tests a
particular hypothesis conditional on its constraints. Neither establishes that
the inverse problem can identify reaction order, energy distributions,
prefactors or microscopic mechanisms from an arbitrary experimental trace.

The ethanol example exposes an energy--prefactor tradeoff: a fitted curve can
improve slightly while the inferred energy moves away from a literature
component estimate. Baseline and selected temperature window similarly shift
methyl-acetate and methyl-mercaptan leading-edge slopes. Consequently a small
energy difference, high regression R-squared or converged optimizer cannot
alone serve as a validation criterion. The published quantities also require
matching kinetic-order, coverage, prefactor and signal-calibration conventions
before a numerical difference has physical meaning.

The O₂/Pt(111) series adds a useful example of this distinction: the candidate
second-order law is consistently preferred to first order by AICc, while the
constant-energy whole-window model does not match the same source's
leading-edge estimates under its documented coverage-dependent barriers. The
ranking is conditional on the compared models and preprocessing; it does not
validate the fitted energies or establish a universal order classifier.

Whole-peak model failure is scientifically informative when retained. For the
pure Ar/CO and methyl-mercaptan cases, the idealized exhaustion shape misses
features of the observed traces. A broad trailing tail may be consistent with
several causes, including heterogeneous states, overlapping contributions or
instrument response; these datasets do not isolate which explanation applies.
Likewise a first-order multicomponent fit may give exchangeable assignments
when peaks coincide. A ranking among prescribed models is therefore a
conditional comparison of those models under their objective and preprocessing,
not a measured probability of a desorption mechanism or a universal method of
recovering fractional orders.

Parametric Monte Carlo quantifies sensitivity to *simulated iid Gaussian noise
about a chosen fitted reference*. Increasing refit counts does not correct an
incorrect reference model, temperature-program mismatch, image extraction
bias, correlated noise or missing identifiability. Such contributions should be
tested separately or reported as limitations. The present assessments support
an inspectable workflow that records these constraints; they do not establish
general experimental energy accuracy, reliable discrimination of all orders,
or demonstrated use by an independent research group.

**Submission evidence still required:** document completed use in an actual
research workflow, obtain independent scientific and clean-Windows acceptance,
and satisfy the public-development-history requirement. External adoption,
enabled publications and general experimental accuracy are not claimed in
this draft. This paragraph must be rewritten from completed evidence before
submission, not deleted to conceal the gaps.

![Independent numerical-reference errors (A) and the selected measured D2 trace (B). The numerical tolerance applies to normalized population, not experimental energy accuracy. The external trace is attributed to Becker and colleagues; see the dataset provenance record.](assessment_overview.png){#fig-assessment}

# AI usage disclosure

Generative AI assistance, including ChatGPT/Codex, was used in software work,
documentation, assessment scripts and drafting this manuscript. The complete
historical tool/model inventory and division of assistance must be confirmed
by the author. Automated checks and source records document part of the
verification; they do not replace human scientific review. **Author confirmation
pending:** record the actual tools/versions where known, assistance scope,
human review and validation, and responsibility for core design decisions.
No completed human-validation declaration is asserted here.

# Acknowledgements

Author confirmation required for funding, institutional support and individual
contributions. None has been inferred or invented for this draft.

# References
