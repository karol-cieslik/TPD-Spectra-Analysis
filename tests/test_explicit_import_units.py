"""Known physical ramp must agree across explicit source-unit representations."""
import numpy as np
import pandas as pd
import pytest
from tpd_spectra.analysis import load_spectrum, heating_rate


@pytest.mark.parametrize('time_unit,divisor', [('ms', .001), ('s', 1.), ('min', 60.)])
@pytest.mark.parametrize('temperature_unit,offset', [('degC', 0.), ('K', 273.15)])
def test_explicit_units_recover_same_physical_ramp(tmp_path, time_unit, divisor, temperature_unit, offset):
    seconds = np.arange(61.)
    path = tmp_path / 'ramp.csv'
    pd.DataFrame({'Time': seconds / divisor, 'Temperature': 80. + .5 * seconds + offset,
                  'Signal': 1. + seconds}).to_csv(path, index=False)
    spec = load_spectrum(path, time_unit=time_unit, temperature_unit=temperature_unit)
    np.testing.assert_allclose(spec.time_min, seconds / 60.)
    np.testing.assert_allclose(spec.temperature_c, 80. + .5 * seconds)
    assert heating_rate(spec.time_min, spec.temperature_clean_c, lower_c=80., upper_c=111.)[0] == pytest.approx(.5)
    assert spec.import_report['source_units'] == {'time': time_unit, 'temperature': temperature_unit}


@pytest.mark.parametrize('units', [{'time_unit': 'hours'}, {'temperature_unit': 'F'}])
def test_unknown_source_units_are_rejected_before_parsing(tmp_path, units):
    with pytest.raises(ValueError, match='Supported source units'):
        load_spectrum(tmp_path / 'not-needed.csv', **units)
