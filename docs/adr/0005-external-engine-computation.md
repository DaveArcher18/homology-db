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
   own labelling, the model is pinned by the hash of its canonical facet list rather than
   by recipe. A model is **checked in** when its source licence permits redistribution and
   **identified only** when it does not; the record says which, and the distinction changes
   what can be verified here.
3. For a checked-in model, everything derivable from it is re-derived rather than trusted:
   canonical facet order, the recomputed facet hash, that the simplicial boundary squares
   to zero, and the graded-ring axioms of the imported table.
4. For an identified-only model there is no facet list to reduce, and the verification that
   remains is weaker and is stated as such. What is still checked here: that the Euler
   characteristic of the recorded f-vector equals the alternating sum of the recorded Betti
   numbers, which ties the model's combinatorics to its groups; that the imported homology
   over each field agrees with the universal-coefficient consequence of the imported
   integral homology, which compares two computations the engine performed separately; that
   the additive groups of the ring records agree with the homology records; and the
   graded-ring axioms of the imported table. The chain complex stored alongside such a
   record is a **calculation certificate** built from the recorded groups, so reducing it
   and recovering them tests this repository's converter, not the engine's answer, and is
   never reported as corroboration.
5. What is not re-derived -- that the structure constants are the cup product of that model,
   and for an identified-only model that the recorded groups are the homology of the named
   triangulation -- is recorded as imported evidence, with engine, engine version, and
   source locator.
6. A slot may carry both a sourced and a computed record. They are corroborating
   assertions, exposed side by side and never merged. If their additive groups disagree the
   slot is a conflict and the build fails; provenance does not settle a disagreement.
7. Where both exist and agree, the cited text takes precedence for display: the ring, its
   presentation and its multiplication table are read from the literature record, and the
   computed record is named as corroboration. Precedence is by provenance, not by which
   record happens to carry a presentation.

## Consequences

- Redistribution is not assumed. Where an upstream catalogue states no licence for its
  triangulations, this repository identifies the model and declines to ship it, rather than
  treating silence as permission. That choice buys the contribution at the price of the
  re-derivation in point 3, and point 4 says exactly what is bought and what is lost.
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
