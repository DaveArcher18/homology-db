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
