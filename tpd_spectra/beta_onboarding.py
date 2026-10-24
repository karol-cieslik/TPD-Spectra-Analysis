"""Small optional example chooser and parameter hints, not a setup wizard."""
import json
import tkinter as tk
from tkinter import ttk
from .beta_resources import resource


class ExampleDialog:
    def __init__(self,app):
        self.app=app
        self.catalog=json.loads(resource('examples/beta_collection/catalog.json').read_text(encoding='utf-8'))
        self.win=tk.Toplevel(app.root)
        self.win.title('Open Example Dataset — synthetic simulations')
        self.win.geometry('760x520')
        ttk.Label(self.win,text='Synthetic Polanyi–Wigner examples',font=('Segoe UI',14,'bold'),padding=12).pack(anchor='w')
        ttk.Label(self.win,text='No experimental measurements are included. Start with the clean first-order example.\nEach CSV has a JSON file recording ground truth, noise, baseline and limitations.',wraplength=710,padding=12).pack(fill='x')
        self.list=tk.Listbox(self.win,exportselection=False,font=('Segoe UI',10))
        self.list.pack(fill='both',expand=True,padx=12)
        for row in self.catalog:
            self.list.insert('end',row['title'])
        self.description=tk.StringVar(self.win)
        ttk.Label(self.win,textvariable=self.description,wraplength=710,padding=12).pack(fill='x')
        self.list.bind('<<ListboxSelect>>',self.describe)
        self.list.selection_set(1)
        self.describe()
        ttk.Button(self.win,text='Open selected example',command=self.open).pack(anchor='e',padx=12,pady=12)

    def describe(self,_event=None):
        if self.list.curselection():
            row=self.catalog[self.list.curselection()[0]]
            self.description.set(row['description']+f" Heating rate: {row['beta_K_s']:g} K/s.")

    def open(self):
        if self.app.job_busy:
            self.description.set('Finish or cancel the calculation before loading an example.')
            return
        if not self.list.curselection():
            return
        row=self.catalog[self.list.curselection()[0]]
        try:
            path=resource('examples/beta_collection/'+row['file'])
            meta=json.loads(resource('examples/beta_collection/'+row['metadata']).read_text(encoding='utf-8'))
            self.app._load_paths([path])
            dataset=next(d for d in self.app.project.datasets.values() if d.path==str(path.resolve()))
            self.app.project.select_dataset(dataset.id)
            if self.app.project.active_region is None:
                self.app.project.add_region('Synthetic example — full trace',*meta['recommended_peak_c'])
            for method in ('Leading edge','Redhead','Polanyi–Wigner'):
                self.app.project.method_settings(method)['beta']=meta['beta_K_s']
            self.app.project.method_settings('Leading edge').update(lower=90.,upper=110.)
            self.app.project.method_settings('Polanyi–Wigner').update(energy=1.2,prefactor=1e13)
            key=f'{dataset.id}/{self.app.project.active_region}'
            from .workflow_modeling import DEFAULTS
            session=self.app.project.modeling.setdefault(key,{'settings':dict(DEFAULTS)})
            session['settings']['beta']=str(meta['beta_K_s'])
            session['settings']['energy']='1.2'
            self.app.method.set('Redhead')
            self.app.refresh_context()
            self.app.status.set('Synthetic example opened. Heating rate loaded from its metadata; inspect the selected interval and method assumptions before interpreting results.')
            self.win.destroy()
        except Exception as exc:
            self.app.diagnostic_log.record('Example unavailable',str(exc),exc)
            self.description.set('Could not open this example. Extract the complete beta ZIP or use Open Spectrum to import its CSV manually.')


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
