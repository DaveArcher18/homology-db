Type: wayfinder:map
Status: complete

# Classical spaces reference

## Destination

Deliver the student-facing ordinary (co)homology iteration in [spec.md](spec.md).
The 13-space scope and page design are accepted for autonomous implementation.

## Frontier

- [01 — Qualify the classical ring corpus](issues/01-qualify-ring-corpus.md)
- [02 — Build, verify, and publish](issues/02-build-and-publish.md)

Ticket 02 coordinates the complete implementation and release across separately
owned components, retaining independent mathematical review.

## Decisions so far

- 2026-09-06: Both tickets resolved. All 65 ring records and the student reference
  are live; independent mathematical/integration review, regression tests,
  deterministic build, Pages, and live browser/byte checks passed. Human review
  remains pending. Resume from actual user feedback, not an automatic backlog.

- 2026-09-06: David selected both homology and cohomology with rings central,
  a small textbook core, and fields first with integral data retained.
- The proposed implementation uses 13 existing entries and the current static
  atlas architecture. The exact source-qualified mathematics is the next frontier.
- Previous stable-spectrum work and its open nested-knowl exploration are retained
  in `.scratch/steenrod-cw49-v1/`; they are not active work for this iteration.
