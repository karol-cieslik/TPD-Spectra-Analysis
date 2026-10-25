"""Immutable reviewed runs, exclusive output directories and cancellable execution."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import uuid

from .identity import build_identity


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def proposed_run_folder(parent):
    parent = Path(parent).expanduser().resolve()
    return parent / (datetime.now().strftime("run-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8])


@dataclass(frozen=True)
class RunPlan:
    arguments: tuple[str, ...]
    settings_json: str
    inputs: tuple[tuple[str, str], ...]
    output: Path
    preview: bool = False

    @classmethod
    def create(cls, settings, arguments, *, preview=False):
        paths = tuple(str(Path(p).resolve()) for p in settings["input_files"])
        if len({Path(p).name.casefold() for p in paths}) != len(paths):
            raise ValueError("Included files have identical names. Run them separately to avoid ambiguous tables and diagnostic filenames.")
        output = Path(settings["output_path"]).expanduser().resolve()
        if output.exists():
            raise ValueError("The proposed run folder already exists. Choose a new run folder; existing results are never overwritten.")
        if not output.parent.is_dir():
            raise ValueError("Choose an existing parent folder for the results.")
        if not os.access(output.parent, os.W_OK):
            raise ValueError("The selected parent folder is not writable.")
        return cls(tuple(arguments), json.dumps(settings, sort_keys=True),
                   tuple((p, sha256(p)) for p in paths), output, preview)


def write_record(plan, state, **extra):
    payload = {"schema_version": 1, "state": state, "preview": plan.preview,
               "updated_utc": datetime.now(timezone.utc).isoformat(),
               "software": build_identity(), "settings": json.loads(plan.settings_json),
               "inputs": [{"path": p, "sha256": digest} for p, digest in plan.inputs],
               **extra}
    temporary = plan.output / "run_status.json.tmp"
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(plan.output / "run_status.json")


def result_state(folder, returncode):
    manifest = folder / "analysis_project.json"
    if not manifest.exists():
        return "failed"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("failed_files"):
        return "partially failed" if data.get("successful_files") else "failed"
    if returncode:
        return "failed"
    if (folder / "analysis_warnings.csv").exists():
        return "completed with warnings"
    return "completed"


def execute(plan, messages, cancel, *, command_prefix=None):
    """Own the child until it exits; stream logs and persist terminal status."""
    process = None
    created = False
    finished = threading.Event()
    try:
        for path, digest in plan.inputs:
            if sha256(path) != digest:
                raise ValueError(f"Input changed since review: {Path(path).name}. Review the analysis again.")
        if cancel.is_set():
            messages.put(("finished", "cancelled"))
            return
        plan.output.mkdir(exist_ok=False)
        created = True
        write_record(plan, "running")
        prefix = command_prefix or ([sys.executable, "--tpd-cli"] if getattr(sys, "frozen", False)
                                    else [sys.executable, "-u", "-m", "tpd_spectra"])
        environment = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        with (plan.output / "run.log").open("w", encoding="utf-8", buffering=1) as log:
            process = subprocess.Popen([*prefix, *plan.arguments], stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                       errors="replace", env=environment, creationflags=flags)

            def watch_cancel():
                while not finished.wait(.1):
                    if cancel.is_set():
                        if process.poll() is None:
                            try:
                                process.terminate()
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                process.kill()
                            except ProcessLookupError:
                                pass
                        return

            watcher = threading.Thread(target=watch_cancel, daemon=True)
            watcher.start()
            for line in process.stdout:
                log.write(line)
                messages.put(("log", line.rstrip()))
            returncode = process.wait()
            finished.set()
            watcher.join(timeout=6)
        state = "cancelled" if cancel.is_set() else result_state(plan.output, returncode)
        write_record(plan, state, returncode=returncode)
        messages.put(("finished", state))
    except Exception as exc:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        if created:
            try:
                write_record(plan, "failed", error=str(exc))
            except OSError:
                pass
        messages.put(("error", str(exc)))
    finally:
        finished.set()
