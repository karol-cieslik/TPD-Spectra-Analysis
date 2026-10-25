"""Conservative numerical identifiability diagnostics for least-squares fits.

These diagnostics are not parameter uncertainty estimates. Jacobian columns
correspond to optimizer parameter coordinates, not physical SI units.
"""
from __future__ import annotations

import numpy as np


def jacobian_diagnostics(jacobian, parameters, lower_bounds, upper_bounds,
                         *, relative_bound_tolerance=1e-6):
    """Summarize local rank and active bounds without reporting false intervals.

    Rank uses NumPy's SVD threshold (max(m,n)*eps*largest singular value).
    Bounds use a fraction of their permitted parameter range. A full-rank
    Jacobian does *not* prove structural or practical identifiability.
    """
    jac = np.asarray(jacobian, dtype=float)
    p = np.asarray(parameters, dtype=float)
    lo = np.asarray(lower_bounds, dtype=float)
    hi = np.asarray(upper_bounds, dtype=float)
    if jac.ndim != 2 or jac.shape[1] != p.size or p.ndim != 1:
        raise ValueError("Jacobian and parameter dimensions are inconsistent")
    if lo.shape != p.shape or hi.shape != p.shape or np.any(lo >= hi):
        raise ValueError("parameter bounds are invalid")
    if not (np.all(np.isfinite(jac)) and np.all(np.isfinite(p))
            and np.all(np.isfinite(lo)) and np.all(np.isfinite(hi))):
        raise ValueError("diagnostics require finite inputs")
    if not np.isfinite(relative_bound_tolerance) or relative_bound_tolerance < 0:
        raise ValueError("relative_bound_tolerance must be finite and nonnegative")
    s = np.linalg.svd(jac, compute_uv=False)
    tolerance = max(jac.shape) * np.finfo(float).eps * s[0] if s.size else 0.
    rank = int(np.count_nonzero(s > tolerance))
    condition = float(s[0] / s[-1]) if s.size and s[-1] > 0 else float("inf")
    width = hi - lo
    near_lower = (p - lo) <= relative_bound_tolerance * width
    near_upper = (hi - p) <= relative_bound_tolerance * width
    warnings = []
    if rank < p.size:
        warnings.append("Local residual Jacobian is rank deficient; parameters are not locally identifiable.")
    if np.any(near_lower | near_upper):
        warnings.append("One or more parameters lie near optimizer bounds; local intervals may be invalid.")
    if not np.isfinite(condition) or condition > 1e8:
        warnings.append("Residual Jacobian is poorly conditioned; parameter estimates may be strongly correlated.")
    return {
        "jacobian_rank": rank,
        "n_parameters": int(p.size),
        "jacobian_condition_number": condition,
        "near_lower_bound_indices": np.flatnonzero(near_lower).tolist(),
        "near_upper_bound_indices": np.flatnonzero(near_upper).tolist(),
        "warnings": warnings,
    }
