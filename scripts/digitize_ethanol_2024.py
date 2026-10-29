"""Extract black experimental marks in Perrero et al. Fig. 7 (not red fit).

Figure and extracted data retain CC-BY-NC-3.0; see case attribution.
Coordinates are raster columns, not independent instrument measurements.
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation/experimental/ethanol_2024'


def extract(im, threshold):
    rgb = np.asarray(im.convert('RGB')).astype(float)
    mask = (rgb.max(2) < threshold) & (np.ptp(rgb, axis=2) < 30)
    x = np.arange(420, 744)
    y = np.full(x.size, np.nan)
    span = y.copy()
    for i, column in enumerate(x):
        ys = np.flatnonzero(mask[9:222, column]) + 9
        # Legend is entirely above y=63 and left of x=548.
        if column < 550:
            ys = ys[ys >= 65]
        if ys.size and np.ptp(ys) <= 14:
            y[i] = np.median(ys)
            span[i] = np.ptp(ys) + 1
    return x, y, span


def main():
    cfg = json.loads((OUT / 'provenance.json').read_text())
    source = OUT / 'source_figure7.jpg'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == cfg['source_sha256']
    im = Image.open(source)
    x, y, span = extract(im, 110)
    alternatives = [extract(im, threshold)[1] for threshold in (85, 135)]
    variation = np.fmax(abs(alternatives[0]-y), abs(alternatives[1]-y))
    bound_y = np.fmax(span / 2 + 1, variation)
    temperature = 90 + (x - 416.5) * 80 / 331
    signal = (225 - y) * .018 / 220
    bound = bound_y * .018 / 220
    with (OUT / 'digitized.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['temperature_K', 'desorption_rate_ML_s', 'signal_pixel_threshold_bound', 'source_x_px', 'source_y_px', 'black_mark_span_px'])
        for row in zip(temperature, signal, bound, x, y, span):
            writer.writerow(['' if not np.isfinite(v) else f'{v:.12g}' for v in row])
    selected = np.flatnonzero(np.isfinite(y))
    markers = selected[np.linspace(0, selected.size-1, 18).round().astype(int)]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), layout='constrained')
    axes[0].imshow(im)
    axes[0].plot(x, y, lw=.6, color='#00a6ce')
    axes[0].scatter(x[markers], y[markers], s=28, facecolors='none', edgecolors='#00a6ce')
    axes[0].set(xlim=(410,755), ylim=(230,0), title='Black experimental marks + extracted centerline (cyan)')
    axes[1].plot(temperature, signal, lw=1, color='black')
    axes[1].fill_between(temperature, signal-bound, signal+bound, color='gray', alpha=.4)
    axes[1].set(xlabel='Temperature (K)', ylabel='Figure rate (ML/s)', title='No red simulation pixels or gap interpolation')
    fig.savefig(OUT / 'extraction_check.png', dpi=140)
    plt.close(fig)
    quality = dict(columns=len(x), recovered_columns=len(selected), missing_columns=int(np.isnan(y).sum()),
                   peak_temperature_K=float(temperature[np.nanargmax(signal)]),
                   peak_rate_ML_s=float(np.nanmax(signal)),
                   temperature_pixel_halfwidth_K=40/331,
                   additional_axis_placement_allowance_K=120/331,
                   signal_axis_placement_allowance_ML_s=1.5*.018/220,
                   maximum_signal_pixel_threshold_bound=float(np.nanmax(bound)),
                   unused_tick_checks=dict(x_110_K_error=90+(499-416.5)*80/331-110,
                                           x_150_K_error=90+(665-416.5)*80/331-150,
                                           y_001_ML_s_error=(225-103)*.018/220-.010),
                   limitation='Raster centerlines of black symbols, not recovered instrument samples. Pixel bounds are engineering allowances, not confidence intervals.',
                   visual_markers=[dict(x=float(x[i]), y=float(y[i])) for i in markers])
    (OUT / 'extraction_quality.json').write_text(json.dumps(quality, indent=2) + '\n')
    print(json.dumps(quality, indent=2))


if __name__ == '__main__':
    main()
