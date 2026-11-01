"""Three-stage desktop workflow; the classic workspace remains available."""
from pathlib import Path
import json
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector

from .gui import TpdSpectraApp
from .branding import NAVY, brand_image, set_windows_app_identity
from .workflow_state import WorkflowProject, METHODS, STAGES
from .workflow_results_gui import ResultsMixin
from .workflow_analysis import processed_signal
from .workflow_modeling import ModelingPanel
from .workflow_project_gui import ProjectMixin
from .beta_onboarding import ExampleDialog, Tooltip
from .beta_resources import resource
from .scientific_help import ScientificHelpDialog, help_button
from .quickstart_dialog import QuickStartDialog
from . import __version__
from .equation_help import EquationCard


class WorkflowApp(ProjectMixin, ResultsMixin, TpdSpectraApp):
    def __init__(self, root):
        self.project = WorkflowProject()
        self.restoring = False
        self.classic = None
        self.scientific_help_dialog = None
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
        self.setup_results()
        self.setup_project_actions()

    def open_default_demo(self):
        """Explicit startup action, also usable from a source or frozen build."""
        try:
            self._load_paths([resource('examples/synthetic_two_peak_demo.csv')])
            self.status.set('Bundled synthetic demo: first peak selected. Open Modeling to simulate or compare models; the second peak needs a separate hypothesis.')
        except (OSError, ValueError) as exc:
            self.status.set(f'Demo unavailable: {exc}. Use Open Example Dataset or Open Spectrum.')

    def open_scientific_help(self, topic_id=None):
        """Open or reuse the non-modal, read-only parameter reference."""
        dialog = self.scientific_help_dialog
        if dialog is not None and dialog.window.winfo_exists():
            dialog.select_topic(topic_id)
            return dialog
        try:
            dialog = ScientificHelpDialog(self, topic_id)
            self.scientific_help_dialog = dialog
            return dialog
        except (OSError, ValueError) as exc:
            self.status.set(f'Scientific Help unavailable: {exc}')
            messagebox.showwarning('Scientific Help unavailable',
                                   'The Help reference could not be loaded. Extract the full beta ZIP.\n\n' + str(exc),
                                   parent=self.root)
            return None

    def _build(self):
        # Scientific desktop tools keep infrequent commands in a discoverable
        # menu and reserve the working surface for spectra and analysis.
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Open spectrum…", accelerator="Ctrl+O", command=self._import_files)
        file_menu.add_command(label="Add folder…", command=self._import_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Open project…", command=self.open_project)
        file_menu.add_command(label="Save project…", accelerator="Ctrl+S", command=self.save_project)
        file_menu.add_command(label="Report / Export…", command=self.report_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu.add_cascade(label="File", menu=file_menu)
        examples_menu = tk.Menu(menu, tearoff=False)
        examples_menu.add_command(label="Browse example library…", command=self.open_example)
        examples_menu.add_command(label="Simulated spectra…", command=lambda: self.open_example("synthetic"))
        examples_menu.add_command(label="Publication-derived spectra…", command=lambda: self.open_example("publication"))
        menu.add_cascade(label="Examples", menu=examples_menu)
        view_menu = tk.Menu(menu, tearoff=False)
        view_menu.add_command(label="Classic / batch workspace", command=self.open_classic)
        menu.add_cascade(label="View", menu=view_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Quick start", accelerator="F1", command=self.workflow_help)
        help_menu.add_command(label="Scientific Help / Parameters", command=self.open_scientific_help)
        help_menu.add_command(label="Worked examples", command=self.open_worked_examples)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Report a bug / Send feedback", command=self._show_feedback)
        menu.add_cascade(label="Help", menu=help_menu)
        self.root.configure(menu=menu)
        self.root.bind("<Control-o>", lambda _e: self._import_files())
        self.root.bind("<Control-s>", lambda _e: self.save_project())
        self.root.bind("<F1>", lambda _e: self.workflow_help())

        header = tk.Frame(self.root, bg=NAVY, padx=12, pady=5)
        header.pack(fill="x")
        self.brand_mark = brand_image(header, 38)
        tk.Label(header, image=self.brand_mark, bg=NAVY).pack(side="left", padx=(0, 10))
        ttk.Label(header, text="TPD Spectra Studio", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text=f"EXTERNAL BETA  {__version__}", style="Subtitle.TLabel").pack(side="right")
        actions = ttk.Frame(self.root, padding=(10, 7, 10, 8))
        actions.pack(fill="x")
        ttk.Button(actions, text="Open spectrum…", command=self._import_files).pack(side="left")
        ttk.Button(actions, text="Browse examples…", command=self.open_example).pack(side="left", padx=7)
        self.project_actions = ttk.Frame(actions)
        self.project_actions.pack(side="right")
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
        self.example_source_note = ttk.Label(context, text="", wraplength=1100)
        self.example_source_note.grid(row=2, column=0, columnspan=4, sticky="w")
        self.example_source_note.grid_remove()
        try:
            rows = json.loads(resource('examples/publication_data/catalog.json').read_text(encoding='utf-8'))
        except (FileNotFoundError, OSError, ValueError):
            rows = []
        self.published_examples = {row['file']: row for row in rows}
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
        self.processing_baseline = tk.StringVar(self.root, value='0')
        baseline_row = ttk.Frame(self.sidebar)
        baseline_row.pack(fill='x')
        ttk.Label(baseline_row, text='Subtract constant baseline (signal units)').pack(side='left')
        help_button(baseline_row,self,'constant_baseline').pack(side='right')
        ttk.Entry(self.sidebar, textvariable=self.processing_baseline).pack(fill='x')
        ttk.Button(self.sidebar, text='Apply smoothing / baseline to analysis', command=self.apply_processing).pack(fill='x', pady=4)
        help_button(self.sidebar,self,'smoothing').pack(anchor='e')
        ttk.Button(self.sidebar, text='Undo processing', command=self.undo_processing).pack(fill='x')
        ttk.Button(self.sidebar, text='Reset processing to raw signal', command=self.reset_processing).pack(fill='x', pady=4)
        self.processing_label = ttk.Label(self.sidebar, text='Analysis recipe: raw signal', wraplength=320)
        self.processing_label.pack(fill='x')
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
        help_button(region_bar,self,'peak_interval').grid(row=0,column=9,padx=3)
        self.region_table = ttk.Treeview(frame, columns=("peak", "lower", "upper"), show="headings", height=3)
        for name, label in (("peak", "Named peak"), ("lower", "From °C"), ("upper", "To °C")):
            self.region_table.heading(name, text=label)
        self.region_table.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.region_table.bind("<<TreeviewSelect>>", self.select_table_region)

    def _build_modeling(self, frame):
        self.modeling_panel = ModelingPanel(self, frame)

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
        self.method_equations = {}
        fields = {METHODS[0]: [("lower", "Leading edge from °C"), ("upper", "Leading edge to °C"), ("beta", "Heating rate (K/s; verify)")],
                  METHODS[1]: [("beta", "Heating rate (K/s)"), ("prefactor", "Assumed prefactor (s⁻¹)")],
                  METHODS[2]: [("beta", "Heating rate (K/s)"), ("energy", "Initial energy (eV)"),
                               ("prefactor", "Initial prefactor (s⁻¹)"), ("order", "Fixed / initial order"),
                               ("max_nfev", "Maximum evaluations")]}
        help_text = {METHODS[0]: "Apparent slope energy requires a suitable rate signal and approximately unchanged coverage. It is not a zero-order assignment.",
                     METHODS[1]: "Classical first-order Redhead estimate with an assumed prefactor and linear ramp. No measured confidence interval is inferred.",
                     METHODS[2]: "Single-state linear-ramp fit; normalized initial coverage is one. Energy/prefactor may be non-identifiable. Fixed zero order uses a depletion-edge search. Its prefactor/scale are representative values with conditional ranges, not unique estimates. Inspect residuals and assumptions."}
        for method in METHODS:
            panel = ttk.Frame(sidebar)
            self.method_panels[method] = panel
            equation = EquationCard(panel, method)
            equation.pack(fill='x', pady=(0, 8))
            self.method_equations[method] = equation
            method_topic = {METHODS[0]:'leading_edge',METHODS[1]:'redhead',
                            METHODS[2]:'polanyi_wigner_fit'}[method]
            help_button(panel,self,method_topic).pack(anchor='e')
            for key, label in fields[method]:
                label_row = ttk.Frame(panel)
                label_row.pack(fill='x',pady=(6,0))
                ttk.Label(label_row, text=label).pack(side='left')
                topic = {'lower':'peak_interval','upper':'peak_interval',
                         'beta':'heating_rate','energy':'initial_guess',
                         'prefactor':'prefactor','order':'reaction_order',
                         'max_nfev':'max_evaluations'}[key]
                help_button(label_row,self,topic).pack(side='right')
                entry=ttk.Entry(panel, textvariable=self.method_values[key])
                entry.pack(fill="x")
                Tooltip(entry,{'beta':'Linear heating rate in kelvin per second. Confirm acquisition conditions; it is not inferred automatically.',
                    'prefactor':'Arrhenius prefactor in s⁻¹ under normalized coverage. Redhead assumes it; full fitting optimizes it.',
                    'energy':'Initial optimizer guess in electronvolts; the result is shown separately.',
                    'order':'Fixed order unless Fit order is selected. A fitted order does not prove a mechanism.',
                    'max_nfev':'Maximum optimizer evaluations, not Monte Carlo replicates.',
                    'lower':'Leading-edge subinterval in degrees Celsius, inside the selected peak.',
                    'upper':'Use only the rising edge where coverage change is small, not the whole peak.'}[key])
            if method == METHODS[2]:
                ttk.Checkbutton(panel, text="Fit order (0.2–3)", variable=self.method_flags["free_order"]).pack(anchor="w", pady=5)
                ttk.Checkbutton(panel, text="Fit constant baseline", variable=self.method_flags["fit_baseline"]).pack(anchor="w")
                help_button(panel,self,'fixed_zero_order').pack(anchor='e')
            ttk.Label(panel, text=help_text[method], wraplength=280, padding=(0, 12)).pack(fill="x")
        self.method_action_frame = ttk.Frame(sidebar)
        self.method_action_frame.pack(fill="x", side="bottom")
        self.result_title = ttk.Label(workspace, text="Results · select a dataset and peak", padding=8)
        self.result_title.pack(fill="x")
        # A full-sized plot and an inspectable parameter table are different
        # reading tasks. Separate tabs avoid squeezing either below the other.
        self.result_views = ttk.Notebook(workspace)
        self.result_views.pack(fill="both", expand=True)
        plot_view, parameter_view, notes_view = (ttk.Frame(self.result_views) for _ in range(3))
        for view, title in ((plot_view, 'Spectrum & residuals'),
                            (parameter_view, 'Parameter summary'),
                            (notes_view, 'Assumptions & provenance')):
            self.result_views.add(view, text=title)
        self.result_figure = Figure(figsize=(8, 5), constrained_layout=True)
        self.result_canvas = FigureCanvasTkAgg(self.result_figure, master=plot_view)
        self.result_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.result_state = tk.StringVar(self.root, value='No result for this selection.')
        ttk.Label(parameter_view, textvariable=self.result_state, padding=(8, 8)).grid(
            row=0, column=0, columnspan=2, sticky='ew')
        ttk.Label(parameter_view,
                  text='Roles distinguish fitted parameters, assumed inputs, approximate estimates and diagnostics.',
                  wraplength=650, padding=(8, 0, 8, 8)).grid(row=1, column=0, columnspan=2, sticky='ew')
        parameter_view.rowconfigure(2, weight=1)
        parameter_view.columnconfigure(0, weight=1)
        columns = ('parameter', 'value', 'unit', 'role')
        self.result_table = ttk.Treeview(parameter_view, columns=columns, show='headings', height=8)
        for key, title, width in (("parameter", "Parameter", 240), ("value", "Value", 170),
                                  ("unit", "Unit", 75), ("role", "How obtained", 180)):
            self.result_table.heading(key, text=title)
            self.result_table.column(key, width=width, minwidth=65, stretch=(key != 'unit'))
        self.result_table.grid(row=2, column=0, sticky='nsew', padx=(8, 0))
        yscroll = ttk.Scrollbar(parameter_view, orient='vertical', command=self.result_table.yview)
        yscroll.grid(row=2, column=1, sticky='ns')
        self.result_table.configure(yscrollcommand=yscroll.set)
        xscroll = ttk.Scrollbar(parameter_view, orient='horizontal', command=self.result_table.xview)
        xscroll.grid(row=3, column=0, sticky='ew', padx=(8, 0))
        self.result_table.configure(xscrollcommand=xscroll.set)
        ttk.Button(parameter_view, text='Copy parameter summary', command=self.copy_result_summary).grid(
            row=4, column=0, sticky='w', padx=8, pady=8)
        help_button(parameter_view,self,'identifiability').grid(row=4,column=1,sticky='e',padx=8)
        notes_view.rowconfigure(0, weight=1)
        notes_view.columnconfigure(0, weight=1)
        # Keep this text widget for the legacy result status consumers.
        self.result_text = tk.Text(notes_view, height=9, wrap="word", font=("Segoe UI", 10), padx=12, pady=8)
        self.result_text.grid(row=0, column=0, sticky='nsew')
        notes_scroll = ttk.Scrollbar(notes_view, orient='vertical', command=self.result_text.yview)
        notes_scroll.grid(row=0, column=1, sticky='ns')
        self.result_text.configure(yscrollcommand=notes_scroll.set)
        self.refresh_method()

    def _load_paths(self, paths, preloaded=None):
        super()._load_paths(paths, preloaded=preloaded)
        for row in self.spectra.values():
            dataset = self.project.add_dataset(row["path"], row["spec"])
            # Seed only the actual shipped demo, never an arbitrary imported spectrum.
            try:
                bundled = resource('examples/synthetic_two_peak_demo.csv').resolve()
            except FileNotFoundError:
                bundled = None
            if Path(dataset.path) == bundled and not any(r.dataset_id == dataset.id for r in self.project.regions.values()):
                self.project.select_dataset(dataset.id)
                self.project.add_region('Demo — first peak (single-state approximation)', 70., 210.)
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
        dataset = self.project.datasets.get(self.project.active_dataset)
        source = (self.published_examples.get(Path(dataset.path).name)
                  if dataset is not None and Path(dataset.path).parent.name == 'publication_data' else None)
        if source:
            self.example_source_note.configure(
                text=f"Publication-derived · {source['short_source']} · {source['description']} · DOI {source['doi']}")
            self.example_source_note.grid()
        else:
            self.example_source_note.grid_remove()
        self.refresh_method()
        self.modeling_panel.restore()
        self._draw_plot()
        if self.project.active_dataset:
            self.processing_label.configure(text='Analysis recipe: ' + str(self.project.datasets[self.project.active_dataset].processing))

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
            self.status.set('Peak interval updated. Previous fits are retained but stale; re-run Compare models for the new range. Use Add peak to retain both peaks.')
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
        self._span_selector = SpanSelector(getattr(self,'_selected_plot_axis',self.axis), selected, "horizontal", interactive=True,
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
        if hasattr(self, 'jobs'):
            self.restore_result()
            self.schedule_preview()

    def apply_processing(self):
        try:
            self.project.set_processing({'smoothing': self.filter_method.get(), 'window': int(self.window.get()),
                                         'baseline': float(self.processing_baseline.get())})
            self.refresh_context()
        except (ValueError, KeyError, tk.TclError) as exc:
            self.status.set('Processing unavailable: ' + str(exc))

    def undo_processing(self):
        self.project.undo_processing()
        self.refresh_context()

    def reset_processing(self):
        if self.project.active_dataset:
            self.project.set_processing({'smoothing': 'none', 'window': 1, 'baseline': 0.0})
            self.refresh_context()

    def _draw_plot(self):
        previous_status = self.status.get() if hasattr(self,'status') else ''
        super()._draw_plot()
        if hasattr(self,'status'):
            if getattr(self,'job_busy',False):
                self.status.set(previous_status)
            else:
                self.status.set('Select a dataset and named peak, then explore models or choose one kinetic method. Save labeled results to build a report.')
        if not hasattr(self, "figure"):
            return
        for axis in self.figure.axes:
            for patch in list(axis.patches):
                patch.remove()
        selected_axis = self.axis
        visible = [key for key,row in self.spectra.items() if row['visible']]
        dataset = self.project.datasets.get(self.project.active_dataset)
        if dataset and self.view_mode.get() == 'Small multiples' and dataset.path in visible:
            selected_axis = self.figure.axes[visible.index(dataset.path)]
        self._selected_plot_axis = selected_axis
        if self.x_mode.get() == "Temperature" and self.project.active_region in self.project.regions and dataset and dataset.path in visible:
            region = self.project.regions[self.project.active_region]
            selected_axis.axvspan(region.lower, region.upper, color="teal", alpha=.12, label=region.label)
        if dataset and dataset.path in visible and self.x_mode.get() == 'Temperature':
            if dataset.processing != {'smoothing': 'none', 'window': 1, 'baseline': 0.0}:
                y = processed_signal(dataset)
                if self.normalize.get():
                    y = (y-y.min()) / max(float(y.max()-y.min()), 1e-15)
                selected_axis.plot(dataset.spectrum.temperature_clean_c, y, label='Selected analysis recipe', color='teal', linestyle='--')
                selected_axis.legend(fontsize=8)
        self.canvas.draw_idle()

    def open_classic(self):
        if getattr(self, 'job_busy', False):
            self.status.set('Finish or cancel the workflow calculation before opening the classic workspace.')
            return
        if self.classic and self.classic.root.winfo_exists():
            self.classic.root.lift()
            return
        self.classic = TpdSpectraApp(tk.Toplevel(self.root))
        self.classic._load_paths([Path(d.path) for d in self.project.datasets.values()])
        for key,row in self.classic.spectra.items():
            row['included'] = self.spectra[key]['included']
            self.classic.file_table.set(key,'included','✓' if row['included'] else '—')

    def _remove_selected(self):
        if getattr(self,'job_busy',False):
            self.status.set('Finish or cancel the active calculation before removing datasets.')
            return
        for path in self.file_table.selection():
            dataset = next((d for d in self.project.datasets.values() if d.path == path),None)
            if dataset is None:
                continue
            if any(r['snapshot']['dataset_id']==dataset.id for r in self.project.runs.values()):
                self.status.set('This dataset has saved runs. Delete those runs before removing it, or hide the trace.')
                continue
            self.project.regions = {k:r for k,r in self.project.regions.items() if r.dataset_id != dataset.id}
            for field in ('settings','current_results','modeling'):
                values=getattr(self.project,field)
                setattr(self.project,field,{k:v for k,v in values.items() if not k.startswith(dataset.id+'/')})
            self.project.processing_history.pop(dataset.id,None)
            del self.project.datasets[dataset.id]
            self.spectra.pop(path,None)
            self.file_table.delete(path)
        if self.project.active_dataset not in self.project.datasets:
            self.project.active_dataset=None
            self.project.active_region=None
            self.dataset_choice.set('')
            if self.project.datasets:
                self.project.select_dataset(next(iter(self.project.datasets)))
        self.refresh_context()

    def workflow_help(self):
        return QuickStartDialog(self)

    def open_worked_examples(self):
        """Open the full, self-contained offline tutorial in the default reader."""
        try:
            import webbrowser
            webbrowser.open(resource('docs/beta/WORKED_EXAMPLES.html').as_uri())
        except (OSError, ValueError) as exc:
            self.status.set('Worked examples unavailable: ' + str(exc))

    def open_example(self, section="synthetic"):
        try:
            return ExampleDialog(self, section=section)
        except Exception as exc:
            self.status.set(str(exc))

    def open_beta_guide(self):
        try:
            import webbrowser
            webbrowser.open(resource('docs/beta/QUICK_START.pdf').as_uri())
        except (OSError,ValueError) as exc:
            self.status.set(str(exc))


def main():
    set_windows_app_identity()
    root = tk.Tk()
    app = WorkflowApp(root)
    app.open_default_demo()
    root.mainloop()
    return 0
