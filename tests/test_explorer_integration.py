"""Independent numerical references and regressions for Explorer integration."""
from pathlib import Path
from types import SimpleNamespace
import json
import tkinter as tk

import numpy as np
import pytest
from scipy.integrate import quad

from tpd_spectra.analysis import load_spectrum
from tpd_spectra.kinetics import simulate_tpd, _fit_information_criteria
from tpd_spectra.kinetics_explorer import ModelCandidate
from tpd_spectra.kinetics_uncertainty import run_kinetics_monte_carlo
from tpd_spectra.explorer_export import export_explorer_bundle

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("order", [0., .5, 1., 1.5, 2., 2.5])
@pytest.mark.parametrize("beta", [.2, 1., 5.])
def test_all_orders_against_separable_analytic_coverage(order, beta):
    # Independent quadrature and closed-form coverage, no app forward solver.
    t = np.linspace(80., 360., 141)
    energy, nu, theta0, kb = .9, 1e10, .8, 8.617333262145e-5
    coverage, rate = simulate_tpd(t, beta, energy, nu, order, theta0)
    expected = []
    for temp in t:
        integral, _ = quad(lambda kelvin: nu / beta * np.exp(-energy / (kb * kelvin)),
                           t[0] + 273.15, temp + 273.15, epsabs=1e-11, epsrel=1e-11)
        if order == 1:
            theta = theta0 * np.exp(-integral)
        else:
            base = theta0 ** (1 - order) - (1 - order) * integral
            theta = max(base, 0.) ** (1 / (1 - order))
        expected.append(theta)
    # Absolute coverage tolerance 2e-6 (normalized population), specified before execution.
    np.testing.assert_allclose(coverage, expected, rtol=0, atol=2e-6)
    assert np.all(np.isfinite(rate)) and np.all(rate >= 0)


def test_information_criteria_count_estimated_noise_variance():
    # Direct Gaussian MLE likelihood including its constants, then remove those constants.
    n, mean_parameters, rss = 40, 4, 2.5
    k = mean_parameters + 1
    minus2loglike = n * (np.log(2 * np.pi) + 1 + np.log(rss / n))
    common = n * (np.log(2 * np.pi) + 1)
    expected_aic = minus2loglike + 2 * k - common
    aic, aicc, bic = _fit_information_criteria(rss, n, mean_parameters)
    assert aic == pytest.approx(expected_aic)
    assert aicc == pytest.approx(expected_aic + 2 * k * (k + 1) / (n - k - 1))
    assert bic == pytest.approx(minus2loglike + k * np.log(n) - common)


@pytest.mark.parametrize("file", sorted((ROOT / "examples/kinetics_orders").glob("*.csv")))
def test_every_explorer_example_imports_without_temperature_corrections(file):
    spec = load_spectrum(file)
    assert spec.signal.size == 281
    assert spec.points_temperature_corrected == 0
    assert np.ptp(spec.temperature_clean_c) / (spec.time_min[-1] * 60) == pytest.approx(1.)


def test_mc_withholds_incomplete_rankings_and_sparse_ranges(monkeypatch):
    from tpd_spectra import kinetics_uncertainty as module
    t, y = np.arange(20.) + 100, np.arange(20.) * .1
    fit = SimpleNamespace(activation_energy_eV=1., prefactor_s_inv=1e13, reaction_order=1., aicc=0.)
    good = ModelCandidate("first", fit, y + .05, None)
    bad = ModelCandidate("second", None, None, "did not converge")
    monkeypatch.setattr(module, "compare_desorption_orders", lambda *a, **kw: [good, bad])
    result = run_kinetics_monte_carlo(t, y, 1., orders=("first", "second"), replicates=3,
                                     reference_comparison=[good, bad])
    assert result.failed_rankings == 3
    assert sum(result.winning_counts.values()) == 0
    assert result.parameter_intervals == {"first": {}, "second": {}}
    assert result.successful_parameter_fits == {"first": 3, "second": 0}
    assert len(result.replicate_records) == 6
    assert result.replicate_records[1]["error"] == "did not converge"


def test_export_never_overwrites_and_invalid_input_creates_no_folder(tmp_path):
    t = np.arange(20.) + 100
    y = np.arange(20.)
    candidate = ModelCandidate("first", None, y.copy(), None)
    with pytest.raises(FileExistsError):
        export_explorer_bundle(tmp_path, t, y, [candidate], beta_k_s=1.)
    with pytest.raises(ValueError):
        export_explorer_bundle(tmp_path / "invalid", t, y, [candidate], beta_k_s=float('nan'))
    assert list(tmp_path.iterdir()) == []


def test_explorer_export_uses_fitted_snapshot_when_controls_change(root, tmp_path, monkeypatch):
    from tpd_spectra import explorer_gui as module
    path = ROOT / "examples/synthetic_two_peak_demo.csv"
    window = module.KineticsExplorerWindow(root, {"demo": {"path": path, "spec": load_spectrum(path)}})
    t, y = np.arange(20.) + 100, np.arange(20.)
    window.snapshot = dict(beta_k_s=1., fit_baseline=True, orders=("first",), source="original.csv")
    window.last_fit = (t, y, [ModelCandidate("first", None, y.copy(), None)])
    window.beta.set("99")
    assert window.stale
    monkeypatch.setattr(module.filedialog, "askdirectory", lambda **kw: str(tmp_path))
    window.export_results()
    manifest = json.loads(next(tmp_path.rglob("explorer_analysis.json")).read_text())
    assert manifest["heating_rate_k_s"] == 1.
    assert manifest["source"] == "original.csv"
    window.close()


def test_explorer_can_close_and_reopen_without_orphan_callbacks(root):
    from tpd_spectra.explorer_gui import KineticsExplorerWindow
    root.tk.eval('set callback_errors {}; proc bgerror {message} {lappend ::callback_errors $message}')
    path = ROOT / "examples/synthetic_two_peak_demo.csv"
    spectra = {"demo": {"path": path, "spec": load_spectrum(path)}}
    for _ in range(2):
        window = KineticsExplorerWindow(root, spectra)
        root.update()
        window.canvas.draw_idle()
        window.close()
        done = tk.BooleanVar(root, value=False)
        root.after(150, lambda: done.set(True))
        root.wait_variable(done)
        assert not window.win.winfo_exists()
    assert not root.tk.call("set", "callback_errors")
