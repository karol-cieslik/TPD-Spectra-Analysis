"""Explicit screening of a reconstructed constant-ramp temperature coordinate."""
import numpy as np


def checked_linear_ramp(time_min, measured_c, beta_k_s, *, tolerance_K=2.):
    """Return legacy anchored coordinate and diagnostics, or reject mismatch.

    The 2 K default is an engineering screen, not a calibration uncertainty or
    assurance that the constant-ramp model is physically appropriate. Callers
    must justify the selected tolerance for the experiment. Celsius differences
    equal kelvin differences. No measured data are modified.
    """
    time=np.asarray(time_min,dtype=float)
    measured=np.asarray(measured_c,dtype=float)
    if time.ndim!=1 or time.shape!=measured.shape or time.size<3:
        raise ValueError('Ramp check requires matching arrays of at least three points')
    if not np.all(np.isfinite(time)) or not np.all(np.isfinite(measured)) or np.any(np.diff(time)<=0):
        raise ValueError('Ramp check requires finite temperatures and increasing acquisition times')
    if not np.isfinite(beta_k_s) or beta_k_s<=0 or not np.isfinite(tolerance_K) or tolerance_K<=0:
        raise ValueError('Ramp beta and tolerance must be positive and finite')
    coordinate=measured[0]+beta_k_s*(time-time[0])*60.
    differences=measured-coordinate
    metrics={'coordinate':'first cleaned temperature + fitted beta * elapsed acquisition time',
             'max_abs_deviation_K':float(np.max(np.abs(differences))),
             'rms_deviation_K':float(np.sqrt(np.mean(differences**2))),
             'tolerance_K':float(tolerance_K),
             'interpretation':'engineering mismatch screen, not instrument calibration or model validation'}
    if metrics['max_abs_deviation_K']>tolerance_K:
        raise ValueError(f"Measured/reconstructed ramp mismatch {metrics['max_abs_deviation_K']:.6g} K "
                         f"exceeds {tolerance_K:.6g} K. Inspect holds, cooling, nonlinear ramps and temperature units; "
                         'a constant-ramp kinetic fit was not performed.')
    return coordinate,metrics
