# Synthetic demo — for interface testing only

`synthetic_two_peak_demo.csv` is an illustrative generated CSV with 151 rows, a strictly linear 1 K/s temperature ramp, and two artificial Gaussian peaks plus constant offset.

Columns: `Time_ms` (milliseconds), `Signal` (arbitrary units), `Temperature` (°C).

**Important:** This is **not** a Polanyi–Wigner simulated desorption trace and has no meaningful reference activation energy or reaction order. Use it to test CSV import, overlays, selection, peak windows, graph exporting, and error handling **only**, not to validate kinetic fitting.

Try a peak-search interval of 150–270 °C. For scientific validation use a documented physical-model synthetic spectrum with known parameters and experimental spectra with known provenance.

This CSV is provided in the repository branch. It is **not bundled** with the preexisting Windows build artifact: download it separately.
