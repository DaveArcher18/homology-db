# Static atlas read model

Status: development frontend over the frozen `local-preview-60` Snapshot

## Source selection

The atlas exporter binds to the database that is useful today: the disposable
60-subject preview built by `homology_db.preview.PreviewDatabase`. The newer
migration-driven atlas schema is a production-shape prototype, but it does not
yet contain named-space Homology assertions and therefore cannot supply this
frontend honestly.

The measured preview database is **1,167,360 bytes** (285 SQLite pages of 4,096
bytes). Its current record counts are:

| Preview record | Count |
|---|---:|
| Snapshot | 1 |
| Conceptual spaces | 60 |
| Aliases | 181 |
| Homology assertions | 2,570 |
| Evidence records | 60 |
| Primary summands | 60 |

The generated self-contained HTML is **2,065,520 bytes**. It is below the PRD's
5 MB one-file threshold and contains no external script, stylesheet, font, or
image dependency.

## Mapping

Physical SQLite names remain inside the Python adapter. Browser JavaScript sees
only `homology-db.static-atlas/1`:

| Atlas field | Authoritative input |
|---|---|
| Snapshot identity and count | `Tools.corpus_summary()` plus the one Snapshot record |
| Stable Conceptual-space ID | preview Conceptual-space ID |
| Display name, family, dimension, model-relation qualifier | preview subject record |
| Aliases and notation | recorded preview aliases |
| Homology | `Tools.read_homology()` for each recorded coefficient and reduced choice, qualified by ordinary theory and a Snapshot-versioned convention identity |
| Evidence and algorithm capability | `Tools.expand_evidence()` |
| Computation runs | empty, because the preview has no distinct run records with inputs, outputs, environment, parameters, and logs |
| Models and relations | empty arrays, because the preview exposes no qualified records of those kinds |
| Raw record | stable tool responses and their source subject record |

The adapter adds display-only labels, deterministic stable-ID-derived slugs,
section membership from the recorded family, source hashes, and read-model
metadata. It does not add mathematical assertions or infer taxonomy.

## Export invariants

- Stable IDs and slugs are unique.
- Every Conceptual space appears in exactly one data-backed section.
- Every Homology row names its theory, coefficient system, versioned
  convention, reduced choice, degree, Knowledge state, and evidence.
- Every Homology evidence reference resolves before output is written.
- A non-`exact` Knowledge state is rendered by state, never by a numeric value.
- Knowledge state, evidence reliability, Snapshot release status, and
  Computation runs remain separate. Missing reliability or run records are
  reported as missing rather than synthesized.
- Output order and bytes are deterministic for one input Snapshot; the
  `--snapshot current` build is deterministic at a fixed source commit.
- Embedded JSON escapes HTML/script delimiters and Unicode line separators.
- The browser receives denormalized JSON and never opens SQLite or names its
  physical tables.

Build the checked-in artifact with:

```bash
python3 scripts/export_static_atlas.py \
  --snapshot current \
  --output dist/atlas.html
```

The command prints the Conceptual-space and evidence counts, unresolved-reference count,
HTML byte size, and source database SHA-256.
