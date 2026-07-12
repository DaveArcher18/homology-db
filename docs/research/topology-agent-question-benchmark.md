# Topology-agent question benchmark

**Status:** prospective benchmark design for `named-atlas-review-v1`, not a
claim about the capabilities of `local-preview-60`
**Survey date:** 2026-07-12
**Scope:** the four public Homology DB operations, one immutable Snapshot, and
the named-atlas corpus defined by the active Wayfinder map

## Executive conclusion

The most useful first benchmark is not a list of isolated table lookups. Public
questions repeatedly combine a familiar named space with one of five sources of
error: coefficient conventions, reduced versus unreduced degree zero, torsion,
a construction such as a product or cofiber, or an unjustified conclusion from
equal Homology. A trustworthy agent therefore needs to do three things at once:

1. return the selected immutable assertion and its exact evidence chain;
2. state the coefficient, reduced/unreduced, degree, and completeness scope;
3. refuse any extra conclusion that is not represented by a selected assertion.

The ordered manifest below contains 68 questions. It deliberately includes
ordinary calculations, evidence inspection, family boundary cases, conflicts,
and unsupported requests. Passing it requires tickets 03--09 of the
`named-atlas-review-v1` map; ticket 10 is the clean-checkout audit of the result.

## Source policy: question shape is not assertion evidence

This report uses two disjoint source roles.

- **QP (question-pattern evidence)** indicates that people publicly ask a
  question of this shape. Mathematics Stack Exchange is useful for this limited
  purpose. Its answers, vote totals, and view totals are not assertion evidence.
- **AE (assertion-evidence candidate)** is an author-owned book, official
  project documentation, or a primary source that may ground expected
  mathematical behavior after ticket 06 pins an exact revision and pinpoint.
- **PR (project rule)** is a repository-owned contract governing typed outcomes,
  provenance, Snapshot selection, and the prohibition on hidden inference. It
  is not mathematical evidence.

Wikipedia is used for neither role. Search-result view counts are mutable and
biased, so this is a qualitative recurrence survey rather than a statistical
claim about all topology questions.

### Question-pattern sources

| Code | Public pattern source | What it contributes |
|---|---|---|
| QP-RP | [Questions about Hatcher's computation of `RP^n`](https://math.stackexchange.com/questions/802479/homology-of-real-projective-space-im-not-satisfied-with-the-argument-in-hatc) | Family lookup, parity, cellular boundaries, and requests for derivation rather than a bare table. |
| QP-RED | [Use of reduced Homology](https://math.stackexchange.com/questions/51142/use-of-reduced-homology) and [the suspension degree shift](https://math.stackexchange.com/questions/3576791/long-exact-sequence-of-reduced-homology) | Degree-zero conventions, wedges, suspensions, and the need to name the convention explicitly. |
| QP-COEF | [`RP^n` with `Z/2` coefficients](https://math.stackexchange.com/questions/86140/cohomology-of-mathbb-rpn-with-mathbb-z-2-coefficients), [why coefficient systems are used](https://math.stackexchange.com/questions/619544/why-homology-with-coefficients), and [integral versus field coefficients](https://math.stackexchange.com/questions/3508832/homology-with-integral-coefficients-vs-homology-with-field-coefficients) | Field dimensions are not obtained by simply relabeling integral groups; torsion and `Tor` matter. |
| QP-CON | [Degree-three mapping-cone calculation](https://math.stackexchange.com/questions/4731900/calculate-homology-of-mapping-cone), [finite-CW smash products](https://math.stackexchange.com/questions/4204031/computing-homology-of-smash-product-of-two-finite-cw-complexes), and [relative Homology reduced to wedges](https://math.stackexchange.com/questions/95374/relative-homology-groups-of-the-torus) | Cofibers, smashes, products, and wedges are recurring calculation shapes. |
| QP-CMP | [Non-homotopic spaces with the same Homology](https://math.stackexchange.com/questions/3678039/non-homotopic-spaces-with-the-same-homology-groups/3678073) and [same Homology but different fundamental group](https://math.stackexchange.com/questions/4333250/same-homology-but-different-fundamental-group) | Equal graded groups do not establish identity, homeomorphism, or homotopy equivalence. |
| QP-MOD | [Why a proposed `RP^2` triangulation is not a simplicial complex](https://math.stackexchange.com/questions/2658523/triangulation-of-the-projective-plane-number-of-points-required) and [whether cellular Homology depends on the CW structure](https://math.stackexchange.com/questions/2009496/does-cellular-homology-depend-on-cw-structure) | Users confuse Conceptual spaces with Models and need inspectable Model kind, validation, and provenance. |

### Assertion-evidence candidates

| Code | Author-owned or official source | Relevant pinpoints and role |
|---|---|---|
| AE-H | Allen Hatcher, [*Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), distributed from the [author's book page](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html) | `CP^n` CW structure at printed pp. 6--8; Moore spaces and `RP^n`/lens-space calculations in Examples 2.40--2.43; coefficients in §2.2; universal coefficients in §3.A; products, wedges, suspensions, smashes, quotients, and mapping cones throughout Chapters 0, 2, and 3. |
| AE-M | J. P. May, [*A Concise Course in Algebraic Topology*](https://www.math.uchicago.edu/~may/CONCISE/ConciseRevised.pdf) | Cofibrations and cofiber sequences in Chapters 6 and 8; cellular Homology and examples in Chapter 13; reduced Homology and suspension in Chapter 14; universal coefficients and Künneth in Chapter 17. |
| AE-SC | SageMath, [official simplicial-complex examples](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html) | Official finite Models for the 9-vertex `CP^2`, K3, Moore spaces, the 16-vertex Poincaré sphere, `RP^2`, and `HP^2`; the docs also expose example Homology computations and source links. |
| AE-SS | SageMath, [official simplicial-set examples](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_set_examples.html) | Compact `RP^n`; `CP^0` through `CP^4`; and a Hopf-map mapping cone whose Homology agrees with the supplied `CP^2` Model. |
| PR-CUR | [`current-projection-v1`](../contracts/current-projection-v1.md) and [`homology-pattern-v1`](../contracts/homology-pattern-v1.md) | Immutable assertions, conflict fences, selected Knowledge states, completeness, and three-valued search behavior. |
| PR-MAP | [Named-atlas Wayfinder map](../../.scratch/named-atlas-review-v1/map.md) and tickets 03--10 | Materialized family range, Model qualification boundary, four-operation contract, QA gate, and release audit. |

Ticket 06 must turn each AE candidate into an exact source artifact, revision,
hash, and pinpoint before it can ground a database assertion. This report does
not substitute a URL for that ingestion work.

## Required answer discipline

Every successful answer in this benchmark must expose the `snapshot_id`,
subject ID, convention, coefficient domain, completeness scope, immutable
assertion ID, and all evidence/dependency IDs. Every used subject must be
evidence-expanded. A derived specialization must name the family assertion and
specialization edge; a computation must name its qualified Model, run,
algorithm, environment, inputs, outputs, and hashes.

The expected outcome labels below are prospective API labels:

- `answer`: one or more selected, grounded assertions answer the request;
- `outside_materialized_range`: the family exists, but the requested integer
  parameter lies above the Snapshot's materialized bound;
- `model_not_qualified`: mathematical Homology may be present, but no admitted
  Model supports the requested Model/computation claim;
- `unsupported_coefficient`: the coefficient domain is outside the operation's
  declared support;
- `not_computed`: the requested computational artifact or map has an explicit
  uncomputed state;
- `not_found` / `subject_not_resolved`: no selected subject resolves;
- `ambiguous_subject`: more than one selected subject matches and no identity
  assertion resolves the ambiguity;
- `invalid_parameter`: the family parameter violates its type/domain;
- `unsupported_invariant`: the request is for something other than supported
  Homology data;
- `unresolved_selection`: Current is fenced by a conflict or missing promotion.

None of these labels implies a mathematical zero unless an exact selected
assertion explicitly contains the zero group.

## Ordered benchmark manifest

`T03`--`T10` refer to the correspondingly numbered issues in
`.scratch/named-atlas-review-v1/issues/`. `T09` freezes and grades every row;
the earlier ticket shown in each row is the principal enabling implementation.

### I. Named spaces and families

| ID | Question | Expected outcome and required capability | Source roles | Enables |
|---|---|---|---|---|
| N01 | What is integral `H_*(RP^2)`? | `answer`: `H_0=Z`, `H_1=Z/2`, all other degrees zero within a complete finite-dimensional scope; return the specialization and source chain. | QP-RP; AE-H | T06, T07, T08 |
| N02 | What is integral `H_*(RP^5)`? | `answer`: `Z` in degrees 0 and 5, `Z/2` in degrees 1 and 3, zero otherwise; exercise parity and top-dimensional orientability. | QP-RP; AE-H, AE-SS | T06, T07 |
| N03 | What is integral `H_*(CP^2)`? | `answer`: `Z` in degrees 0, 2, and 4 and zero otherwise; expose literature specialization plus independent qualified Models. | QP-RP; AE-H, AE-SC, AE-SS | T04--T08 |
| N04 | What is integral `H_*(CP^12)`? | `answer`: `Z` in every even degree 0 through 24 and zero otherwise, grounded by a materialized specialization, not query-time formula evaluation. | AE-H; PR-MAP | T03, T06--T08 |
| N05 | What is integral `H_*(HP^2)`? | `answer`: `Z` in degrees 0, 4, and 8 and zero otherwise; keep cited family evidence separate from the Sage Model/computation. | AE-H, AE-SC | T04, T06, T07 |
| N06 | What is `H_*(M(Z/3,1);Z)`? | `answer`: connected, with reduced Homology `Z/3` only in degree 1; resolve the Moore-space parameters explicitly. | AE-H, AE-SC | T03, T06, T07 |
| N07 | Does the Poincaré homology sphere have the same integral Homology as `S^3`? | `answer`: yes as graded integral groups, with both subjects and all evidence expanded; make no equivalence inference. | QP-CMP; AE-SC | T06--T09 |
| N08 | What is integral `H_*(L(5,1))`? | `answer`: `Z` in degrees 0 and 3, `Z/5` in degree 1, and zero otherwise for the selected 3-dimensional lens-space convention. | AE-H | T06, T07 |
| N09 | What is integral Homology of the selected K3 surface? | `answer`: return the complete selected assertion (`Z` in degrees 0 and 4, `Z^22` in degree 2, zero otherwise) and distinguish source evidence from the 16-vertex Model/run. | AE-SC | T05--T08 |
| N10 | What is integral Homology of the orientable genus-two surface? | `answer`: `Z` in degrees 0 and 2 and `Z^4` in degree 1; include the subject's naming and completeness scope. | QP-CON; AE-H | T06--T08 |
| N11 | What is integral Homology of the nonorientable genus-three surface `N_3`? | `answer`: `H_0=Z`, `H_1=Z^2 + Z/2`, no top `Z`; the response must use normalized summands rather than prose-only notation. | QP-COEF; AE-H | T03, T06--T08 |
| N12 | What is integral Homology of `T^3`? | `answer`: ranks `1,3,3,1` in degrees `0..3`, complete above dimension 3; expose the product identity/model if selected. | QP-CON; AE-H/AE-M | T06--T08 |
| N13 | Give the cited integral-Homology theorem for `RP^n`, all finite `n>=0`. | `answer`: return the family assertion and quantified parameter domain itself, including parity cases; do not claim that all instances are materialized. | QP-RP; AE-H | T03, T06, T08 |
| N14 | Give the cited integral-Homology theorem for `CP^n`, all finite `n>=0`. | `answer`: return the family assertion (`Z` in even degrees `0..2n`) with its source and formula representation; do not silently specialize an unmaterialized instance. | AE-H | T03, T06, T08 |

### II. Coefficients, reduced conventions, and torsion

| ID | Question | Expected outcome and required capability | Source roles | Enables |
|---|---|---|---|---|
| C01 | What is reduced integral Homology of a point? | `answer`: exact zero in every degree, explicitly reduced; zero comes from a selected assertion/derivation, not absent rows. | QP-RED; AE-H/AE-M | T03, T07, T08 |
| C02 | Compare ordinary and reduced integral Homology of `S^2`. | `answer`: ordinary `H_0=Z`, `H_2=Z`; reduced has only `Z` in degree 2. Return two convention-qualified assertions. | QP-RED; AE-H | T03, T07, T08 |
| C03 | What is `H_*(RP^5;F_2)`? | `answer`: one-dimensional over `F_2` in every degree 0 through 5, zero otherwise; dependency chain must include coefficient specialization/UCT evidence. | QP-COEF; AE-H, AE-SS | T03, T06--T08 |
| C04 | What is `H_*(RP^4;F_3)`? | `answer`: `F_3` only in degree 0; show why integral 2-torsion does not become an `F_3` class. | QP-COEF; AE-H | T03, T06--T08 |
| C05 | What is `H_*(RP^4;F_2)`? | `answer`: one-dimensional in degrees 0 through 4, including top degree despite vanishing integral top Homology. | QP-COEF; AE-H | T03, T06--T08 |
| C06 | What is `H_*(CP^3;F_2)`? | `answer`: one-dimensional in degrees 0, 2, 4, and 6 and zero otherwise; show field dimensions as normalized data. | AE-H, AE-SS | T03, T06--T08 |
| C07 | What is `H_*(M(Z/3,1);F_3)`? | `answer`: `F_3` in degrees 0, 1, and 2; the degree-2 class must retain its `Tor` dependency rather than being omitted. | QP-COEF; AE-H | T03, T06--T08 |
| C08 | What is `H_*(M(Z/3,1);F_2)`? | `answer`: `F_2` only in degree 0; preserve completeness and do not turn lack of 2-primary torsion evidence into missing data. | QP-COEF; AE-H | T03, T06--T08 |
| C09 | Find materialized named spaces with a `Z/2` summand in `H_1`. | `answer`: Snapshot-bounded query results only, each with its own selected assertion/evidence IDs and an explicit query-completeness statement. | QP-COEF; PR-CUR | T03, T07, T08 |
| C10 | Find materialized named spaces with 3-primary torsion in any degree. | `answer`: Snapshot-bounded candidates such as the selected mod-3 Moore and relevant lens spaces; normalized primary summands drive the query. | QP-COEF; AE-H; PR-CUR | T03, T07, T08 |
| C11 | Is `H_0(X)=0` for a connected nonempty space when I request reduced Homology? | `answer`: explain that reduced `H_0` is zero while ordinary `H_0` is `Z`, using separate convention-qualified assertions/definitions. | QP-RED; AE-H/AE-M | T03, T08 |
| C12 | What is rational Homology of `CP^2`? | `unsupported_coefficient` if `Q` is not in the declared supported coefficient set; the agent may identify the resolved subject but must not fill in groups from the integral answer. | QP-COEF; PR-MAP | T08, T09 |

### III. Bounded constructions

These questions recommend the exact bounded construction slice to materialize in
ticket 07. If a different slice is chosen, the manifest must change explicitly;
the agent must not synthesize these answers at query time.

| ID | Question | Expected outcome and required capability | Source roles | Enables |
|---|---|---|---|---|
| X01 | What is integral Homology of `S^1 vee S^2`? | `answer`: `Z` in degrees 0, 1, and 2; name the wedge construction assertion and reduced-wedge dependencies. | QP-RED, QP-CON; AE-H/AE-M | T03, T06, T07 |
| X02 | What is integral Homology of `S^1 x S^2`? | `answer`: `Z` in degrees 0, 1, 2, and 3; expose product and Künneth dependencies. | QP-CON; AE-H/AE-M | T03, T06, T07 |
| X03 | Do `S^1 vee S^2` and `S^1 x S^2` have the same Homology? | `answer`: no, degree 3 distinguishes them; comparison must cite each subject's assertions rather than use name-based heuristics. | QP-CON; AE-H/AE-M | T07--T09 |
| X04 | What is reduced integral Homology of `Sigma S^2`? | `answer`: `Z` only in degree 3, with a cited suspension/degree-shift implication and the selected construction assertion. | QP-RED; AE-H/AE-M | T03, T06--T08 |
| X05 | What is integral Homology of `Sigma RP^2`? | `answer`: connected, with `Z/2` in degree 2 and no other positive-degree group; preserve the reduced shift dependency. | QP-RED; AE-H/AE-M | T03, T06--T08 |
| X06 | What is integral Homology of `S^1 smash S^2`? | `answer`: that of `S^3`; record the smash construction and any identity assertion explicitly rather than rewriting the subject silently. | QP-CON; AE-H/AE-M | T03, T06--T08 |
| X07 | What is the Homology of the mapping cone of a degree-3 map `S^1 -> S^1`? | `answer`: connected with `H_1=Z/3`, a materialized cofiber/`M(Z/3,1)` identity and exact map-degree dependency. | QP-CON; AE-H/AE-M | T03, T05--T08 |
| X08 | What is the Homology of the mapping cone of a degree-4 map `S^1 -> S^1`? | `answer`: connected with `H_1=Z/4`; this is the bounded `M(Z/4,1)` construction and must not be inferred from X07 by text substitution. | QP-CON; AE-H/AE-M | T03, T05--T08 |
| X09 | What is integral Homology of `RP^2 x S^1`? | `answer`: `H_0=Z`, `H_1=Z + Z/2`, `H_2=Z/2`, zero otherwise; retain tensor/Tor-free product dependencies. | QP-CON; AE-H/AE-M | T03, T06--T08 |
| X10 | What is reduced Homology of the cofiber of `id:S^2->S^2`? | `answer`: exact zero in every degree for the materialized cofiber; evidence must include the actual map assertion, not merely equal domain/codomain names. | QP-CON; AE-H/AE-M | T03, T05--T08 |

### IV. Comparisons, identities, and non-equivalence safety

| ID | Question | Expected outcome and required capability | Source roles | Enables |
|---|---|---|---|---|
| R01 | Compare integral Homology of the Poincaré sphere and `S^3`. | `answer`: the groups agree degree by degree; return two assertion/evidence chains and state only what the comparison establishes. | QP-CMP; AE-SC | T06--T09 |
| R02 | Since those groups agree, are the Poincaré sphere and `S^3` homotopy equivalent? | `unsupported_invariant` or a separately grounded relation answer; Homology equality alone must never produce an equivalence. | QP-CMP; AE-SC; PR-CUR | T03, T08, T09 |
| R03 | Compare `T^2` with `S^1 vee S^1 vee S^2`. | `answer`: integral Homology agrees; do not infer identity/equivalence. Any stronger distinction requires a separately selected invariant outside this tool contract. | QP-CMP; AE-H/AE-M | T07--T09 |
| R04 | Compare `CP^2` with `S^2 vee S^4`. | `answer`: integral Homology agrees; no homotopy-equivalence claim follows from this database evidence. | QP-CMP; AE-H | T07--T09 |
| R05 | Do the finite simplicial-set and 9-vertex triangulation Models of `CP^2` compute the same Homology? | `answer`: yes only after both qualified runs are selected and expanded; report independent Model IDs, hashes, algorithms, and agreement record. | QP-MOD; AE-SC, AE-SS | T04, T05, T07--T09 |
| R06 | Do the compact simplicial-set and independent abstract-simplicial Models of `RP^2` agree? | `answer`: yes after cross-model validation; agreement is a Model/result relation, not silent Model merging. | QP-MOD; AE-SS, AE-SC | T04, T05, T07--T09 |
| R07 | Are `CP^1` and `S^2` the same atlas subject? | `answer`: resolve through the selected explicit identity assertion and aliases/permanent labels; do not infer identity merely from equal Homology. | AE-H; PR-MAP | T03, T07, T08 |
| R08 | Are `RP^3` and `L(2,1)` the same atlas subject? | `answer`: resolve via the explicit identity assertion and lens-space convention; return that assertion's evidence. | AE-H; PR-MAP | T03, T06--T08 |
| R09 | Can Homology distinguish the selected K3 surface from `CP^2`? | `answer`: yes, their degree-2 free ranks are 22 and 1; cite both complete assertions. | AE-H, AE-SC | T06--T09 |
| R10 | Can Homology distinguish `CP^4` from `HP^2`? | `answer`: yes, `CP^4` also has nonzero groups in degrees 2 and 6; compare selected specializations without equating their dimension-8 top classes. | AE-H, AE-SC, AE-SS | T06--T09 |

### V. Completeness, Models, provenance, and editorial history

| ID | Question | Expected outcome and required capability | Source roles | Enables |
|---|---|---|---|---|
| P01 | Show all evidence for the claim `H_2(CP^2;Z)=Z`. | `answer`: expand reference/pinpoint/hash, family specialization edge, both selected Model artifacts and runs where applicable, reviews, and Snapshot membership. | AE-H, AE-SC, AE-SS; PR-CUR | T03--T08 |
| P02 | Which `CP^2` Homology claims come from literature, computation, or specialization? | `answer`: separately typed assertions and dependencies; no blended “source” paragraph and no computation credited for a citation-only degree. | PR-CUR, PR-MAP | T03, T05--T08 |
| P03 | Does `CP^7` have Homology if no Model is qualified? | `answer` plus `model_not_qualified`: the cited/materialized Homology remains available while Model status is visibly separate. | AE-H; PR-MAP | T03, T07, T08 |
| P04 | Give an explicit cycle representative for the generator of `H_24(CP^12;Z)`. | `not_computed` unless a selected qualified run actually stores it; do not turn the abstract generator or family formula into a chain. | PR-CUR, PR-MAP | T05, T08, T09 |
| P05 | What map on Homology is induced by an arbitrary user-supplied map `CP^2 -> S^4`? | `not_computed`/unsupported map input unless the exact map and run are selected; matching domain/codomain groups do not determine the map. | AE-H/AE-M; PR-CUR | T05, T08, T09 |
| P06 | What does “primary torsion summand” mean, and is that definition evidence for `H_1(RP^2)`? | `answer`: expand the reviewed Knowledge revision with `role: exposition`, then explicitly say it is not assertion evidence; expand the real evidence separately. | PR-MAP | T03, T08, T09 |
| P07 | A Homology assertion was corrected. Can I inspect both versions, and which one is Current? | `answer`: both immutable assertions/editorial events remain addressable; Snapshot selection names the promoted one and its review. No overwrite. | PR-CUR | T03, T08, T09 |
| P08 | Two admitted exact assertions conflict for the same fully qualified slot. What does the agent answer? | `unresolved_selection`: expose both assertions and conflict record; select neither and never average, union, or prefer the newer silently. | PR-CUR | T03, T08, T09 |

### VI. Family boundaries and adversarial unsupported requests

| ID | Question | Expected outcome and required capability | Source roles | Enables |
|---|---|---|---|---|
| A01 | What is integral Homology of `RP^12`? | `answer`: the last materialized `RP` instance, with exact IDs and completeness. This is an inclusive-boundary test. | AE-H; PR-MAP | T07--T09 |
| A02 | What is integral Homology of `RP^13`? | `outside_materialized_range`; may expose the all-`n` family theorem but must not display specialized groups without an immutable instance assertion. | AE-H; PR-MAP | T03, T08, T09 |
| A03 | What is integral Homology of `CP^12`? | `answer`: the last materialized `CP` instance, even though its Model status is unqualified. | AE-H; PR-MAP | T07--T09 |
| A04 | What is integral Homology of `CP^13`? | `outside_materialized_range`, distinct from `model_not_qualified`, `not_found`, and zero. | AE-H; PR-MAP | T03, T08, T09 |
| A05 | What is integral Homology of `CP^100`? | `outside_materialized_range`; do not evaluate the stored family formula at query time. | AE-H; PR-MAP | T03, T08, T09 |
| A06 | What is `H_*(CP^-1;Z)`? | `invalid_parameter`, because the typed family parameter requires `n>=0`; not `outside_materialized_range`. | AE-H; PR-MAP | T03, T08, T09 |
| A07 | Resolve “the projective plane.” | `ambiguous_subject` with candidates `RP^2`, `CP^2`, and `HP^2` unless the input supplies the scalar field; no popularity-based default. | QP-RP, QP-MOD; PR-MAP | T03, T08, T09 |
| A08 | What is integral Homology of `CP^infinity`? | `not_found`/`subject_not_resolved` in the selected core atlas unless that distinct infinite object is explicitly admitted; it is not a finite-`n` specialization. | AE-H; PR-MAP | T03, T08, T09 |
| A09 | What is `H_*(S^2;Q)`? | `unsupported_coefficient`; do not replace `Z` by `Q` from memory or silently derive a rational answer. | QP-COEF; PR-MAP | T08, T09 |
| A10 | What is `H_*(RP^2;Z/4)`? | `unsupported_coefficient` unless composite coefficients are explicitly selected; do not confuse a coefficient ring with a `Z/4` torsion summand query. | QP-COEF; PR-MAP | T03, T08, T09 |
| A11 | What is the integral cohomology ring of `CP^2`? | `unsupported_invariant` for a Homology-only operation even though an AE source contains the answer; source availability does not enlarge the public contract. | AE-H; PR-MAP | T08, T09 |
| A12 | What is the fundamental group of the Poincaré sphere? | `unsupported_invariant` unless a separately typed selected assertion is exposed by the contract; never smuggle the official Sage doc's value into a Homology response. | QP-CMP; AE-SC; PR-MAP | T08, T09 |
| A13 | List every space in mathematics with the integral Homology of `S^3`. | `answer` only as a Snapshot-bounded materialized query with explicit incompleteness; never present selected examples as an exhaustive mathematical classification. | QP-CMP; PR-CUR | T03, T08, T09 |
| A14 | Include a newly discovered but unselected subject in the example-query result. | Refuse: `query_examples` searches only assertions selected into the requested immutable Snapshot. External existence is not Snapshot membership. | PR-CUR, PR-MAP | T03, T08, T09 |

## Coverage and grading

The manifest allocates questions as follows:

| Category | Count | Principal failure caught |
|---|---:|---|
| Named spaces and family theorems | 14 | Missing representative examples, parity errors, formula prose without materialized assertions |
| Coefficients/reduced/torsion | 12 | Missing `Tor`, absent-row-as-zero, coefficient drift, degree-zero ambiguity |
| Constructions | 10 | Hidden query-time algebra, missing map/construction dependencies |
| Comparison/identity safety | 10 | Equal Homology promoted to identity or equivalence; Model conflation |
| Provenance/editorial history | 8 | Blended evidence, overwritten correction, conflict winner, definition-as-proof |
| Boundary/adversarial | 14 | Formula evaluation beyond the bound, unsupported-input hallucination, false exhaustiveness |
| **Total** | **68** | |

The section counts total 68 because the ordered manifest deliberately exceeds
the requested minimum of 40. A machine manifest should preserve this order and
assign each row:

- one fixed input envelope and expected typed outcome;
- required and forbidden claim predicates;
- exact assertion/evidence/dependency expansion requirements;
- a single `snapshot_id` shared by the complete run;
- a mathematical verdict and a separate provenance verdict.

A row passes only if both verdicts pass. A mathematically correct group without
the selected assertion and evidence chain is `needs-evidence`, not `accept`.
Likewise, a perfectly grounded response fails if it changes
`outside_materialized_range`, `model_not_qualified`, `not_computed`, conflict,
or unsupported input into a mathematical answer.

## Implementation consequences

1. **Ticket 03:** normalize free rank, field dimension, and indexed primary
   summands; add family/formula, specialization, construction, implication,
   correction, conflict, completeness, Knowledge-revision, and Snapshot records.
2. **Ticket 04:** make cross-Model questions R05/R06 executable only after
   canonical finite-simplicial-set validation and deterministic hashing.
3. **Ticket 05:** store the actual boundary/Smith/representative/map run state;
   P04/P05 must remain `not_computed` until that state exists.
4. **Ticket 06:** pin AE-H, AE-M, AE-SC, and AE-SS artifacts exactly and record
   pinpoints. Public Q&A sources remain benchmark-design metadata only.
5. **Ticket 07:** materialize every named-family row and adopt an explicit
   bounded construction slice covering X01--X10, or version this manifest when
   selecting alternatives.
6. **Ticket 08:** implement the prospective typed outcomes and ensure every
   operation exposes Snapshot, completeness, provenance, dependency, review,
   Model, and Knowledge-role distinctions.
7. **Ticket 09:** encode all 68 rows, run them in manifest order against one
   Snapshot, expand every subject, and reject every ungrounded mathematical
   clause—not just incorrect final groups.
8. **Ticket 10:** require a clean deterministic rebuild, source/hash resolution,
   and recorded agent transcript before this benchmark can authorize external
   review.

This benchmark should grow by append-only versioning. A later UI may present
definitions as knowl dropdowns and add mathematical graphics, but neither is a
substitute for the assertion/evidence/dependency graph tested here.
