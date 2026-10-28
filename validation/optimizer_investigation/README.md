# Wrong-energy fit investigation

Reproduced on the 81-point independent first-order reference: E=1.1 eV,
nu=1e12, beta=1 K/s, scale=1e4, offset=2, iid noise 1.5% of peak, seed 123.
Each fit used max_nfev=100. No production algorithm was changed.

All three default starts returned success via ftol termination but normalized
RMSE approximately 0.2643033, baseline approximately 40.30056 and negligible
signal scale. Energies were 0.89857, 0.99365 and 1.46474 eV. AICc values differ
only around 1e-8; the selected 1.46474 eV fit is merely the marginally lowest
of three poor, essentially baseline-only fits. Its scale was 2.21e-20.

A start at E=1.1 eV, nu=1e12 recovered E=1.094635 eV, nu=8.496e11,
scale=10090.88, baseline=1.95671, normalized RMSE=0.0127347 and AICc=224.354,
versus AICc=715.662 for the default-start results. Thus these are not equally
good alternative energy estimates: a much better solution exists.

The confirmed failure is inadequate initialization/global search followed by
local least-squares convergence to a signal-suppressed solution. ftol success
only certifies the local termination condition. Existing large-residual warnings
flag poor fits but do not prevent their selection. Model ranking can therefore
be based on poorly optimized candidates. This compromises general order and
energy recovery claims even when conditional MC rankings are repeatable.

Next fix to evaluate: initialize energy/prefactor combinations so their predicted
peaks lie within the observed peak range, profile the linear detector-scale and
baseline nuisance parameters, and explicitly diagnose signal-suppressed fits.
Add a regression reproducing this case before adopting a correction. Verify
independent first/second/fractional examples, noise, drift, truncation and genuine
non-identifiability. Do not simply add the known truth to a hard-coded start list,
reject all high-residual data as invalid, or describe favorable initialization
as general validation. Numerical derivative/solver behavior may contribute,
but its independent causal contribution has not yet been isolated.

Full per-start values are in results.json. The previous timing stall was not
reproduced and should not be presented as a confirmed solver bug.
