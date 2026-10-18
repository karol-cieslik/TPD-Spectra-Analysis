"""Desktop GUI entry point and bundled batch-analysis dispatcher."""
import sys

if __name__ == "__main__":
    if sys.argv[1:2] == ["--tpd-cli"]:
        from tpd_spectra.cli import main as cli_main
        raise SystemExit(cli_main(sys.argv[2:]))
    from tpd_spectra.gui import main as gui_main
    raise SystemExit(gui_main())
