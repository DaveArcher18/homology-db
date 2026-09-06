# Textbook QA readiness evidence

Plan committed before implementation: c7371dd, baseline e33e830.
Feature: .underbite/features/F-01-textbook-qa.md. Static-only scope.

## Ownership and independent checks

- family_math_review: teaching inventory, exposition and HP²/OP² ring extension.
- student_workbench: teaching/map/comparison and scoped-review UI.
- family_engine: narrow review validation/history/form/guide.
- Root: source-bound exporter, integration, browser QA, release, human QA packet.
- Independent math/content review by family_engine: primary-source readings,
  90 independently modeled ordered products across ten new records, 14 focused
  tests, all42 IDs/introductions and comparison links; PASS after Thom citation
  correction. Exact hashes: math-content-review.md.
- Independent review workflow inspection by family_math_review: 19 tests and
  actual-family narrow/stale fixtures, production registry unchanged; PASS.
  Exact hashes: review-workflow-review.md. Append-only helper is tested but is a
  maintainer procedure with trusted prior JSON, not an automatic release gate.

## Integrated preview

- 46 focused Python tests pass (teaching, exporter, classical, review, families).
- Static atlas suite: 16 pass; one expected checked-in-artifact stale-source gate
  remains until source freeze and rebuild. This is not waived for release.
- Existing reading browser suite:42spaces/171coefficientviews, alldisclosures,
  print/copy/reload/history/keyboard/sourcefocus/dark; PASS.
- Existing navigation suite:11widths/33pickerselections, About/history/resize,
  real125%/200% zoom; PASS.
- Existing family suite:21familyviews/42legacy/49spectra/21responsive; PASS.
  Updated test uses actual Review this result -> publicform interaction.
- New textbook browser suite:42inventoryentries/3comparisons/75records, all42
  source notes, scope selection/copiedpacket/invalidscope/wholeoption, all11
  widths, isolated partialconcern+wholeacceptance fixture; PASS, no pageerrors.
- Desktop/mobile screenshot inspection at390/1440: map, comparison, reviewpanel.
  Follow-up compact heading CSS improves reference-page hierarchy; final checks
  below will cover that exact source. Images /tmp/homology-textbook-qa-images.
- New route tests explicitly wait for actual rendered state, not just hash
  changes; invalid review links lose href and are checked without assuming
  they retain link semantics. Added explicit accessible name to scope picker.

No formula-family evaluator, production review register or corpus files changed.
Original13core retained, selected2extension adds10fieldrecords; 27gaps explicit.
Static exponent/degree-window semantics and ordinary vsreduced separation retained.
New source material/locators and derived-field justification recorded in
docs/research/textbook-coverage.md. Not an exhaustive Hatcher index.

Codex computer-use check could not start because the Mac is locked. User informed;
Chrome is not represented as the in-app browser. No public reviews submitted.

## Frozen release

Initial exact candidate6d3c594 passed deterministic rebuild and all4Chrome
suites. Independent integration review found About hid narrow concern text
beside whole approval and retained the old review-control instructions. Root
stopped the running full suite before editing, fixed both, and added isolated
About fixture coverage. The full suite will restart on the corrected commit.
Final source: ec3054786670c52a0e2d78687773d4177b1dacb9.
Final artifact: 5,386,015 bytes; SHA-256
b5cad415c8d3d42195ee2109b2ebdb91ba2d962d9bfe4cf910b8e6b26cec9f7f.
Full unittest discovery: 211 tests, OK (3 optional skips), 216.399 seconds.
All4Chrome suites pass on exactartifact. Deterministic --verify-rebuild passes.
Independent integration re-review passes, including About concern fixture and
actual clickthrough, plus7focusedtests; integration-verification.md records hashes.
Existing SQLite ResourceWarnings are non-failing. No source changes during final
fullsuite. Remote main confirmed e33e830 before authorized nonforce publication.
Live publication and verification pending.
Human QA journey: docs/QA_WITH_GABRIEL.md; acceptance remains pending.

## Publication identity refresh

Connected publication re-created the source commit as
63116513cc59565e88877c41362a0461862f56a6. Independent full-tree comparison found
only two deliberate differences from local be891b7: the old artifact awaiting
rebuild and WORKSTATE.md retained unchanged from upstream. Every implementation,
test, source and review-form blob is identical. Source-input SHA-256 remains
ffdf2030163d6df28a615414da8b7850b420fdd5e4eaa813dd1bb73dde4e5c84.

Fresh artifact: 5,386,015 bytes; SHA-256
80f2adaa588657c8cf33c8450f8ae7ad037d3bdb46671fdbaf0239de0f89d974.
Deterministic --verify-rebuild passes against this source. All four exact-artifact
Chrome suites pass with the same coverage recorded above and zero page errors.
The original content-level independent reviews remain applicable by exact hashes.
Fresh full unittest discovery: 211tests, OK (3optional skips), 222.844 seconds.
Release commit5bf19f8ca49009e412ec73247acd231e9740b1b5 changes only the artifact
from source63116513. Remote Git blob equals local rebuilt file exactly.
Main advanced non-force only after all checks; preceding main was e33e830.
Pages run34039872067 succeeded. Live HTTP200 is5,386,015bytes and equals the
artifact SHA-25680f2adaa588657c8cf33c8450f8ae7ad037d3bdb46671fdbaf0239de0f89d974.
All four browser suites also pass against the live GitHub Pages URL:42mapentries,
3comparisons,75records,171coefficientviews,11widths,33pickerselections, keyboard,
125%/200%zoom,21familyviews,42legacyspaces and49spectra, with zero page errors.
Codex in-app verification remains unavailable, not passed. No production review
was added. The three tasks are complete for human QA, not human acceptance.
