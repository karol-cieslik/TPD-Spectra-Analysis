# TPD Spectra Studio identity

Product: **TPD Spectra Studio**. Creator and maintainer: **Karol Cieślik**.
Repository/package names remain TPD-Spectra-Analysis and tpd-spectra.

The original mark is a pair of asymmetric spectrum peaks on a rounded navy
tile. It is an identifying illustration, not measured data or a fitted result.
No stock images, institutional marks, downloaded fonts or third-party logos
were used. The editable SVG and generated PNG/ICO files live in
`tpd_spectra/assets/`; `scripts/generate_brand_assets.py` reproduces them.
These project-created brand assets are offered under the repository's MIT
license. No trademark clearance or exclusivity is asserted.

## Desktop usage

- Navy `#142D3B` anchors the header; mint `#8DE2CF` identifies the mark.
- Teal `#087E8B` identifies the primary action; dark ink and muted slate provide
  readable text on white and pale grey surfaces.
- The window/taskbar icon has native small and high-DPI sizes; PyInstaller
  embeds the ICO and bundles the runtime images. Python wheels include them.
- Import/help and analysis actions are grouped; analysis actions reflow below
  import controls when they do not fit. Plot export sits next to the plot.
- A persistent beta label distinguishes this candidate. About retains the
  author, exact build, repository, license and scientific-use context.
- Branding stays out of scientific figures. Data colours, numerical results,
  units, method assumptions and uncertainty labels retain their meanings.

## Acceptance scope

Automated checks cover icon sizes, asset loading, toolbar visibility at two
Tk scaling/window configurations, and the packaged GUI workflow. They do not
establish screen-reader accessibility or exhaustive Windows scaling support.
Desktop capture during this pass failed with `FrameArrived timed out`; no
manual visual acceptance or actual-application screenshot is claimed.

Before stable release, review the executable's Explorer/taskbar appearance,
100/125/150/200% display scaling, keyboard focus, long filenames, model warning
visibility and About on representative Windows machines. The historical
`assets/studio-preview.svg` is an illustration and is not a screenshot of this
candidate.
