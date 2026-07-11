# Owned Homology logic prototype

Status: **throwaway primary source**, not release code or release evidence.

Run one command:

```bash
python3 prototype/owned_homology.py demo
```

It rebuilds `/tmp/homology-db-PROTOTYPE.sqlite`, computes integral and field
Homology for the fixed 60-common-manifold QA cohort from ordered sparse chain
complexes, and exercises the four public QA tools. Human and agent callers use
the same stable JSON requests.

The experiment intentionally uses an exact but exponential Smith-invariant
algorithm and supports only chain complexes with separated nonzero boundaries.
It records representatives and nonidentity induced maps as `not_computed` when
their necessary basis transforms are absent. Those limitations are the design
question, not bugs to conceal with empty output.
