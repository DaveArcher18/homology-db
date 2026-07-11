Type: grilling
Status: claimed
Claimed by: /root
Claimed at: 2026-07-11T11:54:48Z
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
  its full closure/face poset: the order complex is a deterministic barycentric
  subdivision. The poset does not reproduce the historical characteristic
  maps, embedding, metric, or PL structure.
- Arbitrary graded incidence data, signed incidence matrices, and `d^2 = 0` do
  not prove regularity. Counted face-poset Models therefore need regularity
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

## Grill state

Question 1 asked at 2026-07-11T12:04:26Z; awaiting the user's decision:

> For `0.0.1`, should the CW side stop at finite **regular** CW complexes,
> with nonregular CW complexes deferred until we have a finite, executable
> attaching-map language?

Recommended answer: **yes**. It gives the release a precise reconstruction
contract through certified face posets while reserving an extensible future
Model kind for nonregular CW presentations. If the answer is no, the next work
must be a throwaway prototype of a deliberately narrow attaching-map language
(recommended starting point: explicit simplicial maps from triangulated
spheres into a triangulated prior skeleton) before such Models can count.

Dependent decisions—regular-CW carrier and regularity witness, the 400-model
counting rule and nonsimplicial sanity slice, native versus normalized cubical
data, finite simplicial sets and generalized triangulations, Model identity
across conversions, and canonicalization/equivalence strength—remain unasked.
