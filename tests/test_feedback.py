import json
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse,parse_qs
from zipfile import ZipFile
import pytest
from tpd_spectra.feedback import DiagnosticLog,diagnostics,sanitize,compose_report,save_zip,email_url,github_url,SUBJECT
from tpd_spectra.feedback_gui import FeedbackDialog
from tpd_spectra.workflow_gui import WorkflowApp

DEMO=Path(__file__).resolve().parents[1]/'examples/synthetic_two_peak_demo.csv'


@pytest.mark.parametrize('private',[r'C:\Users\Alice\Private Lab\sample.csv','/home/alice/private/sample.csv',r'\\lab-server\secret\sample.csv','file:///home/alice/secret.csv','alice@example.org','token=abcdef12345','sample.csv'])
def test_redaction_removes_private_values(private):
    clean=sanitize('Failure: '+private)
    assert 'Alice' not in clean and 'alice' not in clean and 'sample.csv' not in clean and 'abcdef12345' not in clean


def test_diagnostic_allowlist_excludes_spectrum_labels_paths_and_extra_fields(root):
    app=WorkflowApp(root)
    app._load_paths([DEMO])
    app.project.add_region('Private sample X',100,210)
    settings=app.project.method_settings('Leading edge')
    settings.update(energy='C:/Users/Alice/secrets.csv',private_token='abc123',raw_signal=[1,2,3])
    app.diagnostic_log.record('error',f'Could not fit Private sample X in {DEMO.name}')
    report=json.dumps(diagnostics(app))
    assert 'Private sample X' not in report and DEMO.name not in report
    assert 'raw_signal' not in report and 'abc123' not in report and 'Alice' not in report
    assert 'invalid numeric input' in report
    assert str(DEMO) not in report and 'source_sha256' not in report
    assert 'Leading edge' in report


def test_report_zip_is_exact_reviewed_text_and_contains_no_files(tmp_path):
    report=compose_report('Question','My question','Optional steps','reply@example.org',{'version':'test'})
    path=tmp_path/'diagnostics.zip'
    save_zip(path,report)
    with ZipFile(path) as archive:
        assert set(archive.namelist())=={'feedback-report.txt','README.txt'}
        assert archive.read('feedback-report.txt').decode()==report
    with pytest.raises(FileExistsError):
        save_zip(path,'replacement')
    url=urlparse(email_url(report))
    assert url.path=='karol.j.cieslik@gmail.com'
    assert parse_qs(url.query)=={'subject':[SUBJECT],'body':[report]}
    assert urlparse(github_url(report)).netloc=='github.com'


def test_bounded_exception_log_omits_local_values_and_source_code():
    log=DiagnosticLog()
    for i in range(40):
        log.record('status',str(i))
    try:
        private_measurement='never include this local variable'
        raise ValueError('Failed in C:/Users/Alice/private.csv')
    except ValueError as exc:
        log.record('failure',str(exc),exc)
    data=log.snapshot()
    assert len(data)==30
    serialized=json.dumps(data)
    assert private_measurement not in serialized and 'Alice' not in serialized
    assert data[-1]['exception_type']=='ValueError' and data[-1]['frames']


def test_feedback_preview_copy_zip_draft_and_failure_are_safe(root,tmp_path,monkeypatch):
    app=WorkflowApp(root)
    dialog=FeedbackDialog(app)
    root.update()
    dialog.description.insert('1.0','A test report with a literal line break.\nSecond line.')
    dialog.contact.set('tester@example.org')
    dialog.refresh()
    report=dialog.report()
    assert 'Second line.' in report
    dialog.copy()
    assert root.clipboard_get()==report
    path=tmp_path/'report.zip'
    monkeypatch.setattr('tpd_spectra.feedback_gui.filedialog.asksaveasfilename',lambda **_:str(path))
    dialog.save()
    assert path.exists()
    opened=[]
    monkeypatch.setattr('tpd_spectra.feedback_gui.webbrowser.open',lambda url:opened.append(url) or True)
    dialog.email()
    assert opened==[]  # Explicit review is required before opening external drafts.
    dialog.reviewed.set(True)
    dialog.email()
    assert opened and opened[-1].startswith('mailto:')
    monkeypatch.setattr('tpd_spectra.feedback_gui.webbrowser.open',lambda _:(_ for _ in ()).throw(OSError('no mail app')))
    dialog.email()
    assert dialog.win.winfo_exists() and 'could not be completed' in dialog.status.get()
    assert dialog.report()==report
    monkeypatch.setattr('tpd_spectra.feedback_gui.diagnostics',lambda _:(_ for _ in ()).throw(TypeError('bad serialization')))
    dialog.refresh()
    assert 'Unavailable' in dialog.report()
    dialog.win.destroy()


def test_feedback_actions_stay_visible_at_minimum_size(root):
    app=WorkflowApp(root)
    dialog=FeedbackDialog(app)
    dialog.win.geometry('620x520')
    root.update()
    actions=[w for frame in dialog.footer.winfo_children() for w in frame.winfo_children()
             if w.winfo_class()=='TButton']
    assert len(actions)==4
    for button in actions:
        assert button.winfo_ismapped()
        bottom=button.winfo_rooty()+button.winfo_height()-dialog.win.winfo_rooty()
        assert 0<bottom<=dialog.win.winfo_height()
    canvas=dialog.content.master
    assert canvas.yview()[1]<1  # Form scrolls instead of hiding the footer.
    canvas.yview_moveto(1)
    root.update()
    assert dialog.preview.winfo_rooty()<canvas.winfo_rooty()+canvas.winfo_height()
    dialog.win.destroy()
