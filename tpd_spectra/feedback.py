"""Offline-first feedback. Diagnostics use an allowlist, never project dumps."""
from collections import deque
from datetime import datetime, timezone
import json
import math
import platform
import re
import threading
import traceback
from urllib.parse import urlencode
from zipfile import ZipFile, ZIP_DEFLATED
from .identity import build_identity, REPOSITORY, CONTACT_EMAIL

CATEGORIES = ('Bug report', 'Improvement suggestion', 'Unexpected scientific result', 'Question', 'General feedback')
SUBJECT = '[TPD Spectra Studio Beta] Bug Report / Feedback'
NUMERIC_SETTINGS = {'lower','upper','beta','prefactor','energy','order','max_nfev','coverage','amplitude','baseline','replicates','seed','window'}
BOOL_SETTINGS = {'free_order','fit_baseline','multistart','zero','first','second','fractional'}


def sanitize(text, private_terms=()):
    text = str(text)[:24000]
    for value in sorted({str(v) for v in private_terms if v and len(str(v))>=3}, key=len, reverse=True):
        text = re.sub(re.escape(value), '[private]', text, flags=re.I)
    text = re.sub(r'(?i)(?:https?|file)://[^\s<>]+', '[URL removed]', text)
    text = re.sub(r'(?i)\b[A-Z]:[\\/][^\r\n\"\x27<>|]*', '[path removed]', text)
    text = re.sub(r'\\\\[^\r\n\"\x27<>|]*', '[network path removed]', text)
    text = re.sub(r'(?<!\w)/(?:[^\s\"\x27<>]+/?)+', '[path removed]', text)
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email removed]', text)
    text = re.sub(r'(?i)\b(token|password|secret|api[_-]?key|authorization)\s*[:=]\s*[^\s,;]+', r'\1=[removed]', text)
    return text


def safe_settings(settings):
    safe = {}
    for key,value in settings.items():
        if key in BOOL_SETTINGS and isinstance(value,bool):
            safe[key] = value
        elif key in NUMERIC_SETTINGS:
            try:
                number=float(value)
                safe[key]=number if math.isfinite(number) else 'invalid/nonfinite'
            except (TypeError,ValueError,OverflowError):
                safe[key]='invalid numeric input'
        elif key=='smoothing' and value in ('none','mean','median'):
            safe[key]=value
    return safe


class DiagnosticLog:
    """Bounded memory-only events; no disk logs, source lines, or locals."""
    def __init__(self):
        self.events=deque(maxlen=30)
        self.lock=threading.Lock()

    def record(self,event,message='',exc=None):
        frames=[]
        if exc is not None and exc.__traceback__ is not None:
            frames=[{'function':frame.name,'line':frame.lineno} for frame in traceback.extract_tb(exc.__traceback__)[-8:]]
        entry={'utc':datetime.now(timezone.utc).isoformat(),'event':sanitize(event),
               'message':sanitize(message),'exception_type':type(exc).__name__ if exc else None,'frames':frames}
        with self.lock:
            self.events.append(entry)

    def snapshot(self,private_terms=()):
        with self.lock:
            events=json.loads(json.dumps(list(self.events)))
        def redact(value):
            if isinstance(value,str):
                return sanitize(value,private_terms)
            if isinstance(value,list):
                return [redact(v) for v in value]
            if isinstance(value,dict):
                return {k:redact(v) for k,v in value.items()}
            return value
        return redact(events)


def diagnostics(app):
    private=[]
    result={'identity':build_identity(),'system':{'os':platform.system(),'release':platform.release(),
        'machine':platform.machine(),'python':platform.python_version()},
        'scope':'No spectra, project files, source paths, filenames, peak labels, usernames, hostnames or environment variables are collected.',
        'settings':{},'selected_method':None}
    project=getattr(app,'project',None)
    if project:
        for dataset in project.datasets.values():
            from pathlib import Path
            private.extend([dataset.path,Path(dataset.path).name,Path(dataset.path).stem])
        private.extend(r.label for r in project.regions.values())
        result['imported_dataset_count']=len(project.datasets)
        method=app.method.get()
        if method in ('Leading edge','Redhead','Polanyi–Wigner'):
            result['selected_method']=method
            try:
                result['settings']=safe_settings(project.method_settings(method))
                dataset,region=project.context()
                result['selected_interval_c']=[region.lower,region.upper]
                result['processing']=safe_settings(dataset.processing)
                session=project.modeling.get(f'{dataset.id}/{region.id}')
                if session:
                    result['modeling_settings']=safe_settings(session.get('settings',{}))
            except (KeyError,ValueError):
                pass
    result['events']=getattr(app,'diagnostic_log',DiagnosticLog()).snapshot(private)
    return result


def compose_report(category,description,steps,contact,diagnostic_data):
    if category not in CATEGORIES:
        raise ValueError('Select a feedback category.')
    return (f'TPD Spectra Studio beta feedback\nCategory: {category}\n\nDescription:\n{description.strip()}\n\n'
            f'Reproduction steps (optional):\n{steps.strip()}\n\nReply email (optional): {contact.strip()}\n\n'
            'DIAGNOSTICS (review before sharing)\n'+json.dumps(diagnostic_data,indent=2,ensure_ascii=False,allow_nan=False)
            +'\n\nNo files are attached automatically. If useful, attach the reviewed diagnostic ZIP manually. '
            'Only share experimental data separately if you have permission.\n')


def save_zip(path,reviewed_report):
    # Exclusive creation prevents accidental overwrite; archive members are fixed.
    with ZipFile(path,'x',compression=ZIP_DEFLATED) as archive:
        archive.writestr('feedback-report.txt',reviewed_report)
        archive.writestr('README.txt','This ZIP contains only the reviewed feedback text. No spectra, projects, screenshots or local files were attached. Review before emailing it to '+CONTACT_EMAIL+'.\n')


def email_url(report):
    return 'mailto:'+CONTACT_EMAIL+'?'+urlencode({'subject':SUBJECT,'body':report})


def github_url(report):
    return REPOSITORY+'/issues/new?'+urlencode({'title':SUBJECT,'body':report})
