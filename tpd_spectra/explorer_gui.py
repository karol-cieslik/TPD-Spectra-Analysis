"""Interactive single-peak kinetic model comparison (experimental Phase 3 UI)."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .kinetics_explorer import compare_desorption_orders
from .kinetics_uncertainty import run_kinetics_monte_carlo
from .explorer_export import export_explorer_bundle


def select_peak_window(temperature, signal, start, end):
    """Validate selection and return a strictly increasing temperature slice."""
    t = np.asarray(temperature, dtype=float)
    y = np.asarray(signal, dtype=float)
    if t.ndim != 1 or y.shape != t.shape or not np.isfinite([start, end]).all() or start >= end:
        raise ValueError("Choose increasing, finite peak boundaries.")
    keep = np.isfinite(t) & np.isfinite(y) & (t >= start) & (t <= end)
    t, y = t[keep], y[keep]
    if t.size < 12:
        raise ValueError("Select at least 12 finite experimental points.")
    if np.any(np.diff(t) <= 0):
        raise ValueError("The selected temperature values must increase strictly.")
    if np.ptp(y) <= 0:
        raise ValueError("Selected signal has no measurable variation.")
    return t, y


class KineticsExplorerWindow:
    """Dedicated window; all Tk interactions stay on the main thread."""

    def __init__(self, parent, spectra):
        if not spectra:
            raise ValueError("Import spectra before opening the Explorer.")
        self.win = tk.Toplevel(parent)
        self.win.title("Desorption Kinetics Explorer — experimental")
        self.win.geometry("1110x760")
        self.spectra = spectra
        self.busy = False
        self.last_fit = None
        self.last_mc = None
        self.cancel_event = threading.Event()
        self.names = {str(k): v for k, v in spectra.items()}
        self.selected = tk.StringVar(value=next(iter(self.names)))
        self.beta = tk.StringVar(value="1.0")
        self.low = tk.StringVar()
        self.high = tk.StringVar()
        self.baseline = tk.BooleanVar(value=True)
        self.orders = {n: tk.BooleanVar(value=True) for n in ("zero", "first", "second", "fractional")}
        self.status = tk.StringVar(value="Select one peak using two clicks on the top plot.")
        bar = ttk.Frame(self.win, padding=8)
        bar.pack(fill="x")
        ttk.Label(bar, text="Spectrum").pack(side="left")
        ttk.Combobox(bar, values=list(self.names), textvariable=self.selected,
                     state="readonly", width=32).pack(side="left", padx=5)
        ttk.Button(bar, text="Load trace", command=self.draw_input).pack(side="left")
        ttk.Label(bar, text="β (K/s)").pack(side="left", padx=(12, 2))
        ttk.Entry(bar, textvariable=self.beta, width=7).pack(side="left")
        ttk.Checkbutton(bar, text="Fit constant baseline", variable=self.baseline).pack(side="left", padx=10)
        controls = ttk.Frame(self.win, padding=(8, 0, 8, 8))
        controls.pack(fill="x")
        for title, var in self.orders.items():
            ttk.Checkbutton(controls, text=title.capitalize(), variable=var).pack(side="left", padx=4)
        ttk.Label(controls, text="From °C").pack(side="left", padx=(12, 3))
        ttk.Entry(controls, textvariable=self.low, width=9).pack(side="left")
        ttk.Label(controls, text="To °C").pack(side="left", padx=(8, 3))
        ttk.Entry(controls, textvariable=self.high, width=9).pack(side="left")
        self.run_button = ttk.Button(controls, text="Compare models", command=self.run)
        self.run_button.pack(side="right")
        self.mc_button = ttk.Button(controls, text="Monte Carlo (500)", command=self.run_mc)
        self.mc_button.pack(side="right", padx=6)
        self.cancel_button = ttk.Button(controls, text="Cancel MC", command=self.cancel_event.set, state="disabled")
        self.cancel_button.pack(side="right")
        self.export_button = ttk.Button(controls, text="Export results", command=self.export_results)
        self.export_button.pack(side="right", padx=6)
        self.fig = Figure(figsize=(10, 6), dpi=95)
        self.raw_ax = self.fig.add_subplot(211)
        self.res_ax = self.fig.add_subplot(212)
        self.fig.tight_layout(pad=3)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.win)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.clicks = []
        self.table = ttk.Treeview(self.win, columns=("model", "order", "energy", "rmse", "delta", "warning"), show="headings", height=5)
        for name, width in (("model", 100), ("order", 75), ("energy", 90), ("rmse", 100), ("delta", 100), ("warning", 430)):
            self.table.heading(name, text=name.title())
            self.table.column(name, width=width)
        self.table.pack(fill="x", padx=8)
        ttk.Label(self.win, textvariable=self.status).pack(fill="x", padx=8, pady=5)
        self.draw_input()

    def draw_input(self):
        self.last_fit = None
        self.last_mc = None
        spec = self.names[self.selected.get()]["spec"]
        t = np.asarray(spec.temperature_clean_c, dtype=float)
        y = np.asarray(spec.signal, dtype=float)
        self.raw_ax.clear()
        self.res_ax.clear()
        self.raw_ax.plot(t, y, label="Experimental", color="#2563eb")
        self.raw_ax.set_ylabel("Detector signal")
        self.raw_ax.set_xlabel("Temperature (°C) — click start then end")
        self.res_ax.set_ylabel("Residual")
        self.res_ax.set_xlabel("Temperature (°C)")
        self.clicks.clear()
        self.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes != self.raw_ax or event.xdata is None or self.busy:
            return
        self.clicks.append(float(event.xdata))
        if len(self.clicks) == 2:
            lower, upper = sorted(self.clicks)
            self.low.set(f"{lower:.2f}")
            self.high.set(f"{upper:.2f}")
            self.clicks.clear()
            self.status.set(f"Peak interval selected: {lower:.2f}–{upper:.2f} °C")
            self.draw_input()
            self.raw_ax.axvspan(lower, upper, color="#93c5fd", alpha=0.25)
            self.canvas.draw_idle()

    def run(self):
        try:
            t, y = select_peak_window(
                self.names[self.selected.get()]["spec"].temperature_clean_c,
                self.names[self.selected.get()]["spec"].signal,
                float(self.low.get()), float(self.high.get()))
            beta = float(self.beta.get())
            if not np.isfinite(beta) or beta <= 0:
                raise ValueError("Heating rate must be positive.")
            orders = tuple(k for k, v in self.orders.items() if v.get())
            if not orders:
                raise ValueError("Select at least one kinetic order.")
        except (ValueError, KeyError) as exc:
            messagebox.showerror("Invalid kinetics selection", str(exc), parent=self.win)
            return
        self.busy = True
        self.run_button.configure(state="disabled")
        self.status.set("Fitting selected kinetic models…")
        fit_baseline = self.baseline.get()

        def worker():
            try:
                result = compare_desorption_orders(t, y, beta, orders=orders, fit_baseline=fit_baseline)
                self.win.after(0, lambda: self.show_result(t, y, result))
            except Exception as exc:
                message = str(exc)
                self.win.after(0, lambda: self.failure(message))
        threading.Thread(target=worker, daemon=True).start()

    def run_mc(self):
        if self.busy:
            return
        try:
            spec = self.names[self.selected.get()]["spec"]
            t, y = select_peak_window(spec.temperature_clean_c, spec.signal,
                                      float(self.low.get()), float(self.high.get()))
            beta = float(self.beta.get())
            if not np.isfinite(beta) or beta <= 0:
                raise ValueError("Heating rate must be positive.")
            orders = tuple(k for k, v in self.orders.items() if v.get())
            if not orders:
                raise ValueError("Select at least one model.")
        except (ValueError, KeyError) as exc:
            messagebox.showerror("Invalid Monte Carlo input", str(exc), parent=self.win)
            return
        self.cancel_event.clear()
        self.busy = True
        self.run_button.configure(state="disabled")
        self.mc_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status.set("Monte Carlo — starting 500 replicates")
        fit_baseline = self.baseline.get()

        def worker():
            try:
                def progress(done, total):
                    if done % 10 == 0 or done == total:
                        self.win.after(0, lambda d=done, n=total:
                                       self.status.set(f"Monte Carlo — {d}/{n}"))
                result = run_kinetics_monte_carlo(
                    t, y, beta, orders=orders, replicates=500, seed=42,
                    fit_baseline=fit_baseline, progress=progress,
                    cancelled=self.cancel_event.is_set)
                self.win.after(0, lambda: self.show_mc(result))
            except Exception as exc:
                message = str(exc)
                self.win.after(0, lambda: self.failure(message))
        threading.Thread(target=worker, daemon=True).start()

    def show_mc(self, result):
        self.last_mc = result
        self.busy = False
        self.run_button.configure(state="normal")
        self.mc_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        rows = [f"{name}: {wins}/{result.replicates_completed} wins"
                for name, wins in result.winning_counts.items()]
        messagebox.showinfo(
            "Monte Carlo results",
            f"Reference: {result.reference_model}; seed {result.seed}; "
            f"Gaussian sigma {result.noise_sigma:.3g}; "
            f"completed {result.replicates_completed}/{result.replicates_requested}; "
            f"no successful ranking {result.failed_rankings}.\\n"
            + "\\n".join(rows)
            + "\\nRanking frequency is not the probability of a physical mechanism.",
            parent=self.win)
        self.status.set("Monte Carlo cancelled." if result.cancelled else "Monte Carlo complete.")

    def export_results(self):
        if self.busy:
            messagebox.showinfo("Export unavailable", "Finish the active analysis first.", parent=self.win)
            return
        if self.last_fit is None:
            messagebox.showinfo("Nothing to export", "Compare models first.", parent=self.win)
            return
        folder = filedialog.askdirectory(parent=self.win, title="Choose Explorer export folder")
        if not folder:
            return
        try:
            t, y, models = self.last_fit
            result = export_explorer_bundle(
                folder, t, y, models, beta_k_s=float(self.beta.get()),
                monte_carlo=self.last_mc, source=self.selected.get(),
                settings={"fit_baseline": self.baseline.get(),
                          "selected_models": [m.name for m in models]})
            self.status.set(f"Explorer bundle exported: {result}")
        except (OSError, ValueError, TypeError) as exc:
            messagebox.showerror("Export failed", str(exc), parent=self.win)

    def failure(self, message):
        self.busy = False
        self.run_button.configure(state="normal")
        self.mc_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.status.set("Model fitting failed.")
        messagebox.showerror("Model comparison failed", message, parent=self.win)

    def show_result(self, t, y, models):
        self.last_fit = (np.array(t, copy=True), np.array(y, copy=True), models)
        self.last_mc = None
        self.busy = False
        self.run_button.configure(state="normal")
        for child in self.table.get_children():
            self.table.delete(child)
        self.raw_ax.clear()
        self.res_ax.clear()
        self.raw_ax.plot(t, y, color="#2563eb", label="Experimental")
        for candidate in models:
            fit = candidate.fit
            if candidate.error is None:
                self.raw_ax.plot(t, candidate.prediction, label=candidate.name)
                self.res_ax.plot(t, y - candidate.prediction, label=candidate.name)
            self.table.insert("", "end", values=(
                candidate.name,
                f"{fit.reaction_order:.3f}" if fit else "—",
                f"{fit.activation_energy_eV:.3f}" if fit else "—",
                f"{fit.rmse_signal:.4g}" if fit else "—",
                f"{candidate.delta_aicc:.2f}" if candidate.delta_aicc is not None else "—",
                "; ".join(candidate.warnings) if not candidate.error else candidate.error,
            ))
        self.raw_ax.legend(loc="best", fontsize=8)
        self.raw_ax.set_ylabel("Signal")
        self.res_ax.axhline(0, color="gray", linewidth=0.8)
        self.res_ax.set_xlabel("Temperature (°C)")
        self.res_ax.set_ylabel("Residual")
        self.fig.tight_layout(pad=3)
        self.canvas.draw_idle()
        self.status.set("Model comparison finished. AICc rankings are exploratory, not proof of mechanism.")
