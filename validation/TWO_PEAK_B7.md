# Focused two-peak b7 candidate — 1 November 2026

Work starts from `main` at `77798d5790f434322e32616d00a47241d58a1538`
on `feat/two-peak-fitting-b7`. Existing checkouts and synced project references
are preserved. Version stays `0.11.0b7`; no tag, merge or release is part of this work.

## Reproduced failure and bounded numerical improvement

Input is the retained `examples/publication_data/zaki_2018_d2o_fe3o4.csv`,
644 accepted digitization points. The graphical maximum is −17.6506 °C.
The source catalog cites Zaki et al. (2018), DOI `10.1039/C8CP02333F`, 3 K/s.
The imported time coordinate is constructed from the nominal ramp, not measured.

With initial energies 1.25 and 1.55 eV, fixed first order, `nu=1e13 s^-1`,
coverage one and a fitted offset, the original narrow three-start search gives:

| Quantity | Original search | Temperature-informed multistart |
| --- | ---: | ---: |
| Normalized RMSE (RMSE / observed range) | 0.2612373 | 0.1257011 |
| Shared offset | 0.2116504 | 0.1197292 |
| Energy outputs (eV, supplied label order) | 1.21785, 3.25677 | 0.681924, 0.758592 |
| Peak component contributions | effectively zero | two non-negligible contributions |
| Starts attempted / converged | 3 / 3 | 12 / 12 |

The original result is a flat/baseline-dominated numerical failure despite
optimizer convergence. The new result is a stress-test improvement, not
experimental energy truth. Its strongly correlated residuals and exchangeable
labels withhold local intervals. Multiple populations, recombination, graphical
normalization and digitization limit interpretation; two independent first-order
populations are not validated by this comparison.

## User-facing and numerical checks

- Direct Fit 2 Peaks entry; two rows; real Matplotlib click dispatch; numeric
  positions; pending-edit validation; Advanced controls; repeated editor opening.
- Source-specific rate suggestion from metadata or exact bundled CSV bytes;
  same-name user files do not inherit it. Rejection retains settings; explicit
  acceptance updates Modeling only and is retained in projects/fit snapshots.
- Independent low-temperature PW quadrature recovers energies within 0.002 eV,
  scales within 2%, and normalized RMSE below 0.001 without manual energy guesses.
  Detector-unit scaling is also checked.
- Negative cases include invalid/nonphysical inputs, flat/linear-baseline data,
  bounds excluding the signal, coincident positions, poor residual fits and a
  good sum with one collapsed/unsupported component. Existing tests cover
  nonconvergence, cancellation, context switching, mixed orders, label ambiguity,
  count comparison, one-peak methods, persistence and exports.
- Failed optimization preserves previous results. A converged inadequate fit
  remains inspectable with explicit quality screening; it does not become a
  supported decomposition through optimizer success or AICc ranking alone.
- Python dependency consistency and CLI help/startup pass. Documentation links
  and packaged Help are included in the regression suite.

## Presentation and acceptance limits

All five regenerated Quick Start PDF pages were rendered with Poppler and
visually checked; the final page-1 candidate-build notice was checked again.
A clean two-peak exported plot was visually checked. Components use different
colors and dash patterns and render above the complete sum so neither is hidden.
Baseline and observation-minus-sum residuals remain separate.

Real Windows/Tk tests check editor scrolling, fixed footer visibility at
860×560, scaling 1.333 and 2.0, Help reachability, interaction and worker behavior.
Live screenshot capture was attempted but failed with `FrameArrived timed out`
and, after window refresh/activation, `window capture timed out`. This does not
establish visual acceptance of the live app, a frozen binary, or a clean-machine
installation. Those human checks remain outstanding for the exact built package.

The manual, workflow guide, Help catalog (including wheel fallback), in-app
Quick Start, Markdown/HTML worked examples, PDF generator/PDF, tester checklist,
method status and beta notes describe the same candidate behavior. Earlier main
artifacts sharing the b7 version do not contain these feature-branch changes.
