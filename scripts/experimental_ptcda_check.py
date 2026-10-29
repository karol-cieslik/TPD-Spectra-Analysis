"""Inventory deposited PTCDA traces; conditional fits, not zero-coverage validation.

Usage: python scripts/experimental_ptcda_check.py /path/to/ptcda_tpd.zip
Download archive: https://data.fz-juelich.de/api/access/datafile/11413
Selection rules live in protocol.json and precede any optimization. No networking.
"""
from pathlib import Path
import csv, gzip, hashlib, io, json, sys, zipfile
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tpd_spectra.kinetics import fit_polanyi_wigner

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation/experimental/ptcda_au111'
ARCHIVE_SHA = '265956f4b776e82e0248edc2b2cd07d38f403ae3bde56fe701961b45c863a043'

def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def main():
    archive = (Path(sys.argv[1]) if len(sys.argv)>1 else OUT/'source.zip').read_bytes()
    assert hashlib.sha256(archive).hexdigest() == ARCHIVE_SHA, 'Archive checksum mismatch'
    protocol = json.loads((OUT/'protocol.json').read_text())
    inventory, results = [], []
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for name in z.namelist():
            if name.endswith('/'): continue
            raw = z.read(name)
            row = dict(file=Path(name).name, sha256=hashlib.sha256(raw).hexdigest(), selected=False)
            try:
                a = np.loadtxt(io.BytesIO(raw), skiprows=3)
                if a.ndim != 2 or a.shape[1] != 3:
                    raise ValueError('Not exactly three numeric columns; channel mapping required')
                a = a[(a[:,1]>=550)&(a[:,1]<=740)]
                if len(a)<100 or a[0,1]>552 or a[-1,1]<738:
                    raise ValueError('Does not span the frozen 550-740 K interval')
                t,T,y = a.T
                if not np.all(np.isfinite(a)) or np.any(np.diff(t)<=0):
                    raise ValueError('Nonfinite data or nonincreasing time')
                span = float(np.ptp(y))
                ramp = float(np.max(np.abs(T-(T[0]+t-t[0]))))
                edge = float(max(np.mean(y[:10])-np.min(y),np.mean(y[-10:])-np.min(y))/span) if span else 1.
                row.update(points=len(a), peak_K=float(T[np.argmax(y)]), signal_span=span,
                           ramp_max_mismatch_K=ramp, endpoint_fraction=edge,
                           temperature_reversals=int(np.sum(np.diff(T)<0)))
                if np.any(np.diff(T)<=0): raise ValueError('Temperature is not strictly increasing')
                if ramp>2: raise ValueError('Anchored 1 K/s mismatch exceeds 2 K')
                if span<=0 or edge>.15: raise ValueError('Insufficient signal or endpoint screen fails')
                row['selected']=True
                row['reason']='All frozen screens passed; coverage still unassigned'
                for baseline in (True,False):
                    for nu in protocol['initial_prefactors_s_inv']:
                        fit,pred=fit_polanyi_wigner(T-273.15,y,1.,reaction_order=1.,fit_baseline=baseline,
                            initial_energy_ev=2.,initial_prefactor_s_inv=nu,max_nfev=300)
                        record=dict(file=Path(name).name,fit_baseline=baseline,initial_prefactor_s_inv=nu,
                                    fit=fit.as_dict())
                        # json serialization retains diagnostics while avoiding nonstandard NaN/Infinity.
                        record=json.loads(json.dumps(record),parse_constant=lambda _:None)
                        results.append(record)
                        print(row['file'],baseline,nu,fit.activation_energy_eV,fit.normalized_rmse,fit.success,flush=True)
            except (ValueError,RuntimeError) as exc:
                row['reason']=str(exc)
            inventory.append(row)
    keys=sorted(set().union(*(r.keys() for r in inventory)))
    with (OUT/'inventory.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(inventory)
    payload = dict(protocol=protocol,archive_files=len(inventory),
         selected_files=sum(r['selected'] for r in inventory),fit_records=results,
         interpretation='Conditional constant-energy fits; published zero-coverage complete-analysis energy is not the same estimand.')
    (OUT/'fits.json.gz').write_bytes(gzip.compress((json.dumps(payload, indent=2, allow_nan=False)+'\n').encode(),mtime=0))

if __name__=='__main__': main()
