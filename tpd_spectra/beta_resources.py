"""Resolve portable-package resources without depending on the working folder."""
from pathlib import Path
import sys


def package_root():
    return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[1]


def resource(relative):
    root=package_root()
    target=(root/relative).resolve()
    if not target.is_relative_to(root) or not target.exists():
        raise FileNotFoundError('Included resource is unavailable. Extract the complete beta ZIP, keeping examples and docs beside the executable.')
    return target
