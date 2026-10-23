"""Real desktop layout/resource checks for the shipped identity."""
from PIL import Image
import pytest
from tpd_spectra.branding import ASSETS
from tpd_spectra.gui import TpdSpectraApp


def test_windows_icon_contains_small_and_high_dpi_sizes():
    with Image.open(ASSETS / "studio.ico") as icon:
        assert {(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)} <= icon.ico.sizes()
        for size in icon.ico.sizes():
            rendered = icon.ico.getimage(size)
            assert rendered.mode == "RGBA"
            assert rendered.getextrema()[3] == (0, 255)


@pytest.mark.parametrize("scaling,width,height", [(1.333, 1040, 740), (2.0, 1440, 900)])
def test_branded_workspace_keeps_primary_actions_accessible(root, scaling, width, height):
    root.tk.call("tk", "scaling", scaling)
    app = TpdSpectraApp(root)
    root.state("normal")
    root.geometry(f"{width}x{height}")
    root.update()
    assert len(root._studio_icons) == 6
    for group in (app.import_actions, app.analysis_actions):
        assert group.winfo_ismapped()
        assert group.winfo_rootx() >= root.winfo_rootx()
        assert group.winfo_rootx() + group.winfo_width() <= root.winfo_rootx() + root.winfo_width()
        for button in group.winfo_children():
            assert button.winfo_width() >= button.winfo_reqwidth()
    assert app.run_button.winfo_ismapped()
    assert app.canvas.get_tk_widget().winfo_height() > 150
    # Exercise reflow without changing font settings or dropping an action.
    app.toolbar.pack_configure(fill="none", anchor="w")
    app.toolbar.grid_propagate(False)
    app.toolbar.configure(width=max(app.import_actions.winfo_reqwidth(), app.analysis_actions.winfo_reqwidth()) + 40,
                          height=150)
    root.update()
    assert app.analysis_actions.grid_info()["row"] == 1
    assert app.run_button.winfo_ismapped()
