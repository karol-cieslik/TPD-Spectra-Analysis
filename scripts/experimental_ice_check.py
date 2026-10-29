"""Reproduce a bounded external zero-order comparison without network access."""
from pathlib import Path
import gzip, hashlib, io, json, sys
import numpy as np
from scipy.optimize import minimize_scalar
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tpd_spectra.kinetics import fit_polanyi_wigner, K_B_EV
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/experimental/ice_2024'

def leading_edge(T,y,baseline):
    def evaluate(E,details=False):
        shape=np.exp(-E/K_B_EV*(1/T-1/T[-1]))
        if baseline:
            shape0=shape-shape.mean();y0=y-y.mean()
            amp=max(0.,float(shape0@y0)/float(shape0@shape0))
            offset=float(y.mean()-amp*shape.mean())
        else:
            amp=max(0.,float(shape@y)/float(shape@shape));offset=0.
        pred=amp*shape+offset;rss=float(np.sum((pred-y)**2))
        return (pred,amp,offset,rss) if details else rss/float(np.ptp(y))**2
    opt=minimize_scalar(evaluate,bounds=(.001,1.),method='bounded',options={'xatol':1e-12})
    pred,amp,offset,rss=evaluate(float(opt.x),True)
    return dict(energy_eV=float(opt.x),energy_K=float(opt.x/K_B_EV),success=bool(opt.success),
        amplitude_ML_per_K=amp,baseline_ML_per_K=offset,rmse_ML_per_K=float(np.sqrt(rss/len(T))),
        NRMSE=float(np.sqrt(rss/len(T))/np.ptp(y)),n_points=len(T))

def main():
    protocol=json.loads((OUT/'protocol.json').read_text())
    provenance=json.loads((OUT/'provenance.json').read_text())
    records=[]
    predictions=[]
    for species,info in provenance['files'].items():
        b=gzip.decompress((OUT/'raw'/(Path(info['member']).name+'.gz')).read_bytes())
        assert hashlib.sha256(b).hexdigest()==info['sha256']
        a=np.loadtxt(io.BytesIO(b),delimiter=';',comments='#')
        for label in ['primary','sensitivity']:
            lo,hi=protocol[label+'_interval_K'];selected=a[(a[:,0]>=lo)&(a[:,0]<=hi)]
            T,y=selected.T
            if not (np.all(np.isfinite(selected)) and np.all(np.diff(T)>0)):
                records.append(dict(species=species,method='full_peak',interval=label,status='withheld_input_screen',reason='Nonfinite data or non-increasing raw temperatures; no sorting or repairs applied'))
                continue
            for baseline in protocol['baseline_cases']:
                fit,pred=fit_polanyi_wigner(T-273.15,y,protocol['beta_K_s'],reaction_order=0,
                    fit_baseline=baseline,max_nfev=200)
                result=json.loads(json.dumps(fit.as_dict()),parse_constant=lambda _:None)
                E=fit.activation_energy_eV/K_B_EV
                records.append(dict(species=species,method='full_peak',interval=label,baseline=baseline,
                    energy_K=float(E),difference_from_reference_K=float(E-protocol['reference_energy_K'][species]),
                    within_reported_band=bool(abs(E-protocol['reference_energy_K'][species])<=protocol['reference_reported_uncertainty_K'][species]),result=result))
                if label=='primary' and baseline:
                    predictions.extend([[species,float(t),float(yi),float(pi),float(yi-pi)] for t,yi,pi in zip(T,y,pred)])
                print(species,label,baseline,float(E),fit.normalized_rmse,flush=True)
        lo,hi=protocol['leading_edge_intervals_K'][species];selected=a[(a[:,0]>=lo)&(a[:,0]<hi)]
        if not np.all(np.diff(selected[:,0])>0):
            records.append(dict(species=species,method='independent_leading_edge',status='withheld_input_screen',reason='Raw temperatures are not strictly increasing'))
            continue
        for baseline in protocol['baseline_cases']:
            result=leading_edge(*selected.T,baseline)
            E=result['energy_K']
            records.append(dict(species=species,method='independent_leading_edge',baseline=baseline,
                energy_K=E,difference_from_reference_K=E-protocol['reference_energy_K'][species],
                within_reported_band=bool(abs(E-protocol['reference_energy_K'][species])<=protocol['reference_reported_uncertainty_K'][species]),result=result))
            print(species,'leading_edge',baseline,E,flush=True)
    payload=dict(protocol=protocol,records=records)
    (OUT/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    import csv
    with (OUT/'predictions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['species','temperature_K','observed_ML_per_K','predicted_ML_per_K','observed_minus_predicted_ML_per_K']);w.writerows(predictions)

if __name__=='__main__':main()
