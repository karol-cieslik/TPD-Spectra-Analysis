import hashlib
import json
from copy import deepcopy
from pathlib import Path
import numpy as np
import pytest
from tpd_spectra.analysis import load_spectrum,redhead_energy,leading_edge_fit
from tpd_spectra.kinetics import fit_polanyi_wigner

FOLDER=Path(__file__).resolve().parents[1]/'examples/beta_collection'
CATALOG=json.loads((FOLDER/'catalog.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('entry',CATALOG,ids=lambda e:e['file'])
def test_each_beta_example_imports_directly_and_has_ground_truth(entry):
    path=FOLDER/entry['file']
    metadata=json.loads((FOLDER/entry['metadata']).read_text(encoding='utf-8'))
    spectrum=load_spectrum(path)
    assert len(spectrum.signal)==metadata['points']==801
    assert np.isfinite(spectrum.signal).all()
    assert np.all(np.diff(spectrum.temperature_clean_c)>0)
    assert metadata['synthetic'] is True and metadata['experimental'] is False
    assert hashlib.sha256(path.read_bytes()).hexdigest()==metadata['csv_sha256']
    assert metadata['number_of_states']==len(metadata['states'])
    for state in metadata['states']:
        assert state['energy_eV']>0 and state['prefactor_s_inv']>0 and 0<state['initial_normalized_coverage']<=1
    assert metadata['noise'] and metadata['baseline'] and isinstance(metadata['random_seed'],int)
    assert metadata['expected_behavior'] and metadata['limitations']
    beta=np.polyfit(spectrum.time_min*60,spectrum.temperature_clean_c,1)[0]
    assert beta==pytest.approx(metadata['beta_K_s'],rel=1e-7)


@pytest.mark.parametrize('name',[
    'zero_order_single_peak',
    'first_order_single_peak','second_order_single_peak','fractional_order_1p5'])
def test_documented_recovery_tolerances(name):
    metadata=json.loads((FOLDER/(name+'.json')).read_text(encoding='utf-8'))
    s=load_spectrum(FOLDER/(name+'.csv'))
    truth=metadata['states'][0]
    check=metadata['recovery_check']
    fit,prediction=fit_polanyi_wigner(s.temperature_clean_c,s.signal,metadata['beta_K_s'],reaction_order=truth['order'],
        initial_energy_ev=check['initial_energy_eV'],initial_prefactor_s_inv=check['initial_prefactor_s_inv'],
        fit_baseline=check['fit_baseline'],max_nfev=check['max_nfev'])
    assert fit.success
    assert abs(fit.activation_energy_eV/truth['energy_eV']-1)<check['energy_relative_tolerance']
    assert abs(np.log10(fit.prefactor_s_inv/truth['prefactor_s_inv']))<check['log10_prefactor_absolute_tolerance']
    assert prediction.shape==s.signal.shape
    assert fit.normalized_rmse<check['normalized_rmse_tolerance']


def test_first_result_and_physical_series_behavior():
    first=load_spectrum(FOLDER/'first_order_single_peak.csv')
    peak=first.temperature_clean_c[np.argmax(first.signal)]
    assert redhead_energy(peak,1e13,1)==pytest.approx(1.2,rel=.025)
    assert leading_edge_fit(first.temperature_clean_c,first.signal,1,90,110).energy_ev==pytest.approx(1.2,rel=.02)
    positions=[]
    for name in ('heating_rate_0p5_K_s','first_order_single_peak','heating_rate_2p0_K_s','heating_rate_5p0_K_s'):
        s=load_spectrum(FOLDER/(name+'.csv'))
        positions.append(s.temperature_clean_c[np.argmax(s.signal)])
    assert np.all(np.diff(positions)>0)
    low=load_spectrum(FOLDER/'first_order_coverage_0p25.csv')
    np.testing.assert_allclose(low.signal,first.signal*.25,rtol=1e-10,atol=1e-12)
    zero=load_spectrum(FOLDER/'zero_order_single_peak.csv')
    zero_low=load_spectrum(FOLDER/'zero_order_coverage_0p25.csv')
    assert zero_low.temperature_clean_c[np.argmax(zero_low.signal)]<zero.temperature_clean_c[np.argmax(zero.signal)]


def test_resource_lookup_is_independent_of_working_directory(tmp_path,monkeypatch):
    from tpd_spectra.beta_resources import resource
    monkeypatch.chdir(tmp_path)
    assert resource('examples/beta_collection/catalog.json').is_file()
    with pytest.raises(FileNotFoundError):
        resource('../outside-private.txt')


def test_example_chooser_opens_clean_reference_and_supplies_ramp(root):
    from tpd_spectra.workflow_gui import WorkflowApp
    app=WorkflowApp(root)
    dialog=app.open_example()
    dialog.open()
    dataset,region=app.project.context()
    assert Path(dataset.path).name=='first_order_single_peak.csv'
    assert app.project.method_settings('Redhead')['beta']==1
    app.preview_selected()
    assert app.displayed_result['values']['energy_ev']==pytest.approx(1.2,rel=.025)


def test_beta_generator_reproduces_csv_bytes_and_metadata(tmp_path):
    from scripts.generate_beta_examples import generate,simulate
    first,second=tmp_path/'first',tmp_path/'second'
    catalog=generate(first)
    assert generate(second)==catalog==CATALOG
    assert (first/'catalog.json').read_bytes()==(second/'catalog.json').read_bytes()
    for entry in catalog:
        # A repeated seeded run in one numerical environment must be exact.
        for name in (entry['file'],entry['metadata']):
            assert (first/name).read_bytes()==(second/name).read_bytes()

        generated=json.loads((first/entry['metadata']).read_text(encoding='utf-8'))
        shipped=json.loads((FOLDER/entry['metadata']).read_text(encoding='utf-8'))
        assert generated.keys()==shipped.keys()
        # Each artifact's hash identifies its actual bytes. Numerical libraries
        # on another platform can round the last printed signal digit differently.
        for folder,metadata in ((first,generated),(FOLDER,shipped)):
            assert hashlib.sha256((folder/entry['file']).read_bytes()).hexdigest()==metadata['csv_sha256']
            if 'clean_reference_sha256' in metadata:
                reference=folder/metadata['clean_reference_file']
                assert hashlib.sha256(reference.read_bytes()).hexdigest()==metadata['clean_reference_sha256']

        generated_truth,shipped_truth=deepcopy(generated),deepcopy(shipped)
        for key in ('csv_sha256','clean_reference_sha256'):
            generated_truth.pop(key,None)
            shipped_truth.pop(key,None)
        # Only these values are computed from the floating-point clean peak.
        # Models, seeds, physical inputs, grid, units and validation limits stay exact.
        for section,key in (('noise','sigma_signal_units'),('baseline','offset_signal_units'),
                            ('baseline','slope_signal_units_per_K')):
            assert generated_truth[section].pop(key)==pytest.approx(shipped_truth[section].pop(key),rel=1e-12,abs=0)
        assert generated_truth==shipped_truth

        produced=np.loadtxt(first/entry['file'],delimiter=',',skiprows=1)
        reference=np.loadtxt(FOLDER/entry['file'],delimiter=',',skiprows=1)
        assert (first/entry['file']).read_bytes().splitlines()[0]==(FOLDER/entry['file']).read_bytes().splitlines()[0]
        np.testing.assert_array_equal(produced[:,[0,2]],reference[:,[0,2]])
        clean=simulate(shipped,np.linspace(50.,450.,80001))[::100]
        # Both CSVs use %.12e. Bound cross-library roundoff at that export
        # precision, far below the separate physical recovery tolerances.
        np.testing.assert_allclose(produced[:,1],reference[:,1],rtol=0,atol=1e-12*clean.max())


@pytest.mark.parametrize('label,fraction',[('low',.01),('moderate',.02),('high',.05)])
def test_noise_variants_retain_clean_reference_and_record_relative_sigma(label,fraction):
    path=FOLDER/f'first_order_{label}_noise.csv'
    meta=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    clean=load_spectrum(FOLDER/meta['clean_reference_file'])
    observed=load_spectrum(path)
    assert meta['noise_fraction_of_clean_maximum']==fraction
    sigma=meta['noise']['sigma_signal_units']
    assert sigma==pytest.approx(fraction*clean.signal.max(),rel=1e-12)
    expected=clean.signal+np.random.default_rng(meta['random_seed']).normal(0,sigma,len(clean.signal))
    # Allow only the accumulated rounding of two %.12e CSV observations.
    np.testing.assert_allclose(observed.signal,expected,rtol=0,atol=1e-12*clean.signal.max())
