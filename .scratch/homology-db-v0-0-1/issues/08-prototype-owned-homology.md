Type: prototype
Status: claimed
Claimed by: /root (interactive chat)
Claimed at: 2026-07-11T17:26:42Z
Blocked by: 04, 07

# Prototype the owned cellular-homology boundary

## Question

What is the smallest owned computation contract—ordered bases, sparse boundaries, Smith data, representatives, and induced maps—that computes the selected corpus reproducibly and differential-tests against independent references without inheriting their runtime models?

## Prototype seam

The agreed public test seams are the four QA tools already fixed by the
observable contract: `resolve_subject`, `read_homology`, `query_examples`, and
`expand_evidence`. A human-facing command-line adapter may compose those tools
but may not add hidden mathematical inference. The prototype will use a
disposable local SQLite snapshot and stable JSON requests/responses so both a
person in Codex and a model tool caller exercise the same interface.

## Prototype checkpoint

The throwaway primary source is commit `25b5e07` on branch
`codex/prototype-owned-homology`. It exercises ordered bases, sparse integral
boundaries, exact Smith invariants, direct finite-field ranks, a disposable
indexed SQLite Snapshot, and the four tool seams over the frozen 60-subject QA
cohort.

The experiment establishes that the four-tool interface is deep enough for a
human CLI and an agent caller. It also exposes the missing production seam:
Smith diagonal invariants suffice for group structure, but general cycle
representatives and induced maps require retained basis transformations and
kernel/image coordinates. Those capabilities are explicitly `not_computed` in
the preview rather than represented by empty data.

The usable interface has been folded into `homology_db/` on main with public-
seam tests and [a guided test drive](../../../docs/TEST_DRIVE.md). The ticket
remains claimed: it is not resolved until general adjacent-boundary examples,
representatives, induced maps, deterministic production runs, and independent
oracle comparisons choose the owned computation contract.
