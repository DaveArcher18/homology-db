# Static atlas read model

Status: development frontend over `chromatic-gateway-42`

Read-model version: `homology-db.static-atlas/3`

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
| Space relationships | 11 |
| Recorded computation runs | 41 |
| Homology coverage records | 42 |
| Homology assertions | 4,190 |
| Primary-summand rows | 252 |

The checked-in release candidate has Snapshot ID
`chromatic-16e4f2be46edd93a`. Its disposable SQLite database is 2,535,424
bytes with SHA-256
`4c9791aba051dec8b0fe5643f710e0fb674426ff96a65b730eef46c469da820f`.
The generated `dist/atlas.html` is 4,097,121 bytes with SHA-256
`f1d3742018f40e74c6dd2378e331623728aa5a0be3b5d05d3dd077890954c36c`.
The same measurements, Snapshot identity, source commit, generation time, and
record counts are embedded in the artifact. The one-file exporter enforces the
5 MiB cap and rejects external script, stylesheet, font, or image dependencies.

## Mapping

Physical SQLite names stay inside the Python adapter. Browser JavaScript sees
only the denormalized `/3` read model:

| Atlas field | Authoritative input |
|---|---|
| Snapshot identity, scope, count, degree bound, and release state | `ChromaticTools.corpus_summary()` plus the one Snapshot record |
| Family label, summary, relevance, order, and membership | `family` records and each space's recorded family ID |
| Stable Conceptual-space ID | `space.space_id` |
| English name, curated TeX display name, aliases, parameters, tags, finite-type state, dimension, components, summary, and chromatic relevance | recorded `space` and `alias` fields plus a deterministic family/parameter TeX projection |
| Homology and Knowledge state | `ChromaticTools.read_homology()` for every supported coefficient and reduced choice |
| Coverage | the tool response cross-checked against `homology_coverage` |
| Model | `ChromaticTools.expand_evidence()`, including construction, cells or cell formula, attaching map, cellular boundary formula, scope, and optional pinned artifact |
| Citation | typed reference links with role and pinpoint locator from expanded Evidence |
| Computation sketch | expanded Evidence; always present and not represented as a run |
| Computation run | the nullable expanded run record; absent for the citation-backed Poincare calculation |
| Relationship | recorded source, typed target, detail, and source-owned Evidence link from `space_relation` |
| Raw record | stable tool responses and the database subject projection for review/download |
| Definition knowls | atlas-editorial exposition identified by stable `id` plus integer `revision`, with `selected_for_snapshot_id` bound to this Snapshot; explicitly not assertion Evidence and not a substitute for missing homology-convention metadata |

The adapter adds stable-ID-derived slugs, deterministic display ordering,
display labels, source-file revision metadata, and static data-quality
diagnostics. It does not infer a missing mathematical assertion or turn an
unknown/not-computed state into zero.

## Coverage semantics

Every finite CW space has `kind = complete_finite_cw`, a bound equal to its
dimension, and `upper_vanishing_starts_at = dimension + 1`. The frontend shows
the green exhaustive state for a selected coefficient/convention only when
every row through that bound is present and exact.

Every infinite finite-type space has `kind = bounded_through_degree`, a null
dimension, a current computation bound of 24, and a null upper-vanishing field.
The frontend renders that distinction next to the Homology table. A missing row
above degree 24 is not a zero assertion.

## Export invariants

- Stable Conceptual-space, slug, Model, Evidence, Computation, and Relationship IDs are
  unique within the Snapshot.
- Every Conceptual space has separate nonempty English and curated TeX display
  names. Definition IDs are unique, every definition has the supported
  editorial revision and is explicitly selected for the exported Snapshot,
  and every definition is non-evidentiary exposition.
- Every Conceptual space appears exactly once in a data-backed family section.
- Every space has a qualified Model, Evidence, computation sketch, and at least
  one citation with an HTTPS URL, source role, and pinpoint locator.
- Model and Evidence identity and input hashes agree. A Model artifact path and
  hash are either both present and verified or both absent.
- Every Homology row names its theory, coefficient, reduced choice, degree,
  Knowledge state, assertion, and Evidence. Recorded computation IDs resolve.
- Every Relationship names its source, type, in-Snapshot target, explanatory
  detail, and source-owned Evidence record. The current build has zero
  unresolved relationship or evidence references.
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
