"""Frozen methyl-acetate assessment; retain all cases, gaps and limitations."""
from pathlib import Path
import csv
import hashlib
import json
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tpd_spectra.analysis import leading_edge_fit, K_B_EV
from tpd_spectra.kinetics import fit_polanyi_wigner
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/experimental/methyl_acetate_2024'
EV_KJMOL=96.4853321233


def leading(T,y,cfg,lo,hi):
    fit=leading_edge_fit(T-273.15,y,cfg['beta_K_s'],lo-273.15,hi-273.15)
    m=(T>=lo)&(T<=hi)&np.isfinite(y)&(y>0)
    # Independent NumPy least-squares regression, same inputs/objective.
    x=1/T[m];z=np.log(y[m]);slope,intercept=np.polyfit(x,z,1)
    energy=fit.energy_ev*EV_KJMOL
    return dict(energy_kJ_mol=float(energy),difference_from_reference_kJ_mol=float(energy-cfg['reference_kJ_mol']),
                apparent_energy_K=float(fit.energy_ev/K_B_EV),
                r_squared=float(fit.r_squared),n_points=int(fit.n_points),
                slope=float(fit.slope),intercept=float(fit.intercept),
                independent_OLS_difference_kJ_mol=float(energy-(-slope*K_B_EV*EV_KJMOL)),
                nonpositive_omitted=int(np.sum((T>=lo)&(T<=hi)&np.isfinite(y)&(y<=0))),
                statistical_CI_interpretation='Not used: correlated raster columns and systematic extraction/model uncertainty'),m


def main():
    protocol=(OUT/'protocol.json').read_bytes();cfg=json.loads(protocol)
    for name,h in cfg['hashes'].items():assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==h
    a=np.genfromtxt(OUT/'spectrum.csv',delimiter=',',names=True)
    finite=np.isfinite(a['signal_normalized_graph_height'])
    T=a['temperature_K'][finite];y=a['signal_normalized_graph_height'][finite];bounds=a['signal_pixel_threshold_bound'][finite]
    assert np.all(np.diff(T)>0)
    blo,bhi=cfg['preedge_median_window_K'];base=float(np.median(y[(T>=blo)&(T<=bhi)]))
    records=[];predictions=[]
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    axes[0,0].plot(a['temperature_K'],a['signal_normalized_graph_height'],'.-',lw=.6,ms=2,color='black',label='Recovered spectrum; gaps retained')
    for window,(lo,hi) in cfg['leading_windows_K'].items():
        for baseline in cfg['baseline_cases']:
            offset=base if baseline=='preedge_median' else 0.
            case=f'leading_{window}_{baseline}'
            try:
                result,m=leading(T,y-offset,cfg,lo,hi)
                row=dict(case=case,method='production_leading_edge',window=window,baseline=baseline,subtracted_offset=offset,**result)
                records.append(row)
                zz=np.log(y[m]-offset);pred=result['intercept']+result['slope']/T[m]
                predictions.extend([[case,float(t),float(v),float(p),float(v-p),'log_signal'] for t,v,p in zip(T[m],zz,pred)])
                axes[0,1].plot(1000/T[m],zz,'.',ms=3)
                axes[0,1].plot(1000/T[m],pred,lw=1,label=f"{window}, {baseline}: {result['energy_kJ_mol']:.2f}")
                print(case,result['energy_kJ_mol'],result['r_squared'],result['n_points'],flush=True)
            except Exception as error:records.append(dict(case=case,method='production_leading_edge',error=repr(error)))
    # Whole peak is a separate model-adequacy diagnostic, no baseline pre-subtraction.
    lo,hi=cfg['full_peak_window_K'];m=(T>=lo)&(T<=hi)
    assert m.sum()>=30
    for baseline in cfg['full_peak_baseline_cases']:
        case=f'whole_peak_baseline{int(baseline)}'
        try:
            fit,pred=fit_polanyi_wigner(T[m]-273.15,y[m],cfg['beta_K_s'],reaction_order=0,
                                       fit_baseline=baseline,max_nfev=cfg['full_peak_max_nfev'])
            result=fit.as_dict();energy=fit.activation_energy_eV*EV_KJMOL
            records.append(dict(case=case,method='production_zero_order_whole_peak',energy_kJ_mol=float(energy),result=result))
            predictions.extend([[case,float(t),float(v),float(p),float(v-p),'normalized_signal'] for t,v,p in zip(T[m],y[m],pred)])
            axes[0,0].plot(T[m],pred,lw=1,label=f'Whole peak, baseline {baseline}: {energy:.2f} kJ/mol')
            axes[1,0].scatter(T[m],y[m]-pred,s=7,label=f'Baseline {baseline}')
            print(case,energy,fit.normalized_rmse,fit.success,flush=True)
        except Exception as error:records.append(dict(case=case,method='production_zero_order_whole_peak',error=repr(error)))
    quality=json.loads((OUT/'extraction_quality.json').read_text())
    lo,hi=cfg['leading_windows_K']['primary']
    for tsign in (-1,1):
        for ysign in (-1,1):
            case=f'pixel_T{tsign}_signal{ysign}'
            shift=tsign*quality['spectrum']['axis_placement_allowance_K']
            try:
                # Shift the window with the calibration, retaining the same columns.
                result,m=leading(T+shift,y+ysign*bounds,cfg,lo+shift,hi+shift)
                records.append(dict(case=case,method='leading_pixel_sensitivity',**result))
                print(case,result['energy_kJ_mol'],flush=True)
            except Exception as error:records.append(dict(case=case,method='leading_pixel_sensitivity',error=repr(error)))
    b=np.genfromtxt(OUT/'published_transformed.csv',delimiter=',',names=True)
    m=np.isfinite(b['ln_I_minus_n_ln_theta_rel']);x=b['inverse_temperature_1000_per_K'][m];z=b['ln_I_minus_n_ln_theta_rel'][m]
    # Reverse only this descending-temperature transformed-plot coordinate order.
    temp=(1000/x)[::-1];signal=np.exp(z[::-1])
    result,m=leading(temp,signal,cfg,float(temp.min()),float(temp.max()))
    records.append(dict(case='transformed_plot_reconstruction',method='already_corrected_ordinate_not_raw_spectrum',**result))
    pred=result['intercept']+result['slope']/temp
    axes[1,1].plot(1000/temp,np.log(signal),'.',ms=3,label='Published corrected ordinate')
    axes[1,1].plot(1000/temp,pred,lw=1,label=f"Reconstructed slope: {result['energy_kJ_mol']:.2f} kJ/mol")
    predictions.extend([['transformed_plot_reconstruction',float(t),float(v),float(p),float(v-p),'published_corrected_log_ordinate'] for t,v,p in zip(temp,np.log(signal),pred)])
    print('transformed_plot_reconstruction',result['energy_kJ_mol'],flush=True)
    axes[0,0].set(xlabel='Temperature (K)',ylabel='Normalized graph height',title='Whole-peak diagnostic includes phase shoulder')
    axes[0,1].set(xlabel='1000/T',ylabel='ln signal',title='Spectrum-derived apparent leading-edge energies')
    axes[1,0].axhline(0,color='gray',lw=.7);axes[1,0].set(xlabel='Temperature (K)',ylabel='Observed minus fit')
    axes[1,1].set(xlabel='1000/T',ylabel='ln I − n ln relative coverage',title='Reconstruction check, not independent validation')
    for ax in axes.flat:ax.legend(fontsize=7)
    fig.savefig(OUT/'comparison.png',dpi=150);plt.close(fig)
    payload=dict(protocol_sha256=hashlib.sha256(protocol).hexdigest(),protocol=cfg,preedge_median_normalized=base,records=records,
                 code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'tpd_spectra/analysis.py',ROOT/'tpd_spectra/kinetics.py',ROOT/'tpd_spectra/zero_order.py']})
    payload=json.loads(json.dumps(payload),parse_constant=lambda _:None)
    (OUT/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    with (OUT/'predictions.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['case','temperature_K','observed_or_transformed','prediction','residual','ordinate']);w.writerows(predictions)


if __name__=='__main__':main()
