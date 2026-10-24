"""Versioned portable projects and explicit source provenance checks."""
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4
import hashlib
import json
import os
import numpy as np
from .analysis import Spectrum
from .workflow_analysis import serial
from .workflow_state import WorkflowProject, Dataset, Region
from .run_session import sha256

SCHEMA_VERSION = 1


def payload_digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def project_payload(project):
    datasets = []
    for dataset in project.datasets.values():
        data = serial(asdict(dataset))
        data['embedded_sha256'] = payload_digest(data['spectrum'])
        datasets.append(data)
    return serial(dict(schema_version=SCHEMA_VERSION, datasets=datasets,
        regions=[asdict(r) for r in project.regions.values()], settings=project.settings,
        runs=project.runs, current_results=project.current_results, modeling=project.modeling,
        processing_history=project.processing_history, active_dataset=project.active_dataset,
        active_region=project.active_region, report_selection=getattr(project,'report_selection',[])))


def save_project(project, path):
    path = Path(path)
    payload = project_payload(project)
    temporary = path.with_name(path.name + '.' + uuid4().hex + '.tmp')
    try:
        with temporary.open('x',encoding='utf-8') as handle:
            json.dump(payload,handle,ensure_ascii=False,indent=2,allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def load_project(path):
    with Path(path).open(encoding='utf-8') as handle:
        payload = json.load(handle)
    if payload.get('schema_version') != SCHEMA_VERSION:
        raise ValueError('Unsupported project schema version; existing workspace has not been changed.')
    project = WorkflowProject()
    project.source_warnings = []
    try:
        for item in payload['datasets']:
            data = dict(item)
            expected = data.pop('embedded_sha256')
            if payload_digest(data['spectrum']) != expected:
                raise ValueError('Embedded spectrum checksum mismatch')
            spec = data['spectrum']
            for key in ('time_min','temperature_c','temperature_clean_c','signal'):
                spec[key] = np.asarray(spec[key],dtype=float)
                spec[key].setflags(write=False)
            shape = spec['signal'].shape
            if len(shape) != 1 or shape[0] < 3 or any(spec[k].shape != shape or not np.isfinite(spec[k]).all() for k in ('time_min','temperature_c','temperature_clean_c','signal')):
                raise ValueError('Invalid embedded spectrum arrays')
            data['spectrum'] = Spectrum(**spec)
            dataset = Dataset(**data)
            if dataset.id in project.datasets:
                raise ValueError('Duplicate dataset ID')
            project.datasets[dataset.id] = dataset
            project.active_dataset = dataset.id
            project.set_processing(dataset.processing)
            source = Path(dataset.path)
            if not source.is_file():
                project.source_warnings.append(f'{dataset.path}: source unavailable; using checksummed embedded data.')
            elif sha256(source) != dataset.digest:
                project.source_warnings.append(f'{dataset.path}: source changed; using original checksummed embedded data, not the changed file.')
        for data in payload['regions']:
            region = Region(**data)
            project.validate_bounds(region.dataset_id,region.lower,region.upper)
            if region.id in project.regions:
                raise ValueError('Duplicate region ID')
            project.regions[region.id] = region
        for field in ('settings','runs','current_results','modeling','processing_history'):
            setattr(project,field,payload[field])
        for result in [*project.runs.values(),*project.current_results.values()]:
            snap = result['snapshot']
            region = project.regions[snap['region_id']]
            if region.dataset_id != snap['dataset_id'] or project.datasets[region.dataset_id].digest != snap['source_sha256']:
                raise ValueError('Result provenance does not match its dataset')
        project.active_dataset = payload['active_dataset']
        project.active_region = payload['active_region']
        if project.active_dataset is not None:
            project.select_dataset(project.active_dataset)
        if project.active_region is not None:
            project.context()
        project.report_selection = [i for i in payload.get('report_selection',[]) if i in project.runs]
    except (KeyError,TypeError,IndexError) as exc:
        raise ValueError('Invalid or incomplete project structure') from exc
    return project
