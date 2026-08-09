Type: task
Status: open
Claimed by:
Claimed at:
Blocked by:

# Explore nested mathematical knowls

Capture and investigate friend feedback that terms on the stable atlas—most
immediately Steenrod operations—should open contextual mathematical knowls,
and that those knowls should themselves be able to open further knowls in the
style of the LMFDB.

## Working definition

A knowl is a small, reusable piece of exposition attached to a term. Activating
the term expands its definition or context in place, so a reader can learn what
it means without leaving the mathematical page. A nested knowl allows a term
inside that explanation to expand another explanation.

The repository already has revisioned `knowledge_entry` records, typed
`knowledge_link` edges—including knowledge-entry-to-knowledge-entry links—and
single-level knowl presentation for the ordinary-space atlas. The exploration
should determine how much of that model can be reused for stable pages and what
is needed for safe, comprehensible nesting.

## Questions to answer

- Which stable terms deserve first-wave knowls: Steenrod operations,
  cohomology, stable homotopy category, spectra, module spectra, basis elements,
  exact zero, unknown actions, completeness, and profile modules?
- What exact interaction and authoring conventions should be borrowed from the
  LMFDB, and which should be adapted to this one-file atlas?
- Should a nested knowl expand inside its parent, beside it, or in one shared
  disclosure region?
- How should nesting depth, cycles, duplicate openings, URLs, browser history,
  focus return, keyboard use, screen readers, narrow layouts, and printing be
  handled?
- How do revision, review, provenance, and Snapshot selection remain visible
  while keeping exposition separate from mathematical assertion evidence?
- Can the feature stay dependency-free and within the existing 5 MiB release
  cap?

## Exploration acceptance

- Document the LMFDB knowl behavior from primary project sources and a small
  set of representative live examples, including nested behavior.
- Inventory the existing knowledge schema and atlas knowl renderer, identifying
  reusable seams and missing contracts.
- Propose a minimal domain and rendering contract with cycle/depth guards and
  accessible nested interaction semantics.
- Identify an initial reviewed vocabulary for the stable atlas without
  presenting imported mathematical claims as independently verified.
- Produce an implementation recommendation and focused acceptance-test plan;
  do not ship the feature as part of this exploration ticket.

## Boundaries

- This note does not authorize mathematical-content changes, review-state
  promotion, a new schema migration, or a public deployment.
- Tooltips alone do not satisfy the request: the defining property is reusable,
  reader-controlled exposition that can be nested.

## Feedback source

Friend feedback relayed by the user on 2026-08-09: add knowls for concepts such
as Steenrod operations, noting that LMFDB knowls can be nested so definitions
can be stacked.
