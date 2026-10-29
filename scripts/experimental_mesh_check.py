"""Assess previously digitized pure-MeSH trace without redigitization or networking.

Source and derived data retain Narayanan et al. CC-BY-4.0 attribution.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import numpy as np
import scipy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tpd_spectra.analysis import leading_edge_fit, K_B_EV
from tpd_spectra.kinetics import fit_polanyi_wigner
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/experimental/mesh_2025'


def clean(value):
    return json.loads(json.dumps(value),parse_constant=lambda _:None)


def main():
    protocol=(OUT/'protocol.json').read_bytes();cfg=json.loads(protocol)
    src=ROOT/cfg['source_csv']
    assert hashlib.sha256(src.read_bytes().replace(b'\r\n',b'\n')).hexdigest()==cfg['source_sha256_canonical_lf']
    a=np.genfromtxt(src,delimiter=',',names=True)
    good=np.isfinite(a['signal_figure_units'])
    T=a['temperature_K'][good];y=a['signal_figure_units'][good];bounds=a['signal_pixel_threshold_bound'][good]
    assert np.all(np.diff(T)>0)
    lo,hi=cfg['preedge_window_K'];base=float(np.median(y[(T>=lo)&(T<=hi)]))
    quality=json.loads((src.parent/'quality.json').read_text())
    records=[];predictions=[]
    def checkpoint(row):
        records.append(clean(row))
        (OUT/'checkpoint.json').write_text(json.dumps(dict(protocol_sha256=hashlib.sha256(protocol).hexdigest(),records=records),indent=2)+'\n')
        print(row['case'], row.get('energy_K',row.get('error')),flush=True)
    def leading(case,temp,signal,lo,hi,**meta):
        try:
            fit=leading_edge_fit(temp-273.15,signal,cfg['beta_K_s'],lo-273.15,hi-273.15)
            m=(temp>=lo)&(temp<=hi)&np.isfinite(signal)&(signal>0)
            slope,intercept=np.polyfit(1/temp[m],np.log(signal[m]),1)
            prediction=fit.intercept+fit.slope/temp[m]
            row=dict(case=case,energy_K=float(fit.energy_ev/K_B_EV),energy_kJ_mol=float(fit.energy_ev*96.4853321233),
                     difference_from_TST_reference_K=float(fit.energy_ev/K_B_EV-cfg['reference_TST_energy_K']),
                     independent_OLS_difference_K=float(fit.energy_ev/K_B_EV+slope),
                     nonpositive_omitted=int(np.sum((temp>=lo)&(temp<=hi)&np.isfinite(signal)&(signal<=0))),
                     result=fit.as_dict(),**meta)
            predictions.extend([[case,float(t),float(v),float(p),float(v-p),'ln_figure_signal'] for t,v,p in zip(temp[m],np.log(signal[m]),prediction)])
            checkpoint(row)
        except Exception as error:checkpoint(dict(case=case,error=repr(error),**meta))
    for label,(lo,hi) in cfg['leading_windows_K'].items():
        for baseline in cfg['baseline_cases']:
            leading(f'leading_{label}_{baseline}',T,y-(base if baseline=='preedge_median' else 0),lo,hi,
                    method='production_leading_edge',window=label,baseline=baseline)
    for label,(lo,hi) in cfg['full_peak_windows_K'].items():
        m=(T>=lo)&(T<=hi)
        assert m.sum()>=30
        for baseline in cfg['full_peak_baseline_cases']:
            case=f'full_peak_{label}_baseline{int(baseline)}'
            try:
                fit,pred=fit_polanyi_wigner(T[m]-273.15,y[m],cfg['beta_K_s'],reaction_order=0,
                                          fit_baseline=baseline,max_nfev=cfg['full_peak_max_nfev'])
                checkpoint(dict(case=case,method='production_zero_order_full_peak',window=label,baseline_fitted=baseline,
                                energy_K=float(fit.activation_energy_eV/K_B_EV),result=fit.as_dict()))
                predictions.extend([[case,float(t),float(v),float(p),float(v-p),'figure_signal'] for t,v,p in zip(T[m],y[m],pred)])
            except Exception as error:checkpoint(dict(case=case,method='production_zero_order_full_peak',window=label,error=repr(error)))
    lo,hi=cfg['leading_windows_K']['primary']
    for tsign in (-1,1):
        for ysign in (-1,1):
            shift=tsign*quality['additional_axis_placement_allowance_K']
            leading(f'pixel_T{tsign}_signal{ysign}',T+shift,y+ysign*bounds,lo+shift,hi+shift,
                    method='leading_pixel_sensitivity',temperature_sign=tsign,signal_sign=ysign)
    payload=dict(protocol_sha256=hashlib.sha256(protocol).hexdigest(),protocol=cfg,preedge_median_figure_units=base,
                 records=records,code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'tpd_spectra/analysis.py',ROOT/'tpd_spectra/kinetics.py',ROOT/'tpd_spectra/zero_order.py']},
                 software=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__))
    (OUT/'results.json').write_text(json.dumps(clean(payload),indent=2,allow_nan=False)+'\n')
    with (OUT/'predictions.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['case','temperature_K','observed_or_transformed','prediction','residual','ordinate']);w.writerows(predictions)
    # Draw only saved sampled predictions. Gaps are observations, not filled data.
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    axes[0,0].plot(a['temperature_K'],a['signal_figure_units'],'.-',ms=2,lw=.5,color='black',label='Existing figure extraction; gaps retained')
    for row in records:
        if 'error' in row or row['method']=='leading_pixel_sensitivity':continue
        pts=[p for p in predictions if p[0]==row['case']]
        if not pts:continue
        temp=np.array([p[1] for p in pts]);obs=np.array([p[2] for p in pts]);pred=np.array([p[3] for p in pts])
        if row['method']=='production_zero_order_full_peak':
            if row['window']=='primary':
                axes[0,0].plot(temp,pred,lw=1,label=f"Full peak baseline {row['baseline_fitted']}: {row['energy_K']:.0f} K")
                axes[1,0].scatter(temp,obs-pred,s=5,label=f"Baseline {row['baseline_fitted']}")
        else:
            axes[0,1].plot(1000/temp,obs,'.',ms=2)
            axes[0,1].plot(1000/temp,pred,lw=1,label=f"{row['window']}, {row['baseline']}: {row['energy_K']:.0f} K")
            axes[1,1].scatter(temp,obs-pred,s=5,label=f"{row['window']}, {row['baseline']}")
    axes[0,0].set(xlim=(90,120),xlabel='Temperature (K)',ylabel='Figure signal (10¹⁵ molecules/K)',title='Pure MeSH, 11 ± 2.1 ML: whole-peak diagnostic')
    axes[0,1].set(xlabel='1000/T',ylabel='ln figure signal',title='Apparent leading-edge slopes; TST reference is 4610 K')
    axes[1,0].set(xlabel='Temperature (K)',ylabel='Signal residual');axes[1,0].axhline(0,color='gray',lw=.7)
    axes[1,1].set(xlabel='Temperature (K)',ylabel='Log residual');axes[1,1].axhline(0,color='gray',lw=.7)
    for ax in axes.flat:ax.legend(fontsize=7)
    fig.savefig(OUT/'comparison.png',dpi=150);plt.close(fig)


if __name__=='__main__':main()
