"""Command-line batch interface for the TPD Spectra analysis core."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import json
import hashlib
from datetime import datetime, timezone
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .analysis import analyze_file, load_spectrum, smooth_signal
from .kinetics import fit_polanyi_wigner, fit_two_state_polanyi_wigner
import numpy as np
from . import __version__
from .identity import build_identity
from .ramp import checked_linear_ramp
import importlib.metadata


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


CONFIG_KEYS = {
    'leading_edge': 'leading_edge', 'redhead_region': 'redhead_region',
    'prefactor': 'prefactor', 'window': 'window', 'filter': 'filter',
    'max_time_min': 'max_time_min', 'kinetic_fit': 'kinetic_fit',
    'kinetic_order': 'kinetic_order', 'kinetic_initial_energy': 'kinetic_initial_energy',
    'kinetic_initial_prefactor': 'kinetic_initial_prefactor',
    'kinetic_no_baseline': 'kinetic_no_baseline', 'kinetic_model': 'kinetic_model',
    'kinetic_ramp_tolerance_K': 'kinetic_ramp_tolerance_K',
}


def main(argv=None) -> int:
    # Load config first so explicit CLI flags can override its defaults.
    argv = list(sys.argv[1:] if argv is None else argv)
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument('--config')
    pre.add_argument('--preset', choices=('standard', 'broad-peak', 'unsmoothed'))
    pre_args, _ = pre.parse_known_args(argv)
    presets = {
        'standard': {},
        # Broader search windows are exploratory presets, not universal settings.
        'broad-peak': {'leading_edge': [120.0, 190.0], 'redhead_region': [200.0, 450.0]},
        'unsmoothed': {'window': 1, 'filter': 'none'},
    }
    config_defaults = {}
    if pre_args.preset:
        config_defaults.update(presets[pre_args.preset])
    if pre_args.config:
        try:
            loaded = json.loads(Path(pre_args.config).read_text(encoding='utf-8'))
            if not isinstance(loaded, dict):
                raise ValueError('configuration root must be a JSON object')
            unknown = sorted(set(loaded) - set(CONFIG_KEYS))
            if unknown:
                raise ValueError(f'unknown configuration keys: {", ".join(unknown)}')
            config_defaults.update(loaded)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f'Invalid --config: {exc}')

    parser = argparse.ArgumentParser(description='Batch analysis of TPD/TDS instrument CSV files')
    parser.add_argument('input', nargs='+', default=['input'], help='one or more CSV files or directories (default: input/)')
    parser.add_argument('--output', default='output', help='output directory (default: output/)')
    parser.add_argument('--config', help='load analysis parameters from a JSON file')
    parser.add_argument('--preset', choices=('standard', 'broad-peak', 'unsmoothed'), help='named parameter preset; explicit CLI flags override preset/config')
    parser.add_argument('--save-config', help='write effective analysis parameters to this JSON file')
    parser.add_argument('--leading-edge', nargs=2, type=float, metavar=('LOW_C','HIGH_C'), default=(130.,170.))
    parser.add_argument('--redhead-region', nargs=2, type=float, metavar=('LOW_C','HIGH_C'), default=(230.,400.))
    parser.add_argument('--prefactor', type=float, default=1e20, help='assumed first-order prefactor in s^-1 (default: 1e20)')
    parser.add_argument('--window', type=int, default=10, help='smoothing window in points (default: 10)')
    parser.add_argument('--filter', choices=('median','mean','none'), default='median')
    parser.add_argument('--max-time-min', type=float, default=10.0, help='maximum time for heating-rate fit; use --max-time-min -1 to disable')
    parser.add_argument('--kinetic-fit', action='store_true',
                        help='also fit a single-state Polanyi–Wigner model to each smoothed full trace')
    parser.add_argument('--kinetic-model', choices=('single','two-state','compare'), default='single',
                        help='single-state fit (default), exploratory two-state fit, or run both for comparison')
    parser.add_argument('--kinetic-order', choices=('0','1','2','fit'), default='1',
                        help='fixed reaction order, or fit order within [0.2, 3] (default: 1)')
    parser.add_argument('--kinetic-initial-energy', type=float, default=1.0,
                        help='initial activation-energy guess in eV (default: 1.0)')
    parser.add_argument('--kinetic-initial-prefactor', type=float, default=1e13,
                        help='initial prefactor guess in s^-1 (default: 1e13)')
    parser.add_argument('--kinetic-no-baseline', action='store_true',
                        help='fix kinetic-fit additive signal baseline at zero')
    parser.add_argument('--kinetic-ramp-tolerance-K', type=float, default=2.,
                        help='maximum measured/reconstructed ramp mismatch in K (default 2; engineering screen, not calibration)')
    parser.set_defaults(**config_defaults)
    args = parser.parse_args(argv)
    # Validate key numeric settings early, before touching the input files.
    if not all(np.isfinite(value) for value in [*args.leading_edge, *args.redhead_region,
            args.prefactor, args.kinetic_initial_energy, args.kinetic_initial_prefactor, args.max_time_min,
            args.kinetic_ramp_tolerance_K]):
        parser.error('numeric settings must be finite')
    if args.window < 1:
        parser.error('--window must be >= 1')
    if args.prefactor <= 0:
        parser.error('--prefactor must be positive')
    if args.kinetic_initial_energy <= 0 or args.kinetic_initial_prefactor <= 0:
        parser.error('kinetic initial energy and prefactor must be positive')
    if args.kinetic_ramp_tolerance_K <= 0:
        parser.error('--kinetic-ramp-tolerance-K must be positive')
    if args.kinetic_model != 'single' and not args.kinetic_fit:
        parser.error('--kinetic-model two-state/compare requires --kinetic-fit')
    if args.leading_edge[0] >= args.leading_edge[1] or args.redhead_region[0] >= args.redhead_region[1]:
        parser.error('analysis intervals must have lower bound < upper bound')
    effective_config = {
        'leading_edge': list(args.leading_edge), 'redhead_region': list(args.redhead_region),
        'prefactor': args.prefactor, 'window': args.window, 'filter': args.filter,
        'max_time_min': args.max_time_min, 'kinetic_fit': args.kinetic_fit,
        'kinetic_order': args.kinetic_order, 'kinetic_initial_energy': args.kinetic_initial_energy,
        'kinetic_initial_prefactor': args.kinetic_initial_prefactor,
        'kinetic_no_baseline': args.kinetic_no_baseline, 'kinetic_model': args.kinetic_model,
        'kinetic_ramp_tolerance_K': args.kinetic_ramp_tolerance_K,
    }
    if args.save_config:
        save_path = Path(args.save_config)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(effective_config, indent=2) + '\n', encoding='utf-8')
    sources = [Path(item) for item in args.input]
    files = []
    missing_sources = []
    for source in sources:
        if source.is_file():
            files.append(source)
        elif source.is_dir():
            files.extend(sorted(source.rglob('*.csv')))
        else:
            missing_sources.append(str(source))
    if missing_sources:
        parser.error(f'Input path does not exist: {", ".join(missing_sources)}')
    if not files:
        parser.error(f'No CSV files found at {", ".join(str(path) for path in sources)}')
    if len({file.name.casefold() for file in files}) != len(files):
        parser.error('Input filenames must be distinct within a batch; run duplicate names separately to avoid output collisions.')
    outdir = Path(args.output); outdir.mkdir(parents=True, exist_ok=True)
    results, failures, warning_rows, kinetic_rows = [], [], [], []
    input_manifest = []
    diagnostic_dir = outdir / 'diagnostics'
    diagnostic_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    for file_index, file in enumerate(files, 1):
        try:
            print(f'[{file_index}/{len(files)}] Loading and analyzing {file.name}', flush=True)
            input_manifest.append({'path': str(file.resolve()), 'name': file.name, 'size_bytes': file.stat().st_size, 'sha256': _sha256(file)})
            result = analyze_file(file, leading_edge_c=tuple(args.leading_edge),
                redhead_region_c=tuple(args.redhead_region), prefactor_s_inv=args.prefactor,
                smoothing_window=args.window, smoothing_method=args.filter,
                max_time_min=None if args.max_time_min < 0 else args.max_time_min)
            results.append(result)
            spec = load_spectrum(file)
            report = dict(spec.import_report, source_sha256=_sha256(file))
            (diagnostic_dir / f'{file.stem}_import.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            if report['rejected_records'] or report['sorted_by_time'] or spec.points_temperature_corrected:
                warning_rows.append({'file_name': file.name, 'warnings':
                    f"Import changed row order or data: rejected={len(report['rejected_records'])}; "
                    f"sorted={report['sorted_by_time']}; corrected temperatures={spec.points_temperature_corrected}. Inspect import report."})
            sig = smooth_signal(spec.signal, args.window, args.filter)
            if args.kinetic_fit:
                print(f'[{file_index}/{len(files)}] Exploratory kinetic fitting: {file.name}', flush=True)
                try:
                    order_fit = args.kinetic_order == 'fit'
                    order = 1.0 if order_fit else float(args.kinetic_order)
                    # A linear-ramp kinetic model requires a monotonic temperature
                    # coordinate. The measured channel contains jitter/reversals,
                    # so use the fitted beta and acquisition time for the model
                    # coordinate; plots remain against measured temperature.
                    kinetic_temp, ramp_check = checked_linear_ramp(
                        spec.time_min, spec.temperature_clean_c, result['heating_rate_K_s'],
                        tolerance_K=args.kinetic_ramp_tolerance_K)
                    kfit, prediction = fit_polanyi_wigner(
                        kinetic_temp, sig, result['heating_rate_K_s'],
                        reaction_order=order, fit_reaction_order=order_fit,
                        initial_energy_ev=args.kinetic_initial_energy,
                        initial_prefactor_s_inv=args.kinetic_initial_prefactor,
                        fit_baseline=not args.kinetic_no_baseline)
                    kinetic_rows.append({
                        'file_name': file.name, **kfit.as_dict(),
                        'reaction_order_setting': args.kinetic_order,
                        'heating_rate_K_s': result['heating_rate_K_s'],
                        'ramp_max_abs_deviation_K': ramp_check['max_abs_deviation_K'],
                        'ramp_rms_deviation_K': ramp_check['rms_deviation_K'],
                        'ramp_tolerance_K': ramp_check['tolerance_K'],
                        'signal_used': f'{args.filter} smoothed, window={args.window}; kinetic temperature coordinate from fitted linear ramp and acquisition time',
                        'model': 'single-state Polanyi-Wigner; linear heating ramp; signal scale and baseline nuisance parameters'})
                    kfig, kax = plt.subplots(figsize=(9, 5), constrained_layout=True)
                    kax.plot(spec.temperature_clean_c, sig, label='Smoothed experimental signal', linewidth=1)
                    kax.plot(spec.temperature_clean_c, prediction, label='Polanyi–Wigner fit', linewidth=1.5)
                    kax.set(xlabel='Temperature (°C)', ylabel='Signal (a.u.)',
                            title=f'{file.name}: full-trace kinetic fit')
                    kax.legend(fontsize='small')
                    kfig.savefig(diagnostic_dir / f'{file.stem}_kinetic_fit.png', dpi=160)
                    plt.close(kfig)
                    if not kfit.success or kfit.normalized_rmse > 0.15:
                        warning_rows.append({'file_name': file.name,
                            'warnings': f"Full-trace kinetic fit: success={kfit.success}; normalized RMSE={kfit.normalized_rmse:.4g}. Review residuals and identifiability."})
                    if kfit.jacobian_condition_number > 1e8 or not np.isfinite(kfit.jacobian_condition_number):
                        warning_rows.append({'file_name': file.name, 'warnings':
                            f'Single-state fit Jacobian condition number is {kfit.jacobian_condition_number:.4g}; fitted parameters may be poorly identifiable.'})
                    if args.kinetic_model in ('two-state', 'compare'):
                        try:
                            two_fit, two_prediction = fit_two_state_polanyi_wigner(
                                kinetic_temp, sig, result['heating_rate_K_s'], reaction_order=order,
                                initial_energies_ev=(max(0.1, args.kinetic_initial_energy * 0.8),
                                                     min(7.9, args.kinetic_initial_energy * 1.3 + 0.1)),
                                initial_prefactor_s_inv=args.kinetic_initial_prefactor,
                                fit_baseline=not args.kinetic_no_baseline)
                            two_row = {'file_name': file.name, **two_fit.as_dict(),
                                'model': 'two-state Polanyi-Wigner; independent populations; shared reaction order and baseline',
                                'reaction_order_setting': args.kinetic_order,
                                'heating_rate_K_s': result['heating_rate_K_s']}
                            kinetic_rows.append(two_row)
                            tfig, tax = plt.subplots(figsize=(9, 5), constrained_layout=True)
                            tax.plot(spec.temperature_clean_c, sig, label='Smoothed experimental signal', linewidth=1)
                            tax.plot(spec.temperature_clean_c, two_prediction, label='Two-state fit', linewidth=1.5)
                            tax.set(xlabel='Temperature (°C)', ylabel='Signal (a.u.)',
                                    title=f'{file.name}: exploratory two-state kinetic fit')
                            tax.legend(fontsize='small')
                            tfig.savefig(diagnostic_dir / f'{file.stem}_two_state_fit.png', dpi=160)
                            plt.close(tfig)
                            if two_fit.warnings:
                                warning_rows.append({'file_name': file.name, 'warnings': '; '.join(two_fit.warnings)})
                        except Exception as two_exc:
                            kinetic_rows.append({'file_name': file.name, 'model': 'two-state', 'fit_error': str(two_exc)})
                            warning_rows.append({'file_name': file.name, 'warnings': f'Two-state fit unavailable: {two_exc}'})
                except Exception as exc:
                    kinetic_rows.append({'file_name': file.name, 'fit_error': str(exc),
                                         'reaction_order_setting': args.kinetic_order})
                    print(f'WARN {file.name}: kinetic fit unavailable: {exc}', file=sys.stderr)
                    warning_rows.append({'file_name': file.name, 'warnings': f'Kinetic fit unavailable: {exc}'})
            ax.plot(spec.temperature_clean_c, sig, label=result['short_name'])
            # Per-file diagnostic plot: raw/smoothed signal and the leading-edge
            # regression residuals. No automatic baseline correction is applied.
            dfig, (dax, rax) = plt.subplots(2, 1, figsize=(9, 7), constrained_layout=True)
            dax.plot(spec.temperature_clean_c, spec.signal, color='0.65', linewidth=0.8, label='Raw signal')
            dax.plot(spec.temperature_clean_c, sig, linewidth=1.2, label='Smoothed signal')
            dax.axvspan(*tuple(args.leading_edge), alpha=0.12, label='Leading-edge interval')
            dax.axvspan(*tuple(args.redhead_region), alpha=0.10, label='Redhead search interval')
            dax.axvline(result['second_peak_temperature_C'], linestyle='--', linewidth=1, label='Selected maximum')
            dax.set(xlabel='Temperature (°C)', ylabel='Signal (a.u.)', title=f"{file.name}: signal and selected intervals")
            dax.legend(fontsize='small', loc='best')
            temp = spec.temperature_clean_c
            edge_mask = np.isfinite(temp) & np.isfinite(sig) & (temp >= args.leading_edge[0]) & (temp <= args.leading_edge[1]) & (sig > 0)
            if edge_mask.sum() >= 3:
                x = 1000.0 / (temp[edge_mask] + 273.15)
                y = np.log(sig[edge_mask])
                fit_line = np.polyfit(x, y, 1)
                residual = y - (fit_line[0] * x + fit_line[1])
                rax.scatter(x, residual, s=10)
                rax.axhline(0, color='0.3', linewidth=1)
                rax.set(xlabel='1000/T (1000 K⁻¹)', ylabel='Residual in ln(signal)', title='Leading-edge linear-fit residuals')
            else:
                rax.text(0.5, 0.5, 'Insufficient positive points for residual plot', ha='center', va='center', transform=rax.transAxes)
                rax.set_axis_off()
            dfig.savefig(diagnostic_dir / f'{file.stem}_diagnostics.png', dpi=160)
            plt.close(dfig)
            if result['diagnostic_warnings']:
                warning_rows.append({'file_name': file.name, 'warnings': result['diagnostic_warnings']})
            lead = f"{result['leading_edge_energy_eV']:.4f} eV" if pd.notna(result['leading_edge_energy_eV']) else 'not fitted'
            print(f"OK  {file.name}: E_leading={lead}; "
                  f"E_Redhead={result['redhead_energy_eV']:.4f} eV; beta={result['heating_rate_K_s']:.5g} K/s")
            if result['leading_edge_error']:
                print(f"WARN {file.name}: leading-edge fit unavailable: {result['leading_edge_error']}", file=sys.stderr)
        except Exception as exc:
            failures.append({'file_name': file.name, 'error': str(exc)})
            print(f'FAIL {file.name}: {exc}', file=sys.stderr)
    if results:
        df = pd.DataFrame(results)
        df.to_csv(outdir / 'all_desorption_parameters.csv', index=False)
        ax.set(xlabel='Temperature (°C)', ylabel='Signal (a.u.)', title='TPD/TDS spectra')
        ax.legend(loc='best', fontsize='small')
        fig.tight_layout(); fig.savefig(outdir / 'all_tds_spectra.png', dpi=160)
        plt.close(fig)
    if kinetic_rows:
        kinetic_df = pd.DataFrame(kinetic_rows)
        kinetic_df.to_csv(outdir / 'polanyi_wigner_fits.csv', index=False)
    else:
        kinetic_df = pd.DataFrame()
    if results:
        summary = pd.DataFrame(results)
        if not kinetic_df.empty and 'file_name' in kinetic_df.columns:
            # Keep the classical analysis as the primary row and append numerical-fit columns.
            summary = summary.merge(kinetic_df, on='file_name', how='left', suffixes=('', '_kinetic'))
        summary.to_csv(outdir / 'batch_summary.csv', index=False)
    if failures:
        pd.DataFrame(failures).to_csv(outdir / 'analysis_errors.csv', index=False)
    elif (outdir / 'analysis_errors.csv').exists():
        (outdir / 'analysis_errors.csv').unlink()
    if warning_rows:
        pd.DataFrame(warning_rows).to_csv(outdir / 'analysis_warnings.csv', index=False)
    elif (outdir / 'analysis_warnings.csv').exists():
        (outdir / 'analysis_warnings.csv').unlink()
    manifest = {
        'project_format_version': 1,
        'software': 'tpd-spectra', 'software_version': __version__,
        'build': build_identity(),
        'dependencies': {name: importlib.metadata.version(name) for name in ('numpy', 'pandas', 'scipy', 'matplotlib')},
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'input_source': str(sources[0].resolve()) if len(sources) == 1 else [str(p.resolve()) for p in sources],
        'parameters': effective_config,
        'inputs_processed': input_manifest,
        'successful_files': [r.get('file_name') for r in results],
        'failed_files': failures,
        'outputs': sorted(p.name for p in outdir.iterdir() if p.is_file() and p.name != 'analysis_project.json'),
        'notes': [
            'Input SHA-256 hashes support provenance checks; they do not validate instrument calibration.',
            'Scientific validity depends on experiment-specific assumptions and manual review.',
        ],
    }
    (outdir / 'analysis_project.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Completed: {len(results)} succeeded, {len(failures)} failed. Results: {outdir.resolve()}')
    print(f'Diagnostic plots: {diagnostic_dir.resolve()}')
    return 1 if failures and not results else 0

if __name__ == '__main__':
    raise SystemExit(main())
