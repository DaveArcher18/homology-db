Type: wayfinder:map
Status: active

# Stable Steenrod modules and cw49 atlas

## Destination

Deliver a deterministic review candidate containing all 49 stable
spectra from Wayne Lin's cw49 index, complete mod-2 Steenrod-module records,
Bruner/sseq/SSeqCpp downloads, and table-led atlas routes. Publish it as an
openly labeled imported-unreviewed preview for informal feedback; Dan
Isaksen's eventual acceptance remains a separate finalized-release event.

## Fixed decisions

- Stable spectra are distinct from Conceptual spaces; later unstable
  realizations may point to a spectrum with an explicit suspension shift.
- Missing Steenrod actions are unknown unless an exact completeness assertion
  covers the slot. Exporters never convert unknown data to zero.
- Store `Sq^(2^k)` on a versioned ordered basis. Bruner export derives every
  nonzero composite square through Adem closure.
- The corpus contains 48 finite-basis records and one profile record (`tmf`).
  Bruner reports typed unsupported for `tmf`; no truncation is invented.
- Atlas presentation is table-first. Public preview is allowed only through an
  explicit reproducible preview gate and never manufactures acceptance.

## Tickets

- [01 — Fix the stable Steenrod contract](issues/01-fix-stable-steenrod-contract.md)
- [02 — Normalize cw49 and implement exporters](issues/02-normalize-cw49-and-export.md)
- [03 — Extend the production schema](issues/03-extend-production-schema.md)
- [04 — Add spectrum atlas routes](issues/04-add-spectrum-atlas-routes.md)
- [05 — Build and gate the review candidate](issues/05-build-and-gate-review-candidate.md)
- [06 — Publish the open review preview](issues/06-publish-open-review-preview.md)
- [07 — Refine the stable atlas presentation](issues/07-refine-stable-atlas-presentation.md)

## Decisions so far

<!-- Append one context pointer per resolved ticket. -->

- [Fix the stable Steenrod contract](issues/01-fix-stable-steenrod-contract.md)
  — Conceptual spectra remain distinct from spaces; generator actions use a
  versioned ordered basis, and only exact completeness permits omission-as-zero
  exports.
- [Extend the production schema](issues/03-extend-production-schema.md)
  — Append-only migration 0005 gives spectra and Steenrod records typed
  identity, exact zero/unknown/absent semantics, reviewed Snapshot closure,
  and unstable-only instability enforcement.
- [Normalize cw49 and implement exporters](issues/02-normalize-cw49-and-export.md)
  — The pinned corpus has 48 complete finite modules plus the `tmf` profile;
  deterministic Bruner, sseq, and SSeqCpp adapters pass their real consumers.
- [Add spectrum atlas routes](issues/04-add-spectrum-atlas-routes.md)
  — Review builds preserve all space behavior while adding separate stable
  spectrum search, table-first detail routes, provenance, and local downloads.
- [Build and gate the review candidate](issues/05-build-and-gate-review-candidate.md)
  — A byte-reproducible hashed review packet is ready locally; the public
  artifact remains the accepted 42-space atlas until Dan accepts that packet.
- [Publish the open review preview](issues/06-publish-open-review-preview.md)
  — The user superseded the prior publication hold for informal feedback. The
  49-spectrum corpus is live as an explicit `public_review_preview`; imported
  claims remain unreviewed and Dan acceptance still controls final admission.
- [Refine the stable atlas presentation](issues/07-refine-stable-atlas-presentation.md)
  — Home remains spaces-first; stable mathematics uses one safe semantic TeX
  path, obvious spectrum names are curated conservatively with exact-ID
  fallbacks, and provisional categorical language is disclosed without
  changing the corpus or review state.

## Out of scope

- Canonical unstable realizations, minimum realization dimensions, or
  attaching-map data.
- A graph-first Steenrod-operation visualization.
- Implicit finite truncations of infinite profile modules.
- Marking imported operations reviewed without Dan's explicit verdict.
