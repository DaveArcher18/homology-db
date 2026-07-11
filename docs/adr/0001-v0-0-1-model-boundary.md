---
status: accepted
---

# Limit 0.0.1 to simplicial and certified regular-CW Models

Homology DB `0.0.1` admits finite abstract simplicial complexes and finite
regular CW complexes with a complete Cell-closure poset and a Regularity
witness. This limits presentation kinds rather than mathematical spaces: a
torsion-rich space may enter through any admitted finite presentation. The
boundary keeps every counted Model topologically reconstructible while avoiding
the false claim that cellular boundary matrices retain arbitrary attaching maps.

## Consequences

- A regular-CW decoder reconstructs the dimensioned Cell-closure poset. After
  removing any artificial bottom element, its deterministic order complex is a
  homeomorphic reconstruction; no claim is made about the source's
  characteristic maps, embedding, metric, or PL structure.
- Regularity is accepted only through a whitelisted owned preserving
  construction or checked certificate whose checker is part of the release.
  Each lower open interval in the corresponding augmented CW poset must have
  the required sphere realization, or the witness must establish a stronger
  versioned sufficient condition. Incidence signs and `d^2 = 0` are not a
  Regularity witness.
- Rejecting or superseding a Regularity witness withdraws release eligibility
  through append-only editorial history; it never deletes the Model, artifacts,
  old assertion, or old snapshot.
- The guaranteed G10 chain carrier for a finite regular-CW Model is the ordered
  simplicial chain complex of that deterministic order complex. A future
  one-generator-per-cell chain artifact requires a separately verified
  orientation and incidence derivation.
- A strict cubical presentation whose cells and intersections form a finite
  regular CW complex may be translated losslessly to its complete Cell-closure
  poset as another artifact of the same Model. Triangulation or subdivision
  creates a distinct Model with a typed relation.
- Native Delta-complex, finite-simplicial-set, Regina generalized-triangulation,
  and nonregular attaching-map formats are deferred. Handpicked special
  examples obey the same certified regular-CW boundary and are not exceptions.
- A lossless alternate encoding belongs to the same Model only through a
  recorded decoding/re-encoding witness identifying the same cell
  presentation. Independent inputs remain distinct Models unless an editorial
  identity decision explicitly says otherwise; subdivision always creates a
  distinct Model.
- Every counted Model has one immutable admitted presentation class,
  `finite_simplicial` or `finite_regular_cw`. Alternate artifacts cannot move
  it between buckets or make it count twice.
- `0.0.1` promises deterministic normalization of a labeled presentation, not
  canonicalization under combinatorial isomorphism, homeomorphism, or homotopy
  equivalence. Such relationships never trigger a silent merge.
- Ordered based chain complexes, cellular signs, homology groups, renderings,
  and other computed views are Derived artifacts and do not count toward the
  Model floor.
