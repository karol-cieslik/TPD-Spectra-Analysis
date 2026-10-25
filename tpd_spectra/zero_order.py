"""Fixed-zero-order single-state fitting with an explicit sampled depletion edge.

For each possible last occupied sample j, profile energy while solving peak
height and optional constant baseline linearly. Include the no-depletion model
as a competing boundary so a truncated rising trace is not forced to deplete.
No smoothing or invented detector response is applied to the physical edge.
"""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from .analysis import K_B_EV


def fit_zero_order(temp_c, signal, beta, *, fit_baseline, max_nfev, cancelled=None):
    # Called after the common single-state input validation and duplicate handling.
    from .kinetics import KineticFitResult, _fit_information_criteria
    t = np.asarray(temp_c) + 273.15
    if np.any(t <= 0):
        raise ValueError('Temperature must be positive kelvin.')
    span = float(np.ptp(signal))
    y = np.asarray(signal) / span
    baseline_bounds = (float(np.min(y)-2), float(np.max(y)+1))
    best = None
    evaluations = 0

    def check_cancelled():
        if cancelled is not None and cancelled():
            raise InterruptedError('Zero-order depletion search cancelled')

    for j in range(2, len(t)):
        check_cancelled()
        x = (1/t[:j+1] - 1/t[j]) / K_B_EV

        def evaluate(energy, details=False):
            check_cancelled()
            q = np.zeros_like(t)
            q[:j+1] = np.exp(-energy*x)
            qq, qy, qs = np.dot(q,q), np.dot(q,y), float(np.sum(q))
            if fit_baseline:
                denominator = qq - qs*qs/len(t)
                height = max(0., (qy - qs*float(np.mean(y)))/max(denominator, np.finfo(float).tiny))
                baseline = float(np.clip(np.mean(y-height*q), *baseline_bounds))
                # If the baseline bound is active, solve the remaining coefficient.
                height = max(0., float(np.dot(q,y-baseline)/qq))
            else:
                height, baseline = max(0., float(qy/qq)), 0.
            predicted = height*q + baseline
            residual = predicted-y
            cost = float(np.dot(residual,residual))
            return (cost,height*span,baseline*span,predicted*span) if details else cost

        opt = minimize_scalar(evaluate, bounds=(.05,8.), method='bounded',
                              options={'xatol':1e-9,'maxiter':int(max_nfev)})
        evaluations += opt.nfev
        if not opt.success:
            raise RuntimeError('Zero-order energy profiling reached its evaluation limit; increase Maximum fit evaluations (per depletion boundary).')
        candidates = [(float(opt.x), evaluate(float(opt.x),True)),
                      (.05,evaluate(.05,True)), (8.,evaluate(8.,True))]
        evaluations += 3
        energy, values = min(candidates, key=lambda item:item[1][0])
        if best is None or values[0] < best[0]:
            best = (*values,energy,j)

    cost,height,baseline,predicted,energy,j = best
    if j == len(t)-1 or len(t)-j-1 < 3:
        raise ValueError('Zero-order fit needs a resolved depletion edge and at least three samples after it; extend the selected interval.')
    if height <= 0 or not np.isfinite(height):
        raise ValueError('No positive zero-order desorption signal was resolved.')
    check_cancelled()

    def log_integral(upper):
        # Integrate a scaled Arrhenius factor to retain relative precision even
        # when its unscaled integral is many orders below quad's absolute limit.
        value, _ = quad(lambda v: np.exp(-energy/K_B_EV*(1/v-1/upper)),
                        float(t[0]), float(upper), epsabs=1e-10, epsrel=2e-10)
        if not np.isfinite(value) or value <= 0:
            raise ValueError('Could not resolve the zero-order depletion integral.')
        return -energy/(K_B_EV*upper) + np.log(value)

    # theta(T_start)=1, so nu*integral/beta reaches one between j and j+1.
    physical_lo = np.log(beta) - log_integral(t[j+1])
    physical_hi = np.log(beta) - log_integral(t[j])
    log_product = np.log(height) + energy/(K_B_EV*t[j])  # log(A*nu)
    lo = max(physical_lo, np.log(1e3), log_product-np.log(1e30))
    hi = min(physical_hi, np.log(1e30), log_product-np.log(1e-30))
    if not np.isfinite([lo,hi]).all() or hi <= lo:
        raise ValueError('Zero-order depletion is incompatible with the prefactor/scale bounds; inspect temperature units, interval and model.')
    log_nu = (lo+hi)/2
    nu, scale = float(np.exp(log_nu)), float(np.exp(log_product-log_nu))
    warnings = [
        'Zero-order prefactor and signal scale are representative values, not a unique fitted pair. See conditional ranges at fixed energy and normalized initial coverage one.',
        'Depletion and parameter brackets reflect sample spacing and fixed fitted energy; they are not confidence intervals.',
        'Zero-order information criteria count the searched depletion boundary as one parameter; the usual AICc approximation is heuristic for this nonregular edge model.'
    ]
    if lo > physical_lo or hi < physical_hi:
        warnings.append('Conditional prefactor/scale ranges were restricted by parameter bounds.')
    if energy <= .050001 or energy >= 7.999999:
        warnings.append('Zero-order energy lies at a fit bound; inspect model adequacy.')
    n, p = len(t), 3+int(fit_baseline)  # energy, height, searched edge, [baseline]
    rmse = float(np.sqrt(cost/n)*span)
    noise = float(np.sqrt(cost/max(1,n-p))*span)
    if height <= 3*noise:
        raise ValueError('Zero-order depletion edge is not resolved above residual scatter (height <= 3 residual standard deviations).')
    if rmse/span > .15:
        warnings.append('Large residual: numerical completion does not establish zero-order model adequacy.')
    profile = {
        'depletion_bracket_c':[float(temp_c[j]),float(temp_c[j+1])],
        'conditional_prefactor_range_s_inv':[float(np.exp(lo)),float(np.exp(hi))],
        'conditional_signal_scale_range':[float(np.exp(log_product-hi)),float(np.exp(log_product-lo))],
        'representative_rule':'Geometric midpoint of compatible prefactors, within parameter bounds.',
        'condition':'Fixed fitted energy; normalized initial coverage 1 at interval start; point-sampled ideal zero-order model. Not confidence intervals.',
        'boundary_convention':'Depletion occurs after the last occupied sample and at or before the next sample; physical prefactor lower bound inclusive, upper bound exclusive.',
        'boundaries_evaluated':len(t)-2, 'energy_evaluations':int(evaluations),
        'max_energy_evaluations_per_boundary':int(max_nfev),
        'mean_model_parameter_count_for_information_criteria':p,
        'edge_height_to_residual_sigma':float(height/max(noise,np.finfo(float).tiny)),
        'fit_status':'Numerical profile search completed; review residuals and assumptions.'
    }
    diagnostics = {'jacobian_rank':2+int(fit_baseline),'n_parameters':p,
        'jacobian_condition_number':float('inf'), 'near_lower_bound_indices':[],
        'near_upper_bound_indices':[], 'warnings':warnings, 'zero_order_profile':profile,
        'jacobian_note':'Within a fixed occupied sample set, prefactor and scale occur only as their product; local derivatives cannot identify both.'}
    rss = float(np.sum((predicted-signal)**2))
    total = float(np.sum((signal-np.mean(signal))**2))
    aic,aicc,bic = _fit_information_criteria(rss,n,p)
    result = KineticFitResult(0.,False,energy,nu,scale,baseline,rmse,rmse/span,
        1-rss/total,n,True,'Zero-order depletion profile completed; prefactor and scale are representative, not unique.',
        float(temp_c[0]),float(temp_c[-1]),aic,aicc,bic,float('inf'),diagnostics)
    return result,predicted
