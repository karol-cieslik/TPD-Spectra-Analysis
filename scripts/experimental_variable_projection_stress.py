"""Compare nuisance profiling on a complex existing TPD digitization.

The D2O/Fe3O4 trace is a numerical optimizer stress case only: its README
explicitly rejects a single-state positive validation interpretation.
"""
from pathlib import Path
import json, sys, time
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.kinetics import fit_polanyi_wigner
from tpd_spectra.variable_projection import fit_variable_projection

src=ROOT/'validation/digitized/water_2018/digitized.csv'
df=pd.read_csv(src).dropna(subset=['signal_figure_units'])
t=df.temperature_K.to_numpy(float)-273.15
y=df.signal_figure_units.to_numpy(float)
records=[]
for method in ('current','variable_projection'):
  start=time.perf_counter()
  if method=='current':
    fit,pred=fit_polanyi_wigner(t,y,3.,reaction_order=1.,initial_energy_ev=.5,
      initial_prefactor_s_inv=1e13,fit_baseline=True,max_nfev=300)
    row={'method':method,'success':fit.success,'E_eV':fit.activation_energy_eV,
      'nu_s-1':fit.prefactor_s_inv,'NRMSE':fit.normalized_rmse,
      'jacobian_condition_number':fit.jacobian_condition_number}
  else:
    fit=fit_variable_projection(t,y,3.,reaction_order=1.,initial_energy_ev=.5,
      initial_prefactor_s_inv=1e13,fit_baseline=True,max_nfev=300)
    row={'method':method,'success':fit.success,'E_eV':fit.activation_energy_eV,
      'nu_s-1':fit.prefactor_s_inv,'NRMSE':fit.normalized_rmse,'nfev_best_seed':fit.nfev}
  row['wall_seconds']=time.perf_counter()-start
  records.append(row)
  print(row,flush=True)
out={'dataset':'Zaki et al. (2018), D2O/Fe3O4(111), published-figure digitization',
  'beta_K_s':3.,'n_points':len(t),'reaction_order':1,'initial_E_eV':.5,
  'initial_nu_s-1':1e13,'baseline_fitted':True,'records':records,
  'interpretation':'Stress-only optimizer comparison. The source trace is multi-population and has arbitrary ordinate, so this single-state fit is not experimental kinetic validation. Both fits hit the prefactor lower bound and retain substantial residuals.'}
outfile=ROOT/'validation/digitized/water_2018/variable_projection_stress.json'
outfile.write_text(json.dumps(out,indent=2)+'\n')
print('SAVED',outfile)
