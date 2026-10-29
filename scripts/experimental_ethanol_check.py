"""Frozen ethanol comparison using production simulation and free-nu fitting.

Input CSV and comparison plots retain the source CC-BY-NC-3.0 licence.
No synthetic samples, interpolation, Monte Carlo or protocol tuning.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import time
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tpd_spectra.kinetics import simulate_tpd, fit_polanyi_wigner, K_B_EV
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation/experimental/ethanol_2024'


def profile(rate, signal, baseline):
    peak = float(np.max(rate))
    if peak <= np.finfo(float).tiny:
        return np.full_like(signal, np.mean(signal) if baseline else 0.), 0., float(np.mean(signal) if baseline else 0.)
    shape = rate / peak
    centered = shape - shape.mean() if baseline else shape
    target = signal - signal.mean() if baseline else signal
    amplitude = max(0., float(centered @ target) / max(float(centered @ centered), np.finfo(float).tiny))
    offset = float(np.clip(np.mean(signal-amplitude*shape), signal.min()-2*np.ptp(signal), signal.max()+np.ptp(signal))) if baseline else 0.
    amplitude = max(0., float(shape @ (signal-offset)) / max(float(shape @ shape), np.finfo(float).tiny))
    return offset + amplitude*shape, amplitude/peak, offset


def fixed_fit(T, signal, cfg, baseline):
    nu = cfg['fixed_prefactor_s_inv']
    def evaluate(energy, details=False):
        _, rate = simulate_tpd(T-273.15, cfg['beta_K_s'], energy, nu, 1.)
        pred, scale, offset = profile(rate, signal, baseline)
        rss = float(np.sum((pred-signal)**2))
        return (pred, scale, offset, rss, rate) if details else rss/np.ptp(signal)**2
    grid = np.linspace(*cfg['fixed_energy_search_eV'], cfg['fixed_profile_grid_points'])
    scores = np.array([evaluate(e) for e in grid])
    j = int(scores.argmin())
    opt = minimize_scalar(evaluate, bounds=(grid[max(0,j-1)], grid[min(len(grid)-1,j+1)]), method='bounded', options={'xatol':1e-10})
    candidates = [(float(opt.fun),float(opt.x)),(float(scores[j]),float(grid[j]))]
    score, energy = min(candidates)
    pred, scale, offset, rss, rate = evaluate(energy, True)
    return dict(activation_energy_eV=energy, prefactor_s_inv=nu, signal_scale=scale, baseline=offset,
                normalized_rmse=float(np.sqrt(rss/len(T))/np.ptp(signal)),
                r_squared=float(1-rss/np.sum((signal-signal.mean())**2)), n_points=len(T),
                success=bool(opt.success), message=str(opt.message),
                energy_search_boundary=bool(abs(energy-grid[0])<1e-5 or abs(energy-grid[-1])<1e-5),
                coarse_best_eV=float(grid[j])), pred, rate


def main():
    protocol_bytes = (OUT/'protocol.json').read_bytes()
    cfg = json.loads(protocol_bytes)
    assert hashlib.sha256((OUT/'digitized.csv').read_bytes()).hexdigest() == cfg['data_sha256']
    data = np.genfromtxt(OUT/'digitized.csv', delimiter=',', names=True)
    records, predictions, curves = [], [], {}
    for window, (lo,hi) in cfg['windows_K'].items():
        mask = (data['temperature_K']>=lo) & (data['temperature_K']<=hi) & np.isfinite(data['desorption_rate_ML_s'])
        T = data['temperature_K'][mask]
        signal = data['desorption_rate_ML_s'][mask]
        assert len(T)>=30 and np.all(np.diff(T)>0)
        for baseline in cfg['baseline_cases']:
            cases = [('fixed_prefactor',None)] + [('production_free_prefactor',nu) for nu in cfg['free_prefactor_starts_s_inv']]
            for method, start_nu in cases:
                case = f'{window}_{method}_baseline{int(baseline)}_start{start_nu}'
                started = time.monotonic()
                try:
                    if method == 'fixed_prefactor':
                        result, pred, rate = fixed_fit(T,signal,cfg,baseline)
                    else:
                        fit,pred = fit_polanyi_wigner(T-273.15,signal,cfg['beta_K_s'], reaction_order=1.,
                                                     initial_energy_ev=cfg['initial_energy_eV'],initial_prefactor_s_inv=start_nu,
                                                     fit_baseline=baseline,max_nfev=cfg['free_max_nfev'])
                        result = fit.as_dict()
                    energy = result['activation_energy_eV']/K_B_EV
                    row = dict(case=case, method=method, window=window, baseline_fitted=baseline,
                               initial_prefactor_s_inv=start_nu, energy_K=energy,
                               energy_kJ_mol=result['activation_energy_eV']*96.4853321233,
                               difference_from_dominant_reference_K=energy-cfg['energy_reference_K'],
                               relative_difference_percent=100*(energy/cfg['energy_reference_K']-1),result=result)
                    records.append(row)
                    curves[case] = (T,signal,pred)
                    predictions.extend([[case,float(t),float(y),float(p),float(y-p)] for t,y,p in zip(T,signal,pred)])
                    print(case, round(energy,4), result['normalized_rmse'], result['success'],flush=True)
                    if window=='primary' and baseline and method=='fixed_prefactor':
                        # Independent exact first-order survival, quadrature from same T0.
                        E=result['activation_energy_eV']
                        integral=np.array([quad(lambda t: cfg['fixed_prefactor_s_inv']/cfg['beta_K_s']*np.exp(-E/K_B_EV/t),T[0],t,epsabs=1e-11,epsrel=1e-10)[0] for t in T])
                        exact=cfg['fixed_prefactor_s_inv']*np.exp(-E/K_B_EV/T)*np.exp(-integral)
                        numerical_check=dict(max_rate_difference_relative_to_peak=float(np.max(abs(rate-exact))/np.max(exact)),
                                             tolerance=2e-5,passed=bool(np.max(abs(rate-exact))/np.max(exact)<2e-5))
                except Exception as error:
                    records.append(dict(case=case,method=method,window=window,baseline_fitted=baseline,error=repr(error)))
                    print(case,'FAILED',repr(error),flush=True)
                records[-1]['elapsed_seconds']=time.monotonic()-started
    # Four engineering perturbations, not random noise or confidence intervals.
    quality=json.loads((OUT/'extraction_quality.json').read_text())
    lo,hi=cfg['windows_K']['primary']
    mask=(data['temperature_K']>=lo)&(data['temperature_K']<=hi)&np.isfinite(data['desorption_rate_ML_s'])
    for tsign in (-1,1):
        for ysign in (-1,1):
            T=data['temperature_K'][mask]+tsign*quality['additional_axis_placement_allowance_K']
            signal=data['desorption_rate_ML_s'][mask]+ysign*(data['signal_pixel_threshold_bound'][mask]+quality['signal_axis_placement_allowance_ML_s'])
            result,pred,_=fixed_fit(T,signal,cfg,True)
            case=f'pixel_corner_T{tsign}_signal{ysign}'
            records.append(dict(case=case,method='fixed_prefactor_pixel_sensitivity',temperature_offset_sign=tsign,
                                signal_bound_sign=ysign,energy_K=result['activation_energy_eV']/K_B_EV,result=result))
            predictions.extend([[case,float(t),float(y),float(p),float(y-p)] for t,y,p in zip(T,signal,pred)])
            print(case,records[-1]['energy_K'],flush=True)
    payload=dict(protocol_sha256=hashlib.sha256(protocol_bytes).hexdigest(),protocol=cfg,records=records,
                 independent_numerical_check=numerical_check,
                 source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'tpd_spectra/kinetics.py',ROOT/'tpd_spectra/analysis.py']},
                 software=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__))
    # Retain nonfinite diagnostics as JSON null, never nonstandard Infinity/NaN.
    payload=json.loads(json.dumps(payload),parse_constant=lambda _:None)
    (OUT/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    with (OUT/'predictions.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['case','temperature_K','observed_or_perturbed_ML_s','prediction_ML_s','observed_minus_prediction_ML_s']);writer.writerows(predictions)
    fig,axes=plt.subplots(2,1,figsize=(9,7),layout='constrained',sharex=True)
    for i,baseline in enumerate(cfg['baseline_cases']):
        fixed=next(r for r in records if r.get('window')=='primary' and r['method']=='fixed_prefactor' and r['baseline_fitted']==baseline and 'result' in r)
        free=min((r for r in records if r.get('window')=='primary' and r['method']=='production_free_prefactor' and r['baseline_fitted']==baseline and 'result' in r),key=lambda r:r['result']['normalized_rmse'])
        T,y,p=curves[fixed['case']]
        axes[0].scatter(T,y,s=9,color='black',label='Digitized experiment' if i==0 else None)
        for record,style in [(fixed,'-'),(free,'--')]:
            T,y,p=curves[record['case']]
            label=f"{'Fixed nu' if record['method']=='fixed_prefactor' else 'Free nu'}, baseline {'free' if baseline else '0'}: {record['energy_K']:.0f} K"
            line,=axes[0].plot(T,p,style,lw=1.3,label=label)
            axes[1].plot(T,y-p,style,color=line.get_color(),lw=1)
    axes[0].set(ylabel='Figure rate (ML/s)',title='Ethanol/Au: single-state comparison, primary 110–165 K window')
    axes[0].legend(fontsize=8)
    axes[1].axhline(0,color='gray',lw=.7)
    axes[1].set(xlabel='Temperature (K)',ylabel='Experiment minus fit (ML/s)')
    fig.savefig(OUT/'comparison.png',dpi=150);plt.close(fig)


if __name__=='__main__':
    main()
