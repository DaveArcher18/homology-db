# Test log

## 2026-07-11 — local preview checkpoint

Environment: Python 3.10.16; SQLite 3.45.3; macOS development workspace.

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 12/12 public-seam and review-pack tests passed |
| `ruff check homology_db tests scripts/verify_manifest_spec.py` | all checks passed |
| `python3 scripts/verify_manifest_spec.py` | derived 174 curated spaces, 1,159 planned Models, 138 torsion pairs, and 100 QA prompts |
| `python3 -m homology_db demo` | built the deterministic 60-subject Snapshot and completed the concise tour |
| SQLite `PRAGMA integrity_check` | `ok` on the generated preview database |

The local `/usr/local/bin/sage` launcher failed because its referenced
`SageMath-9-6.app` is absent. The preview therefore uses only the standard
library. Production Sage 10.9 versus FLINT adapter benchmarking remains part of
the owned-computation ticket; this environment failure is not treated as a
platform decision.

## 2026-07-12 — database-connected review task

Pinned Codex task `Review Homology DB answers`
(`019f55a2-6b0b-7711-86cf-e716981cb01e`) completed the twelve-question review
pack read-only. It reported 12/12 preflight tests, used only Snapshot
`preview-5ea7db464f937061`, grounded group claims with returned assertion and
evidence IDs, expanded subject evidence, and retained typed outcomes for the
unsupported rational-coefficient and unresolved `CP^2` questions. Human
mathematical and UX approval is intentionally pending in that task.

## 2026-07-12 — external reviewer handoff

Scope: documentation-only handoff, source-backed example prioritization, and
append-only review logging. The frozen `local-preview-60` database behavior and
question manifest were not changed.

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 12/12 tests passed |
| `ruff check homology_db tests scripts/verify_manifest_spec.py` | all checks passed |
| `python3 -m compileall -q homology_db tests scripts` | passed |
| `python3 scripts/verify_manifest_spec.py` | re-derived 174 curated spaces, 1,159 planned Models, 128 common manifolds, 138 torsion pairs, and 100 QA prompts |
| `python3 -m homology_db --db /tmp/homology-db-doc-verification.sqlite3 demo` | rebuilt the 60-subject Snapshot `preview-5ea7db464f937061` and completed the tour |
| starting reviewer prompt | manually replayed R01--R12 and three free-form questions against `/tmp/homology-db-external-review.sqlite3`; all 46 responses used one Snapshot and preserved grounding/typed gaps |
| adversarial reviewer prompt | manually replayed all six cases against `/tmp/homology-db-adversarial-review.sqlite3`; typed `CP^2` and rational-coefficient failures, comparison safety, reduced `F5`, 5-primary search, and capability states all remained explicit on one Snapshot |
| Markdown local-link and code-fence check | every referenced local target exists; all checked fenced blocks are balanced |
| two-axis standards/spec review | initial reproducibility findings corrected; final re-audits reported no remaining hard defect |
| `git diff --check` | passed after the final review corrections |

The adversarial replay used only `resolve_subject`, `read_homology`,
`query_examples`, and `expand_evidence`. Its before/after status showed the
same intended documentation changes and no additional repository mutation.
The starting-prompt replay used the same four operations, built its database
once, retained Snapshot `preview-5ea7db464f937061` through both phases, and is
recorded with its exact ordered payloads in `docs/REVIEW_PROCESS.md`.
Remote research links were opened during the primary-source survey; they are
reference inputs, not database evidence for preview answers.

## 2026-07-12 — named-atlas execution-map checkpoint

Scope: planning and continuity only. This checkpoint adds the active
`named-atlas-review-v1` Wayfinder map and its blocking tickets; it does not
claim that the production schema, named corpus, or reviewer gate exists.

| Check | Result |
| --- | --- |
| Wayfinder ticket graph audit | ten tickets are numbered uniquely; every blocker exists; the first frontier is `Supersede the external-review gate`; publication and external review remain blocked |
| `python3 -m unittest discover -s tests -v` | 12/12 tests passed |
| `ruff check homology_db tests scripts/verify_manifest_spec.py` | all checks passed |
| `python3 -m compileall -q homology_db tests scripts` | passed |
| `python3 scripts/verify_manifest_spec.py` | re-derived 174 curated spaces, 1,159 planned Models, 128 common manifolds, 138 torsion pairs, and 100 QA prompts |
| `python3 -m homology_db --db /tmp/homology-db-named-atlas-map.sqlite3 demo` | rebuilt the frozen 60-subject Snapshot `preview-5ea7db464f937061` and completed the tour |
| `git diff --check` | passed |
| two-axis standards/spec review | initial map-specificity findings corrected; final re-audits reported no remaining defect |

The first graph-audit invocation had a shell quoting syntax error and did not
execute repository code. The simplified rerun passed and produced the result
recorded above.

## 2026-07-12 — review hold and ICERM/LMFDB feedback

Scope: documentation, research, and execution-map acceptance criteria. The
frozen `local-preview-60` implementation and database contents were not
changed.

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 12/12 tests passed |
| `ruff check homology_db tests scripts/verify_manifest_spec.py` | all checks passed |
| `python3 -m compileall -q homology_db tests scripts` | passed |
| `python3 scripts/verify_manifest_spec.py` | re-derived 174 curated spaces, 1,159 planned Models, 128 common manifolds, 138 torsion pairs, and 100 QA prompts |
| `python3 -m homology_db --db /tmp/homology-db-knowl-review.sqlite3 demo` | rebuilt unchanged Snapshot `preview-5ea7db464f937061` with 60 subjects |
| modified Markdown local-link check | 15 files checked; 34 local links resolve; code fences balanced |
| Wayfinder blocker/frontier audit | review hold resolved; publication, schema, and finite-simplicial-set admission are the open frontier |
| `git diff --check` | passed |

The first frontier-audit invocation over-escaped its digit-matching expression
and failed inside the checker. The corrected read-only audit printed the actual
ticket states and passed; no repository code failed.

## 2026-07-12 — question-driven adversarial and schema testing

Scope: online question research, adversarial testing through the four public
operations, preview safety hardening without changing the 60-subject cohort,
and the first separate production-schema migrations.

### Research and adversarial breadth

- A primary-source research agent produced 68 ordered prospective questions
  across named families, coefficients and reduced conventions, constructions,
  comparison safety, provenance/editorial history, and typed unsupported
  boundaries. Public Q&A is used only as question-pattern evidence; Hatcher,
  May, official Sage documentation, and repository contracts are the proposed
  assertion-evidence sources.
- A read-only adversarial agent ran 89 initial CLI/envelope cases against one
  disposable Snapshot. It found four crashes, unsafe acceptance of non-boolean
  `reduced`, invalid/truncated searches that could resemble mathematical
  emptiness, unbound error envelopes, string/dictionary iteration bugs, and
  missing query evidence IDs.
- After the red-green fixes, the agent ran 72 focused cases with zero crashes
  and confirmed every original safety defect fixed. A manual follow-up verified
  that integral-valued JSON floats for degree, torsion prime, and limit are also
  rejected as `invalid_pattern`; the agent's contrary three-case note was stale
  relative to the final files.

### Red-green public-seam slices

Each preview change was first observed failing through `Tools.call`,
`query_examples`, or the CLI JSON envelope, then made green:

1. non-boolean `reduced` cannot select empty groups;
2. malformed public argument types return Snapshot-bound errors, not crashes;
3. invalid degrees, primes, limits, and reduced predicates cannot prove an
   empty result;
4. wrong-typed family/coefficient/torsion/free-rank predicates are rejected;
5. bounded result sets expose total count and truncation;
6. query matches include evidence IDs;
7. empty searches disclose Snapshot-bounded, non-global coverage;
8. unknown/missing/nonstring tool names have typed Snapshot-bound envelopes;
9. invalid CLI JSON is bound to the already-built Snapshot; and
10. the original supported mathematical lookups remain unchanged.

### Atlas-schema slices

- Four hashed SQLite migrations separate Conceptual spaces, names/families,
  Models and three artifact kinds, structured references, runs, immutable
  assertions, normalized group representations, evidence/dependencies,
  editorial history, conflicts, knowledge revisions, Snapshots, and Current.
- Integrity tests reject mismatched/unreviewed Snapshot knowls, knowledge prose
  used as assertion evidence, in-place base assertion/knowledge rewrites,
  values on nonexact assertions, and Current selection without a same-slot
  Homology subtype, exact value when exact, typed evidence, accepted review,
  admission event, and hash-matching Snapshot closure.
- The post-audit correction pass also rejects mutation of claim components,
  reviews, events, and projection records; replaces mutable conflict authority
  with an append-only ledger; rejects dangling assertion subjects; and permits
  distinct Models to retain byte-identical Model artifacts without merging.
  Typed, hash-matching artifact inputs and existing-target knowl links are also
  enforced.
- A review-discovered migration-history defect was corrected by restoring
  migrations 1--3 byte-for-byte and moving table replacements into migration
  4. The suite builds a v3 database, upgrades it to v4, and verifies that all
  three prior hashes are unchanged. The migration ledger itself is append-only;
  byte-identical Derived artifacts retain separate Model provenance.
- A populated-v3 fixture proves v4 refuses legacy conflicts for explicit
  editorial migration and leaves their rows intact. The migration does not
  fabricate declaration times for later members or erase removed members.
- Forward and reverse insertion of 1,159 synthetic Models and 1,159 Model
  artifacts produce byte-identical canonical logical exports.
- An independent schema audit found this remains a skeleton rather than a safe
  complete production projection. The unresolved reducer, normalization,
  conflict, promotion, completeness, immutability, and closure requirements are
  retained in `docs/contracts/atlas-schema-prototype-v1.md`; ticket 03 remains
  claimed rather than falsely resolved.

### Verification

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 37/37 tests passed, including an exact 72-case CLI replay from the checked-in audit artifact |
| `ruff check homology_db tests scripts/verify_manifest_spec.py` | all checks passed |
| `python3 -m compileall -q homology_db tests scripts` | passed |
| `python3 scripts/verify_manifest_spec.py` | re-derived 174 curated spaces, 1,159 planned Models, 128 common manifolds, 138 torsion pairs, and 100 QA prompts |
| frozen preview demo and Snapshot check | rebuilt 60 subjects with unchanged Snapshot `preview-5ea7db464f937061` |
| SQLite `PRAGMA integrity_check` and `foreign_key_check` for atlas workload | `ok`; no foreign-key violations; 1,159 Models and 1,159 artifacts; canonical SHA-256 `2fe3f2cbb1eebe62ca32be9380f910ce6514fe951e6f2e2987983401b91df0c6` |
| Markdown links, benchmark IDs, and `git diff --check` | 9 changed Markdown files and 32 local links checked; code fences balanced; 68 unique benchmark IDs; diff check passed |
| independent two-axis code review | initial migration, provenance, conflict-history, immutability, and referential-integrity findings corrected; final specification and standards re-audits found no hard checkpoint violation |

The first benchmark-ID command over-escaped its table-row regular expression
and matched empty alternatives throughout the document. The corrected literal
row matcher found exactly 68 unique IDs; no benchmark content failed.
The first combined final Markdown-check one-liner had a Python syntax error and
did not execute its checks. The corrected invocation produced the 9-file,
32-link, 68-ID passing result recorded above.

The machine-readable final adversarial cases are retained in
[`qa/audits/preview-adversarial-2026-07-12.json`](qa/audits/preview-adversarial-2026-07-12.json).
The replay builds the database once, exercises only the public CLI boundary
and the four supported operations, checks all 72 unique cases, verifies the
recorded implementation hashes, and requires every response—even invalid JSON
and unknown-tool envelopes—to name Snapshot `preview-5ea7db464f937061`.

Packaging status: the final staging request at 15:32 SAST was rejected because
the Git approval service reported its usage quota exhausted until 16:20. No
workaround was attempted; the verified changes remain intact and unstaged for
the next authorized run.

## 2026-07-12 — reviewer Loom planning and packaging retry

Scope: record a durable video/email handoff plan without reopening the external
review gate, then package the complete verified testing and schema checkpoint.

- `docs/LOOM_WALKTHROUGH.md` contains a timed 7--9 minute storyboard, separate
  internal-rehearsal and external-review cuts, clean-clone recording setup,
  final named-atlas demonstrations, reviewer prompt, role-specific email draft,
  recording checklist, and append-only run metadata template.
- `docs/REVIEW_PROCESS.md` records the communication plan as
  `review-2026-07-12-008`. It is explicitly not a mathematical review and does
  not supersede the held-review decision.
- README and the retained external-review guide link the plan while preserving
  the `named-atlas-review-v1` send gate.

The prior implementation result was not silently reused. This packaging retry
reran the complete gate:

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 41/41 tests passed, including the 72-case CLI audit, Snapshot sealing, target/hash validation, and atomic migration rollback |
| `ruff check homology_db tests scripts/verify_manifest_spec.py` | all checks passed |
| `python3 -m compileall -q homology_db tests scripts` | passed |
| `python3 scripts/verify_manifest_spec.py` | re-derived 174 curated spaces, 1,159 planned Models, 128 common manifolds, 138 torsion pairs, and 100 QA prompts |
| frozen preview demo | rebuilt 60 subjects at unchanged Snapshot `preview-5ea7db464f937061` |
| 1,159-Model atlas workload | SQLite integrity `ok`; no foreign-key violations; canonical SHA-256 `2fe3f2cbb1eebe62ca32be9380f910ce6514fe951e6f2e2987983401b91df0c6` |
| Markdown plan/link/fence audit | 12 changed Markdown files; all 43 local links resolve; fences balanced; 68 unique benchmark IDs |
| adversarial audit JSON and `git diff --check` | valid and passed |
| final two-axis review against `origin/main` | specification and standards re-audits found no hard checkpoint violation after corrections |

The first final standards review found that finalized Snapshot rows could still
receive late members/projections, Snapshot records admitted arbitrary dangling
kinds, and Derived artifacts could lack Models. Three new red-green schema
tests now require a Model-bound Derived artifact, a recognized hash-matching
Snapshot member, and a one-way draft-to-sealed Snapshot transition that rejects
late member and projection inserts. The complete suite therefore contains 40
tests. A fourth red-green test then exposed non-atomic migration DDL: a legacy
Model-free Derived artifact could fail v4 after earlier table replacements had
committed. Migration SQL and its ledger row now share one transaction, and the
failure fixture proves the entire v3 schema and row survive. The complete suite
therefore contains 41 tests; the final verification table above records the
correction review result.

The initially mixed correction/Loom commit was removed before publication.
Atlas integrity and adversarial testing are committed coherently as `33e91c2`;
the Loom, email, review-process, and continuity documentation are packaged as a
separate documentation commit.
