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
    assert len(catalog)==16
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
        assert not errors,errors
        record={'identity':build_identity(),'examples_imported':len(catalog),
            'resource_lookup_from_unrelated_cwd':True,'redhead_reference_passed':True,
            'offline_feedback_copy_zip_passed':True,'external_drafts_opened':False,
            'callback_errors':errors,'visual_acceptance':'not assessed by automation'}
        (output/'beta_smoke.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        print('Frozen external beta: 16 imports, bundled guide, example chooser, Redhead preview, offline feedback copy/ZIP and contact passed',flush=True)
    finally:
        for callback in root.tk.call('after','info'):
            root.after_cancel(callback)
        root.destroy()
    return 0
