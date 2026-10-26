"""Real GUI joint fitting, full-grid provenance, persistence and individual exports."""
from dataclasses import asdict
import csv
import json
from pathlib import Path
import time
import numpy as np
import pytest
from tpd_spectra.workflow_gui import WorkflowApp
from tpd_spectra.workflow_io import save_project,load_project
from tpd_spectra.component_export import export_components
from tpd_spectra.multicomponent import ComponentDefinition

EXAMPLES=Path(__file__).resolve().parents[1]/'examples/beta_collection'


def wait(app,root):
    deadline=time.monotonic()+90
    while app.job_busy and time.monotonic()<deadline:
        root.update()
        time.sleep(.005)
    assert not app.job_busy,'joint fitter timed out'


@pytest.fixture
def joint_app(root):
    app=WorkflowApp(root)
    app._load_paths([EXAMPLES/'three_overlapping_peaks.csv'])
    # Deliberately crop the named navigation region: joint fitting must use ALL observations.
    app.project.add_region('Navigation only',100,160)
    app.refresh_context()
    panel=app.modeling_panel
    panel.variables['multistart'].set(False)
    panel.session()['component_settings']=dict(fit_baseline=False,fit_drift=False,components=[
        asdict(ComponentDefinition(f'State {i+1}',energy_eV=e+.005,energy_bounds=(e-.04,e+.04)))
        for i,e in enumerate((1.18,1.26,1.34))])
    app.stages.select(1)
    root.update()
    return app,panel,panel.components


def test_joint_gui_fit_full_spectrum_sums_residuals_and_roundtrip(root,joint_app,tmp_path):
    app,panel,controller=joint_app
    assert controller.run()
    wait(app,root)
    record=panel.session()['components']
    fit=record['fit']
    assert record['snapshot']['region']==[50.,450.]
    assert record['snapshot']['selected_named_region']==[100.,160.]
    assert len(fit['observed'])==801
    assert fit['normalized_rmse']<1e-3
    np.testing.assert_allclose(fit['prediction'],np.sum(fit['component_predictions'],axis=0)+fit['baseline_prediction'])
    np.testing.assert_allclose(fit['residuals'],np.asarray(fit['observed'])-fit['prediction'])
    assert panel.session()['display_mode']=='components'
    assert len(panel.table.get_children())==3
    labels=[line.get_label() for line in panel.fig.axes[0].lines]
    assert 'Original measured spectrum' in labels and 'Combined kinetic fit' in labels
    assert 'fixed' in panel.notes.get('1.0','end')
    assert 'sum' in panel.fig.axes[1].lines[1].get_label() or 'combined' in panel.fig.axes[1].lines[1].get_label()
    panel.monte_carlo()
    assert not app.job_busy and 'Component Monte Carlo is not implemented' in app.status.get()
    panel.table.selection_set('component-0')
    panel.transfer()
    assert 'Simultaneous components' in app.status.get()
    path=save_project(app.project,tmp_path/'joint.tpd.json')
    loaded=load_project(path)
    key=panel.key()
    assert loaded.modeling[key]['components']==record
    app.install_project(loaded)
    assert panel.components.current(record)
    assert 'Combined kinetic fit' in [line.get_label() for line in panel.fig.axes[0].lines]
    export=export_components(record,tmp_path/'export')
    saved=json.loads((export/'components.json').read_text(encoding='utf-8'))
    assert saved['snapshot']['source_sha256']==app.project.context()[0].digest
    with (export/'component_curves.csv').open(encoding='utf-8',newline='') as handle:
        rows=list(csv.reader(handle))
    assert len(rows)==802 and len(rows[0])==8
    numbers=np.asarray(rows[1:],dtype=float)
    np.testing.assert_allclose(numbers[:,2],numbers[:,3]+numbers[:,5:].sum(axis=1))
    np.testing.assert_allclose(numbers[:,4],numbers[:,1]-numbers[:,2])
    assert (export/'components.png').stat().st_size>1000
    assert (export/'components.svg').stat().st_size>1000
    assert 'fixed' in (export/'README.txt').read_text()
    with pytest.raises(FileExistsError):
        export_components(record,export)
    # Editing settings marks the submitted result stale without erasing it or auto-previewing one component.
    panel.variables['beta'].set('2')
    assert panel.preview_after is None
    assert 'STALE' in panel.notes.get('1.0','end')
    assert panel.session()['components']==record


@pytest.mark.parametrize('scaling',[1.333,2.0])
def test_editor_multiple_components_validation_and_context_guard(root,joint_app,scaling):
    app,panel,controller=joint_app
    root.tk.call('tk','scaling',scaling)
    callback_errors=[]
    root.report_callback_exception=lambda *args:callback_errors.append(args)
    controller.open()
    controller.window.geometry('860x560')
    root.update()
    assert not callback_errors
    assert len(controller.rows)==3
    def children(widget):
        for child in widget.winfo_children():
            yield child
            yield from children(child)
    for widget in children(controller.window):
        if widget.winfo_class()=='TButton':
            assert widget.winfo_ismapped()
            assert widget.winfo_rootx()+widget.winfo_width()<=controller.window.winfo_rootx()+controller.window.winfo_width()
            assert widget.winfo_rooty()+widget.winfo_height()<=controller.window.winfo_rooty()+controller.window.winfo_height()
    assert controller.editor_horizontal.winfo_ismapped()
    assert controller.editor_vertical.winfo_ismapped()
    controller.editor_canvas.xview_moveto(1)
    controller.editor_canvas.yview_moveto(1)
    root.update()
    controller.remove_row()
    assert len(controller.rows)==2
    controller.add_row()
    assert len(controller.rows)==3
    controller.add_row()
    assert len(controller.rows)==3
    controller.rows[2][0][0].set('Renamed state')
    controller.rows[2][0][1].set('0')
    assert not controller.apply()
    assert 'positive' in controller.message.get()
    controller.rows[2][0][1].set('2')
    assert controller.apply()
    assert controller.settings()['components'][2]['order']==2
    assert controller.settings()['components'][2]['label']=='Renamed state'
    app.project.add_region('Other region',180,260)
    app.refresh_context()
    assert not controller.apply()
    assert 'changed' in controller.message.get()
    controller.window.destroy()


def test_joint_count_comparison_uses_same_data_and_keeps_single_state_path(root,joint_app):
    app,panel,controller=joint_app
    assert controller.run(compare=True)
    wait(app,root)
    record=panel.session()['components']
    candidates=record['count_comparison']
    assert {c['count'] for c in candidates}=={1,2,3}
    assert candidates[0]['count']==3
    assert all(len(c['fit']['observed'])==801 for c in candidates if c['fit'])
    assert len(panel.table.get_children())==6
    panel.table.selection_set('count-2')
    controller.select_count()
    assert len(panel.session()['components']['fit']['components'])==2
    panel.table.selection_set('count-3')
    controller.select_count()
    assert len(panel.session()['components']['fit']['components'])==3
    record=panel.session()['components']
    panel.show_single()
    assert panel.session()['display_mode']=='single'
    assert not panel.table.get_children()
    controller.show()
    assert panel.session()['display_mode']=='components'
    # Failure preserves the previous joint fit and displayed spectrum.
    panel.variables['max_nfev'].set('1')
    assert controller.run()
    wait(app,root)
    assert panel.session()['components'] is record
    assert 'did not converge' in app.status.get()


def test_joint_cancellation_and_context_switch_do_not_destroy_or_misassign_results(root,joint_app,monkeypatch):
    import threading
    app,panel,controller=joint_app
    assert controller.run()
    wait(app,root)
    first_key=panel.key()
    previous=panel.session()['components']
    release=threading.Event()
    def delayed(*args,**kwargs):
        assert release.wait(10)
        return previous['fit']
    monkeypatch.setattr('tpd_spectra.component_gui.fit_components',delayed)
    assert controller.run()
    panel.cancel_job()
    release.set()
    wait(app,root)
    assert panel.session()['components'] is previous
    assert 'cancelled' in app.status.get()
    release.clear()
    assert controller.run()
    app.project.add_region('Other context',180,260)
    app.refresh_context()
    second_key=panel.key()
    release.set()
    wait(app,root)
    assert first_key!=second_key
    assert 'components' not in panel.session()
    assert 'components' in app.project.modeling[first_key]
