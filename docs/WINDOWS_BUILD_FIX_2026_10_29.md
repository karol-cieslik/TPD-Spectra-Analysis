# Windows packaging correction — 29 October 2026

Failed run: https://github.com/karol-cieslik/TPD-Spectra-Analysis/actions/runs/40865737200

The run passed all 366 Windows regression tests. Build identity preparation then rejected three apparently modified scientific CSVs: ice_2024/predictions.csv and ptcda_au111/{inventory,metadata_inventory}. Their retained CRLF Git blobs conflicted with text/eol normalization attributes. The version resource was never created. A later successful pip-freeze command masked the preparation failure in PowerShell; PyInstaller consequently failed on the missing output/windows-version.txt.

The correction marks validation CSVs -text, preserving existing retained LF/CRLF bytes and hashes. It does not renormalize any scientific input/output. The workflow now stops on a nonzero preparation exit and checks that the version resource exists. The clean-source identity guard is unchanged.

Local verification: six focused checkout/packaging tests pass. The new regression constructs raw CRLF blobs and checks a Windows-style core.autocrlf=true checkout remains byte-preserving and clean. No scientific fitting was repeated. The ensuing Windows workflow must confirm executable packaging; local tests are not Windows GUI acceptance or release approval.
