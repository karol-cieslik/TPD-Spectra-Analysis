"""Entry point used by PyInstaller for the standalone TPD Spectra executable."""
from tpd_spectra.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
