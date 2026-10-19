"""Interactive desktop workspace for importing, comparing, and analyzing TPD/TDS data."""
from __future__ import annotations

import queue
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from . import __version__
from .analysis import load_spectrum, smooth_signal


PALETTE = ["#2563eb", "#e76f51", "#059669", "#9333ea", "#d97706", "#0891b2",
           "#db2777", "#4f46e5", "#65a30d", "#475569"]
BG = "#f3f6fb"
INK = "#172b4d"
MUTED = "#64748b"
BLUE = "#2563eb"


def build_cli_arguments(settings: dict[str, object]) -> list[str]:
    """Validate the desktop settings and map them to the established CLI."""
    configured_inputs = settings.get("input_files")
    if configured_inputs is None:
        input_paths = [str(settings.get("input_path", "")).strip()]
    elif isinstance(configured_inputs, (list, tuple)):
        input_paths = [str(path).strip() for path in configured_inputs if str(path).strip()]
    else:
        raise ValueError("Input files must be provided as a list.")
    output_path = str(settings.get("output_path", "")).strip()
    if not input_paths or not input_paths[0]:
        raise ValueError("Import one or more CSV spectra first.")
    missing = [path for path in input_paths if not Path(path).exists()]
    if missing:
        raise ValueError(f"Input path does not exist: {missing[0]}")
    if not output_path:
        raise ValueError("Choose an output folder.")

    def number(key: str, label: str) -> float:
        try:
            return float(settings[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{label} must be a number.") from exc

    edge_low, edge_high = number("leading_low", "Leading-edge lower limit"), number("leading_high", "Leading-edge upper limit")
    red_low, red_high = number("redhead_low", "Peak-search lower limit"), number("redhead_high", "Peak-search upper limit")
    prefactor = number("prefactor", "Redhead prefactor")
    initial_energy = number("kinetic_initial_energy", "Initial kinetic energy")
    initial_prefactor = number("kinetic_initial_prefactor", "Initial kinetic prefactor")
    try:
        window = int(str(settings["window"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Smoothing window must be a positive integer.") from exc
    if edge_low >= edge_high or red_low >= red_high:
        raise ValueError("Each temperature interval needs a lower value below its upper value.")
    if min(prefactor, initial_energy, initial_prefactor) <= 0:
        raise ValueError("Prefactors and initial kinetic energy must be positive.")
    if window < 1:
        raise ValueError("Smoothing window must be at least 1.")
    method = str(settings.get("filter", "median"))
    if method not in {"median", "mean", "none"}:
        raise ValueError("Choose median, mean, or no smoothing.")
    args = [*input_paths, "--output", output_path, "--leading-edge", str(edge_low), str(edge_high),
            "--redhead-region", str(red_low), str(red_high), "--prefactor", str(prefactor),
            "--window", str(window), "--filter", method,
            "--max-time-min", str(number("max_time_min", "Heating-fit time limit"))]
    if bool(settings.get("kinetic_fit", False)):
        model, order = str(settings.get("kinetic_model", "single")), str(settings.get("kinetic_order", "1"))
        if model not in {"single", "two-state", "compare"} or order not in {"0", "1", "2", "fit"}:
            raise ValueError("Choose a valid kinetic model and reaction order.")
        args.extend(["--kinetic-fit", "--kinetic-model", model, "--kinetic-order", order,
                     "--kinetic-initial-energy", str(initial_energy),
                     "--kinetic-initial-prefactor", str(initial_prefactor)])
        if bool(settings.get("kinetic_no_baseline", False)):
            args.append("--kinetic-no-baseline")
    return args



def workflow_guidance(imported: int, visible: int, *, running: bool = False) -> str:
    """Give a useful next step without conflating preview and completed analysis."""
    if running:
        return "Analyzing spectra… Review warnings and results when the run finishes."
    if imported == 0:
        return "Step 1 of 4 · Import CSV spectra or add a folder to begin."
    if visible == 0:
        return "Step 2 of 4 · All imported traces are hidden. Select Show all to continue."
    return (
        f"Step 2–3 of 4 · {visible} visible of {imported} imported. "
        "Inspect traces and analysis windows, then select Run full analysis."
    )


class TpdSpectraApp:
    """Compact three-panel app: import, tune, compare, then export or analyze."""
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title(f"TPD Spectra Studio  ·  {__version__}")
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        min_width = min(1040, max(480, screen_width - 48))
        min_height = min(700, max(400, screen_height - 96))
        root.minsize(min_width, min_height)
        root.geometry(f"{max(min_width, min(1380, screen_width - 48))}x"
                      f"{max(min_height, min(900, screen_height - 96))}+0+0")
        try:
            root.state("zoomed")
        except tk.TclError:
            # Retain the screen-fitted bordered geometry on window managers
            # that do not expose Tk's maximized state.
            pass
        root.configure(background=BG)
        self.spectra: dict[str, dict] = {}
        self.worker_messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self.running = False
        self.view_mode = tk.StringVar(value="Overlay")
        self.x_mode = tk.StringVar(value="Temperature")
        self.filter_method = tk.StringVar(value="median")
        self.normalize = tk.BooleanVar(value=False)
        self.show_raw = tk.BooleanVar(value=True)
        self.kinetic_fit = tk.BooleanVar(value=False)
        self.kinetic_model = tk.StringVar(value="single")
        self.kinetic_order = tk.StringVar(value="1")
        self.output_path = tk.StringVar(value=str(Path.home() / "TPD-Spectra-Results"))
        self.leading_low = tk.DoubleVar(value=130)
        self.leading_high = tk.DoubleVar(value=170)
        self.peak_low = tk.DoubleVar(value=230)
        self.peak_high = tk.DoubleVar(value=400)
        self.window = tk.IntVar(value=10)
        self.prefactor = tk.StringVar(value="1e20")
        self.max_time = tk.StringVar(value="10")
        self.kinetic_energy = tk.StringVar(value="1.0")
        self.kinetic_prefactor = tk.StringVar(value="1e13")
        self.no_baseline = tk.BooleanVar(value=False)
        self._style()
        self._build()
        self.root.after(100, self._poll_worker)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background=BG, foreground=INK, font=("Segoe UI", 9))
        style.configure("Card.TLabel", background="#ffffff", foreground=INK, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background="#102a43", foreground="white", font=("Segoe UI", 19, "bold"))
        style.configure("Subtitle.TLabel", background="#102a43", foreground="#d7e5f5", font=("Segoe UI", 9))
        style.configure("Section.TLabel", background="#ffffff", foreground=INK, font=("Segoe UI", 10, "bold"))
        style.configure("Muted.TLabel", background="#ffffff", foreground=MUTED, font=("Segoe UI", 8))
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), padding=(13, 8),
                        foreground="white", background=BLUE)
        style.map("Primary.TButton", background=[("active", "#1d4ed8"), ("disabled", "#94a3b8")])
        style.configure("TButton", font=("Segoe UI", 9), padding=(9, 6))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TCheckbutton", background="#ffffff", foreground=INK)
        style.configure("TCombobox", padding=4)

    def _build(self) -> None:
        header = tk.Frame(self.root, bg="#102a43", padx=22, pady=16)
        header.pack(fill="x")
        title = ttk.Label(header, text="TPD Spectra Studio", style="Title.TLabel")
        title.pack(anchor="w")
        ttk.Label(header, text="Explore, compare, and analyze temperature-programmed desorption data",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(3, 0))

        toolbar = ttk.Frame(self.root, padding=(18, 10))
        toolbar.pack(fill="x")
        self.import_button = ttk.Button(toolbar, text="＋  Import CSV files", style="Primary.TButton", command=self._import_files)
        self.import_button.pack(side="left")
        ttk.Button(toolbar, text="＋  Add folder", command=self._import_folder).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Export plot PNG", command=self._export_png).pack(side="left", padx=(8, 0))
        self.run_button = ttk.Button(toolbar, text="Run full analysis", style="Primary.TButton", command=self._run_analysis)
        self.run_button.pack(side="right")
        ttk.Button(toolbar, text="Quick start  ?", command=self._show_quick_start).pack(side="right", padx=(0, 10))
        self.status = tk.StringVar(value=workflow_guidance(0, 0))
        ttk.Label(toolbar, textvariable=self.status, foreground=MUTED).pack(side="right", padx=12)

        body = ttk.Frame(self.root, padding=(18, 0, 18, 10))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0, minsize=322)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        sidebar_frame = ttk.Frame(body, style="Card.TFrame", width=322)
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sidebar_frame.grid_propagate(False)
        sidebar_frame.rowconfigure(0, weight=1)
        sidebar_frame.columnconfigure(0, weight=1)
        sidebar_canvas = tk.Canvas(sidebar_frame, background="white", highlightthickness=0, width=306)
        sidebar_scroll = ttk.Scrollbar(sidebar_frame, orient="vertical", command=sidebar_canvas.yview)
        sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        sidebar_canvas.grid(row=0, column=0, sticky="nsew")
        sidebar_scroll.grid(row=0, column=1, sticky="ns")
        self.sidebar = ttk.Frame(sidebar_canvas, style="Card.TFrame", padding=14)
        sidebar_window = sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")
        self.sidebar.bind("<Configure>", lambda _event: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        sidebar_canvas.bind("<Configure>", lambda event: sidebar_canvas.itemconfigure(sidebar_window, width=event.width))
        sidebar_canvas.bind("<MouseWheel>", lambda event: sidebar_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units"))
        workspace = ttk.Frame(body, style="Card.TFrame", padding=(12, 10))
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(1, weight=1)

        self._files_panel()
        self._workspace(workspace)

        footer = ttk.Frame(self.root, padding=(20, 5))
        footer.pack(fill="x")
        ttk.Label(footer, text="Review model assumptions and warnings before scientific interpretation.", foreground=MUTED).pack(side="left")
        ttk.Button(footer, text="Open results folder", command=self._open_output).pack(side="right")

    def _show_quick_start(self) -> None:
        """Explain the normal workflow without changing analysis settings."""
        messagebox.showinfo(
            "Getting started with TPD Spectra Studio",
            "1. IMPORT: Select one or more CSV spectra or add a folder.\\n\\n"
            "2. EXPLORE: Show or hide traces, choose an overlay or small multiples, "
            "and adjust smoothing. The comparison updates interactively.\\n\\n"
            "3. SELECT: Set leading-edge and peak-search temperature windows. "
            "Shaded areas show which data will be analyzed.\\n\\n"
            "4. ANALYZE: Choose a results folder. Enable kinetic fitting only if "
            "the model assumptions apply, then click Run full analysis.\\n\\n"
            "5. REVIEW: Open the results folder and inspect diagnostic plots "
            "and warnings before interpreting energies.\\n\\n"
            "TIP: Export plot PNG saves the current view without running the "
            "full analysis. A good-looking fit does not establish a unique mechanism.",
            parent=self.root,
        )

    def _files_panel(self) -> None:
        ttk.Label(self.sidebar, text="1  ·  IMPORTED SPECTRA", style="Section.TLabel").pack(anchor="w")
        ttk.Label(self.sidebar, text="Imported traces appear together in the plot.", style="Muted.TLabel").pack(anchor="w", pady=(2, 8))
        columns = ("visible", "name", "points")
        self.file_table = ttk.Treeview(self.sidebar, columns=columns, show="headings", height=7, selectmode="extended")
        self.file_table.heading("visible", text="On")
        self.file_table.heading("name", text="File")
        self.file_table.heading("points", text="Points")
        self.file_table.column("visible", width=34, anchor="center", stretch=False)
        self.file_table.column("name", width=184, anchor="w")
        self.file_table.column("points", width=55, anchor="e", stretch=False)
        self.file_table.pack(fill="x")
        self.file_table.bind("<Button-1>", self._toggle_row)
        self.file_table.bind("<Double-1>", self._toggle_row)
        row = ttk.Frame(self.sidebar, style="Card.TFrame")
        row.pack(fill="x", pady=(6, 12))
        ttk.Button(row, text="Show all", command=lambda: self._set_visible(True)).pack(side="left")
        ttk.Button(row, text="Hide all", command=lambda: self._set_visible(False)).pack(side="left", padx=5)
        ttk.Button(row, text="Remove", command=self._remove_selected).pack(side="right")

        ttk.Label(self.sidebar, text="RESULTS DESTINATION", style="Section.TLabel").pack(anchor="w", pady=(3, 4))
        output_row = ttk.Frame(self.sidebar, style="Card.TFrame")
        output_row.pack(fill="x", pady=(0, 8))
        ttk.Entry(output_row, textvariable=self.output_path, width=25).pack(side="left", fill="x", expand=True)
        ttk.Button(output_row, text="Browse", command=self._choose_output).pack(side="left", padx=(5, 0))

        ttk.Separator(self.sidebar).pack(fill="x", pady=5)
        ttk.Label(self.sidebar, text="2  ·  EXPLORE SPECTRA", style="Section.TLabel").pack(anchor="w", pady=(7, 6))
        self._choice("Chart layout", self.view_mode, ("Overlay", "Small multiples"))
        self._choice("X axis", self.x_mode, ("Temperature", "Time"))
        self._choice("Smoothing", self.filter_method, ("median", "mean", "none"))
        self._slider("Smoothing window", self.window, 1, 60, " points")
        ttk.Checkbutton(self.sidebar, text="Overlay raw signal", variable=self.show_raw,
                        command=self._draw_plot).pack(anchor="w", pady=(5, 0))
        ttk.Checkbutton(self.sidebar, text="Normalize each trace to 0–1", variable=self.normalize,
                        command=self._draw_plot).pack(anchor="w", pady=(3, 9))

        ttk.Separator(self.sidebar).pack(fill="x", pady=5)
        ttk.Label(self.sidebar, text="3  ·  SELECT ANALYSIS WINDOWS  ·  °C", style="Section.TLabel").pack(anchor="w", pady=(7, 4))
        self._slider("Leading edge · from", self.leading_low, 0, 700, " °C", on_change=self._range_changed)
        self._slider("Leading edge · to", self.leading_high, 0, 700, " °C", on_change=self._range_changed)
        self._slider("Peak search · from", self.peak_low, 0, 700, " °C", on_change=self._range_changed)
        self._slider("Peak search · to", self.peak_high, 0, 700, " °C", on_change=self._range_changed)
        ttk.Label(self.sidebar, text="Shaded bands mark the selected analysis regions.", style="Muted.TLabel").pack(anchor="w", pady=(3, 8))
        details = ttk.Frame(self.sidebar, style="Card.TFrame")
        details.pack(fill="x", pady=(0, 7))
        ttk.Label(details, text="Redhead prefactor (s⁻¹)", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(details, textvariable=self.prefactor, width=11).grid(row=0, column=1, sticky="e")
        ttk.Label(details, text="Heating-fit time limit (min; −1 = all)", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(details, textvariable=self.max_time, width=11).grid(row=1, column=1, sticky="e")
        self._advanced_panel()

    def _choice(self, label: str, variable: tk.StringVar, values: tuple[str, ...]) -> None:
        row = ttk.Frame(self.sidebar, style="Card.TFrame")
        row.pack(fill="x", pady=3)
        ttk.Label(row, text=label, style="Card.TLabel").pack(side="left")
        combo = ttk.Combobox(row, textvariable=variable, values=values, state="readonly", width=17)
        combo.pack(side="right")
        combo.bind("<<ComboboxSelected>>", lambda _event: self._draw_plot())

    def _slider(self, label: str, variable: tk.Variable, low: int, high: int, suffix: str,
                on_change=None) -> None:
        row = ttk.Frame(self.sidebar, style="Card.TFrame")
        row.pack(fill="x", pady=1)
        ttk.Label(row, text=label, style="Card.TLabel").pack(side="left")
        value_label = ttk.Label(row, text=f"{variable.get()}{suffix}", style="Card.TLabel", foreground=BLUE)
        value_label.pack(side="right")
        def changed(value) -> None:
            value_label.configure(text=f"{int(float(value))}{suffix}")
            if on_change:
                on_change()
            else:
                self._draw_plot()
        tk.Scale(self.sidebar, from_=low, to=high, orient="horizontal", showvalue=False, resolution=1,
                 variable=variable, command=changed, bg="white", fg=INK, troughcolor="#dbeafe",
                 activebackground=BLUE, highlightthickness=0, bd=0, sliderrelief="flat", length=270).pack(fill="x", pady=(0, 3))

    def _advanced_panel(self) -> None:
        ttk.Checkbutton(self.sidebar, text="Enable numerical kinetic fitting", variable=self.kinetic_fit,
                        command=self._toggle_kinetics).pack(anchor="w", pady=(2, 5))
        row = ttk.Frame(self.sidebar, style="Card.TFrame")
        row.pack(fill="x")
        self.kinetic_combo = ttk.Combobox(row, textvariable=self.kinetic_model,
                values=("single", "two-state", "compare"), state="disabled", width=12)
        self.kinetic_combo.pack(side="left")
        self.order_combo = ttk.Combobox(row, textvariable=self.kinetic_order,
                values=("0", "1", "2", "fit"), state="disabled", width=7)
        self.order_combo.pack(side="right")
        ttk.Label(row, text="order", style="Muted.TLabel").pack(side="right", padx=5)
        self.kinetic_options = ttk.Frame(self.sidebar, style="Card.TFrame")
        self.kinetic_options.pack(fill="x", pady=5)
        ttk.Label(self.kinetic_options, text="Initial energy (eV)", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(self.kinetic_options, textvariable=self.kinetic_energy, width=10).grid(row=0, column=1, sticky="e")
        ttk.Label(self.kinetic_options, text="Initial prefactor (s⁻¹)", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(self.kinetic_options, textvariable=self.kinetic_prefactor, width=10).grid(row=1, column=1, sticky="e")
        ttk.Checkbutton(self.kinetic_options, text="Fix baseline at zero", variable=self.no_baseline).grid(row=2, column=0, columnspan=2, sticky="w")
        self.kinetic_options.grid_remove()

    def _toggle_kinetics(self) -> None:
        enabled = self.kinetic_fit.get()
        self.kinetic_combo.configure(state="readonly" if enabled else "disabled")
        self.order_combo.configure(state="readonly" if enabled else "disabled")
        if enabled:
            self.kinetic_options.grid()
        else:
            self.kinetic_options.grid_remove()

    def _workspace(self, parent: ttk.Frame) -> None:
        top = ttk.Frame(parent, style="Card.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        ttk.Label(top, text="Spectrum comparison", style="Section.TLabel").pack(side="left")
        self.count_label = ttk.Label(top, text="0 traces", style="Muted.TLabel")
        self.count_label.pack(side="right")
        plot_wrap = ttk.Frame(parent, style="Card.TFrame")
        plot_wrap.grid(row=1, column=0, sticky="nsew")
        plot_wrap.rowconfigure(0, weight=1)
        plot_wrap.columnconfigure(0, weight=1)
        self.figure = Figure(figsize=(8.7, 6.4), dpi=100, facecolor="white")
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_wrap)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        nav = ttk.Frame(plot_wrap, style="Card.TFrame")
        nav.grid(row=1, column=0, sticky="ew")
        self.nav_toolbar = NavigationToolbar2Tk(self.canvas, nav, pack_toolbar=False)
        self.nav_toolbar.update()
        self.nav_toolbar.pack(side="left")
        self._empty_plot()

    def _empty_plot(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor("#ffffff")
        self.axis.text(.5, .54, "1 · Import CSV spectra to begin", transform=self.axis.transAxes,
                       ha="center", va="center", fontsize=16, color="#64748b", weight="bold")
        self.axis.text(.5, .47, "Use Import CSV files or Add folder above; then explore and analyze", transform=self.axis.transAxes,
                       ha="center", va="center", fontsize=10, color="#94a3b8")
        self.axis.set_xticks([]); self.axis.set_yticks([])
        for edge in self.axis.spines.values(): edge.set_visible(False)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _import_files(self) -> None:
        paths = filedialog.askopenfilenames(parent=self.root, title="Choose spectra to compare",
                filetypes=(("CSV spectra", "*.csv"), ("All files", "*.*")))
        if paths:
            self._load_paths([Path(p) for p in paths])

    def _import_folder(self) -> None:
        folder = filedialog.askdirectory(parent=self.root, title="Choose a folder containing CSV spectra")
        if folder:
            self._load_paths(sorted(Path(folder).rglob("*.csv")))

    def _choose_output(self) -> None:
        folder = filedialog.askdirectory(parent=self.root, title="Choose where analysis results will be saved",
                                         initialdir=str(Path(self.output_path.get()).expanduser().parent))
        if folder:
            self.output_path.set(folder)

    def _load_paths(self, paths: list[Path]) -> None:
        added, errors = 0, []
        for path in paths:
            key = str(path.resolve())
            if key in self.spectra:
                continue
            try:
                spec = load_spectrum(path)
                self.spectra[key] = {"path": path, "spec": spec, "visible": True}
                self.file_table.insert("", "end", iid=key, values=("✓", path.name, f"{spec.signal.size:,}"))
                added += 1
            except Exception as exc:
                errors.append(f"{path.name}: {exc}")
        self.status.set(f"Added {added} trace{'s' if added != 1 else ''}." if added else "No new spectra were added.")
        self._draw_plot()
        if errors:
            messagebox.showwarning("Some files could not be imported", "\n".join(errors[:10]), parent=self.root)

    def _toggle_row(self, event) -> str | None:
        row = self.file_table.identify_row(event.y)
        column = self.file_table.identify_column(event.x)
        if row and column == "#1" and row in self.spectra:
            item = self.spectra[row]
            item["visible"] = not item["visible"]
            self.file_table.set(row, "visible", "✓" if item["visible"] else "—")
            self._draw_plot()
            return "break"
        return None

    def _set_visible(self, visible: bool) -> None:
        for key, item in self.spectra.items():
            item["visible"] = visible
            self.file_table.set(key, "visible", "✓" if visible else "—")
        self._draw_plot()

    def _remove_selected(self) -> None:
        for key in self.file_table.selection():
            self.spectra.pop(key, None)
            self.file_table.delete(key)
        self._draw_plot()

    def _range_changed(self) -> None:
        if self.leading_low.get() >= self.leading_high.get():
            self.leading_high.set(min(700, self.leading_low.get() + 1))
        if self.peak_low.get() >= self.peak_high.get():
            self.peak_high.set(min(700, self.peak_low.get() + 1))
        self._draw_plot()

    def _draw_plot(self) -> None:
        if not hasattr(self, "axis"):
            return
        visible = [(key, row) for key, row in self.spectra.items() if row["visible"]]
        self.count_label.configure(text=f"{len(visible)} of {len(self.spectra)} traces shown")
        if not self.running:
            self.status.set(workflow_guidance(len(self.spectra), len(visible)))
        if not visible:
            self._empty_plot()
            if self.spectra:
                self.axis.text(.5, .38, "All traces hidden · Click Show all in the sidebar",
                               transform=self.axis.transAxes, ha="center", fontsize=10, color=MUTED)
                self.canvas.draw_idle()
            return
        self.figure.clear()
        mode = self.view_mode.get()
        count = len(visible) if mode == "Small multiples" else 1
        if count > 1:
            cols = 2 if count > 2 else count
            rows = (count + cols - 1) // cols
            axes = [self.figure.add_subplot(rows, cols, i + 1) for i in range(count)]
        else:
            axes = [self.figure.add_subplot(111)]
        self.axis = axes[0]
        palette = PALETTE
        for i, (key, row) in enumerate(visible):
            target_axes = axes[i] if mode == "Small multiples" else axes[0]
            spec = row["spec"]
            x = spec.temperature_clean_c if self.x_mode.get() == "Temperature" else spec.time_min
            raw = spec.signal
            smooth = smooth_signal(raw, int(self.window.get()), self.filter_method.get())
            if self.normalize.get():
                span = max(float(smooth.max() - smooth.min()), 1e-15)
                smooth = (smooth - smooth.min()) / span
                if self.show_raw.get():
                    raw_span = max(float(raw.max() - raw.min()), 1e-15)
                    raw = (raw - raw.min()) / raw_span
            color = palette[i % len(palette)]
            if self.show_raw.get():
                target_axes.plot(x, raw, color=color, alpha=.20, linewidth=.8)
            target_axes.plot(x, smooth, color=color, linewidth=1.7, label=Path(key).stem)
            if self.x_mode.get() == "Temperature":
                target_axes.axvspan(self.leading_low.get(), self.leading_high.get(), color="#f59e0b", alpha=.08)
                target_axes.axvspan(self.peak_low.get(), self.peak_high.get(), color="#8b5cf6", alpha=.07)
            if mode == "Small multiples":
                target_axes.set_title(Path(key).name, loc="left", fontsize=9, color=INK)
            target_axes.grid(True, color="#e7edf5", linewidth=.7)
            target_axes.tick_params(labelsize=8, colors=MUTED)
            for spine in target_axes.spines.values(): spine.set_color("#d9e2ec")
        x_label = "Temperature (°C)" if self.x_mode.get() == "Temperature" else "Time (min)"
        y_label = "Normalized signal (0–1)" if self.normalize.get() else "Signal (a.u.)"
        for ax in axes:
            ax.set_xlabel(x_label, color=INK, fontsize=9)
            ax.set_ylabel(y_label, color=INK, fontsize=9)
        if mode == "Overlay":
            axes[0].legend(loc="best", fontsize=8, frameon=True, framealpha=.92)
            axes[0].set_title("Overlay comparison" if len(visible) > 1 else Path(visible[0][0]).name,
                              loc="left", color=INK, fontsize=11, weight="bold")
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    def _export_png(self) -> None:
        if not self.spectra:
            messagebox.showinfo("Nothing to export", "Import at least one spectrum before exporting a plot.", parent=self.root)
            return
        path = filedialog.asksaveasfilename(parent=self.root, title="Export plot as PNG",
                defaultextension=".png", initialfile="tpd-spectra-comparison.png",
                filetypes=(("PNG image", "*.png"),))
        if path:
            self.figure.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
            self.status.set(f"PNG exported: {Path(path).name}")

    def _settings(self, input_files: list[Path], output_folder: Path) -> dict[str, object]:
        return {"input_files": [str(path) for path in input_files], "output_path": str(output_folder),
                "leading_low": self.leading_low.get(), "leading_high": self.leading_high.get(),
                "redhead_low": self.peak_low.get(), "redhead_high": self.peak_high.get(),
                "prefactor": self.prefactor.get(), "window": self.window.get(), "filter": self.filter_method.get(),
                "max_time_min": self.max_time.get(), "kinetic_fit": self.kinetic_fit.get(),
                "kinetic_model": self.kinetic_model.get(), "kinetic_order": self.kinetic_order.get(),
                "kinetic_initial_energy": self.kinetic_energy.get(),
                "kinetic_initial_prefactor": self.kinetic_prefactor.get(),
                "kinetic_no_baseline": self.no_baseline.get()}

    def _run_analysis(self) -> None:
        if self.running:
            return
        selected = [(key, row["path"]) for key, row in self.spectra.items() if row["visible"]]
        if not selected:
            messagebox.showinfo("No spectra selected", "Import spectra and turn on at least one trace to analyze.", parent=self.root)
            return
        outdir = Path(self.output_path.get()).expanduser()
        try:
            outdir.mkdir(parents=True, exist_ok=True)
            settings = self._settings([path for _, path in selected], outdir)
            args = build_cli_arguments(settings)
        except Exception as exc:
            messagebox.showerror("Could not prepare analysis", str(exc), parent=self.root)
            return
        self.running = True
        self.run_button.configure(state="disabled")
        self.status.set(f"Analyzing {len(selected)} spectrum{'s' if len(selected) != 1 else ''}…")
        threading.Thread(target=self._analysis_worker, args=(args,), daemon=True).start()

    def _analysis_worker(self, args: list[str]) -> None:
        try:
            if getattr(sys, "frozen", False):
                # The GUI executable doubles as a hidden CLI entry point.
                command = [sys.executable, "--tpd-cli", *args]
            else:
                command = [sys.executable, "-m", "tpd_spectra", *args]
            completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       errors="replace", check=False)
            for line in completed.stdout.splitlines():
                self.worker_messages.put(("log", line))
            self.worker_messages.put(("done", str(completed.returncode)))
        except Exception as exc:
            self.worker_messages.put(("error", str(exc)))

    def _poll_worker(self) -> None:
        try:
            while True:
                kind, value = self.worker_messages.get_nowait()
                if kind == "done":
                    self.running = False
                    self.run_button.configure(state="normal")
                    if value == "0":
                        self.status.set(f"Analysis complete · results saved to {self.output_path.get()}")
                        messagebox.showinfo("Analysis complete", f"Your tables, comparison plot, and diagnostics are in:\n{self.output_path.get()}", parent=self.root)
                    else:
                        self.status.set("Analysis finished with errors; review the run log.")
                elif kind == "error":
                    self.running = False
                    self.run_button.configure(state="normal")
                    self.status.set("Could not start the analysis.")
                    messagebox.showerror("Analysis could not start", value, parent=self.root)
                else:
                    self.status.set(value[:100])
        except queue.Empty:
            pass
        self.root.after(120, self._poll_worker)

    def _open_output(self) -> None:
        path = Path(self.output_path.get()).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "win32":
                import os
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Cannot open folder", str(exc), parent=self.root)

    def _close(self) -> None:
        if self.running and not messagebox.askyesno("Analysis is running", "Close the app while analysis is in progress?", parent=self.root):
            return
        self.root.destroy()


def main() -> int:
    root = tk.Tk()
    TpdSpectraApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
