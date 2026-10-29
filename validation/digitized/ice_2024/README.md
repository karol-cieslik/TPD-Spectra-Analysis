# Kruczkiewicz et al. (2024): vector-digitized pure CO and Ar

Source: [Comprehensive laboratory constraints on thermal desorption of interstellar ice analogues](https://doi.org/10.1051/0004-6361/202346948), A&A 686, A236,
final article PDF page 9. Fig. 2b is pure CO; Fig. 3a is pure Ar.
Reproduced/adapted from F. Kruczkiewicz and colleagues under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

[CO coordinates](CO_digitized.csv) contain 328 original plotted path vertices;
[Ar coordinates](Ar_digitized.csv) contain 191. Axes are temperature K and
ML/K, with published beta 0.2 K/s. These are vector plot vertices, not original
instrument samples. `source_paths.json` preserves the exact selected PDF paths;
`source_context.png` retains the axes/captions context. The path selection,
axis ticks, source PDF hash, licence and derivation are in `provenance.json`.

[QA overlay/comparison](extraction_check.png) checks path-to-source placement
and compares both curves with the deposited originals. Unused calibration ticks
and a separate 0.25-point axis-placement allowance (about 0.19 K) are recorded
in `quality.json`. Ar shows close correspondence (peak difference −0.059 K;
comparison NRMSE 0.00589). CO does not (peak difference −9.187 K and height
ratio 3.441). The cause is unverified; no authors were contacted and no source
was overwritten. [The correction](../SOURCE_CORRESPONDENCE_UPDATE.md) qualifies
our prior deposited-CO interpretation.

No kinetic fits were performed in this digitization. Extraction/cropping,
coordinate transformation and QA annotations are changes made for this project;
the original authors did not perform or endorse them.
