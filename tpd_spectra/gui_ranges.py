"""Pure helpers for interactive temperature-window selection."""
from __future__ import annotations

import math


def validate_temperature_window(lower, upper, *, minimum=0.0, maximum=700.0):
    """Return finite ordered endpoints; reject out-of-range or degenerate spans."""
    lo, hi = float(lower), float(upper)
    if not all(map(math.isfinite, (lo, hi))):
        raise ValueError("Temperature window endpoints must be finite.")
    if not minimum <= lo < hi <= maximum:
        raise ValueError(f"Choose an increasing interval between {minimum:g} and {maximum:g} °C.")
    return lo, hi


def window_from_drag(start, end, *, minimum=0.0, maximum=700.0):
    """Sort drag endpoints and clamp them to the selectable temperature range."""
    a, b = float(start), float(end)
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError("Drag endpoints must be finite.")
    lo, hi = sorted((max(minimum, min(maximum, a)), max(minimum, min(maximum, b))))
    return validate_temperature_window(lo, hi, minimum=minimum, maximum=maximum)
