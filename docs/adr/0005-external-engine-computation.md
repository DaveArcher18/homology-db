# ADR 0005: Admit external-engine computation as attributed evidence

- Status: proposed
- Date: 2026-09-09

## Context

Open decision 4 in [the project brief](../planning/00-project-brief.md) asks whether a
reproducible computation may be published as exact without a literature citation, and
under what validation rule. Until now the question was theoretical: every cohomology ring
in the atlas was read out of Hatcher. A contribution of cup-product rings computed from
explicit triangulations forces an answer.

[The compute-platform strategy](../planning/05-compute-platform-strategy.md) already fixes
the architecture -- canonical versioned input, isolated adapter, engine, canonical output
plus a run manifest -- and states that no engine writes database tables and no
engine-native artifact is canonical data. [The reimplementation doctrine](../planning/07-reimplementation-doctrine.md)
already states that no imported output becomes canonical merely because two programs
agree. What is missing is the admission rule.

## Decision

An ordinary cohomology ring computed by an external computer algebra system is admissible
as an **attributed imported assertion**, never as an owned result and never as human
review.

1. It carries `provenance.kind = "external_engine_computation"` and
   `review_state = "imported_unreviewed"`. The release gate refuses to promote that state.
2. It is bound to one immutable model. Where the generating recipe does not reproduce its
   own labelling, the model is checked in and pinned by hash rather than by recipe.
3. Everything derivable from the checked-in data is re-derived here rather than trusted:
   canonical facet order, the recomputed facet hash, that the simplicial boundary squares
   to zero, and the graded-ring axioms of the imported table.
4. What is not re-derived -- that the structure constants are the cup product of that model
   -- is recorded as imported evidence, with engine, engine version, and source locator.
5. A slot may carry both a sourced and a computed record. They are corroborating
   assertions, exposed side by side and never merged. If their additive groups disagree the
   slot is a conflict and the build fails; provenance is not a tiebreaker.

## Consequences

- Absence of a computed ring stays an absence. Nothing in this decision permits a missing
  ring to be shown as zero.
- Agreement between a computed record and a sourced one is evidence attached to an
  assertion, not proof, and does not change either record's review state.
- Human mathematical review remains a separate, human-authored act. No amount of engine
  agreement produces it, and the review schema still admits no non-human reviewer.
- The engine stays outside the build: the atlas is rebuilt from checked-in data with the
  standard library alone, and no contributor needs the engine installed to verify what this
  repository verifies.
- This ADR admits ordinary cohomology rings only. Extending the rule to other computed
  invariants is a separate decision.
