"""Deterministic multi-start comparison for current and profiled TPD fitting."""
from pathlib import Path
import json, sys, time
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.kinetics import fit_polanyi_wigner
from tpd_spectra.variable_projection import fit_variable_projection

source=ROOT/'validation/experimental/ethanol_2024/digitized.csv'
df=pd.read_csv(source)
df=df[(df.temperature_K>=110)&(df.temperature_K<=165)].dropna(subset=['desorption_rate_ML_s'])
t=df.temperature_K.to_numpy(float)-273.15
y=df.desorption_rate_ML_s.to_numpy(float)
beta=.15
starts=[(.35,1e12),(.60,1e16),(.80,1e18),(1.0,1e13),(1.20,1e24),(2.0,1e28)]
records=[]
for E,nu in starts:
  for method in ('current','variable_projection'):
    begin=time.perf_counter()
    try:
      if method=='current':
        f,p=fit_polanyi_wigner(t,y,beta,reaction_order=1.,initial_energy_ev=E,
          initial_prefactor_s_inv=nu,fit_baseline=True,max_nfev=300)
        row={'method':method,'success':f.success,'E_eV':f.activation_energy_eV,
          'nu_s-1':f.prefactor_s_inv,'NRMSE':f.normalized_rmse,
          'jacobian_condition_number':f.jacobian_condition_number}
      else:
        f=fit_variable_projection(t,y,beta,reaction_order=1.,initial_energy_ev=E,
          initial_prefactor_s_inv=nu,fit_baseline=True,max_nfev=300)
        row={'method':method,'success':f.success,'E_eV':f.activation_energy_eV,
          'nu_s-1':f.prefactor_s_inv,'NRMSE':f.normalized_rmse,'nfev_best_seed':f.nfev}
    except Exception as exc:
      row={'method':method,'success':False,'error':f'{type(exc).__name__}: {exc}'}
    row.update(start_E_eV=E,start_nu_s_1=nu,wall_seconds=time.perf_counter()-begin)
    records.append(row)
    print(row,flush=True)
out={'dataset':'ethanol/Au(111) digitized primary window 110–165 K','beta_K_s':beta,
     'n_points':len(t),'reaction_order':1,'starts':[{'E_eV':E,'nu_s-1':nu} for E,nu in starts],
     'records':records,
     'scope':'Within-dataset optimizer stress comparison; same observed trace, not six independent experimental validations. No uncertainty coverage claim.'}
target=ROOT/'validation/experimental/ethanol_2024/variable_projection_multistart.json'
target.write_text(json.dumps(out,indent=2)+'\n')
print('SAVED',target)
