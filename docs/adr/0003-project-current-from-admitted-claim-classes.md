---
status: accepted
---

# Project Current from admitted claim classes

Homology assertions remain immutable claim records, while an append-only
Editorial-event ledger is the sole authority for admission, supersession,
retraction, and Conflict-set lifecycle. In each Snapshot, Current projection v1
groups active same-slot assertions by a strict semantic Claim fingerprint: one
class selects a deterministic assertion-ID representative and exposes every
other member as support; several classes remain unresolved unless one explicit
maximal Conflict set declares the incompatibility. Source rank, recency, and a
manual winner may not hide other active claims.

## Consequences

- Presence is not publication, Knowledge state is not editorial status, and
  absence is still a derived lookup outcome with no assertion ID.
- The canonical supersession relation lives only in Editorial events. Old
  assertions and Snapshot answers remain addressable, and retirement never
  silently resurrects a predecessor.
- Corroborating evidence remains as independent assertions. The bytewise-smallest
  assertion ID is only a reproducible carrier for identical canonical content,
  not a reliability judgment.
- A Model result reaches a Conceptual-space slot only through a fresh Promotion
  assertion with active reviewed dependencies and a versioned preservation
  rule. Query-time tier inheritance is forbidden.
- Invalid lifecycle, conflict, promotion, or evidence graphs abort Snapshot
  publication. Multiple valid but unreconciled claims are returned honestly as
  unresolved data instead of being treated as database corruption.
