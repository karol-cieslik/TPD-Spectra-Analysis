"""Review and results dialogs; all calculations use the established CLI engine."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.image import imread

from .analysis import smooth_signal
from .run_session import proposed_run_folder, sha256


def text_panel(parent, content=""):
    panel = ttk.Frame(parent)
    panel.rowconfigure(0, weight=1)
    panel.columnconfigure(0, weight=1)
    text = tk.Text(panel, wrap="word", font=("Segoe UI", 10), padx=14, pady=12,
                   width=60, height=12)
    scroll = ttk.Scrollbar(panel, command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    text.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")
    text.insert("1.0", content)
    text.configure(state="disabled")
    return panel, text


def configure_dialog(dialog, parent, title):
    dialog.title(title)
    dialog.transient(parent)
    width = min(940, parent.winfo_screenwidth() - 60)
    height = min(780, parent.winfo_screenheight() - 100)
    dialog.geometry(f"{width}x{height}")
    dialog.minsize(min(540, width), min(420, height))
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(1, weight=1)
    dialog.bind("<Escape>", lambda _event: dialog.destroy())


def review_text(settings, rows):
    content = [f"INCLUDED INPUTS ({len(rows)})", ""]
    for row in rows:
        spec = row["spec"]
        signal = smooth_signal(spec.signal, int(settings["window"]), settings["filter"])
        temperature = spec.temperature_clean_c
        edge = ((temperature >= float(settings["leading_low"])) &
                (temperature <= float(settings["leading_high"])) & (signal > 0))
        peak = ((temperature >= float(settings["redhead_low"])) &
                (temperature <= float(settings["redhead_high"])))
        if not np.any(peak):
            raise ValueError(f"{row['path'].name}: peak-search interval contains no points. Adjust it before running.")
        content.extend([str(row["path"].resolve()),
                        f"  {len(signal)} accepted points; {min(temperature):.3g}–{max(temperature):.3g} °C; "
                        f"{spec.time_min[-1]:.3g} min elapsed",
                        f"  Temperature corrections: {spec.points_temperature_corrected}; "
                        f"leading-edge positive points: {edge.sum()}; peak-search points: {peak.sum()}"])
        if edge.sum() < 5:
            content.append("  WARNING: leading-edge estimate will be unavailable (fewer than 5 positive points).")
    content.extend(["", "PROCESSING AND METHODS",
                    f"Smoothing: {settings['filter']}, window {settings['window']} points.",
                    "Plot normalization is display-only; calculations use the unnormalized signal.",
                    f"Leading edge: {settings['leading_low']}–{settings['leading_high']} °C. "
                    "Apparent activation energy; inspect positivity, baseline, depletion and overlap.",
                    f"Peak search: {settings['redhead_low']}–{settings['redhead_high']} °C.",
                    f"Redhead ASSUMED prefactor: {settings['prefactor']} s⁻¹ (user setting, not measured).",
                    "Redhead assumes first-order desorption and an approximately linear heating ramp.",
                    f"Heating-fit time limit: {settings['max_time_min']} min (−1 means all).",
                    "No automatic baseline subtraction. Temperature cleaning is a heuristic, not calibration.",
                    "Input rows are sorted by time; duplicate times keep the first row. Inspect import reports.",
                    "Regression confidence intervals exclude experimental and model uncertainty."])
    if settings["kinetic_fit"]:
        content.extend(["", "EXPLORATORY KINETIC FIT",
                        f"Model: {settings['kinetic_model']}; order: {settings['kinetic_order']}.",
                        f"Initial guesses: {settings['kinetic_initial_energy']} eV; "
                        f"{settings['kinetic_initial_prefactor']} s⁻¹.",
                        f"Baseline: {'fixed zero' if settings['kinetic_no_baseline'] else 'fitted'}.",
                        "Uses a fitted linear temperature ramp. A converged fit does not establish a unique mechanism."])
    content.extend(["", "OUTPUTS", "Parameter and batch tables; diagnostic plots; warnings/errors where present; "
                    "input hashes, reviewed settings, run status and streamed run log.",
                    "Each saved run uses a new folder. Source CSV files are never modified.",
                    "A computed preview analyzes only the selected input and is stored temporarily."])
    return "\n".join(content)


class ReviewDialog(tk.Toplevel):
    def __init__(self, parent, settings, rows, on_start):
        # Validate before creating a partially initialized window.
        summary = review_text(settings, rows)
        fingerprints = {str(row["path"].resolve()): sha256(row["path"]) for row in rows}
        for row in rows:
            if row.get("sha256") and row["sha256"] != fingerprints[str(row["path"].resolve())]:
                raise ValueError(f"Input changed after import: {row['path'].name}. Remove it and import the updated file before review.")
        super().__init__(parent)
        configure_dialog(self, parent, "Review analysis · TPD Spectra Studio")
        self.settings = json.loads(json.dumps(settings))
        self.rows = rows
        self.fingerprints = fingerprints
        self.on_start = on_start
        ttk.Label(self, text="Review inputs, assumptions and destination", font=("Segoe UI", 14, "bold"),
                  padding=12).grid(row=0, column=0, sticky="w")
        tabs = ttk.Notebook(self)
        tabs.grid(row=1, column=0, sticky="nsew", padx=12)
        panel, self.summary = text_panel(tabs, summary)
        tabs.add(panel, text="Review")
        reports = {str(row["path"]): row["spec"].import_report for row in rows}
        panel, _ = text_panel(tabs, json.dumps(reports, indent=2, ensure_ascii=False))
        tabs.add(panel, text="Import reports")
        setup = ttk.Frame(tabs)
        tabs.add(setup, text="Setup preview")
        self.selection = tk.StringVar(value=str(rows[0]["path"]))
        selector = ttk.Combobox(setup, textvariable=self.selection, state="readonly",
                               values=[str(row["path"]) for row in rows])
        selector.pack(fill="x", padx=8, pady=8)
        selector.bind("<<ComboboxSelected>>", lambda _e: self.draw_setup())
        self.figure = Figure(figsize=(7, 4), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.figure, master=setup)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.draw_setup()
        destination = ttk.Frame(self, padding=12)
        destination.grid(row=2, column=0, sticky="ew")
        destination.columnconfigure(0, weight=1)
        ttk.Label(destination, text="New run folder (confirm below; no overwriting)").grid(row=0, column=0, sticky="w")
        self.destination = tk.StringVar(value=str(proposed_run_folder(settings["output_path"])))
        ttk.Entry(destination, textvariable=self.destination).grid(row=1, column=0, sticky="ew", pady=6)
        ttk.Button(destination, text="Choose parent folder…", command=self.browse).grid(row=1, column=1, padx=8)
        self.confirmed = tk.BooleanVar(value=False)
        self.destination.trace_add("write", lambda *_: self.confirmed.set(False))
        ttk.Checkbutton(destination, variable=self.confirmed,
                        text="I reviewed the included files, assumed prefactor and save location.").grid(row=2, column=0, columnspan=2, sticky="w")
        buttons = ttk.Frame(self, padding=12)
        buttons.grid(row=3, column=0, sticky="ew")
        ttk.Button(buttons, text="Back / Cancel", command=self.destroy).pack(side="left")
        ttk.Button(buttons, text="Compute selected preview", command=lambda: self.start(True)).pack(side="left", padx=8)
        self.run_button = ttk.Button(buttons, text="Run and save", style="Primary.TButton", command=lambda: self.start(False))
        self.run_button.pack(side="right")
        self.grab_set()
        self.run_button.focus_set()

    def browse(self):
        parent = filedialog.askdirectory(parent=self, title="Choose an existing parent folder")
        if parent:
            self.destination.set(str(proposed_run_folder(parent)))
            self.confirmed.set(False)

    def draw_setup(self):
        row = next(row for row in self.rows if str(row["path"]) == self.selection.get())
        spec = row["spec"]
        self.figure.clear()
        axis, temp_axis = self.figure.subplots(2, 1)
        axis.plot(spec.temperature_clean_c, spec.signal, color=".65", label="Raw signal")
        axis.plot(spec.temperature_clean_c, smooth_signal(spec.signal, int(self.settings["window"]), self.settings["filter"]), label="Processed signal")
        axis.axvspan(float(self.settings["leading_low"]), float(self.settings["leading_high"]), alpha=.15, color="orange", label="Leading edge")
        axis.axvspan(float(self.settings["redhead_low"]), float(self.settings["redhead_high"]), alpha=.12, color="purple", label="Peak search")
        axis.set(xlabel="Temperature (°C)", ylabel="Signal (a.u.)", title="Setup preview · no fit calculated")
        axis.legend(fontsize=8)
        temp_axis.plot(spec.time_min, spec.temperature_c, label="Raw temperature")
        temp_axis.plot(spec.time_min, spec.temperature_clean_c, linestyle="--", label="Cleaned temperature")
        changed = ~np.isclose(spec.temperature_c, spec.temperature_clean_c)
        temp_axis.scatter(spec.time_min[changed], spec.temperature_clean_c[changed], color="red", label="Corrected points")
        temp_axis.set(xlabel="Elapsed time (min)", ylabel="Temperature (°C)")
        temp_axis.legend(fontsize=8)
        self.canvas.draw_idle()

    def start(self, preview):
        if not self.confirmed.get():
            messagebox.showinfo("Review required", "Review the inputs and assumptions, then tick the confirmation box.", parent=self)
            return
        try:
            for path, digest in self.fingerprints.items():
                if sha256(path) != digest:
                    raise ValueError(f"Input changed since review: {Path(path).name}. Close this review and import it again.")
            settings = json.loads(json.dumps(self.settings))
            settings["output_path"] = self.destination.get()
            if preview:
                settings["input_files"] = [self.selection.get()]
            if self.on_start(settings, preview):
                self.destroy()
        except Exception as exc:
            messagebox.showerror("Cannot start analysis", str(exc), parent=self)


class ResultsDialog(tk.Toplevel):
    def __init__(self, parent, folder, state, *, preview=False, stale=False):
        super().__init__(parent)
        configure_dialog(self, parent, "Results review · TPD Spectra Studio")
        title = ("Unsaved computed preview — one spectrum" if preview else "Saved analysis")
        if stale:
            title += " · settings have changed since this run"
        ttk.Label(self, text=f"{title}\nStatus: {state}\n{folder}", padding=12,
                  wraplength=780).grid(row=0, column=0, sticky="w")
        tabs = ttk.Notebook(self)
        tabs.grid(row=1, column=0, sticky="nsew", padx=12)
        lines = ["Results describe the saved settings snapshot. Editing the workspace never updates these results.",
                 "Inspect warnings and residuals before interpreting values. Blank or nonfinite estimates are unavailable.", ""]
        table = folder / "all_desorption_parameters.csv"
        if table.exists():
            with table.open(encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream):
                    lines.extend([row["file_name"],
                                  f"  Leading-edge apparent energy: {row.get('leading_edge_energy_eV', 'unavailable')} eV",
                                  f"  Redhead energy: {row.get('redhead_energy_eV', 'unavailable')} eV",
                                  f"  Assumed prefactor: {row.get('redhead_prefactor_assumed_s_inv', 'unavailable')} s⁻¹",
                                  f"  Heating rate: {row.get('heating_rate_K_s', 'unavailable')} K/s", ""])
        for name in ("analysis_warnings.csv", "analysis_errors.csv"):
            if (folder / name).exists():
                lines.extend([name, (folder / name).read_text(encoding="utf-8"), ""])
        panel, self.summary = text_panel(tabs, "\n".join(lines))
        tabs.add(panel, text="Results and warnings")
        plots = sorted(folder.rglob("*.png"))
        if plots:
            plot_panel = ttk.Frame(tabs)
            tabs.add(plot_panel, text="Plots and residuals")
            self.plot_selection = tk.StringVar(value=str(plots[0].relative_to(folder)))
            combo = ttk.Combobox(plot_panel, textvariable=self.plot_selection, state="readonly",
                                 values=[str(p.relative_to(folder)) for p in plots])
            combo.pack(fill="x", padx=8, pady=8)
            self.figure = Figure(figsize=(7, 5), constrained_layout=True)
            self.canvas = FigureCanvasTkAgg(self.figure, master=plot_panel)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            def draw(_event=None):
                self.figure.clear()
                ax = self.figure.add_subplot()
                ax.imshow(imread(folder / self.plot_selection.get()))
                ax.set_axis_off()
                self.canvas.draw_idle()
            combo.bind("<<ComboboxSelected>>", draw)
            draw()
        for name, label in (("run.log", "Run log"), ("run_status.json", "Reviewed settings")):
            content = (folder / name).read_text(encoding="utf-8") if (folder / name).exists() else "No record available."
            panel, _ = text_panel(tabs, content)
            tabs.add(panel, text=label)
        ttk.Button(self, text="Close", command=self.destroy).grid(row=2, column=0, sticky="e", padx=12, pady=12)
