"""Plots and exports from a submitted simultaneous kinetic-fit snapshot."""
import csv
import json
from pathlib import Path
from matplotlib.figure import Figure
from .workflow_analysis import plot_observations, serial
from .identity import build_identity


def draw_components(axis, residual_axis, fit):
    t = fit['temperature_c']
    plot_observations(axis,t,fit['observed'],label='Submitted observations (full spectrum)')
    colors = ('#2563eb','#059669','#9333ea')
    for index,(component,curve) in enumerate(zip(fit['components'],fit['component_predictions'])):
        axis.plot(t,curve,color=colors[index],linestyle=('--','-.',':')[index],linewidth=1.6,zorder=3,
                  label=f"{component['label']} (n={component['order']:g})")
    axis.plot(t,fit['baseline_prediction'],color='#a16207',linestyle=':',label='Shared baseline')
    axis.plot(t,fit['prediction'],color='#d35400',linewidth=1.9,label='Combined kinetic fit')
    residual_axis.plot(t,fit['residuals'],color='#475569',linewidth=.8,label='Observed − combined fit')
    residual_axis.axhline(0,color='gray',linewidth=.7)
    axis.set(ylabel='Signal (instrument units)')
    residual_axis.set(xlabel='Temperature (°C)',ylabel='Residual')
    quality=fit.get('diagnostics',{}).get('fit_quality')
    if quality:
        titles={'baseline_only':'UNUSABLE: baseline-only fit — main signal unexplained',
                'poor_fit':'POOR FIT: substantial residual error — review assumptions',
                'collapsed_components':'COLLAPSED COMPONENT: requested decomposition unsupported',
                'review_required':'Joint fit converged — review residuals and assumptions'}
        axis.set_title(titles[quality],fontsize=10,color='#b91c1c' if quality!='review_required' else '#334155')
    residual_axis.legend(fontsize=7,loc='upper right')
    axis.legend(fontsize=7,ncol=2)


def export_components(record, directory):
    """Export fixed assumptions, fitted parameters and individual physical curves."""
    destination=Path(directory)
    destination.mkdir(parents=True,exist_ok=False)
    fit=record['fit']
    payload=serial(dict(software=build_identity(),**record))
    (destination/'components.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    with (destination/'component_parameters.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(fit['components'][0]))
        writer.writeheader()
        for component in fit['components']:
            writer.writerow({key:json.dumps(value,ensure_ascii=False) if isinstance(value,(list,dict)) else value
                             for key,value in component.items()})
    with (destination/'component_curves.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.writer(handle)
        writer.writerow(['temperature_c','observed_signal','combined_fit','shared_baseline','observed_minus_combined']+
                        [f"component_{i+1}: {c['label']}" for i,c in enumerate(fit['components'])])
        writer.writerows(zip(fit['temperature_c'],fit['observed'],fit['prediction'],fit['baseline_prediction'],
                             fit['residuals'],*fit['component_predictions']))
    figure=Figure(figsize=(9,7),layout='constrained')
    draw_components(figure.add_subplot(211),figure.add_subplot(212),fit)
    for extension in ('png','svg'):
        figure.savefig(destination/f'components.{extension}',dpi=160)
    (destination/'README.txt').write_text(
        'Simultaneous independent Polanyi-Wigner components; full submitted spectrum.\n'
        'Orders, prefactors and initial coverages are fixed hypotheses, not estimates.\n'
        'Each component curve includes its fitted detector scale; baseline is separate.\n'
        'Residual = observed - (sum of component curves + shared baseline).\n'
        'Inspect components.json for source hash, submitted settings, model comparisons, diagnostics and warnings.\n'
        +fit['uncertainty_note']+'\n'+'\n'.join(fit['warnings'])+'\n',encoding='utf-8')
    return destination
