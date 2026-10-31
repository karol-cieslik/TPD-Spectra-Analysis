"""Delimited-text discovery and non-destructive import inspection."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import pandas as pd


SUPPORTED_SPECTRUM_SUFFIXES = frozenset({".csv", ".tsv", ".txt"})
DELIMITERS = {",": "comma", ";": "semicolon", "\t": "tab"}

TIME_COLUMNS = ("ms", "Time_ms", "time_ms", "Time (ms)", "Time_s", "Time (s)",
                "Time_min", "Time (min)", "Time", "time")
SIGNAL_COLUMNS = ("DHTA+", "Signal", "signal", "Intensity", "intensity",
                  "Signal (a.u.)", "Intensity (a.u.)")
TEMPERATURE_COLUMNS = (
    "Temperatura", "Temperature", "temperature", "Temp", "temp",
    "Temperature (°C)", "Temperature_C", "Temp_C", "Temperature_K",
    "Temperature (K)", "Temp_K", "Temp (K)",
)


@dataclass(frozen=True)
class SpectrumFilePreview:
    path: Path
    frame: pd.DataFrame
    delimiter: str
    decimal_mark: str
    metadata_rows_skipped: int
    data_records: int
    suggested_columns: dict[str, str | None]
    suggested_units: dict[str, str | None]
    legacy_schema: bool


def supported_spectrum_files(folder: str | Path) -> list[Path]:
    """Return supported delimited text files recursively, case-insensitively."""
    root = Path(folder)
    return sorted((path for path in root.rglob("*")
                   if path.is_file() and path.suffix.lower() in SUPPORTED_SPECTRUM_SUFFIXES),
                  key=lambda path: str(path).casefold())


def _matching_column(columns, aliases):
    by_normalized = {str(column).strip().casefold(): str(column).strip() for column in columns}
    for alias in aliases:
        found = by_normalized.get(alias.casefold())
        if found is not None:
            return found
    return None


def _layout_candidates():
    # Preserve the established instrument export as the first choice, then
    # inspect ordinary headered CSV/TSV layouts without assuming a fixed offset.
    candidates = [(29, ";", ","), (29, ";", "."),
                  (29, ",", "."), (29, "\t", "."), (29, "\t", ","),
                  (0, ";", ","), (0, ";", "."),
                  (0, ",", "."), (0, ",", ","),
                  (0, "\t", "."), (0, "\t", ",")]
    return list(dict.fromkeys(candidates))


def _candidate_score(frame, rows):
    columns = frame.columns
    recognized = sum(_matching_column(columns, aliases) is not None for aliases in
                     (TIME_COLUMNS, SIGNAL_COLUMNS, TEMPERATURE_COLUMNS))
    # For unfamiliar vendor headers, prefer a plausible three-column numeric
    # table with many records. This is only a preview suggestion; the user must
    # map each channel before loading it.
    numeric = 0.0
    if len(columns) >= 3 and not recognized:
        sample = frame.iloc[:20, :3]
        numeric = sum(pd.to_numeric(sample[col], errors="coerce").notna().mean()
                      for col in sample.columns)
    return recognized, int(len(columns) >= 3), numeric, len(frame), -rows


def _suggest_units(time_column, temperature_column, *, legacy_schema=False):
    time_name = (time_column or "").strip().casefold()
    temp_name = (temperature_column or "").strip().casefold()
    if re.search(r"(?:^|[^a-z])ms(?:$|[^a-z])|msec|millisecond|_ms$", time_name):
        time_unit = "ms"
    elif re.search(r"\bmin(?:ute)?s?\b|_min$", time_name):
        time_unit = "min"
    elif re.search(r"\bsec(?:ond)?s?\b|\(s\)|_s$", time_name):
        time_unit = "s"
    elif legacy_schema and time_name == "ms":
        time_unit = "ms"
    else:
        time_unit = None

    if re.search(r"\bkelvin\b|\(k\)|_k$", temp_name):
        temperature_unit = "K"
    elif re.search(r"°\s*c|deg\s*c|celsius|\(°c\)|_c$|\(c\)", temp_name):
        temperature_unit = "degC"
    elif legacy_schema and temp_name == "temperatura":
        temperature_unit = "degC"
    else:
        temperature_unit = None
    return {"time": time_unit, "temperature": temperature_unit}


def inspect_spectrum_file(path: str | Path) -> SpectrumFilePreview:
    """Detect a likely delimited-text layout and expose columns before import.

    This function never applies unit conversions or modifies the source file.
    Generic headers deliberately leave units unselected for user confirmation.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    candidates = []
    errors = []
    for rows, delimiter, decimal in _layout_candidates():
        try:
            frame = pd.read_csv(path, skiprows=rows, sep=delimiter,
                                decimal=decimal, encoding="utf-8-sig")
            frame.columns = [str(column).strip() for column in frame.columns]
            if len(frame.columns) < 2 or frame.empty:
                continue
            candidates.append((_candidate_score(frame, rows), frame, rows, delimiter, decimal))
        except (OSError, UnicodeError, ValueError, pd.errors.ParserError) as exc:
            errors.append(str(exc))
    if not candidates:
        detail = errors[-1] if errors else "no headered table with at least two columns was found"
        raise ValueError(f"Could not preview {path.name} as delimited text: {detail}")
    _, frame, rows, delimiter, decimal = max(candidates, key=lambda item: item[0])
    time_col = _matching_column(frame.columns, TIME_COLUMNS)
    signal_col = _matching_column(frame.columns, SIGNAL_COLUMNS)
    temp_col = _matching_column(frame.columns, TEMPERATURE_COLUMNS)
    legacy = (rows == 29 and time_col == "ms" and signal_col == "DHTA+"
              and temp_col == "Temperatura")
    return SpectrumFilePreview(
        path=path,
        frame=frame.head(12).copy(),
        delimiter=delimiter,
        decimal_mark=decimal,
        metadata_rows_skipped=rows,
        data_records=len(frame),
        suggested_columns={"time": time_col, "signal": signal_col, "temperature": temp_col},
        suggested_units=_suggest_units(time_col, temp_col, legacy_schema=legacy),
        legacy_schema=legacy,
    )
