"""Bounded independent numerical and conditional Monte Carlo assessment.

Run from repository root: python -m scripts.joss_assessment --output validation/joss
This is a specified numerical experiment, not experimental/coverage validation.
The protocol is in docs/JOSS_ASSESSMENT_PROTOCOL.md.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
from tpd_spectra.kinetics import simulate_tpd
from tpd_spectra.kinetics_explorer import compare_desorption_orders
from tpd_spectra.kinetics_uncertainty import run_kinetics_monte_carlo

KB = 8.617333262145e-5  # CODATA eV/K, independent of production constant import


def reference(temp_c, beta, energy, nu, order, theta0=1.):
    """Separable solution with independent quadrature, no production solver."""
    integral = np.array([quad(lambda k: nu / beta * np.exp(-energy / (KB*k)),
                             temp_c[0]+273.15, t+273.15,
                             epsabs=1e-11, epsrel=1e-11)[0] for t in temp_c])
    if order == 1.:
        theta = theta0*np.exp(-integral)
    else:
        base = theta0**(1-order)-(1-order)*integral
        theta = np.maximum(base, 0.)**(1/(1-order))
    rate = np.where(theta > 0, nu*theta**order*np.exp(-energy/(KB*(temp_c+273.15))), 0.)
    return theta, rate


def numerical_matrix():
    rows=[]
    for order in (0., .5, 1., 1.5, 2., 2.5):
        for beta in (.2, 1., 5.):
            for points in (141, 281):
                temp=np.linspace(80.,360.,points)
                expected,_=reference(temp,beta,.9,1e10,order,.8)
                actual,_=simulate_tpd(temp,beta,.9,1e10,order,.8)
                error=float(np.max(np.abs(actual-expected)))
                rows.append(dict(order=order,beta_K_s=beta,points=points,
                                 max_abs_coverage_error=error,tolerance=2e-6,passed=error<=2e-6))
    return rows


def summarize(result, count):
    records=[r for r in result.replicate_records if r['replicate']<=count]
    rankings={}
    for r in records:
        rankings.setdefault(r['replicate'],[]).append(r)
    complete=[rs for rs in rankings.values() if all(r['error'] is None for r in rs)]
    wins={name:0 for name in result.winning_counts}
    for rs in complete:
        wins[min(rs,key=lambda r:r['aicc'])['model']]+=1
    ranges={}
    for name in wins:
        good=[r for r in records if r['model']==name and r['error'] is None]
        ranges[name]=dict(successes=len(good), energy_range_eV=(
            np.percentile([r['energy_eV'] for r in good],[2.5,97.5]).tolist() if len(good)>=100 else None))
    return dict(prefix_replicates=count,completed=len(rankings),complete_rankings=len(complete),
                failed_rankings=len(rankings)-len(complete),winning_counts=wins,
                winning_fractions_all_completed={n:v/max(1,len(rankings)) for n,v in wins.items()},
                parameter_ranges=ranges)


def assess(output, replicates=200):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    numerical=numerical_matrix()
    result={'protocol':'docs/JOSS_ASSESSMENT_PROTOCOL.md','upstream_source':'d85be6bbaeb6b58fce12bf9b7ff2e47c5fd123ac',
            'environment':dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform()),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'numerical':numerical,'cases':[],
            'interpretation':'Conditional stability under fitted-reference iid Gaussian noise, not confidence coverage or mechanism probability.'}
    (output/'assessment.json').write_text(json.dumps(result,indent=2)+'\n')
    for case,noise,drift in [('matched_gaussian',.015,0.),('baseline_drift_mismatch',.06,.08)]:
        temp=np.linspace(80.,340.,65)
        _,rate=reference(temp,1.,1.1,1e12,1.)
        peak=float(rate.max()*1e4)
        signal=2.+1e4*rate+drift*peak*(temp-temp.mean())/np.ptp(temp)
        signal+=np.random.default_rng(123).normal(0,noise*peak,len(temp))
        np.savetxt(output/(case+'.csv'),np.column_stack([temp,signal]),delimiter=',',header='Temperature_C,Signal',comments='')
        comparison=compare_desorption_orders(temp,signal,1.,orders=('first',),max_nfev=50,multistart=False,
                                            initial_energy_ev=1.1,initial_prefactor_s_inv=1e12)
        entry=dict(case=case,true_energy_eV=1.1,true_prefactor_s_inv=1e12,beta_K_s=1.,
                   noise_fraction_of_clean_peak=noise,drift_fraction_of_clean_peak=drift,
                   input_sha256=hashlib.sha256(np.column_stack([temp,signal]).tobytes()).hexdigest(),
                   comparison=[dict(model=c.name,error=c.error,fit=c.fit.as_dict() if c.fit else None) for c in comparison],runs=[])
        result['cases'].append(entry)
        for seed in (11,42,73):
            started=time.monotonic()
            mc=run_kinetics_monte_carlo(temp,signal,1.,orders=('first',),replicates=replicates,
                seed=seed,max_nfev=50,multistart=False,reference_comparison=comparison)
            record=vars(mc)
            (output/f'{case}_seed{seed}.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
            entry['runs'].append(dict(seed=seed,seconds=time.monotonic()-started,
                reference_model=mc.reference_model,noise_sigma=mc.noise_sigma,
                prefixes=[summarize(mc,n) for n in (100,replicates) if n<=mc.replicates_completed]))
            (output/'assessment.json').write_text(json.dumps(result,indent=2)+'\n')
            print(case,seed,mc.replicates_completed,'completed;',mc.failed_rankings,'failed rankings',flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    assess(args.output)
