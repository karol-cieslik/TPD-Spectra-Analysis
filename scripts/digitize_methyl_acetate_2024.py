"""Extract labelled spectrum and published transformed plot; no kinetic fits.

Source and derived data: Fulker & Brown 2024, CC-BY-3.0.
"""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/experimental/methyl_acetate_2024'


def write(path, names, rows):
    with path.open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(names)
        for row in rows:w.writerow(['' if not np.isfinite(v) else f'{v:.12g}' for v in row])


def spectrum(im, tolerance):
    a=np.asarray(im.convert('RGB')).astype(float)
    # Actual 50 Lm legend colour. Adjacent 40 Lm is much redder.
    R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
    # R-G separates royal blue (50 Lm) from pure blue (20 Lm),
    # including their white-antialiased pixels; the upper cut excludes 40 Lm.
    mask=(B>170)&(R<150)&(G<tolerance)&(B-R>100)&(R-G>25)&(R-G<95)
    x=np.arange(285,498);y=np.full(x.size,np.nan);span=y.copy()
    for i,col in enumerate(x):
        rows=np.flatnonzero(mask[145:349,col])+145
        if rows.size and np.ptp(rows)<=12:
            y[i]=np.median(rows);span[i]=np.ptp(rows)+1
    return x,y,span


def main():
    cfg=json.loads((OUT/'provenance.json').read_text())
    for name,info in cfg['sources'].items():assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==info['sha256']
    im=Image.open(OUT/'source_figure4.jpg')
    x,y,span=spectrum(im,85)
    alternates=[spectrum(im,t)[1] for t in (60,110)]
    variation=np.fmax(abs(alternates[0]-y),abs(alternates[1]-y))
    height=350-np.nanmin(y)
    signal=(350-y)/height
    bound=np.fmax(span/2+1,variation)/height
    T=110+(x-282)*40/217
    write(OUT/'spectrum.csv',['temperature_K','signal_normalized_graph_height','signal_pixel_threshold_bound','source_x_px','source_y_px','stroke_span_px'],zip(T,signal,bound,x,y,span))
    # Black open circles in transformed plot. Exclude legend (above y=100),
    # bottom annotation (below y=365) and panel frame; retain gaps.
    trans=Image.open(OUT/'source_figure6.jpg')
    a=np.asarray(trans.convert('RGB')).astype(float)
    mask=(a.max(2)<140)&(np.ptp(a,axis=2)<35)
    tx=np.arange(566,737);ty=np.full(tx.size,np.nan);ts=ty.copy()
    for i,col in enumerate(tx):
        rows=np.flatnonzero(mask[100:366,col])+100
        # Visual diagonal region follows the symbols, not distant error-bar caps.
        # Endpoints read from pixels before fitting; not a fitted energy constraint.
        expected_y=86+1.4*(col-566)
        rows=rows[abs(rows-expected_y)<=12]
        # Long error-bar columns/dotted fit are not accepted as circle centers.
        if rows.size and np.ptp(rows)<=10:
            ty[i]=np.median(rows);ts[i]=np.ptp(rows)+1
    invT=8.0+(tx-604)*.3/127
    z=7+(414-ty)*3/344
    write(OUT/'published_transformed.csv',['inverse_temperature_1000_per_K','ln_I_minus_n_ln_theta_rel','source_x_px','source_y_px','black_span_px'],zip(invT,z,tx,ty,ts))
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    axes[0,0].imshow(im);axes[0,0].plot(x,y,color='#00aa70',lw=.8)
    axes[0,0].set(xlim=(275,505),ylim=(355,140),title='Fig 4B: selected 50 Lm royal-blue trace')
    axes[1,0].plot(T,signal,'.-',ms=2,lw=.7);axes[1,0].set(xlabel='Temperature (K)',ylabel='Normalized graphical height')
    axes[0,1].imshow(trans);axes[0,1].plot(tx,ty,color='#00aa70',lw=.8)
    axes[0,1].set(xlim=(558,744),ylim=(370,90),title='Fig 6C: black-symbol centerline; not raw intensity')
    axes[1,1].plot(invT,z,'.',ms=2);axes[1,1].set(xlabel='1000/T (K⁻¹)',ylabel='ln I − n ln relative coverage')
    fig.savefig(OUT/'extraction_check.png',dpi=150);plt.close(fig)
    quality=dict(spectrum=dict(total_columns=len(x),recovered=int(np.isfinite(y).sum()),missing=int(np.isnan(y).sum()),peak_K=float(T[np.nanargmax(signal)]),normalization_height_px=float(height),pixel_halfwidth_K=20/217,axis_placement_allowance_K=60/217,maximum_signal_bound=float(np.nanmax(bound)),unused_x_tick_130_error_K=110+(391-282)*40/217-130,unused_x_tick_140_error_K=110+(445-282)*40/217-140),
                 transformed=dict(total_columns=len(tx),recovered=int(np.isfinite(ty).sum()),missing=int(np.isnan(ty).sum()),axis_x_allowance_1000_per_K=1.5*.3/127,axis_y_allowance_log_units=1.5*3/344,unused_x_tick_8_1_error=8+(646-604)*.3/127-8.1,unused_y_tick_9_error=7+(414-185)*3/344-9),
                 interpretation='Columns, not independent instrument samples; engineering pixel bounds, no statistical CI; no interpolation. Fig6C input already includes authors coverage correction and may include dotted fitted line fragments.',
                 baseline='Graphical lower edge is the display origin, not a measured background.')
    (OUT/'extraction_quality.json').write_text(json.dumps(quality,indent=2)+'\n')
    print(json.dumps(quality,indent=2))


if __name__=='__main__':main()
