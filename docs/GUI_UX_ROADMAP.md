> Historical planning context. The maintained priority/status sources are [PUBLICATION_ROADMAP.md](PUBLICATION_ROADMAP.md), [CHECKPOINT_LEDGER.md](CHECKPOINT_LEDGER.md) and [METHOD_STATUS.md](METHOD_STATUS.md). The user has authorized beta improvements and experimental Explorer integration; main and public-release gates remain protected.

# GUI/UX roadmap for TPD Spectra Studio

Agreed 2026-10-19. Target: a beginner-friendly yet scientifically transparent desktop tool with a polished and reliable Windows distribution. Implementation is incremental on a GUI-focused branch, separate from kinetic-model and uncertainty research.

## Problems observed from GUI source
Current Tkinter/ttk application has a long ~322 px sidebar mixing file management, visualization, fit windows, advanced kinetic controls and output settings. The core interactive plot is useful, but the information hierarchy makes first use difficult. Do not confuse aesthetic redesign with improving scientific calculations.

## Prioritized stages and acceptance criteria

### GUI-1: Workflow and user research / low-risk usability
- Define main user journey: import -> inspect/clean -> select method -> fit/review -> export.
- Keep a prominent, understandable next action, clear empty states and human-readable errors.
- Add integrated quick start, concise field-level help and explanations of model assumptions.
- Capture keyboard navigation and basic accessibility requirements.
- Test with representative datasets and a new user without specialized software knowledge.

### GUI-2: Information architecture / responsive layout
- Organize primary navigation as Import, Explore, Analyze, Results & Export (tabs or step navigation).
- Large, resizable plot in the center; spectra list and essential options readily available; collapsible Advanced options.
- Avoid excessive scrolling, adapt to lower resolution and HiDPI displays.
- Distinguish *preview settings* from *analysis settings* and clearly indicate which controls affect exported results.
- Retain an efficient workflow for experienced users.

### GUI-3: Interactive visual analysis
- Preserve pan/zoom, multi-curve overlays, small multiples, legend and high-resolution export.
- Direct manipulation of analysis windows where practical (drag boundaries) with exact numeric entries and reset controls.
- Preview baseline, smoothing, fit and residuals; never silently alter underlying measured data.
- Readable units, consistent axis labels, colorblind-friendly curve selection and sensible defaults.

### GUI-4: Scientific model wizard
- Explain leading-edge, Redhead and Polanyi–Wigner methods in plain language alongside their assumptions.
- Separate fixed/free kinetic parameters, initial guesses and bounds; contextual units and validation feedback.
- Display model-comparison diagnostics without implying that best fit proves a mechanism.
- Prevent invalid parameter combinations before running long optimizations.

### GUI-5: Results, uncertainty and trust
- Dedicated results table/cards plus raw/fitted overlay, residual plot and warnings.
- Show uncertainties only when the scientific backend supports and validates them; identify the method, assumptions and unavailable results.
- Make it easy to compare fits and copy/export tables, plots, JSON settings and diagnostics.
- Include provenance: data identifiers, input preprocessing, bounds, solver settings, software version.

### GUI-6: Production polish and packaging
- Conduct Windows visual/functional smoke tests, keyboard and accessibility tests, HiDPI/resize tests, large-data responsiveness tests and error-state tests.
- Evaluate staying with Tkinter/ttk versus a scoped PySide6/Qt prototype based on polish, reliability, build size, maintainability and licenses; do not migrate frameworks solely for appearance.
- Keep scientific analysis off UI thread and show progress/cancel feedback for lengthy runs.
- Screenshot-based user guide and onboarding material once layout stabilizes.

## Process
One focused GUI PR per stage (or smaller). Avoid simultaneous edits to kinetic core from GUI PRs; keep the main branch working. Document user-facing behavior and test it. After scientific uncertainty APIs stabilize, integrate them into the GUI; do not mock scientific accuracy in actual releases.

## Immediate next implementation
GUI-1: user workflow review and layout improvements without replacing the GUI framework. Prepare a short usability checklist and a first testable improvement before rethinking the whole design.
## 1 November 2026: navigation and literature examples

Design references: [Mantid Workbench's main menus and task-specific toolboxes](https://docs.mantidproject.org/v6.12.0/workbench/index.html)
keep workspaces and algorithms accessible without turning every command into
a large permanent button. [Igor Pro's Data Browser and data folder hierarchy](https://docs.wavemetrics.com/igorpro/igor-basics/data-folders)
show how source data can be organized by meaningful scientific grouping.
The beta therefore uses a native File/Examples/View/Help menu and only three
visible quick actions, instead of building a heavyweight custom Office-style
ribbon in Tkinter. The scientific stage notebook remains the main task area.

The example browser separates truth-known simulations from licensed
publication-derived traces. A two-category browser is sufficient at this
collection size; the detail pane reports precise paper, figure, source units,
licence, limitations and DOI before loading. The active literature source is
also shown beneath the dataset selector. Source-coordinate preservation,
explicit time reconstruction and excluded rights/mismatch cases are documented
in `examples/publication_data/README.md`.

This is an information-architecture implementation, not a completed usability
study. Real Windows scaling/keyboard checks and independent scientific
acceptance remain release gates.
