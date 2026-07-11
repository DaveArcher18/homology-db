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
