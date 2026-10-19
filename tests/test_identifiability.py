import numpy as np
import pytest

from tpd_spectra.identifiability import jacobian_diagnostics


def test_full_rank_interior_fit_has_no_warning():
    result = jacobian_diagnostics(np.eye(3), [0.5, 0.5, 0.5], [0, 0, 0], [1, 1, 1])
    assert result["jacobian_rank"] == 3
    assert result["n_parameters"] == 3
    assert result["warnings"] == []
    assert result["near_lower_bound_indices"] == []


def test_rank_deficiency_and_bounds_reported():
    result = jacobian_diagnostics([[1, 1], [2, 2], [3, 3]],
                                  [0, 1], [0, 0], [1, 1])
    assert result["jacobian_rank"] == 1
    assert result["near_lower_bound_indices"] == [0]
    assert result["near_upper_bound_indices"] == [1]
    assert len(result["warnings"]) >= 2


def test_near_singular_full_rank_warns_without_claiming_confidence_interval():
    result = jacobian_diagnostics(np.diag([1.0, 1e-10]),
                                  [0.5, 0.5], [0, 0], [1, 1])
    assert result["jacobian_rank"] == 2
    assert any("poorly conditioned" in warning for warning in result["warnings"])
    assert "confidence_interval" not in result


def test_invalid_dimensions_and_nonfinite_inputs_rejected():
    with pytest.raises(ValueError):
        jacobian_diagnostics(np.eye(3), [0, 1], [0, 0], [1, 1])
    with pytest.raises(ValueError):
        jacobian_diagnostics([[np.nan]], [0.5], [0], [1])
