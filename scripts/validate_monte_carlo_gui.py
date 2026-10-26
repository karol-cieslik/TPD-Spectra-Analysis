"""Audit real Tk Monte Carlo progress using the loaded default first-peak data.

Run in an environment with a working Tk display, for example:
    python scripts/validate_monte_carlo_gui.py --replicates 500 --seed 42

This exercises one first-order hypothesis and GUI lifecycle. It does not validate
physical order identification, interval coverage or experimental applicability.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import time
import tkinter as tk
import traceback

import numpy as np

from tpd_spectra import __version__
from tpd_spectra.workflow_gui import WorkflowApp


def validate(output, replicates=500, seed=42):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    record = {
        'audit': 'real Tk worker, first-order Monte Carlo refits',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'platform': platform.platform(),
        'python': platform.python_version(),
        'application_version': __version__,
        'dependencies': {name: version(name) for name in ('numpy','scipy','pandas','matplotlib')},
        'tk_version': tk.TkVersion,
        'requested_replicates': replicates,
        'seed': seed,
        'limitation': ('One fixed first-order hypothesis on the loaded default first-peak interval. '
            'This checks GUI progress, responsiveness and state retention; it is not physical '
            'order identification, experimental validation or uncertainty coverage validation.'),
    }
    root = None
    try:
        root = tk.Tk()
        app = WorkflowApp(root)
        app.open_default_demo()
        panel = app.modeling_panel
        dataset, region = app.project.context()
        original = dataset.spectrum.signal.copy()
        for key in ('zero','second','fractional','multistart'):
            panel.variables[key].set(False)
        panel.variables['replicates'].set(str(replicates))
        panel.variables['seed'].set(str(seed))
        panel.variables['max_nfev'].set('150')
        app.stages.select(1)
        root.update()
        panel.compare()
        deadline = time.monotonic() + 120
        while app.job_busy and time.monotonic() < deadline:
            root.update()
            time.sleep(.005)
        assert not app.job_busy, 'comparison timeout'
        comparison = panel.session()['comparison']
        assert comparison['candidates'][0]['error'] is None, comparison['candidates'][0]['error']
        arrays = np.column_stack((comparison['temperature'],comparison['signal'])).astype('<f8')
        record.update(
            source_file=Path(dataset.path).name,
            source_sha256=dataset.digest,
            input_arrays_sha256=hashlib.sha256(arrays.tobytes()).hexdigest(),
            input_array_encoding='C-contiguous little-endian float64 columns: temperature_C, signal',
            input_points=len(arrays),
            region_c=[region.lower,region.upper],
            settings=comparison['snapshot']['settings'],
        )
        metadata_path = Path(dataset.path).with_suffix('.json')
        if metadata_path.is_file():
            metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
            if metadata.get('csv_sha256') == dataset.digest:
                record['observation_metadata'] = {key: metadata.get(key) for key in
                    ('observational_variant','noise_fraction_of_clean_maximum','random_seed','noise','baseline')}
        snapshots = []
        heartbeats = []
        raw_visible_samples = []
        started = time.monotonic()

        def heartbeat():
            heartbeats.append(time.monotonic())
            snapshots.append(panel.mc_progress.completed)
            lines = [line for line in panel.fig.axes[0].lines if line.get_label() == 'Original measured spectrum']
            raw_visible_samples.append(bool(lines) and np.array_equal(lines[0].get_ydata(),original))
            if app.job_busy:
                root.after(10,heartbeat)

        panel.monte_carlo()
        root.after(10,heartbeat)
        deadline = started + max(600,replicates * 3)
        while app.job_busy and time.monotonic() < deadline:
            root.update()
            time.sleep(.003)
        root.update()
        assert not app.job_busy, 'Monte Carlo timeout'
        mc = panel.session()['monte_carlo']['result']
        snapshots.append(panel.mc_progress.completed)
        assert mc['replicates_completed'] == replicates
        assert panel.mc_progress.state == 'Completed'
        assert snapshots == sorted(snapshots) and snapshots[-1] == replicates
        assert len(heartbeats) > (20 if replicates >= 50 else 0)
        assert all(raw_visible_samples)
        np.testing.assert_array_equal(dataset.spectrum.signal,original)
        successful = sum(mc['successful_parameter_fits'].values())
        attempted = mc['replicates_completed'] * len(mc['successful_parameter_fits'])
        record.update(
            status='passed',
            elapsed_seconds=round(time.monotonic()-started,3),
            completed=mc['replicates_completed'],
            successful_fitting_attempts=successful,
            failed_fitting_attempts=attempted-successful,
            failed_rankings=mc['failed_rankings'],
            heartbeats=len(heartbeats),
            unique_progress_values=sorted(set(snapshots)),
            progress_monotonic=True,
            raw_visible_throughout=True,
            progress_text=panel.progress_count.get(),
            completion_text=panel.progress_detail.get(),
        )
    except Exception:
        record.update(status='failed',error=traceback.format_exc())
        raise
    finally:
        output.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        if root is not None:
            for callback in root.tk.call('after','info'):
                root.after_cancel(callback)
            root.destroy()
        print(json.dumps({key: value for key,value in record.items() if key != 'unique_progress_values'},indent=2))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('validation/monte-carlo-gui.json'))
    parser.add_argument('--replicates',type=int,default=500)
    parser.add_argument('--seed',type=int,default=42)
    args = parser.parse_args()
    if not 1 <= args.replicates <= 10000:
        parser.error('--replicates must be in 1–10000')
    if args.seed < 0:
        parser.error('--seed must be non-negative')
    validate(args.output,args.replicates,args.seed)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
