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
date: 28 October 2026
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
