"""Real dialog clicks, confirmed source rate, full-spectrum fit and failure paths."""
from types import SimpleNamespace
import numpy as np
import pytest
from tpd_spectra.workflow_gui import WorkflowApp
from tpd_spectra.beta_onboarding import ExampleDialog
from tpd_spectra.heating_rate import confirm_source_rate
from test_component_workflow import wait, EXAMPLES


def test_source_rate_is_never_applied_without_confirmation(root,monkeypatch,tmp_path):
    app=WorkflowApp(root)
    dialog=ExampleDialog(app,section='publication')
    dialog.open()
    panel=app.modeling_panel
    assert float(panel.variables['beta'].get())==1
    assert app.project.method_settings('Redhead')['beta']==1
    panel.components.open(count=2)
    controller=panel.components
    old=controller.rows[0][0][2].get()
    prompts=[]
    def reject(*args,**kwargs):
        prompts.append(args)
        return False
    monkeypatch.setattr('tpd_spectra.heating_rate.messagebox.askyesno',reject)
    assert not confirm_source_rate(panel)
    assert float(panel.variables['beta'].get())==1
    assert 'source_heating_rate_confirmation' not in panel.session()
    monkeypatch.setattr('tpd_spectra.heating_rate.messagebox.askyesno',lambda *a,**k:True)
    controller.confirm_rate()
    assert float(panel.variables['beta'].get())==3
    assert controller.apply()  # Basic mode refreshes guesses after a rate change.
    assert controller.rows[0][0][2].get()!=old
    assert panel.session()['source_heating_rate_confirmation']['beta_K_s']==3
    snap=controller.snapshot()
    assert snap['settings']['beta']=='3'
    assert 'Zaki' in snap['source_heating_rate_confirmation']['citation']
    from tpd_spectra.workflow_io import save_project,load_project
    restored=load_project(save_project(app.project,tmp_path/'rate.tpd.json'))
    assert restored.modeling[panel.key()]['source_heating_rate_confirmation']==snap['source_heating_rate_confirmation']
    assert app.project.method_settings('Redhead')['beta']==1
    assert prompts and '3 K/s' in prompts[0][1]


def test_click_two_positions_fits_both_and_preserves_single_state_path(root):
    app=WorkflowApp(root)
    app._load_paths([EXAMPLES.parent/'synthetic_two_peak_demo_clean.csv'])
    if app.project.active_region is None:
        t=app.project.datasets[app.project.active_dataset].spectrum.temperature_clean_c
        app.project.add_region('Navigation',float(t[0]),float(t[-1]))
    app.refresh_context()
    app.stages.select(1)
    panel=app.modeling_panel
    controller=panel.components
    controller.open(count=2)
    root.update()
    assert len(controller.rows)==2
    assert not controller.advanced.get()
    assert not controller.rows_frame.winfo_ismapped()
    assert controller.fit_button.cget('text')=='Fit Both Peaks'
    # Real Matplotlib event dispatch exercises the connected callback.
    from matplotlib.backend_bases import MouseEvent
    for position in (170.,270.):
        ylim=controller.position_axis.get_ylim()
        x,y=controller.position_axis.transData.transform((position,(ylim[0]+ylim[1])/2))
        event=MouseEvent('button_press_event',controller.position_canvas,x,y,button=1)
        controller.position_canvas.callbacks.process('button_press_event',event)
    assert [float(v.get()) for v in controller.position_vars]==pytest.approx([170,270],abs=.01)
    assert controller.apply()
    assert controller.run()
    wait(app,root)
    fit=panel.session()['components']['fit']
    assert len(fit['components'])==2
    assert fit['normalized_rmse']<.01
    curves=panel.fig.axes[0].lines
    components=[line for line in curves if '(n=' in line.get_label()]
    assert len(components)==2
    assert components[0].get_color()!=components[1].get_color()
    assert components[0].get_linestyle()!=components[1].get_linestyle()
    assert 'review' in panel.fig.axes[0].get_title().lower()
    assert panel.fig.axes[1].get_legend() is not None
    panel.show_single()
    assert panel.session()['display_mode']=='single'
    controller.window.destroy()
    controller.open(count=2)  # Reopening must retain rows and not use dead Tk widgets.
    assert len(controller.rows)==2


def test_invalid_and_coincident_positions_do_not_mutate_definitions(root):
    app=WorkflowApp(root)
    app._load_paths([EXAMPLES/'three_overlapping_peaks.csv'])
    t=app.project.datasets[app.project.active_dataset].spectrum.temperature_clean_c
    app.project.add_region('Navigation',float(t[0]),float(t[-1]))
    app.refresh_context()
    c=app.modeling_panel.components
    c.open(count=2)
    original=[[v.get() for v in row] for row,_ in c.rows]
    c.position_vars[0].set('nan')
    assert not c.apply()
    assert 'finite' in c.message.get()
    assert [[v.get() for v in row] for row,_ in c.rows]==original
    c.position_vars[0].set(c.position_vars[1].get())
    assert not c.apply()
    assert 'distinct' in c.message.get()
    c.position_vars[0].set('100')
    c.rows[0][0][1].set('2')
    assert not c.estimate_positions()
    assert 'first order' in c.message.get()
