# Navigation repair verification

## Preview, before release

- Chrome interaction suite: all 11 requested widths (320, 390, 640, 641,
  700, 768, 900, 960, 961, 1024, 1440); 33 native picker selections;
  keyboard selection of CP/RP/spheres; explicit Explore application; About
  focus, reload, direct return, Back/Forward, and resizing; zero page/console errors.
- Actual Chrome page zoom at 125% and 200%, using an isolated disposable
  profile's Appearance setting. Measured CSS viewport widths 1024 and 640 from
  a 1280px viewport, devicePixelRatio 1.25 and 2; no control/document overflow.
- Existing family browser suite: 21 family views, 42 legacy space links,
  49 spectra, 21 responsive cases; review forms, downloads, products, glossary
  typesetting and reduced-state isolation; zero console errors.
- Codex in-app browser: selected CP by keyboard, spheres and RP through the
  native control, applied n=6/start=9. About is visible, heading focused, and
  About reload → Workbench retains exact CP6 parameters. Resized About from
  mobile390 to960, then Workbench at700; visible wrapping nav and contained
  controls confirmed visually. Open picker accessibility tree exposes all three
  options as an expanded native menu. In-app browser's existing110% zoom also
  exercised; real125%/200% zoom verified separately in isolated Chrome.
- Independent source review: two initial findings fixed; final report is
  `review.md`. Four mathematical engine/metadata/review-binding sources remain
  unchanged relative to7cf1a00.
- Focused Python suite:20 pass; one expected stale-committed-artifact failure
  before source freeze/rebuild. This is not waived: full suite and deterministic
  gate must pass on the release artifact below.

## Release

Source commit: `346af910430364ed3e7feb095b89a68f200ab907`.
Artifact: 5,270,111 bytes, SHA-256
`912776cb004a7312a0272ccc4e42170140b95fa3a154bd0a6f59abfd2136a98e`.
Deterministic rebuild/release gate passes; public-review-preview state preserved.
Both Chrome suites above pass against this exact artifact, including actual zoom.

First full run:189 tests, one stale markup assertion and three optional external
consumer skips. Corrected the test to expect the footer's still-hidden
`nav-spectra` link instead of its removed sidebar CSS class. No runtime/source or
artifact change was required. Fresh full run:189 tests in220.645s, OK with three
optional external-consumer tests skipped. The corrected individual test also
passes. No new runtime edits followed the source-bound artifact verification.

Publication and final live checks pending.
