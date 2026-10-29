"""Post-fix joint parameter/ranking reassessment; not mechanism probabilities.

Protocol fixed before execution: reuse both recorded 65-point datasets, compare
first/second orders with initial E=1.1, nu=1e12, 50 evaluations and no multistart.
For seeds 11/42/73 run 200 conditional refits, summarize nested 50/100/200 prefixes.
Each seed runs in a separate subprocess with a 300-second wall limit. Retain
timeouts/failures without calling them completed rankings. Three seeds on one
dataset per case do not measure frequentist model-selection accuracy/coverage.
"""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from scripts.joss_assessment import summarize
from tpd_spectra.kinetics_explorer import compare_desorption_orders
from tpd_spectra.kinetics_uncertainty import run_kinetics_monte_carlo


def worker(case,seed,output):
    source=Path('validation/joss_parameter_stability')/(case+'.csv')
    data=np.genfromtxt(source,delimiter=',',names=True)
    t,y=data['Temperature_C'],data['Signal']
    comparison=compare_desorption_orders(t,y,1.,orders=('first','second'),
        initial_energy_ev=1.1,initial_prefactor_s_inv=1e12,max_nfev=50,multistart=False)
    mc=run_kinetics_monte_carlo(t,y,1.,orders=('first','second'),replicates=200,
        seed=seed,max_nfev=50,multistart=False,reference_comparison=comparison)
    with gzip.open(output,'wt',encoding='utf-8') as f:json.dump(vars(mc),f,allow_nan=False)
    print(json.dumps(dict(case=case,seed=seed,reference_model=mc.reference_model,
                         prefixes=[summarize(mc,n) for n in (50,100,200)])))


def run(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result=dict(protocol=__doc__,runs=[])
    from concurrent.futures import ThreadPoolExecutor, as_completed
    def task(case, seed):
        started=time.monotonic()
        try:
            p=subprocess.run([sys.executable,'-m','scripts.joss_postfix_assessment',
                '--worker',case,'--seed',str(seed),'--output',str(out/f'{case}_{seed}.json.gz')],
                capture_output=True,text=True,encoding='utf-8',timeout=300)
            row=json.loads(p.stdout) if p.returncode==0 else dict(case=case,seed=seed,error=p.stderr[-2000:])
        except subprocess.TimeoutExpired:row=dict(case=case,seed=seed,timeout_seconds=300)
        row['elapsed_seconds']=time.monotonic()-started
        return row
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(task,c,s) for c in ('matched_gaussian','baseline_drift_mismatch') for s in (11,42,73)]
        for future in as_completed(futures):
            row=future.result();result['runs'].append(row)
            result['runs'].sort(key=lambda r:(r['case'],r['seed']))
            (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
            print(row['case'],row['seed'],'timeout' if 'timeout_seconds' in row else 'error' if 'error' in row else 'completed',flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True);p.add_argument('--worker');p.add_argument('--seed',type=int)
    a=p.parse_args()
    worker(a.worker,a.seed,a.output) if a.worker else run(a.output)
