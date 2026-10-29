"""Reproduce the separately declared log-regression diagnostic only."""
from pathlib import Path
import gzip,io,json,sys
from dataclasses import asdict
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tpd_spectra.analysis import leading_edge_fit,K_B_EV
OUT=Path(__file__).resolve().parents[1]/'validation/experimental/ice_2024'

def main():
    protocol=json.loads((OUT/'log_diagnostic_protocol.json').read_text())
    a=np.loadtxt(io.BytesIO(gzip.decompress((OUT/'raw/2_CO_pure.csv.gz').read_bytes())),delimiter=';',comments='#')
    lo,hi=protocol['interval_K'];T,y=a[(a[:,0]>=lo)&(a[:,0]<=hi)].T
    fit=leading_edge_fit(T-273.15,y,.2,lo-273.15,hi-273.15)
    result=json.loads(json.dumps(asdict(fit)),parse_constant=lambda _:None)
    direct=float(-np.polyfit(1/T[y>0],np.log(y[y>0]),1)[0])
    v=dict(protocol=protocol,result=result,energy_K=fit.energy_ev/K_B_EV,
        selected_input_points=len(y),positive_signal_points=int(np.sum(y>0)),
        independent_numpy_OLS_energy_K=direct,absolute_OLS_difference_K=abs(fit.energy_ev/K_B_EV-direct))
    (OUT/'log_diagnostic.json').write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
