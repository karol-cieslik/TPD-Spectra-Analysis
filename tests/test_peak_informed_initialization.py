"""Independent recovery regressions for signal-suppressed local minima."""
import numpy as np
import pytest
from scripts.joss_assessment import reference
from tpd_spectra.kinetics_explorer import compare_desorption_orders


@pytest.mark.parametrize('order,name,energy,nu',[(1.,'first',1.1,1e12),(2.,'second',1.2,1e13),(1.5,'fractional',1.05,1e11)])
def test_default_starts_do_not_abandon_independent_peak(order,name,energy,nu):
    temp=np.linspace(80.,340.,81)
    _,rate=reference(temp,1.,energy,nu,order)
    signal=2+1e4*rate+np.random.default_rng(123).normal(0,.015*1e4*rate.max(),len(temp))
    candidate=compare_desorption_orders(temp,signal,1.,orders=(name,),max_nfev=150,multistart=True)[0]
    assert candidate.error is None
    assert candidate.fit.normalized_rmse<.03
    assert candidate.fit.activation_energy_eV==pytest.approx(energy,rel=.05)
