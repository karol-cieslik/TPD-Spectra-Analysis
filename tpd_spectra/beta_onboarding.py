"""Curated example browser and parameter hints for the desktop beta."""
import json
import tkinter as tk
from tkinter import ttk
import webbrowser
from .beta_resources import resource


class ExampleDialog:
    """Two clearly separated sources with visible provenance before loading."""

    def __init__(self, app, section="synthetic"):
        self.app = app
        self.catalog = json.loads(resource('examples/beta_collection/catalog.json').read_text(encoding='utf-8'))
        self.publication_catalog = json.loads(resource('examples/publication_data/catalog.json').read_text(encoding='utf-8'))
        self.win = tk.Toplevel(app.root)
        self.win.title("Example library · TPD Spectra Studio")
        self.win.transient(app.root)
        width = min(900, self.win.winfo_screenwidth() - 48)
        height = min(660, self.win.winfo_screenheight() - 96)
        self.win.geometry(f"{width}x{height}")
        self.win.minsize(min(540, width), min(430, height))
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(2, weight=1)
        ttk.Label(self.win, text="Explore example spectra",
                  font=('Segoe UI', 15, 'bold'), padding=(16, 12, 16, 4)).grid(
                      row=0, column=0, sticky='w')
        ttk.Label(self.win, text="Simulations have known model inputs. Published data are experimental curves digitized from figures or taken from deposited measurements; neither establishes kinetic-model validity.",
                  wraplength=830, padding=(16, 0, 16, 10)).grid(row=1, column=0, sticky='ew')
        self.tabs = ttk.Notebook(self.win)
        self.tabs.grid(row=2, column=0, sticky='nsew', padx=14)
        self.trees = {}
        self._add_section('synthetic', f"Simulated ({len(self.catalog)})", self.catalog)
        self._add_section('publication', f"Publication-derived ({len(self.publication_catalog)})", self.publication_catalog)
        info = ttk.LabelFrame(self.win, text="What is this dataset?")
        info.grid(row=3, column=0, sticky='ew', padx=14, pady=(9, 2))
        info.columnconfigure(0, weight=1)
        self.details = tk.Text(info, height=7, wrap='word', font=('Segoe UI', 9),
                               relief='flat', background='#f8fafc', padx=10, pady=7,
                               takefocus=False)
        self.details.grid(row=0, column=0, sticky='ew')
        self.details.configure(state='disabled')
        buttons = ttk.Frame(self.win, padding=(14, 8, 14, 12))
        buttons.grid(row=4, column=0, sticky='ew')
        self.description = tk.StringVar(self.win)
        ttk.Label(buttons, textvariable=self.description).pack(side='left', fill='x', expand=True)
        ttk.Button(buttons, text="Open paper / DOI", command=self.open_source).pack(side='right', padx=(8, 0))
        ttk.Button(buttons, text="Open selected spectrum", command=self.open).pack(side='right')
        self.tabs.bind("<<NotebookTabChanged>>", self.describe)
        self.tabs.select(1 if section == 'publication' else 0)
        for kind, default in (('synthetic', 1), ('publication', 0)):
            tree = self.trees[kind]
            item = str(min(default, len(tree.get_children()) - 1))
            if tree.exists(item):
                tree.selection_set(item)
                tree.focus(item)
        self.describe()

    def _add_section(self, kind, title, rows):
        frame = ttk.Frame(self.tabs, padding=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.tabs.add(frame, text=title)
        tree = ttk.Treeview(frame, columns=('name', 'source'), show='headings',
                            selectmode='browse', height=10)
        tree.heading('name', text='Spectrum')
        tree.heading('source', text='Source / category')
        tree.column('name', width=325, minwidth=160)
        tree.column('source', width=460, minwidth=180)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        for i, row in enumerate(rows):
            tree.insert('', 'end', iid=str(i), values=(
                row['title'],
                row.get('short_source', 'Synthetic · known ground truth')))
        tree.bind('<<TreeviewSelect>>', self.describe)
        tree.bind('<Double-1>', lambda _event: self.open())
        self.trees[kind] = tree

    def selected(self):
        kind = 'publication' if self.tabs.index(self.tabs.select()) == 1 else 'synthetic'
        tree = self.trees[kind]
        selection = tree.selection()
        if not selection:
            return kind, None
        row = (self.publication_catalog if kind == 'publication' else self.catalog)[int(selection[0])]
        return kind, row

    def describe(self, _event=None):
        kind, row = self.selected()
        if not row:
            return
        if kind == 'synthetic':
            info = (f"SIMULATED · {row['title']}\n\n{row['description']}\n"
                    f"Heating rate: {row['beta_K_s']:g} K/s · Polanyi–Wigner model example.\n"
                    "Artificial data with known generating assumptions. Not a literature measurement.")
        else:
            info = (f"PUBLICATION-DERIVED · {row['title']}\n"
                    f"{row['citation']}\nDOI: {row['doi']} · {row['figure']}\n"
                    f"Heating: {row['heating_note']} · Original signal: {row['signal_units']}\n"
                    f"Reuse: {row['license']} · {row['description']}\n"
                    f"LIMITATION: {row['limitations']}\n"
                    "Source temperatures in kelvin are converted to °C for this GUI. "
                    "For figure digitizations, the CSV time coordinate is constructed from the cited nominal ramp, NOT measured time.")
        self.details.configure(state='normal')
        self.details.delete('1.0', 'end')
        self.details.insert('1.0', info)
        self.details.configure(state='disabled')
        self.description.set("Read the provenance and fit assumptions before interpreting a result." if kind == 'publication'
                             else "Select an example, then explore the model settings.")

    def open_source(self):
        kind, row = self.selected()
        if kind != 'publication' or not row:
            self.description.set("Simulations have no publication DOI.")
            return
        url = 'https://doi.org/' + row['doi']
        webbrowser.open(url)

    def open(self):
        if self.app.job_busy:
            self.description.set("Finish or cancel the calculation before loading an example.")
            return
        kind, row = self.selected()
        if not row:
            return
        try:
            folder = 'examples/publication_data/' if kind == 'publication' else 'examples/beta_collection/'
            path = resource(folder + row['file'])
            self.app._load_paths([path])
            dataset = next(d for d in self.app.project.datasets.values() if d.path == str(path.resolve()))
            self.app.project.select_dataset(dataset.id)
            if kind == 'publication':
                if not any(r.dataset_id == dataset.id for r in self.app.project.regions.values()):
                    lo, hi = row['region_K']
                    self.app.project.add_region(row['peak_label'], lo - 273.15, hi - 273.15)
                if row['beta_K_s'] is not None:
                    for method in ('Leading edge', 'Redhead', 'Polanyi–Wigner'):
                        self.app.project.method_settings(method)['beta'] = row['beta_K_s']
                note = ("Published data opened, not a known-ground-truth validation. "
                        + row['limitations'] + " Review the source, region, baseline and heating rate.")
            else:
                meta = json.loads(resource(folder + row['metadata']).read_text(encoding='utf-8'))
                if not any(r.dataset_id == dataset.id for r in self.app.project.regions.values()):
                    self.app.project.add_region('Synthetic example — full trace', *meta['recommended_peak_c'])
                for method in ('Leading edge', 'Redhead', 'Polanyi–Wigner'):
                    self.app.project.method_settings(method)['beta'] = meta['beta_K_s']
                region = self.app.project.context()[1]
                self.app.project.method_settings('Leading edge').update(
                    lower=region.lower, upper=region.upper)
                self.app.project.method_settings('Polanyi–Wigner').update(energy=1.2, prefactor=1e13)
                key = f'{dataset.id}/{self.app.project.active_region}'
                from .workflow_modeling import DEFAULTS
                session = self.app.project.modeling.setdefault(key, {'settings': dict(DEFAULTS)})
                session['settings']['beta'] = str(meta['beta_K_s'])
                session['settings']['energy'] = '1.2'
                note = ("Synthetic example opened. Known simulation settings loaded; "
                        "inspect the region and model assumptions.")
            self.app.method.set('Redhead')
            self.app.refresh_context()
            self.app.status.set(note)
            self.win.destroy()
        except Exception as exc:
            self.app.diagnostic_log.record('Example unavailable', str(exc), exc)
            self.description.set("Could not open this example; check the dataset and package contents.")


class Tooltip:
    def __init__(self,widget,text):
        self.widget,self.text,self.win,self.pending=widget,text,None,None
        widget.bind('<Enter>',self.enter,add='+')
        widget.bind('<Leave>',self.hide,add='+')
        widget.bind('<Destroy>',self.hide,add='+')

    def enter(self,_event=None):
        self.pending=self.widget.after(600,self.show)

    def show(self):
        self.pending=None
        if not self.widget.winfo_exists():
            return
        self.win=tk.Toplevel(self.widget)
        self.win.overrideredirect(True)
        self.win.geometry(f'+{self.widget.winfo_rootx()+10}+{self.widget.winfo_rooty()+self.widget.winfo_height()+4}')
        ttk.Label(self.win,text=self.text,wraplength=320,padding=8).pack()

    def hide(self,_event=None):
        if self.pending:
            self.widget.after_cancel(self.pending)
            self.pending=None
        if self.win:
            self.win.destroy()
            self.win=None