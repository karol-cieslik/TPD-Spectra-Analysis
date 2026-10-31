"""Compare current and profiled-nuisance fits on the retained ethanol/Au trace.

This checks numerical equivalence and optimizer behavior for an existing
experimental digitization. It is not a new kinetic validation dataset.
"""
from pathlib import Path
import json, sys, time
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.kinetics import fit_polanyi_wigner
from tpd_spectra.variable_projection import fit_variable_projection

source=ROOT/'validation/experimental/ethanol_2024/digitized.csv'
df=pd.read_csv(source)
mask=(df.temperature_K>=110)&(df.temperature_K<=165)&df.desorption_rate_ML_s.notna()
df=df.loc[mask]
t=df.temperature_K.to_numpy(float)-273.15
y=df.desorption_rate_ML_s.to_numpy(float)
beta=.15
start=time.perf_counter()
current,pred=fit_polanyi_wigner(t,y,beta,reaction_order=1.,initial_energy_ev=1.,
    initial_prefactor_s_inv=1e18,fit_baseline=True,max_nfev=300)
current_seconds=time.perf_counter()-start
start=time.perf_counter()
profiled=fit_variable_projection(t,y,beta,reaction_order=1.,initial_energy_ev=1.,
    initial_prefactor_s_inv=1e18,fit_baseline=True,max_nfev=300)
profiled_seconds=time.perf_counter()-start
out={
 'dataset':'ethanol on Au(111), 2024, digitized primary window 110-165 K',
 'beta_K_s':beta,'n_points':len(t),
 'current':{'E_eV':current.activation_energy_eV,'nu_s-1':current.prefactor_s_inv,
    'scale':current.signal_scale,'baseline':current.baseline,'NRMSE':current.normalized_rmse,
    'jacobian_condition_number':current.jacobian_condition_number,'wall_seconds':current_seconds,
    'nonlinear_parameter_count':4},
 'variable_projection':{'E_eV':profiled.activation_energy_eV,'nu_s-1':profiled.prefactor_s_inv,
    'scale':profiled.signal_scale,'baseline':profiled.baseline,'NRMSE':profiled.normalized_rmse,
    'nfev_best_seed':profiled.nfev,'wall_seconds':profiled_seconds,'nonlinear_parameter_count':2,
    'seed_grid':'requested start plus first-order peak-informed estimates over nu=1e12..1e28'},
 'delta':{'E_eV':profiled.activation_energy_eV-current.activation_energy_eV,
    'nu_relative':profiled.prefactor_s_inv/current.prefactor_s_inv-1,
    'NRMSE':profiled.normalized_rmse-current.normalized_rmse},
 'interpretation':'Same single-state first-order model and source trace; a numerical optimizer comparison, not independent experimental validation. Runtime is environment-specific.'}
outpath=ROOT/'validation/experimental/ethanol_2024/variable_projection_comparison.json'
outpath.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
