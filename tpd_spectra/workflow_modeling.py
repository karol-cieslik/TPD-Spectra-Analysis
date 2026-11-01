"""Embedded modeling workspace backed by the existing kinetic engines."""
from copy import deepcopy
from dataclasses import asdict
import json
import math
import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .workflow_analysis import selected_arrays, serial, plot_observations
from .kinetics import simulate_tpd, KineticFitResult
from .kinetics_explorer import compare_desorption_orders, ModelCandidate
from .kinetics_uncertainty import run_kinetics_monte_carlo
from .equation_help import EquationCard
from .job_progress import MonteCarloProgress
from .component_gui import ComponentsController
from .scientific_help import help_button
from .heating_rate import source_heating_rate, confirm_source_rate

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


def transfer_starting_values(candidate, mc_result=None):
    """Return initial guesses, never independent kinetic estimates.

    Monte Carlo refits provide marginal parameter medians. These do not form
    a joint optimum and therefore must only initialize a subsequent fit.
    """
    fit = candidate.get('fit')
    if candidate.get('error') or not fit:
        raise ValueError('Only a converged model can supply starting parameters.')
    name = candidate['name']
    values = dict(energy=float(fit['activation_energy_eV']),
                  prefactor=float(fit['prefactor_s_inv']),
                  order=float(fit['reaction_order']),
                  free_order=name == 'fractional')
    if not math.isfinite(values['energy']) or values['energy'] <= 0:
        raise ValueError('The selected model has an invalid activation energy.')
    if not math.isfinite(values['prefactor']) or values['prefactor'] <= 0:
        raise ValueError('The selected model has an invalid prefactor.')
    if mc_result is None:
        return values, f'{name} model point fit; refitting is optional when assumptions change.'

    if mc_result.get('cancelled') or mc_result.get('replicates_completed', 0) < mc_result.get('replicates_requested', 0):
        raise ValueError('Use a completed Monte Carlo run before transferring medians.')
    records = [row for row in mc_result.get('replicate_records', ())
               if row.get('model') == name and not row.get('error')
               and row.get('energy_eV') is not None
               and math.isfinite(float(row['energy_eV']))]
    minimum = max(100, int(mc_result.get('minimum_successful_refits', 100)))
    if len(records) < minimum:
        raise ValueError(f'Monte Carlo has only {len(records)} successful {name} refits; '
                         f'at least {minimum} are required for median starting values. '
                         'Use the point-fit transfer or run more replicates.')
    values['energy'] = float(np.median([row['energy_eV'] for row in records]))
    if name != 'zero':
        logs = [float(row['log10_prefactor']) for row in records
                if row.get('log10_prefactor') is not None
                and math.isfinite(float(row['log10_prefactor']))]
        if len(logs) < minimum:
            raise ValueError('Monte Carlo has insufficient valid prefactor refits.')
        values['prefactor'] = float(10.0 ** np.median(logs))
    if name == 'fractional':
        orders = [float(row['order']) for row in records
                  if row.get('order') is not None and math.isfinite(float(row['order']))]
        if len(orders) < minimum:
            raise ValueError('Monte Carlo has insufficient valid fractional-order refits.')
        values['order'] = float(np.median(orders))
    caution = (' Zero-order prefactor remains the representative point-fit value; '
               'it is not separately identifiable.' if name == 'zero' else '')
    return values, (f'{name}: medians of {len(records)} successful Monte Carlo refits '
                    f'(seed {mc_result["seed"]}; generating model {mc_result["reference_model"]}). '
                    'Marginal medians are heuristic initial guesses, not a joint fit or '
                    'confidence interval.' + caution)


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
        self.model_equation = EquationCard(sidebar, 'Polanyi–Wigner')
        self.model_equation.pack(fill='x', pady=8)
        help_button(sidebar,app,'polanyi_wigner_fit').pack(anchor='e')
        parameter_topics = {'beta':'heating_rate','energy':'activation_energy',
            'prefactor':'prefactor','order':'reaction_order','coverage':'initial_coverage',
            'amplitude':'signal_scale','baseline':'constant_baseline',
            'max_nfev':'max_evaluations','replicates':'mc_replicates','seed':'mc_seed'}
        for key, label in (('beta','Heating rate (K/s)'), ('energy','Initial / simulated energy (eV)'),
            ('prefactor','Initial / simulated prefactor (s⁻¹)'), ('order','Simulation order (≥0)'),
            ('coverage','Simulation initial coverage (0–1)'), ('amplitude','Simulation signal scale'),
            ('baseline','Simulation constant baseline'), ('max_nfev','Maximum fit evaluations'),
            ('replicates','Monte Carlo replicates (1–10000)'), ('seed','Monte Carlo seed')):
            if key == 'replicates':
                self.mc_equation = EquationCard(sidebar, 'Monte Carlo')
                self.mc_equation.pack(fill='x', pady=(12, 8))
            label_row=ttk.Frame(sidebar)
            label_row.pack(fill='x',pady=(4,0))
            ttk.Label(label_row, text=label).pack(side='left')
            help_button(label_row,app,parameter_topics[key]).pack(side='right')
            ttk.Entry(sidebar, textvariable=self.variables[key]).pack(fill='x')
        for key in ('zero','first','second','fractional','fit_baseline','multistart'):
            option_row=ttk.Frame(sidebar)
            option_row.pack(fill='x')
            ttk.Checkbutton(option_row, text=key.replace('_',' ').capitalize(), variable=self.variables[key]).pack(side='left')
            help_button(option_row,app, {'zero':'fixed_zero_order','first':'reaction_order',
                'second':'reaction_order','fractional':'reaction_order',
                'fit_baseline':'constant_baseline','multistart':'multistart'}[key]).pack(side='right')
        ttk.Label(sidebar, text='Fits normalize initial coverage to one and optimize signal scale. Simulation coverage/amplitude/baseline apply only to manual preview.', wraplength=280).pack(fill='x', pady=8)
        self.calculation_buttons = []
        for title, callback in (('Simulate parameters',self.simulate), ('Compare models',self.compare),
                                ('Use selected / best fit → Kinetic Analysis',self.transfer)):
            button = ttk.Button(sidebar, text=title, command=callback)
            button.pack(fill='x', pady=3)
            self.calculation_buttons.append(button)
        help_button(sidebar,app,'simulation').pack(anchor='e')
        self.components = ComponentsController(self)
        component_actions=ttk.Frame(workspace,padding=(4,4))
        component_actions.pack(fill='x')
        component_button=ttk.Button(component_actions,text='Fit Multiple Peaks…',command=self.components.open)
        component_button.pack(side='left',padx=(0,4))
        help_button(component_actions,app,'simultaneous_components').pack(side='left',padx=(0,8))
        self.calculation_buttons.append(component_button)
        ttk.Button(component_actions,text='Single-state view',command=self.show_single).pack(side='left',padx=4)
        ttk.Button(component_actions,text='Export component fit…',command=self.components.export).pack(side='left')
        self.source_rate_button=ttk.Button(workspace,command=lambda:confirm_source_rate(self))
        self.source_rate_button.pack(fill='x')
        # Keep feedback and cancellation visible even when the parameter sidebar scrolls.
        self.mc_progress = MonteCarloProgress()
        self.mc_active = False
        self.progress_frame = ttk.LabelFrame(workspace, text='Monte Carlo', padding=8)
        self.progress_frame.pack(fill='x')
        self.progress_frame.columnconfigure(0, weight=1)
        self.mc_run = ttk.Button(self.progress_frame, text='Run Monte Carlo', command=self.monte_carlo)
        self.mc_run.grid(row=0, column=1, padx=4)
        self.mc_cancel = ttk.Button(self.progress_frame, text='Cancel', command=self.cancel_job, state='disabled')
        self.mc_cancel.grid(row=0, column=2)
        self.mc_transfer = ttk.Button(self.progress_frame, text='Use MC medians → Kinetic Analysis',
                                      command=lambda: self.transfer(monte_carlo=True))
        self.mc_transfer.grid(row=1, column=3, rowspan=2, padx=4, sticky='n')
        help_button(self.progress_frame,app,'mc_progress').grid(row=0,column=3,padx=4)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky='ew', padx=(0,8))
        self.progress_count = tk.StringVar(app.root)
        self.progress_detail = tk.StringVar(app.root)
        ttk.Label(self.progress_frame, textvariable=self.progress_count).grid(row=1, column=0, columnspan=3, sticky='w')
        self.progress_detail_label = ttk.Label(self.progress_frame, textvariable=self.progress_detail, wraplength=650)
        self.progress_detail_label.grid(row=2, column=0, columnspan=3, sticky='w')
        self.progress_frame.bind('<Configure>',lambda e:self.progress_detail_label.configure(wraplength=max(150,e.width-20)))
        self.update_progress_view()
        # Separate views keep parameters and scientific cautions reachable on
        # smaller displays instead of letting the canvas push them off-screen.
        self.views=ttk.Notebook(workspace)
        self.views.pack(fill='both',expand=True)
        plot_view,table_view,notes_view=(ttk.Frame(self.views) for _ in range(3))
        for view,title in ((plot_view,'Spectrum & residuals'),(table_view,'Parameters & models'),(notes_view,'Assumptions & warnings')):
            self.views.add(view,text=title)
        self.fig = Figure(figsize=(8,5), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_view)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        columns = ('model','order','energy','prefactor','rmse','aicc','warning')
        self.table = ttk.Treeview(table_view, columns=columns, show='headings', height=4)
        labels = ('Model','Order','E (eV)','ν (s⁻¹)','RMSE','Δ AICc','Validity / warnings')
        for col,label in zip(columns,labels):
            self.table.heading(col, text=label, command=lambda c=col:self.sort(c))
            self.table.column(col, width=85 if col != 'warning' else 260, minwidth=60)
        table_view.rowconfigure(1,weight=1)
        table_view.columnconfigure(0,weight=1)
        table_help=ttk.Label(table_view,text='Select a single-state model for transfer. Double-click a component-count row to inspect its fit.',wraplength=650)
        table_help.grid(row=0,column=0,columnspan=2,sticky='ew',padx=6,pady=4)
        table_view.bind('<Configure>',lambda e:table_help.configure(wraplength=max(200,e.width-16)))
        self.table.grid(row=1,column=0,sticky='nsew')
        self.table.bind('<Double-1>',lambda _e:self.components.select_count())
        scroll = ttk.Scrollbar(table_view, orient='horizontal', command=self.table.xview)
        self.table.configure(xscrollcommand=scroll.set)
        scroll.grid(row=2,column=0,sticky='ew')
        vertical=ttk.Scrollbar(table_view,orient='vertical',command=self.table.yview)
        vertical.grid(row=1,column=1,sticky='ns')
        self.table.configure(yscrollcommand=vertical.set)
        notes_view.rowconfigure(0,weight=1)
        notes_view.columnconfigure(0,weight=1)
        self.notes = tk.Text(notes_view, height=6, wrap='word', font=('Segoe UI',10))
        self.notes.grid(row=0,column=0,sticky='nsew')
        note_scroll=ttk.Scrollbar(notes_view,orient='vertical',command=self.notes.yview)
        note_scroll.grid(row=0,column=1,sticky='ns')
        self.notes.configure(yscrollcommand=note_scroll.set)
        for key,var in self.variables.items():
            var.trace_add('write',lambda *_args,k=key:self.changed(k))

    def key(self):
        dataset, region = self.app.project.context()
        return f'{dataset.id}/{region.id}'

    def show_single(self):
        try:
            self.session()['display_mode']='single'
            self.render()
        except ValueError as exc:
            self.app.status.set(str(exc))

    def set_job_busy(self, busy):
        for button in [*self.calculation_buttons, self.mc_run, self.mc_transfer]:
            button.configure(state='disabled' if busy else 'normal')
        self.mc_cancel.configure(state='normal' if busy else 'disabled')

    def cancel_job(self):
        if self.app.job_busy:
            self.app.job_cancel.set()
            if self.mc_active:
                self.mc_progress.state = 'Cancelling'
                self.update_progress_view()
            self.mc_cancel.configure(state='disabled')
            self.app.status.set('Cancelling calculation; previous successful results retained.')

    def update_progress_view(self):
        count, detail = self.mc_progress.text()
        self.progress_count.set(count)
        self.progress_detail.set(detail)
        self.progress_bar.configure(maximum=max(1,self.mc_progress.total), value=self.mc_progress.completed)

    def progress_updated(self, completed, total):
        self.mc_progress.update(completed,total)
        self.update_progress_view()

    def job_finished(self, error=None, cancelled=False):
        if self.mc_active and (error is not None or cancelled):
            self.mc_progress.finish('Cancelled' if cancelled else 'Failed',
                'previous results retained' if cancelled else str(error))
            self.mc_active = False
            self.update_progress_view()

    def tick_progress(self):
        if self.mc_active:
            if self.app.job_cancel.is_set():
                self.mc_progress.state = 'Cancelling'
            self.update_progress_view()

    def session(self):
        return self.app.project.modeling.setdefault(self.key(), {'settings':deepcopy(DEFAULTS)})

    def snapshot(self):
        snap = self.app.project.snapshot('Polanyi–Wigner')
        snap.pop('kinetic_engine_revision',None)
        snap['method'] = 'Model exploration'
        snap['settings'] = deepcopy(self.session()['settings'])
        snap['modeling_engine_revision'] = 'zero-order-profile-v1'
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
            if key in {'beta','energy','prefactor','order','coverage','amplitude','baseline'} and self.session().get('display_mode')!='components':
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
        # A region is an analysis prerequisite, never a prerequisite for viewing data.
        dataset = self.app.project.datasets.get(self.app.project.active_dataset)
        suggestion=source_heating_rate(dataset) if dataset is not None else None
        self.source_rate_button.configure(text=(f"Source suggests {suggestion['beta_K_s']:g} K/s — review and confirm…"
            if suggestion else 'No source heating rate available — verify and enter it in Modeling'),
            state='normal' if suggestion and not self.app.job_busy else 'disabled')
        self.fig.clear()
        ax = self.fig.add_subplot(211)
        residual = self.fig.add_subplot(212)
        ax.set(ylabel='Signal (instrument units)')
        residual.axhline(0,color='gray',linewidth=.7)
        residual.set(xlabel='Temperature (°C)',ylabel='Residual')
        if dataset is not None:
            ax.plot(dataset.spectrum.temperature_clean_c, dataset.spectrum.signal,
                    color='0.5', linewidth=.8, label='Original measured spectrum')
        self.table.delete(*self.table.get_children())
        try:
            session = self.session()
            component_result = session.get('components')
            stale_component = bool(component_result and session.get('display_mode') == 'components'
                                   and not self.components.current(component_result))
            if component_result and session.get('display_mode') == 'components' and not stale_component:
                self.components.render(ax, residual, component_result)
                self.canvas.draw_idle()
                return
            result = session.get('comparison')
            comparison_current = bool(result and self.current(result))
            # A stale result stays in the project for provenance, but must not
            # replace the data from the newly selected peak in the live plot.
            show_comparison = comparison_current and session.get('display_mode') != 'simulation'
            dataset, _ = self.app.project.context()
            t, y = (result['temperature'], result['signal']) if show_comparison else selected_arrays(dataset, self.snapshot())
        except ValueError:
            guidance = ('In Spectra & Preparation, enter a peak name and bounds, then Add peak (or use Drag interval). '
                        'The original spectrum remains visible; calculations need a named region.'
                        if dataset is not None else 'Open a spectrum or use Open Example Dataset to begin.')
            ax.text(.02,.97,guidance,transform=ax.transAxes,va='top',wrap=True,fontsize=9)
            if dataset is not None:
                ax.legend(fontsize=8)
            self.note(guidance)
            self.canvas.draw_idle()
            return
        plot_observations(ax, t, y, label='Comparison input (submitted snapshot)' if show_comparison else 'Selected processed signal')
        plotted_signals = [np.asarray(y, dtype=float)]
        notes = 'A ranking does not prove a mechanism. Single-state fits assume a linear heating ramp and coverage one at the interval start.\nZero-order fits search the depletion edge; displayed prefactors are representative, with conditional ranges rather than unique values. Edge-model AICc rankings are heuristic.\n'
        if stale_component:
            notes += 'STALE component fit — showing the current peak data; refit components for the new interval.\n'
        if result:
            if not comparison_current:
                notes += 'STALE comparison — showing current peak data, not old fitted curves. Re-run Compare models for the changed interval/settings.\n'
            elif show_comparison:
                notes += 'Current comparison.\n'
            else:
                notes += 'A current comparison is retained; manual simulation is shown separately. Click Compare models to return to fitted curves.\n'
            notes += 'Stored comparison interval: ' + str(result['snapshot']['region']) + ' °C; β = ' + str(result['snapshot']['settings']['beta']) + ' K/s\n'
        if show_comparison:
            for index,c in enumerate(result['candidates']):
                fit = c['fit']
                vals = [c['name']] + ([fit['reaction_order'],fit['activation_energy_eV'],fit['prefactor_s_inv'],fit['rmse_signal'],c['delta_aicc']] if fit else ['—']*5)
                self.table.insert('','end',iid=str(index),values=vals+[c['error'] or '; '.join(c['warnings'])])
                if c['prediction'] is not None and not c['error']:
                    predicted = np.asarray(c['prediction'], dtype=float)
                    plotted_signals.append(predicted)
                    ax.plot(t,predicted,linestyle=('-', '--', '-.', ':')[index%4],
                            linewidth=1.5,label=c['name'])
                    residual.plot(t,np.asarray(y)-predicted,label=c['name'])
        simulation = session.get('simulation')
        if simulation and self.current(simulation) and not show_comparison:
            prediction = np.asarray(simulation['prediction'], dtype=float)
            plotted_signals.append(prediction)
            ax.plot(simulation['temperature'], prediction, '--', label='Manual simulation (not fitted)')
            observed_scale = max(float(np.max(np.abs(y))), 1e-12)
            if float(np.max(np.abs(prediction))) > 20 * observed_scale:
                notes += 'Manual simulation greatly exceeds measured signal; adjust Simulation signal scale. This is not a fitted curve.\n'
        mc = session.get('monte_carlo')
        if mc:
            r = mc['result']
            notes += f"Monte Carlo seed {r['seed']}; {r['replicates_completed']}/{r['replicates_requested']} replicates; failed rankings {r['failed_rankings']}. "
            notes += json.dumps(r['winning_counts']) + '\n' + r['interval_note'] + '\n'
            notes += 'Conditional parameter ranges: ' + json.dumps(r['parameter_intervals']) + '\n'
            notes += ('MC settings are current. ' if self.current(mc) else 'MC settings are stale. ')
        notes += 'Monte Carlo uses iid Gaussian residual noise around the lowest-AICc converged reference; ranges withheld below 100 successful refits. Frequencies are not mechanism probabilities.'
        # Always focus the live axes on the selected peak, not the full source
        # spectrum or the previous interval. Autoscale from visible data and
        # displayed curves, excluding hidden/stale simulations.
        temperature = np.asarray(t, dtype=float)
        finite_t = temperature[np.isfinite(temperature)]
        if finite_t.size:
            low_t, high_t = float(finite_t.min()), float(finite_t.max())
            pad_t = max((high_t - low_t) * .025, .01)
            for axis in (ax, residual):
                axis.set_xlim(low_t - pad_t, high_t + pad_t)
        finite_y = [array[np.isfinite(array)] for array in plotted_signals]
        finite_y = [array for array in finite_y if array.size]
        if finite_y:
            values = np.concatenate(finite_y)
            low_y, high_y = float(values.min()), float(values.max())
            pad_y = max((high_y - low_y) * .08, max(abs(low_y), abs(high_y)) * .02, 1e-9)
            ax.set_ylim(low_y - pad_y, high_y + pad_y)
        ax.legend(fontsize=7,ncol=2)
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
        if kind == 'monte_carlo':
            r = result['result']
            if r['cancelled']:
                self.mc_progress.update(r['replicates_completed'],r['replicates_requested'])
                self.job_finished(cancelled=True)
                self.app.status.set('Monte Carlo cancelled; previous successful results retained.')
                return
            successful = sum(r['successful_parameter_fits'].values())
            attempted = r['replicates_completed'] * len(r['successful_parameter_fits'])
            summary = (f"{successful} successful / {attempted-successful} failed fitting attempts; "
                       f"{r['failed_rankings']} incomplete rankings; seed {r['seed']}")
            self.mc_progress.update(r['replicates_completed'],r['replicates_requested'])
            self.mc_progress.finish('Completed',summary)
            self.mc_active = False
            self.update_progress_view()
        snap = result['snapshot']
        key = f"{snap['dataset_id']}/{snap['region_id']}"
        session = self.app.project.modeling[key]
        session[kind] = result
        if kind in ('comparison', 'components', 'simulation'):
            session['display_mode'] = kind
        if kind == 'comparison':
            session.pop('monte_carlo',None)
        self.render()
        self.app.status.set(('Monte Carlo finished: ' + summary) if kind == 'monte_carlo' else
                            kind.replace('_',' ').capitalize() + ' finished; results retain submitted settings.')

    def monte_carlo(self):
        if self.app.job_busy:
            self.app.status.set('A calculation is already running; finish or cancel it first.')
            return
        try:
            if self.session().get('display_mode')=='components':
                raise ValueError('Component Monte Carlo is not implemented. Single-state view uses the separate order comparison; component intervals are conditional local estimates.')
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
                    progress=lambda done,total:self.app.jobs.put(('progress', (done,total))))
                return serial(dict(snapshot=snap,result=result))
            self.mc_active = True
            self.mc_progress.start(replicates)
            self.update_progress_view()
            if not self.app.start_job(work,lambda r:self.complete('monte_carlo',r)):
                self.job_finished(error=self.app.status.get())
        except (ValueError,KeyError) as exc:
            self.app.status.set(str(exc))

    def transfer(self, monte_carlo=False):
        """Carry current fitted guesses into the same peak's kinetic workspace."""
        try:
            if self.app.job_busy:
                raise ValueError('Wait for the running calculation before transferring parameters.')
            session = self.session()
            if session.get('display_mode') == 'components':
                raise ValueError('Simultaneous components are not single-state starting guesses. '
                                 'Switch to Single-state view first.')
            result = session.get('comparison')
            if not result or not self.current(result):
                raise ValueError('Compare current settings before transferring a candidate.')
            mc = session.get('monte_carlo') if monte_carlo else None
            if monte_carlo and (not mc or not self.current(mc)):
                raise ValueError('Run Monte Carlo on the current comparison before transferring medians.')
            candidates = result['candidates']
            selection = self.table.selection()
            selected = next((candidates[int(item)] for item in selection
                             if item.isdigit() and int(item) < len(candidates)), None)
            if selected is None:
                preferred = mc['result']['reference_model'] if mc else None
                selected = next((row for row in candidates if row['name'] == preferred
                                 and row['fit'] and not row['error']), None)
                if selected is None:
                    selected = next((row for row in candidates if row['fit'] and not row['error']), None)
            if selected is None:
                raise ValueError('No converged model is available for transfer.')
            values, description = transfer_starting_values(selected, mc['result'] if mc else None)
            settings = self.app.project.method_settings('Polanyi–Wigner')
            settings.update(beta=result['snapshot']['settings']['beta'],
                            energy=values['energy'], prefactor=values['prefactor'],
                            order=values['order'], free_order=values['free_order'],
                            fit_baseline=result['snapshot']['settings']['fit_baseline'])
            session['selected_hypothesis'] = deepcopy(selected)
            session['kinetic_transfer'] = {'model': selected['name'],
                                           'description': description,
                                           'source': 'monte_carlo' if monte_carlo else 'point_fit'}
            self.app.method.set('Polanyi–Wigner')
            self.app.stages.select(2)
            self.app.refresh_context()
            self.app.status.set('Starting values transferred: ' + description)
        except (ValueError, KeyError, OverflowError) as exc:
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
