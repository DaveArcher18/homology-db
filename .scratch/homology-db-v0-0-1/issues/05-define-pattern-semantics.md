Type: grilling
Status: claimed
Claimed by: /root (interactive chat)
Claimed at: 2026-07-11T13:13:33Z
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
