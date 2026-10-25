# Research tools preserved during consolidation

These optional developer tools were developed in PR #2 and now live alongside
the application. They do not run automatically from the GUI, produce no published
validation claim by themselves, and do not replace independent reference data.
Install the package in a virtual environment (`python -m pip install -e .`) and
run these commands from the repository root:

```text
python -m scripts.kinetic_recovery_benchmark --output output/recovery
python -m scripts.export_benchmark_matrix --output output/matrix
python -m scripts.leading_edge_interval_coverage --output output/leading-edge-coverage
python -m scripts.nonlinear_bootstrap_coverage --output output/bootstrap-coverage
```

- Recovery/matrix scripts use the application's own forward simulator. They
  measure internal recovery, convergence and failures; they are not independent
  experimental validation. Zero-order prefactor-error scores are withheld because
  that parameter is not unique; its conditional sampling bracket is exported.
- Leading-edge coverage assumes independent Gaussian errors in log(signal) and
  a predeclared temperature window. It excludes calibration, drift and model error.
- Nonlinear coverage reports how often the optional bootstrap issues or withholds
  intervals, and conditional coverage among issued intervals. Withholding must not
  be hidden when interpreting coverage. Default runs can be computationally expensive.
- The [experimental bootstrap API](NONLINEAR_BOOTSTRAP_UNCERTAINTY.md) retains its
  separate 20-refit research floor. Explorer's default 100-success rule is unchanged.
  Neither threshold establishes frequentist coverage. Refits with diagnostic
  warnings are excluded, and this API rejects zero order.

The independent dense-quadrature zero-order regressions and existing Explorer
references remain in the application test suite. They are distinct from these
same-simulator research experiments. See [METHOD_STATUS.md](METHOD_STATUS.md)
for current scientific scope and [the literature catalog](../validation/README.md)
for external-validation candidates; no catalog figure has been digitized here.
