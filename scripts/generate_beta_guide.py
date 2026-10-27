"""Build the five-page review guide; no fabricated application screenshots."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/beta/QUICK_START.pdf'


def generate(font_directory=None):
    if font_directory is None:
        from matplotlib import get_data_path
        font_directory=Path(get_data_path())/'fonts/ttf'
    fonts=Path(font_directory)
    pdfmetrics.registerFont(TTFont('Guide',str(fonts/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('GuideBold',str(fonts/'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFontFamily('Guide',normal='Guide',bold='GuideBold')
    c=Canvas(str(OUT),pagesize=(595.28,841.89))
    c.setTitle('TPD Spectra Studio - Quick Start 0.11.0b5 (review guide)')
    c.setAuthor('Karol Cieślik')
    c.setCreator('TPD Spectra Studio')
    c.setSubject('Five-page Quick Start for informal research beta testing')
    body=ParagraphStyle('body',fontName='Guide',fontSize=10.5,leading=16,textColor=HexColor('#243748'))
    heading=ParagraphStyle('heading',parent=body,fontName='GuideBold',fontSize=14,leading=20,textColor=HexColor('#087e8b'))
    y=0
    def start(number,title,subtitle):
        nonlocal y
        c.setFillColor(HexColor('#11283e'));c.rect(0,726,596,116,fill=1,stroke=0)
        c.setFillColor(HexColor('#73d6d3'));c.setFont('GuideBold',10)
        c.drawString(42,808,'TPD SPECTRA STUDIO  /  0.11.0b5')
        c.setFillColor(HexColor('#ffffff'));c.setFont('GuideBold',23);c.drawString(42,772,title)
        c.setFont('Guide',10);c.drawString(42,746,subtitle)
        c.setFillColor(HexColor('#657482'));c.setFont('Guide',8)
        c.drawString(42,31,'Karol Cieślik  •  External beta review guide  •  27 October 2026')
        c.drawRightString(553,31,f'{number} / 5')
        y=701
    def p(text,style=body,gap=12):
        nonlocal y
        paragraph=Paragraph(text,style);w,h=paragraph.wrap(510,700)
        assert y-h>55, f'Page overflow: {text[:40]}'
        paragraph.drawOn(c,42,y-h);y-=h+gap
    start(1,'Your first useful result','A five-to-ten-minute starting exercise using clearly labeled synthetic data')
    p('1  Extract and launch',heading)
    p('Open <link href="https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/workflows/desktop-build.yml?query=branch%3Amain" color="#087e8b">Windows beta builds</link>, choose the latest successful <b>main</b> run, and download the 0.11.0b5 ZIP under Artifacts. GitHub sign-in may be required. Extract the entire ZIP, keeping <b>docs</b> and <b>examples</b> beside <b>TPD-Spectra-Studio.exe</b>. Double-click the executable. The seeded noisy two-peak demo opens with its first peak selected. Check VERSION.json for the build commit. The unsigned beta must comply with your institution’s software policy.')
    p('2  Open the clean example',heading)
    p('Click <b>Open Example Dataset</b>. Keep <b>first order single peak</b> and open it. You should see 801 points and a named full-trace interval, 50–450 °C. The chooser supplies the documented 1 K/s ramp. These are simulated rates, not measurements.')
    p('3  Read an energy estimate',heading)
    p('Open <b>Kinetic Analysis</b> and select <b>Redhead</b>. Check heating rate <b>1 K/s</b> and assumed prefactor <b>1e13 s⁻¹</b>. The automatic preview should be approximately <b>1.2 eV</b>, within 2.5% of the simulation input. This first-order approximation has no measured confidence interval.')
    p('4  Keep the result',heading)
    p('Click <b>Save labeled result…</b> and give it a meaningful name. Use <b>Report / Export…</b> to select that run and choose a destination. Open the exported PDF. Use <b>Save project…</b> to retain the whole workspace for later.')
    p('<b>Need help?</b> The beta includes a feedback form under <b>Report a Bug / Send Feedback</b>. Even a short note about an unclear control or unexpected result is useful. This walkthrough uses synthetic data, so there is no need to share your measurements.',gap=0)
    c.showPage()
    start(2,'Prepare and compare','Keep the dataset, named peak and processing recipe visible')
    p('Bring your own spectrum',heading)
    p('Use <b>Open Spectrum…</b> for a CSV. Confirm temperature and time units, heating rate and signal meaning from acquisition records. The synthetic CSV format is <b>Time_ms, Signal, Temperature</b>, with temperature in °C. Inspect the import report; do not change cleaning thresholds merely to force bad data through.')
    p('Define a physically useful interval',heading)
    p('In <b>Spectra &amp; Preparation</b>, enter a peak name and From/To temperatures, then <b>Add peak</b>. Or use <b>Drag interval</b> with plot pan/zoom off. Save edits with <b>Update peak</b>. The persistent Dataset and Peak selectors control all three stages. Include adequate tails; avoid unmodeled neighbors.')
    p('Separate display choices from analysis',heading)
    p('Normalization changes the display only. Smoothing initially previews the plot. <b>Apply smoothing / baseline to analysis</b> records an analysis recipe; Undo and Reset are available. Changing bounds or processing marks previous results stale, while saved runs retain their original settings.')
    p('Explore a hypothesis',heading)
    p('In <b>Modeling &amp; Order Identification</b>, simulate parameters or select candidate orders and <b>Compare models</b>. Start with the first-order candidate on the clean first-order example. Inspect fit residuals, convergence and identifiability warnings, not only the lowest AICc. A good curve match does not identify a unique mechanism.')
    p('<b>Fixed zero-order fitting:</b> the new method searches the depletion edge. Include rising signal and at least three samples after exhaustion. Prefactor and scale represent conditional ranges, not unique estimates or confidence intervals. Review residuals; numerical completion does not prove the model.')
    p('Other examples',heading)
    p('The chooser includes second/fractional order, overlapping populations, noisy/drifting traces, heating-rate and coverage series. The default demo also has clean, 1%, 2%, 5% noise and baseline-drift variants. Noise is added after the physical calculation with fixed seeds; clean truth is retained. Each CSV has an adjacent JSON with generating parameters and assumptions. Read <b>examples/README.md</b>.')
    c.showPage()
    start(3,'Fit and inspect uncertainty','Simulation, model comparison and a final kinetic fit are separate steps')
    p('Transfer a candidate deliberately',heading)
    p('Open <b>Parameters &amp; models</b>, select a converged comparison row and choose <b>Use selected model in Kinetic Analysis</b>. This transfers a hypothesis and initial guesses. Check the method, ramp, order and interval, then press <b>Calculate / Fit selected peak</b>. Inspect residuals and <b>Assumptions &amp; provenance</b> before saving.')
    p('Choose a method that fits the question',heading)
    p('<b>Leading edge:</b> apparent slope energy on a rising interval with little coverage change. On the clean reference, try 90–110 °C; expect about 1.2 eV. Do not use the entire peak. This does not assign zero order.<br/><br/><b>Redhead:</b> first-order estimate with an assumed prefactor and linear ramp.<br/><br/><b>Polanyi–Wigner:</b> single-state numerical fitting. Energy, prefactor and amplitude may be poorly identifiable. The fitter normalizes initial coverage to one; absolute coverage is not measured here.')
    p('Try Monte Carlo after comparison',heading)
    p('Return to Modeling, complete a current comparison, choose a seed/count, then <b>Run Monte Carlo</b>. For a short software check use first order only, multistart off, 20 replicates and seed 42. The visible bar shows count, percentage, elapsed time and an estimated remainder. <b>Cancel</b> preserves prior valid results. Completion separates fit failures from incomplete rankings. Conditional ranges require 100 successful refits and are not coverage-validated.')
    p('What Monte Carlo means here',heading)
    p('This is <b>parametric refitting</b> with iid Gaussian noise around the lowest-AICc converged reference and its residual noise estimate. It is not microscopic kinetic Monte Carlo or Bayesian MCMC. Rank frequencies describe conditional stability, not probabilities of mechanisms. Drift, correlated noise, calibration and model uncertainty are not included.')
    p('Science before presentation',heading)
    p('Synthetic recovery is a software check. The clean benchmarks use known-order, truth-informed starts; they do not demonstrate robust blind inference. Compare real results with an independent calculation and suitable reference measurements. Keep acquisition conditions, model assumptions and limitations with every exported result.')
    c.showPage()
    start(4,'Fit overlapping components','Explicit independent physical populations on one full experimental spectrum')
    p('Define physical hypotheses',heading)
    p('In Modeling click <b>Overlapping components…</b>. Add up to three named rows. Set each fixed positive order, prefactor, initial normalized coverage, initial energy and energy bounds. <b>Fit components together</b> optimizes all energies and nonnegative detector scales jointly. Shared offset and optional linear drift can be fitted. Heating rate, evaluation budget and multistart come from Modeling.')
    p('Try the three-state synthetic reference',heading)
    p('Open <b>three overlapping peaks</b>. Define three first-order rows with prefactor <b>1e13 s⁻¹</b> and coverage one. Use initial energies <b>1.185, 1.265, 1.345 eV</b>; bounds <b>1.14–1.22, 1.22–1.30, 1.30–1.38 eV</b>; heating rate 1 K/s; multistart off and 300 evaluations. This truth-informed numerical exercise does not demonstrate blind physical identification. Try the moderate-noise variant and alternative justified assumptions.')
    p('Inspect the whole fitted signal',heading)
    p('The joint calculation uses the <b>entire selected dataset</b>; named regions do not crop it. <b>Spectrum &amp; residuals</b> shows observations, every component, baseline, combined fit and observation-minus-sum residuals. <b>Compare component counts</b> fits the first 1, 2, … defined rows on identical data/baseline assumptions. Double-click a count in <b>Parameters &amp; models</b> to plot it. Read <b>Assumptions &amp; warnings</b>; rankings are heuristic.')
    p('Retain assumptions and uncertainty limits',heading)
    p('<b>Save project…</b> retains definitions/results. <b>Export component fit…</b> writes individual parameters, curves, residuals, JSON provenance and PNG/SVG into a new folder. Local intervals are conditional on fixed kinetics and iid noise; ambiguous, exchangeable or ill-conditioned decompositions withhold them. Three features do not prove three states. Component Monte Carlo and multicomponent zero-order fitting are unavailable in this increment. See <b>docs/MULTICOMPONENT_FITTING.md</b>.')
    c.showPage()
    start(5,'Save, share and report','Choose what leaves the application and inspect it before sharing')
    p('Review results and choose the destination',heading)
    p('Use <b>Save labeled result…</b> for each result you want to retain. <b>Report / Export…</b> shows the saved-run selection; use Ctrl/Shift for multiple rows. Click <b>Choose destination and generate report…</b>. A fresh folder receives PDF, parameter/curve CSV, JSON, PNG and SVG. Existing report folders are preserved. The dialog previews selected content, not the rendered PDF.')
    p('Save a portable project',heading)
    p('<b>Save project…</b> writes a .tpd.json file containing imported arrays, named peaks, settings, recipes, saved results and modeling sessions. <b>Open project…</b> restores them. Projects and analysis reports contain data and provenance; they are not privacy-filtered diagnostic reports.')
    p('Send useful feedback without a GitHub account',heading)
    p('Open <b>Report a Bug / Send Feedback</b>, choose a category, describe the problem and optionally add steps or your email. Click <b>Update report preview</b>. Inspect/edit the exact text. <b>Copy Diagnostic Report</b> works offline; <b>Save Diagnostic ZIP</b> saves only the report and an explanatory README. No spectra or arbitrary files are attached.')
    p('After checking the review box, <b>Send Feedback by Email</b> opens a draft to <b>karol.j.cieslik@gmail.com</b>. Attach the ZIP manually if wanted and decide whether to send. If no mail application opens, copy the report into your preferred mail service. <b>Report on GitHub</b> opens a public issue draft; review it before submission.')
    p('About and contribution',heading)
    p('<b>Dr. Karol Cieślik</b> created and maintains TPD Spectra Studio. About shows the version/build, contact, source, fork and license information. Suggestions, scientific discrepancies and contributions are welcome.<br/><link href="https://github.com/karol-cieslik/TPD-Spectra-Analysis" color="#087e8b">github.com/karol-cieslik/TPD-Spectra-Analysis</link>')
    p('No experimental data is required for feedback. Share only material you have permission to share. Private debugging permission does not authorize publication or redistribution. See the optional tester checklist for a short, low-pressure review.')
    c.save()
    return OUT


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--font-directory',type=Path)
    print(generate(parser.parse_args().font_directory))
