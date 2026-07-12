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

The first four executable SQLite migrations now separate the catalog,
provenance, assertion/editorial, and Snapshot/Current layers. Twenty atlas-
schema tests cover domain-table separation, reviewed knowledge selection,
definition/evidence separation, append-only base records, nonexact-value
fences, grounded Snapshot closure for Current, and a deterministic
1,159-Model/1,159-artifact workload under reversed insertion order. The fourth
migration extends append-only guards, rejects dangling assertion subjects,
uses an append-only conflict ledger, and preserves separate Model identity when
artifacts have identical bytes.
Applied migration hashes are append-only and regression-tested against
in-place rewrite. A real v3 database upgrades to v4 without changing the first
three migration hashes. Byte-identical Derived artifacts also retain their
distinct Model provenance.
Because v3 stores only final conflict membership, v4 rejects a populated legacy
conflict for explicit editorial migration instead of fabricating causal event
timing; that refusal and preservation of the v3 rows are regression-tested.
Computation inputs now require a typed, hash-matching artifact, and knowl links
require an existing target of an implemented target kind.
Derived artifacts require a Model. Snapshot records require a recognized,
hash-matching target, and a Snapshot may be populated only while in its draft
state; its single finalization seals every member and projection table against
later inserts.
Migration SQL and its ledger row are one transaction; a deliberately invalid
v3 Derived artifact proves a failed v4 upgrade restores the complete v3 schema
and data rather than leaving an unledgered partial migration.

This is deliberately a partial checkpoint, not an answer to the ticket. The
remaining integrity and adversarial-constellation work is itemized in
[`docs/contracts/atlas-schema-prototype-v1.md`](../../../docs/contracts/atlas-schema-prototype-v1.md).
In particular, the editorial reducer, conflict maximality, normalized group
audits, family specialization, Model promotion, complete transitive closure,
and canonical full-Snapshot/Current rebuild are not yet proven.
