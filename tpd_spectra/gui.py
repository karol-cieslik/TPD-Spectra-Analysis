"""Optional Tkinter desktop front end for the TPD/TDS batch CLI.

Tkinter is part of many standard Python installations. The GUI deliberately
reuses the existing CLI pipeline so GUI and command-line results stay aligned.
"""
from __future__ import annotations

import contextlib
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from . import __version__


def build_cli_arguments(settings: dict[str, object]) -> list[str]:
    """Validate GUI settings and translate them into CLI arguments.

    Kept independent of Tk so it can be unit-tested on headless systems.
    """
    input_path = str(settings.get("input_path", "")).strip()
    output_path = str(settings.get("output_path", "")).strip()
    if not input_path:
        raise ValueError("Choose an input CSV file or folder.")
    if not Path(input_path).exists():
        raise ValueError(f"Input path does not exist: {input_path}")
    if not output_path:
        raise ValueError("Choose an output folder.")

    def number(key: str, label: str) -> float:
        try:
            value = float(settings[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{label} must be a number.") from exc
        return value

    edge_low = number("leading_low", "Leading-edge lower limit")
    edge_high = number("leading_high", "Leading-edge upper limit")
    red_low = number("redhead_low", "Redhead lower limit")
    red_high = number("redhead_high", "Redhead upper limit")
    prefactor = number("prefactor", "Redhead prefactor")
    initial_energy = number("kinetic_initial_energy", "Initial kinetic energy")
    initial_prefactor = number("kinetic_initial_prefactor", "Initial kinetic prefactor")
    try:
        window = int(str(settings["window"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Smoothing window must be a positive integer.") from exc

    if edge_low >= edge_high or red_low >= red_high:
        raise ValueError("Each temperature interval must have lower limit < upper limit.")
    if prefactor <= 0 or initial_energy <= 0 or initial_prefactor <= 0:
        raise ValueError("Prefactors and initial kinetic energy must be positive.")
    if window < 1:
        raise ValueError("Smoothing window must be at least 1.")
    filter_method = str(settings.get("filter", "median"))
    if filter_method not in {"median", "mean", "none"}:
        raise ValueError("Filter must be median, mean, or none.")

    args = [
        input_path, "--output", output_path,
        "--leading-edge", str(edge_low), str(edge_high),
        "--redhead-region", str(red_low), str(red_high),
        "--prefactor", str(prefactor), "--window", str(window),
        "--filter", filter_method, "--max-time-min", str(number("max_time_min", "Maximum time")),
    ]
    if bool(settings.get("kinetic_fit", False)):
        model = str(settings.get("kinetic_model", "single"))
        order = str(settings.get("kinetic_order", "1"))
        if model not in {"single", "two-state", "compare"}:
            raise ValueError("Choose a valid kinetic model.")
        if order not in {"0", "1", "2", "fit"}:
            raise ValueError("Reaction order must be 0, 1, 2, or fit.")
        args.extend([
            "--kinetic-fit", "--kinetic-model", model, "--kinetic-order", order,
            "--kinetic-initial-energy", str(initial_energy),
            "--kinetic-initial-prefactor", str(initial_prefactor),
        ])
        if bool(settings.get("kinetic_no_baseline", False)):
            args.append("--kinetic-no-baseline")
    return args


class _QueueWriter:
    def __init__(self, output_queue: queue.Queue[str], prefix: str = "") -> None:
        self.output_queue = output_queue
        self.prefix = prefix
        self.pending = ""

    def write(self, value: str) -> int:
        self.pending += value
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            if line.strip():
                self.output_queue.put(self.prefix + line)
        return len(value)

    def flush(self) -> None:
        if self.pending.strip():
            self.output_queue.put(self.prefix + self.pending)
        self.pending = ""


class TpdSpectraApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title(f"TPD Spectra Analysis {__version__}")
        root.geometry("850x760")
        root.minsize(720, 640)
        self.messages: queue.Queue[str] = queue.Queue()
        self.running = False

        self.vars: dict[str, tk.Variable] = {
            "input_path": tk.StringVar(value="input"),
            "output_path": tk.StringVar(value="output"),
            "leading_low": tk.StringVar(value="130"),
            "leading_high": tk.StringVar(value="170"),
            "redhead_low": tk.StringVar(value="230"),
            "redhead_high": tk.StringVar(value="400"),
            "prefactor": tk.StringVar(value="1e20"),
            "window": tk.StringVar(value="10"),
            "filter": tk.StringVar(value="median"),
            "max_time_min": tk.StringVar(value="10"),
            "kinetic_fit": tk.BooleanVar(value=False),
            "kinetic_model": tk.StringVar(value="single"),
            "kinetic_order": tk.StringVar(value="1"),
            "kinetic_initial_energy": tk.StringVar(value="1.0"),
            "kinetic_initial_prefactor": tk.StringVar(value="1e13"),
            "kinetic_no_baseline": tk.BooleanVar(value=False),
        }
        self._build_ui()
        self.root.after(100, self._drain_messages)

    def _entry(self, parent: ttk.Frame, label: str, key: str, row: int, col: int,
               width: int = 13) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=col * 2, sticky="w", padx=(4, 6), pady=5)
        ttk.Entry(parent, textvariable=self.vars[key], width=width).grid(
            row=row, column=col * 2 + 1, sticky="ew", padx=(0, 12), pady=5)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="TPD Spectra Analysis", font=("TkDefaultFont", 17, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Batch analysis and optional Polanyi–Wigner kinetic fitting").pack(anchor="w", pady=(0, 12))

        paths = ttk.LabelFrame(outer, text="Input and output", padding=8)
        paths.pack(fill="x", pady=(0, 10))
        ttk.Label(paths, text="Input CSV or folder").grid(row=0, column=0, sticky="w", padx=4, pady=5)
        ttk.Entry(paths, textvariable=self.vars["input_path"]).grid(row=0, column=1, sticky="ew", padx=4, pady=5)
        ttk.Button(paths, text="Choose file…", command=self._choose_file).grid(row=0, column=2, padx=4, pady=5)
        ttk.Button(paths, text="Choose folder…", command=self._choose_input_folder).grid(row=0, column=3, padx=4, pady=5)
        ttk.Label(paths, text="Output folder").grid(row=1, column=0, sticky="w", padx=4, pady=5)
        ttk.Entry(paths, textvariable=self.vars["output_path"]).grid(row=1, column=1, sticky="ew", padx=4, pady=5)
        ttk.Button(paths, text="Browse…", command=self._choose_output_folder).grid(row=1, column=2, padx=4, pady=5)
        paths.columnconfigure(1, weight=1)

        classic = ttk.LabelFrame(outer, text="Classical analysis settings", padding=8)
        classic.pack(fill="x", pady=(0, 10))
        self._entry(classic, "Leading edge (°C): low", "leading_low", 0, 0)
        self._entry(classic, "high", "leading_high", 0, 1)
        self._entry(classic, "Redhead range (°C): low", "redhead_low", 1, 0)
        self._entry(classic, "high", "redhead_high", 1, 1)
        self._entry(classic, "Redhead prefactor (s⁻¹)", "prefactor", 2, 0)
        self._entry(classic, "Smoothing window", "window", 2, 1)
        self._entry(classic, "Heating fit cutoff (min; -1 = none)", "max_time_min", 3, 0)
        ttk.Label(classic, text="Smoothing filter").grid(row=3, column=2, sticky="w", padx=4, pady=5)
        ttk.Combobox(classic, textvariable=self.vars["filter"], values=("median", "mean", "none"),
                     state="readonly", width=10).grid(row=3, column=3, sticky="w", padx=4, pady=5)
        for col in (1, 3):
            classic.columnconfigure(col, weight=1)

        kinetic = ttk.LabelFrame(outer, text="Optional numerical kinetics", padding=8)
        kinetic.pack(fill="x", pady=(0, 10))
        ttk.Checkbutton(kinetic, text="Enable Polanyi–Wigner kinetic fitting", variable=self.vars["kinetic_fit"],
                        command=self._toggle_kinetic).grid(row=0, column=0, columnspan=4, sticky="w", padx=4, pady=4)
        ttk.Label(kinetic, text="Model").grid(row=1, column=0, sticky="w", padx=4, pady=5)
        self.model_combo = ttk.Combobox(kinetic, textvariable=self.vars["kinetic_model"],
                                        values=("single", "two-state", "compare"), state="disabled", width=12)
        self.model_combo.grid(row=1, column=1, sticky="w", padx=4, pady=5)
        ttk.Label(kinetic, text="Reaction order").grid(row=1, column=2, sticky="w", padx=4, pady=5)
        self.order_combo = ttk.Combobox(kinetic, textvariable=self.vars["kinetic_order"],
                                        values=("0", "1", "2", "fit"), state="disabled", width=8)
        self.order_combo.grid(row=1, column=3, sticky="w", padx=4, pady=5)
        self._entry(kinetic, "Initial energy (eV)", "kinetic_initial_energy", 2, 0)
        self._entry(kinetic, "Initial prefactor (s⁻¹)", "kinetic_initial_prefactor", 2, 1)
        self.no_baseline_check = ttk.Checkbutton(kinetic, text="Fix fitted baseline at zero",
                                                 variable=self.vars["kinetic_no_baseline"], state="disabled")
        self.no_baseline_check.grid(row=3, column=0, columnspan=3, sticky="w", padx=4, pady=4)
        for col in (1, 3):
            kinetic.columnconfigure(col, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(0, 8))
        self.run_button = ttk.Button(actions, text="Run analysis", command=self._start)
        self.run_button.pack(side="left")
        self.progress = ttk.Progressbar(actions, mode="indeterminate", length=180)
        self.progress.pack(side="left", padx=12)
        ttk.Button(actions, text="Open output folder", command=self._open_output).pack(side="right")

        log_frame = ttk.LabelFrame(outer, text="Run log", padding=6)
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(log_frame, height=12, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._append_log("Ready. Review analysis warnings and fit diagnostics before interpreting parameters physically.")

    def _toggle_kinetic(self) -> None:
        enabled = bool(self.vars["kinetic_fit"].get())
        state = "readonly" if enabled else "disabled"
        self.model_combo.configure(state=state)
        self.order_combo.configure(state=state)
        self.no_baseline_check.configure(state="normal" if enabled else "disabled")

    def _choose_file(self) -> None:
        path = filedialog.askopenfilename(title="Select a spectrum CSV", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if path:
            self.vars["input_path"].set(path)

    def _choose_input_folder(self) -> None:
        path = filedialog.askdirectory(title="Select input folder")
        if path:
            self.vars["input_path"].set(path)

    def _choose_output_folder(self) -> None:
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.vars["output_path"].set(path)

    def _settings(self) -> dict[str, object]:
        return {key: variable.get() for key, variable in self.vars.items()}

    def _start(self) -> None:
        if self.running:
            return
        try:
            args = build_cli_arguments(self._settings())
        except ValueError as exc:
            messagebox.showerror("Check settings", str(exc), parent=self.root)
            return
        self.running = True
        self.run_button.configure(state="disabled")
        self.progress.start(10)
        self._append_log("\n$ python -m tpd_spectra " + " ".join(args))
        thread = threading.Thread(target=self._worker, args=(args,), daemon=True)
        thread.start()

    def _worker(self, args: list[str]) -> None:
        from .cli import main as cli_main
        out = _QueueWriter(self.messages)
        err = _QueueWriter(self.messages, prefix="[stderr] ")
        code = 0
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = int(cli_main(args) or 0)
                except SystemExit as exc:
                    code = int(exc.code or 0) if isinstance(exc.code, (int, type(None))) else 2
                except Exception as exc:  # keep the GUI responsive on unexpected failures
                    print(f"Unhandled error: {exc}", file=err)
                    code = 1
        finally:
            out.flush()
            err.flush()
            self.messages.put(f"__DONE__:{code}")

    def _drain_messages(self) -> None:
        try:
            while True:
                message = self.messages.get_nowait()
                if message.startswith("__DONE__:"):
                    code = int(message.split(":", 1)[1])
                    self.running = False
                    self.progress.stop()
                    self.run_button.configure(state="normal")
                    self._append_log(f"\nFinished with exit code {code}. Output: {self.vars['output_path'].get()}")
                else:
                    self._append_log(message)
        except queue.Empty:
            pass
        self.root.after(100, self._drain_messages)

    def _append_log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _open_output(self) -> None:
        path = Path(str(self.vars["output_path"].get())).expanduser()
        if not path.exists():
            messagebox.showinfo("Output folder", "The output folder will be created when analysis runs.", parent=self.root)
            return
        try:
            import os
            import subprocess
            import sys
            if sys.platform == "win32":
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Cannot open folder", str(exc), parent=self.root)


def main() -> int:
    root = tk.Tk()
    TpdSpectraApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
