# Windows verification notes

The source suite includes real Tk widget assertions; these must not be skipped
on Windows. The frozen executable is checked separately by
`scripts/verify_windows_build.py`, including demo analysis, dialogs, an Explorer
fit, a two-replicate Monte Carlo packaging smoke and PNG/SVG export. Two
replicates test execution and export only, not uncertainty accuracy.

## Output capture and Tcl

Runs 39803320051 and 39803738329 failed while creating a Tcl interpreter,
before the relevant GUI assertions: `init.tcl` could not be read, with the
message `No error`. Other Tk tests in the same runs passed. The focused local
54-test suite passed with `--capture=sys` after the default file-descriptor
capture had produced intermittent initialization failures.

The pytest configuration now captures Python streams without replacing OS
descriptors. This preserves the existing assertions and their Windows failure
policy; it does not retry, xfail or skip Tk failures. The same capture interaction
is documented in [ttkbootstrap's test configuration](https://github.com/israel-dryer/ttkbootstrap/blob/master/pyproject.toml).
See [pytest's capture modes](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html).

The local bundled Python needs explicitly supplied Tcl/Tk script locations.
Local runs with borrowed runtime scripts are development evidence only. The
Windows workflow installs Python with its own runtime and clears external
Tcl/Python overrides when testing the frozen executable.

Each downloadable candidate must be linked to its exact successful workflow
run and source commit in PR #5. A passing source suite alone does not verify
the packaged app. Automated widget checks do not replace manual checks of
screen scaling, keyboard use, layouts or scientific interpretation.
