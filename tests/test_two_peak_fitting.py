"""Low-temperature recovery and failed-fit screening; no Gaussian fit oracle."""
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from scipy.integrate import cumulative_trapezoid

from tpd_spectra.analysis import K_B_EV
from tpd_spectra.multicomponent import (
    ComponentDefinition, fit_components, suggest_peak_positions, suggest_component,
)
from tpd_spectra.heating_rate import source_heating_rate
from tpd_spectra.workflow_state import WorkflowProject

ROOT=Path(__file__).resolve().parents[1]
ZAKI=ROOT/'examples/publication_data/zaki_2018_d2o_fe3o4.csv'


def low_temperature_reference():
    dense=np.linspace(-135,170,100001)
    curves=[]
    for energy,scale in ((.66,30),(.83,22)):
        k=1e13*np.exp(-energy/(K_B_EV*(dense+273.15)))
        theta=np.exp(-cumulative_trapezoid(k/3,dense,initial=0))
        curves.append((scale*k*theta)[::250])
    return dense[::250],np.sum(curves,axis=0),curves


@pytest.mark.parametrize('detector_unit_factor',[1.,1e-12])
def test_two_peaks_recover_from_positions_without_manual_energy_guesses(detector_unit_factor):
    t,y,curves=low_temperature_reference()
    y=y*detector_unit_factor
    curves=[c*detector_unit_factor for c in curves]
    positions=suggest_peak_positions(t,y)
    definitions=[suggest_component(p,3,label=f'Peak {i+1}') for i,p in enumerate(positions)]
    result=fit_components(t,y,3,definitions,fit_baseline=False)
    assert result.normalized_rmse<.001
    indices=np.argsort([c['energy_eV'] for c in result.components])
    np.testing.assert_allclose([result.components[i]['energy_eV'] for i in indices],[.66,.83],atol=.002,rtol=0)
    np.testing.assert_allclose([result.components[i]['signal_scale']/detector_unit_factor for i in indices],[30,22],rtol=.02)
    for fit,truth in zip([result.component_predictions[i] for i in indices],curves):
        assert np.sqrt(np.mean((fit-truth)**2))/np.ptp(y)<.001
    assert not result.diagnostics['baseline_only']
    assert not result.diagnostics['collapsed_components']


@pytest.fixture(scope='module')
def zaki_results():
    data=pd.read_csv(ZAKI)
    t,y=data.Temperatura.to_numpy(),data['DHTA+'].to_numpy()
    wrong=[ComponentDefinition('Peak 1',energy_eV=1.25),ComponentDefinition('Peak 2',energy_eV=1.55)]
    old=fit_components(t,y,3,wrong,multistart=False)
    rescued=fit_components(t,y,3,wrong,multistart=True)
    return t,y,old,rescued


def test_zaki_reproduces_baseline_collapse_and_reports_it(zaki_results):
    t,y,old,_=zaki_results
    assert -21<t[y.argmax()]<-15
    assert old.baseline==pytest.approx(.21165,abs=.002)
    assert old.normalized_rmse>.25
    assert old.diagnostics['baseline_only']
    assert old.diagnostics['fit_quality']=='baseline_only'
    assert set(old.diagnostics['collapsed_components'])=={'Peak 1','Peak 2'}
    assert any('BASELINE-ONLY / UNUSABLE' in w for w in old.warnings)
    assert not old.diagnostics['uncertainty_available']
    assert old.diagnostics['initial_peak_at_boundary_components']
    from matplotlib.figure import Figure
    from tpd_spectra.component_export import draw_components
    from tpd_spectra.workflow_analysis import serial
    figure=Figure()
    axis,residual=figure.add_subplot(211),figure.add_subplot(212)
    draw_components(axis,residual,serial(old))
    assert 'UNUSABLE' in axis.get_title()
    assert len([line for line in axis.lines if '(n=' in line.get_label()])==2


def test_multistart_rescues_zaki_numerics_without_claiming_physical_validation(zaki_results):
    _,_,old,result=zaki_results
    assert result.starts_attempted>3 and result.starts_converged>0
    assert result.normalized_rmse<.14 and result.normalized_rmse<.6*old.normalized_rmse
    assert not result.diagnostics['baseline_only']
    assert not result.diagnostics['collapsed_components']
    assert any('serially correlated' in w for w in result.warnings)
    assert not result.diagnostics['uncertainty_available']
    assert result.diagnostics['fit_quality']=='review_required'


def test_constraints_are_respected_even_when_they_preclude_the_peaks():
    t,y,_=low_temperature_reference()
    constrained=[ComponentDefinition(f'Bad {i}',energy_eV=1.5,energy_bounds=(1.4,1.6)) for i in (1,2)]
    result=fit_components(t,y,3,constrained)
    assert result.diagnostics['baseline_only']
    assert not result.diagnostics['uncertainty_available']
    assert all(1.4<=c['energy_eV']<=1.6 for c in result.components)
    assert all(1.4<=e<=1.6 for row in result.diagnostics['energy_starts_eV'] for e in row)


def test_linear_baseline_does_not_support_two_states():
    t=np.linspace(-130,170,101)
    result=fit_components(t,2+.01*t,3,[suggest_component(-20,3),suggest_component(40,3,label='Peak 2')],
                          fit_drift=True,multistart=False)
    assert result.diagnostics['baseline_only']
    assert not result.diagnostics['uncertainty_available']


def test_poor_fit_is_distinct_from_a_baseline_only_fit():
    t,_,curves=low_temperature_reference()
    y=curves[0]+2*curves[1]
    # Resolve only the lower-temperature population; the second true peak remains.
    one=ComponentDefinition('Only low peak',energy_eV=.66,energy_bounds=(.64,.68))
    result=fit_components(t,y,3,[one],multistart=False)
    assert not result.diagnostics['baseline_only']
    assert result.normalized_rmse>.15
    assert result.diagnostics['fit_quality']=='poor_fit'
    assert not result.diagnostics['uncertainty_available']


def test_a_good_sum_with_one_collapsed_component_does_not_support_two_states():
    t,_,curves=low_temperature_reference()
    result=fit_components(t,curves[0],3,[
        ComponentDefinition('Supported',energy_eV=.66,energy_bounds=(.64,.68)),
        ComponentDefinition('Unsupported',energy_eV=1.5,energy_bounds=(1.4,1.6))],
        fit_baseline=False,multistart=False)
    assert result.normalized_rmse<.001
    assert not result.diagnostics['baseline_only']
    assert result.diagnostics['collapsed_components']==['Unsupported']
    assert result.diagnostics['fit_quality']=='collapsed_components'
    assert not result.diagnostics['uncertainty_available']


@pytest.mark.parametrize('temperature,beta,nu',[(-273.15,3,1e13),(-20,0,1e13),(-20,3,0),
    (np.nan,3,1e13),(-20,3,np.inf),(-20,3,1e-15)])
def test_nonphysical_position_guesses_are_rejected(temperature,beta,nu):
    with pytest.raises(ValueError):
        suggest_component(temperature,beta,prefactor_s_inv=nu)


def test_hints_use_celsius_and_supplied_heating_rate():
    c=suggest_component(-20,3)
    assert .66<c.energy_eV<.69
    assert c.energy_bounds==pytest.approx((.7*c.energy_eV,1.3*c.energy_eV))
    assert c.energy_eV<suggest_component(-20,1).energy_eV
    assert suggest_component(155,1).energy_eV==pytest.approx(1.2,rel=.025)
    t,y,_=low_temperature_reference()
    assert suggest_peak_positions(t,y)==suggest_peak_positions(t,y)
    with pytest.raises(ValueError):
        suggest_peak_positions(t,np.ones_like(y))
    with pytest.raises(ValueError):
        suggest_peak_positions(t[::-1],y)


def test_source_suggestions_require_metadata_or_exact_known_csv_bytes(tmp_path):
    project=WorkflowProject()
    dataset=project.add_dataset(ZAKI)
    assert source_heating_rate(dataset)['beta_K_s']==3
    # A user file with this familiar basename must never inherit a source rate.
    path=tmp_path/ZAKI.name
    path.write_text('Time,Signal,Temperature\n0,1,0\n1000,2,1\n2000,1,2\n')
    assert source_heating_rate(project.add_dataset(path)) is None
    for value in (None,0,-1,np.nan,True,'3'):
        fake=SimpleNamespace(spectrum=SimpleNamespace(import_report={'publication_example':{'beta_K_s':value}}))
        assert source_heating_rate(fake) is None
