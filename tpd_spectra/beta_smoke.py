"""Exercise resources and offline feedback in the assembled frozen package."""
from pathlib import Path
import json
import tkinter as tk
from zipfile import ZipFile
from .analysis import load_spectrum
from .beta_resources import resource
from .feedback_gui import FeedbackDialog
from .feedback import save_zip
from .identity import build_identity, about_text
from .workflow_gui import WorkflowApp


def main(output):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    catalog=json.loads(resource('examples/beta_collection/catalog.json').read_text(encoding='utf-8'))
    assert len(catalog)>=19
    assert {'first_order_low_noise.csv','first_order_moderate_noise.csv','first_order_high_noise.csv'} <= {entry['file'] for entry in catalog}
    for entry in catalog:
        assert len(load_spectrum(resource('examples/beta_collection/'+entry['file'])).signal)==801
    assert resource('docs/beta/QUICK_START.pdf').read_bytes().startswith(b'%PDF')
    assert resource('START_HERE.md').is_file()
    root=tk.Tk()
    app=WorkflowApp(root)
    errors=[]
    root.report_callback_exception=lambda *args:errors.append(str(args))
    try:
        dialog=app.open_example()
        dialog.open()
        app.stages.select(2)
        app.preview_selected()
        root.update()
        assert abs(app.displayed_result['values']['energy_ev']/1.2-1)<.025
        feedback=FeedbackDialog(app)
        root.update()
        report=feedback.report()
        assert 'first_order_single_peak' not in report
        assert str(resource('examples')) not in report
        feedback.copy()
        assert root.clipboard_get()==report
        zip_path=output/'diagnostics.zip'
        save_zip(zip_path,report)
        with ZipFile(zip_path) as archive:
            assert set(archive.namelist())=={'README.txt','feedback-report.txt'}
            assert archive.read('feedback-report.txt').decode()==report
        assert 'karol.j.cieslik@gmail.com' in about_text()
        feedback.win.destroy()
        # Exercise zero order through the actual frozen workflow and report path.
        import time
        import numpy as np
        from .workflow_io import save_project,load_project
        from .workflow_report import export_report
        from .kinetics_uncertainty import run_kinetics_monte_carlo
        example=app.open_example()
        example.list.selection_clear(0,'end')
        example.list.selection_set(0)
        example.open()
        app.method.set('Polanyi–Wigner')
        app.project.method_settings('Polanyi–Wigner').update(order=0.,fit_baseline=False)
        app.refresh_context()
        app.calculate_selected()
        deadline=time.monotonic()+120
        while app.job_busy and time.monotonic()<deadline:
            root.update()
            time.sleep(.02)
        assert not app.job_busy
        assert app.displayed_result['values']['normalized_rmse']<.02
        assert app.displayed_result['values']['conditional_prefactor_range_s_inv']
        saved=app.project.save_result(app.displayed_result,'Frozen zero-order profile')
        loaded=load_project(save_project(app.project,output/'zero-order.tpd.json'))
        export_report(loaded,[saved['id']],output/'zero-order-report')
        assert (output/'zero-order-report/COMPLETE.txt').exists()
        data,_=app.project.context()
        t=data.spectrum.temperature_clean_c[::4]
        y=data.spectrum.signal[::4]
        noisy=y+np.random.default_rng(91).normal(0,.01*np.ptp(y),len(y))
        mc=run_kinetics_monte_carlo(t,noisy,1.,orders=('zero',),replicates=2,
            seed=42,fit_baseline=False,minimum_successful_refits=2)
        assert mc.successful_parameter_fits['zero']==2
        assert 'log10_prefactor' not in mc.parameter_intervals['zero']
        assert not errors,errors
        record={'identity':build_identity(),'examples_imported':len(catalog),
            'resource_lookup_from_unrelated_cwd':True,'redhead_reference_passed':True,
            'offline_feedback_copy_zip_passed':True,'external_drafts_opened':False,
            'zero_order_gui_fit_project_report_and_short_mc_passed':True,
            'callback_errors':errors,'visual_acceptance':'not assessed by automation'}
        (output/'beta_smoke.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        print(f'Frozen external beta: {len(catalog)} imports, bundled guide, example chooser, Redhead preview, offline feedback copy/ZIP and contact passed',flush=True)
        print('Frozen zero order: explicit GUI fit, conditional ranges, project, report and two MC refits passed',flush=True)
    finally:
        for callback in root.tk.call('after','info'):
            root.after_cancel(callback)
        root.destroy()
    return 0
