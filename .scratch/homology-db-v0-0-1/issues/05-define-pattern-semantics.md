Type: grilling
Status: resolved
Claimed by: /root (interactive chat)
Claimed at: 2026-07-11T13:13:33Z
Resolved at: 2026-07-11T13:37:31Z
Blocked by: 01, 02, 04

# Define structured homology-pattern semantics

## Question

What do exact, required, forbidden, partial, and unknown constraints mean across degrees, coefficient systems, reduced conventions, primary torsion summands, completeness regions, and corpus tiers—and how does every result explain why it matched?

## Grill record

Question 1 asked at 2026-07-11T12:19:37Z:

> Should an `unknown` pattern constraint mean “the current selected assertion is
> explicitly in the `unknown` knowledge state,” or should it also match absent,
> not-computed, incomplete, unresolved-selection, and conflicting slots?
>
> **Recommendation:** make `unknown` exact and narrow: it matches only an
> explicit selected `unknown` assertion. Treat absence, `not_computed`, a
> completeness failure, unresolved selection, and conflict as distinct queryable
> outcomes. Use `include_unresolved` only to return separately labelled
> candidates that cannot prove another required/forbidden/exact constraint; it
> is not an `unknown` match. This preserves the G6 three-valued evidence rule and
> lets an LLM distinguish “explicitly unknown” from “we have no answer.”

## Comments

- 2026-07-11T12:49:09Z: Marked `needs-info` after three consecutive runs
  awaiting Question 1. Resume only when the user supplies this decision.
- 2026-07-11T13:13:33Z: Reassigned from the standalone scheduler to this
  interactive chat at the user's direction. The previous `needs-info` marker is
  retained as history here; this ticket is now claimed by the chat and advances
  only on explicit interactive direction.
- 2026-07-11T13:37:31Z: The user said `Continue`. Consistent with the prior
  direction to infer obvious reversible choices, Question 1 was resolved to the
  narrow explicit meaning already forced by G6 and ticket 02.

## Answer

Homology pattern v1 is a snapshot-bound, nonempty conjunction over exactly one
corpus tier. A normal clause binds one candidate to one fully qualified Homology
slot and has a typed predicate plus `require` or `forbid` polarity. A
require-only Exact signature macro is the sole ranged exception. “Exact” and
“unknown” name predicates/evidence; “partial” means unspecified slots impose no
condition. They are not additional polarities.

Every mathematical predicate evaluates from selected evidence to one Evidence
trit: `proven_true`, `proven_false`, or `unresolved`. Polarity maps that trit to
`satisfied`, `violated`, or `unresolved`. The conjunction then classifies a
candidate:

- all satisfied: `proven_match`;
- any violated, even with another unresolved clause: `proven_nonmatch`;
- no violation and at least one unresolved: `unresolved_candidate`.

`include_unresolved` affects presentation only. Proven matches and unresolved
candidates are returned in separate arrays and never jointly ranked or called
equally valid examples.

The recorded `unknown` question is resolved narrowly:
`selected_knowledge_state_is: unknown` matches only a selected explicit atomic
`unknown` assertion. `not_computed`, `not_applicable`, absence, insufficient
coverage, unresolved selection, and conflict remain distinct. Metadata
predicates are require-only exact comparisons; conflicts and unresolved
selections are hard fences for mathematical predicates.

Mathematical clauses are proved in v1 only by a selected exact complete group
or an applicable selected, registered vanishing Completeness region. Bounded
and conjectural assertions remain queryable states but do not prove
mathematical predicates. Bare absence never proves a forbidden condition.
Missing rows inside declared complete coverage, corrupt primary derivations, or
simultaneously selected contradictory exact and vanishing evidence abort the
query as snapshot-integrity failures rather than becoming zero or unresolved.

The v1 predicate union covers exact groups, integral free rank, prime-field
dimension, p-primary torsion, exact `Z/(p^e)` summands and multiplicities,
exact p-primary decomposition, p-primary exponent, atomic Knowledge state,
Current-projection outcome, and exact integral signatures. It keeps p-primary
summands distinct from order divisibility, p-rank, and total p-adic order; it
performs no read-time UCT or cross-coefficient inference.

Curated and Model tiers are evaluated separately. Model evidence never fills a
Conceptual-space slot without a published promotion. Every result carries the
normalized query/hash, snapshot/release identity, complete candidate-universe
coverage, per-clause reason codes and concrete slots, selected/supporting
assertions, and Homology/completeness/conflict/proof evidence. Zero results mean
zero proven examples in that snapshot and tier, not global nonexistence.

V1 deliberately defers nested Boolean logic, arbitrary bound reasoning,
wildcard degrees, cross-tier union, similarity scoring, natural-language
parsing, and implicit promotion. Invalid or directly contradictory requests
fail atomically with path- and clause-specific versioned errors.

## Evidence

- [Homology pattern query contract v1](../../../docs/contracts/homology-pattern-v1.md)
  defines the normalized request, typed predicates, evidence tables,
  Completeness regions, pagination, validation, response envelope, and fifteen
  adversarial fixture classes.
- [ADR 0002](../../../docs/adr/0002-evidence-trits-for-homology-patterns.md)
  records the evidence-trit and unresolved-candidate boundary.
- [The domain glossary](../../../CONTEXT.md) now defines Completeness region,
  Candidate-bound slot selector, Pattern clause, Exact signature macro,
  Evidence trit, Pattern outcome, and Unresolved candidate.
- Three independent reviews checked formal logic, LLM-facing evidence, and
  indexable implementation semantics. Their corrections fixed signature shape,
  state negation, completeness projection, cursor identity/pagination, numeric
  bounds, contradiction validation, integrity failures, and coverage cost.
