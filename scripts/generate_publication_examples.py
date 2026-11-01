"""Regenerate instrument-compatible *views* of licensed publication spectra.

No pixel gaps are interpolated. Source K and signal values are preserved;
for a figure, the time axis is an explicitly artificial nominal-ramp coordinate.
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "examples" / "publication_data"


def transform(row):
    original = BASE / row["source_csv"]
    with original.open(newline="", encoding="utf-8-sig") as stream:
        raw = list(csv.DictReader(stream))
    t_key, y_key, time_key = (row["source_temperature_column"],
                              row["source_signal_column"], row["source_time_column"])
    samples = []
    for record in raw:
        try:
            temp = float(record[t_key])
            signal = float(record[y_key])
            source_time = float(record[time_key]) if time_key else None
        except (ValueError, TypeError):
            continue  # Missing digitized graphical column; never fill it.
        if not (math.isfinite(temp) and math.isfinite(signal) and
                (source_time is None or math.isfinite(source_time))):
            continue
        samples.append((temp, signal, source_time))
    samples.sort(key=lambda record: record[2] if time_key else record[0])
    kept, seen = [], set()
    for sample in samples:
        key = sample[2] if time_key else sample[0]
        if key in seen:
            continue  # Original vector paths can contain a repeated abscissa.
        seen.add(key)
        kept.append(sample)
    if len(kept) < 3:
        raise ValueError(f"Not enough usable points in {original}")
    if len(raw) - len(kept) != row["omitted_records"]:
        raise ValueError(f"Source point count changed for {original}; review provenance")
    first_temp, _, first_time = kept[0]
    output = []
    for temp, signal, observed_time in kept:
        if time_key:
            ms = 1000 * (observed_time - first_time)
        else:
            beta = row["beta_K_s"]
            if not beta or beta <= 0:
                raise ValueError("A digitized trace needs a documented nominal ramp")
            ms = 1000 * (temp - first_temp) / beta
        output.append((ms, signal, temp - 273.15))
    if any(b[0] <= a[0] for a, b in zip(output, output[1:])):
        raise ValueError(f"Non-monotonic compatible time axis for {original}")
    return output


def regenerate():
    catalog = json.loads((BASE / "catalog.json").read_text(encoding="utf-8"))
    for row in catalog:
        output = transform(row)
        with (BASE / row["file"]).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("ms", "DHTA+", "Temperatura"))
            writer.writerows(output)


if __name__ == "__main__":
    regenerate()
