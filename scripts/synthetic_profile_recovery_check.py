"""Known-parameter recovery checks for the conditional E/log-nu profiler."""
from pathlib import Path
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.kinetics import simulate_tpd
from tpd_spectra.profile_diagnostics import profile_energy_prefactor
cases=[
 {'name':'near-first fractional order','order':1.23,'E_eV':.65,'nu_s-1':1e22,'beta':.5,'T_K':[100.,165.],'E_grid':[.60,.70,41],'lognu_bounds':[18.,26.]},
 {'name':'second order','order':2.,'E_eV':.70,'nu_s-1':1e15,'beta':1.,'T_K':[150.,280.],'E_grid':[.65,.75,41],'lognu_bounds':[12.,20.]},
]
results=[]
for c in cases:
 tK=np.linspace(*c['T_K'],161); tC=tK-273.15
 _,rate=simulate_tpd(tC,c['beta'],c['E_eV'],c['nu_s-1'],c['order'])
 scale=.73; baseline=.04
 y=baseline+scale*rate
 egrid=np.linspace(*c['E_grid'][:2],int(c['E_grid'][2]))
 prof=profile_energy_prefactor(tC,y,c['beta'],reaction_order=c['order'],energy_grid_eV=egrid,
      log10_prefactor_bounds=tuple(c['lognu_bounds']),fit_baseline=True)
 best=min(prof,key=lambda r:r['rss'])
 result={'name':c['name'],'known':{'order':c['order'],'E_eV':c['E_eV'],'nu_s-1':c['nu_s-1'],'scale':scale,'baseline':baseline},
   'recovered_profile_grid':best,'E_error_eV':best['energy_eV']-c['E_eV'],
   'log10_nu_error':best['log10_prefactor']-np.log10(c['nu_s-1']),
   'NRMSE':best['normalized_rmse'],'grid_size':len(prof),
   'interpretation':'Exact-model synthetic numerical recovery only; does not validate real-data uncertainty or model selection.'}
 results.append(result);print(result,flush=True)
out={'cases':results,'pointwise_noise':'none','statistical_intervals':'not computed'}
path=ROOT/'validation/synthetic/profile_recovery_checkpoint.json'
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(out,indent=2)+'\n')
print('SAVED',path)
