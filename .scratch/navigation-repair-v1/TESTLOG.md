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

Pending clean source commit, deterministic artifact, full suite and live checks.
