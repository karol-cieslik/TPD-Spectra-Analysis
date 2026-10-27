"""Exercise the submitted default-example workflow with a real Tk interpreter."""
from pathlib import Path
import time
import numpy as np
import pytest
from tpd_spectra.workflow_gui import WorkflowApp


def wait_job(app, root, timeout=60):
    deadline = time.monotonic() + timeout
    while app.job_busy and time.monotonic() < deadline:
        root.update()
        time.sleep(.01)
    assert not app.job_busy, 'background calculation timed out'


def assert_raw(figure, dataset):
    lines = [line for ax in figure.axes for line in ax.lines if line.get_label() == 'Original measured spectrum']
    assert lines
    np.testing.assert_array_equal(lines[0].get_ydata(), dataset.spectrum.signal)


def test_no_region_keeps_raw_trace_across_all_stages(root, tmp_path):
    # A same-named arbitrary import must not receive assumed physical regions.
    source = Path(__file__).resolve().parents[1] / 'examples/synthetic_two_peak_demo.csv'
    imported = tmp_path / source.name
    imported.write_bytes(source.read_bytes())
    app = WorkflowApp(root)
    app._load_paths([imported])
    assert app.project.active_region is None
    dataset = app.project.datasets[app.project.active_dataset]
    for index in range(3):
        app.stages.select(index)
        root.update()
        assert_raw(app.modeling_panel.fig, dataset)
        assert_raw(app.result_figure, dataset)
    assert 'Add peak' in app.modeling_panel.notes.get('1.0', 'end')
    app.modeling_panel.simulate()
    app.modeling_panel.monte_carlo()
    assert not app.job_busy
    assert_raw(app.modeling_panel.fig, dataset)


def test_default_example_simulate_compare_mc_and_analysis(root):
    app = WorkflowApp(root)
    app.open_default_demo()
    dataset, region = app.project.context()
    assert Path(dataset.path).name == 'synthetic_two_peak_demo.csv'
    assert (region.lower, region.upper) == (70., 210.)
    app._load_paths([Path(dataset.path)])
    assert len(app.project.regions) == 1
    panel = app.modeling_panel
    # A short, single-hypothesis run tests real dispatch, fitting and seeded MC.
    for key in ('zero', 'second', 'fractional', 'multistart'):
        panel.variables[key].set(False)
    panel.variables['replicates'].set('2')
    panel.variables['max_nfev'].set('150')
    app.stages.select(1)
    root.update()
    panel.simulate()
    wait_job(app, root)
    assert 'simulation' in panel.session()
    panel.compare()
    wait_job(app, root)
    assert panel.session()['comparison']['candidates'][0]['error'] is None
    panel.monte_carlo()
    assert_raw(panel.fig, dataset)
    wait_job(app, root)
    assert panel.session()['monte_carlo']['result']['replicates_completed'] == 2
    assert_raw(panel.fig, dataset)
    panel.table.selection_set('0')
    panel.transfer()
    app.calculate_selected()
    wait_job(app, root)
    assert app.displayed_result is not None
    assert_raw(app.result_figure, dataset)
    app.method.set('Leading edge')
    app.refresh_method()
    app.project.method_settings('Leading edge').update(lower=110., upper=140.)
    app.refresh_method()
    app.preview_selected()
    assert_raw(app.result_figure, dataset)


def test_model_worker_failure_preserves_simulation_and_raw(root):
    app = WorkflowApp(root)
    app.open_default_demo()
    panel = app.modeling_panel
    panel.simulate()
    wait_job(app, root)
    previous = panel.session()['simulation']
    def fail():
        raise ValueError('test failure')
    app.start_job(fail, lambda _: pytest.fail('failed calculation accepted'))
    wait_job(app, root)
    assert panel.session()['simulation'] is previous
    assert 'test failure' in app.status.get()
    assert_raw(panel.fig, app.project.context()[0])
