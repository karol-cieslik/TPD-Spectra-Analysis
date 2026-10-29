"""Read all original headers and audit mapping prerequisites, without refitting."""
from pathlib import Path
import csv, hashlib, io, json, re, zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/experimental/ptcda_au111'

def main():
    rows=[]
    with zipfile.ZipFile(OUT/'source.zip') as z:
        for item in z.infolist():
            if item.is_dir(): continue
            raw=z.read(item); lines=raw.decode('latin1').splitlines()
            headers=[i for i,s in enumerate(lines) if '_time' in s.lower() and '_t1' in s.lower()]
            if len(headers)!=1:raise ValueError(f'Ambiguous channel header: {item.filename}')
            h=headers[0]; cols=lines[h].split('\t')
            a=np.loadtxt(io.StringIO('\n'.join(lines[h+1:])))
            # The historical fixed skiprows=3 drops two startup samples when the
            # header is line 1. Verify that its frozen fit interval is unchanged.
            legacy=np.loadtxt(io.BytesIO(raw),skiprows=3)
            current_window=a[(a[:,1]>=550)&(a[:,1]<=740)]
            prior_window=legacy[(legacy[:,1]>=550)&(legacy[:,1]<=740)]
            same=np.array_equal(current_window,prior_window)
            rows.append(dict(file=Path(item.filename).name,sha256=hashlib.sha256(raw).hexdigest(),
                creation_header=' | '.join(lines[:h]),channel_header_line=h+1,
                numeric_rows=len(a),numeric_columns=a.shape[1],channels=' | '.join(cols),
                detector_scale_exponents=' | '.join(re.findall(r'E-\d+',lines[h])),
                coverage_ML='unknown',published_curve_label='unknown',
                saturation_reference='unverified',window_identical_to_retained_fits=same))
    with (OUT/'metadata_inventory.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result=dict(files=len(rows),explicit_coverage_assignments=0,
        explicit_published_curve_assignments=0,verified_saturation_references=0,
        header_line_counts={str(i):sum(r['channel_header_line']==i for r in rows) for i in sorted({r['channel_header_line'] for r in rows})},
        detector_scales=sorted({s for r in rows for s in r['detector_scale_exponents'].split(' | ') if s}),
        all_frozen_windows_identical=all(r['window_identical_to_retained_fits'] for r in rows),
        status='blocked_by_missing_trace_reference_and_calibration',
        interpretation='No coverage was assigned from area, filename order, peak position or date. Complete analysis was not run. Retained 438 fits are unchanged.')
    (OUT/'metadata_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
