Type: grilling
Status: resolved
Claimed by: /root (interactive chat)
Claimed at: 2026-07-11T14:20:01Z
Resolved at: 2026-07-11T14:48:15Z
Blocked by: 02, 04

# Define assertion selection and correction semantics

## Question

Given literature and computed assertions, conflicts, corrections, supersession, incomplete computations, and model-to-space promotion, what deterministic semantics produce a current projection without inventing facts or erasing history?

## Grill record

- The user explicitly said to proceed and challenged the previous ticket-boundary
  yield. No new user choice was required: tickets 02 and 05 already forbid
  source-priority winners, implicit conflict, absence-as-zero, and read-time
  tier promotion.
- Three independent audits challenged the state reducer, editorial lifecycle,
  and promotion/snapshot boundary. Their final passes found and corrected
  admission/absence contradictions, silent dependency invalidation, arbitrary
  representative coupling, partial Conflict-set semantics, event-order
  ambiguity, and missing Completeness read projections. All three reported no
  remaining defect after correction.

## Answer

Current projection v1 is a deterministic Snapshot fold with three separate
axes: immutable mathematical claim, explicit Admission decision, and derived
projection outcome. A Knowledge state is never an editorial status, and merely
retaining an assertion never makes it selectable.

An append-only Editorial-event ledger is the sole lifecycle authority.
Assertions carry no mutable current/publication/conflict status and no second
canonical supersession field. One event has one total ledger position and an
unordered canonical set of effects with joint atomic pre/post semantics.
Correction or supersession admits fresh same-slot successors and terminally
retires predecessors; retraction never asserts a mathematical negation and
never resurrects an earlier assertion.

For each complete Homology slot, active admitted assertions are partitioned by
a strict versioned Claim fingerprint over slot, Knowledge state, typed payload,
and completeness semantics. With no active assertions the outcome is `absent`.
One fingerprint class selects the bytewise-smallest assertion ID only as a
deterministic carrier and returns all other members as Supporting assertions.
Several classes yield `unresolved_selection`; source rank, recency, exactness,
or a manual winner cannot hide them.

Conflict remains explicit. One open maximal Conflict set names the active
assertions participating in registered incompatibility edges; nonconflicting
active states may remain outside it. A valid open set produces `conflicting`
with its member IDs and no selected value. Malformed/stale conflict history is a
Snapshot-integrity failure, whereas several undeclared claim classes are valid
unresolved data.

Model-to-space promotion never occurs through a query join. It creates a new
Conceptual-space assertion pinned to an active source assertion in a selected
exact-complete Model claim class, its fingerprint/value, an admitted reviewed
`model_of` assertion, and a versioned preservation rule. V1 does not promote
bounds, conjectures, incomplete exact claims, unknown, not-computed, or
not-applicable states. Completeness and vanishing use the same explicit target
assertion discipline. Invalid active dependencies abort Snapshot publication;
they never silently remove a result.

The derived read model materializes Homology and Completeness projections with
stable reason codes, selected/support/conflict IDs, exact primary rows, policy
and record digests, and per-assertion provenance/promotion lineage. Rebuilds and
incremental builds from identical Snapshot inputs must be byte-identical and
input-row-order independent.

## Evidence

- [Current assertion projection contract v1](../../../docs/contracts/current-projection-v1.md)
  gives the normative claim schemas, event effects, reducer, promotion rule,
  materialized-view obligations, integrity boundary, and 27 adversarial fixture
  classes.
- [ADR 0003](../../../docs/adr/0003-project-current-from-admitted-claim-classes.md)
  records the admitted-claim-class architecture and rejection of implicit
  winners or query-time promotion.
- [The domain glossary](../../../CONTEXT.md) now defines Claim fingerprint,
  Admission decision, Active/Retired/Supporting assertions, and Promotion
  assertion, and sharpens Current projection, Editorial event, Conflict set,
  and Unresolved selection.
