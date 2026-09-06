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

Release commit: `8e5f3a6e3ac7f9dc65d9d07b7a7cea0fa52d5057`, pushed fast-forward
to main. [Pages run34033019164](https://github.com/DaveArcher18/homology-db/actions/runs/34033019164)
succeeded. Live HTTP200 response is byte-identical to the artifact above.
Both browser suites pass again against https://davearcher18.github.io/homology-db/,
including all11 widths,33 selections,125%/200% zoom,21 family views,42 legacy
space links and49 spectra with zero errors. Codex live check selected CP8/start9
through the dropdown, opened About, reloaded, and returned with exact parameters
and no overflow. The live workbench is left open; viewport override reset.

## Deployment provenance

- Source: GitHub Actions run34033019164, DaveArcher18/homology-db, main,
  exact release commit above; actor DaveArcher18. Created2026-09-06T12:24:48Z,
  updated2026-09-06T12:25:10Z; observed success2026-09-06T12:26:25Z.
- Acquisition: connected GitHub read-only REST fetch, exact run URL above;
  Gather/gather-github local skill version inspected2026-09-06 (no explicit
  skill revision declared). Transformation: extracted status/conclusion/head_sha.
  Pointer retained, no raw API payload or personal metadata retained.
- Live bytes: direct HTTPS fetch compared with local artifact; browser evidence
  from Chrome Playwright and Codex CUA interactions, completed by12:28UTC.
- Limitations: human mathematical review still pending; three optional external
  consumer tests skipped. No mathematical expansion or acceptance implied.
