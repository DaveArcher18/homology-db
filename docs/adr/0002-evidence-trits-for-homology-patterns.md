---
status: accepted
---

# Use evidence trits for homology-pattern matching

Homology DB evaluates every mathematical Pattern clause as `proven_true`,
`proven_false`, or `unresolved` against one snapshot-bound Current projection.
This prevents missing, incomplete, disputed, or merely conjectural data from
becoming a negative mathematical answer while still allowing an LLM to request
and inspect unresolved candidates separately.

## Consequences

- A normalized v1 pattern is a nonempty conjunction over exactly one corpus
  tier. A `slot_clause` has one Candidate-bound slot selector, one typed
  predicate, and `require` or `forbid` polarity; a require-only
  `exact_signature_clause` is the explicit ranged macro exception.
- `unknown` is narrow: it is one selected atomic Knowledge state. Absence,
  not-computed, not-applicable, unresolved selection, conflict, and insufficient
  coverage remain distinct.
- State predicates are require-only and compare snapshot metadata exactly.
  Mathematical predicates require selected exact complete data or a selected
  registered Completeness-region rule. Conflicts and unresolved selections in
  either projection are hard fences.
- V1 registers exact-group evaluation and published vanishing evidence; it does
  not reason from bounded or conjectural assertions, apply UCT in the read path,
  or use closed-world anti-joins.
- A selected vanishing rule may derive exact zero for a bare-absent slot or
  corroborate selected exact zero. Any simultaneous nonzero or nonexact selected
  slot evidence must be reconciled as supersession/conflict or fail snapshot
  integrity; the evaluator never chooses precedence.
- Every candidate is a proven match, proven nonmatch, or unresolved candidate.
  `include_unresolved` returns the last class separately and never relaxes the
  meaning of match.
- Exact signatures list every group in a contiguous range and state whether
  outside degrees are ignored or must vanish under published completeness.
- Nested Boolean logic, scoring, similarity, cross-tier unions, and implicit
  promotion are deferred. The structured evidence explanation, not generated
  prose, is authoritative.
