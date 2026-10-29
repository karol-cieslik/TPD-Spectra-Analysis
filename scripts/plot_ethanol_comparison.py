"""Plot saved ethanol fit parameters on a dense model grid; no refitting."""
from pathlib import Path
import json
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tpd_spectra.kinetics import simulate_tpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/experimental/ethanol_2024'


def main():
    saved=json.loads((OUT/'results.json').read_text())
    rows=saved['records']
    a=np.genfromtxt(OUT/'digitized.csv',delimiter=',',names=True)
    mask=(a['temperature_K']>=110)&(a['temperature_K']<=165)&np.isfinite(a['desorption_rate_ML_s'])
    T=a['temperature_K'][mask];y=a['desorption_rate_ML_s'][mask]
    grid=np.linspace(T[0],T[-1],1000)
    fig,axes=plt.subplots(2,1,figsize=(9,7),layout='constrained',sharex=True)
    axes[0].scatter(T,y,s=10,color='black',label='Recovered black marks (correlated raster columns)',zorder=4)
    for baseline in (False,True):
        for method,style in [('fixed_prefactor','-'),('production_free_prefactor','--')]:
            candidates=[r for r in rows if r.get('window')=='primary' and r['method']==method and r['baseline_fitted']==baseline and 'result' in r]
            record=min(candidates,key=lambda r:r['result']['normalized_rmse'])
            result=record['result']
            def model(temps):
                _,rate=simulate_tpd(temps-273.15,.15,result['activation_energy_eV'],result['prefactor_s_inv'],1.)
                return result['baseline']+result['signal_scale']*rate
            pred=model(T)
            label=f"{'Fixed nu' if method=='fixed_prefactor' else 'Free nu'}, baseline {'free' if baseline else '0'}: {record['energy_K']:.0f} K"
            line,=axes[0].plot(grid,model(grid),style,lw=1.3,label=label)
            axes[1].scatter(T,y-pred,s=7,color=line.get_color(),alpha=.7)
    # Missing source columns stay visible; model lines are dense simulations.
    missing=(a['temperature_K']>=110)&(a['temperature_K']<=165)&~np.isfinite(a['desorption_rate_ML_s'])
    axes[0].plot(a['temperature_K'][missing],np.full(missing.sum(),-.0007),'|',color='gray',label='Unrecovered columns')
    axes[0].set(ylabel='Figure rate (ML/s)',title='Ethanol/Au: single-state comparison, primary 110–165 K window')
    axes[0].legend(fontsize=8)
    axes[1].axhline(0,color='gray',lw=.7)
    axes[1].set(xlabel='Temperature (K)',ylabel='Experiment minus model (ML/s)')
    fig.savefig(OUT/'comparison.png',dpi=150)
    plt.close(fig)


if __name__=='__main__':
    main()
