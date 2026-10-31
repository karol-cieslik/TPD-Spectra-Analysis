"""CLI accepts common delimited-text formats with explicit unit/channel settings."""
import json
import numpy as np
import pandas as pd

from tpd_spectra.cli import main


def test_cli_reads_tsv_txt_units_and_custom_columns(tmp_path):
    seconds = np.arange(601.)
    temperature_k = 300. + .5 * seconds
    signal = .02 + np.exp(-((temperature_k - 500.) / 18.) ** 2)
    source = tmp_path / "instrument.TXT"
    pd.DataFrame({"Elapsed": seconds, "Detector 1": signal,
                  "SampleTemp": temperature_k}).to_csv(source, sep="\t", index=False)
    output = tmp_path / "results"
    reviewed_choices = tmp_path / "import-options.json"
    reviewed_choices.write_text(json.dumps({str(source.resolve()): {
        "skiprows": 0, "delimiter": "\t", "decimal": ".",
        "time_column": "Elapsed", "signal_column": "Detector 1",
        "temperature_column": "SampleTemp", "time_unit": "s", "temperature_unit": "K",
    }}), encoding="utf-8")
    result = main([
        str(source), "--output", str(output), "--import-options-file", str(reviewed_choices),
        "--leading-edge", "100", "180", "--redhead-region", "180", "260",
    ])
    assert result == 0
    import_report = output / "diagnostics" / "instrument_import.json"
    payload = json.loads(import_report.read_text(encoding="utf-8"))
    assert payload["delimiter"] == "\t"
    assert payload["source_units"] == {"time": "s", "temperature": "K"}
    assert payload["accepted_records"] == 601
