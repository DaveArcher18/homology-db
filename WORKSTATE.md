# Work state

Status: ACTIVE

## Objective

Implement Gabriel Ong's information-architecture and mathematical-display
feedback for the 42-space Chromatic Homology Atlas: add a real landing page,
Spaces and family landing views, focused Conceptual-space pages with local
coefficient controls, TeX-quality names, compact repeated direct sums,
definition knowls, restrained tags, and explicit exhaustive/bounded coverage
badges. Preserve Snapshot identity, provenance, uncertainty, feedback,
permalinks, print, themes, review records, and keyboard accessibility.

## Active map

The historical release map remains at `.scratch/named-atlas-review-v1/map.md`.
The current vertical slice is implemented by `corpus/chromatic-v1/`,
`homology_db/chromatic.py`, and the `homology-db.static-atlas/2` exporter.

## Control mode

`INTERACTIVE_ONLY` — this chat is the sole control plane. The standalone
`resume-homology-db-hard-push` automation is paused and must not be re-enabled
without an explicit user request here.

## Current ticket

`Implement Gabriel's atlas IA and mathematical-display review`, claimed by
`/root (interactive chat)` on 2026-07-23.

## Active run lease

`/root (interactive chat)` — active while implementing, reviewing, testing,
and preparing the Gabriel-feedback iteration.

## Last checkpoint

- This iteration starts from clean, synchronized `main` at `d2b6399`. Gabriel
  Ong's seven accepted review points are the fixed product delta; the existing
  42-space Snapshot, Models, Evidence, Homology assertions, sources, and
  deterministic one-file delivery remain fixed inputs.
- Main was pushed through `9108496` with no remote divergence. GitHub Pages run
  `29984104725` completed successfully in 11 seconds. The public HTTP 200 body
  is 4,149,026 bytes and byte-identical to `dist/atlas.html` at SHA-256
  `b6efaad48b0d8382963592a540ed07ab77291c23c8f85ad4331efc92b8e6ee99`.
- Live 320-pixel checks passed for the exact `Real projective spaces` family
  search, automatic family-outline expansion, zero horizontal overflow, and
  Refine dialog/inert/focus behavior. The final 1280-pixel System-theme render
  has 42/42 spaces and zero overflow. The in-app browser was restored to its
  default viewport and left on the clean public atlas URL.
- Commits `3e957a2` and `7f31886` replaced the form-like controls and flat
  family menu with a compact command bar, persistent family/member outline,
  native family permalinks, family focus, parameterized member navigation,
  responsive drawer, and light/dark/system themes. Commit `55f4952` closes the
  independent review findings: family labels and narratives are searchable,
  the directory has a collapsed A–Z fallback, narrow family filtering moves
  focus into the document, Refine is a trapped/inert modal sheet on narrow
  screens, theme selection returns focus, current-family semantics stay
  exposed, zero-result controls retain contrast, and feedback titles include
  the source-database SHA-256.
- Focused export contracts, JavaScript syntax, and `git diff --check` pass.
  Local browser checks pass for five exact family-label queries, the 42-entry
  A–Z index, 320-pixel Refine trap/return/inert behavior, mobile family
  filtering and heading focus, theme focus return, desktop-to-mobile sidebar
  focus handoff, feedback-title length, and zero horizontal overflow.
- `c4790fb` records the deterministic reviewed artifact: 4,149,026 bytes,
  SHA-256
  `b6efaad48b0d8382963592a540ed07ab77291c23c8f85ad4331efc92b8e6ee99`,
  embedding clean source `55f4952` and source-input SHA-256
  `ffefc24a3084d31fe7e3edc3844dd734c7e45800b641319d1e83902df49edb1d`.
  The full 64-test suite passes including artifact parity. Targeted closure
  re-reviews report no remaining specification, accessibility, or
  repository-standards blocker.
- This iteration starts from clean, synchronized `main` at `ccb6465`. The
  deployed redesign is byte-verified and mathematically fixed; direct user
  feedback identifies the remaining problem as menu quality and weak family
  browsing, not data or theme correctness.
- The redesign starts from clean, synchronized `main` at `980b498` and the
  byte-verified live Snapshot `chromatic-16e4f2be46edd93a`. Mathematical data
  and read-model semantics are fixed inputs; this ticket changes presentation
  and preference behavior only.
- `2008d56` implements the researched low-chrome continuous document,
  progressive filters, compact responsive index, corrected heading/table
  semantics, accessible mobile drawer, and persistent System/Light/Dark
  preference. The primary-source synthesis and implementation decisions are
  recorded in `docs/research/atlas-ui-ux-redesign-2026-07-23.md`.
- `420d0bd` checks in the deterministic one-file release artifact:
  4,113,332 bytes, SHA-256
  `59f32287e8534af13fc640c1500711dcb3abb16f7cb8b1c6f96418d4d5b8da40`,
  source commit `2008d56fe2cd73603780cf24a554bdab7e920b1a`, clean source
  tree, and 1,129,548 bytes below the 5 MiB cap.
- The 64-test suite passes including artifact parity. The exact artifact passed
  light/dark/system persistence, search, coefficients, review, reset, feedback,
  1440/390/320-pixel reflow, inline filter dismissal, modal-index focus,
  mobile About, and zero-console-error browser checks. Final specification and
  release-security reviews found no code/content blocker; the standards review
  requested this checkpoint and `TESTLOG.md` update before publication.
- Commit `15051ca` was pushed to synchronized `main`. GitHub Pages run
  `29979578366` completed successfully in 12 seconds. The live HTTP 200 body is
  4,113,332 bytes and byte-identical to `dist/atlas.html` at SHA-256
  `59f32287…d5b8da40`; the live 390-pixel search/index smoke test passed with
  no console warning/error. The browser was restored to its default viewport
  and left on <https://davearcher18.github.io/homology-db/>.
- Commits `caeedc4` through `e1d9a4b` implement, independently review, test,
  and publish the 42-space vertical slice: 32 finite CW complexes and 10
  infinite finite-type CW complexes in 17 families.
- Twenty-one spaces carry exact integral torsion at primes 2, 3, 5, and 7,
  including `Z/4`, `Z/8`, and `Z/9`; field rows include the UCT Tor term.
- Every space has a qualified Model, at least one HTTPS source with a pinpoint,
  and a computation sketch. The Poincare sphere uses a checked-in pinned
  16-vertex/90-facet triangulation rather than the sparse chain of `S^3`.
- Infinite finite-type rows are complete only through degree 24 and carry no
  upper-vanishing claim. Identity guards retain `CP^2` versus `S^2 v S^4`, the
  Poincare sphere versus `S^3`, and distinct weighted 5-primary lens spaces.
- The current product is routed through `python3 -m homology_db chromatic ...`;
  the unprefixed 60-space preview remains replayable without modifying its
  cryptographically pinned builder or tests.
- The checked-in release candidate is Snapshot `chromatic-16e4f2be46edd93a`:
  a 4,097,121-byte one-file atlas with 42 Models, 42 Evidence records, 62 cited
  source links, 41 recorded runs, 11 resolved relationships, and 4,190
  Homology rows. It embeds source commit `4544ae3`, a clean source-input state,
  and zero unresolved references.
- Every space and family has structured correction/computation feedback; a
  global structured form requests more spaces. Reliability is filterable and
  Review mode expands source locators and exact record metadata.
- The full 63-test suite, two deterministic rebuilds, three hash-seed database
  builds, current-corpus warning-strict run, Python/JavaScript compilation,
  JSON/YAML parsing, manifest verification, and diff checks pass. Independent
  mathematical, specification, standards, and release-security reviews have
  no remaining hard finding.
- GitHub Pages run `29960163529` deployed `e1d9a4b` successfully. The public
  response is HTTP 200, 4,097,121 bytes, and byte-identical to
  `dist/atlas.html` at SHA-256 `f1d37420…54c36c`. Desktop and 390-by-844 live
  browser smoke tests passed at <https://davearcher18.github.io/homology-db/>.

- `cfe6333` established the standalone repository, project/domain docs, and recovery conventions.
- `1fb1430` committed the Wayfinder map and eleven decision tickets from three independent breadth-first audits.
- The initial frontier is observable contract, honest constellation, and finite-model corpus survey.
- The active `resume-homology-db-hard-push` Codex automation retries every 15 minutes.
- Ticket 01 resolved the hard observable release contract in `docs/research/v0.0.1-observable-contract.md`.
- Ticket 02's branch-only executable constellation passes 22 semantic checks
  across identity, artifacts, conventions, correction, conflict, absence,
  current projection, and three-valued torsion-query behavior.
- Prototype commit `0ebf896` is the retained primary source on
  `prototype/honest-constellation`; main retains the validated decision, not
  the throwaway terminal implementation.
- An overlapping scheduled wakeup was reconciled; the resume protocol now
  requires a fresh run lease to suppress same-agent concurrent mutation.
- Ticket 03 pins Stellar v6 as the leading bulk-source candidate, treats
  polyDB as the overlapping live view, and assigns simpcomp, Sage, HAP, and
  Regina distinct named-corpus, generator, adapter, or oracle roles.
- Three consecutive goal turns reached the same user-owned decision without a
  response; the user resumed at 2026-07-11T12:10:17Z and approved regular
  finite CW Models plus a reviewed handpicked special slice.
- Ticket 04 admits only finite abstract-simplicial and witness-certified
  regular-CW Models, with order-complex chains as the guaranteed CW computation
  route and at least 10 paired genuinely nonsimplicial examples in the manifest.
- Ticket 05 is claimed. Its fixed inputs are G6's strict three-valued evidence
  rule and the honest-constellation fixture; question 1 records the first
  consequential distinction between explicit `unknown` and unresolved data.
- At the user's direction, the recurring automation was paused and ticket 05
  was reclaimed from its standalone worker. Progress is now controlled
  exclusively from this chat.
- Ticket 05 fixes a one-tier conjunctive query contract with evidence trits,
  narrow explicit `unknown`, hard conflict fences, separately returned
  unresolved candidates, and complete structured explanations.
- Ticket 06 is claimed by the interactive chat to define the deterministic
  Current projection over immutable Homology assertions and editorial events.
- Ticket 06 now has a draft normative Current-projection contract and ADR.
  Three independent audits agree on explicit admission, strict claim classes,
  append-only lifecycle authority, declared conflict, and explicit promotion;
  their final defect reviews are in progress.
- Ticket 06 is resolved. Its corrected contract separates admission from
  Knowledge state, projects strict claim classes without implicit winners,
  defines atomic append-only lifecycle events and subset-maximal declared
  conflicts, and requires explicit dependency-checked promotion assertions.
- Ticket 06 passed all contract checks and three independent closure reviews.
  Staging the scoped commit was rejected because the approval service reported
  its usage limit exhausted until 18:26; no workaround was attempted.
- The user explicitly resumed and authorized continuous progress through a
  working database connected to QA. Ticket 06 was committed as `fda475b`, and
  ticket 07 is claimed to pin the exact release corpus.
- Ticket 07 now has a machine-readable selection contract, verifier, and
  explanatory contract: 174 curated spaces (128 common manifolds), a planned
  1,159 qualified Model ledger, explicit G3 margins, 66 validation Models, and
  a 60-manifold/100-prompt QA cohort. Source-lock and final gate reviews are in
  progress; these remain targets, not achieved release counts.
- Ticket 07 is resolved and committed as `5725154`; its verifier derives all
  family, format, torsion, validation, and QA counts from the machine manifest.
- Ticket 08 is claimed. Its public prototype seams are the four versioned QA
  tools, with one disposable local SQLite Snapshot and shared human/agent JSON.
- The throwaway computation experiment is preserved as `25b5e07` on
  `codex/prototype-owned-homology`. Its validated interface is folded into the
  main-branch `homology_db` local preview: 60 common manifolds, eleven public-seam
  tests, a concise demo, typed safety outcomes, and evidence expansion.
- `docs/TEST_DRIVE.md` is the user handoff and `docs/NEXT_STEPS.md` is the
  Wayfinder execution route. The preview remains explicitly distinct from
  qualified `0.0.1` release evidence.
- The durable local preview and handoff were committed as `2779475`.
- A frozen twelve-question database-connected review pack now covers integral
  and field lookups, reduced conventions, example search, comparison safety,
  provenance caveats, unsupported coefficients, and a missing subject. Its
  dedicated Codex task is the next handoff action.
- The pinned Codex task `Review Homology DB answers`
  (`019f55a2-6b0b-7711-86cf-e716981cb01e`) completed all twelve questions
  read-only against Snapshot `preview-5ea7db464f937061`. Its final response is
  the human review artifact; approval remains deliberately unmarked.
- Human review identified the unresolved `CP^2` case as a corpus-
  representativeness concern. A primary-source audit confirmed that `CP^2` is
  already planned with a pinned finite Sage Model but is not part of the
  deliberately hand-built 60-subject preview.
- The external-review handoff now targets Gabriel Ong and Dan Isaksen before
  any hosting decision. Review history is append-only, and `CP^2` is the first
  post-review polish blocker rather than an ungrounded preview fact.
- `1fd137b` added the external reviewer handoff and append-only review process.
- The user then superseded the intended timing: no Gabriel Ong or Dan Isaksen
  review may begin until a separate named atlas and production-like schema pass
  their full gate. `local-preview-60` remains a frozen regression fixture.
- The execution route is now charted under
  `.scratch/named-atlas-review-v1/`, with primary-source family theorems,
  materialized `RP^0..12` and `CP^0..12`, representative hybrid Model
  evidence, finite-simplicial-set investigation, and a new QA gate.
- The external-review hold is now visible in README and the retained onboarding
  guide and append-only in `docs/REVIEW_PROCESS.md`; no prior run, decision, or
  verdict was rewritten, and `local-preview-60` remains unchanged.
- Gabriel Ong's LMFDB feedback is source-audited in
  `docs/research/icerm-lmfdb-knowl-review.md`. Versioned reviewed definition
  records and persistent labels are named-atlas data/API/QA requirements;
  inline knowl rendering and mathematical graphics remain later UI work.
- `origin` now points to `DaveArcher18/homology-db`; the previously empty
  remote accepted `main` without force at commit `6c4e99c`, and local `main`
  tracks `origin/main`.
- Online research produced a 68-question topology-agent benchmark. An initial
  89-case adversarial run exposed preview safety defects; red-green fixes and a
  72-case rerun eliminated the crashes, apparent-empty invalid queries,
  ungrounded query matches, unmarked truncation, and unbound parsed errors.
- Ticket 03 now has four executable migrations and twenty schema tests,
  including a deterministic 1,159-Model workload. Independent audit correctly
  classifies it as a partial skeleton; unsafe bare-assertion Current selection,
  mutable conflict authority, mutable claim components, dangling assertion
  subjects, dangling computation inputs/knowl links, mutable migration hashes,
  and cross-Model artifact merging were closed. A committed v3 database now
  upgrades to v4 without rewriting prior migrations. The remaining map/field
  references, populated-legacy-conflict editorial migration, reducer,
  normalization, and closure work stays explicit.
- Final standards review additionally closed late mutation of finalized
  Snapshots, arbitrary/dangling Snapshot records, and Model-free Derived
  artifacts. Snapshot construction now has an explicit draft-to-sealed
  transition and rejects all later membership/projection inserts.
- Migration application is atomic with its ledger insert. A failed v4 data
  qualification now rolls back every DDL change and preserves the v3 database.
- `33e91c2` commits the final atlas integrity/adversarial checkpoint as a
  coherent scope. Final specification and standards re-audits report no hard
  checkpoint violation after the Snapshot, provenance, migration, and commit-
  scope corrections.
- The final 72-case preview adversarial replay is machine-readable under
  `qa/audits/` and runs through the real CLI in the regular unit suite.
- The Gabriel Ong/Dan Isaksen orientation is now a deliberately simple
  four-minute Loom: two minutes on what does and does not exist, one minute on
  a coefficient-qualified lookup, and one minute on a Snapshot-bounded example
  search. Homotopy-pattern retrieval is stated as future work. Sharing it now
  is an informal development preview, not the held mathematical review.
- `LOOM_START_HERE.md` is the presenter workspace: Codex performs all Python
  preparation read-only, returns a compact readiness card, and then accepts two
  paste-ready on-camera prompts. The spoken introduction is 264 words, so the
  presenter does not need to operate a terminal or improvise the scope.
- A direct user request temporarily brought the previously deferred static Web
  UI into scope. The resulting `homology-db.static-atlas/1` exporter and
  self-contained atlas bind only to the frozen `local-preview-60` data and
  display its preview limitations. This does not resolve production-schema
  ticket 03 or lift the external-review hold.

## Exact next action

Inspect the current static-atlas view state, data shapes, formatting helpers,
and tests; pin the smallest route/view model for Home, Spaces, family, and
Conceptual-space pages; then implement the accepted feedback in vertical
slices before rebuilding and running the full review gate.

## Verification state

Baseline `d2b6399` is clean and synchronized. Its 64-test suite, deterministic
artifact, Pages run `29984104725`, and live byte comparison passed before this
iteration. No Gabriel-feedback source or artifact change is yet claimed
implemented or verified.

The release contract is documented and reviewed. Ticket 02's deterministic
script exits successfully with 22/22 observations. Ticket 03's primary-source
survey was independently split across Sage, HAP, and simpcomp/other sources,
integrated, source-reviewed, and passes `git diff --check`.
Ticket 04 is recorded in ADR 0001 and the glossary, and was independently
reviewed for mathematical, domain, and G2/G10 compatibility. No executable
database, ingested corpus, public API, or release test suite exists yet. Ticket
05 is specified in the v1 pattern contract and ADR 0002 and was independently
reviewed for formal, LLM-envelope, and indexed-query semantics.
Ticket 06 is specified in the v1 Current-projection contract and ADR 0003. Its
state-machine, editorial-history, and promotion/snapshot reviews all report no
remaining defect after two correction passes.
Ticket 07 is specified by the machine corpus manifest and its deriving
verifier. The local preview builds a deterministic 60-subject SQLite Snapshot
and passes eleven human/agent public-seam tests; it is not the 1,159-Model release.
`ruff`, Python compilation, the manifest verifier, the concise demo, SQLite
integrity, and `git diff --check` all pass at checkpoint `2779475`.
The database-connected review used one Snapshot and preserved typed failures.
The external-review documents distinguish that preview evidence from planned
corpus Models and from the future cited-implication review graph.
The named-atlas execution map is charted and its external-review-gate ticket is
resolved. The existing executable database remains only `local-preview-60`;
none of the new schema, corpus, Model-kind, definition, or QA gates is claimed
complete. The review-hold documentation and ICERM/LMFDB research passed the
scoped verification recorded in `TESTLOG.md`; the frozen preview rebuilt with
the unchanged Snapshot ID `preview-5ea7db464f937061`.
The current chromatic corpus and `/2` static exporter have 22 focused checks
while retaining the frozen preview and schema replays; the complete suite
passes 63 tests. The release candidate is a 4,097,121-byte self-contained
HTML file with 42 spaces and zero unresolved relationship/evidence references.
Browser-facing language preserves
`development_corpus_not_externally_reviewed`. GitHub Pages run `29960163529`
deployed release commit `e1d9a4b`; the live download matches the committed
artifact byte-for-byte and the live browser smoke test passed.

The redesign adds one focused static-atlas contract test, bringing the full
suite to 64 passing tests. `dist/atlas.html` is byte-identical to a clean
rebuild at SHA-256 `59f32287…d5b8da40`; JavaScript syntax and diff checks pass.
Local browser QA exercised the exact artifact at 1440×900, 390×844, and
320×720 with no horizontal overflow or console warning/error. GitHub Pages run
`29979578366` deployed synchronized `main`; the live HTTP response matches the
committed artifact byte-for-byte and the live mobile interaction smoke test
passed. Final standards, specification, and release-security reviews report no
remaining blocker.

## Recovery notes

- Preserve unrelated parent-workspace changes; this directory is now its own repository.
- Existing planning documents are inputs, not proof that implementation requirements are met.
- The standalone repository is clean at the checkpoint commits above.
- The recurring automation cannot bypass a hard quota; it retries after capacity returns.
- While `Status: BLOCKED`, recurring wakeups exit without mutation. This user
  response resumed the goal and started a fresh blocked audit.
- Ticket 05 reached three consecutive runs awaiting Question 1 on
  2026-07-11T12:49:09Z. The user then reclaimed control through this chat; no
  semantic choice was inferred.
- The recurring automation is paused. Do not create, resume, or re-enable a
  standalone worker unless the user explicitly requests it here.
- 2026-07-11T14:50:18Z: ticket 06 is fully verified but uncommitted. The sole
  blocker is the git-index escalation approval service quota; retry only after
  explicit user approval or the reported 18:26 capacity reset.
