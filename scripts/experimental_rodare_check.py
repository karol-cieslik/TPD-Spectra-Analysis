"""Reproduce a limited published experimental peak and test input/ramp handling.

Data: Becker et al. (2026), RODARE 10.14278/rodare.4644, CC-BY-4.0.
Selected columns from sheet H2 D2, original calibrated D2 channel.
No desorption-energy, order, mechanism or calibration validation is claimed.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from tpd_spectra.analysis import load_spectrum
from tpd_spectra.ramp import checked_linear_ramp


def evaluate(directory=None):
    root=Path(__file__).resolve().parents[1]
    directory=Path(directory) if directory else root/'validation/experimental/rodare_4644'
    path=directory/'H2_D2_D2_source_units.csv'
    provenance=json.loads((directory/'provenance.json').read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest()!=provenance['csv_sha256']:
        raise ValueError('Experimental source CSV does not match recorded hash')
    spec=load_spectrum(path,time_unit='s',temperature_unit='K')
    raw=np.genfromtxt(path,delimiter=',',names=True)
    conversion_error=float(np.max(np.abs(spec.temperature_c+273.15-raw['Temperature'])))
    seconds=spec.time_min*60
    beta=float(np.polyfit(seconds,spec.temperature_clean_c,1)[0])
    peak_K=float(raw['Temperature'][np.argmax(spec.signal)])
    try:
        _,ramp=checked_linear_ramp(spec.time_min,spec.temperature_clean_c,beta)
        rejection=None
    except ValueError as exc:
        ramp=None;rejection=str(exc)
    return dict(dataset_doi=provenance['dataset_doi'],article_doi=provenance['article_doi'],
        sheet=provenance['sheet'],points=len(spec.signal),csv_sha256=provenance['csv_sha256'],
        source_units=spec.import_report['source_units'],temperature_conversion_max_error_K=conversion_error,
        time_conversion_max_error_s=float(np.max(np.abs(seconds-raw['Time']))),
        signal_max_relative_error=float(np.max(np.abs((spec.signal-raw['Signal'])/np.max(raw['Signal'])))),
        temperature_points_corrected=spec.points_temperature_corrected,
        peak_temperature_K=peak_K,published_peak_approx_K=92.,peak_difference_from_rounded_text_K=peak_K-92.,
        published_heating_rate_K_s=.1,whole_trace_regression_beta_K_s=beta,
        ramp_check=ramp,ramp_rejection=rejection,
        interpretation='Experimental import/conversion/rounded peak-position comparison and negative ramp screen only. No kinetic fit performed.')


if __name__=='__main__':
    result=evaluate()
    p=Path(__file__).resolve().parents[1]/'validation/experimental/rodare_4644/results.json'
    p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
