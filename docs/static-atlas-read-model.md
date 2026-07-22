# Static atlas read model

Status: development frontend over `chromatic-gateway-42`

Read-model version: `homology-db.static-atlas/2`

## Source selection

The public atlas is generated from the deterministic disposable database built
by `homology_db.chromatic.ChromaticDatabase`. The older
`local-preview-60` database remains a frozen regression fixture and is not the
source of this frontend.

The current database contains:

| Record | Count |
|---|---:|
| Snapshot | 1 |
| Families | 17 |
| Conceptual spaces | 42 |
| Aliases | 172 |
| Qualified Models | 42 |
| References | 9 |
| Evidence records | 42 |
| Evidence-to-reference links | 62 |
| Recorded computation runs | 41 |
| Homology coverage records | 42 |
| Homology assertions | 4,190 |
| Primary-summand rows | 252 |

The exact byte sizes, hashes, Snapshot ID, source commit, generation time, and
counts are embedded in each generated artifact rather than treated as stable
prose constants. The one-file exporter enforces the product requirement that
`dist/atlas.html` remain below 5 MiB and contain no external script,
stylesheet, font, or image dependency.

## Mapping

Physical SQLite names stay inside the Python adapter. Browser JavaScript sees
only the denormalized `/2` read model:

| Atlas field | Authoritative input |
|---|---|
| Snapshot identity, scope, count, degree bound, and release state | `ChromaticTools.corpus_summary()` plus the one Snapshot record |
| Family label, summary, relevance, order, and membership | `family` records and each space's recorded family ID |
| Stable Conceptual-space ID | `space.space_id` |
| Name, aliases, parameters, tags, finite-type state, dimension, components, summary, and chromatic relevance | recorded `space` and `alias` fields |
| Homology and Knowledge state | `ChromaticTools.read_homology()` for every supported coefficient and reduced choice |
| Coverage | the tool response cross-checked against `homology_coverage` |
| Model | `ChromaticTools.expand_evidence()`, including construction, cells or cell formula, attaching map, cellular boundary formula, scope, and optional pinned artifact |
| Citation | typed reference links with role and pinpoint locator from expanded Evidence |
| Computation sketch | expanded Evidence; always present and not represented as a run |
| Computation run | the nullable expanded run record; absent for the citation-backed Poincare calculation |
| Raw record | stable tool responses and the database subject projection for review/download |

The adapter adds stable-ID-derived slugs, deterministic display ordering,
display labels, source-file revision metadata, and static data-quality
diagnostics. It does not infer a missing mathematical assertion or turn an
unknown/not-computed state into zero.

## Coverage semantics

Every finite CW space has `kind = complete_finite_cw`, a bound equal to its
dimension, and `upper_vanishing_starts_at = dimension + 1`.

Every infinite finite-type space has `kind = bounded_through_degree`, a null
dimension, a current computation bound of 24, and a null upper-vanishing field.
The frontend renders that distinction next to the Homology table. A missing row
above degree 24 is not a zero assertion.

## Export invariants

- Stable Conceptual-space, slug, Model, Evidence, and Computation IDs are
  unique within the Snapshot.
- Every Conceptual space appears exactly once in a data-backed family section.
- Every space has a qualified Model, Evidence, computation sketch, and at least
  one citation with an HTTPS URL, source role, and pinpoint locator.
- Model and Evidence identity and input hashes agree. A Model artifact path and
  hash are either both present and verified or both absent.
- Every Homology row names its theory, coefficient, reduced choice, degree,
  Knowledge state, assertion, and Evidence. Recorded computation IDs resolve.
- Every coefficient/reduced combination is present in every degree covered by
  that record.
- Finite and finite-type coverage satisfy the rules above.
- A non-`exact` Knowledge state is rendered by state, never by numeric payload.
- Embedded JSON escapes HTML/script delimiters and Unicode line separators.
- Output order and bytes are deterministic for one database. A `current` build
  derives its timestamp from the latest committed mathematical/frontend source
  input, so unrelated documentation commits do not perturb artifact parity.
- The browser never opens SQLite, performs background network requests, or
  names physical database tables.

## Feedback boundary

The atlas stays self-contained and account-free for browsing. Per-space and
per-family feedback links and the request-a-space link open structured GitHub
Issue Forms only after a user click. Space/family and Snapshot identity are
prefilled in the issue title. GitHub authentication is required only to submit
the external form; the atlas has no embedded account, comment, moderation, or
write backend.

## Build and publication

Build the checked-in artifact with:

```bash
python3 scripts/export_static_atlas.py \
  --snapshot current \
  --output dist/atlas.html
```

Normal export fails on malformed identity, model, citation, evidence,
computation, coverage, or section data. A validator may add
`--allow-malformed-for-review` to create an explicitly diagnostic local
artifact; the checked-in deployment never uses that flag.

The repository's GitHub Pages workflow publishes the exact checked-in
`dist/atlas.html` from `main`. Release verification compares the downloaded
live file byte-for-byte with that artifact before the deployment is reported
ready for testing.
