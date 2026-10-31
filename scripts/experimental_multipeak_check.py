"""Bounded experimental curve challenge; never overwrite retained results.

python -m scripts.experimental_multipeak_check --output output/multipeak-new
Protocol and unmodified attributed inputs: validation/experimental/multipeak_ice_2024.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import platform
import subprocess
import sys
import time
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'validation/experimental/multipeak_ice_2024'


def clean(value):
    return json.loads(json.dumps(value), parse_constant=lambda _: None)


def load(case, cfg):
    raw = (SOURCE / case['raw_file']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == case['sha256']
    rows, excluded = [], []
    for number, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1):
        if not line.strip() or line.startswith('#'):
            continue
        cells = line.split(';')
        if not any(c.strip() for c in cells):
            continue
        if not all(c.strip() for c in cells):
            excluded.append(number)
            continue
        rows.append([float(c) for c in cells])
    a = np.array(rows)
    lo, hi = case['window_K']
    a = a[(a[:, 0] >= lo) & (a[:, 0] <= hi)]
    if len(a) < 20 or not np.isfinite(a).all() or not np.all(np.diff(a[:, 0]) > 0):
        raise ValueError('Selected input fails finite/increasing/native-point screen')
    return a[:, 0], a[:, case['signal_column']] * cfg['beta_K_s'], excluded


def worker(case, task, cfg, destination):
    from tpd_spectra.kinetics import fit_polanyi_wigner, fit_two_state_polanyi_wigner
    T, y, _ = load(case, cfg)
    started = time.monotonic()
    kwargs = dict(fit_baseline=cfg['fit_baseline'], max_nfev=cfg['max_nfev'],
                  initial_prefactor_s_inv=cfg['initial_prefactor_s_inv'])
    if task['states'] == 1:
        fit, pred = fit_polanyi_wigner(T - 273.15, y, cfg['beta_K_s'],
            reaction_order=task['order'], initial_energy_ev=cfg['initial_energy_eV'], **kwargs)
    else:
        fit, pred = fit_two_state_polanyi_wigner(T - 273.15, y, cfg['beta_K_s'],
            reaction_order=task['order'], initial_energies_ev=task['initial_energies_eV'], **kwargs)
    residual = y - pred
    # Same native points, same unweighted Gaussian working likelihood; no iid claim.
    rss = float(residual @ residual)
    k = 7 if task['states'] == 2 else 4  # E, log nu, scale, baseline for single-state
    # Fixed zero-order depletion boundary is selected from the sampled grid.
    # Count it explicitly in the assessment criterion, even if nuisance profiling
    # collapses the representation used by the production result.
    if task['states'] == 1 and task['order'] == 0:
        k = 4  # E, depletion boundary, amplitude, baseline; nu/scale are not independent
    n = len(y)
    aic = n * np.log(max(rss / n, np.finfo(float).tiny)) + 2 * k
    result = dict(status='completed', task=task, elapsed_seconds=time.monotonic()-started,
                  result=fit.as_dict(), assessment_aicc=float(aic+2*k*(k+1)/(n-k-1)),
                  assessment_parameter_count=k, rss=rss,
                  residual_lag1=float(np.corrcoef(residual[:-1], residual[1:])[0, 1]))
    Path(destination).write_text(json.dumps(clean(result), indent=2, allow_nan=False)+'\n')
    np.savetxt(Path(destination).with_suffix('.csv'), np.column_stack([T, y, pred, residual]),
        delimiter=',', header='temperature_K,observed_ML_s,predicted_ML_s,residual_ML_s', comments='')


def run(output, protocol_path):
    output.mkdir(parents=True, exist_ok=False)
    cfg = json.loads(protocol_path.read_text())
    (output/'protocol.json').write_bytes(protocol_path.read_bytes())
    results, qa = [], []
    for case in cfg['cases']:
        T, y, excluded = load(case, cfg)
        qa.append(dict(case=case['name'], native_points=len(T), incomplete_lines_excluded=excluded,
                       min_K=float(T.min()), max_K=float(T.max()),
                       sampled_maximum_K=float(T[np.argmax(y)])))
        tasks = [dict(states=1, order=n) for n in cfg['single_orders']]
        if case['name'] != 'NH3':
            tasks += [dict(states=2, order=1, initial_energies_eV=e)
                      for e in cfg['two_state_initial_energies_eV']]
        for index, task in enumerate(tasks):
            label = f"{case['name']}_{index}"
            dest = output/(label+'.json')
            command = [sys.executable, '-m', 'scripts.experimental_multipeak_check',
                       '--worker', json.dumps([case, task, cfg, str(dest.resolve())])]
            started = time.monotonic()
            try:
                done = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                      timeout=cfg['timeout_seconds_per_fit'])
                (output/(label+'.log')).write_text(done.stdout+'\n'+done.stderr)
                if done.returncode != 0:
                    record = dict(status='error', task=task, returncode=done.returncode)
                else:
                    record = json.loads(dest.read_text())
            except subprocess.TimeoutExpired:
                record = dict(status='timeout', task=task,
                              timeout_seconds=cfg['timeout_seconds_per_fit'])
            record.update(case=case['name'], label=label, wall_seconds=time.monotonic()-started)
            results.append(record)
            (output/'results.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n')
            print(label, record['status'], record.get('result', {}).get('normalized_rmse'), flush=True)
    (output/'input_qa.json').write_text(json.dumps(qa, indent=2)+'\n')
    environment = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                       platform=platform.platform(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                       protocol_sha256=hashlib.sha256(protocol_path.read_bytes()).hexdigest())
    (output/'environment.json').write_text(json.dumps(environment, indent=2)+'\n')
    plot(output, cfg, results)


def plot(output, cfg, results):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 2, figsize=(13, 10))
    for axs, case in zip(axes, cfg['cases']):
        T, y, _ = load(case, cfg)
        axs[0].plot(T, y, color='black', lw=2, label='measured')
        for r in results:
            if r['case'] != case['name'] or r['status'] != 'completed':
                continue
            a = np.loadtxt(output/(r['label']+'.csv'), delimiter=',', skiprows=1)
            label = r['label']+'; '+('converged' if r['result']['success'] else 'not converged')
            line, = axs[0].plot(a[:, 0], a[:, 2], label=label, lw=1)
            axs[1].plot(a[:, 0], a[:, 3], color=line.get_color(), lw=1)
        axs[0].set(title=case['description'], ylabel='ML/s')
        axs[0].legend(fontsize=7)
        axs[1].set(title='Observed minus predicted', ylabel='ML/s')
        for ax in axs:
            ax.set_xlabel('Temperature (K)')
    fig.suptitle('Experimental model challenge: curve fits do not identify physical states')
    fig.tight_layout(); fig.savefig(output/'comparison.png', dpi=150); plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker')
    parser.add_argument('--protocol', type=Path, default=SOURCE/'protocol.json')
    args = parser.parse_args()
    if args.worker:
        worker(*json.loads(args.worker))
    elif args.output:
        run(args.output.resolve(), args.protocol.resolve())
    else:
        parser.error('--output is required')
