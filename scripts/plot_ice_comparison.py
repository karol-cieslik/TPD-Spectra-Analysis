"""Plot retained experimental results without rerunning an optimizer."""
from pathlib import Path
import gzip, io, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/experimental/ice_2024'

def main():
    d=json.loads((OUT/'results.json').read_text());r=d['records']
    a=np.loadtxt(io.BytesIO(gzip.decompress((OUT/'raw/2_CO_pure.csv.gz').read_bytes())),delimiter=';',comments='#')
    p=np.genfromtxt(OUT/'predictions.csv',delimiter=',',names=True,dtype=None,encoding='utf-8')
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    ax=axes[0];ax.plot(a[:,0],a[:,1],color='black',lw=1,label='Deposited CO spectrum')
    ax.plot(p['temperature_K'],p['predicted_ML_per_K'],color='#b63b36',lw=1.5,label='Studio full-peak zero order')
    ax.set(xlim=(20,60),xlabel='Temperature (K)',ylabel='Desorption signal (ML/K)',title='Full peak: bound-limited fit')
    ax.legend(fontsize=8)
    ax=axes[1];s=a[(a[:,0]>=20)&(a[:,0]<28)];T,y=s.T
    ax.scatter(T,y,color='black',s=9,label='Deposited CO, 20–28 K')
    for b,color in [(False,'#2a638c'),(True,'#af6527')]:
        x=next(x for x in r if x['species']=='CO' and x['method']=='independent_leading_edge' and x['baseline']==b)['result']
        pred=x['amplitude_ML_per_K']*np.exp(-x['energy_K']*(1/T-1/T[-1]))+x['baseline_ML_per_K']
        ax.plot(T,pred,color=color,label=f"{'Free' if b else 'Zero'} baseline: {x['energy_K']:.0f} K")
    ax.set(xlabel='Temperature (K)',ylabel='Desorption signal (ML/K)',title='Independent leading-edge calculation')
    ax.legend(fontsize=8)
    fig.savefig(OUT/'comparison.png',dpi=180)
    plt.close(fig)

if __name__=='__main__':main()
