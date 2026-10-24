"""Read-only explanations of the equations used by the existing engines."""
from tkinter import ttk


EQUATIONS = {
    'Polanyi–Wigner': (
        'Desorption and measured signal',
        'r = −dθ/dt = ν θⁿ exp[−E/(k_B T)]\ndθ/dT = −r/β\nS(T) = A r(T) + b',
        'T in K · E in eV · β in K/s',
        'θ: dimensionless normalized coverage; n: desorption order; ν: prefactor '
        '(s⁻¹ with this coverage convention); β = dT/dt: constant heating rate. '
        'k_B: Boltzmann constant in eV/K. A: detector signal scale; b: constant '
        'baseline. The rate is zero after coverage is exhausted. Fits start '
        'with θ = 1 at the selected interval start; manual simulation can use '
        'another initial coverage. Fitting optimizes A and optionally b. '
        'Entered energy and prefactor are initial guesses, not fixed truths.'),
    'Leading edge': (
        'Leading-edge apparent energy',
        'ln(S) = a + m/T\nE_app = −k_B m',
        'T in K · E_app in eV',
        'S: positive processed signal in the recorded signal units; '
        'm: slope against 1/T; a: intercept; k_B: Boltzmann constant in eV/K. '
        'Requires signal proportional to rate and approximately unchanged '
        'coverage over the rising-edge interval. The arbitrary-unit intercept '
        'does not identify a physical prefactor. Heating rate is recorded '
        'but does not enter this slope-energy conversion.'),
    'Redhead': (
        'First-order Redhead approximation',
        'E ≈ k_B Tₚ [ln(ν Tₚ/β) − 3.64]',
        'Tₚ in K · E in eV · β in K/s',
        'Tₚ: temperature of the selected peak maximum; ν: assumed prefactor '
        '(s⁻¹); β: constant heating rate; k_B: Boltzmann constant in eV/K. '
        'This approximation assumes first-order kinetics. The prefactor is '
        'supplied, not fitted. All equations use T = temperature in °C + 273.15.'),
    'Monte Carlo': (
        'Parametric Monte Carlo refitting',
        'Sᵢ* = S_ref(Tᵢ) + εᵢ\nεᵢ ∼ Normal(0, σ²)',
        'Generate a noisy trace, then refit every candidate.',
        'S_ref: prediction from the lowest-AICc converged reference model; '
        'εᵢ: independent Gaussian noise. σ is estimated as '
        'sqrt(Σ[Sᵢ − S_ref(Tᵢ)]² / max(1, N − p)), where N is the number '
        'of selected points and p counts fitted mean-model parameters. '
        'The same simulated trace is used for all candidates in each replicate. '
        'Replicates controls how many traces are generated; seed initializes '
        'the random generator. This is not microscopic kinetic Monte Carlo '
        'or MCMC. Rankings and ranges are conditional on the reference and '
        'iid-noise assumptions, not validated mechanism probabilities or '
        'confidence limits.'),
}


class EquationCard(ttk.Frame):
    """Keep the equation visible and offer an optional symbol/assumption legend."""
    def __init__(self, parent, method):
        super().__init__(parent, padding=8, relief='groove', borderwidth=1)
        self.method = method
        title, equation, units, details = EQUATIONS[method]
        self.labels = []
        for text, font in ((title, ('Segoe UI', 10, 'bold')),
                           (equation, ('Segoe UI', 11)),
                           (units, ('Segoe UI', 9))):
            label = ttk.Label(self, text=text, font=font, wraplength=250, justify='left')
            label.pack(fill='x', pady=(0, 4))
            self.labels.append(label)
        self.toggle_button = ttk.Button(self, text='Symbols and assumptions ▸', command=self.toggle)
        self.toggle_button.pack(fill='x')
        self.details = ttk.Label(self, text=details, wraplength=250, justify='left')
        self.expanded = False
        self.bind('<Configure>', self.reflow)

    def toggle(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.details.pack(fill='x', pady=(6, 0))
        else:
            self.details.pack_forget()
        self.toggle_button.configure(text='Symbols and assumptions ▾' if self.expanded else 'Symbols and assumptions ▸')

    def reflow(self, event):
        width = max(120, event.width - 20)
        for label in (*self.labels, self.details):
            label.configure(wraplength=width)
