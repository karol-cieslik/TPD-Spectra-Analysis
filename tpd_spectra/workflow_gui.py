"""Three-stage desktop workflow; the classic workspace remains available."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector

from .gui import TpdSpectraApp
from .branding import NAVY, brand_image, set_windows_app_identity
from .workflow_state import WorkflowProject, METHODS, STAGES


class WorkflowApp(TpdSpectraApp):
    def __init__(self, root):
        self.project = WorkflowProject()
        self.restoring = False
        self.classic = None
        self.dataset_choice = tk.StringVar(root)
        self.region_choice = tk.StringVar(root)
        self.region_name = tk.StringVar(root, value="Peak 1")
        self.region_low = tk.StringVar(root)
        self.region_high = tk.StringVar(root)
        self.method = tk.StringVar(root, value=METHODS[0])
        self.method_values = {k: tk.StringVar(root) for k in
                              ("lower", "upper", "beta", "prefactor", "energy", "order", "max_nfev")}
        self.method_flags = {k: tk.BooleanVar(root) for k in ("free_order", "fit_baseline")}
        super().__init__(root)
        self.filter_method.set("none")
        self.window.set(1)

    def _build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=16, pady=10)
        header.pack(fill="x")
        self.brand_mark = brand_image(header, 48)
        tk.Label(header, image=self.brand_mark, bg=NAVY).pack(side="left", padx=(0, 12))
        ttk.Label(header, text="TPD Spectra Studio", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="WORKFLOW PREVIEW", style="Subtitle.TLabel").pack(side="right")
        actions = ttk.Frame(self.root, padding=10)
        actions.pack(fill="x")
        ttk.Button(actions, text="Import spectra…", command=self._import_files).pack(side="left")
        ttk.Button(actions, text="Add folder…", command=self._import_folder).pack(side="left", padx=5)
        ttk.Button(actions, text="Classic / batch workspace", command=self.open_classic).pack(side="right")
        ttk.Button(actions, text="About", command=self._show_about).pack(side="right", padx=5)
        self.project_actions = actions
        context = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        context.pack(fill="x")
        context.columnconfigure(1, weight=1)
        context.columnconfigure(3, weight=1)
        ttk.Label(context, text="Dataset").grid(row=0, column=0, padx=4)
        self.dataset_combo = ttk.Combobox(context, textvariable=self.dataset_choice, state="readonly")
        self.dataset_combo.grid(row=0, column=1, sticky="ew")
        self.dataset_combo.bind("<<ComboboxSelected>>", self.select_dataset)
        ttk.Label(context, text="Peak").grid(row=0, column=2, padx=8)
        self.region_combo = ttk.Combobox(context, textvariable=self.region_choice, state="readonly")
        self.region_combo.grid(row=0, column=3, sticky="ew")
        self.region_combo.bind("<<ComboboxSelected>>", self.select_region)
        self.context_label = ttk.Label(context, text="Import a spectrum and define a peak.")
        self.context_label.grid(row=1, column=0, columnspan=4, sticky="w", pady=(5, 0))
        self.stages = ttk.Notebook(self.root)
        self.stages.pack(fill="both", expand=True, padx=12)
        self.stage_frames = [ttk.Frame(self.stages) for _ in STAGES]
        for frame, title in zip(self.stage_frames, STAGES):
            self.stages.add(frame, text=title)
        self._build_preparation(self.stage_frames[0])
        self._build_modeling(self.stage_frames[1])
        self._build_kinetic(self.stage_frames[2])
        self.status = tk.StringVar(self.root, value="Import spectra to begin.")
        ttk.Label(self.root, textvariable=self.status, padding=10, wraplength=1100).pack(fill="x")
        self.stages.bind("<<NotebookTabChanged>>", lambda _e: self.refresh_context())

    def _build_preparation(self, frame):
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        panes = ttk.Panedwindow(frame, orient="horizontal")
        panes.grid(row=0, column=0, sticky="nsew")
        controls, workspace = ttk.Frame(panes, width=375), ttk.Frame(panes)
        panes.add(controls, weight=0)
        panes.add(workspace, weight=1)
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(1, weight=1)
        self.sidebar = self._scroll_panel(controls)
        self._files_panel()
        ttk.Label(self.sidebar, text="Normalization is display-only. Smoothing is a view preview here.\n"
                  "Analysis uses the recorded processing recipe for the selected dataset.", wraplength=320).pack(fill="x", pady=8)
        self.file_table.bind("<<TreeviewSelect>>", self.select_table_dataset)
        self._workspace(workspace)
        region_bar = ttk.Frame(frame, padding=8)
        region_bar.grid(row=1, column=0, sticky="ew")
        for col, (label, var) in enumerate((("Peak name", self.region_name), ("From °C", self.region_low), ("To °C", self.region_high))):
            ttk.Label(region_bar, text=label).grid(row=0, column=col * 2, padx=4)
            ttk.Entry(region_bar, textvariable=var, width=14 if col == 0 else 9).grid(row=0, column=col * 2 + 1)
        ttk.Button(region_bar, text="Add peak", command=self.add_region).grid(row=0, column=6, padx=5)
        ttk.Button(region_bar, text="Update peak", command=self.update_region).grid(row=0, column=7, padx=5)
        ttk.Button(region_bar, text="Drag interval", command=self.select_region_on_plot).grid(row=0, column=8, padx=5)
        self.region_table = ttk.Treeview(frame, columns=("peak", "lower", "upper"), show="headings", height=3)
        for name, label in (("peak", "Named peak"), ("lower", "From °C"), ("upper", "To °C")):
            self.region_table.heading(name, text=label)
        self.region_table.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.region_table.bind("<<TreeviewSelect>>", self.select_table_region)

    def _build_modeling(self, frame):
        ttk.Label(frame, text="Explore candidate models and conditional Monte Carlo", font=("Segoe UI", 14, "bold"), padding=16).pack(anchor="w")
        ttk.Label(frame, text="Zero, first, second and fitted fractional order. Rankings do not prove a unique mechanism.", padding=16).pack(anchor="w")
        self.explorer_button = ttk.Button(frame, text="Open model comparison / Monte Carlo…", command=self._open_explorer)
        self.explorer_button.pack(anchor="w", padx=16)

    def _build_kinetic(self, frame):
        panes = ttk.Panedwindow(frame, orient="horizontal")
        panes.pack(fill="both", expand=True)
        controls, workspace = ttk.Frame(panes, width=330), ttk.Frame(panes)
        panes.add(controls, weight=0)
        panes.add(workspace, weight=1)
        sidebar = self._scroll_panel(controls)
        ttk.Label(sidebar, text="Analysis method", style="Section.TLabel").pack(anchor="w")
        selector = ttk.Combobox(sidebar, textvariable=self.method, values=METHODS, state="readonly", width=24)
        selector.pack(fill="x", pady=8)
        selector.bind("<<ComboboxSelected>>", lambda _e: self.refresh_method())
        self.method_panels = {}
        fields = {METHODS[0]: [("lower", "Leading edge from °C"), ("upper", "Leading edge to °C")],
                  METHODS[1]: [("beta", "Heating rate (K/s)"), ("prefactor", "Assumed prefactor (s⁻¹)")],
                  METHODS[2]: [("beta", "Heating rate (K/s)"), ("energy", "Initial energy (eV)"),
                               ("prefactor", "Initial prefactor (s⁻¹)"), ("order", "Fixed / initial order"),
                               ("max_nfev", "Maximum evaluations")]}
        help_text = {METHODS[0]: "Apparent slope energy requires a suitable rate signal and approximately unchanged coverage. It is not a zero-order assignment.",
                     METHODS[1]: "Classical first-order Redhead estimate with an assumed prefactor and linear ramp. No measured confidence interval is inferred.",
                     METHODS[2]: "Single-state linear-ramp fit; normalized initial coverage is one. Energy/prefactor may be non-identifiable. Bounds and solver follow the existing engine."}
        for method in METHODS:
            panel = ttk.Frame(sidebar)
            self.method_panels[method] = panel
            for key, label in fields[method]:
                ttk.Label(panel, text=label).pack(anchor="w", pady=(6, 0))
                ttk.Entry(panel, textvariable=self.method_values[key]).pack(fill="x")
            if method == METHODS[2]:
                ttk.Checkbutton(panel, text="Fit order (0.2–3)", variable=self.method_flags["free_order"]).pack(anchor="w", pady=5)
                ttk.Checkbutton(panel, text="Fit constant baseline", variable=self.method_flags["fit_baseline"]).pack(anchor="w")
            ttk.Label(panel, text=help_text[method], wraplength=280, padding=(0, 12)).pack(fill="x")
        self.method_action_frame = ttk.Frame(sidebar)
        self.method_action_frame.pack(fill="x", side="bottom")
        self.result_title = ttk.Label(workspace, text="Results · select a dataset and peak", padding=8)
        self.result_title.pack(fill="x")
        self.result_figure = Figure(figsize=(8, 5), constrained_layout=True)
        self.result_canvas = FigureCanvasTkAgg(self.result_figure, master=workspace)
        self.result_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.result_text = tk.Text(workspace, height=7, wrap="word", font=("Segoe UI", 10), padx=12, pady=8)
        self.result_text.pack(fill="x")
        self.refresh_method()

    def _load_paths(self, paths):
        super()._load_paths(paths)
        for row in self.spectra.values():
            self.project.add_dataset(row["path"], row["spec"])
        self.refresh_context()

    def refresh_context(self):
        if not hasattr(self, "region_table"):
            return
        self.dataset_ids = list(self.project.datasets)
        self.dataset_combo.configure(values=[f"{Path(self.project.datasets[i].path).name} [{i[:6]}]" for i in self.dataset_ids])
        if self.project.active_dataset in self.dataset_ids:
            self.dataset_combo.current(self.dataset_ids.index(self.project.active_dataset))
        self.region_ids = [r.id for r in self.project.regions.values() if r.dataset_id == self.project.active_dataset]
        self.region_combo.configure(values=[self.project.regions[i].label for i in self.region_ids])
        self.region_table.delete(*self.region_table.get_children())
        for ident in self.region_ids:
            region = self.project.regions[ident]
            self.region_table.insert("", "end", iid=ident, values=(region.label, region.lower, region.upper))
        if self.project.active_region in self.region_ids:
            self.region_combo.current(self.region_ids.index(self.project.active_region))
            dataset, region = self.project.context()
            self.region_name.set(region.label)
            self.region_low.set(f"{region.lower:g}")
            self.region_high.set(f"{region.upper:g}")
            self.context_label.configure(text=f"{Path(dataset.path).name} / {region.label} / {region.lower:g}–{region.upper:g} °C")
        else:
            self.region_choice.set("")
            self.context_label.configure(text="Define a named peak using numeric bounds or drag an interval.")
        self.refresh_method()
        self._draw_plot()

    def select_dataset(self, _event=None):
        index = self.dataset_combo.current()
        if index >= 0:
            self.project.select_dataset(self.dataset_ids[index])
            self.refresh_context()

    def select_region(self, _event=None):
        index = self.region_combo.current()
        if index >= 0:
            self.project.active_region = self.region_ids[index]
            self.refresh_context()

    def select_table_dataset(self, _event=None):
        selected = self.file_table.selection()
        if selected:
            item = next((d for d in self.project.datasets.values() if d.path == selected[0]), None)
            if item:
                self.project.select_dataset(item.id)
                self.refresh_context()

    def select_table_region(self, _event=None):
        selected = self.region_table.selection()
        if selected and selected[0] != self.project.active_region:
            self.project.active_region = selected[0]
            self.refresh_context()

    def add_region(self):
        try:
            self.project.add_region(self.region_name.get(), self.region_low.get(), self.region_high.get())
            self.refresh_context()
        except ValueError as exc:
            messagebox.showerror("Invalid peak", str(exc), parent=self.root)

    def update_region(self):
        try:
            self.project.context()
            self.project.update_region(self.project.active_region, self.region_name.get(), self.region_low.get(), self.region_high.get())
            self.refresh_context()
        except ValueError as exc:
            messagebox.showerror("Invalid peak", str(exc), parent=self.root)

    def select_region_on_plot(self):
        if self.x_mode.get() != "Temperature" or not self.project.active_dataset:
            messagebox.showinfo("Select a spectrum", "Select an imported spectrum and the temperature axis first.", parent=self.root)
            return
        if self.nav_toolbar.mode:
            messagebox.showinfo("Disable navigation", "Disable plot pan/zoom before selecting a peak.", parent=self.root)
            return
        self._stop_span()
        def selected(a, b):
            self.region_low.set(f"{min(a, b):.3f}")
            self.region_high.set(f"{max(a, b):.3f}")
            self.status.set("Interval selected. Choose Add peak or Update peak to retain it.")
        self._span_selector = SpanSelector(self.axis, selected, "horizontal", interactive=True,
                                           props={"facecolor": "teal", "alpha": .18})

    def refresh_method(self):
        if not hasattr(self, "method_panels"):
            return
        for name, panel in self.method_panels.items():
            panel.pack_forget()
        self.method_panels[self.method.get()].pack(fill="x")
        self.restoring = True
        try:
            dataset, region = self.project.context()
            settings = self.project.method_settings(self.method.get())
            for key, var in self.method_values.items():
                var.set(str(settings[key]))
            for key, var in self.method_flags.items():
                var.set(settings[key])
            self.result_title.configure(text=f"Results for {Path(dataset.path).name} / {region.label} / {self.method.get()}")
        except ValueError:
            self.result_title.configure(text="Results · select a dataset and peak")
        finally:
            self.restoring = False
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", "Not calculated for this selection.")
        self.result_text.configure(state="disabled")

    def _draw_plot(self):
        super()._draw_plot()
        if not hasattr(self, "figure"):
            return
        for axis in self.figure.axes:
            for patch in list(axis.patches):
                patch.remove()
        if self.x_mode.get() == "Temperature" and self.project.active_region in self.project.regions:
            region = self.project.regions[self.project.active_region]
            self.axis.axvspan(region.lower, region.upper, color="teal", alpha=.12, label=region.label)
        self.canvas.draw_idle()

    def open_classic(self):
        if self.classic and self.classic.root.winfo_exists():
            self.classic.root.lift()
            return
        self.classic = TpdSpectraApp(tk.Toplevel(self.root))
        self.classic._load_paths([Path(d.path) for d in self.project.datasets.values()])


def main():
    set_windows_app_identity()
    root = tk.Tk()
    WorkflowApp(root)
    root.mainloop()
    return 0
