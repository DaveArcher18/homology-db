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
