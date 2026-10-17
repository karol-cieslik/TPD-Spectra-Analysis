# Public release checklist

This checklist is intentionally conservative: software packaging is not a substitute for rights review or scientific validation.

- [x] Added a scoped MIT license for project-authored software code.
- [ ] Confirm code ownership and separately review redistribution rights for the historical notebook, example spectra, schematic image, and any thesis-derived or third-party material. Do not redistribute assets until rights are clear.
- [x] Omitted experimental spectra, the historical notebook, and images from this code-only repository; review `ASSET-RIGHTS.md` before adding any of them later.
- [ ] Update `CITATION.cff` if the version, author details, or release date change; add a repository URL and DOI only after they exist.
- [ ] Run `python -m pytest -q` and `python scripts/phase6_validation.py` in a clean environment.
- [ ] Build and install a wheel in a clean environment; confirm `tpd-spectra --help` and `tpd-spectra-gui` entry points work.
- [ ] Build both CLI and GUI artifacts on the target Windows runner and test them on a clean Windows machine.
- [ ] Verify the GUI can select one CSV and a folder, writes results to a selected output directory, and displays errors without freezing.
- [ ] Confirm the standalone GUI does not require a separately installed Python interpreter and that Tkinter and scientific dependencies are bundled.
- [ ] Archive the validation outputs and record Python/dependency versions with the release.
- [ ] Review all warnings and known limitations in the README.
- [ ] Do not describe fitted parameters as validated physical constants without independent experimental validation.
