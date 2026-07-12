# Common-example priorities after the local preview

Date: 2026-07-12
Status: source-backed prioritization for external review; not a corpus-manifest
amendment, an ingestion record, or release evidence

## Result

The first post-review additions should be:

1. `CP^2` and a small visible slice of Moore spaces;
2. the Poincaré homology 3-sphere;
3. K3 and `HP^2`, after the smaller additions exercise the full import path;
4. provenance-bearing wedges, products, suspensions, smashes, and cofibres; and
5. only later, explicitly bounded or otherwise qualified work on `BG`,
   `K(A,n)`, Thom spaces, and stable-homotopy objects.

This is a ranking by **reference utility, reviewer recognition, discriminating
power, and availability of a concrete route into the repository**. It is not a
bibliometric ranking. No citation database was queried, and this note does not
claim that one example has a larger publication count than another. Hatcher and
May supply author-owned reference texts; Sage supplies executable finite-model
recipes; Isaksen--Wang--Xu supply a primary account of modern computational
stable-homotopy practice. Those sources answer different questions and are not
collapsed into a single popularity score.

The existing 60-subject preview must remain frozen. These priorities belong to
a new external-review cohort and, where already selected, to the unimplemented
`0.0.1` corpus plan.

## Why `CP^2` is planned but absent

`CP^2` is already present in the normative selection plan. The
[corpus contract](../contracts/corpus-manifest-v0.0.1.md) selects it among the
174 curated conceptual spaces and places it in the 66-Model independent-
validation cohort. The
[source-pin audit](v0.0.1-corpus-source-pins.md) fixes SageMath 10.9 and its
`simplicial_complexes.ComplexProjectivePlane()` recipe, whose literal abstract
simplicial complex has 9 vertices and 36 maximal facets. Current
[Sage documentation](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html#sage.topology.simplicial_complex_examples.ComplexProjectivePlane)
describes the same minimal triangulation and f-vector.

The runnable preview is a different artifact: it is a hand-built, fixed
60-common-manifold QA cohort, not an ingestion of the planned 174-space corpus.
It contains only the nine rollups listed in the corpus contract's QA section.
Consequently `CP^2` returns a typed unresolved-subject outcome in the preview.
That outcome is correct and is useful as a hallucination test.

Promoting familiar textbook Homology groups into the preview would skip the
essential work. Before `CP^2` can become a database-backed answer, the pinned
Sage recipe must be materialized, neutrally exported, hashed, parsed as a
finite simplicial Model, run through the owned general-chain computation, and
connected to the conceptual space by reviewed model evidence. The resulting
Homology assertions must cite that computation and one immutable Snapshot.
Neither Sage's displayed Homology nor mathematical memory substitutes for
those records.

`CP^2` is especially valuable beyond name recognition. Hatcher's
[cohomology chapter](https://pi.math.cornell.edu/~hatcher/AT/ATch3.pdf) uses it
to show that additive Homology or additive cohomology cannot distinguish
`CP^2` from `S^2 ∨ S^4`, while the cup product can. A Homology-only product
should therefore answer the groups it has and explicitly refuse the stronger
homotopy conclusion. That makes `CP^2` both the first polish blocker and a
forward-compatibility test for a future cited-implication graph.

## Ranked additions

### 1. `CP^2` and Moore spaces

Add `CP^2` first through the already pinned Sage route. Then expose a small
external-review slice `M(Z/q,1)` for `q = 3, 4, 5`; do not create a second
identity for `M(Z/2,1)`, which the corpus contract identifies with `RP^2`.

Moore spaces are unusually efficient test objects. Hatcher's
[Homology chapter, Example 2.40](https://pi.math.cornell.edu/~hatcher/AT/ATch2.pdf)
treats `M(G,n)` as a standard construction and realizes the finite-cyclic case
by attaching an `(n+1)`-cell to `S^n` by a degree map. Sage's
[Moore-space constructor](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html#sage.topology.simplicial_complex_examples.MooreSpace)
provides finite triangulations for mod-`q` Moore spaces and demonstrates that
suspension moves the torsion class to a higher degree.

They test prime torsion, prime powers, coefficient changes, degree shifts,
reduced conventions, and exact pattern queries with very little unrelated
geometry. The release plan already selects an owned Moore seed-and-suspension
route and controlled mixed bouquets. The post-review slice should exercise
that route; it must not import the textbook construction or Sage's printed
answer as an assertion. Each parameter value remains a distinct conceptual
space with its own finite Model, computation, assertions, and evidence.

### 2. The Poincaré homology 3-sphere

Sage provides a
[16-vertex triangulation](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html#sage.topology.simplicial_complex_examples.PoincareHomologyThreeSphere)
of the Poincaré homology 3-sphere. Its documentation deliberately compares the
space with `S^3`: their integral Homology agrees, while the Poincaré sphere has
nontrivial fundamental group of order 120.

That makes it the best next comparison-safety fixture. The database should
retain `S^3` and the Poincaré sphere as different subjects and may report equal
selected Homology assertions. It must not infer identity, homeomorphism, or
homotopy equivalence from that equality. Unless a separately supported
fundamental-group capability is added, the product should not repeat the
group-order claim as a database result; the claim here only explains why the
fixture is discriminating.

The model still requires a pinned source artifact, neutral facet export,
owned computation, model assertion, and evidence expansion. Availability in a
Sage catalog is a source route, not admission.

### 3. K3 and `HP^2`

Sage documents a
[16-vertex, 288-facet K3 triangulation](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html#sage.topology.simplicial_complex_examples.K3Surface)
and a
[15-vertex, 490-facet `HP^2` triangulation](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html#sage.topology.simplicial_complex_examples.QuaternionicProjectivePlane).
K3 also has a second attributed literal-facet route in the pinned HAP source
tree, which makes it a candidate for cross-source validation once the relation
and independence of the two routes have been established.

These examples extend the recognizable manifold range into dimensions four
and eight and make the review cohort more credible to a homotopy theorist.
They follow rather than precede `CP^2`, Moore spaces, and the Poincaré sphere
because their larger chain complexes add implementation cost without first
testing a new safety outcome. They enter only after the same neutral-export,
owned-computation, identity, and evidence route works on the smaller examples.
Sage's names, model descriptions, and cached computations remain attributed
claims, not canonical Homology.

### 4. Constructions as cited implication edges

The database already includes hand-built products in its preview, but the
longer-term value lies in retaining the construction, its inputs, and its
mathematical justification rather than merely adding more output rows.
Hatcher's [book and chapter index](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html)
uses wedges, products, suspensions, smash products, and cell attachments
throughout. May's
[chapters on based cofiber and fiber sequences](https://www.math.uchicago.edu/~may/CONCISE/ConciseRevised.pdf)
define smash products, suspensions, and homotopy cofibers as basic organizing
constructions.

Prioritize finite, deterministic cases for which every input Model and, for a
cofiber, the map are explicit. A construction should create a new immutable
Model artifact plus cited derivation and relation assertions. It must not
silently merge the result with a named space, infer a conceptual-space result
at read time, or reuse a group formula as though it were an owned computation.
This is the natural first substrate for the proposed human-reviewable graph:
nodes are cited claims, and edges are cited implications or preserving
constructions whose hypotheses a reviewer can inspect.

### 5. Bounded and infinite-object work later

`BG`, `K(A,n)`, Thom spaces, spectra, and related examples are central rather
than obscure. May constructs
[classifying spaces and Eilenberg--Mac Lane spaces](https://www.math.uchicago.edu/~may/CONCISE/ConciseRevised.pdf)
and later develops Thom spaces, generalized Homology, and stable homotopy in
the same text. The Isaksen--Wang--Xu
[stable-stems survey and computation](https://arxiv.org/abs/2001.04247)
shows why this direction matters computationally: it organizes machine-aided
stable-stem results, records remaining uncertainties, and uses graphical
descriptions to expose structure rather than presenting a flat list of
groups.

Those references establish mathematical importance, not admissibility as
finite Models. Standard `BG` and `K(A,n)` constructions are generally not
finite presentations of the full spaces. A finite skeleton, truncation, or
bounded computation is not silently a Model of the unbounded object and must
carry its bound in both identity and completeness claims. Thom spaces require
an explicit bundle and quotient construction; some particular Thom spaces can
have finite CW Models, but the name alone provides neither a finite artifact
nor the required provenance. Spectra require a new subject/model boundary and
are outside the ordinary-space `0.0.1` contract.

This tier should begin only after the finite construction graph is reviewable.
Its first design task is to specify bounded identity, map, and completeness
semantics, not to insert remembered stable-homotopy tables into the existing
Homology schema.

## Review and hosting consequences

- Preserve `local-preview-60` exactly; add a separately named external-review
  cohort rather than changing the meaning of its fixed acceptance pack.
- Keep unresolved `CP^2` in the current adversarial review. Its absence tests
  whether the agent respects the Snapshot boundary.
- Treat `CP^2` as the first corpus-polish blocker before public hosting, then
  add the small Moore slice and Poincaré sphere. Defer K3 and `HP^2` until that
  path is measured and reproducible.
- Require every external-review answer to distinguish source assertions,
  owned computations, and implications. A mathematically correct statement
  with no selected assertion and expanded evidence is a grounding failure.
- Host only the existing four read-only operations over an immutable Snapshot
  at first. Do not place an unrecorded inference layer between the reviewer
  and the evidence-bearing database responses.

## Source roles and limits

| Source | What it supports here | What it does not support |
| --- | --- | --- |
| [Hatcher, *Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html) | Recognition and mathematical test value of `CP^2`, Moore spaces, and standard constructions | Citation-frequency counts or database-ready artifacts |
| [May, *A Concise Course in Algebraic Topology*](https://www.math.uchicago.edu/~may/CONCISE/ConciseRevised.pdf) | Importance of cofibers, smash products, `BG`, `K(A,n)`, Thom spaces, generalized Homology, and stable homotopy | A claim that these full objects fit the current finite-Model boundary |
| [Sage topology examples](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html) | Concrete routes to finite triangulations of `CP^2`, Moore spaces, the Poincaré sphere, K3, and `HP^2` | Automatic identity, qualification, or canonical Homology assertions |
| [Isaksen--Wang--Xu, *Stable homotopy groups of spheres*](https://arxiv.org/abs/2001.04247) | Contemporary computational motivation, graphical structure, and explicit retained uncertainty | Ordinary-Homology corpus priorities, finite Models, or evidence for preview answers |

The implementation authority remains the repository's pinned manifest,
source-lock audit, model-boundary ADR, and eventual release ledger. This survey
orders follow-up work; it does not replace any of them.
