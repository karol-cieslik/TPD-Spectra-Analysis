"""Explicit physical hypotheses for simultaneous full-spectrum fitting."""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime,timezone
from importlib.metadata import version
import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .workflow_analysis import processed_signal, serial
from .multicomponent import (ComponentDefinition, fit_components, compare_component_counts,
    _definitions, suggest_peak_positions, suggest_component)
from .component_export import draw_components, export_components
from .run_session import proposed_run_folder
from .scientific_help import help_button
from .heating_rate import source_heating_rate, confirm_source_rate
from .analysis import redhead_energy
from scipy.optimize import brentq


def defaults():
    return dict(components=[asdict(ComponentDefinition(f'Peak {i+1}',energy_eV=1.2+.08*i)) for i in range(2)],fit_baseline=True,fit_drift=False)


class ComponentsController:
    def __init__(self,panel):
        self.panel=panel
        self.app=panel.app
        self.window=None

    def settings(self):
        session=self.panel.session()
        if 'component_settings' not in session:
            settings=defaults()
            try:
                dataset,_=self.app.project.context()
                positions=suggest_peak_positions(dataset.spectrum.temperature_clean_c,
                    processed_signal(dataset,dataset.processing),2)
                settings['components']=[asdict(suggest_component(p,float(session['settings']['beta']),label=f'Peak {i+1}'))
                    for i,p in enumerate(positions)]
            except ValueError:
                pass
            session['component_settings']=settings
        return session['component_settings']

    def snapshot(self):
        snap=self.panel.snapshot()
        dataset,_=self.app.project.context()
        snap['method']='Simultaneous Polanyi–Wigner components'
        snap['component_engine_revision']='temperature-multistart-v2'
        snap['selected_named_region']=snap['region']
        t=dataset.spectrum.temperature_clean_c
        snap['region']=[float(t[0]),float(t[-1])]
        snap['scope']='Entire selected spectrum; named regions do not crop this fit'
        snap['settings']={key:snap['settings'][key] for key in ('beta','max_nfev','multistart')}
        snap['component_settings']=deepcopy(self.settings())
        snap['source_heating_rate_confirmation']=deepcopy(self.panel.session().get('source_heating_rate_confirmation'))
        return snap

    def current(self,record):
        try:
            return self.app.project.fingerprint(record['snapshot'])==self.app.project.fingerprint(self.snapshot())
        except (ValueError,KeyError):
            return False

    def open(self,count=None):
        try:
            self.app.project.context()
            beta=float(self.panel.variables['beta'].get())
            if not np.isfinite(beta) or beta<=0:
                raise ValueError('Enter a positive finite heating rate before opening component fitting.')
        except ValueError as exc:
            self.app.status.set(str(exc))
            return
        if self.window is not None and self.window.winfo_exists():
            if count is not None and len(self.rows)!=count:
                self.message.set('Close this editor before starting a new two-peak hypothesis; current edits are retained.')
            self.window.lift()
            return
        self.editor_key=self.panel.key()
        self.building_editor=True
        self.window=tk.Toplevel(self.app.root)
        self.window.title('Fit multiple peaks — full spectrum')
        self.window.geometry('1040x740')
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
        dataset,_=self.app.project.context()
        t=dataset.spectrum.temperature_clean_c
        y=processed_signal(dataset,dataset.processing)
        if count is not None and len(settings['components'])!=count:
            settings['components']=[asdict(suggest_component(p,float(self.panel.variables['beta'].get()),label=f'Peak {i+1}'))
                for i,p in enumerate(suggest_peak_positions(t,y,count))]
        rate_row=ttk.Frame(body)
        rate_row.pack(fill='x',pady=4)
        ttk.Label(rate_row,text='1. Verify heating rate (K/s):').pack(side='left')
        ttk.Entry(rate_row,textvariable=self.panel.variables['beta'],width=10).pack(side='left',padx=6)
        suggestion=source_heating_rate(dataset)
        ttk.Button(rate_row,text=(f"Confirm source suggestion: {suggestion['beta_K_s']:g} K/s…" if suggestion
            else 'No source rate; enter verified value'),state='normal' if suggestion else 'disabled',
            command=self.confirm_rate).pack(side='left')
        ttk.Label(body,text='2. Click approximate peak positions below (left click cycles through the rows), or edit °C positions.\n'
            'Auto hints may include a shoulder. They do not identify physical states. New rows use n=1, ν=1e13 s⁻¹, θ₀=1; saved assumptions are retained.',wraplength=940).pack(fill='x')
        self.position_figure=Figure(figsize=(8,2.2),dpi=100,layout='constrained')
        self.position_axis=self.position_figure.add_subplot(111)
        self.position_axis.plot(t,y,color='#334155',linewidth=1)
        self.position_axis.set(xlabel='Temperature (°C)',ylabel='Processed signal')
        self.position_canvas=FigureCanvasTkAgg(self.position_figure,master=body)
        self.position_canvas.get_tk_widget().pack(fill='x')
        self.position_canvas.mpl_connect('button_press_event',self.select_position)
        self.position_frame=ttk.Frame(body)
        self.position_frame.pack(fill='x',pady=4)
        self.fixed_summary=tk.StringVar(self.window)
        ttk.Label(body,textvariable=self.fixed_summary,wraplength=940).pack(fill='x')
        self.position_vars=[]
        self.position_markers=[]
        self.next_position=0
        self.advanced=tk.BooleanVar(self.window,value=False)
        self.advanced_toggle=ttk.Checkbutton(body,text='Advanced settings: fixed kinetics, energy bounds, baseline and optimizer',
            variable=self.advanced,command=self.toggle_advanced)
        self.advanced_toggle.pack(anchor='w')
        self.advanced_frame=ttk.Frame(body)
        self.rows=[]
        row_options=ttk.Frame(self.advanced_frame)
        row_options.pack(fill='x')
        self.rows_frame=ttk.Frame(self.advanced_frame)
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
            option=ttk.Frame(self.advanced_frame)
            option.pack(fill='x')
            ttk.Checkbutton(option,text=label,variable=variable).pack(side='left')
            help_button(option,self.app,topic).pack(side='left',padx=4)
        for key,title in (('max_nfev','Maximum evaluations per start'),):
            option=ttk.Frame(self.advanced_frame)
            option.pack(fill='x')
            ttk.Label(option,text=title).pack(side='left')
            ttk.Entry(option,textvariable=self.panel.variables[key],width=10).pack(side='left',padx=6)
        ttk.Checkbutton(self.advanced_frame,text='Deterministic multistart (recommended)',
            variable=self.panel.variables['multistart']).pack(anchor='w')
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
            button=ttk.Button(buttons,text=text,command=command)
            button.grid(row=index//3,column=index%3,padx=3,pady=3,sticky='ew')
            if index==1:
                self.fit_button=button
        self.message=tk.StringVar(self.window,value='Review the rate, select two positions, then Fit Both Peaks. Advanced edits are preserved until you use Re-estimate.')
        message_label=ttk.Label(footer,textvariable=self.message,wraplength=980)
        message_label.pack(fill='x',pady=4)
        footer.bind('<Configure>',lambda e:message_label.configure(wraplength=max(300,e.width-16)))
        def resize_help(event):
            for child in body.winfo_children():
                if isinstance(child,ttk.Label) and str(child.cget('wraplength')).strip() not in ('','0'):
                    child.configure(wraplength=max(300,self.editor_canvas.winfo_width()-30))
            self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox('all'))
        body.bind('<Configure>',resize_help)
        self.building_editor=False
        self.refresh_positions()

    def toggle_advanced(self):
        if self.advanced.get():
            self.advanced_frame.pack(fill='x',after=self.advanced_toggle)
        else:
            self.advanced_frame.pack_forget()

    def confirm_rate(self):
        if self.panel.key()!=self.editor_key:
            self.message.set('Dataset or named region changed. Close and reopen this editor.')
            return
        if confirm_source_rate(self.panel,self.window):
            self.message.set('Source rate confirmed. Click Re-estimate from positions to update energy guesses/bounds for this rate.')

    def refresh_positions(self):
        for widget in self.position_frame.winfo_children():
            widget.destroy()
        self.position_vars=[]
        self.positions_dirty=False
        dataset,_=self.app.project.context()
        t=dataset.spectrum.temperature_clean_c
        try:
            beta=float(self.panel.variables['beta'].get())
            for i,(variables,_) in enumerate(self.rows):
                energy,nu=float(variables[2].get()),float(variables[3].get())
                low,high=float(t[0]),float(t[-1])
                if redhead_energy(low,nu,beta)<=energy<=redhead_energy(high,nu,beta):
                    position=brentq(lambda p:redhead_energy(p,nu,beta)-energy,low,high)
                else:
                    position=low if energy<redhead_energy(low,nu,beta) else high
                variable=tk.StringVar(self.window,value=f'{position:.3f}')
                variable.trace_add('write',lambda *_:setattr(self,'positions_dirty',True))
                self.position_vars.append(variable)
                ttk.Label(self.position_frame,text=f'Peak {i+1} °C:').pack(side='left')
                ttk.Entry(self.position_frame,textvariable=variable,width=9).pack(side='left',padx=4)
            ttk.Button(self.position_frame,text='Re-estimate from positions',command=self.estimate_positions).pack(side='left',padx=6)
            self.draw_positions()
            self.position_beta=beta
            self.fit_button.configure(text='Fit Both Peaks' if len(self.rows)==2 else f'Fit {len(self.rows)} Components Together')
            self.fixed_summary.set('Retained fixed assumptions: '+ '; '.join(
                f'{v[0].get()}: n={v[1].get()}, ν={v[3].get()} s⁻¹, θ₀={v[4].get()}' for v,_ in self.rows)
                +'. Shared offset '+('on' if self.fit_baseline.get() else 'off')+', drift '+('on' if self.fit_drift.get() else 'off')+'.')
        except ValueError as exc:
            self.message.set(str(exc))

    def draw_positions(self):
        for marker in self.position_markers:
            marker.remove()
        self.position_markers=[]
        for i,variable in enumerate(self.position_vars):
            self.position_markers.append(self.position_axis.axvline(float(variable.get()),
                color=('#2563eb','#059669','#9333ea')[i],linestyle=('--','-.',':')[i],label=f'Peak {i+1} hint'))
        self.position_axis.legend(fontsize=8)
        self.position_canvas.draw_idle()

    def estimate_positions(self):
        try:
            if self.app.job_busy or self.panel.key()!=self.editor_key:
                raise ValueError('Finish the calculation and reopen for the selected dataset/region before changing positions.')
            dataset,_=self.app.project.context()
            t=dataset.spectrum.temperature_clean_c
            positions=[float(v.get()) for v in self.position_vars]
            if not all(np.isfinite(p) and t[0]<=p<=t[-1] for p in positions):
                raise ValueError('Peak positions must be finite and within the spectrum.')
            if len(positions)>1 and min(np.diff(sorted(positions))) <= .001:
                raise ValueError('Choose distinct approximate peak positions; coincident components are ambiguous.')
            updates=[]
            for p,(variables,_) in zip(positions,self.rows):
                if float(variables[1].get())!=1:
                    raise ValueError('Redhead position estimates assume first order. Keep other orders and edit energy/bounds in Advanced settings.')
                updates.append(suggest_component(p,float(self.panel.variables['beta'].get()),
                    label=variables[0].get(),prefactor_s_inv=float(variables[3].get())))
            for definition,(variables,_) in zip(updates,self.rows):
                for index,value in ((2,definition.energy_eV),(5,definition.energy_bounds[0]),(6,definition.energy_bounds[1])):
                    variables[index].set(f'{value:.8g}')
            self.draw_positions()
            self.positions_dirty=False
            self.position_beta=float(self.panel.variables['beta'].get())
            self.message.set('First-order energy guesses and ±30% search bounds updated. These are heuristic starts, not measured energies or uncertainty intervals. Fit Both Peaks to optimize.')
            return True
        except ValueError as exc:
            self.message.set(str(exc))
            return False

    def select_position(self,event):
        if event.inaxes is not self.position_axis or event.button!=1 or event.xdata is None:
            return
        if self.app.job_busy or self.panel.key()!=self.editor_key:
            self.message.set('Finish the calculation and reopen for the current dataset before selecting peaks.')
            return
        index=self.next_position%len(self.position_vars)
        previous=self.position_vars[index].get()
        self.position_vars[index].set(f'{event.xdata:.3f}')
        if self.estimate_positions():
            self.next_position=(index+1)%len(self.position_vars)
            self.message.set(f'Peak {index+1} selected at {event.xdata:.2f} °C. Next click selects Peak {self.next_position+1}. Review positions, then Fit Both Peaks.')
        else:
            self.position_vars[index].set(previous)

    def add_row(self,definition=None):
        if len(self.rows)>=3:
            return
        if definition is None:
            dataset,_=self.app.project.context()
            position=suggest_peak_positions(dataset.spectrum.temperature_clean_c,
                processed_signal(dataset,dataset.processing),len(self.rows)+1)[-1]
            definition=asdict(suggest_component(position,float(self.panel.variables['beta'].get()),
                label=f'Component {len(self.rows)+1}'))
        values=[definition['label'],definition['order'],definition['energy_eV'],definition['prefactor_s_inv'],
                definition['initial_coverage'],*definition['energy_bounds']]
        variables=[tk.StringVar(self.window,value=value) for value in values]
        widgets=[]
        for index,variable in enumerate(variables):
            widget=ttk.Entry(self.rows_frame,textvariable=variable,width=18 if index==0 else 13)
            widget.grid(row=len(self.rows)+1,column=index,padx=3,pady=3,sticky='ew')
            widgets.append(widget)
        self.rows.append((variables,widgets))
        if not self.building_editor:
            self.refresh_positions()

    def remove_row(self):
        if len(self.rows)>1:
            _,widgets=self.rows.pop()
            for widget in widgets:
                widget.destroy()
            self.refresh_positions()

    def apply(self):
        try:
            if self.app.job_busy:
                raise ValueError('Finish or cancel the running calculation before applying component definitions.')
            if self.panel.key()!=self.editor_key:
                raise ValueError('Dataset or named region changed. Close and reopen this editor for the current selection.')
            if self.positions_dirty or (not self.advanced.get() and float(self.panel.variables['beta'].get())!=self.position_beta):
                if not self.estimate_positions():
                    return False
            definitions=[]
            for variables,_ in self.rows:
                label,n,energy,nu,coverage,lo,hi=[v.get() for v in variables]
                definitions.append(ComponentDefinition(label.strip(),float(n),float(energy),float(nu),float(coverage),(float(lo),float(hi))))
            _definitions(definitions)
            if self.fit_drift.get() and not self.fit_baseline.get():
                raise ValueError('Enable the shared offset when fitting drift.')
            self.panel.session()['component_settings']=dict(components=[asdict(c) for c in definitions],
                fit_baseline=self.fit_baseline.get(),fit_drift=self.fit_drift.get(),
                peak_position_hints_c=[float(v.get()) for v in self.position_vars])
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
        fit=record['fit']
        quality=fit['diagnostics'].get('fit_quality','review_required')
        status=(quality.replace('_',' ').upper()+f"; normalized RMSE {fit['normalized_rmse']:.3g}. "
            'Inspect component contributions, residuals and Assumptions & warnings.')
        self.app.status.set(status)
        if self.window is not None and self.window.winfo_exists():
            self.message.set(status)

    def render(self,axis,residual_axis,record):
        fit=record['fit']
        draw_components(axis,residual_axis,fit)
        notes=('Current simultaneous fit.\n' if self.current(record) else 'STALE simultaneous fit — submitted assumptions plotted; refit after edits.\n')
        notes+='Full spectrum fitted jointly; fixed orders/prefactors/initial coverages, optimized energies and detector scales.\n'
        notes+=f"Quality: {fit['diagnostics'].get('fit_quality','not screened')}; normalized RMSE {fit['normalized_rmse']:.4g}. Optimizer success alone does not establish an adequate fit.\n"
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
