"""Review detected delimited-text columns and units before adding spectra."""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from .analysis import load_spectrum
from .importer import DELIMITERS, inspect_spectrum_file


class ImportPreviewDialog(tk.Toplevel):
    """Batch preview with per-file column/unit choices and rejected-row counts."""

    def __init__(self, app, paths, on_import):
        super().__init__(app.root)
        self.app = app
        self.on_import = on_import
        self.records = []
        self.current = None
        self.title("Review spectrum import")
        self.geometry("1060x690")
        self.minsize(820, 560)
        self.transient(app.root)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="Import preview", font=("Segoe UI", 15, "bold"),
                  padding=(14, 12, 14, 4)).grid(row=0, column=0, sticky="w")
        ttk.Label(self, text=("Check the detected layout and channel mapping. Confirm units when they are not explicit in the headers. "
                              "No source files are changed."), wraplength=1000,
                  padding=(14, 0, 14, 10)).grid(row=1, column=0, sticky="w")

        body = ttk.Panedwindow(self, orient="horizontal")
        body.grid(row=2, column=0, sticky="nsew", padx=14)
        left = ttk.Frame(body, padding=6)
        right = ttk.Frame(body, padding=6)
        body.add(left, weight=1)
        body.add(right, weight=3)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self.file_table = ttk.Treeview(left, columns=("file", "format", "status"),
                                       show="headings", selectmode="browse", height=16)
        for key, title, width in (("file", "File", 190), ("format", "Detected format", 145),
                                  ("status", "Status", 130)):
            self.file_table.heading(key, text=title)
            self.file_table.column(key, width=width, anchor="w")
        self.file_table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.file_table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_table.configure(yscrollcommand=scrollbar.set)
        self.file_table.bind("<<TreeviewSelect>>", self._select_file)

        right.columnconfigure(1, weight=1)
        ttk.Label(right, text="Detected channels · adjust if needed",
                  font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.column_vars = {key: tk.StringVar(self) for key in ("time", "signal", "temperature")}
        self.column_boxes = {}
        for row, (key, label) in enumerate((("time", "Time column"), ("signal", "Signal column"),
                                            ("temperature", "Temperature column")), start=1):
            ttk.Label(right, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=3)
            box = ttk.Combobox(right, textvariable=self.column_vars[key], state="readonly")
            box.grid(row=row, column=1, sticky="ew", pady=3)
            box.bind("<<ComboboxSelected>>", self._settings_changed)
            self.column_boxes[key] = box
        self.time_unit = tk.StringVar(self)
        self.temperature_unit = tk.StringVar(self)
        ttk.Label(right, text="Source time unit").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=3)
        self.time_box = ttk.Combobox(right, textvariable=self.time_unit,
                                     values=("", "ms", "s", "min"), state="readonly", width=12)
        self.time_box.grid(row=4, column=1, sticky="w", pady=3)
        self.time_box.bind("<<ComboboxSelected>>", self._settings_changed)
        ttk.Label(right, text="Source temperature unit").grid(row=5, column=0, sticky="w", padx=(0, 8), pady=3)
        self.temperature_box = ttk.Combobox(right, textvariable=self.temperature_unit,
                                             values=("", "degC", "K"), state="readonly", width=12)
        self.temperature_box.grid(row=5, column=1, sticky="w", pady=3)
        self.temperature_box.bind("<<ComboboxSelected>>", self._settings_changed)

        self.format_label = ttk.Label(right, text="Detected layout: —", wraplength=760)
        self.format_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 2))
        self.count_label = ttk.Label(right, text="Select a file to preview.", wraplength=760)
        self.count_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.preview_table = ttk.Treeview(right, show="headings", height=12)
        self.preview_table.grid(row=8, column=0, columnspan=2, sticky="nsew")
        right.rowconfigure(8, weight=1)
        self.message = tk.StringVar(self, value="")
        ttk.Label(self, textvariable=self.message, wraplength=1000,
                  padding=(14, 8)).grid(row=3, column=0, sticky="ew")
        buttons = ttk.Frame(self, padding=(14, 0, 14, 12))
        buttons.grid(row=4, column=0, sticky="ew")
        buttons.columnconfigure(0, weight=1)
        self.import_button = ttk.Button(buttons, text="Import ready files", command=self._import_ready)
        self.import_button.grid(row=0, column=1, padx=(8, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).grid(row=0, column=2, padx=(8, 0))

        for index, path in enumerate(map(Path, paths)):
            try:
                preview = inspect_spectrum_file(path)
                options = {
                    "skiprows": preview.metadata_rows_skipped,
                    "delimiter": preview.delimiter,
                    "decimal": preview.decimal_mark,
                    "time_column": preview.suggested_columns["time"],
                    "signal_column": preview.suggested_columns["signal"],
                    "temperature_column": preview.suggested_columns["temperature"],
                    "time_unit": preview.suggested_units["time"],
                    "temperature_unit": preview.suggested_units["temperature"],
                }
                record = {"path": path, "preview": preview, "options": options,
                          "status": "Needs unit choice" if not options["time_unit"] or not options["temperature_unit"] else "Ready",
                          "spec": None, "error": None}
                fmt = f"{DELIMITERS[preview.delimiter]}, decimal {preview.decimal_mark}, skip {preview.metadata_rows_skipped}"
            except Exception as exc:
                record = {"path": path, "preview": None, "options": {}, "status": "Preview failed",
                          "spec": None, "error": str(exc)}
                fmt = "unrecognized"
            self.records.append(record)
            self.file_table.insert("", "end", iid=str(index), values=(path.name, fmt, record["status"]))
        if self.records:
            first = next((i for i, r in enumerate(self.records) if r["preview"] is not None), 0)
            self.file_table.selection_set(str(first))
            self.file_table.focus(str(first))
            self._show_record(first)
        else:
            self.count_label.configure(text="No files were selected.")
            self.import_button.configure(state="disabled")
        self.grab_set()

    def _select_file(self, _event=None):
        selection = self.file_table.selection()
        if selection:
            self._show_record(int(selection[0]))

    def _show_record(self, index):
        self.current = index
        record = self.records[index]
        preview = record["preview"]
        if preview is None:
            self.format_label.configure(text="Detected layout: unavailable")
            self.count_label.configure(text=record["error"] or "Could not inspect this file.")
            self._render_preview(())
            return
        options = record["options"]
        for key, box in self.column_boxes.items():
            box.configure(values=("", *preview.frame.columns))
            self.column_vars[key].set(options.get(f"{key}_column") or "")
        self.time_unit.set(options.get("time_unit") or "")
        self.temperature_unit.set(options.get("temperature_unit") or "")
        self.format_label.configure(text=(f"Detected layout: {DELIMITERS[preview.delimiter]} delimiter; decimal "
                                         f"'{preview.decimal_mark}'; skipped {preview.metadata_rows_skipped} metadata rows. "
                                         f"Columns: {', '.join(map(str, preview.frame.columns))}"))
        self._render_preview(preview.frame.columns)
        self._refresh_counts()

    def _render_preview(self, columns):
        self.preview_table.delete(*self.preview_table.get_children())
        self.preview_table.configure(columns=tuple(str(c) for c in columns))
        for column in columns:
            self.preview_table.heading(str(column), text=str(column))
            self.preview_table.column(str(column), width=145, anchor="w")
        if self.current is None or self.records[self.current]["preview"] is None:
            return
        frame = self.records[self.current]["preview"].frame
        for _, row in frame.iterrows():
            self.preview_table.insert("", "end", values=tuple(str(value) for value in row))

    def _settings_changed(self, _event=None):
        if self.current is None:
            return
        record = self.records[self.current]
        if record["preview"] is None:
            return
        for key in self.column_vars:
            record["options"][f"{key}_column"] = self.column_vars[key].get() or None
        record["options"]["time_unit"] = self.time_unit.get() or None
        record["options"]["temperature_unit"] = self.temperature_unit.get() or None
        record["spec"] = None
        self._refresh_counts()

    def _refresh_counts(self):
        record = self.records[self.current]
        preview = record["preview"]
        options = record["options"]
        missing = [name for name in ("time_column", "signal_column", "temperature_column",
                                     "time_unit", "temperature_unit") if not options.get(name)]
        if missing:
            record["status"] = "Needs mapping/unit"
            record["error"] = "Choose all three channels and both source units before importing."
            self.count_label.configure(text=(f"Preview rows: {preview.data_records}. "
                                              "Choose the missing channels or confirm source units to calculate accepted/rejected counts."))
            self.message.set(record["error"])
            self.file_table.set(str(self.current), "status", record["status"])
            return
        try:
            record["spec"] = load_spectrum(record["path"], **options)
            report = record["spec"].import_report
            rejected = len(report["rejected_records"])
            record["status"] = "Ready" if rejected == 0 else "Ready with rejected rows"
            record["error"] = None
            rejected_examples = [f"row {item['data_record']}: {item['reason']}"
                                for item in report["rejected_records"][:5]]
            rejected_text = ("\nRejected rows: " + "; ".join(rejected_examples)
                             + ("; …" if rejected > 5 else "")) if rejected_examples else ""
            self.count_label.configure(text=(f"Rows: {report['original_data_records']} · accepted: {report['accepted_records']} · "
                                              f"rejected: {rejected} · sorted by time: {report['sorted_by_time']} · "
                                              f"temperature points corrected: {record['spec'].points_temperature_corrected}"
                                              + rejected_text))
            self.message.set("Accepted rows will be imported; rejected rows are excluded and recorded in the import report.")
        except Exception as exc:
            record["spec"] = None
            record["status"] = "Import error"
            record["error"] = str(exc)
            self.count_label.configure(text=f"Could not load with these choices: {exc}")
            self.message.set("Adjust the column mapping or units, then review the preview again.")
        self.file_table.set(str(self.current), "status", record["status"])

    def _import_ready(self):
        ready = [(record["path"], record["spec"]) for record in self.records
                 if record["spec"] is not None and record["status"].startswith("Ready")]
        if not ready:
            self.message.set("No files are ready. Correct the highlighted mappings or units first.")
            return
        paths = [path for path, _ in ready]
        specs = {str(path.resolve()): spec for path, spec in ready}
        self.on_import(paths, specs)
        for index, record in enumerate(self.records):
            if record["path"] not in paths:
                continue
            record["status"] = "Imported"
            record["spec"] = None
            self.file_table.set(str(index), "status", "Imported")
        if all(record["status"] == "Imported" for record in self.records):
            self.destroy()
        else:
            self.message.set("Ready files were added. Correct the remaining rows, then import them or close this preview.")
