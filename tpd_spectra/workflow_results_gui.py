"""Method-scoped results controller and cancellable background work."""
from copy import deepcopy
import queue
import threading
import tkinter as tk
from tkinter import ttk, simpledialog
from .workflow_analysis import calculate, draw_result
from .result_view import parameter_rows, scientific_notes


class ResultsMixin:
    def setup_results(self):
        self.jobs = queue.Queue()
        self.job_cancel = threading.Event()
        self.job_busy = False
        self.preview_after = None
        self.displayed_result = None
        actions = self.method_action_frame
        self.fit_button = ttk.Button(actions, text='Calculate / Fit selected peak', command=self.calculate_selected)
        self.fit_button.pack(fill='x', pady=4)
        self.cancel_fit = ttk.Button(actions, text='Cancel calculation', command=self.job_cancel.set, state='disabled')
        self.cancel_fit.pack(fill='x')
        self.show_annotation = tk.BooleanVar(self.root,value=True)
        ttk.Checkbutton(actions,text='Show estimate on plot',variable=self.show_annotation,command=self.restore_result).pack(anchor='w',pady=4)
        ttk.Button(actions, text='Save labeled result…', command=self.save_current_result).pack(fill='x', pady=4)
        self.saved_choice = tk.StringVar(self.root)
        self.saved_combo = ttk.Combobox(actions, textvariable=self.saved_choice, state='readonly')
        self.saved_combo.pack(fill='x')
        ttk.Button(actions, text='Reopen saved run', command=self.reopen_selected_run).pack(fill='x', pady=3)
        ttk.Button(actions, text='Delete selected saved run', command=self.delete_selected_run).pack(fill='x')
        for var in [*self.method_values.values(), *self.method_flags.values()]:
            var.trace_add('write', self.method_edited)
        self.root.after(100, self.poll_jobs)

    def result_message(self, text):
        self.result_text.configure(state='normal')
        self.result_text.delete('1.0', 'end')
        self.result_text.insert('end', text)
        self.result_text.configure(state='disabled')

    def copy_result_summary(self):
        """Copy only the submitted result; no implicit recomputation or export mutation."""
        if self.displayed_result is None:
            self.status.set('Calculate a result before copying parameters.')
            return
        result = self.displayed_result
        current = self.project.result_is_current(result)
        lines = [f"{result['snapshot']['method']} — {'CURRENT' if current else 'STALE'}",
                 f"Peak: {result['snapshot'].get('peak', '')}",
                 f"Dataset: {result['snapshot'].get('dataset', '')}",
                 'Parameter\tValue\tUnit\tHow obtained']
        lines += ['\t'.join(row) for row in parameter_rows(result)]
        lines += ['', scientific_notes(result, current)]
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(lines))
        self.status.set('Parameter summary and scientific cautions copied to clipboard.')

    def method_edited(self, *_):
        if self.restoring:
            return
        try:
            settings = self.project.method_settings(self.method.get())
            # Keep incomplete edits as text so a context switch never loses them.
            settings.update({k: v.get() for k, v in self.method_values.items()})
            settings.update({k: v.get() for k, v in self.method_flags.items()})
        except ValueError:
            return
        self.restore_result()
        self.schedule_preview()

    def schedule_preview(self):
        if self.preview_after is not None:
            self.root.after_cancel(self.preview_after)
        self.preview_after = None
        if self.method.get() != 'Polanyi–Wigner':
            self.preview_after = self.root.after(400, self.preview_selected)

    def preview_selected(self):
        self.preview_after = None
        if self.method.get() == 'Polanyi–Wigner':
            return
        try:
            dataset, _ = self.project.context()
            result = calculate(dataset, self.project.snapshot(self.method.get()))
            self.project.accept_result(result)
            self.restore_result()
        except (ValueError, KeyError, TypeError, OverflowError) as exc:
            self.diagnostic_log.record('Preview unavailable',str(exc),exc)
            self.restore_result()
            self.result_message(f'Preview unavailable: {exc}\nPrevious successful result, if shown, is retained with its original settings.')

    def start_job(self, function, on_success):
        if self.job_busy:
            self.status.set('A calculation is already running; finish or cancel it first.')
            return False
        if self.classic and self.classic.root.winfo_exists():
            self.status.set('Close the classic workspace before running a workflow calculation (the numerical integrator is not reentrant).')
            return False
        self.job_busy = True
        self.job_cancel.clear()
        self.fit_button.configure(state='disabled')
        self.cancel_fit.configure(state='normal')
        self.modeling_panel.set_job_busy(True)
        def work():
            try:
                value = function()
                if self.job_cancel.is_set():
                    raise InterruptedError('Cancelled; previous successful results retained.')
                self.jobs.put(('done', (on_success, value)))
            except InterruptedError as exc:
                self.jobs.put(('cancelled', str(exc)))
            except Exception as exc:
                self.diagnostic_log.record('Calculation stopped',str(exc),exc)
                self.jobs.put(('error', str(exc)))
        self.workflow_worker = threading.Thread(target=work, daemon=True)
        self.workflow_worker.start()
        return True

    def poll_jobs(self):
        try:
            while True:
                kind, payload = self.jobs.get_nowait()
                if kind == 'progress':
                    if isinstance(payload, tuple):
                        self.modeling_panel.progress_updated(*payload)
                        self.status.set(self.modeling_panel.progress_count.get())
                    else:
                        self.status.set(payload)
                    continue
                # Cancellation may arrive after the worker queued success but before
                # this GUI-thread commit. Never replace valid results in that race.
                cancelled = kind == 'cancelled' or self.job_cancel.is_set()
                self.job_busy = False
                self.fit_button.configure(state='normal')
                self.cancel_fit.configure(state='disabled')
                self.modeling_panel.set_job_busy(False)
                if cancelled:
                    self.modeling_panel.job_finished(cancelled=True)
                    self.status.set('Calculation cancelled; previous successful results retained.')
                elif kind == 'done':
                    self.diagnostic_log.record('Calculation finished','Background calculation returned successfully.')
                    callback, value = payload
                    callback(value)
                else:
                    self.modeling_panel.job_finished(error=payload)
                    self.status.set('Calculation stopped: ' + payload)
        except queue.Empty:
            pass
        self.modeling_panel.tick_progress()
        self.root.after(100, self.poll_jobs)

    def calculate_selected(self):
        if self.method.get() != 'Polanyi–Wigner':
            self.preview_selected()
            return
        try:
            dataset, _ = self.project.context()
            snapshot = self.project.snapshot(self.method.get())
        except ValueError as exc:
            self.status.set(str(exc))
            return
        if self.start_job(lambda: calculate(dataset, snapshot, self.job_cancel.is_set), self.complete_fit):
            self.status.set('Fitting selected peak… parameters and results retain the submitted snapshot.')

    def complete_fit(self, result):
        self.project.accept_result(result)
        self.restore_result()
        self.status.set('Fit finished. Stored under its submitted dataset, peak and method.'
                        + ('' if self.project.result_is_current(result) else ' Settings/context changed; result is stale for the current selection.'))

    def restore_result(self):
        if not hasattr(self, 'jobs'):
            return
        self.displayed_result = None
        self.result_table.delete(*self.result_table.get_children())
        self.result_figure.clear()
        try:
            result = self.project.current_results.get(self.project.key(self.method.get()))
        except ValueError:
            result = None
        if result:
            self.displayed_result = deepcopy(result)
            current = self.project.result_is_current(result)
            status = result['status'].upper() if current else 'STALE — original settings shown; recalculate for current inputs'
            self.result_state.set(status + ' · ' + result['snapshot']['method'])
            draw_result(self.result_figure, result, self.project.datasets.get(self.project.active_dataset))
            self.result_figure.suptitle(status, fontsize=9)
            values=result['values']
            energy=values.get('energy_ev',values.get('activation_energy_eV'))
            if self.show_annotation.get() and energy is not None:
                self.result_figure.axes[0].text(.02,.97,f'E = {energy:.6g} eV\n'+result['snapshot']['method'],
                    transform=self.result_figure.axes[0].transAxes,va='top',fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.5',facecolor='white',edgecolor='#087E8B',alpha=.9))
            for row in parameter_rows(result):
                self.result_table.insert('', 'end', values=row)
            self.result_message(scientific_notes(result, current))
        else:
            self.result_state.set('Not calculated for this dataset / peak / method.')
            self.result_message('Not calculated for this dataset / peak / method.\n\n'
                                'Select a named peak and method, then calculate or fit.\n'
                                'Model comparisons and Monte Carlo results remain in Modeling & Order Identification.')
            dataset = self.project.datasets.get(self.project.active_dataset)
            if dataset is not None:
                ax = self.result_figure.add_subplot(111)
                ax.plot(dataset.spectrum.temperature_clean_c, dataset.spectrum.signal,
                        color='0.5', linewidth=.8, label='Original measured spectrum')
                ax.set(xlabel='Temperature (°C)', ylabel='Signal (instrument units)')
                ax.legend(fontsize=8)
        self.result_canvas.draw_idle()
        self.refresh_saved_runs()

    def refresh_saved_runs(self):
        self.saved_ids = list(self.project.runs)
        self.saved_combo.configure(values=[self.project.runs[i]['label'] for i in self.saved_ids])
        self.refresh_report_action()

    def save_current_result(self):
        if self.displayed_result is None:
            self.status.set('Calculate a result before saving a run.')
            return
        label = simpledialog.askstring('Save analysis run', 'Run label (original settings are preserved):', parent=self.root)
        if label is not None:
            self.project.save_result(self.displayed_result, label)
            self.refresh_saved_runs()
            self.saved_combo.current(len(self.saved_ids)-1)
            self.status.set('Analysis run saved. Use Report / Export at the top to generate the report bundle.')

    def reopen_selected_run(self):
        index = self.saved_combo.current()
        if index >= 0:
            self.method.set(self.project.reopen_run(self.saved_ids[index]))
            self.refresh_context()

    def delete_selected_run(self):
        index = self.saved_combo.current()
        if index >= 0:
            del self.project.runs[self.saved_ids[index]]
            self.saved_choice.set('')
            self.refresh_saved_runs()

    def _finish_close(self):
        if getattr(self.modeling_panel,'preview_after',None) is not None:
            self.root.after_cancel(self.modeling_panel.preview_after)
            self.modeling_panel.preview_after=None
        if getattr(self, 'job_busy', False):
            self.job_cancel.set()
            self.status.set('Cancelling calculation before closing…')
            self.root.after(100, self._finish_close)
            return
        if self.classic and self.classic.root.winfo_exists():
            if self.classic.running:
                self.classic.close_after_run = True
                self.classic._cancel_run()
                self.root.after(100, self._finish_close)
                return
            self.classic._finish_close()
            if self.classic.root.winfo_exists():
                self.root.after(100, self._finish_close)
                return
        super()._finish_close()
