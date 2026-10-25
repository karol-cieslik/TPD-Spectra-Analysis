"""Independent quadrature benchmarks and adversarial zero-order fit inputs."""
import numpy as np
import pytest
from scipy.integrate import cumulative_trapezoid
from tpd_spectra.analysis import K_B_EV
from tpd_spectra.kinetics import fit_polanyi_wigner, simulate_tpd


def independent_trace(energy=1.2,nu=1e13,beta=1.,coverage=1.,step=1.):
    dense=np.linspace(20,650,126001)  # independent 0.005 K cumulative quadrature
    k=nu*np.exp(-energy/(K_B_EV*(dense+273.15)))
    theta=coverage-cumulative_trapezoid(k/beta,dense,initial=0)
    rate=np.where(theta>0,k,0.)
    stride=round(step/.005)
    return dense[::stride],10000*rate[::stride]


def fit(t,y,beta=1.,**kwargs):
    return fit_polanyi_wigner(t,y,beta,reaction_order=0,fit_baseline=kwargs.pop('fit_baseline',False),**kwargs)


@pytest.mark.parametrize('energy,nu,beta,coverage,step',[
    (1.2,1e13,1.,1.,.5),(.9,1e10,.5,1.,1.),(1.5,1e15,2.,1.,1.),
    (1.2,1e13,5.,1.,2.),(1.2,1e13,1.,.25,1.),(1.2,1e13,1.,.5,1.)])
def test_independent_recovery_and_physical_prediction(energy,nu,beta,coverage,step):
    t,y=independent_trace(energy,nu,beta,coverage,step)
    result,prediction=fit(t,y,beta)
    assert result.success
    assert result.activation_energy_eV==pytest.approx(energy,rel=.002)
    assert result.normalized_rmse<.002
    profile=result.identifiability_diagnostics['zero_order_profile']
    lo,hi=profile['conditional_prefactor_range_s_inv']
    assert lo <= nu/coverage <= hi  # inverse model normalizes coverage to one
    _,rate=simulate_tpd(t,beta,result.activation_energy_eV,result.prefactor_s_inv,0)
    np.testing.assert_allclose(prediction,result.signal_scale*rate+result.baseline,rtol=1e-7,atol=np.ptp(y)*1e-8)
    assert 'not confidence' in profile['condition'].lower()


def test_noise_baseline_and_different_starts():
    t,y=independent_trace(step=2.)
    rng=np.random.default_rng(20261025)
    offset=.05*np.ptp(y)
    noisy=y+offset+rng.normal(0,.01*np.ptp(y),y.size)
    a,p=fit(t,noisy,fit_baseline=True,initial_energy_ev=.8,initial_prefactor_s_inv=1e10)
    b,q=fit(t,noisy,fit_baseline=True,initial_energy_ev=1.5,initial_prefactor_s_inv=1e15)
    assert a.success and b.success
    assert a.activation_energy_eV==pytest.approx(1.2,rel=.05)
    assert a.normalized_rmse<.02
    assert a.baseline==pytest.approx(offset,abs=.01*np.ptp(y))
    np.testing.assert_array_equal(p,q)
    assert a.prefactor_s_inv==b.prefactor_s_inv


def test_repeated_temperatures_expand_predictions_and_scale_invariance():
    t,y=independent_trace(step=2.)
    a,p=fit(t,y)
    b,q=fit(np.repeat(t,2),np.repeat(y*1e-4,2))
    assert b.activation_energy_eV==pytest.approx(a.activation_energy_eV,abs=1e-6)
    np.testing.assert_allclose(q,np.repeat(p*1e-4,2),rtol=1e-6,atol=1e-9)


def test_truncated_trace_and_unphysical_temperature_are_rejected():
    t,y=independent_trace(step=1.)
    occupied=y>0
    with pytest.raises(ValueError,match='depletion edge'):
        fit(t[occupied],y[occupied])
    with pytest.raises(ValueError,match='kelvin'):
        fit(t-1000,y)
    with pytest.raises(ValueError,match='bounds'):
        fit(t,y,beta=1e200)


def test_limits_and_cancellation_do_not_return_partial_success():
    t,y=independent_trace(step=2.)
    with pytest.raises(RuntimeError,match='evaluation limit'):
        fit(t,y,max_nfev=1)
    calls=0
    def cancel():
        nonlocal calls
        calls+=1
        return calls>=15
    with pytest.raises(InterruptedError,match='cancelled'):
        fit(t,y,cancelled=cancel)


def test_zero_order_comparison_runs_one_profile_search():
    from tpd_spectra.kinetics_explorer import compare_desorption_orders
    t,y=independent_trace(step=2.)
    model=compare_desorption_orders(t,y,1.,orders=('zero',),fit_baseline=False)[0]
    assert model.error is None
    assert model.starts_attempted==model.starts_converged==1
    assert any('representative' in warning for warning in model.warnings)


def test_zero_order_monte_carlo_preserves_brackets_and_withholds_prefactor_percentiles():
    from tpd_spectra.kinetics_uncertainty import run_kinetics_monte_carlo
    t,y=independent_trace(step=5.)
    y=y+np.random.default_rng(91).normal(0,.01*np.ptp(y),len(y))
    options=dict(orders=('zero',),replicates=2,seed=42,fit_baseline=False,
                 minimum_successful_refits=2,max_nfev=100)
    a=run_kinetics_monte_carlo(t,y,1.,**options)
    b=run_kinetics_monte_carlo(t,y,1.,**options)
    assert a.replicates_completed==a.successful_parameter_fits['zero']==2
    assert a.failed_rankings==0 and a.winning_counts=={'zero':2}
    assert a.replicate_records==b.replicate_records
    assert 'energy_eV' in a.parameter_intervals['zero']
    assert 'log10_prefactor' not in a.parameter_intervals['zero']
    assert 'withheld' in a.interval_note
    for row in a.replicate_records:
        assert row['log10_prefactor'] is None
        assert row['zero_order_profile']['conditional_prefactor_range_s_inv']


def test_profile_survives_project_report_and_legacy_results_are_stale(tmp_path):
    from pathlib import Path
    import json
    from copy import deepcopy
    from tpd_spectra.workflow_state import WorkflowProject
    from tpd_spectra.workflow_analysis import calculate
    from tpd_spectra.workflow_io import save_project,load_project
    from tpd_spectra.workflow_report import export_report
    project=WorkflowProject()
    source=Path(__file__).resolve().parents[1]/'examples/beta_collection/zero_order_single_peak.csv'
    dataset=project.add_dataset(source)
    project.add_region('Zero-order reference',50,450)
    project.method_settings('Polanyi–Wigner').update(order=0.,fit_baseline=False)
    result=calculate(dataset,project.snapshot('Polanyi–Wigner'))
    assert project.result_is_current(result)
    legacy=deepcopy(result)
    legacy['snapshot'].pop('kinetic_engine_revision')
    assert not project.result_is_current(legacy)
    saved=project.save_result(result,'Depletion-profile result')
    loaded=load_project(save_project(project,tmp_path/'project.tpd.json'))
    assert loaded.runs[saved['id']]['values']==saved['values']
    export_report(loaded,[saved['id']],tmp_path/'report')
    data=json.loads((tmp_path/'report/results.json').read_text(encoding='utf-8'))
    assert data['runs'][0]['values']['conditional_prefactor_range_s_inv']
    assert 'not uniquely' in data['runs'][0]['values']['prefactor_interpretation']
    assert (tmp_path/'report/COMPLETE.txt').exists()


def test_explorer_export_labels_representative_values(tmp_path):
    import csv
    from tpd_spectra.kinetics_explorer import compare_desorption_orders
    from tpd_spectra.explorer_export import export_explorer_bundle
    t,y=independent_trace(step=5.)
    models=compare_desorption_orders(t,y,1.,orders=('zero',),fit_baseline=False)
    export_explorer_bundle(tmp_path/'export',t,y,models,beta_k_s=1.)
    with (tmp_path/'export/model_comparison.csv').open(encoding='utf-8') as handle:
        row=next(csv.DictReader(handle))
    assert 'not unique' in row['prefactor_interpretation']
    assert row['conditional_prefactor_range_s_inv']
