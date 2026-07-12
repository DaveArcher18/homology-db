Type: prototype
Status: open
Claimed by:
Claimed at:
Blocked by: 03, 07

# Deepen the four public operations

## Question

What schema-versioned envelopes let `resolve_subject`, `read_homology`,
`query_examples`, and `expand_evidence` expose family coverage, identity and
Model assertions, literature/computation/specialization derivations, source
pinpoints, implication dependencies, reviews, and typed
`outside_materialized_range` or `model_not_qualified` outcomes without hidden
inference?

## Acceptance criteria

- `resolve_subject` returns typed family parameters, aliases, identity
  assertions, and bounded-coverage status.
- `read_homology` distinguishes literature, owned-computation, and derived
  specialization assertions.
- `query_examples` searches only materialized assertions selected into the
  requested immutable Snapshot.
- `expand_evidence` returns structured references and pinpoints, source and
  artifact hashes, computation runs, algorithms, environments and logs,
  assertion dependencies, reviews, and Model qualification status.
- Responses attach stable definition references to mathematical terms, search
  fields, supported input syntax, Knowledge states, and source/completeness/
  reliability labels. `expand_evidence` can expand those records through a
  separately typed request while keeping their explanatory role distinct from
  assertion evidence.
- Each `knowledge_ref` resolves within the response Snapshot and exposes its
  entry ID, selected revision ID, title, short display text, review status,
  content hash, and `role: exposition`. A missing definition is a distinct
  editorial gap, never a failed mathematical assertion or zero.
- Public subject labels are persistent, mathematically meaningful where
  possible, concise, and separately documented; aliases never create a silent
  identity or change the permanent subject identifier.
- All envelopes are schema-versioned. `outside_materialized_range` and
  `model_not_qualified` are typed outcomes and never aliases for mathematical
  zero, absence, or `not_computed`.
