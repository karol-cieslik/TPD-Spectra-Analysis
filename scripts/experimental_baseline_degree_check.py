"""Compare constant and sloped profiled baselines on ethanol/Au data."""
from pathlib import Path
import json,sys,time
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.variable_projection import fit_variable_projection
D=pd.read_csv(ROOT/'validation/experimental/ethanol_2024/digitized.csv')
D=D[(D.temperature_K>=110)&(D.temperature_K<=165)].dropna(subset=['desorption_rate_ML_s'])
t=D.temperature_K.to_numpy(float)-273.15;y=D.desorption_rate_ML_s.to_numpy(float)
rows=[]
for degree in (0,1):
 start=time.perf_counter()
 f=fit_variable_projection(t,y,.15,reaction_order=1.,initial_energy_ev=1.,
   initial_prefactor_s_inv=1e18,fit_baseline=True,baseline_degree=degree)
 rows.append({'baseline_degree':degree,'success':f.success,'E_eV':f.activation_energy_eV,
   'nu_s-1':f.prefactor_s_inv,'baseline_at_mean_T':f.baseline,
   'slope_per_normalized_T':f.baseline_slope_per_normalized_T,
   'NRMSE':f.normalized_rmse,'wall_seconds':time.perf_counter()-start})
out={'dataset':'ethanol/Au(111), digitized 110–165 K primary window',
 'beta_K_s':.15,'order_fixed':1,'n_points':len(t),'results':rows,
 'interpretation':'One figure-derived experimental trace; descriptive baseline sensitivity, not independent validation. Lower residual does not establish that the sloped baseline is physically correct.'}
p=ROOT/'validation/experimental/ethanol_2024/baseline_degree_comparison.json'
p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
