# Static space reading — verification

Baseline: 2e11291. Scope: presentation only, no mathematical/schema changes.

## Design evidence

Read Notion UX and “UX should be on the user's side” on 2026-09-06:
https://app.notion.com/p/3c947863c0ff8177938fd20053d4d50c
https://app.notion.com/p/3c947863c0ff81d8b0dbf0559cdf72a2

Applied calm reading, visible true state, and direct reader intent. No settings
agent or backend. Audit covered all 42 retained routes, including 9 redirects
into the 3 parameterized families. Inspected all seven desktop contact sheets
before and after and representative mobile views. Shared legacy summaries were
preserved rather than inventing new mathematical prose.

Key repairs: available homology precedes unrecorded cohomology; dimensions and
human review state are visible; sources use homology-role citations rather than
first contextual citations; technical records sit behind disclosure; long tables
have an explicitly limited display (not limited knowledge); copied links preserve
coefficient/reduced state; reduced row labels use a tilde. Family pages lead with
the selected space, hide repetitive all-degree derivations initially, keep Z and
Q separate, and provide a keyboard-scrollable row of five finite-field cards.

## Preview checks

- New reading browser suite: 42 spaces, 33 legacy pages, 169 coefficient views,
  12 degree disclosures; widths 320/390/700/1100; copy/reload/history, print,
  keyboard scrolling, source focus, dark theme; zero page errors.
- Existing family suite: 21 family views, 42 legacy spaces, 49 spectra,
  21 responsive cases; zero errors.
- Navigation suite: 11 specified widths, 33 picker selections, 125% and 200%
  browser zoom; zero errors.
- All 42 after-audit mobile pages have no document horizontal overflow.
- Representative sphere mobile document height falls from about 7,500px to
  3,386px without deleting information; finite fields scroll within their row.
- Independent review caught citation-role substring, sticky-header focus and
  print-display-note defects; all corrected and regression tested.

Reproducible scripts: scripts/audit_space_pages.cjs and
scripts/verify_space_reading_browser.cjs. Local screenshots/metrics:
/tmp/homology-space-audit.l3gqQk and /tmp/homology-space-after.DsuR9U.

Codex computer-use could not run because the Mac was locked. This limitation was
reported to the user; isolated Chrome is not claimed to verify the in-app browser.

## Frozen release

Source commit: 66b550709b538ddbffd59194560be67dc1a1800c.
Independent review passes on exact source hashes in review.md.
Full unittest discovery: 189 tests, OK, 3 optional skips, 215.688 seconds.
Existing non-failing SQLite ResourceWarnings remain.
All three Chrome suites pass again on the frozen dist/atlas.html artifact.
Deterministic release gate with --verify-rebuild passes in public_review_preview.
Artifact: 5,280,258 bytes; SHA-256
516648907cebad4ee275f4c8bf7bffb5a93a1b01557f7e449066551b036a459f.
No differences in homology_db, docs/reviews or static_atlas/families.js.
Remote main verified at baseline 2e11291 before non-force publication.
Release commit: 7174f93f36ae96cb9deb42e66b60b12a275065ab, pushed without force.
GitHub Pages run 34034689672 succeeded on 2026-09-06:
https://github.com/DaveArcher18/homology-db/actions/runs/34034689672
Observed using connected GitHub fetch (Gather GitHub instructions, local revision
read 2026-09-06). Workflow actor DaveArcher18; no derived acceptance claim.
Live HTTP 200 response matches the artifact bytes and SHA-256 above.
All three browser suites pass again against https://davearcher18.github.io/homology-db/:
42 space routes, 169 legacy coefficient views, 21 family views, 49 spectra,
11 navigation widths, 33 picker selections, actual zoom, keyboard and history.
Zero browser errors. Source and artifact committed/published; no pending release
work. Codex in-app verification remains unperformed because the Mac was locked.
