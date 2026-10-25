"""Build the four-page review guide; no fabricated application screenshots."""
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
    c.setTitle('TPD Spectra Studio - Quick Start 0.11.0b3 (review guide)')
    c.setAuthor('Karol Cieślik')
    body=ParagraphStyle('body',fontName='Guide',fontSize=10.5,leading=16,textColor=HexColor('#243748'))
    heading=ParagraphStyle('heading',parent=body,fontName='GuideBold',fontSize=14,leading=20,textColor=HexColor('#087e8b'))
    y=0
    def start(number,title,subtitle):
        nonlocal y
        c.setFillColor(HexColor('#11283e'));c.rect(0,726,596,116,fill=1,stroke=0)
        c.setFillColor(HexColor('#73d6d3'));c.setFont('GuideBold',10)
        c.drawString(42,808,'TPD SPECTRA STUDIO  /  0.11.0b3')
        c.setFillColor(HexColor('#ffffff'));c.setFont('GuideBold',23);c.drawString(42,772,title)
        c.setFont('Guide',10);c.drawString(42,746,subtitle)
        c.setFillColor(HexColor('#657482'));c.setFont('Guide',8)
        c.drawString(42,31,'Karol Cieślik  •  External beta review guide  •  25 October 2026')
        c.drawRightString(553,31,f'{number} / 4')
        y=701
    def p(text,style=body,gap=12):
        nonlocal y
        paragraph=Paragraph(text,style);w,h=paragraph.wrap(510,700)
        assert y-h>55, f'Page overflow: {text[:40]}'
        paragraph.drawOn(c,42,y-h);y-=h+gap
    start(1,'Your first useful result','A five-to-ten-minute starting exercise using clearly labeled synthetic data')
    p('1  Extract and launch',heading)
    p('Download the successful <b>release/external-beta-v0.11.0b3</b> build from GitHub Actions. Extract the entire ZIP into a writable folder. Keep <b>docs</b> and <b>examples</b> beside <b>TPD-Spectra-Studio.exe</b>, then double-click that executable. No Python installation is needed. The unsigned beta must comply with your institution’s software policy.')
    p('2  Open the clean example',heading)
    p('Click <b>Open Example Dataset</b>. Keep <b>first order single peak</b> and open it. You should see 801 points and a named full-trace interval, 50–450 °C. The chooser supplies the documented 1 K/s ramp. These are simulated rates, not measurements.')
    p('3  Read an energy estimate',heading)
    p('Open <b>Kinetic Analysis</b> and select <b>Redhead</b>. Check heating rate <b>1 K/s</b> and assumed prefactor <b>1e13 s⁻¹</b>. The automatic preview should be approximately <b>1.2 eV</b>, within 2.5% of the simulation input. This first-order approximation has no measured confidence interval.')
    p('4  Keep the result',heading)
    p('Click <b>Save labeled result…</b> and give it a meaningful name. Use <b>Report / Export…</b> to select that run and choose a destination. Open the exported PDF. Use <b>Save project…</b> to retain the whole workspace for later.')
    p('<b>Review status:</b> actual GUI screenshots and human display-scaling acceptance are still pending because native capture failed. This guide uses verified control names and numerical checks; it contains no mock interface images.',gap=0)
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
    p('The chooser includes second/fractional order, overlapping populations, noisy/drifting traces, heating-rate series and coverage series. Each CSV has an adjacent JSON with its true parameters and assumptions. Read <b>examples/beta_collection/README.md</b> before interpreting a challenge dataset.')
    c.showPage()
    start(3,'Fit and inspect uncertainty','Simulation, model comparison and a final kinetic fit are separate steps')
    p('Transfer a candidate deliberately',heading)
    p('Select a converged comparison row and choose <b>Use selected model in Kinetic Analysis</b>. This transfers a hypothesis and initial guesses. In Kinetic Analysis, check the method, ramp, order and fit interval, then press <b>Calculate / Fit selected peak</b>. Inspect the residuals and warnings before saving a labeled result.')
    p('Choose a method that fits the question',heading)
    p('<b>Leading edge:</b> apparent slope energy on a rising interval with little coverage change. On the clean reference, try 90–110 °C; expect about 1.2 eV. Do not use the entire peak. This does not assign zero order.<br/><br/><b>Redhead:</b> first-order estimate with an assumed prefactor and linear ramp.<br/><br/><b>Polanyi–Wigner:</b> single-state numerical fitting. Energy, prefactor and amplitude may be poorly identifiable. The fitter normalizes initial coverage to one; absolute coverage is not measured here.')
    p('Try Monte Carlo after comparison',heading)
    p('Return to Modeling, complete a current comparison, choose a seed and replicate count, then <b>Run Monte Carlo</b>. A short run checks the workflow; a repeat with the same seed helps assess reproducibility. Cancel is available. Ranges require 100 successful refits and are not coverage-validated. Zero-order prefactor percentiles are withheld; per-refit depletion brackets are recorded.')
    p('What Monte Carlo means here',heading)
    p('This is <b>parametric refitting</b> with iid Gaussian noise around the lowest-AICc converged reference and its residual noise estimate. It is not microscopic kinetic Monte Carlo or Bayesian MCMC. Rank frequencies describe conditional stability, not probabilities of mechanisms. Drift, correlated noise, calibration and model uncertainty are not included.')
    p('Science before presentation',heading)
    p('Synthetic recovery is a software check. The clean benchmarks use known-order, truth-informed starts; they do not demonstrate robust blind inference. Compare real results with an independent calculation and suitable reference measurements. Keep acquisition conditions, model assumptions and limitations with every exported result.')
    c.showPage()
    start(4,'Save, share and report','Choose what leaves the application and inspect it before sharing')
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
