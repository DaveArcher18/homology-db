Type: wayfinder:map
Status: active

# Named atlas review candidate

## Destination

Deliver a deterministic `named-atlas-review-v1` Snapshot and the same four
public tools over a production-like assertion/provenance schema. It is ready
for Gabriel Ong or Dan Isaksen only after the complete named-atlas gate passes
with no critical mathematical-safety, schema, or provenance defect.

## Notes

- This map carries execution through the verified review candidate; it does
  not stop after resolving design questions.
- Preserve `local-preview-60` unchanged as a regression fixture. It is not the
  external reviewer experience.
- Record cited family theorems for all `RP^n` and `CP^n`, materialize grounded
  instances for `0 <= n <= 12`, and return `outside_materialized_range` above
  that bound.
- Use primary or author-owned sources only for assertion evidence.
- Use the hybrid gate: every named instance has cited Homology; a
  representative cross-model slice also has qualified Models and owned
  computations.
- Keep the four public operations and prohibit query-time formula invention.
- Carry stable, versioned, context-independent mathematical definition records
  inspired by LMFDB knowls. Public responses must reference and expand these
  definitions without confusing exposition with assertion evidence.
- Use persistent, mathematically meaningful public labels while preserving
  aliases and identity assertions instead of merging Conceptual spaces.
- The supplied remote is `https://github.com/DaveArcher18/homology-db.git`.
  Fetch before push and never overwrite conflicting remote history.
- Use `domain-modeling`, `codebase-design`, `prototype`, `tdd`, `research`,
  `wrangler` only if hosting enters scope, and `code-review` as each ticket
  requires.
- Existing contracts are inputs. The disposable preview schema is not proof
  that the production schema is adequate.

## Decisions so far

<!-- One context pointer per resolved ticket. The answer lives in the ticket. -->

- [Supersede the external-review gate](issues/01-supersede-external-review-gate.md)
  — Keep `local-preview-60` as a frozen regression fixture, place external
  review on hold until `named-atlas-review-v1` passes, and carry Gabriel Ong's
  knowl/naming feedback into schema, operation, QA, and audit acceptance.
- [Publish the current history](issues/02-publish-current-history.md) — Fetch
  the empty supplied GitHub repository, push `main` without force, and track
  `origin/main` at the held-review checkpoint.

## Not yet specified

- SQLite versus PostgreSQL physical design after the logical schema and
  1,159-Model workload exist.
- The canonical formula/quantifier AST after the family-assertion constellation
  exposes its identity and review requirements.
- Whether finite simplicial sets become an admitted release Model kind after
  canonicalization, validation, chain, map, and size prototypes are measured.
- Adapter/runtime packaging after pinned Sage, HAP, simpcomp, and Regina paths
  are exercised in clean environments.
- The exact prompt count and category allocation for the named-atlas QA pack
  after the final subject/coverage manifest is materialized.
- Which mathematical object portraits or graph views are useful enough to
  justify a later visual-design ticket. The data model should enable them, but
  no decorative graphic is a review-candidate gate.

## Out of scope

- External mathematical review before this map's gate passes.
- Public hosting, Web UI (including inline knowl dropdown rendering), and
  CW/simplicial rendering. The review candidate still includes the definition
  records and four-operation access needed by a later UI.
- Grassmannians, flag or other homogeneous spaces, general `BG`, `K(A,n)`,
  Thom spaces, spectra, stable stems, and spectral-sequence data.
- Query-time natural-language inference, embeddings, semantic similarity, or
  formula specialization that does not create Snapshot-bound assertions.
- Requiring a qualified Model for every citation-backed named instance.
