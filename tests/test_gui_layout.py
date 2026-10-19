"""Structural checks for Phase 2 layout without requiring a display server."""
import inspect

from tpd_spectra.gui import TpdSpectraApp


def test_workspace_has_resizable_panes_and_separate_controls():
    source = inspect.getsource(TpdSpectraApp._build)
    assert 'ttk.Panedwindow' in source
    assert 'self.main_panes.add(controls' in source
    assert 'self.main_panes.add(workspace' in source
    assert 'self.control_tabs.add(self.spectra_tab' in source
    assert 'self.control_tabs.add(self.analysis_tab' in source


def test_existing_controls_remain_in_their_respective_tabs():
    files = inspect.getsource(TpdSpectraApp._files_panel)
    analysis = inspect.getsource(TpdSpectraApp._analysis_panel)
    assert 'self.file_table' in files
    assert 'self._choice("Chart layout"' in files
    assert 'self._slider("Leading edge' in analysis
    assert 'self._advanced_panel()' in analysis
    assert 'self.output_path' in analysis
