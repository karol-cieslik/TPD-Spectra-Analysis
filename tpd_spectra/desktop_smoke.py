"""Packaged GUI/Explorer smoke exercised by Windows CI, not a validation study."""
import json
from pathlib import Path
import tkinter as tk

from .gui import TpdSpectraApp, QuickStartDialog
from .gui_review import ReviewDialog
from .explorer_gui import KineticsExplorerWindow
from .kinetics_explorer import compare_desorption_orders
from .kinetics_uncertainty import run_kinetics_monte_carlo
from .explorer_export import export_explorer_bundle
from .identity import build_identity
from .branding import set_windows_app_identity


def main(source, output):
    print("GUI smoke: creating Tk workspace", flush=True)
    set_windows_app_identity()
    root = tk.Tk()
    try:
        app = TpdSpectraApp(root)
        assert len(root._studio_icons) == 6
        assert app.brand_mark.width() == 64
        app._load_paths([Path(source)])
        root.update()
        assert len(app.spectra) == 1
        print("GUI smoke: imported demo; opening dialogs", flush=True)
        quick = QuickStartDialog(root)
        root.update()
        assert r"\n" not in quick.text.get("1.0", "end")
        quick.destroy()
        app.leading_low.set(110)
        app.leading_high.set(140)
        app.peak_low.set(150)
        app.peak_high.set(210)
        settings = app._settings([Path(source)], Path(output).parent)
        review = ReviewDialog(root, settings, list(app.spectra.values()), lambda *_: False)
        root.update()
        assert review.run_button.winfo_ismapped()
        review.destroy()
        explorer = KineticsExplorerWindow(root, app.spectra)
        root.update()
        assert explorer.run_button.winfo_ismapped()
        print("GUI smoke: dialogs opened; fitting first-order model", flush=True)
        spec = next(iter(app.spectra.values()))["spec"]
        mask = (spec.temperature_clean_c < 210)
        t, y = spec.temperature_clean_c[mask][::3], spec.signal[mask][::3]
        models = compare_desorption_orders(t, y, 1., orders=("first",),
                                          initial_energy_ev=1.25, initial_prefactor_s_inv=1e13,
                                          max_nfev=80, multistart=False)
        assert models[0].error is None
        print("GUI smoke: fit complete; short Monte Carlo", flush=True)
        mc = run_kinetics_monte_carlo(t, y, 1., orders=("first",), replicates=2,
                                      seed=42, max_nfev=40, reference_comparison=models)
        assert mc.replicates_completed == 2
        print("GUI smoke: Monte Carlo complete; exporting PNG/SVG and records", flush=True)
        destination = export_explorer_bundle(Path(output), t, y, models, beta_k_s=1., monte_carlo=mc,
                                             source=source, settings={"purpose": "packaging smoke; not uncertainty validation"})
        (destination / "desktop_smoke.json").write_text(json.dumps(build_identity()), encoding="utf-8")
        explorer.close()
        print("GUI smoke: all checks passed", flush=True)
        return 0
    finally:
        root.destroy()
