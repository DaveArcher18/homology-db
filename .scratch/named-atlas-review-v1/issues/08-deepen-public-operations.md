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
- All envelopes are schema-versioned. `outside_materialized_range` and
  `model_not_qualified` are typed outcomes and never aliases for mathematical
  zero, absence, or `not_computed`.
