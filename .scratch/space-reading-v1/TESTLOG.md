# Static space reading — verification

## 2026-10-04 — reference polish candidate

Baseline: `e845cd783c42b4dd223797ad530781ff473b81ed` (current main).
Source commits:
- `f0dd4c622bb894973bd1863f6e07a32b590e2d92`: reference UI/copy/tests.
- `c2e08aa7980ef90823fd5565f23ec0cb193b03bb`: compact accessible basis keys.
- `d2d08084a0a4beccaa594c70ab85578a944085bd`: keep short convention equations together.

Candidate: 20,181,816 bytes; SHA-256
`9751f42580077d2a72b2c2ea97235f38b432cb6bdb18b17147788c7be3488afd`.
Local preview: `http://127.0.0.1:8765/`. No push/deployment or human acceptance.

Verification:
- `python3 scripts/run_unittest_shard.py --shard-count 8 --verify-partition`:
  complete deterministic partition of 243 cases.
- `python3 scripts/run_unittest_shard.py --shard-count 8 --shard-index N`,
  for N=0 through 7: 240 passes and three optional-consumer skips after retries.
  Two runs crossed a styling/source commit and correctly rejected changed source
  bindings; shard 1 was rerun, and the failing current-snapshot determinism test
  was rerun on frozen inputs. The final CSS-only equation-wrap change followed
  this regression run; the focused checks and release rebuild below passed on
  the final source above.
- `python3 -m unittest tests.test_static_atlas tests.test_canonical_space_contract`:
  22 cases initially, with two source-transition determinism failures; both
  affected cases subsequently passed in the frozen-input checks.
- `python3 -m unittest tests.test_static_atlas.StaticAtlasTest.test_current_snapshot_build_is_deterministic tests.test_canonical_space_contract`:
  five passes on frozen c2e08aa inputs.
- Final focused command: `python3 -m unittest tests.test_canonical_space_contract tests.test_static_atlas.StaticAtlasTest.test_direct_sum_scripts_are_preserved_and_nonwrapping tests.test_static_atlas.StaticAtlasTest.test_presentation_contracts_execute_as_pure_javascript tests.test_static_atlas.StaticAtlasTest.test_checked_in_artifact_remains_release_gated`:
  seven passes.
- `node --check static_atlas/atlas.js`,
  `node --check scripts/verify_space_reading_browser.cjs`, and `git diff --check`:
  pass. The standalone browser script was updated and syntax-checked; actual
  browser interactions used Codex CUA, not that standalone runner.
- Export: `python3 scripts/export_static_atlas.py --snapshot current --output dist/atlas.html --steenrod-review-candidate --allow-public-review-preview`.
- Deterministic release gate: `python3 scripts/verify_steenrod_release.py --atlas dist/atlas.html --allow-public-review-preview --verify-rebuild`:
  pass for the exact final artifact above.
- Sharded local preview built with `python3 scripts/build_static_bundle.py --atlas dist/atlas.html --output <outside-repository-preview>`.
- CUA Chrome: all 194 durable space routes retain two group tables, one visible
  ring section, lazy products, and no math-rendering errors or page overflow.
  Twelve representative routes checked at 1440x1000, 390x844 and 320x844:
  Home, About, CP2, K3, L(5,2), S0, torus, genus-26 surface, 19-fold connected sum,
  four-manifold family, lens family, and RP2. No console warnings/errors observed.
- Interaction checks: global/family alias search and keyboard focus/Escape;
  Z/F2 comparison on RP2; F5/F2/Z lens conventions and refreshed product tables;
  product/full-record/provenance disclosures; 22 K3 generators/252 relations;
  K3 and 40-element connected-sum table scrolling; withheld S0 literature versus
  unavailable genus-26 data; current About and retained historical scope note.
  Final screenshots re-captured on d2d0808; short sign formula stays on one line
  at 390px and 320px without page overflow.
- Data comparison: the entire embedded read model equals baseline except
  snapshot source_commit, source_inputs_sha256 and generated_at. All 194 space
  records, 49 spectra, formulas/products, teaching, sources and review bindings
  are unchanged. No mathematical-source paths changed.

Original screenshots, one ordered contact sheet, DOM/console evidence and logs
are retained outside the repository in this chat's visualization directory.
Review still required: visual preference and new graded-algebra/four-manifold
wording. No geometric K3 interpretation, proofs, graph, new records or backend.

## Historical verification — 2026-09-06


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
