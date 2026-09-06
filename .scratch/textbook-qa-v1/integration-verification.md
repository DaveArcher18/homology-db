# F-01 independent integration verification

Verifier: `/root/family_engine` (agent). The agreed feature
`.underbite/features/F-01-textbook-qa.md` was read before inspecting the
implementation/test results. Scope: UI, exporter, content composition and QA
handoff. This verifier authored the review backend, so its backend authority
checks are explicitly outside this independent report; that component received
the separate peer review in `review-workflow-review.md`.

## Exact candidate

- Source commit: `ec3054786670c52a0e2d78687773d4177b1dacb9`.
- Artifact: `dist/atlas.html`, 5,386,015 bytes.
- Artifact SHA-256: `b5cad415c8d3d42195ee2109b2ebdb91ba2d962d9bfe4cf910b8e6b26cec9f7f`.
- Embedded source-input SHA-256: `ffdf2030163d6df28a615414da8b7850b420fdd5e4eaa813dd1bb73dde4e5c84`.
- Embedded teaching SHA-256: `0eb14c70c73c71f8554d58e9e5e2698ca9215e0b62aa42d24dc6d8d3174e80ad`.

## Claims and evidence

| Claim | Result | Evidence |
| --- | --- | --- |
| Selected textbook map covers all retained spaces without claiming an exhaustive book index | PASS | Independently executed textbook browser: 42 entries, search/zero results/chapter filtering; seven teaching/export tests pass. |
| Original core stays distinct from extension | PASS | Embedded data has 13 core flags, 15 ring-bearing spaces, 75 five-field records. Export metadata lists original and extension IDs separately. |
| Teaching content is bound to current actual coverage | PASS | `teaching_projection` requires the exact space set; its hash includes derived coverage/redirect metadata, and `validate_read_model` rejects exposition/coverage/snapshot drift. |
| Guided comparisons and page explanations are accessible | PASS | Browser follows all three comparison routes/steps, checks all 42 page teaching notes and zero mathematical rendering fallbacks. Eleven widths pass overflow checks. |
| UI prepares precise narrow review packet without publication | PASS | Browser selects RP²/F2/degrees0–2/cohomology+products; copied JSON and GitHub query carry exact scope/hash/source. Invalid bounds disable actions. Whole scope is explicit. No issue was submitted. |
| Scoped concern is not falsely applied to an entire family/current instance | PASS | Isolated fixture shows whole acceptance beside a narrow concern and the actual n=2 scope while viewing n=99. Separate intercepted HTML fixture confirms About also qualifies whole acceptance and links to workbench review details. |
| Human QA is enabled, not fabricated | PASS | Production review history remains empty; packet requires human endorsement/maintainer validation. `docs/QA_WITH_GABRIEL.md` provides a focused 15-minute journey with exact comparisons, honest gaps and scoped handoff. |
| Full current release and live publication are complete | NOT VERIFIABLE in this audit | Root is running the full regression/release sequence; QA document still marks release identity pending. This report does not claim a deployed outcome. |
| Codex in-app verification | NOT VERIFIABLE | Mac is locked; this limitation must remain explicit. Independent isolated Chrome verification succeeded instead. |

## Independently executed checks

`node scripts/verify_textbook_browser.cjs dist/atlas.html` with the bundled
Playwright dependency ran in an isolated temporary Chrome profile and passed:
42 inventory entries, 3 comparisons, 75 records, 11 widths, scoped packet,
invalid-scope and temporary concern-fixture checks; zero page errors.

`python3 -m unittest tests.test_teaching_atlas tests.test_teaching -v` passed
all **7 tests**, including deterministic projection and tampering checks.

The embedded artifact contains all 49 spectra. Root's existing all-route/browser
suites provide their interaction coverage; this narrow independently executed
script did not repeat every spectrum interaction.

## Finding resolved and final disposition

Initial candidate `6d3c594` omitted scoped concerns from the About review list.
Correction `ec30547` adds the narrower-scope concern/review qualifier, a link
to inspect the exact scopes, and current “Review this result” instructions.
I inspected the exact correction diff and independently reran the complete
textbook browser script against the rebuilt artifact: PASS, including the new
isolated About fixture with whole approval plus scoped rejection and its
workbench clickthrough. The fixture is intercepted temporary HTML only;
production reviews remain untouched. All seven focused teaching/export tests
also passed again. The correction changes no mathematical rule or coverage.

Disposition: **PASS for this bounded independent integration review; no
remaining findings**. This does not replace root's release-wide verification
or live publication checks. No implementation or production review data was
edited by this verifier; only this report was written. Human QA remains pending.

## Transport verification addendum — 2026-09-06

The GitHub API transport creates a new commit identity without changing the
reviewed implementation. I independently checked the isolated release checkout:

- Source commit: `63116513cc59565e88877c41362a0461862f56a6`.
- Source-input SHA-256: `ffdf2030163d6df28a615414da8b7850b420fdd5e4eaa813dd1bb73dde4e5c84`, identical to the independently reviewed candidate above.
- Full committed-tree comparison with local release `be891b7f5675140f592c4b2fa2f6d52dbc57668d` differed only in `WORKSTATE.md` and the then-unrebuilt `dist/atlas.html`.
- `WORKSTATE.md` retained upstream `e33e830` blob `bff719185431228d0c88ee0ee8ef764b07b765bb`; it is not a source input.
- No differences from `ec30547` in `homology_db`, `static_atlas`, `scripts`, `tests`, or `.github`. The source-input working tree was clean.

**PASS:** original content-level mathematical and implementation reviews remain
applicable by this exact-tree and input-hash check. Artifact identity necessarily
changes with the transported source commit and must use fresh release evidence.

Root reports the rebuilt artifact SHA-256 as
`80f2adaa588657c8cf33c8450f8ae7ad037d3bdb46671fdbaf0239de0f89d974`,
in release `5bf19f8ca49009e412ec73247acd231e9740b1b5`. Root also reports fresh
unittest discovery: 211 tests, OK with 3 optional skips, 222.844 seconds; all
four Chrome suites pass; deterministic release gate passes. These fresh runs
are **root-reported, not independently rerun by this verifier**.

Live publication checks remain pending. Human QA remains pending, and locked
Codex in-app verification remains not verifiable. This addendum performs no
remote action and does not claim a live deployment outcome.
