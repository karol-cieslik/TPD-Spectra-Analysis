"""Shared desktop identity. Scientific figures retain their own presentation."""
from pathlib import Path
import sys
import tkinter as tk

NAVY = "#142D3B"
TEAL = "#087E8B"
TEAL_ACTIVE = "#066571"
BACKGROUND = "#F2F5F7"
INK = "#142D3B"
MUTED = "#526575"
ASSETS = Path(__file__).resolve().parent / "assets"


def set_windows_app_identity():
    """Use the application's taskbar identity rather than the Python host's."""
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("KarolCieslik.TPDSpectraStudio.Beta")


def install_window_icons(root):
    # Retain Python references and supply multiple native window-icon sizes.
    root._studio_icons = [brand_image(root, size)
                          for size in (16, 32, 48, 64, 128, 256)]
    root.iconphoto(True, *root._studio_icons)


def brand_image(parent, size=48):
    # Python resolves filesystem paths, including Unicode/package extraction paths;
    # Tcl receives image bytes rather than parsing a second filesystem path.
    return tk.PhotoImage(master=parent, data=(ASSETS / f"studio-{size}.png").read_bytes(), format="png")
