"""Desktop GUI entry point and bundled batch-analysis dispatcher."""
import sys


def restore_redirected_output():
    """Windowed PyInstaller builds clear sys.stdout even when a parent supplies pipes."""
    import os
    for name, standard_handle in (("stdout", -11), ("stderr", -12)):
        if getattr(sys, name) is not None:
            continue
        stream = None
        if sys.platform == "win32":
            import ctypes
            import msvcrt
            get_handle = ctypes.windll.kernel32.GetStdHandle
            get_handle.argtypes = [ctypes.c_ulong]
            get_handle.restype = ctypes.c_void_p
            handle = get_handle(standard_handle & 0xffffffff)
            if handle not in (None, ctypes.c_void_p(-1).value):
                try:
                    descriptor = msvcrt.open_osfhandle(handle, os.O_WRONLY | os.O_BINARY)
                    stream = os.fdopen(descriptor, "w", buffering=1, encoding="utf-8", errors="replace", closefd=False)
                except OSError:
                    pass
        setattr(sys, name, stream or open(os.devnull, "w", encoding="utf-8"))

if __name__ == "__main__":
    if sys.argv[1:2] in (["--tpd-smoke-gui"], ["--tpd-smoke-workflow"]):
        restore_redirected_output()
        try:
            if sys.argv[1] == '--tpd-smoke-workflow':
                from tpd_spectra.workflow_smoke import main as smoke_main
            else:
                from tpd_spectra.desktop_smoke import main as smoke_main
            code = smoke_main(*sys.argv[2:])
        except Exception:
            import traceback
            traceback.print_exc()
            code = 1
        raise SystemExit(code)
    if sys.argv[1:2] == ["--tpd-cli"]:
        restore_redirected_output()
        from tpd_spectra.cli import main as cli_main
        raise SystemExit(cli_main(sys.argv[2:]))
    if sys.argv[1:2] == ['--classic']:
        from tpd_spectra.gui import main as gui_main
    else:
        from tpd_spectra.workflow_gui import main as gui_main
    raise SystemExit(gui_main())
