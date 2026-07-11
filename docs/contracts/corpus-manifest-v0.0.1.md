# Corpus manifest selection contract for 0.0.1

Status: normative selection plan for ticket 07; not release evidence.

The machine-readable authority is
[`corpus/v0.0.1/manifest-spec.json`](../../corpus/v0.0.1/manifest-spec.json).
This document explains its mathematical and counting semantics. The generated
release ledger must later enumerate exact expanded public IDs, model/artifact
IDs, hashes, assertions, computations, and qualification outcomes. None of the
targets below count as achieved until that ledger and its audits exist.

## Why this slice

The release must serve two purposes at once:

1. give an agent a broad, recognizable collection of common manifolds;
2. stress exact torsion queries far beyond what the natural 2- and 3-manifold
   sources happen to contain.

The manifest therefore combines a 128-manifold QA slice with 45 transparent
Moore-space constructions. The constructed examples are deliberately labelled
as such; they never masquerade as natural manifolds or independent literature
discoveries.

## Curated conceptual spaces

Expansion produces exactly 174 proposed curated spaces across 15 honest family
rollups. The largest rollup contains 25 spaces (14.4%), below G1's 25% cap.

| Family rollup | Exact parameters | Count | Primary admitted Model route |
| --- | --- | ---: | --- |
| Exceptional spaces | empty space; point | 2 | owned empty complex / 0-simplex |
| Spheres | `S^n`, `0 <= n <= 12` | 13 | boundary of the `(n+1)`-simplex |
| Closed orientable surfaces | `Sigma_g`, `2 <= g <= 13` | 12 | owned surface triangulation |
| Closed nonorientable surfaces | `N_g`, `2 <= g <= 13` | 12 | owned surface triangulation |
| Tori | `T^n`, `n = 2,3,4,5` | 4 | ordered simplicial product of a 3-edge circle |
| Real projective spaces | `RP^n`, `n = 2,4,5,6` | 4 | pinned Sage 10.9 neutral export |
| Complex projective spaces | `CP^2` | 1 | pinned Sage 10.9 literal triangulation, neutrally exported |
| Three-dimensional lens spaces | the 13 pinned simpcomp `(p,q)` pairs | 13 | pinned simpcomp neutral facet export |
| Sphere products | 15 listed unordered pairs `S^a x S^b` | 15 | owned ordered simplicial product |
| Disks | `D^n`, `1 <= n <= 8` | 8 | full `n`-simplex |
| Sphere-disk products | 21 listed pairs `S^a x D^b` | 21 | owned ordered simplicial product |
| Surface-circle products | `Sigma_g x S^1` and `N_g x S^1`, `2 <= g <= 9` | 16 | owned ordered simplicial product |
| Sphere-torus products | `S^n x T^2`, `2 <= n <= 9` | 8 | owned ordered simplicial product |
| Moore spaces | the 24-value `(m,n)` grid with `M(Z/2,1)` replaced by `M(Z/8,4)`, plus `M(Z/27,4)` | 25 | owned Moore seed and suspension |
| Mixed Moore bouquets | ranks `1..20` with the fixed four-prime summands | 20 | owned wedge of suspended Moore models |

The first thirteen rollups contain 128 common manifolds, counting the point but
not the empty space. Moore spaces and mixed bouquets are nonmanifold controlled
torsion examples.

### Identity exclusions

The expansion must not create separate conceptual identities for these known
coincidences:

- `RP^2 = N_1`, so nonorientable surfaces begin at genus 2;
- `M(Z/2,1) = RP^2`, so that Moore-grid value is replaced rather than counted
  as a second conceptual space;
- `T^2 = Sigma_1`, so orientable surfaces begin at genus 2;
- `S^1 = RP^1`, `S^2 = CP^1`, and `S^1 x S^1 = T^2`;
- point equals `D^0` and the zero-dimensional projective spaces;
- sphere-product factors are ordered with `a <= b`;
- lens-space `q` is normalized under the cited unoriented homeomorphism rule
  before a second `q` value is admitted.

Equal Homology does not merge identities. Disks of different dimensions,
`X` and `X x I`, the Poincare-style phenomenon of distinct manifolds with the
same signature, and different Moore constructions remain distinct when their
identity evidence says so.

## Counted Model plan

The post-qualification target is exactly 1,159 counted presentation-isomorphism
classes:

| Disjoint cohort | Finite simplicial | Finite regular CW | Total |
| --- | ---: | ---: | ---: |
| Stellar v6 bulk records | 480 | 480 | 960 |
| One primary Model per curated space | 174 | 0 | 174 |
| Five second simplicial presentations | 5 | 0 | 5 |
| Twenty genuinely nonsimplicial paired presentations | 0 | 20 | 20 |
| **Total** | **659** | **500** | **1,159** |

The 480 bulk regular-CW Models are complete face-poset presentations of a
disjoint set of Stellar triangulations. They are disclosed as
`simplicial_face_poset=true`; they test the regular-CW carrier and chain path but
are not described as genuinely nonsimplicial.

The 20 genuinely nonsimplicial pairs are fixed in the JSON spec: cubical or
strict product-cell Models for seven disks, four tori, six sphere cylinders,
and three solid tori, each paired to a distinct simplicial Model. Five spheres
have two nonisomorphic simplicial presentations (simplex and cross-polytope
boundaries). Thus 25 named spaces have multiple Models and 20 of them span both
format classes.

### What counts

G2 counts a presentation-isomorphism class, not an ID or file:

- one Model has one immutable counted format bucket;
- byte changes, relabelings, alternate lossless encodings, source mirrors, and
  facet-to-face-poset re-encodings do not add counts;
- a subdivision is a distinct Model in the domain, but subdivisions may not
  bulk-fill this manifest;
- only the predeclared 25 multipresentation roots may contribute a second
  counted descendant;
- each source overlap retains all provenance even when it contributes one
  counted Model.

The release audit uses a versioned dimension-coloured incidence/Hasse-graph
presentation-isomorphism checker. A future general homeomorphism or homotopy
deduplicator is neither required nor claimed.

### Stellar reserve and qualification

For each of dimensions 2 and 3, valid records are sorted by raw-record SHA-256
and source ordinal. Ranks `0..499` form the simplicial reserve and `500..999`
the disjoint regular-CW reserve. Each reserve must produce its first 240
qualified, presentation-distinct Models. Failure to fill a quota from the fixed
reserve fails the release instead of silently expanding or changing selection.

A candidate qualifies only after original and neutral hashes resolve, decoding
and normalization round-trip, regularity evidence where applicable, ordered
chains satisfy `d^2=0`, the owned integral computation finishes through Model
dimension, and presentation-isomorphism/derivation-root audits pass. Failed and
duplicate candidates remain in the rejected-candidate ledger with reason codes.

polyDB is corroborating metadata for overlapping Lutz material, not a second
counted corpus. simpcomp, Sage, and HAP runtime-native serializations are Source
artifacts; the clean build consumes pinned neutral exports and transformation
manifests rather than pickles or live engine objects.

## Predicted torsion coverage

The following is a pre-computation lower bound from the selected family
formulas, not a G3 result:

| Measure | Predicted floor | Required |
| --- | ---: | ---: |
| distinct `(space, positive degree)` torsion pairs | 138 | 100 |
| distinct torsion spaces | 74 | 40 |
| 2-primary pairs | 52 | 40 |
| 3-primary pairs | 31 | 25 |
| 5-primary pairs | 30 | 15 |
| 7-primary pairs | 28 | 10 |
| spaces with an exact `Z/(p^e)`, `e >= 2` summand | 19 | 8 |
| spaces with repeated exact primary summands | 5 | 5 |
| torsion pairs outside degree 1 | 102 | 10 |

The owned release audit must recompute these figures from selected exact,
complete, unreduced integral assertions and primary-summand rows, grouping once
by `(space_id, degree)`. It may not count model rows, sources, display strings,
divisibility, or total p-adic valuation as additional summands.

The 20 mixed bouquets each contain controlled `2`, `3`, `5`, and `7` torsion in
degrees 2 through 5 and are distinguished by free `H_1` rank. The first five
contain a second `Z/2` in degree 2. The 25 Moore-space parameters supply the
prime-power witnesses. Nonorientable surfaces, real projective spaces, and
lens spaces provide the natural-manifold cross-check.

## Complete Homology grid

For every curated space and counted Model, the generated ledger declares a
finite Model dimension and the complete expected G4 slot set. Qualification
requires:

- selected exact complete unreduced integral groups in every degree through
  dimension for every counted Model;
- the five-coefficient curated grid over `Z`, `F_2`, `F_3`, `F_5`, and `F_7`;
- explicit reduced degree zero for every curated space;
- a predeclared set of at least 25 full reduced grids;
- an evidence-bearing upper-ray vanishing Completeness assertion beginning at
  `dimension + 1`;
- set difference between expected and selected slots equal to empty.

The empty Model has dimension `-1`, but its grid is not allowed to disappear:
the manifest explicitly selects unreduced and reduced `H_0 = 0` over all five
required coefficient systems. Under `augmented_singular_v1`, it also records
reduced `H_{-1}` as the coefficient module. Bare absence cannot stand in for
any of these exceptional values.

Field groups are computed from the owned chains. A separately registered UCT
derivation may corroborate them during ingestion, including the Tor term from
the preceding integral degree, but pattern queries never perform read-time UCT
inference.

## Adversarial data

G5 fixtures occupy uncounted fixture subjects or slots provably disjoint from
the mandatory G4 grid. The exact planned IDs expand to:

- 10 selected `unknown` assertions with typed scope/reason;
- 10 selected `not_computed` assertions with qualifying-run scope;
- 3 selected `not_applicable` assertions for the empty space in degrees
  `0,1,2`, under the separate `reduced_nonempty_only_v1` convention and its
  registered `reduced_homology_nonempty_subject_required/1` applicability
  rule;
- 5 typed bounded/conjectural assertions;
- 5 correction chains spanning Snapshots;
- 3 open maximal Conflict sets;
- explicit empty, disconnected, exact-zero, and reduced/unreduced fixtures.

No missing row or artificial ordinary-Homology “not applicable” claim may fill
these counts. The fixture-only `reduced_nonempty_only_v1` convention defines
reduced Homology only for nonempty subjects, so the empty-space subject is
genuinely outside its domain. It does not replace or weaken the mandatory
`augmented_singular_v1` empty-space grid, whose exceptional values remain
explicit selected assertions.

## Independent validation cohort

Sixty-six Models are chosen before observing agreement:

- both Models of all 25 multipresentation spaces (50);
- the empty and `S^0` primary Models;
- eight named torsion Models covering all primes, powers, multiplicity, and
  higher degrees;
- the first qualified Stellar Model in each dimension/format stratum;
- `CP^2` and `RP^4` source-lineage representatives.

The cohort covers both formats, every counted source lineage, empty and
disconnected cases, and every G3 feature class. The release ledger must expand
the selection components into exactly 66 Model IDs and name, for every Model,
the generator result and evidence references, the assigned oracle authority,
the oracle result and evidence references, and the declared independence
relation between them. Oracle assignments follow the manifest's pinned
source-lineage policy and are fixed before agreement is observed; a generic
“independently checked” label or two results from the same authority does not
qualify. Disagreement creates retained competing assertions and a Conflict; it
never overwrites canonical output.

## Common-manifold QA cohort

The corpus makes 128 common manifolds available. The pinned QA acceptance
cohort contains 60 exact instances across nine rollups:

- `S^1..S^8`;
- orientable and nonorientable surfaces of genera `2..9`;
- `T^2..T^5`;
- `RP^2, RP^4, RP^5, RP^6`;
- the first 12 listed lens spaces;
- the first eight listed sphere products;
- `D^1..D^4`;
- `Sigma_g x S^1` for `g=2..5`.

Ticket 12 will run 100 checked-in prompts: 60 integral lookups, 8 coefficient
or reduced-convention cases, 12 structured example queries, 8 comparison or
provenance questions, and 12 hallucination/uncertainty cases. The QA agent is a
tool-constrained consumer of the public structured interface; it receives no
SQL, files, network, expected answers, embeddings, vector index, or bespoke
natural-language parser.

## Release-ledger obligations

The expanded counted ledger must name, rather than merely total:

- for every source lock: owner, URL, exact release or commit pin, retrieval
  record, upstream locator, advertised checksum when supplied, our SHA-256,
  byte length, attribution and observed licensing facts, and any retained
  upstream correction or supersession;
- curated public IDs, parameters, exactly one G1 family rollup, identity
  evidence, QA tags, primary Model, dimension, and completeness references;
- for every Model and artifact: immutable IDs, its one counted bucket,
  representation kind, schema, decoder, importer, and normalizer versions,
  raw and neutral hashes, exact source locator, derivation root, dimension,
  ordered cells, regularity witness where required, distinctness decision, and
  qualification or rejection outcome;
- for every owned computation: run ID; input, Model, chain, output, and log
  hashes; ordered bases and boundary matrices; algorithm, implementation, and
  library versions; parameters and environment; exit status; and deterministic
  rerun digest;
- for every Homology assertion: the full subject/theory/coefficient/reduced/
  convention/degree slot, knowledge state, typed payload, completeness scope,
  derivation and evidence references, admission event, and current-projection
  outcome;
- every `model_of` relation, including the exact equivalence claim, review and
  admission references, and the explicit rule governing which properties may
  be preserved across it, together with the exact 25/20 pairing cohorts;
- every G3 qualifying pair and exact `(p,e,multiplicity)` rows;
- every expected and selected G4 slot;
- every G5 assertion/event/conflict ID;
- the exact 66 validation Models, generator/oracle assignments, evidence and
  independence records described above;
- for every Snapshot: exact membership and event references plus projection,
  manifest, and export digests;
- rejected candidates and declared omissions.

The canonical release manifest records the generated ledger digest. Planning
counts, upstream sidecars, or a successful verifier of this selection spec are
not substitutes for the release audit.

## Declared omissions

`0.0.1` does not count live polyDB twice, unverified source rows, Regina
generalized triangulations, finite simplicial sets, Delta-complexes, nonregular
attaching-map CW presentations, relabelings, mass subdivisions, implicit
promotion, or upstream Homology values as canonical truth. Licensing posture
remains undecided; visible source facts and attribution are still retained.
