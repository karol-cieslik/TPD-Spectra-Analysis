"""Independent separable PW solution on a dense temperature grid, not Gaussians.

dtheta/dT = -(nu/beta) theta**n exp(-E/kT). Integrate k/beta by quadrature,
then use the analytic solution in coverage for fixed n. No production ODE/fitter
is called. Regenerate from the repository root with this script.
"""
from pathlib import Path
import json
import hashlib
import math
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.constants import Boltzmann, elementary_charge
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'examples'/'beta_collection'
KB=Boltzmann/elementary_charge


def state(order=1.,energy=1.2,coverage=1.,scale=10000.):
    return dict(order=order,energy_eV=energy,prefactor_s_inv=1e13,initial_normalized_coverage=coverage,detector_scale=scale)


def configurations():
    basic=[
        ('zero_order_single_peak',[state(0)],'Zero-order depletion edge; peak position depends on initial coverage.'),
        ('first_order_single_peak',[state(1)],'Clean first-order reference: start here; isolated peak and no baseline.'),
        ('second_order_single_peak',[state(2)],'Second-order tail; a wider fitting interval matters.'),
        ('fractional_order_1p5',[state(1.5)],'Phenomenological fixed non-integer order; not a coverage-dependent microscopic mechanism.'),
        ('two_overlapping_peaks',[state(1,1.2),state(1,1.28,.65)],'Two independent additive states; single-state fitting can be misleading.'),
        ('three_overlapping_peaks',[state(1,1.18),state(1,1.26,.7),state(1,1.34,.5)],'Three independent additive states; use the GUI simultaneous full-spectrum Polanyi-Wigner fitter with fixed orders, prefactors and initial coverages. Visible features do not establish three physical states; see docs/MULTICOMPONENT_FITTING.md.'),
        ('first_order_noisy',[state(1)],'Independent Gaussian detector noise; compare residuals and try seeded Monte Carlo.'),
        ('first_order_noisy_baseline',[state(1)],'Gaussian noise plus constant offset and linear drift; a constant-baseline fitter cannot model the drift.'),
        ('challenging_overlap_drift',[state(.5,1.2),state(2,1.27,.7)],'Overlapping different-order states, correlated noise and drift deliberately violate single-state/MC assumptions.')]
    configs=[]
    for name,states,note in basic:
        configs.append(dict(name=name,states=states,beta_K_s=1.,expected_behavior=note))
    for beta in (.5,2.,5.):
        configs.append(dict(name=f'heating_rate_{str(beta).replace(".","p")}_K_s',states=[state()],beta_K_s=beta,
            expected_behavior='First-order heating-rate series; compare with first_order_single_peak.csv (1 K/s). Increasing beta shifts the maximum upward.'))
    for coverage in (.25,.5):
        for order in (0,1):
            configs.append(dict(name=f'{"zero" if order==0 else "first"}_order_coverage_{str(coverage).replace(".","p")}',
                states=[state(order,coverage=coverage)],beta_K_s=1.,
                expected_behavior='Coverage series; compare with the corresponding single_peak file (coverage 1). First-order peak position is coverage-independent in this model; zero-order peaks shift.'))
    # Append only: the original collection keeps its names, ordering and RNG seeds.
    for label,fraction in (('low',.01),('moderate',.02),('high',.05)):
        configs.append(dict(name=f'first_order_{label}_noise',states=[state()],beta_K_s=1.,
            noise_fraction_of_clean_maximum=fraction,clean_reference_file='first_order_single_peak.csv',
            expected_behavior=f'Fixed-seed iid Gaussian detector noise, {fraction:.0%} of the clean maximum; compare with the clean first-order reference.'))
    for count,states in (('two',[state(1,1.2),state(1,1.28,.65)]),
                         ('three',[state(1,1.18),state(1,1.26,.7),state(1,1.34,.5)])):
        configs.append(dict(name=f'{count}_overlapping_moderate_noise',states=states,beta_K_s=1.,
            noise_fraction_of_clean_maximum=.02,clean_reference_file=f'{count}_overlapping_peaks.csv',
            expected_behavior='Independent additive physical states with 2% iid Gaussian detector noise; visible features alone do not establish the number of physical states.'))
    return configs


def simulate(config,dense_c):
    rate=np.zeros_like(dense_c)
    for s in config['states']:
        k=s['prefactor_s_inv']*np.exp(-s['energy_eV']/(KB*(dense_c+273.15)))
        integral=cumulative_trapezoid(k/config['beta_K_s'],dense_c,initial=0)
        theta0,n=s['initial_normalized_coverage'],s['order']
        if n==1:
            theta=theta0*np.exp(-integral)
        else:
            base=theta0**(1-n)-(1-n)*integral
            theta=np.maximum(base,0)**(1/(1-n))
        rate+=s['detector_scale']*k*np.where(theta>0,theta**n,0)
    return rate


def add_observation_effects(clean,temperature_c,*,seed,noise_fraction=0.,
                            offset_fraction=0.,slope_fraction_per_K=0.,ar1_coefficient=0.):
    """Add reproducible detector effects after evaluating clean physical kinetics.

    Fractions refer to the maximum clean signal, before baseline addition. No
    clipping is applied: negative background-subtracted observations are valid.
    This helper preserves the original beta collection's floating-point order.
    """
    clean=np.asarray(clean,dtype=float)
    t=np.asarray(temperature_c,dtype=float)
    if clean.shape!=t.shape or clean.ndim!=1 or not np.isfinite(clean).all() or not np.isfinite(t).all():
        raise ValueError('Clean signal and temperature must be finite matching arrays.')
    if not np.isfinite([noise_fraction,offset_fraction,slope_fraction_per_K,ar1_coefficient]).all() or noise_fraction<0 or not abs(ar1_coefficient)<1:
        raise ValueError('Observation parameters must be finite; noise nonnegative and |AR(1)| < 1.')
    rng=np.random.default_rng(seed)
    noise=dict(model='none',sigma_signal_units=0.,ar1_coefficient=0.)
    baseline=dict(offset_signal_units=0.,slope_signal_units_per_K=0.,reference_temperature_c=float(t[0]))
    errors=np.zeros(t.size)
    if noise_fraction:
        noise.update(model='iid Gaussian',sigma_signal_units=float(clean.max()*noise_fraction))
        errors=rng.normal(0,noise['sigma_signal_units'],t.size)
    if offset_fraction or slope_fraction_per_K:
        baseline.update(offset_signal_units=float(clean.max()*offset_fraction),
                        slope_signal_units_per_K=float(clean.max()*slope_fraction_per_K))
    if ar1_coefficient:
        noise.update(model='stationary Gaussian AR(1)',ar1_coefficient=ar1_coefficient)
        for i in range(1,len(errors)):
            errors[i]=ar1_coefficient*errors[i-1]+np.sqrt(1-ar1_coefficient**2)*errors[i]
    observed=clean+errors+baseline['offset_signal_units']+baseline['slope_signal_units_per_K']*(t-baseline['reference_temperature_c'])
    return observed,noise,baseline


def generate(output=OUTPUT):
    output.mkdir(parents=True,exist_ok=True)
    dense=np.linspace(50,450,80001)  # 0.005 K quadrature; 0.5 K CSV sampling.
    t=dense[::100]
    catalog=[]
    configs=configurations()
    rows=math.ceil(len(configs)/4)
    overview=Figure(figsize=(14,3.5*rows),layout='constrained')
    FigureCanvasAgg(overview)
    for index,config in enumerate(configs):
        clean=simulate(config,dense)[::100]
        seed=20261024+index
        noisy='noisy' in config['name'] or 'challenging' in config['name']
        with_baseline='baseline' in config['name'] or 'challenging' in config['name']
        y,noise,baseline=add_observation_effects(clean,t,seed=seed,
            noise_fraction=config.get('noise_fraction_of_clean_maximum',.01 if noisy else 0.),
            offset_fraction=.025 if with_baseline else 0.,slope_fraction_per_K=.00015 if with_baseline else 0.,
            ar1_coefficient=.8 if 'challenging' in config['name'] else 0.)
        csv=output/(config['name']+'.csv')
        # Preserve the CRLF convention used by shipped beta hashes. Repeated
        # runs are byte-identical within one numerical environment; another
        # math library can change the final printed signal digit.
        with csv.open('w',encoding='utf-8',newline='') as handle:
            np.savetxt(handle,np.column_stack(((t-50)/config['beta_K_s']*1000,y,t)),delimiter=',',
                header='Time_ms,Signal,Temperature',comments='',fmt=['%.6f','%.12e','%.2f'],newline='\r\n')
        meta=dict(schema_version=1,synthetic=True,experimental=False,**config,number_of_states=len(config['states']),
            temperature_range_c=[50.,450.],temperature_unit='degC',time_unit='ms',
            signal_unit='arbitrary detector units proportional to normalized coverage/s',points=len(t),
            sampling_step_K=.5,integration_step_K=.005,noise=noise,baseline=baseline,random_seed=seed,
            generation_method='Separable constant-order Polanyi-Wigner solution; cumulative trapezoidal quadrature of Arrhenius rate on 0.005 K grid. Independent of production ODE solver.',
            limitations=['Synthetic data, not experimental measurements.','No readsorption, lateral interactions, transport limitation or instrument response.',
                'Normalized coverage is dimensionless; prefactors are expressed in s^-1 under this convention.',
                'Good parameter recovery is numerical verification, not proof of a unique physical mechanism.'],
            recommended_peak_c=[50.,450.],csv_sha256=hashlib.sha256(csv.read_bytes()).hexdigest())
        if config['name'] in ('first_order_single_peak','second_order_single_peak','fractional_order_1p5','zero_order_single_peak'):
            meta['recovery_check']={'fixed_true_order':True,'initial_energy_eV':1.2,'initial_prefactor_s_inv':1e13,
                'fit_baseline':False,'max_nfev':300,'energy_relative_tolerance':.05 if config['states'][0]['order']==0 else .02,
                'log10_prefactor_absolute_tolerance':.7 if config['states'][0]['order']==0 else .3,
                'normalized_rmse_tolerance':.02 if config['states'][0]['order']==0 else .01,
                'note':'Predefined before verification; truth-informed initialization checks solver consistency, not robust blind identification.'}
        if any(s['order']==0 for s in config['states']):
            meta['limitations'].append('Fixed-zero-order fitting requires a resolved depletion edge. Prefactor and detector scale are representative values within conditional ranges at fitted energy and normalized coverage one; these ranges are not confidence intervals.')
        (output/(config['name']+'.json')).write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')
        catalog.append(dict(file=csv.name,metadata=config['name']+'.json',title=config['name'].replace('_',' '),description=config['expected_behavior'],beta_K_s=config['beta_K_s']))
        ax=overview.add_subplot(rows,4,index+1)
        ax.plot(t,y,linewidth=1,color='#087E8B')
        ax.set(title=config['name'].replace('_',' '),xlabel='Temperature (°C)',ylabel='Signal (a.u.)')
        ax.title.set_fontsize(9)
        ax.tick_params(labelsize=8)
    overview.suptitle('SYNTHETIC TPD EXAMPLES — physical-model simulations, not experimental data',fontsize=16)
    overview.savefig(output/'overview.png',dpi=130)
    (output/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf-8',newline='\n')
    return catalog


if __name__=='__main__':
    print(f'Generated {len(generate())} documented synthetic spectra in {OUTPUT}')
