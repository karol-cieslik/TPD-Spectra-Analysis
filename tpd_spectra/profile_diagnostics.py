"""Conditional energy/prefactor profile diagnostics for single-state TPD fits."""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize_scalar
from .kinetics import simulate_tpd


def profile_energy_prefactor(temperature_c, signal, beta_k_s: float, *,
                             reaction_order: float = 1.0,
                             energy_grid_eV=None,
                             log10_prefactor_bounds=(3.0,30.0),
                             fit_baseline: bool = True,
                             baseline_degree: int = 0,
                             baseline_bounds=None) -> list[dict]:
    """Profile log10(prefactor), scale, and constant baseline at each energy.

    Returns a conditional residual-sum-of-squares landscape. It deliberately
    does not calculate confidence intervals: digitized trace errors are
    correlated and usually lack calibrated pointwise variances.
    """
    t=np.asarray(temperature_c,float); y=np.asarray(signal,float)
    if t.ndim!=1 or y.shape!=t.shape or len(t)<12 or not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)):
        raise ValueError('finite matching 1D arrays with at least 12 samples are required')
    if np.any(np.diff(t)<0) or beta_k_s<=0 or not np.isfinite(beta_k_s):
        raise ValueError('temperature must be non-decreasing and beta positive')
    if reaction_order<0 or not np.isfinite(reaction_order):
        raise ValueError('reaction_order must be nonnegative')
    if baseline_degree not in (0,1):
        raise ValueError('baseline_degree must be 0 or 1')
    energies=np.asarray(energy_grid_eV if energy_grid_eV is not None else np.linspace(.4,1.0,31),float)
    if energies.ndim!=1 or not len(energies) or np.any(~np.isfinite(energies)) or np.any(energies<=0):
        raise ValueError('energy_grid_eV must contain positive finite values')
    span=float(np.ptp(y)); norm=max(span,np.finfo(float).tiny)
    lo,hi=baseline_bounds or (float(y.min()-2*span),float(y.max()+span))
    if not fit_baseline: lo=hi=0.
    z=(t-t.mean())/max(float(np.ptp(t)),np.finfo(float).tiny)
    low_nu,high_nu=map(float,log10_prefactor_bounds)
    if not 3<=low_nu<high_nu<=30: raise ValueError('prefactor log bounds must lie in [3,30]')
    records=[]
    for energy in energies:
        def solve(lognu,details=False):
            _,rate=simulate_tpd(t,beta_k_s,float(energy),10.**float(lognu),reaction_order)
            peak=max(float(rate.max()),np.finfo(float).tiny); shape=rate/peak
            slope=0.0
            if fit_baseline and baseline_degree==1:
                design=np.column_stack([shape,np.ones_like(shape),z])
                coef=np.linalg.lstsq(design,y,rcond=None)[0]
                if coef[0]<0:
                    bg=np.column_stack([np.ones_like(z),z])
                    bc=np.linalg.lstsq(bg,y,rcond=None)[0]
                    coef=np.array([0.,bc[0],bc[1]])
                amp,base,slope=map(float,coef)
            elif fit_baseline:
                sh=shape-shape.mean(); sy=y-y.mean()
                amp=float(sh@sy/max(sh@sh,np.finfo(float).tiny)); base=float(y.mean()-amp*shape.mean())
                candidates=[]
                if amp>=0 and lo<=base<=hi: candidates.append((amp,base))
                for b in (lo,hi):
                    a=max(0.,float(shape@(y-b)/max(shape@shape,np.finfo(float).tiny)))
                    candidates.append((a,b))
                candidates.append((0.,float(np.clip(y.mean(),lo,hi))))
                amp,base=min(candidates,key=lambda ab:float(np.sum((ab[0]*shape+ab[1]-y)**2)))
            else:
                amp=max(0.,float(shape@y/max(shape@shape,np.finfo(float).tiny)));base=0.
            prediction=amp*shape+base+slope*z
            rss=float(np.sum((prediction-y)**2))
            return (rss,amp/peak,base,slope,float(np.sqrt(np.mean((prediction-y)**2))/norm)) if details else rss
        grid=np.linspace(low_nu,high_nu,13)
        vals=np.array([solve(x) for x in grid]); j=int(vals.argmin())
        left=grid[max(0,j-1)];right=grid[min(len(grid)-1,j+1)]
        if left<right:
            opt=minimize_scalar(solve,bounds=(left,right),method='bounded',options={'xatol':1e-5})
            lognu=float(opt.x)
        else: lognu=float(grid[j])
        rss,scale,baseline,slope,nrmse=solve(lognu,True)
        records.append({'energy_eV':float(energy),'log10_prefactor':lognu,'prefactor_s-1':10.**lognu,
                        'signal_scale':scale,'baseline':baseline,'baseline_slope_per_normalized_T':slope,
                        'rss':rss,'delta_rss':None,
                        'normalized_rmse':nrmse})
    best=min(r['rss'] for r in records)
    for r in records:r['delta_rss']=r['rss']-best
    return records
