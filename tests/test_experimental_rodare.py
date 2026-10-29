"""Data integrity and conversions; rounded peak check is not energy validation."""
from scripts.experimental_rodare_check import evaluate


def test_deposited_experimental_trace_preserves_units_and_rounded_peak():
    result=evaluate()
    assert result['points']==289
    assert result['temperature_conversion_max_error_K']<1e-10
    assert result['time_conversion_max_error_s']<1e-10
    assert result['signal_max_relative_error']<1e-12
    assert result['temperature_points_corrected']==0
    assert abs(result['peak_difference_from_rounded_text_K'])<1.
    assert 'constant-ramp kinetic fit was not performed' in result['ramp_rejection']
