"""Compare constant and sloped nuisance baselines on a known synthetic TPD trace."""
from pathlib import Path
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.kinetics import simulate_tpd
from tpd_spectra.variable_projection import fit_variable_projection
T=np.linspace(100.,165.,161);t=T-273.15
known={'E_eV':.65,'nu_s-1':1e22,'order':1.23,'beta_K_s':.5,'scale':.73,'baseline':.04,
       'linear_drift_peak_to_peak':.002}
_,rate=simulate_tpd(t,known['beta_K_s'],known['E_eV'],known['nu_s-1'],known['order'])
y=known['baseline']+known['scale']*rate+known['linear_drift_peak_to_peak']*(T-T.mean())/(T.max()-T.min())
rows=[]
for degree in (0,1):
 f=fit_variable_projection(t,y,known['beta_K_s'],reaction_order=known['order'],
   initial_energy_ev=known['E_eV'],initial_prefactor_s_inv=known['nu_s-1'],
   fit_baseline=True,baseline_degree=degree,max_nfev=300)
 rows.append({'baseline_degree':degree,'E_eV':f.activation_energy_eV,
   'nu_s-1':f.prefactor_s_inv,'baseline_at_mean_T':f.baseline,
   'slope_per_normalized_T':f.baseline_slope_per_normalized_T,
   'NRMSE':f.normalized_rmse,'nfev':f.nfev})
 print(rows[-1],flush=True)
out={'known_model':known,'drift_fraction_signal_range':known['linear_drift_peak_to_peak']/np.ptp(y),
 'results':rows,'interpretation':'Exact synthetic test only. Sloped baseline recovers the generating curve, while a constant-only baseline biases the fitted energy. It does not establish that a linear baseline is physically appropriate for experimental traces.'}
p=ROOT/'validation/synthetic/baseline_degree_checkpoint.json';p.write_text(json.dumps(out,indent=2)+'\n');print('SAVED',p)
