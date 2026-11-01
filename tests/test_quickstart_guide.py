"""Guided first-run exercises and offline source-faithful worked examples."""

from pathlib import Path

from tpd_spectra.quickstart_dialog import PAGES
from tpd_spectra.beta_resources import resource


DEMO = Path(__file__).resolve().parents[1] / 'examples/synthetic_two_peak_demo.csv'


def test_five_exercises_explain_actual_methods_and_limits():
    assert len(PAGES) == 5
    titles = [title for title, _ in PAGES]
    assert titles == ['First result', 'Choose a peak', 'Simulate and compare',
                      'Monte Carlo', 'Overlapping and export']
    content = '\n'.join(text for _, text in PAGES)
    for required in ('1e13', '1.2 eV', '70–210', 'Simulate parameters',
                     'Compare models', '42', '100 successful', '1.185',
                     '1.265', '1.345', 'Save project'):
        assert required in content
    assert 'mechanism probabilities' in content or 'mechanism probabilities' in resource(
        'docs/beta/WORKED_EXAMPLES.html').read_text(encoding='utf-8')


def test_full_html_is_offline_and_in_package_path():
    html = resource('docs/beta/WORKED_EXAMPLES.html').read_text(encoding='utf-8')
    assert '<html' in html.lower()
    assert 'first result' in html.lower()
    assert 'Run Monte Carlo' in html
    assert 'Fit Multiple Peaks' in html
    assert '<style>' in html
    # No remote fonts, scripts or screenshots are required for rendering.
    assert 'src="http' not in html


def test_quickstart_tabs_and_browser_open_are_nonmutating(root, monkeypatch):
    from tpd_spectra.workflow_gui import WorkflowApp
    import webbrowser

    app = WorkflowApp(root)
    app._load_paths([DEMO])
    before = app.project.snapshot('Redhead')
    dialog = app.workflow_help()
    root.update()
    assert [dialog.tabs.tab(t, 'text') for t in dialog.tabs.tabs()] == [name for name, _ in PAGES]
    opened = []
    monkeypatch.setattr(webbrowser, 'open', lambda uri: opened.append(uri) or True)
    app.open_worked_examples()
    assert len(opened) == 1 and opened[0].startswith('file:')
    assert 'WORKED_EXAMPLES.html' in opened[0]
    assert app.project.snapshot('Redhead') == before
    assert not app.job_busy
    dialog.window.destroy()
