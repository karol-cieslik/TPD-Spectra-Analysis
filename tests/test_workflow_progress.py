"""Progress, cancellation, failure and event-loop responsiveness with real Tk."""
import threading
import time
import numpy as np
from tpd_spectra.job_progress import MonteCarloProgress
from tpd_spectra.workflow_gui import WorkflowApp
from tpd_spectra.workflow_analysis import serial
from tpd_spectra.kinetics_uncertainty import MonteCarloResult, run_kinetics_monte_carlo
from tpd_spectra.kinetics import simulate_tpd


def pump(root, predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        root.update()
        time.sleep(.005)
    assert predicate(), 'GUI/worker did not reach expected state'


def result(completed, total, *, cancelled=False):
    return MonteCarloResult('first', 42, total, completed, .01,
        {'first': completed}, 0, {'first': {}}, {'first': completed}, cancelled)


def prepared(root):
    app = WorkflowApp(root)
    app.open_default_demo()
    panel = app.modeling_panel
    panel.session()['comparison'] = dict(snapshot=panel.snapshot(),
        temperature=[70., 71., 72.], signal=[0., .2, 0.], candidates=[])
    panel.session()['monte_carlo'] = serial(dict(snapshot=panel.snapshot(),result=result(2,2)))
    app.stages.select(1)
    root.state('normal')
    root.geometry('1100x720')
    root.update()
    return app, panel


def test_progress_time_and_eta_are_explicit(monkeypatch):
    clock = [100.]
    monkeypatch.setattr('tpd_spectra.job_progress.monotonic',lambda:clock[0])
    progress = MonteCarloProgress()
    progress.start(500)
    clock[0] += 47.
    progress.update(237,500)
    count, detail = progress.text()
    assert '237 / 500' in count and '(47%)' in count
    assert 'Elapsed 00:47' in detail and 'estimated remaining 00:52' in detail
    progress.finish('Cancelled','previous results retained')
    clock[0] += 10
    assert 'Elapsed 00:47' in progress.text()[1]


def test_500_step_progress_is_visible_responsive_cancelable_and_retains_results(root,monkeypatch):
    app,panel = prepared(root)
    previous = panel.session()['monte_carlo']
    comparison = panel.session()['comparison']
    raw = app.project.context()[0].spectrum.signal.copy()
    release = threading.Event()
    worker_ids, ui_ids = [], []
    update = panel.progress_updated
    def main_thread_update(*args):
        ui_ids.append(threading.get_ident())
        update(*args)
    monkeypatch.setattr(panel,'progress_updated',main_thread_update)
    def fake_engine(*args,progress,cancelled,**kwargs):
        worker_ids.append(threading.get_ident())
        for done in range(1,238):
            progress(done,500)
        assert release.wait(8)
        assert cancelled()
        return result(237,500,cancelled=True)
    monkeypatch.setattr('tpd_spectra.workflow_modeling.run_kinetics_monte_carlo',fake_engine)
    panel.monte_carlo()
    worker = app.workflow_worker
    pump(root,lambda:panel.mc_progress.completed == 237)
    assert panel.progress_bar.winfo_ismapped()
    assert panel.mc_cancel.winfo_ismapped()
    assert panel.views.winfo_ismapped()
    panel.views.select(1)
    root.update()
    assert panel.table.winfo_ismapped()
    panel.views.select(2)
    root.update()
    assert panel.notes.winfo_ismapped()
    panel.views.select(0)
    root.update()
    assert panel.canvas.get_tk_widget().winfo_height()>150
    assert '237 / 500' in panel.progress_count.get() and '(47%)' in panel.progress_count.get()
    assert panel.mc_run.instate(['disabled'])
    assert all(button.instate(['disabled']) for button in panel.calculation_buttons)
    heartbeat = []
    root.after(1,lambda:heartbeat.append(True))
    pump(root,lambda:bool(heartbeat))
    panel.monte_carlo()
    panel.compare()
    assert app.workflow_worker is worker
    panel.mc_cancel.invoke()
    assert panel.mc_progress.state == 'Cancelling'
    release.set()
    pump(root,lambda:not app.job_busy)
    assert panel.mc_progress.state == 'Cancelled'
    assert panel.mc_progress.completed == 237
    assert panel.session()['monte_carlo'] is previous
    assert panel.session()['comparison'] is comparison
    assert panel.mc_run.instate(['!disabled'])
    assert panel.mc_cancel.instate(['disabled'])
    assert set(ui_ids) == {threading.get_ident()}
    assert worker_ids[0] != threading.get_ident()
    observed = [line for line in panel.fig.axes[0].lines if line.get_label()=='Original measured spectrum']
    np.testing.assert_array_equal(observed[0].get_ydata(),raw)


def test_completion_counts_fit_attempts_separately_from_rankings_and_error_retry(root,monkeypatch):
    app,panel = prepared(root)
    panel.variables['replicates'].set('5')
    # Re-snapshot so the synthetic comparison remains current after controls restore.
    panel.session()['comparison']['snapshot'] = panel.snapshot()
    def complete(*args,progress,**kwargs):
        for done in range(1,6):
            progress(done,5)
        return MonteCarloResult('first',42,5,5,.01,{'first':3,'second':0},2,
            {'first':{},'second':{}},{'first':4,'second':3},False)
    monkeypatch.setattr('tpd_spectra.workflow_modeling.run_kinetics_monte_carlo',complete)
    panel.monte_carlo()
    pump(root,lambda:not app.job_busy)
    assert panel.mc_progress.state == 'Completed'
    assert '(100%)' in panel.progress_count.get()
    assert '7 successful / 3 failed fitting attempts' in panel.progress_detail.get()
    assert '2 incomplete rankings' in panel.progress_detail.get()
    previous = panel.session()['monte_carlo']
    def fail(*args,**kwargs):
        raise ValueError('deliberate replicate failure')
    monkeypatch.setattr('tpd_spectra.workflow_modeling.run_kinetics_monte_carlo',fail)
    panel.monte_carlo()
    pump(root,lambda:not app.job_busy)
    assert panel.mc_progress.state == 'Failed'
    assert 'deliberate replicate failure' in panel.progress_detail.get()
    assert panel.session()['monte_carlo'] is previous
    assert panel.mc_run.instate(['!disabled'])


def test_cancel_after_worker_queued_success_prevents_commit(root):
    app,panel = prepared(root)
    committed = []
    assert app.start_job(lambda:'must not commit',committed.append)
    app.workflow_worker.join(5)
    assert not app.workflow_worker.is_alive()
    app.job_cancel.set()
    app.poll_jobs()
    assert not app.job_busy
    assert not committed
    assert 'cancelled' in app.status.get()


def test_engine_reported_cancellation_preserves_previous_result_without_event(root,monkeypatch):
    app,panel = prepared(root)
    previous = panel.session()['monte_carlo']
    monkeypatch.setattr('tpd_spectra.workflow_modeling.run_kinetics_monte_carlo',
                        lambda *args,**kwargs:result(1,500,cancelled=True))
    panel.monte_carlo()
    pump(root,lambda:not app.job_busy)
    assert not app.job_cancel.is_set()
    assert panel.mc_progress.state == 'Cancelled'
    assert panel.mc_progress.completed == 1
    assert panel.session()['monte_carlo'] is previous
    assert 'cancelled' in app.status.get()


def test_real_seeded_engine_cancels_after_completed_refit():
    temperature = np.linspace(80.,340.,65)
    _,rate = simulate_tpd(temperature,1.,1.1,1e12,1.)
    signal = 2 + 1e4*rate + np.random.default_rng(12).normal(0,.02,temperature.size)
    updates = []
    cancellation = threading.Event()
    def progress(done,total):
        updates.append((done,total))
        cancellation.set()
    mc = run_kinetics_monte_carlo(temperature,signal,1.,orders=('first',),
        replicates=500,seed=42,max_nfev=50,progress=progress,cancelled=cancellation.is_set)
    assert updates == [(1,500)]
    assert mc.cancelled and mc.replicates_completed == 1
    assert sum(mc.winning_counts.values()) + mc.failed_rankings == 1
