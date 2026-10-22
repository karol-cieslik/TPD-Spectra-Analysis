"""Shared product identity; build metadata is supplied by the packaging job."""
from . import __version__

PRODUCT = "TPD Spectra Studio"
AUTHOR = "Karol Cieślik"
REPOSITORY = "https://github.com/karol-cieslik/TPD-Spectra-Analysis"
CHANNEL = "beta candidate"
try:
    from ._build_info import COMMIT
except ImportError:
    COMMIT = "unrecorded source checkout"


def build_identity():
    return {"product": PRODUCT, "version": __version__, "channel": CHANNEL,
            "commit": COMMIT, "author": AUTHOR, "repository": REPOSITORY}


def about_text():
    return (f"{PRODUCT}\nVersion {__version__} · {CHANNEL}\nBuild: {COMMIT}\n\n"
            f"Created and maintained by {AUTHOR}.\n\n"
            "Tools for inspecting, comparing, and analyzing temperature-programmed "
            "desorption data. Review processing, model assumptions and warnings before "
            "interpreting results. Synthetic benchmarks do not establish experimental validity.\n\n"
            f"Source, documentation and issues:\n{REPOSITORY}\n\n"
            "Code license: MIT. Data and third-party assets have separate rights.\n"
            "When citing this software, record the version and analysis settings; see CITATION.cff.")
