Type: prototype
Status: claimed
Claimed by: /root (interactive chat)
Claimed at: 2026-07-12T12:49:29Z
Blocked by: 01

# Prototype the production assertion and provenance schema

## Question

What versioned SQLite migrations and executable adversarial constellation
prove the separation of Conceptual spaces, families and instances, Models and
artifacts, references, computations, assertions and completeness, implication
dependencies, editorial history, reviews, Snapshots, and Current projections
at the planned 1,159-Model scale?

## Acceptance criteria

- Versioned migrations separately represent Conceptual spaces, names, family
  definitions, typed parameters, family instances, Models, Source artifacts,
  Model artifacts, and Derived artifacts.
- Structured references and pinpoints are distinct from computation runs;
  each run records immutable inputs, outputs, algorithms, environments, and
  logs with resolvable content hashes.
- Versioned definition records have stable hierarchical identifiers, precise
  titles, short context-independent bodies, editorial/review history, and
  optional citation dependencies. They remain distinct from evidence records
  and cannot ground a Homology assertion merely by defining its terminology.
- The executable design includes separate knowledge-entry identity, immutable
  revision, revision-specific review, typed link, and Snapshot-selection
  records. A Snapshot selects one exact reviewed revision; renames add aliases
  or redirects, and corrections append revisions rather than rewriting text.
- Homology and Completeness assertions are immutable and normalize integer
  groups, supported-field dimensions, and indexed primary summands without
  using missing rows as zero.
- Assertion dependencies distinguish cited implication and specialization
  edges. Editorial events separately record admission, conflicts, reviews,
  corrections, Snapshot membership, and deterministic Current projections.
- An executable adversarial constellation covers multiple Models per space,
  citation-only assertions, family specialization, identities without merging,
  correction and conflict history, Model promotion, and reviewed implication
  edges, plus a corrected definition whose prior version remains addressable.
- Deterministic rebuild and integrity tests exercise the logical schema at the
  planned 1,159-Model workload before any physical-database decision.

## Checkpoint: 2026-07-12 testing tranche

The first three executable SQLite migrations now separate the catalog,
provenance, assertion/editorial, and Snapshot/Current layers. Seven atlas-
schema tests cover domain-table separation, reviewed knowledge selection,
definition/evidence separation, append-only base records, nonexact-value
fences, grounded Snapshot closure for Current, and a deterministic
1,159-Model/1,159-artifact workload under reversed insertion order.

This is deliberately a partial checkpoint, not an answer to the ticket. The
remaining integrity and adversarial-constellation work is itemized in
[`docs/contracts/atlas-schema-prototype-v1.md`](../../../docs/contracts/atlas-schema-prototype-v1.md).
In particular, the editorial reducer, conflict maximality, normalized group
audits, family specialization, Model promotion, complete transitive closure,
and canonical full-Snapshot/Current rebuild are not yet proven.
