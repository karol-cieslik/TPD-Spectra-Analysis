"""Selected-run reporting with bounded text pages and vector scientific plots."""
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import textwrap
from importlib.metadata import version
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
from . import __version__
from .workflow_analysis import draw_result, processed_signal, serial, plot_observations


def dependencies():
    return {name:version(name) for name in ('numpy','scipy','pandas','matplotlib')}


class ReportPages:
    def __init__(self,pdf):
        self.pdf = pdf
        self.number = 0

    def page(self,fig,title):
        self.number += 1
        # Fixed plot rectangles leave room for a wrapped title and footer.
        heading = textwrap.wrap(title,62)
        if len(heading)>3:
            heading=heading[:3]
            heading[-1]+='…'
        fig.suptitle('\n'.join(heading),x=.08,y=.96,ha='left',fontsize=12,color='#15304b')
        fig.text(.08,.025,'TPD Spectra Studio | Karol Cieślik',fontsize=8,color='#526170')
        fig.text(.93,.025,str(self.number),ha='right',fontsize=8)
        self.pdf.savefig(fig)

    def text(self,title,text):
        lines = []
        for line in text.splitlines():
            lines.extend(textwrap.wrap(line, width=90,replace_whitespace=False,drop_whitespace=False) or [''])
        for start in range(0,max(1,len(lines)),48):
            fig = Figure(figsize=(8.27,11.69))
            fig.text(.08,.875,'\n'.join(lines[start:start+48]),va='top',fontsize=9,family='DejaVu Sans Mono',linespacing=1.5)
            self.page(fig,title + (' (continued)' if start else ''))


def export_report(project,run_ids,directory):
    if not run_ids or any(i not in project.runs for i in run_ids):
        raise ValueError('Select at least one saved analysis run.')
    if len(run_ids) != len(set(run_ids)):
        raise ValueError('Duplicate report selection')
    runs = [project.runs[i] for i in run_ids]
    directory = Path(directory)
    directory.mkdir(parents=True,exist_ok=False)
    provenance = dict(schema_version=1,software_version=__version__,exported_utc=datetime.now(timezone.utc).isoformat(),
                      export_dependencies=dependencies(),runs=runs,modeling={},source_warnings=getattr(project,'source_warnings',[]))
    summaries = []
    with PdfPages(directory/'report.pdf',metadata={'Title':'TPD Spectra Studio - selected analysis report','Author':'Karol Cieślik'}) as pdf:
        pages = ReportPages(pdf)
        pages.text('Selected analysis report',f'TPD Spectra Studio {__version__}\nCreated: {provenance["exported_utc"]}\n'
            f'Author of software: Karol Cieślik\nhttps://github.com/karol-cieslik/TPD-Spectra-Analysis\n\n'
            f'{len(runs)} explicitly selected saved runs. Original run settings and intervals are retained.\n\n'
            'Acquisition metadata, detector calibration, specimen identity and experimental provenance: not available unless supplied in the original source.\n'
            'Synthetic examples are simulated physical-model data, not experimental measurements.\n\n'
            'Leading-edge intervals quantify regression scatter only. Redhead assumes first-order kinetics and a supplied prefactor. '
            'Kinetic fits and model rankings do not prove a mechanism. Monte Carlo ranges are conditional on the reference and iid Gaussian noise assumptions; coverage has not been validated.\n\n'
            'Runs selected:\n' + '\n'.join(f'{r["label"]} | {r["snapshot"]["method"]} | {r["created_utc"]}' for r in runs)
            + '\n\nSource checks:\n' + '\n'.join(provenance['source_warnings']))
        for index,run in enumerate(runs,1):
            snap = run['snapshot']
            dataset = project.datasets[snap['dataset_id']]
            title = f'{index}. {run["label"]}'
            fig = Figure(figsize=(8.27,11.69))
            ax = fig.add_axes((.12,.18,.80,.66))
            ax.plot(dataset.spectrum.temperature_clean_c,dataset.spectrum.signal,label='Imported raw signal',alpha=.65)
            ax.plot(dataset.spectrum.temperature_clean_c,processed_signal(dataset,snap['processing']),label='Recorded analysis recipe')
            ax.axvspan(*snap['region'],alpha=.12,color='teal',label=snap['peak'])
            ax.set(xlabel='Cleaned temperature (°C)',ylabel='Signal (instrument units)')
            ax.legend(fontsize=9)
            pages.page(fig,title+' - spectrum and selected region')
            fig = Figure(figsize=(8.27,11.69))
            draw_result(fig,run)
            fig.subplots_adjust(left=.13,right=.95,top=.84,bottom=.12,hspace=.4)
            values=run['values']
            energy=values.get('energy_ev',values.get('activation_energy_eV'))
            if energy is not None:
                fig.text(.13,.075,f'Energy estimate: {energy:.6g} eV | Method: {snap["method"]}',fontsize=10,color='#15304b')
            pages.page(fig,title+' - '+snap['method']+' ('+run['status']+')')
            for extension in ('png','svg'):
                fig.savefig(directory/f'run-{index:03d}.{extension}',dpi=160)
            plot = run['plots']
            with (directory/f'run-{index:03d}-curve.csv').open('w',newline='',encoding='utf-8') as handle:
                writer=csv.writer(handle)
                writer.writerow([plot['x_label'],plot['y_label'],'prediction','residual'])
                predicted = plot.get('predicted')
                for j,(x,y) in enumerate(zip(plot['x'],plot['observed'])):
                    writer.writerow([x,y,predicted[j] if predicted else '',y-predicted[j] if predicted else ''])
            detail = dict(label=run['label'],status=run['status'],created_utc=run['created_utc'],software_version=run['version'],
                          calculation_dependencies=run.get('dependencies','not available'),values=run['values'],warnings=run['warnings'],
                          provenance=snap,import_report={k:(f'{len(v)} records; complete list in results.json' if isinstance(v,list) and len(v)>20 else v) for k,v in run.get('import_report',{}).items()})
            pages.text(title+' - parameters, assumptions and provenance',json.dumps(detail,indent=2,ensure_ascii=False,allow_nan=False))
            for parameter,value in run['values'].items():
                summaries.append([run['id'],run['label'],snap['method'],parameter,json.dumps(value,ensure_ascii=False)])
            key = f"{snap['dataset_id']}/{snap['region_id']}"
            if key in project.modeling and key not in provenance['modeling']:
                session = project.modeling[key]
                provenance['modeling'][key] = session
                if 'comparison' in session:
                    c = session['comparison']
                    fig=Figure(figsize=(8.27,11.69))
                    ax=fig.add_subplot(211)
                    res=fig.add_subplot(212)
                    plot_observations(ax,c['temperature'],c['signal'],label='Comparison input')
                    for model_index,model in enumerate(c['candidates']):
                        if model['prediction'] is not None and not model['error']:
                            ax.plot(c['temperature'],model['prediction'],label=model['name'],
                                    linestyle=('-', '--', '-.', ':')[model_index%4],linewidth=1.5)
                            res.plot(c['temperature'],np.asarray(c['signal'])-np.asarray(model['prediction']),label=model['name'])
                    ax.set(ylabel='Signal (instrument units)')
                    ax.legend(fontsize=8)
                    res.set(xlabel='Temperature (°C)',ylabel='Residual')
                    res.axhline(0,color='gray',linewidth=.7)
                    fig.subplots_adjust(top=.84,bottom=.12,hspace=.35)
                    pages.page(fig,title+' - associated exploration (independent settings)')
                    summary = dict(snapshot=c['snapshot'],candidates=[{k:v for k,v in m.items() if k!='prediction'} for m in c['candidates']])
                    if 'monte_carlo' in session:
                        summary['monte_carlo'] = {k:v for k,v in session['monte_carlo'].items()}
                        summary['monte_carlo'] = json.loads(json.dumps(summary['monte_carlo']))
                        summary['monte_carlo']['result'].pop('replicate_records',None)
                    pages.text(title+' - exploration diagnostics (not a final-method result)',json.dumps(summary,indent=2,ensure_ascii=False))
        pages.text('Reproducibility appendix',json.dumps({k:v for k,v in provenance.items() if k not in ('runs','modeling')},indent=2)
                   +'\nFull run curves and MC replicate records are included in results.json. Source hashes and complete effective settings are listed with each run.')
    with (directory/'parameters.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.writer(handle)
        writer.writerow(['run_id','label','method','parameter_with_units','value'])
        writer.writerows(summaries)
    (directory/'results.json').write_text(json.dumps(serial(provenance),indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    (directory/'COMPLETE.txt').write_text(f'{len(runs)} selected runs exported successfully.\n',encoding='utf-8')
    return directory
