"""Embedded modeling workspace backed by the existing kinetic engines."""
from copy import deepcopy
from dataclasses import asdict
import json
import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .workflow_analysis import selected_arrays, serial
from .kinetics import simulate_tpd, KineticFitResult
from .kinetics_explorer import compare_desorption_orders, ModelCandidate
from .kinetics_uncertainty import run_kinetics_monte_carlo

DEFAULTS = dict(beta='1', energy='1.25', prefactor='1e13', order='1', coverage='1',
                amplitude='1', baseline='0', max_nfev='300', replicates='500', seed='42',
                fit_baseline=True, multistart=True, zero=True, first=True, second=True, fractional=True)


def models_from_records(records):
    return [ModelCandidate(name=r['name'], fit=KineticFitResult(**r['fit']) if r['fit'] else None,
                           prediction=np.asarray(r['prediction']) if r['prediction'] is not None else None,
                           error=r['error'], delta_aicc=r['delta_aicc'], akaike_weight=r['akaike_weight'],
                           warnings=tuple(r['warnings']), starts_attempted=r['starts_attempted'],
                           starts_converged=r['starts_converged']) for r in records]


def comparison(dataset, snapshot, cancelled):
    t, y = selected_arrays(dataset, snapshot)
    s = snapshot['settings']
    models = compare_desorption_orders(t, y, float(s['beta']),
        orders=tuple(k for k in ('zero','first','second','fractional') if s[k]),
        initial_energy_ev=float(s['energy']), initial_prefactor_s_inv=float(s['prefactor']),
        fit_baseline=s['fit_baseline'], max_nfev=int(s['max_nfev']), multistart=s['multistart'], cancelled=cancelled)
    return serial(dict(snapshot=snapshot, temperature=t, signal=y, candidates=models))


class ModelingPanel:
    def __init__(self, app, frame):
        self.app = app
        self.restoring = False
        self.preview_after = None
        self.variables = {k: (tk.BooleanVar(app.root, value=v) if isinstance(v, bool) else tk.StringVar(app.root, value=v)) for k,v in DEFAULTS.items()}
        panes = ttk.Panedwindow(frame, orient='horizontal')
        panes.pack(fill='both', expand=True)
        controls, workspace = ttk.Frame(panes, width=320), ttk.Frame(panes)
        panes.add(controls, weight=0)
        panes.add(workspace, weight=1)
        sidebar = app._scroll_panel(controls)
        ttk.Label(sidebar, text='Model hypotheses', style='Section.TLabel').pack(anchor='w')
        for key, label in (('beta','Heating rate (K/s)'), ('energy','Initial / simulated energy (eV)'),
            ('prefactor','Initial / simulated prefactor (s⁻¹)'), ('order','Simulation order (≥0)'),
            ('coverage','Simulation initial coverage (0–1)'), ('amplitude','Simulation signal scale'),
            ('baseline','Simulation constant baseline'), ('max_nfev','Maximum fit evaluations'),
            ('replicates','Monte Carlo replicates (1–10000)'), ('seed','Monte Carlo seed')):
            ttk.Label(sidebar, text=label).pack(anchor='w', pady=(4,0))
            ttk.Entry(sidebar, textvariable=self.variables[key]).pack(fill='x')
        for key in ('zero','first','second','fractional','fit_baseline','multistart'):
            ttk.Checkbutton(sidebar, text=key.replace('_',' ').capitalize(), variable=self.variables[key]).pack(anchor='w')
        ttk.Label(sidebar, text='Fits normalize initial coverage to one and optimize signal scale. Simulation coverage/amplitude/baseline apply only to manual preview.', wraplength=280).pack(fill='x', pady=8)
        for title, callback in (('Simulate parameters',self.simulate), ('Compare models',self.compare),
                                ('Run Monte Carlo',self.monte_carlo), ('Cancel',lambda: app.job_cancel.set()),
                                ('Use selected model in Kinetic Analysis',self.transfer)):
            ttk.Button(sidebar, text=title, command=callback).pack(fill='x', pady=3)
        self.fig = Figure(figsize=(8,5), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=workspace)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        columns = ('model','order','energy','prefactor','rmse','aicc','warning')
        self.table = ttk.Treeview(workspace, columns=columns, show='headings', height=4)
        labels = ('Model','Order','E (eV)','ν (s⁻¹)','RMSE','Δ AICc','Validity / warnings')
        for col,label in zip(columns,labels):
            self.table.heading(col, text=label, command=lambda c=col:self.sort(c))
            self.table.column(col, width=85 if col != 'warning' else 260, minwidth=60)
        self.table.pack(fill='x')
        scroll = ttk.Scrollbar(workspace, orient='horizontal', command=self.table.xview)
        self.table.configure(xscrollcommand=scroll.set)
        scroll.pack(fill='x')
        self.notes = tk.Text(workspace, height=6, wrap='word', font=('Segoe UI',10))
        self.notes.pack(fill='x')
        for key,var in self.variables.items():
            var.trace_add('write',lambda *_args,k=key:self.changed(k))

    def key(self):
        dataset, region = self.app.project.context()
        return f'{dataset.id}/{region.id}'

    def session(self):
        return self.app.project.modeling.setdefault(self.key(), {'settings':deepcopy(DEFAULTS)})

    def snapshot(self):
        snap = self.app.project.snapshot('Polanyi–Wigner')
        snap['method'] = 'Model exploration'
        snap['settings'] = deepcopy(self.session()['settings'])
        return snap

    def current(self, result):
        old,new = deepcopy(result['snapshot']),self.snapshot()
        keys = {'beta','energy','prefactor','max_nfev','fit_baseline','multistart','zero','first','second','fractional'}
        if 'prediction' in result:
            keys = {'beta','energy','prefactor','order','coverage','amplitude','baseline'}
        elif 'result' in result:
            keys |= {'seed','replicates'}
        for snapshot in (old,new):
            snapshot['settings'] = {k:v for k,v in snapshot['settings'].items() if k in keys}
        return self.app.project.fingerprint(old) == self.app.project.fingerprint(new)

    def changed(self, key):
        if self.restoring:
            return
        try:
            self.session()['settings'] = {k:v.get() for k,v in self.variables.items()}
            self.render()
            if key in {'beta','energy','prefactor','order','coverage','amplitude','baseline'}:
                if self.preview_after is not None:
                    self.app.root.after_cancel(self.preview_after)
                self.preview_after = self.app.root.after(650,self.preview)
        except ValueError:
            pass

    def preview(self):
        self.preview_after = None
        if not self.app.job_busy:
            self.simulate()

    def restore(self):
        if self.preview_after is not None:
            self.app.root.after_cancel(self.preview_after)
            self.preview_after = None
        self.restoring = True
        try:
            for key,value in self.session()['settings'].items():
                self.variables[key].set(value)
        except ValueError:
            pass
        finally:
            self.restoring = False
        self.render()

    def note(self, text):
        self.notes.configure(state='normal')
        self.notes.delete('1.0','end')
        self.notes.insert('end',text)
        self.notes.configure(state='disabled')

    def render(self):
        self.fig.clear()
        self.table.delete(*self.table.get_children())
        try:
            session = self.session()
            result = session.get('comparison')
            dataset, _ = self.app.project.context()
            t,y = selected_arrays(dataset,self.snapshot()) if not result else (result['temperature'],result['signal'])
        except ValueError:
            self.note('Select an imported dataset and named peak to model.')
            self.canvas.draw_idle()
            return
        ax = self.fig.add_subplot(211)
        residual = self.fig.add_subplot(212)
        ax.plot(t,y,label='Comparison input (submitted snapshot)' if result else 'Selected processed signal')
        notes = 'A ranking does not prove a mechanism. Single-state fits assume a linear heating ramp and coverage one at the interval start.\n'
        if result:
            notes += ('Current comparison.\n' if self.current(result) else 'STALE comparison — original interval/settings plotted. Compare again before transfer or Monte Carlo.\n')
            notes += 'Compared interval: ' + str(result['snapshot']['region']) + ' °C; β = ' + str(result['snapshot']['settings']['beta']) + ' K/s\n'
            for index,c in enumerate(result['candidates']):
                fit = c['fit']
                vals = [c['name']] + ([fit['reaction_order'],fit['activation_energy_eV'],fit['prefactor_s_inv'],fit['rmse_signal'],c['delta_aicc']] if fit else ['—']*5)
                self.table.insert('','end',iid=str(index),values=vals+[c['error'] or '; '.join(c['warnings'])])
                if c['prediction'] is not None and not c['error']:
                    ax.plot(t,c['prediction'],label=c['name'])
                    residual.plot(t,np.asarray(y)-np.asarray(c['prediction']),label=c['name'])
        simulation = session.get('simulation')
        if simulation and self.current(simulation):
            ax.plot(simulation['temperature'],simulation['prediction'],'--',label='Manual simulation (not fitted)')
        mc = session.get('monte_carlo')
        if mc:
            r = mc['result']
            notes += f"Monte Carlo seed {r['seed']}; {r['replicates_completed']}/{r['replicates_requested']} replicates; failed rankings {r['failed_rankings']}. "
            notes += json.dumps(r['winning_counts']) + '\n' + r['interval_note'] + '\n'
            notes += 'Conditional parameter ranges: ' + json.dumps(r['parameter_intervals']) + '\n'
            notes += ('MC settings are current. ' if self.current(mc) else 'MC settings are stale. ')
        notes += 'Monte Carlo uses iid Gaussian residual noise around the lowest-AICc converged reference; ranges withheld below 100 successful refits. Frequencies are not mechanism probabilities.'
        ax.set(ylabel='Signal (instrument units)')
        ax.legend(fontsize=8)
        residual.axhline(0,color='gray',linewidth=.7)
        residual.set(xlabel='Temperature (°C)',ylabel='Residual')
        self.note(notes)
        self.canvas.draw_idle()

    def simulate(self):
        try:
            dataset,_ = self.app.project.context()
            snap = self.snapshot()
            t,_ = selected_arrays(dataset,snap)
            s = snap['settings']
            def work():
                _, rate = simulate_tpd(t,float(s['beta']),float(s['energy']),float(s['prefactor']),float(s['order']),float(s['coverage']))
                amplitude, baseline = float(s['amplitude']),float(s['baseline'])
                if not np.isfinite([amplitude,baseline]).all() or amplitude <= 0:
                    raise ValueError('Simulation amplitude must be positive; baseline finite.')
                return serial(dict(snapshot=snap,temperature=t,prediction=amplitude*rate+baseline))
            self.app.start_job(work,lambda r:self.complete('simulation',r))
        except (ValueError,KeyError) as exc:
            self.app.status.set(str(exc))

    def compare(self):
        try:
            dataset,_ = self.app.project.context()
            snap = self.snapshot()
            if self.app.start_job(lambda: comparison(dataset,snap,self.app.job_cancel.is_set),lambda r:self.complete('comparison',r)):
                self.app.status.set('Comparing candidate models…')
        except (ValueError,KeyError) as exc:
            self.app.status.set(str(exc))

    def complete(self,kind,result):
        snap = result['snapshot']
        key = f"{snap['dataset_id']}/{snap['region_id']}"
        session = self.app.project.modeling[key]
        session[kind] = result
        if kind == 'comparison':
            session.pop('monte_carlo',None)
        self.render()
        self.app.status.set(kind.replace('_',' ').capitalize() + ' finished; results retain submitted settings.')

    def monte_carlo(self):
        try:
            previous = self.session().get('comparison')
            if not previous or not self.current(previous):
                raise ValueError('Compare current models before running Monte Carlo.')
            snap = self.snapshot()
            s = snap['settings']
            replicates,seed = int(s['replicates']),int(s['seed'])
            if not 1 <= replicates <= 10000 or seed < 0:
                raise ValueError('Use 1–10000 replicates and a non-negative integer seed.')
            def work():
                result = run_kinetics_monte_carlo(previous['temperature'],previous['signal'],float(s['beta']),
                    orders=tuple(c['name'] for c in previous['candidates']),replicates=replicates,seed=seed,
                    fit_baseline=s['fit_baseline'],max_nfev=int(s['max_nfev']),multistart=s['multistart'],
                    reference_comparison=models_from_records(previous['candidates']),cancelled=self.app.job_cancel.is_set,
                    progress=lambda done,total:self.app.jobs.put(('progress',f'Monte Carlo {done}/{total}')))
                return serial(dict(snapshot=snap,result=result))
            self.app.start_job(work,lambda r:self.complete('monte_carlo',r))
        except (ValueError,KeyError) as exc:
            self.app.status.set(str(exc))

    def transfer(self):
        try:
            session = self.session()
            result = session.get('comparison')
            if not result or not self.current(result):
                raise ValueError('Compare current settings before transferring a candidate.')
            selection = self.table.selection()
            if not selection:
                raise ValueError('Select a candidate row to transfer.')
            candidate = result['candidates'][int(selection[0])]
            if candidate['error'] or not candidate['fit']:
                raise ValueError('Only a converged candidate can be transferred.')
            fit = candidate['fit']
            settings = self.app.project.method_settings('Polanyi–Wigner')
            settings.update(beta=result['snapshot']['settings']['beta'],energy=fit['activation_energy_eV'],
                            prefactor=fit['prefactor_s_inv'],order=fit['reaction_order'],
                            free_order=candidate['name']=='fractional',fit_baseline=result['snapshot']['settings']['fit_baseline'])
            session['selected_hypothesis'] = deepcopy(candidate)
            self.app.method.set('Polanyi–Wigner')
            self.app.stages.select(2)
            self.app.refresh_context()
            self.app.status.set('Candidate transferred as initial guesses. Run an explicit fit to produce a kinetic analysis result.')
        except (ValueError,KeyError) as exc:
            self.app.status.set(str(exc))

    def sort(self,column):
        def key(item):
            value = self.table.set(item,column)
            try:
                return (0,float(value))
            except ValueError:
                return (1,value)
        for index,item in enumerate(sorted(self.table.get_children(),key=key)):
            self.table.move(item,'',index)
