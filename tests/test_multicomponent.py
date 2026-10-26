"""Joint kinetic recovery against independent separable PW quadrature.

The reference does not call the production ODE or fit a sum of Gaussians.
These are numerical verification tests, not experimental interval calibration.
"""
from dataclasses import asdict, replace
import json
import numpy as np
import pytest
from scipy.integrate import cumulative_trapezoid

from tpd_spectra.analysis import K_B_EV
from tpd_spectra.kinetics import simulate_tpd
from tpd_spectra.multicomponent import (
    ComponentDefinition, fit_components, compare_component_counts, _jacobian_information,
)
from tpd_spectra.workflow_analysis import serial


def independent_signal(components, scales, *, beta=1.0):
    dense = np.linspace(50.0, 450.0, 80001)
    curves = []
    for c, scale in zip(components, scales):
        k = c.prefactor_s_inv * np.exp(-c.energy_eV / (K_B_EV * (dense + 273.15)))
        exposure = cumulative_trapezoid(k / beta, dense, initial=0)
        if c.order == 1:
            theta = c.initial_coverage * np.exp(-exposure)
        else:
            remaining = c.initial_coverage ** (1 - c.order) - (1 - c.order) * exposure
            theta = np.maximum(remaining, 0) ** (1 / (1 - c.order))
        curves.append((scale * k * np.where(theta > 0, theta ** c.order, 0))[::200])
    return dense[::200], np.sum(curves, axis=0), curves


@pytest.fixture(scope='module')
def three_reference():
    truth = [ComponentDefinition(f'State {i + 1}', energy_eV=e,
                                 energy_bounds=(e - .04, e + .04))
             for i, e in enumerate((1.18, 1.26, 1.34))]
    t, y, curves = independent_signal(truth, (10000, 7000, 5000))
    guesses = [replace(c, energy_eV=c.energy_eV + .005) for c in truth]
    result = fit_components(t, y, 1.0, guesses, fit_baseline=False,
                            multistart=False, max_nfev=150)
    return truth, guesses, t, y, curves, result


def test_three_components_are_jointly_recovered_and_sum_exactly(three_reference):
    truth, _, temperature, signal, reference_curves, result = three_reference
    assert result.success
    assert result.normalized_rmse < 1e-3
    assert result.n_parameters == 6 and result.n_points == len(signal)
    assert [c['label'] for c in result.components] == [c.label for c in truth]
    np.testing.assert_allclose([c['energy_eV'] for c in result.components],
                               [c.energy_eV for c in truth], atol=.002, rtol=0)
    np.testing.assert_allclose([c['signal_scale'] for c in result.components],
                               [10000, 7000, 5000], rtol=.02)
    np.testing.assert_array_equal(result.temperature_c, temperature)
    np.testing.assert_array_equal(result.observed, signal)
    np.testing.assert_allclose(result.prediction,
                               np.sum(result.component_predictions, axis=0) + result.baseline_prediction,
                               rtol=0, atol=0)
    np.testing.assert_array_equal(result.residuals, signal - result.prediction)
    for fitted, reference in zip(result.component_predictions, reference_curves):
        assert np.all(fitted >= 0)
        assert np.sqrt(np.mean((fitted - reference) ** 2)) / signal.max() < 1e-3


def test_mixed_orders_keep_the_supplied_nonunit_coverage():
    truth = [ComponentDefinition('First', order=1, energy_eV=1.16),
             ComponentDefinition('Second', order=2, energy_eV=1.32, initial_coverage=.7)]
    temperature, signal, _ = independent_signal(truth, (8000, 12000))
    guesses = [replace(c, energy_eV=c.energy_eV + .008) for c in truth]
    result = fit_components(temperature, signal, 1, guesses, fit_baseline=False,
                            multistart=False, max_nfev=150)
    assert result.normalized_rmse < 1e-3
    np.testing.assert_allclose([c['energy_eV'] for c in result.components], [1.16, 1.32], atol=.002, rtol=0)
    np.testing.assert_allclose([c['signal_scale'] for c in result.components], [8000, 12000], rtol=.02)
    assert result.components[1]['initial_coverage'] == .7
    assert [c['order'] for c in result.components] == [1, 2]


def test_sub_first_order_forward_fit_and_conservative_uncertainty():
    truth = [ComponentDefinition('Depleting', order=.5, energy_eV=1.2),
             ComponentDefinition('Fractional', order=1.5, energy_eV=1.34, initial_coverage=.7)]
    temperature, signal, _ = independent_signal(truth, (10000, 8000))
    result = fit_components(temperature, signal, 1, truth, fit_baseline=False,
                            multistart=False, max_nfev=120)
    assert result.normalized_rmse < 1e-3
    assert not result.diagnostics['uncertainty_available']
    assert any('finite depletion edge' in warning for warning in result.warnings)


def test_noisy_joint_fit_reports_conditional_uncertainty_and_drift(three_reference):
    truth, guesses, t, clean, _, _ = three_reference
    noise = np.random.default_rng(20261026).normal(0, .01 * clean.max(), clean.size)
    signal = clean + 5 + .02 * (t - t.mean()) + noise
    result = fit_components(t, signal, 1, guesses, fit_baseline=True, fit_drift=True,
                            baseline_bounds=(-20, 20), drift_bounds=(-.1, .1),
                            multistart=False, max_nfev=150)
    assert result.normalized_rmse < .02
    assert result.n_parameters == 8
    assert result.baseline == pytest.approx(5, abs=1)
    assert result.drift_per_K == pytest.approx(.02, abs=.005)
    assert result.baseline_reference_c == t.mean()
    assert result.diagnostics['uncertainty_available']
    assert 'conditional' in result.uncertainty_note
    np.testing.assert_allclose(np.diag(result.diagnostics['parameter_correlation']), 1)
    np.testing.assert_allclose(result.diagnostics['parameter_correlation'],
                               np.asarray(result.diagnostics['parameter_correlation']).T, atol=1e-12)
    assert not result.diagnostics['exchangeable_component_labels']
    for c, expected in zip(result.components, truth):
        assert c['energy_eV'] == pytest.approx(expected.energy_eV, abs=.002)
        assert c['energy_standard_error_eV'] > 0
        assert c['signal_scale_standard_error'] > 0
        assert c['energy_interval_95_eV'][0] < c['energy_eV'] < c['energy_interval_95_eV'][1]
        assert c['fixed_parameters'] == ['order', 'prefactor_s_inv', 'initial_coverage']


def test_coincident_components_withhold_ambiguous_intervals():
    truth = ComponentDefinition('One', energy_eV=1.2, energy_bounds=(1.1, 1.3))
    t, y, _ = independent_signal([truth], [10000])
    definitions = [truth, replace(truth, label='Indistinguishable')]
    result = fit_components(t, y, 1, definitions, fit_baseline=False,
                            multistart=False, max_nfev=100)
    assert result.success and result.normalized_rmse < 1e-3
    assert not result.diagnostics['uncertainty_available']
    assert any('ambiguous' in warning or 'identifiable' in warning for warning in result.warnings)
    assert result.diagnostics['component_profile_similarities'][0]['cosine_similarity'] > .995
    assert all(c['energy_interval_95_eV'] is None for c in result.components)
    assert all(c['signal_scale_interval_95'] is None for c in result.components)


def test_single_component_prediction_uses_the_existing_physical_solver():
    truth = ComponentDefinition('Single', energy_eV=1.2, initial_coverage=.6)
    t, y, _ = independent_signal([truth], [9000])
    result = fit_components(t, y, 1, [truth], fit_baseline=False, multistart=False)
    c = result.components[0]
    _, rate = simulate_tpd(t, 1, c['energy_eV'], c['prefactor_s_inv'], c['order'], c['initial_coverage'])
    np.testing.assert_array_equal(result.prediction, c['signal_scale'] * rate)
    assert c['signal_scale'] == pytest.approx(9000, rel=.01)


def test_cancellation_is_checked_inside_the_numerical_work(three_reference):
    _, guesses, t, y, _, _ = three_reference
    calls = 0
    def cancelled():
        nonlocal calls
        calls += 1
        return calls > 7
    with pytest.raises(InterruptedError, match='cancelled'):
        fit_components(t, y, 1, guesses, cancelled=cancelled)
    assert calls > 7


def test_exhausted_optimizer_does_not_return_a_successful_fit(three_reference):
    _, guesses, t, y, _, _ = three_reference
    with pytest.raises(RuntimeError, match='did not converge'):
        fit_components(t, y, 1, guesses, fit_baseline=False,
                       multistart=False, max_nfev=1)


def test_count_comparison_uses_the_same_observations_and_baseline_model(three_reference):
    _, guesses, t, y, _, _ = three_reference
    candidates = compare_component_counts(t, y, 1, guesses, fit_baseline=True,
                                           multistart=False, max_nfev=150)
    assert {c.count for c in candidates} == {1, 2, 3}
    assert all(c.error is None and c.fit.success for c in candidates)
    assert candidates[0].count == 3 and candidates[0].delta_aicc == 0
    assert sum(c.akaike_weight for c in candidates) == pytest.approx(1)
    for candidate in candidates:
        assert candidate.fit.n_points == len(t)
        assert candidate.fit.n_parameters == 2 * candidate.count + 1
        np.testing.assert_array_equal(candidate.fit.observed, y)
        np.testing.assert_array_equal(candidate.fit.temperature_c, t)
        assert candidate.fit.diagnostics['fit_baseline']
        assert not candidate.fit.diagnostics['fit_drift']
        assert len(candidate.fit.components) == candidate.count


def test_count_comparison_keeps_failures_distinct_from_success(three_reference):
    _, guesses, t, y, _, _ = three_reference
    candidates = compare_component_counts(t, y, 1, guesses, fit_baseline=False,
                                           multistart=False, max_nfev=1)
    assert all(c.error and c.fit is None for c in candidates)
    assert all(c.delta_aicc is None and c.akaike_weight is None for c in candidates)
    with pytest.raises(InterruptedError):
        compare_component_counts(t, y, 1, guesses, cancelled=lambda: True)


@pytest.mark.parametrize('component', [
    ComponentDefinition('Bad', order=0),
    ComponentDefinition('Bad', order=-1),
    ComponentDefinition('Bad', prefactor_s_inv=0),
    ComponentDefinition('Bad', initial_coverage=1.1),
    ComponentDefinition('Bad', energy_bounds=(1.4, 1.0)),
    ComponentDefinition('Bad', energy_eV=2, energy_bounds=(1, 1.5)),
])
def test_invalid_component_definitions_are_rejected(component):
    t = np.linspace(50, 450, 30)
    with pytest.raises(ValueError):
        fit_components(t, np.sin(t), 1, [component])


def test_invalid_input_and_unsupported_count_comparisons(three_reference):
    _, guesses, t, y, _, _ = three_reference
    for bad_t, bad_y, beta in ((t[::-1], y, 1), (t, y, 0), (t, y * np.nan, 1),
                               (np.round(t / 10), y, 1), (t, np.ones_like(y), 1)):
        with pytest.raises(ValueError):
            fit_components(bad_t, bad_y, beta, guesses)
    with pytest.raises(ValueError, match='distinct'):
        fit_components(t, y, 1, [guesses[0], guesses[0]])
    with pytest.raises(ValueError):
        compare_component_counts(t, y, 1, guesses, counts=(1, 4))
    with pytest.raises(ValueError):
        fit_components(t, y, 1, guesses, fit_baseline=False, fit_drift=True)
    with pytest.raises(ValueError):
        fit_components(t, y, 1, guesses, baseline_bounds=(1, -1))


def test_multistart_is_deterministic_and_counts_convergence():
    definition = ComponentDefinition('One', energy_eV=1.2)
    t, y, _ = independent_signal([definition], [10000])
    first = fit_components(t, y, 1, [definition], fit_baseline=False, max_nfev=120)
    second = fit_components(t, y, 1, [definition], fit_baseline=False, max_nfev=120)
    assert first.starts_attempted == 3
    assert first.starts_converged > 0
    assert first.components == second.components
    np.testing.assert_array_equal(first.prediction, second.prediction)


def test_result_is_strict_json_serializable_with_all_components(three_reference):
    *_, result = three_reference
    payload = serial(asdict(result))
    restored = json.loads(json.dumps(payload, allow_nan=False))
    assert len(restored['components']) == len(restored['component_predictions']) == 3
    assert restored['components'][1]['label'] == 'State 2'
    assert restored['uncertainty_note']
    assert restored['diagnostics']['uncertainty_withheld_reasons']


def test_local_information_preserves_independent_directions_across_parameter_units():
    # Three independent directions spanning eighteen orders of magnitude in
    # numerical coordinates must not lose a parameter through raw J.T@J pinv.
    jac = np.random.default_rng(812).normal(size=(100, 3))
    units = np.array([1e-9, 1, 1e9])
    covariance, correlation, rank, condition, _ = _jacobian_information(jac)
    rescaled, rescaled_correlation, rescaled_rank, rescaled_condition, _ = _jacobian_information(jac * units)
    assert rank == rescaled_rank == 3
    assert condition == pytest.approx(rescaled_condition, rel=1e-12)
    np.testing.assert_allclose(rescaled * units[:, None] * units[None, :], covariance, rtol=1e-12, atol=1e-14)
    np.testing.assert_allclose(rescaled_correlation, correlation, rtol=1e-12, atol=1e-14)
    assert np.all(np.diag(rescaled) > 0)


@pytest.mark.parametrize('unit_factor', [1e-16, 1e-12, 1e12])
def test_detector_unit_changes_preserve_predictions_and_conditional_errors(unit_factor):
    definition = ComponentDefinition('One', energy_eV=1.2)
    t, clean, _ = independent_signal([definition], [10000])
    signal = clean + np.random.default_rng(314).normal(0, .01 * clean.max(), clean.size)
    result = fit_components(t, signal, 1, [definition], multistart=False)
    rescaled = fit_components(t, signal * unit_factor, 1, [definition], multistart=False)
    assert result.diagnostics['uncertainty_available'] and rescaled.diagnostics['uncertainty_available']
    np.testing.assert_allclose(rescaled.prediction / unit_factor, result.prediction, rtol=1e-5, atol=1e-5)
    assert rescaled.normalized_rmse == pytest.approx(result.normalized_rmse, rel=1e-5)
    first, second = result.components[0], rescaled.components[0]
    assert second['energy_eV'] == pytest.approx(first['energy_eV'], abs=1e-7)
    assert second['energy_standard_error_eV'] == pytest.approx(first['energy_standard_error_eV'], rel=1e-4)
    assert second['signal_scale'] / unit_factor == pytest.approx(first['signal_scale'], rel=1e-5)
    assert second['signal_scale_standard_error'] / unit_factor == pytest.approx(first['signal_scale_standard_error'], rel=1e-4)


def test_separated_but_exchangeable_labels_withhold_labeled_intervals():
    truth = [ComponentDefinition('Low', energy_eV=1.18, initial_coverage=1, energy_bounds=(1, 1.5)),
             ComponentDefinition('High', energy_eV=1.34, initial_coverage=.6, energy_bounds=(1, 1.5))]
    t, clean, _ = independent_signal(truth, (10000, 9000))
    signal = clean + np.random.default_rng(761).normal(0, .01 * clean.max(), clean.size)
    direct = fit_components(t, signal, 1, truth, multistart=False)
    swapped_guesses = [replace(truth[0], energy_eV=truth[1].energy_eV),
                       replace(truth[1], energy_eV=truth[0].energy_eV)]
    swapped = fit_components(t, signal, 1, swapped_guesses, multistart=False)
    assert direct.diagnostics['jacobian_rank'] == direct.n_parameters
    assert direct.diagnostics['normalized_jacobian_condition_number'] < 100
    assert direct.diagnostics['maximum_absolute_parameter_correlation'] < .95
    assert direct.diagnostics['exchangeable_component_labels'] == [['Low', 'High']]
    assert not direct.diagnostics['uncertainty_available']
    assert any('labels are exchangeable' in warning for warning in direct.warnings)
    assert all(c['energy_interval_95_eV'] is None for c in direct.components)
    np.testing.assert_allclose(direct.prediction, swapped.prediction, rtol=2e-4, atol=.002)
    assert direct.components[0]['energy_eV'] == pytest.approx(swapped.components[1]['energy_eV'], abs=1e-5)
    # Nonoverlapping supplied energy constraints remove this exact permutation,
    # leaving a deliberately conditional interpretation of each user label.
    constrained = [replace(truth[0], energy_bounds=(1.14, 1.22)),
                   replace(truth[1], energy_bounds=(1.30, 1.38))]
    labeled = fit_components(t, signal, 1, constrained, multistart=False)
    assert not labeled.diagnostics['exchangeable_component_labels']
    assert labeled.diagnostics['uncertainty_available']
