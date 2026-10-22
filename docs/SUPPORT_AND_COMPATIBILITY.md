# Support, corrections and compatibility

TPD Spectra Studio is maintained by Karol Cieślik as research software. Windows x64 is the current packaged target; Python source requires Python 3.10+ and Tk. No response-time or long-term-support guarantee is offered. Report reproducible problems through GitHub issues, including the exact version/build, method and steps. Do not publish private measurements, personal paths or instrument-identifying metadata unless you intend to share them.

The beta is unsigned. Executable signing and institutional deployment remain release decisions. Follow local security policy; do not disable operating-system protections to run the software.

Scientific-output corrections must be described in CHANGELOG.md with affected quantities/versions, an explanation and a reproducible regression. Old output is a historical record: never silently recompute it or relabel it as produced by a newer method. The 0.11.0b1 corrections suppress the uncalibrated leading-edge prefactor and include estimated noise variance in information-criterion parameter counts; re-evaluate prior physical-prefactor interpretations and model rankings.

Schemas are versioned independently of app version. Current run_status schema is 1; analysis_project is 1; Explorer export is 2. Automated full project migration/reopening is not yet implemented. Keep the original inputs, output folders and matching executable/source. Unique run folders prevent routine GUI reruns overwriting previous evidence. Cancelled/failed runs may contain partial output; read run_status.json before using it.

No automatic data upload or crash reporting is added. A future diagnostic bundle must show exactly what will be shared and omit raw data and private paths by default. Until implemented, copy only reviewed build information from About.

The public release remains gated on the checkpoint ledger, independent scientific review and Windows acceptance. A successful automated build is necessary but insufficient for release.
