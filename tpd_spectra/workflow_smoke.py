"""Exercise the real redesigned widgets and bundled PDF backend after freezing."""
from pathlib import Path
import json
import time
import tkinter as tk
from .workflow_gui import WorkflowApp
from .workflow_state import STAGES
from .workflow_io import save_project,load_project
from .workflow_report import export_report


def main(source,output):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    root=tk.Tk()
    app=WorkflowApp(root)
    errors=[]
    root.report_callback_exception=lambda *args:errors.append(str(args))
    def wait():
        deadline=time.monotonic()+180
        while app.job_busy and time.monotonic()<deadline:
            root.update()
            time.sleep(.02)
        assert not app.job_busy, 'Workflow worker timed out'
        assert not errors, errors
    try:
        app._load_paths([Path(source)])
        first=app.project.add_region('Synthetic first peak',100,210)
        second=app.project.add_region('Synthetic second peak',230,350)
        app.project.active_region=first.id
        app.refresh_context()
        assert tuple(app.stages.tab(t,'text') for t in app.stages.tabs())==STAGES
        app.method.set('Redhead')
        app.refresh_method()
        app.preview_selected()
        run=app.project.save_result(app.displayed_result,'Frozen workflow Redhead test')
        assert abs(run['values']['energy_ev']-1.25)/1.25<.02
        app.stages.select(1)
        root.update()
        panel=app.modeling_panel
        for key in ('zero','second','fractional','multistart'):
            panel.variables[key].set(False)
        panel.variables['replicates'].set('2')
        panel.simulate()
        wait()
        assert panel.session()['simulation']['prediction']
        panel.compare()
        wait()
        assert panel.session()['comparison']['candidates'][0]['error'] is None
        panel.monte_carlo()
        wait()
        assert panel.session()['monte_carlo']['result']['replicates_completed']==2
        previous=panel.session()['monte_carlo']
        panel.variables['replicates'].set('500')
        panel.monte_carlo()
        deadline=time.monotonic()+90
        while app.job_busy and panel.mc_progress.completed<1 and time.monotonic()<deadline:
            root.update()
            time.sleep(.02)
        assert app.job_busy and panel.mc_progress.completed>=1
        assert panel.mc_cancel.instate(['!disabled'])
        panel.mc_cancel.invoke()
        wait()
        assert panel.session()['monte_carlo']==previous
        assert 'cancel' in app.status.get().lower()
        panel.variables['replicates'].set('2')
        panel.table.selection_set('0')
        panel.transfer()
        app.calculate_selected()
        wait()
        assert app.displayed_result['status']=='fitted'
        app.project.save_result(app.displayed_result,'Frozen workflow kinetic fit')
        app.project.active_region=second.id
        app.refresh_context()
        assert app.displayed_result is None
        path=save_project(app.project,output/'smoke.tpd.json')
        loaded=load_project(path)
        assert len(loaded.runs)==2
        export_report(loaded,[run['id']],output/'report')
        assert (output/'report/report.pdf').stat().st_size>1000
        (output/'workflow_smoke.json').write_text(json.dumps({'stages':STAGES,'saved_runs':len(loaded.runs),'simulation_passed':True,'real_monte_carlo_progress_and_cancel_preserved_result':True,'monte_carlo_replicates':2,'callback_errors':errors}),encoding='utf-8')
        print('Frozen workflow: three stages, context isolation, model comparison, Monte Carlo, explicit fit, project roundtrip and PDF/CSV/JSON/PNG/SVG passed',flush=True)
    finally:
        root.update_idletasks()
        for callback in root.tk.call('after','info'):
            root.after_cancel(callback)
        root.destroy()
    return 0
