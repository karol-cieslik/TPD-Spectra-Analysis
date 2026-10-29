"""Prepare review evidence without fitting or regenerating historical analyses.

Converts measured D2 coordinates for legacy GUI import and checks exports of
a retained zero-order mismatch result. No Windows/GUI acceptance is implied.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tpd_spectra.analysis import load_spectrum
from tpd_spectra.kinetics import KineticFitResult
from tpd_spectra.kinetics_explorer import ModelCandidate
from tpd_spectra.explorer_export import export_explorer_bundle
from tpd_spectra.result_view import scientific_notes, parameter_rows

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New output directory; existing evidence is never overwritten')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    src=ROOT/'validation/experimental/rodare_4644/H2_D2_D2_source_units.csv'
    a=np.genfromtxt(src,delimiter=',',names=True)
    fixture=out/'D2_measured_GUI_ms_degC.csv'
    with fixture.open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['ms','Temperatura','DHTA+'])
        w.writerows(zip(a['Time']*1000,a['Temperature']-273.15,a['Signal']))
    loaded=load_spectrum(fixture)
    assert len(loaded.signal)==len(a)==289
    assert np.allclose(loaded.time_min,a['Time']/60,rtol=0,atol=1e-12)
    assert np.allclose(loaded.temperature_c,a['Temperature']-273.15,rtol=0,atol=1e-12)
    # CSV parsers may differ by a few float64 ulps for large molecule counts.
    signal_relative_error=float(np.max(abs(loaded.signal-a['Signal']))/np.max(abs(a['Signal'])))
    assert np.allclose(loaded.signal,a['Signal'],rtol=1e-14,atol=0)
    corrected_delta=float(np.max(abs(loaded.temperature_clean_c-loaded.temperature_c)))
    peak=float(loaded.temperature_clean_c[np.argmax(loaded.signal)])
    assert abs(peak-(-181.09))<1e-9
    fixture_info=dict(source=str(src.relative_to(ROOT)),source_sha256=digest(src),derived_sha256=digest(fixture),
                      dataset_doi='10.14278/rodare.4644',licence='CC-BY-4.0',
                      attribution='Alexandra Becker, Holger Lippold, Jing Liu, Michael Hirscher and Cornelius Fischer',
                      conversions=['Measured relative time seconds multiplied by 1000 to ms','Measured temperature K minus 273.15 to degC','Signal preserved, molecules/s'],
                      measured_time=True,new_time_channel_fabricated=False,rows=289,peak_K=peak+273.15,
                      peak_degC=peak,maximum_import_temperature_cleaning_change_degC=corrected_delta,
                      signal_import_max_difference_relative_to_peak=signal_relative_error,
                      scope='GUI import/export usability fixture. Not an energy validation. Full source ramp failed earlier screen; do not force a kinetic full-trace fit.')
    (out/'D2_fixture_provenance.json').write_text(json.dumps(fixture_info,indent=2)+'\n')
    case=ROOT/'validation/experimental/methyl_acetate_2024'
    saved=json.loads((case/'results.json').read_text())
    record=next(r for r in saved['records'] if r['case']=='whole_peak_baseline0')
    rows=list(csv.DictReader((case/'predictions.csv').open()))
    selected=[r for r in rows if r['case']=='whole_peak_baseline0']
    T=np.array([float(r['temperature_K']) for r in selected])-273.15
    y=np.array([float(r['observed_or_transformed']) for r in selected])
    prediction=np.array([float(r['prediction']) for r in selected])
    fit=KineticFitResult(**record['result'])
    warnings=tuple(fit.identifiability_diagnostics['warnings'])
    assert any('Large residual' in w for w in warnings)
    candidate=ModelCandidate(name='zero',fit=fit,prediction=prediction,error=None,warnings=warnings)
    settings=dict(review_purpose='Re-export retained mismatch; no optimizer called',assumed_order=0,
                  fit_baseline=False,source_case='whole_peak_baseline0',source_result_sha256=digest(case/'results.json'),
                  scientific_code_review_base='70ef9e2254c1f1aef765dcd2d2f222ecdd76b1e4',
                  source_signal_units='Normalized graphical height, not calibrated physical rate')
    export=export_explorer_bundle(out/'retained_mismatch_export',T,y,[candidate],beta_k_s=.5,
                                   source=str((case/'results.json').relative_to(ROOT)),settings=settings)
    exported=list(csv.DictReader((export/'model_comparison.csv').open()))[0]
    assert all(w in exported['warnings'] for w in warnings)
    assert 'not unique' in exported['prefactor_interpretation']
    curves=list(csv.DictReader((export/'fitted_curves.csv').open()))
    assert np.allclose([float(r['zero_fit']) for r in curves],prediction,rtol=0,atol=1e-14)
    assert np.allclose([float(r['zero_residual']) for r in curves],y-prediction,rtol=0,atol=1e-14)
    metadata=json.loads((export/'explorer_analysis.json').read_text())
    assert metadata['settings']==settings and metadata['heating_rate_k_s']==.5
    view=dict(snapshot=dict(method='Polanyi–Wigner',dataset='Retained methyl-acetate figure-derived trace',
                            peak='Whole-peak model-limit case',region=[float(T.min()),float(T.max())],
                            settings=dict(beta=.5,order=0,fit_baseline=False),processing=dict(baseline=0,smoothing='none')),
              status='fitted',values=record['result'],warnings=list(warnings))
    notes=scientific_notes(view,True)
    assert all(w in notes for w in warnings)
    assert any(row[3]=='Representative; not unique' for row in parameter_rows(view))
    (out/'presentation_helper_notes.txt').write_text('Presentation helper called on retained-result state. Not a GUI screenshot or fresh fit.\n\n'+notes+'\n')
    result=dict(platform=platform.system(),display_available=bool(os.environ.get('DISPLAY')),
                fixture_import='passed; measured coordinates preserved under explicit conversion',
                exporter='Explorer export from retained model result; no fitting',warnings_preserved=True,
                prefactor_caution_preserved=True,curves_and_residuals_preserved=True,settings_preserved=True,
                presentation_helper_warnings_and_roles='passed without rendering a GUI',
                production_fit_calls=0,Windows_GUI_acceptance='NOT RUN',native_workflow_PDF_export='NOT RUN',
                required_manual_check='WINDOWS_ACCEPTANCE.md',
                source_code_sha256={name:digest(ROOT/name) for name in ['tpd_spectra/explorer_export.py','tpd_spectra/result_view.py','tpd_spectra/analysis.py']})
    (out/'headless_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    files={str(p.relative_to(out)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'file_manifest.json').write_text(json.dumps(files,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
