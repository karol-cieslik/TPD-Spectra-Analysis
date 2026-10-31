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
prefactor. Th