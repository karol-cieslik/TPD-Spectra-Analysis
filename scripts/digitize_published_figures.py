"""Digitize three licensed experimental figures from retained image/path inputs.

No synthetic curve generation, kinetic fitting, networking, or gap interpolation.
Raster uncertainty is an engineering pixel/threshold assessment, not a CI.
"""
from pathlib import Path
import csv, gzip, hashlib, io, json, platform
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/digitized'

def linear(values, anchors):
    (a,x),(b,y)=anchors
    return x+(np.asarray(values)-a)*(y-x)/(b-a)

def tick_errors(anchors, checks):
    return [float(linear(v,anchors)-expected) for v,expected in checks]

def write_csv(path,names,values):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(names)
        for row in values:w.writerow(['' if not np.isfinite(v) else f'{v:.10g}' for v in row])

def centerline(image,cfg,variation=0):
    a=np.asarray(image.convert('RGB')).astype(float);R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
    if 'rgb_target' in cfg:
        tol=cfg['rgb_tolerance']+variation
        mask=np.linalg.norm(a-np.array(cfg['rgb_target']),axis=2)<=tol
    else:
        threshold=20+variation
        mask=(R-G>threshold)&(B-G>threshold)&(abs(R-B)<80)&(R>70)&(B>70)
    x0,y0,x1,y1=cfg['roi'];X=np.arange(x0,x1+1);Y=np.full(len(X),np.nan);width=Y.copy()
    for k,x in enumerate(X):
        rows=np.flatnonzero(mask[y0:y1+1,x])+y0
        if len(rows) and rows[-1]-rows[0]<=cfg['max_column_span_px']:
            Y[k]=np.median(rows);width[k]=rows[-1]-rows[0]+1
    return X,Y,width

def raster(case):
    folder=OUT/case;c=json.loads((folder/'provenance.json').read_text());im=Image.open(folder/c['image'])
    X,Y,width=centerline(im,c);T=linear(X,c['x_anchors'])
    if 'y_anchors' in c:
        signal=linear(Y,c['y_anchors']);factor=abs(linear(1,c['y_anchors'])-linear(0,c['y_anchors']))
    else:
        denominator=c['baseline_y_px']-np.nanmin(Y)
        signal=(c['baseline_y_px']-Y)/denominator;factor=1/denominator
    yp_uncertainty=width/2+1
    alt=[centerline(im,c,v)[1] for v in (-6,7)]
    shifts=[abs(y-Y) for y in alt];shift=np.fmax(*shifts)
    uncertainty=np.fmax(yp_uncertainty,shift)*factor
    write_csv(folder/'digitized.csv',['temperature_K','signal_figure_units','signal_pixel_threshold_bound','source_x_px','source_y_px','stroke_span_px'],zip(T,signal,uncertainty,X,Y,width))
    valid=np.isfinite(Y);selected=np.flatnonzero(valid)
    anchors=selected[np.linspace(0,len(selected)-1,15).round().astype(int)]
    fig,axes=plt.subplots(2,1,figsize=(10,6),layout='constrained')
    axes[0].imshow(im);axes[0].plot(X,Y,color='#00a6ce',lw=.7)
    axes[0].scatter(X[anchors],Y[anchors],s=30,facecolors='none',edgecolors='red',lw=.7)
    x0,y0,x1,y1=c['roi'];axes[0].set(xlim=(x0-15,x1+15),ylim=(y1+20,y0-20),title='Source pixels + extracted centerline; 15 visual check markers')
    axes[1].plot(T,signal,lw=1,color='#713e80');axes[1].fill_between(T,signal-uncertainty,signal+uncertainty,alpha=.2,color='#713e80')
    axes[1].set(xlabel='Temperature (K)',ylabel='Figure signal units',title=c['trace'])
    fig.savefig(folder/'extraction_check.png',dpi=140);plt.close(fig)
    qc=dict(present_points=int(valid.sum()),missing_columns=int((~valid).sum()),
        full_columns=len(X),peak_temperature_K=float(T[np.nanargmax(signal)]),peak_signal=float(np.nanmax(signal)),
        x_check_tick_errors_K=tick_errors(c['x_anchors'],c['x_check_ticks']),
        temperature_pixel_halfwidth_K=float(abs(linear(.5,c['x_anchors'])-linear(0,c['x_anchors']))),
        additional_axis_placement_allowance_K=float(abs(linear(1.5,c['x_anchors'])-linear(0,c['x_anchors']))),
        maximum_signal_pixel_threshold_bound=float(np.nanmax(uncertainty)),
        source_missing='Blank fields mark invisible/ambiguous source columns; no interpolation or baseline filling',
        uncertainty_interpretation='Stroke half-width plus one pixel, or threshold-center shift, whichever larger; add axis placement uncertainty separately. Not statistical or physical uncertainty.',
        visual_check_markers=[dict(x_px=int(X[i]),y_px=float(Y[i]),temperature_K=float(T[i])) for i in anchors],
        independent_numeric_reference_available=False)
    if 'y_anchors' in c:qc['y_check_tick_errors']=tick_errors(c['y_anchors'],c['y_check_ticks'])
    (folder/'quality.json').write_text(json.dumps(qc,indent=2,allow_nan=False)+'\n')
    return dict(case=case,doi=c['paper_doi'],traces=1,points=int(valid.sum()),peak_K=qc['peak_temperature_K'])

def vector():
    folder=OUT/'ice_2024';c=json.loads((folder/'provenance.json').read_text());paths=json.loads((folder/'source_paths.json').read_text());summaries={}
    context=Image.open(folder/'source_context.png');fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    for index,species in enumerate(['CO','Ar']):
        cfg=c['traces'][species];path=paths[species];a=np.array(path['points_pdf']);T=linear(a[:,0],cfg['x_anchors']);S=linear(a[:,1],cfg['y_anchors'])
        write_csv(folder/(species+'_digitized.csv'),['temperature_K','desorption_rate_ML_per_K','source_x_pdf_pt','source_y_pdf_pt'],zip(T,S,a[:,0],a[:,1]))
        rawpath=ROOT/'validation/experimental/ice_2024/raw'/('2_CO_pure.csv.gz' if species=='CO' else '4_Ar_pure.csv.gz')
        raw=np.loadtxt(io.BytesIO(gzip.decompress(rawpath.read_bytes())),delimiter=';',comments='#')
        j=int(np.argmax(S));k=int(np.argmax(raw[:,1]));m=(T>=22)&(T<=60);ref=raw[(raw[:,0]>=22)&(raw[:,0]<=61)]
        # No source modification: this QC interval has strictly increasing raw T.
        assert np.all(np.diff(ref[:,0])>0)
        error=S[m]-np.interp(T[m],ref[:,0],ref[:,1]);nrmse=float(np.sqrt(np.mean(error**2))/np.ptp(ref[:,1]))
        qc=dict(points=len(T),peak_temperature_K=float(T[j]),peak_signal_ML_per_K=float(S[j]),
            source_CSV_peak_temperature_K=float(raw[k,0]),source_CSV_peak_signal_ML_per_K=float(raw[k,1]),
            peak_difference_K=float(T[j]-raw[k,0]),peak_height_ratio=float(S[j]/raw[k,1]),
            NRMSE_against_CSV_22_60K=nrmse,reference_range='Raw CSV interpolation on a strictly increasing 22–61 K subset; compare digitized 22–60 K values only.',
            x_tick_errors_K=tick_errors(cfg['x_anchors'],cfg['x_check_ticks']),
            y_tick_errors_ML_per_K=tick_errors(cfg['y_anchors'],cfg['y_check_ticks']),
            source_label='PDF vector vertices, not instrument samples',
            axis_reading_allowance_pdf_pt=.25,
            axis_reading_allowance_K=float(abs(linear(.25,cfg['x_anchors'])-linear(0,cfg['x_anchors']))),
            correspondence='Substantial unresolved source-to-figure discrepancy' if species=='CO' else 'Close figure-to-deposited-data correspondence in tested interval')
        summaries[species]=qc
        ax=axes[0,index];ax.imshow(context);ax.plot((a[:,0]-33)*2,(a[:,1]-80)*2,lw=1,color='#00a6ce')
        ax.set(xlim=((min(a[:,0])-5-33)*2,(max(a[:,0])+5-33)*2),ylim=((max(a[:,1])+5-80)*2,(min(a[:,1])-5-80)*2),title=species+': vector coordinates on source pixels')
        ax=axes[1,index];ax.plot(raw[:,0],raw[:,1],label='Deposited CSV',lw=1);ax.plot(T,S,label='Published figure',lw=1)
        ax.set(xlim=(20,60),xlabel='Temperature (K)',ylabel='Signal (ML/K)',title=species+': independent source comparison');ax.legend()
    fig.savefig(folder/'extraction_check.png',dpi=140);plt.close(fig)
    (folder/'quality.json').write_text(json.dumps(summaries,indent=2,allow_nan=False)+'\n')
    return dict(case='ice_2024',doi=c['paper_doi'],traces=2,points=sum(x['points'] for x in summaries.values()))

def main():
    rows=[raster('water_2018'),raster('mesh_2025'),vector()]
    report=dict(papers=3,traces=4,cases=rows,kinetic_fits_performed=False,
        software=dict(python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'extraction_summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
