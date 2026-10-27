# Results presentation: beta review checklist

The Kinetic Analysis results panel contains three views of the **same stored
result**. The layout does not change the underlying fitter, fit settings,
kinetic assumptions or serialization.

## Colleague journey

1. In **Spectra & Preparation**, open an example and select a named interval.
2. In **Modeling & Order Identification**, simulate, compare orders or run
   Monte Carlo. These exploratory results remain in Modeling.
3. In **Kinetic Analysis**, select the method and calculate/fit the peak.
4. Open **Spectrum & residuals** to inspect the observed trace, model and
   residual where the selected method supplies a fitted curve.
5. Open **Parameter summary** to read each reported parameter, its units and
   how it was obtained. Use **Copy parameter summary** for a textual record.
6. Open **Assumptions & provenance** before reporting a value. The submitted
   spectrum, peak, processing, method settings, warnings and identifiability
   diagnostics remain available.

## Meaning of roles

| Role | Scientific meaning |
| --- | --- |
| Fitted | Optimized by the selected fit, subject to its assumptions. |
| Assumed input / Fixed assumption | Entered or fixed, not inferred from the spectrum. |
| Regression estimate | Based on the selected leading-edge regression only. |
| Derived estimate | Computed from an approximation or the selected maximum; not a nonlinear fit. |
| Representative; not unique | Zero-order prefactor / scale representative of a conditional solution family. |
| Conditional / derived | Model- or regression-conditional quantity, not automatically a general confidence interval. |
| Diagnostic | Fit, regression, convergence or model-comparison statistic. |
| Not identified | Quantity cannot be inferred by this method. |

## Scientific boundaries

- **Leading edge:** apparent activation energy, not an order assignment;
  regression-only interval and **no identified absolute prefactor**.
- **Redhead:** first-order approximation with explicitly assumed prefactor
  and heating rate. No fabricated confidence interval.
- **Single-state Polanyi–Wigner:** fitted energy and prefactor may correlate;
  normalized coverage, constant heating and signal calibration remain assumptions.
  An optimized order is not proof of a microscopic desorption mechanism.
- **Zero order:** display prefactor and signal scale as representative and not
  unique. Conditional ranges must not be relabeled as confidence intervals.
- **Multicomponent fit:** remains in Modeling; never insert its fixed-
  assumptions component parameters into a single-state Kinetic Analysis record.
- **Stale results:** show *STALE* prominently and preserve the originally
  submitted settings. Do not auto-recompute on changing inputs.

## Acceptance checkpoints

- [ ] Redhead, leading edge, single-state PW, fixed zero-order and fitted-order
      PW each populate a meaningful parameter table.
- [ ] The plot remains legible when the long parameter and warning text grow.
- [ ] Every row has name, value, unit (when meaningful), and role.
- [ ] The full original warnings and submitted settings are visible and copied.
- [ ] A current result becomes explicitly stale after changing its inputs.
- [ ] No selected peak and a cancelled/failed fit retain correct empty or
      last-successful state; results from one peak never leak into another.
- [ ] Existing project save/reopen and modeling comparison/MC still work.
- [ ] Keyboard access, window resizing, Windows DPI, 100%/133%/200% scaling
      and clipboard are verified on a Windows 10/11 beta package.
- [ ] Independent scientific beta review of representative experimental data.

The automated test suite covers the classification, staleness and basic Tk
controls. Human Windows acceptance and scientific validation remain necessary
before declaring this feature production-ready.
