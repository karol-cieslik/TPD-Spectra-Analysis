"""Explicit dataset/peak/method state, independent of Tk and numerical solvers."""
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4
import hashlib
import json
import numpy as np

from .analysis import load_spectrum
from .run_session import sha256

METHODS = ("Leading edge", "Redhead", "Polanyi–Wigner")
STAGES = ("Spectra & Preparation", "Modeling & Order Identification", "Kinetic Analysis")


@dataclass
class Dataset:
    id: str
    path: str
    digest: str
    spectrum: object
    processing: dict = field(default_factory=lambda: {"smoothing": "none", "window": 1, "baseline": 0.0})


@dataclass
class Region:
    id: str
    dataset_id: str
    label: str
    lower: float
    upper: float


class WorkflowProject:
    def __init__(self):
        self.datasets = {}
        self.regions = {}
        self.settings = {}
        self.runs = {}
        self.modeling = {}
        self.active_dataset = None
        self.active_region = None

    def add_dataset(self, path, spectrum=None):
        path = str(Path(path).resolve())
        for item in self.datasets.values():
            if item.path == path:
                return item
        spec = spectrum or load_spectrum(path)
        for array in (spec.time_min, spec.temperature_c, spec.temperature_clean_c, spec.signal):
            array.setflags(write=False)
        item = Dataset(uuid4().hex, path, sha256(path), spec)
        self.datasets[item.id] = item
        self.select_dataset(item.id)
        return item

    def select_dataset(self, dataset_id):
        if dataset_id not in self.datasets:
            raise ValueError("Select an imported dataset")
        self.active_dataset = dataset_id
        if self.active_region not in self.regions or self.regions[self.active_region].dataset_id != dataset_id:
            self.active_region = next((r.id for r in self.regions.values() if r.dataset_id == dataset_id), None)

    def add_region(self, label, lower, upper):
        self.validate_bounds(self.active_dataset, lower, upper)
        count = sum(r.dataset_id == self.active_dataset for r in self.regions.values())
        region = Region(uuid4().hex, self.active_dataset, label.strip() or f"Peak {count + 1}", float(lower), float(upper))
        self.regions[region.id] = region
        self.active_region = region.id
        return region

    def validate_bounds(self, dataset_id, lower, upper):
        if dataset_id not in self.datasets:
            raise ValueError("Import and select a spectrum first")
        lower, upper = float(lower), float(upper)
        temperature = self.datasets[dataset_id].spectrum.temperature_clean_c
        if not np.isfinite([lower, upper]).all() or lower >= upper:
            raise ValueError("Peak bounds must be finite and increasing")
        if lower < temperature.min() or upper > temperature.max():
            raise ValueError("Peak bounds must lie within the imported temperature range")
        if ((temperature >= lower) & (temperature <= upper)).sum() < 3:
            raise ValueError("A region needs at least three measured points")

    def update_region(self, region_id, label, lower, upper):
        region = self.regions[region_id]
        self.validate_bounds(region.dataset_id, lower, upper)
        region.label, region.lower, region.upper = label.strip() or region.label, float(lower), float(upper)

    def context(self):
        if self.active_region not in self.regions:
            raise ValueError("Define and select a peak region first")
        region = self.regions[self.active_region]
        if region.dataset_id != self.active_dataset:
            raise ValueError("The selected peak belongs to another dataset")
        return self.datasets[self.active_dataset], region

    def key(self, method):
        dataset, region = self.context()
        if method not in METHODS:
            raise ValueError("Unsupported analysis method")
        return f"{dataset.id}/{region.id}/{method}"

    def method_settings(self, method):
        key = self.key(method)
        if key not in self.settings:
            _, region = self.context()
            self.settings[key] = {"lower": region.lower, "upper": region.upper, "beta": 1.0,
                                  "prefactor": 1e13, "energy": 1.0, "order": 1.0,
                                  "free_order": False, "fit_baseline": True, "max_nfev": 300}
        return self.settings[key]

    def snapshot(self, method, settings=None):
        dataset, region = self.context()
        return deepcopy({"dataset_id": dataset.id, "region_id": region.id, "dataset": dataset.path,
                         "source_sha256": dataset.digest, "peak": region.label,
                         "region": [region.lower, region.upper], "processing": dataset.processing,
                         "method": method, "settings": settings or self.method_settings(method)})

    @staticmethod
    def fingerprint(snapshot):
        return hashlib.sha256(json.dumps(snapshot, sort_keys=True, allow_nan=False).encode()).hexdigest()
