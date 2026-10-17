from pathlib import Path

import pytest

from tpd_spectra.gui import build_cli_arguments


def _settings(tmp_path: Path):
    source = tmp_path / "input.csv"
    source.write_text("placeholder", encoding="utf-8")
    return {
        "input_path": str(source), "output_path": str(tmp_path / "out"),
        "leading_low": "130", "leading_high": "170",
        "redhead_low": "230", "redhead_high": "400",
        "prefactor": "1e20", "window": "10", "filter": "median",
        "max_time_min": "10", "kinetic_fit": False,
        "kinetic_model": "single", "kinetic_order": "1",
        "kinetic_initial_energy": "1.0", "kinetic_initial_prefactor": "1e13",
        "kinetic_no_baseline": False,
    }


def test_gui_arguments_keep_classical_defaults_and_paths(tmp_path):
    settings = _settings(tmp_path)
    args = build_cli_arguments(settings)
    assert args[0] == settings["input_path"]
    assert args[args.index("--output") + 1] == settings["output_path"]
    assert "--kinetic-fit" not in args
    assert args[args.index("--leading-edge") + 1:args.index("--leading-edge") + 3] == ["130.0", "170.0"]


def test_gui_arguments_add_kinetic_options(tmp_path):
    settings = _settings(tmp_path)
    settings.update(kinetic_fit=True, kinetic_model="compare", kinetic_order="fit", kinetic_no_baseline=True)
    args = build_cli_arguments(settings)
    assert "--kinetic-fit" in args
    assert args[args.index("--kinetic-model") + 1] == "compare"
    assert args[args.index("--kinetic-order") + 1] == "fit"
    assert "--kinetic-no-baseline" in args


@pytest.mark.parametrize("field,value", [
    ("leading_high", "120"), ("prefactor", "0"), ("window", "0"),
    ("filter", "gaussian"), ("kinetic_initial_energy", "-1"),
])
def test_gui_arguments_reject_invalid_settings(tmp_path, field, value):
    settings = _settings(tmp_path)
    settings[field] = value
    with pytest.raises(ValueError):
        build_cli_arguments(settings)


def test_gui_arguments_reject_missing_input(tmp_path):
    settings = _settings(tmp_path)
    settings["input_path"] = str(tmp_path / "missing.csv")
    with pytest.raises(ValueError, match="does not exist"):
        build_cli_arguments(settings)
