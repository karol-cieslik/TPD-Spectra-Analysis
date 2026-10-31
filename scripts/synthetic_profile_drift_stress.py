"""Stress-test the conditional profile against an omitted linear baseline drift."""
from pathlib import Path
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.kinetics import simulate_tpd
from tpd_spectra.profile_diagnostics import profile_energy_prefactor
T=np.linspace(100.,165.,161);t=T-273.15
beta=.5;Etrue=.65;nu=1e22;n=1.23;scale=.73;base=.04
_,rate=simulate_tpd(t,beta,Etrue,nu,n)
base_signal=base+scale*rate
amplitudes=[0.,.0005,.001,.002,.003,.005]
rows=[]
for amp in amplitudes:
 y=base_signal+amp*(T-T.mean())/(T.max()-T.min())
 prof=profile_energy_prefactor(t,y,beta,reaction_order=n,
   energy_grid_eV=np.linspace(.60,.70,21),log10_prefactor_bounds=(18,26))
 best=min(prof,key=lambda r:r['rss'])
 rows.append({'linear_drift_peak_to_peak':amp,
   'drift_fraction_of_signal_range':amp/np.ptp(y),
   'profile_E_eV':best['energy_eV'],'profile_log10_nu':best['log10_prefactor'],
   'energy_error_eV':best['energy_eV']-Etrue,'NRMSE':best['normalized_rmse']})
 print(rows[-1],flush=True)
out={'known_model':{'E_eV':Etrue,'nu_s-1':nu,'order':n,'beta_K_s':beta,'scale':scale,'constant_baseline':base},
 'profile_model':'fixed correct order; constant baseline only; prefactor and scale profiled',
 'energy_grid_eV':[.60,.70,21],'drift_cases':rows,
 'interpretation':'Synthetic sensitivity only. A sloped background absent from the fit model biases the inferred energy; the magnitude depends on window and profile grid. No statistical interval or experimental accuracy claim.'}
p=ROOT/'validation/synthetic/profile_linear_drift_stress.json';p.write_text(json.dumps(out,indent=2)+'\n')
print('SAVED',p)
