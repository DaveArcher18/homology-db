# Independent mathematical review: classical core

Reviewer: `/root/math_review`, separate from the implementation owner.
Review date: 2026-09-06.
State: independent mathematical implementation review passed; no blocking finding.
Human mathematical review: pending.

## Source qualification

The reviewer opened Hatcher's author-hosted textbook and checked the exact
locators recorded in [sources.md](sources.md). All 13 spaces over Q, F2, F3,
F5, F7 have source-qualified presentations. The note separates direct ring
statements from deductions using cellular cochains, additive support, and the
unit/degree rules. No mathematics gap was identified.

## Independent additive baseline

Before reading the implementation, the reviewer built a fresh legacy chromatic
database in a temporary directory and checked a manually transcribed oracle
from the qualified source matrix against `ChromaticTools.read_homology`.

Result: **52 field records plus 13 rational dimensions passed**. Prime-field
rows matched degree by degree. Rational dimensions were checked against
integral free ranks because the legacy API intentionally supports Z, F2, F3,
F5, F7, but not Q. This limitation was reported to the coordinating and data
agents so that rational homology can be added with explicit derivation
provenance in the new export without silently altering the old snapshot.

The oracle's characteristic-independent rows were:

```text
point           1
S0              2
S1              1,1
S2              1,0,1
S3              1,0,0,1
S4              1,0,0,0,1
T2              1,2,1
Klein (non2)    1,1,0
RP2 (non2)      1,0,0
RP3 (non2)      1,0,0,1
RP4 (non2)      1,0,0,0,0
CP2             1,0,1,0,1
S2 wedge S4     1,0,1,0,1
```

Overrides in F2: Klein `1,2,1`, RP2 `1,1,1`, RP3 `1,1,1,1`, RP4
`1,1,1,1,1`. These include explicit zero entries through each space's
dimension and do not infer missing data outside a stated coverage region.

## Implementation review

Read every factory, validator, source locator, and derivation in
`homology_db/classical.py`. All 65 requested presentations agree with the source
matrix. The Klein-bottle implementation uses the shorter relations `a²+b², ab`;
these already imply `a³=b³=0`, so the quotient is the same finite algebra as
the expanded presentation in the qualification note.

An independently written oracle, not the implementation's validator, compared
**all 381 ordered basis products** with the qualified formulas and passed.
This covers the unit, omitted zero products, torus signs in odd characteristic,
S0 idempotency, Klein diagonal squares, RP powers, and CP2/wedge squares.
After the size-saving encoding change, the oracle was rerun and again passed
all 381 pairs. It expands the explicitly declared `unit_products: identity`
rule; only omitted **nonunit** basis pairs are interpreted as zero. This is
an explicit complete algebra encoding, not an inference from absent records.

Executed `python3 -m unittest discover -s tests -p 'test_classical*.py' -v`:
**15 tests passed**. These include the separate homology comparison, complete
coefficient coverage, exact missing-versus-zero behavior, source resolution,
display consistency, and rejection of wrong signs, nonassociativity,
inhomogeneous relations, incomplete coverage, and invented human acceptance.

Read the exporter and independently checked **88 rational homology rows**,
including both reduced and unreduced conventions. Every derived row has the
matching integral free rank, degree, convention, parent assertion ID, and
evidence; it has no fabricated computation ID. The export cites Hatcher
Corollary 3A.6(a), p. 266. Explicitly checked S0: reduced H0 has dimension 1,
unreduced H0 has dimension 2, and ordinary H^0 still has dimension 2.

Inspected mathematical presentation in `static_atlas/atlas.js` and the relevant
helpers: coefficient selection applies to both theories, the reduced control
changes only homology, relations and basis monomials are rendered from data,
integral cohomology is explicitly unrecorded, and the CP2/wedge explanation is
correct over every offered field. The rational-homology note correctly
identifies extension of scalars and now directly links its recorded UCT source;
the suggested provenance improvement was checked and is complete.

## Reviewed revision and limits

Classical record content SHA-256:
`e33d8cffc29e5f036c4696285242daca903e0b2265ce43bc16f1acf4631f1cd6`.

The final concise derivation prose and shorter `ring_and_derivation` source
role were rechecked. No formula, locator, basis, characteristic qualification,
or review-state change was introduced by that size reduction. The subsequent
integration fixes and exact implementation input hash are recorded in
`integration-review.md`.

Source-file SHA-256 at the completed inspection:

```text
homology_db/classical.py
e4d9cf5287f6825e3d8136b8994296de5e351677bb88dccde65a52f99b38ca57
scripts/export_static_atlas.py
dfa12299b07dad4c0e3c66b6eeec7900863c38705ee5d434b03cfe0f879b6a15
static_atlas/atlas.js
06fb406a65d55c1242090013abc977460f6f23b2a4816138475378b214a8c756
static_atlas/presentation.js
45b0f0563226037e5e7845507cd09db73c561e6e50661ab58343292f9b8df1c7
```

This review establishes sourced mathematical content and implementation
consistency for those inputs. It is not formal proof, external human review,
browser acceptance, a security review, or verification of the final published
artifact bytes. The parent run owns final integration, browser checks, release
checks, and any required recheck after changes to reviewed mathematics.
