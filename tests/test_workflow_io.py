import json
import shutil
from pathlib import Path
import numpy as np
import pytest
from tpd_spectra.workflow_state import WorkflowProject
from tpd_spectra.workflow_analysis import calculate
from tpd_spectra.workflow_io import save_project, load_project
from tpd_spectra.workflow_report import export_report

DEMO=Path(__file__).resolve().parents[1]/'examples/synthetic_two_peak_demo.csv'


def prepared(tmp_path):
    source=tmp_path/'input.csv'
    shutil.copyfile(DEMO,source)
    project=WorkflowProject()
    dataset=project.add_dataset(source)
    project.add_region('Peak 1',100,210)
    result=calculate(dataset,project.snapshot('Redhead'))
    project.accept_result(result)
    first=project.save_result(result,'First saved estimate')
    project.add_region('Peak 2',230,350)
    other=calculate(dataset,project.snapshot('Redhead'))
    second=project.save_result(other,'Excluded estimate')
    return project,first,second


def test_portable_project_roundtrip_missing_and_changed_sources(tmp_path):
    project,first,second=prepared(tmp_path)
    path=save_project(project,tmp_path/'sample.tpd.json')
    loaded=load_project(path)
    assert loaded.runs==project.runs
    assert loaded.active_region==project.active_region
    assert loaded.source_warnings==[]
    dataset=next(iter(loaded.datasets.values()))
    assert not dataset.spectrum.signal.flags.writeable
    (tmp_path/'input.csv').write_text('changed',encoding='utf-8')
    changed=load_project(path)
    assert 'source changed' in changed.source_warnings[0]
    np.testing.assert_array_equal(next(iter(changed.datasets.values())).spectrum.signal,dataset.spectrum.signal)
    (tmp_path/'input.csv').unlink()
    assert 'source unavailable' in load_project(path).source_warnings[0]


def test_invalid_schema_or_embedded_hash_rejected(tmp_path):
    project,_,_=prepared(tmp_path)
    path=save_project(project,tmp_path/'sample.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    data['datasets'][0]['spectrum']['signal'][0]+=1
    path.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError,match='checksum'):
        load_project(path)
    data['schema_version']=999
    path.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError,match='schema'):
        load_project(path)


def test_report_exports_only_selected_runs_and_never_overwrites(tmp_path):
    project,first,second=prepared(tmp_path)
    directory=export_report(project,[first['id']],tmp_path/'report')
    data=json.loads((directory/'results.json').read_text(encoding='utf-8'))
    assert [r['id'] for r in data['runs']]==[first['id']]
    assert data['runs'][0]['snapshot']['source_sha256']
    assert (directory/'report.pdf').read_bytes().startswith(b'%PDF')
    assert (directory/'run-001.svg').stat().st_size>1000
    assert (directory/'run-001.png').stat().st_size>1000
    assert (directory/'run-001-curve.csv').exists()
    assert (directory/'COMPLETE.txt').exists()
    with pytest.raises(FileExistsError):
        export_report(project,[second['id']],directory)
    with pytest.raises(ValueError,match='Select'):
        export_report(project,[],tmp_path/'empty')
