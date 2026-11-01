"""Source suggestions are provenance, never an implicit acquisition setting."""
import numpy as np
from tkinter import messagebox
from functools import lru_cache
import json
from .beta_resources import resource
from .run_session import sha256


@lru_cache(maxsize=1)
def _known_sources():
    """Recognize bundled publication CSV bytes, never merely a familiar name."""
    try:
        rows=json.loads(resource('examples/publication_data/catalog.json').read_text(encoding='utf-8'))
        return {sha256(resource('examples/publication_data/'+row['file'])): row for row in rows}
    except (OSError,ValueError):
        return {}


def source_heating_rate(dataset):
    source = dataset.spectrum.import_report.get('publication_example', {})
    if 'beta_K_s' not in source:
        known=_known_sources().get(getattr(dataset,'digest',None),{})
        source=dict(beta_K_s=known.get('beta_K_s'),citation=known.get('citation'),
                    heating_rate_note=known.get('heating_note',''),doi=known.get('doi',''))
    value = source.get('beta_K_s')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or value <= 0:
        return None
    return dict(beta_K_s=float(value), citation=source.get('citation', 'Source metadata'),
                note=source.get('heating_rate_note', ''), doi=source.get('doi', ''))


def confirm_source_rate(panel, parent=None):
    try:
        dataset, _ = panel.app.project.context()
    except ValueError as exc:
        panel.app.status.set(str(exc))
        return False
    suggestion = source_heating_rate(dataset)
    if suggestion is None or panel.app.job_busy:
        return False
    rate = suggestion['beta_K_s']
    if not messagebox.askyesno('Confirm heating rate',
            f"{suggestion['citation']}\n{suggestion['note']}\n\n"
            f"Use {rate:g} K/s for Modeling of this dataset/region?\n"
            'This is a source suggestion, not a measurement inferred from the CSV time coordinate. '
            'Verify that it applies to the selected trace. Kinetic Analysis has separate settings.',
            parent=parent or panel.app.root):
        return False
    panel.session()['source_heating_rate_confirmation'] = suggestion
    panel.variables['beta'].set(f'{rate:g}')
    return True
