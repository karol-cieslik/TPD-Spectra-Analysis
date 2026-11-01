"""Short, navigable first-run exercises, with a longer offline HTML guide."""

import tkinter as tk
from tkinter import ttk


PAGES = (
    ('First result', '''1. Click Open Example Dataset and choose first order single peak.
2. Go to Kinetic Analysis → Redhead.
3. Verify heating rate = 1 K/s and assumed prefactor = 1e13 s⁻¹.
4. Calculate the selected peak if the preview has not updated.
5. In Parameter summary, look for an estimated energy near 1.2 eV.
6. Open Spectrum & residuals and Assumptions & provenance.
7. Save labeled result, then use Report / Export to retain the output.

This is a synthetic reference, not experimental validation. Redhead assumes first-order kinetics and a prefactor; it does not measure that prefactor.'''),
    ('Choose a peak', '''1. Open the default noisy two-peak demonstration.
2. The first-peak tutorial region is initially 70–210 °C.
3. To create your own region, go to Spectra & Preparation.
4. Enter a name, From °C and To °C, then click Add peak.
5. Alternatively disable plot pan/zoom, click Drag interval, select bounds, and save them with Add peak or Update peak.
6. Check the persistent Dataset and Peak selectors before fitting.

A named region is only a selection. Two overlapping physical populations are not separated by drawing two interval boxes.'''),
    ('Simulate and compare', '''1. With the default demo first peak selected, open Modeling & Order Identification.
2. Enter heating rate 1, initial energy 1.25 eV, prefactor 1e13 s⁻¹, simulation order 1 and coverage 1.
3. Click Simulate parameters. This overlays a curve from your inputs; it does not fit them.
4. For an introductory comparison enable First order only and turn Multistart off.
5. Click Compare models. Inspect residuals, Parameters & models and Assumptions & warnings.
6. Select the converged model and click Use selected model in Kinetic Analysis.
7. In Kinetic Analysis, click Calculate / Fit selected peak to perform the actual analysis.

A low residual or favorable AICc does not establish a unique desorption mechanism.'''),
    ('Monte Carlo', '''1. Complete a current Compare models calculation first.
2. Set Monte Carlo replicates to 20 for a short software check.
3. Set Monte Carlo seed to 42. This selects a reproducible random sequence, not a physical parameter.
4. Keep First order only and Multistart off for the initial exercise.
5. Click Run Monte Carlo and watch the count, percentage, estimated time and Cancel control.
6. Inspect successful versus failed refits and model-ranking counts.

This program refits noisy simulated spectra around a fitted reference. Ranges are withheld below 100 successful refits. Frequencies are not mechanism probabilities or experimentally calibrated confidence intervals. More replicates may take minutes.'''),
    ('Overlapping and export', '''1. For two peaks open the default demo, then Modeling → Fit Multiple Peaks… and select 2 components.
2. Verify 1 K/s; click approximate positions near 172 and 276 °C (or type positions), then Fit 2 Components.
3. First-order energy guesses and ±30% search bounds are heuristic, not measured values or uncertainty intervals.
4. Read the quality title, individual curves, sum, baseline, residuals and Assumptions & warnings. Baseline-only, collapsed or poor fits are unsupported even after convergence.
5. For Zaki D₂O/Fe₃O₄, explicitly accept/reject the source suggestion of 3 K/s. Opening published data never applies it silently. Modeling and Kinetic Analysis have separate rates. Correlated residuals still limit this stress test.

Advanced three-state exercise:
1. Use Open Example Dataset → three overlapping peaks.
2. In Modeling click Fit Multiple Peaks → select 3 components → Advanced settings.
3. Fix each order to 1 and prefactor to 1e13 s⁻¹; set starting coverages 1.0, 0.7 and 0.5.
4. Enter starting energies 1.185, 1.265 and 1.345 eV.
5. Use energy bounds 1.14–1.22, 1.22–1.30 and 1.30–1.38 eV.
6. Set heating rate to 1 K/s, Multistart off and maximum evaluations to 300.
7. Fit 3 Components, then inspect individual curves, their sum, residuals and warnings.
8. Export component fit and Save project to preserve the full configuration.

The joint model fits the entire spectrum. Order, prefactor and coverage are fixed hypotheses; component energies and nonnegative scales are fitted. This is a truth-informed numerical exercise, not blind identification.'''),
)


class QuickStartDialog:
    def __init__(self, app):
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title('TPD Spectra Studio — Guided Quick Start')
        self.window.geometry('900x610')
        self.window.minsize(700, 460)
        self.window.bind('<Escape>', lambda _event: self.window.destroy())
        ttk.Label(self.window, text='Guided Quick Start', font=('Segoe UI', 14, 'bold'),
                  padding=(12, 12, 12, 4)).pack(anchor='w')
        ttk.Label(self.window, text='Five hands-on exercises using shipped synthetic spectra. No numerical task runs automatically.',
                  padding=(12, 0, 12, 8), wraplength=840).pack(anchor='w')
        self.tabs = ttk.Notebook(self.window)
        self.tabs.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        for name, content in PAGES:
            frame = ttk.Frame(self.tabs)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            note = tk.Text(frame, wrap='word', padx=16, pady=14, font=('Segoe UI', 11))
            note.insert('end', content)
            note.configure(state='disabled')
            note.grid(row=0, column=0, sticky='nsew')
            scroll = ttk.Scrollbar(frame, orient='vertical', command=note.yview)
            scroll.grid(row=0, column=1, sticky='ns')
            note.configure(yscrollcommand=scroll.set)
            self.tabs.add(frame, text=name)
        footer = ttk.Frame(self.window, padding=(12, 0, 12, 12))
        footer.pack(fill='x')
        ttk.Button(footer, text='Open Example Dataset', command=app.open_example).pack(side='left')
        ttk.Button(footer, text='Scientific Help / Parameters',
                   command=app.open_scientific_help).pack(side='left', padx=8)
        ttk.Button(footer, text='Full worked guide (HTML)',
                   command=app.open_worked_examples).pack(side='left')
        ttk.Button(footer, text='Close', command=self.window.destroy).pack(side='right')
