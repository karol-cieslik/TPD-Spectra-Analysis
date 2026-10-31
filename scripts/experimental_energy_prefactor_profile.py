"""Profile E/log-nu tradeoff on the retained ethanol/Au digitization."""
from pathlib import Path
import json,sys,time
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tpd_spectra.profile_diagnostics import profile_energy_prefactor
D=pd.read_csv(ROOT/'validation/experimental/ethanol_2024/digitized.csv')
D=D[(D.temperature_K>=110)&(D.temperature_K<=165)].dropna(subset=['desorption_rate_ML_s'])
t=D.temperature_K.to_numpy(float)-273.15;y=D.desorption_rate_ML_s.to_numpy(float)
E=np.linspace(.60,.72,49)
start=time.perf_counter()
records=profile_energy_prefactor(t,y,.15,reaction_order=1.,energy_grid_eV=E,
    log10_prefactor_bounds=(18.,27.),fit_baseline=True)
seconds=time.perf_counter()-start
outdir=ROOT/'validation/experimental/ethanol_2024'
pd.DataFrame(records).to_csv(outdir/'energy_prefactor_profile.csv',index=False)
best=min(records,key=lambda x:x['rss'])
near=[r for r in records if r['delta_rss']<=max(best['rss']*.01,1e-12)]
summary={'dataset':'ethanol/Au(111), digitized 110–165 K window','beta_K_s':.15,
 'order_fixed':1,'baseline':'profiled bounded constant offset','energy_grid_eV':[float(E.min()),float(E.max()),len(E)],
 'log10_prefactor_profile_bounds':[18,27],'best_grid_point':best,
 'descriptive_1pct_RSS_band_eV':[min(r['energy_eV'] for r in near),max(r['energy_eV'] for r in near)] if near else None,
 'band_note':'Exploratory grid description only; not a confidence interval. Digitization pixels are correlated and no pointwise variance is calibrated.',
 'wall_seconds':seconds,'n_points':len(t),'records_csv':'energy_prefactor_profile.csv'}
(outdir/'energy_prefactor_profile_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=pd.DataFrame(records)
fig,(ax1,ax2)=plt.subplots(2,1,figsize=(7,6),sharex=True)
ax1.plot(P.energy_eV,P.delta_rss*1e6,'o-',ms=3)
ax1.set_ylabel('Profile ΔRSS (× 10⁻⁶)')
ax1.set_title('E–prefactor profile — conditional on first-order single-state model')
ax1.grid(alpha=.25)
ax2.plot(P.energy_eV,P.log10_prefactor,'o-',ms=3,color='#a24b9b')
ax2.set_xlabel('Activation energy (eV)')
ax2.set_ylabel('Best log₁₀(prefactor / s⁻¹)')
ax2.grid(alpha=.25)
fig.tight_layout()
fig.savefig(outdir/'energy_prefactor_profile.png',dpi=170)
plt.close(fig)
