Type: grilling
Status: resolved
Claimed by: /root
Claimed at: 2026-07-11T11:54:48Z
Resolved at: 2026-07-11T12:16:37Z
Blocked by: 02, 03

# Set the first-release model boundary

## Question

Which of abstract simplicial complexes, regular CW presentations, incidence data, attaching data, based cellular chain complexes, cubical complexes, and simplicial sets count as Models in `0.0.1`; which are derived artifacts; and what reconstructibility, canonicalization, or equivalence does the release promise?

## Inputs already fixed

- G2 requires a finite topological presentation that an owned versioned decoder
  can reconstruct. Boundary matrices, Betti numbers, and bare based chain
  complexes are derived computation artifacts, never counted Models.
- One source artifact or Model cannot be counted in both the finite-simplicial
  and finite-CW format buckets merely by re-encoding it.
- Engine-native bytes remain immutable source artifacts; canonical release data
  use neutral, versioned encodings.

These are prior release-contract decisions, not questions to reopen in this
grill.

## Factual boundary audit

- A finite abstract simplicial complex is reconstructible from its vertices and
  maximal simplices. Simplicial isomorphism is stronger than PL homeomorphism;
  subdivisions remain distinct presentations.
- A genuine finite regular CW complex is reconstructed up to homeomorphism by
  its full Cell-closure poset: the order complex of the cells is a deterministic
  barycentric subdivision. If an encoding adds an artificial bottom element,
  that element is removed before taking the order complex. The poset does not
  reproduce the historical characteristic maps, embedding, metric, or PL
  structure.
- Arbitrary graded incidence data, signed incidence matrices, and `d^2 = 0` do
  not prove regularity. Counted Cell-closure-poset Models therefore need regularity
  evidence by owned construction or a checked certificate.
- A general nonregular finite CW complex needs actual attaching maps. Cellular
  incidence numbers retain degrees after collapse, not the maps themselves.
  There is no agreed neutral finite attaching-map language in the repository.
- Cubical complexes, Delta-complexes, and finite simplicial sets are all
  potentially reconstructible, but they are different presentation kinds.
  Delta-complexes and finite simplicial sets need not be regular CW complexes.
- Canonical bytes can prove equality of a normalized encoding. They do not by
  themselves prove combinatorial isomorphism, homeomorphism, or homotopy
  equivalence; those levels require separate algorithms or evidence-bearing
  assertions.

Primary mathematical anchor: Anders Björner, *Posets, Regular CW Complexes and
Bruhat Order*, DOI
[`10.1016/S0195-6698(84)80012-8`](https://doi.org/10.1016/S0195-6698(84)80012-8).

## Grill record

Question 1 was asked at 2026-07-11T12:04:26Z:

> For `0.0.1`, should the CW side stop at finite **regular** CW complexes,
> with nonregular CW complexes deferred until we have a finite, executable
> attaching-map language?

Recommended answer: **yes**. It gives the release a precise reconstruction
contract through certified face posets while reserving an extensible future
Model kind for nonregular CW presentations. If the answer is no, the next work
must be a throwaway prototype of a deliberately narrow attaching-map language
(recommended starting point: explicit simplicial maps from triangulated
spheres into a triangulated prior skeleton) before such Models can count.

The remaining reversible choices—regular-CW carrier and witness, counting,
cubical normalization, deferred native formats, identity across conversions,
and canonicalization strength—were inferred after the user's direction to
proceed and are recorded in the Answer.

## Comments

- 2026-07-11T12:06:51Z — Three consecutive goal turns reached question 1
  without a user response. Work is cleanly paused under the blocked-goal
  protocol; the ticket remains claimed and no recommendation was enacted.
- 2026-07-11T12:10:17Z — The user approved regular finite CW complexes plus
  handpicked special examples, directed the agent to infer the obvious
  reversible dependent choices, and resumed work.

## Answer

Homology DB `0.0.1` has exactly two admitted presentation classes for counted
Models:

1. `finite_simplicial`: a finite abstract simplicial complex;
2. `finite_regular_cw`: a finite Cell-closure poset with a supported Regularity
   witness.

This is a presentation boundary, not a restriction on mathematical spaces.
Moore spaces, lens spaces, projective spaces, and other torsion-rich examples
may enter through finite presentations in either admitted class.

For a regular-CW Model, the decoder reconstructs the dimensioned Cell-closure
poset. The ordered simplicial chains of its deterministic order complex are the
guaranteed G10 chain carrier. The reconstruction is homeomorphic to the regular
CW realization but does not claim to recover historical characteristic maps,
embeddings, metrics, or PL structures. Direct one-generator-per-cell chains are
optional future Derived artifacts and require separately verified orientation
and incidence data.

The initial supported Regularity-witness families are proof-by-construction
from a validated abstract simplicial complex and from a strict face-to-face
cubical complex whose cells and intersections have been checked. Any later
witness kind requires a versioned executable checker. An upstream `regular`
label, graded incidence, signs, and `d^2 = 0` are not witnesses. Economical HAP
or quotient-cell examples with self-identifications do not bypass this rule;
they need a verified regular subdivision or remain excluded as Models.

Native arbitrary/nonregular CW attaching maps, Delta-complexes, finite
simplicial sets, and Regina generalized triangulations are deferred. Their
immutable Source artifacts and provenance may be retained. Strict cubical data
may be translated losslessly into the complete Cell-closure poset of the same
Model; a triangulation or subdivision instead creates a distinct Model with a
typed relation.

Model identity and counting obey these rules:

- each counted Model has exactly one immutable admitted presentation class;
- a lossless alternate encoding belongs to the same Model only with a recorded
  same-cell-presentation witness;
- a subdivision is always a distinct Model linked by `subdivision_of`;
- deterministic normalization is promised for a labeled presentation, but
  canonicalization under isomorphism, homeomorphism, or homotopy equivalence is
  not;
- Model relation assertions name their directed or equivalence kind and never
  silently merge identities;
- Source and Derived artifacts never increment the Model count.

Ticket 07 must publish an executable counted-model ledger with at least 1,000
presentation-isomorphism-distinct Model IDs, an explicit complete split with at
least 400 in each admitted class, and one count bucket per Model. It must audit
Stellar and cross-source overlap using pinned upstream isomorphism-free evidence
or targeted isomorphism checks rather than relying only on disjoint source
rows. The reviewed special slice contains at least 10 genuinely nonsimplicial
regular-CW Models—meaning their Cell-closure posets are not abstract-simplicial
face posets—each paired with a distinct simplicial Model of the same curated
space. These pairs satisfy the G2 cross-format floor; all special examples obey
the same regularity rules. The ledger also names the remaining Models needed
beyond 400 + 400, all 25 multipresentation spaces, and the G10 independent
validation subset of at least 50 Models covering both formats and every required
torsion/adversarial class.

## Evidence

- [ADR 0001](../../../docs/adr/0001-v0-0-1-model-boundary.md) records the
  architectural boundary and consequences.
- [The domain glossary](../../../CONTEXT.md) distinguishes Model, Source
  artifact, Model artifact, Derived artifact, Cell-closure poset, Regularity
  witness, and Model relation assertion.
- The decision was checked independently for mathematical correctness, domain
  identity, and compatibility with G2/G10. Reviews corrected the artificial
  bottom-element convention, chain carrier, cubical/subdivision identity,
  distinctness audit, and nonsimplicial cross-format obligation.
