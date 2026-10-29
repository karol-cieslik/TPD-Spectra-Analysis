import numpy as np
import pytest
from tpd_spectra.ramp import checked_linear_ramp


def test_exact_ramp_and_bounded_jitter_retain_acquisition_coordinate():
    time=np.linspace(0,2,121)
    exact=100+time*30
    measured=exact+.05*np.sin(np.arange(121))
    original=measured.copy()
    coord,check=checked_linear_ramp(time,measured,.5,tolerance_K=.1)
    np.testing.assert_allclose(coord,exact)
    np.testing.assert_array_equal(measured,original)
    assert check['max_abs_deviation_K']<.051


@pytest.mark.parametrize('shape',['hold','cooling','nonlinear'])
def test_nonconstant_temperature_program_is_not_silently_reconstructed(shape):
    time=np.linspace(0,2,121)
    measured={'hold':100+np.minimum(time,1)*30,
              'cooling':100-time*30,
              'nonlinear':100+time**2*30}[shape]
    with pytest.raises(ValueError,match='constant-ramp kinetic fit was not performed'):
        checked_linear_ramp(time,measured,.5)


@pytest.mark.parametrize('tolerance',[0,-1,float('nan')])
def test_invalid_tolerance_rejected(tolerance):
    with pytest.raises(ValueError,match='positive and finite'):
        checked_linear_ramp([0,1,2],[100,160,220],1,tolerance_K=tolerance)


def test_cli_records_rejection_without_calling_kinetic_optimizer(tmp_path,monkeypatch):
    import pandas as pd
    from tpd_spectra import cli
    seconds=np.linspace(0,600,121)
    temperature=130+.2*np.minimum(seconds,400)
    path=tmp_path/'hold.csv'
    pd.DataFrame({'Time_ms':seconds*1000,'Temperature':temperature,
                  'Signal':1+np.exp(-((temperature-180)/15)**2)}).to_csv(path,index=False)
    def forbidden(*args,**kwargs):
        raise AssertionError('Optimizer must not run after a rejected ramp')
    monkeypatch.setattr(cli,'fit_polanyi_wigner',forbidden)
    output=tmp_path/'results'
    assert cli.main([str(path),'--output',str(output),'--kinetic-fit',
                     '--leading-edge','130','170','--redhead-region','130','220'])==0
    warnings=(output/'analysis_warnings.csv').read_text()
    assert 'constant-ramp kinetic fit was not performed' in warnings
