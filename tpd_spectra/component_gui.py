"""Explicit physical hypotheses for simultaneous full-spectrum fitting."""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime,timezone
from importlib.metadata import version
import tkinter as tk
from tkinter import ttk, filedialog
from .workflow_analysis import processed_signal, serial
from .multicomponent import ComponentDefinition, fit_components, compare_component_counts, _definitions
from .component_export import draw_components, export_components
from .run_session import proposed_run_folder
from .scientific_help import help_button


def defaults():
    return dict(components=[asdict(ComponentDefinition('Component 1'))],fit_baseline=True,fit_drift=False)


class ComponentsController:
    def __init__(self,panel):
        self.panel=panel
        self.app=panel.app
        self.window=None

    def settings(self):
        return self.panel.session().setdefault('component_settings',defaults())

    def snapshot(self):
        snap=self.panel.snapshot()
        dataset,_=self.app.project.context()
        snap['method']='Simultaneous Polanyi–Wigner components'
        snap['component_engine_revision']='fixed-kinetics-v1'
        snap['selected_named_region']=snap['region']
        t=dataset.spectrum.temperature_clean_c
        snap['region']=[float(t[0]),float(t[-1])]
        snap['scope']='Entire selected spectrum; named regions do not crop this fit'
        snap['settings']={key:snap['settings'][key] for key in ('beta','max_nfev','multistart')}
        snap['component_settings']=deepcopy(self.settings())
        return snap

    def current(self,record):
        try:
            return self.app.project.fingerprint(record['snapshot'])==self.app.project.fingerprint(self.snapshot())
        except (ValueError,KeyError):
            return False

    def open(self):
        try:
            self.app.project.context()
        except ValueError as exc:
            self.app.status.set(str(exc))
            return
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return
        self.editor_key=self.panel.key()
        self.window=tk.Toplevel(self.app.root)
        self.window.title('Simultaneous kinetic components — full spectrum')
        self.window.geometry('1040x600')
        self.window.minsize(860,560)
        self.window.rowconfigure(0,weight=1)
        self.window.columnconfigure(0,weight=1)
        self.editor_canvas=tk.Canvas(self.window,highlightthickness=0,xscrollincrement=20,yscrollincrement=20)
        self.editor_canvas.grid(row=0,column=0,sticky='nsew')
        self.editor_vertical=ttk.Scrollbar(self.window,orient='vertical',command=self.editor_canvas.yview)
        self.editor_vertical.grid(row=0,column=1,sticky='ns')
        self.editor_horizontal=ttk.Scrollbar(self.window,orient='horizontal',command=self.editor_canvas.xview)
        self.editor_horizontal.grid(row=1,column=0,sticky='ew')
        self.editor_canvas.configure(xscrollcommand=self.editor_horizontal.set,yscrollcommand=self.editor_vertical.set)
        body=ttk.Frame(self.editor_canvas,padding=12)
        embedded=self.editor_canvas.create_window((0,0),window=body,anchor='nw')
        def resize_canvas(event):
            self.editor_canvas.itemconfigure(embedded,width=max(event.width,body.winfo_reqwidth()))
        self.editor_canvas.bind('<Configure>',resize_canvas)
        self.window.bind('<MouseWheel>',lambda e:self.editor_canvas.yview_scroll(-int(e.delta/120),'units'))
        self.window.bind('<Shift-MouseWheel>',lambda e:self.editor_canvas.xview_scroll(-int(e.delta/120),'units'))
        ttk.Label(body,text='Fit the full spectrum as a sum of independent Polanyi–Wigner rates.',font=('Segoe UI',12,'bold')).pack(anchor='w')
        help_button(body,self.app,'simultaneous_components').pack(anchor='e')
        ttk.Label(body,text='Energies and nonnegative detector scales are optimized together. Order, prefactor and initial coverage are fixed assumptions.\n'
            'Use normalized dimensionless coverage (prefactor in s⁻¹ under that convention). Zero order uses the separate single-state method.\n'
            'Three visible features do not establish three physical states. Named regions do not crop this calculation.',
            wraplength=980).pack(fill='x',pady=8)
        settings=deepcopy(self.settings())
        self.rows=[]
        row_options=ttk.Frame(body)
        row_options.pack(fill='x')
        self.rows_frame=ttk.Frame(body)
        self.rows_frame.pack(fill='x',pady=8)
        for i,(title,topic) in enumerate(zip(
                ('Component name','Fixed n (>0)','Initial E (eV)','Fixed ν (s⁻¹)','Fixed θ₀','Min E','Max E'),
                ('simultaneous_components','reaction_order','initial_guess','prefactor',
                 'initial_coverage','energy_bounds','energy_bounds'))):
            header=ttk.Frame(self.rows_frame)
            header.grid(row=0,column=i,padx=3,sticky='w')
            ttk.Label(header,text=title).pack(side='left')
            help_button(header,self.app,topic).pack(side='left',padx=(3,0))
        for definition in settings['components']:
            self.add_row(definition)
        ttk.Button(row_options,text='Add component (up to 3)',command=self.add_row).pack(side='left')
        ttk.Button(row_options,text='Remove last component',command=self.remove_row).pack(side='left',padx=6)
        self.fit_baseline=tk.BooleanVar(self.window,value=settings['fit_baseline'])
        self.fit_drift=tk.BooleanVar(self.window,value=settings['fit_drift'])
        for label,variable,topic in (
                ('Fit shared constant offset',self.fit_baseline,'constant_baseline'),
                ('Fit shared linear baseline drift (requires offset)',self.fit_drift,'baseline_drift')):
            option=ttk.Frame(body)
            option.pack(fill='x')
            ttk.Checkbutton(option,text=label,variable=variable).pack(side='left')
            help_button(option,self.app,topic).pack(side='left',padx=4)
        ttk.Label(body,text='Heating rate, maximum evaluations and deterministic multistart come from Modeling.\n'
            'Count comparison uses the first 1, 2, … defined components on identical full-spectrum observations.\n'
            'Review local optima, correlations, residuals and fixed assumptions. Local intervals may be withheld; component Monte Carlo is not implemented.',
            wraplength=980).pack(fill='x',pady=8)
        help_button(body,self.app,'component_count').pack(anchor='e')
        footer=ttk.Frame(self.window,padding=8)
        footer.grid(row=2,column=0,columnspan=2,sticky='ew')
        buttons=ttk.Frame(footer)
        buttons.pack(fill='x',pady=8)
        for index,(text,command) in enumerate((('Apply definitions',self.apply),('Fit components together',lambda:self.apply_and_run(False)),
                ('Compare component counts',lambda:self.apply_and_run(True)),('Show stored fit',self.show),('Export component fit…',self.export),
                ('Cancel calculation',self.panel.cancel_job))):
            buttons.columnconfigure(index%3,weight=1)
            ttk.Button(buttons,text=text,command=command).grid(row=index//3,column=index%3,padx=3,pady=3,sticky='ew')
        self.message=tk.StringVar(self.window,value='Define physical hypotheses, then fit. Results and warnings appear in Modeling.')
        message_label=ttk.Label(footer,textvariable=self.message,wraplength=980)
        message_label.pack(fill='x',pady=4)
        footer.bind('<Configure>',lambda e:message_label.configure(wraplength=max(300,e.width-16)))
        def resize_help(event):
            for child in body.winfo_children():
                if isinstance(child,ttk.Label) and str(child.cget('wraplength')).strip() not in ('','0'):
                    child.configure(wraplength=max(300,self.editor_canvas.winfo_width()-30))
            self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox('all'))
        body.bind('<Configure>',resize_help)

    def add_row(self,definition=None):
        if len(self.rows)>=3:
            return
        if definition is None:
            definition=asdict(ComponentDefinition(f'Component {len(self.rows)+1}',energy_eV=1.2+.08*len(self.rows)))
        values=[definition['label'],definition['order'],definition['energy_eV'],definition['prefactor_s_inv'],
                definition['initial_coverage'],*definition['energy_bounds']]
        variables=[tk.StringVar(self.window,value=value) for value in values]
        widgets=[]
        for index,variable in enumerate(variables):
            widget=ttk.Entry(self.rows_frame,textvariable=variable,width=18 if index==0 else 13)
            widget.grid(row=len(self.rows)+1,column=index,padx=3,pady=3,sticky='ew')
            widgets.append(widget)
        self.rows.append((variables,widgets))

    def remove_row(self):
        if len(self.rows)>1:
            _,widgets=self.rows.pop()
            for widget in widgets:
                widget.destroy()

    def apply(self):
        try:
            if self.app.job_busy:
                raise ValueError('Finish or cancel the running calculation before applying component definitions.')
            if self.panel.key()!=self.editor_key:
                raise ValueError('Dataset or named region changed. Close and reopen this editor for the current selection.')
            definitions=[]
            for variables,_ in self.rows:
                label,n,energy,nu,coverage,lo,hi=[v.get() for v in variables]
                definitions.append(ComponentDefinition(label.strip(),float(n),float(energy),float(nu),float(coverage),(float(lo),float(hi))))
            _definitions(definitions)
            if self.fit_drift.get() and not self.fit_baseline.get():
                raise ValueError('Enable the shared offset when fitting drift.')
            self.panel.session()['component_settings']=dict(components=[asdict(c) for c in definitions],
                fit_baseline=self.fit_baseline.get(),fit_drift=self.fit_drift.get())
            self.message.set('Definitions applied. Fit the components together or compare counts.')
            self.panel.render()
            return True
        except (ValueError,KeyError) as exc:
            self.message.set(str(exc))
            return False

    def apply_and_run(self,compare):
        if self.apply():
            self.run(compare)

    def run(self,compare=False):
        if self.app.job_busy:
            self.app.status.set('A calculation is already running; finish or cancel it first.')
            return False
        try:
            if self.panel.preview_after is not None:
                self.app.root.after_cancel(self.panel.preview_after)
                self.panel.preview_after=None
            snap=self.snapshot()
            dataset,_=self.app.project.context()
            t=dataset.spectrum.temperature_clean_c.copy()
            y=processed_signal(dataset,snap['processing']).copy()
            settings=snap['component_settings']
            definitions=[ComponentDefinition(**item) for item in settings['components']]
            _definitions(definitions)
            options=dict(beta_k_s=float(snap['settings']['beta']),components=definitions,
                fit_baseline=settings['fit_baseline'],fit_drift=settings['fit_drift'],
                max_nfev=int(snap['settings']['max_nfev']),multistart=snap['settings']['multistart'],
                cancelled=self.app.job_cancel.is_set)
            def work():
                if compare:
                    candidates=compare_component_counts(t,y,counts=tuple(range(1,len(definitions)+1)),**options)
                    usable=[c for c in candidates if c.fit is not None]
                    if not usable:
                        raise ValueError('No component-count candidate converged: '+'; '.join(c.error or '' for c in candidates))
                    fit=usable[0].fit
                else:
                    candidates=[]
                    fit=fit_components(t,y,**options)
                return serial(dict(snapshot=snap,fit=fit,count_comparison=candidates,
                    created_utc=datetime.now(timezone.utc).isoformat(),
                    dependencies={name:version(name) for name in ('numpy','scipy','pandas','matplotlib')}))
            if self.app.start_job(work,self.complete):
                self.app.status.set('Fitting all components jointly on the full spectrum… Cancel remains available.')
                if self.window is not None and self.window.winfo_exists():
                    self.message.set('Running in the background. Use Cancel in Modeling; previous results remain visible.')
                return True
        except (ValueError,KeyError) as exc:
            self.app.status.set(str(exc))
        return False

    def show(self):
        try:
            if self.panel.session().get('components') is None:
                raise ValueError('Fit simultaneous components first.')
            self.panel.session()['display_mode']='components'
            self.panel.render()
        except ValueError as exc:
            self.app.status.set(str(exc))

    def select_count(self):
        try:
            if self.panel.session().get('display_mode')!='components':
                return
            selection=self.panel.table.selection()
            if not selection or not selection[0].startswith('count-'):
                return
            count=int(selection[0].split('-')[1])
            record=deepcopy(self.panel.session()['components'])
            candidate=next(c for c in record['count_comparison'] if c['count']==count)
            if candidate['fit'] is None:
                raise ValueError('This count did not converge: '+candidate['error'])
            record['fit']=candidate['fit']
            record['selected_component_count']=count
            self.panel.session()['components']=record
            self.panel.render()
            self.app.status.set(f'Showing submitted {count}-component hypothesis; rankings are heuristic.')
        except (ValueError,KeyError) as exc:
            self.app.status.set(str(exc))

    def complete(self,record):
        self.panel.complete('components',record)
        if self.window is not None and self.window.winfo_exists():
            self.message.set('Joint fitting finished. Inspect components, their sum, residuals and warnings in Modeling.')

    def render(self,axis,residual_axis,record):
        fit=record['fit']
        draw_components(axis,residual_axis,fit)
        notes=('Current simultaneous fit.\n' if self.current(record) else 'STALE simultaneous fit — submitted assumptions plotted; refit after edits.\n')
        notes+='Full spectrum fitted jointly; fixed orders/prefactors/initial coverages, optimized energies and detector scales.\n'
        notes+=f"RMSE {fit['rmse']:.6g}; AICc {fit['aicc']:.6g}; BIC {fit['bic']:.6g}; starts {fit['starts_converged']}/{fit['starts_attempted']}.\n"
        notes+=fit['uncertainty_note']+'\n'+'\n'.join(fit['warnings'])
        if any(c['error'] for c in record.get('count_comparison',[])):
            notes+='\nSome counts failed. Relative weights describe only the converged subset; the requested ranking is incomplete.'
        for index,component in enumerate(fit['components']):
            interval=component.get('energy_interval_95_eV')
            note=f"scale={component['signal_scale']:.6g}; "+(f'conditional E interval={interval}' if interval else 'local intervals withheld')
            self.panel.table.insert('','end',iid=f'component-{index}',values=(component['label'],component['order'],
                component['energy_eV'],component['prefactor_s_inv'],'—','—',note))
        for candidate in record.get('count_comparison',[]):
            value=candidate.get('fit')
            self.panel.table.insert('','end',iid=f"count-{candidate['count']}",values=(
                f"{candidate['count']} component model",'fixed','—','—',value['rmse'] if value else '—',candidate['delta_aicc'],
                candidate['error'] or f"BIC {value['bic']:.6g}; relative weight {candidate['akaike_weight']}; heuristic"))
        self.panel.note(notes)

    def export(self):
        try:
            record=self.panel.session().get('components')
            if record is None:
                raise ValueError('Fit simultaneous components before exporting.')
            folder=filedialog.askdirectory(parent=self.window or self.app.root,title='Choose parent folder for a new component export')
            if folder:
                destination=export_components(record,proposed_run_folder(folder))
                self.app.status.set('Component fit exported with submitted assumptions: '+str(destination))
        except (ValueError,OSError) as exc:
            self.app.status.set(str(exc))
