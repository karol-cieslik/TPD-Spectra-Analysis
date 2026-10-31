"""Wheel fallback must retain the same scientific content as the source catalog."""
import json
from pathlib import Path
from tpd_spectra import scientific_help


def test_offline_help_without_repository_sidecar(monkeypatch):
    def missing(_):
        raise FileNotFoundError('no source checkout in a wheel installation')
    monkeypatch.setattr(scientific_help,'resource',missing)
    payload=scientific_help.load_help_catalog()
    original=json.loads((Path(__file__).parents[1]/scientific_help.CATALOG_RESOURCE).read_text(encoding='utf-8'))
    assert payload==original
    assert len(payload['topics'])==41
