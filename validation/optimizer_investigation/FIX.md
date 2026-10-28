# Peak-informed initialization correction

The fitter retains the supplied kinetic seed and compares it with an observed-
peak-informed energy seed at the supplied prefactor. Linear detector amplitude
and optional baseline are profiled for initialization; the lower-residual seed
starts the existing bounded nonlinear fit. Final fitting still optimizes all
original parameters with the same model, bounds and diagnostics. Fixed zero
order follows its unchanged separate depletion-profile path.

The peak-energy expression is a numerical first-order-inspired seed for all
positive-order candidates, not an inferred physical order. It does not add a
known synthetic truth to the starts. No global optimum or unique mechanism is
guaranteed. Parameter count and final Jacobian retain the original parameterization.

The reproduced first-order case now yields E=1.09463537 eV and normalized
RMSE=0.01273470 with default multistart, versus 1.46473914 eV and 0.26430331
before correction. Three independent noisy first/second/fractional-order recovery
regressions passed. Existing targeted kinetics/Explorer/zero-order tests: 63
passed, 2 display-dependent skips. Full suite evidence is recorded separately.

Historical MC and ranking records predate this solver initialization change.
They are retained as historical evidence, not silently attributed to the corrected
algorithm. Reassessment is needed before publication claims about its uncertainty
or order-ranking behavior. Windows CI and human desktop acceptance remain separate.

Full corrected headless suite: 328 passed, 38 display-dependent skips, 53.98 seconds. No failures. See optimizer_fix_full_tests.xml in validation/.
