# Atlas schema prototype v1

Status: executable prototype; not the `named-atlas-review-v1` release schema

## Purpose

This prototype tests whether the production domain can be represented without
extending the conflated `local-preview-60` tables. It is migration-driven and
deliberately lives beside, not inside, `homology_db.preview`.

The public mathematical seam remains the four operations. Direct SQLite access
is permitted only in schema migration and integrity tests; database rows are
not a substitute for a public-operation answer.

## Migration boundaries

1. `0001_catalog_provenance.sql` separates Conceptual spaces and names,
   families and typed parameters, family expressions, Models, Source/Model/
   Derived artifacts, references, algorithms, environments, computation runs,
   inputs, outputs, logs, and versioned knowledge entries.
2. `0002_assertions_editorial.sql` adds immutable typed assertions, normalized
   integer groups and field dimensions, indexed primary summands, separate
   literature/computation/derivation evidence, dependencies, reviews,
   append-only editorial events, and conflicts.
3. `0003_snapshot_projection.sql` adds immutable Snapshot membership, selected
   reviewed knowledge revisions, Current Homology/Completeness projections,
   supporting assertions, and canonical-export metadata.
4. `0004_append_only_integrity.sql` upgrades v3 databases without changing the
   hashes of migrations 1--3; it rebuilds the two Model-bound artifact tables,
   Snapshot sealing, and empty conflict authority, then adds subject/target
   fences and append-only guards across catalog, computation,
   assertion-component, evidence, review, editorial, conflict-ledger,
   migration-ledger, and projection records.
   A v3 database with populated legacy conflicts is rejected for explicit
   editorial migration because its final-state membership cannot recover exact
   event history.

The migration runner hashes every SQL migration and rejects a changed migration
when reopening an existing database. Both the immutable migration ledger and a
real v3-to-v4 upgrade that preserves the first three hashes have regression
tests. Schema changes and their migration-ledger row commit atomically; a
failed upgrade rolls back every table change.

## Executably enforced trust boundaries

- the preview has no migration path into these tables;
- Conceptual spaces, Models, artifacts, assertions, evidence, and knowledge
  revisions have separate identities;
- knowledge revisions cannot satisfy assertion-evidence foreign keys;
- a Snapshot-selected knowledge revision must belong to the selected entry and
  have the exact accepted review named by the selection;
- catalog/provenance records, assertion components, evidence, reviews,
  editorial effects, conflict-ledger effects, and projections reject
  update/delete;
- computation inputs must identify an existing Source, Model, or Derived
  artifact with the same content hash, and knowledge links must identify an
  existing target of an implemented target kind;
- `unknown`, `not_computed`, and other nonexact Homology assertions cannot own
  exact integer or field values;
- byte-identical Model artifacts may belong to distinct Models and therefore
  do not silently merge Model identity; the same rule holds for Model-bound
  Derived artifacts;
- every Derived artifact belongs to exactly one Model;
- Snapshot construction uses an explicit draft state followed by one sealing
  update; after sealing, member, knowledge-selection, Current, support, and
  export inserts are rejected;
- every Snapshot record uses a recognized record kind and resolves to an
  existing record with the exact stored hash;
- a selected Current Homology assertion must occupy the same slot and be a
  hash-matching member of the Snapshot closure, have a Homology subtype and
  exact value when exact, and carry Snapshot-member evidence, accepted review,
  and admission event; Current and Snapshot rows reject in-place mutation;
- conflict membership and closure are represented as append-only ledger
  effects rather than mutable membership or resolution fields; and
- a 1,159-Model plus 1,159-artifact logical workload produces byte-identical
  canonical exports under forward and reverse insertion orders.

## Preview safety improvements driven by adversarial testing

The frozen cohort and Snapshot content are unchanged, but its public envelope
now rejects non-boolean reduced conventions, malformed argument types,
non-prime torsion-prime filters, invalid degrees and limits, and wrong-typed
query predicates. Parsed errors are Snapshot-bound. Example queries disclose
their total count and truncation, return evidence IDs, and state that coverage
is limited to selected Snapshot assertions rather than all mathematics.
The exact 72-case final replay is checked in as
[`qa/audits/preview-adversarial-2026-07-12.json`](../../qa/audits/preview-adversarial-2026-07-12.json)
and is executed by the regular unit suite through the CLI boundary.

## Deliberately unresolved before ticket completion

This checkpoint does not yet resolve the production-schema ticket. The
following still require executable adversarial fixtures and named integrity
reason codes:

- family-expression denotation through reviewed identity assertions;
- typed assertion-subtype cardinality and normalized invariant-factor checks;
- typed referential integrity for relation targets not yet represented by a
  catalog table, notably maps and public-operation fields;
- the append-only admission/supersession/conflict reducer and maximal conflict
  validation;
- an explicit, provenance-preserving editorial migration for any populated v3
  conflict fixture (v4 intentionally refuses to synthesize that history);
- dependency and supersession acyclicity;
- active Model-promotion validation;
- full transitive Snapshot closure across every source, artifact, run,
  assertion, dependency, review, and policy record;
- canonical Snapshot and Current exports for the full adversarial
  constellation, rather than only the Model-scale workload; and
- production versions of the four public operations over these projections.

No named-space Homology assertion is admitted by these migrations. Mathematical
coverage remains the responsibility of source pinning and corpus
materialization tickets.

## Question-driven acceptance input

The source-backed [topology-agent question benchmark](../research/topology-agent-question-benchmark.md)
defines 68 prospective questions. Public Q&A establishes only that a question
shape recurs; author-owned sources must still be pinned before they can ground
an expected group. The benchmark is not a claim that the current preview or
this schema prototype answers those questions.

## Verification

Run:

```bash
python3 -m unittest discover -s tests -v
ruff check homology_db tests scripts/verify_manifest_spec.py
python3 scripts/verify_manifest_spec.py
```

The test log records the red-green slices, the adversarial public-operation
audit, the 1,159-Model workload, and the unchanged frozen Snapshot identifier.
