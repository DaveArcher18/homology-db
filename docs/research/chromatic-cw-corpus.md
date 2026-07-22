# A compact CW-space corpus for chromatic-facing Homology DB work

Date: 2026-07-22

Status: primary-source research recommendation; not an ingestion record, a
qualified-Model ledger, or release evidence

> **Implementation disposition (2026-07-22):** This was the first research
> recommendation, not the final catalog. A subsequent independent mathematical
> audit selected a safer 42-space gateway that keeps every Model qualified:
> it omits the two unpinned `V(1)` mapping cones, finite Thom truncations, and
> James models proposed below, and instead strengthens common-space,
> same-Homology/different-topology, Lie/Schubert, and elementary-abelian test
> coverage. The authoritative implemented selection is
> [`corpus/chromatic-v1/manifest.json`](../../corpus/chromatic-v1/manifest.json);
> this note remains the research record and source trail that informed it.

## Result

Use the **42 conceptual spaces** below as the next named corpus. It is small
enough to review one record at a time, but it has a deliberate spine:

- spheres and degree-map cofibres supply the unit, suspensions, and controlled
  `2`, `3`, `5`, and `7` primary torsion;
- finite and infinite lens/projective spaces connect those calculations to
  cyclic isotropy, classifying spaces, and complex orientations;
- `BU(n)` and the actual Thom **spaces** `MU(n) = Th(gamma_n)` expose the
  geometric input to complex cobordism without pretending that the whole `MU`
  spectrum is a space;
- three finite Thom spaces test degree shifts independently of the universal
  examples;
- two unstable four-cell `V(1)` models retain genuinely chromatic finite-CW
  examples rather than replacing every type calculation by a Moore space; and
- three James models give finite-type CW models for loop spaces of spheres.

This is a chromatic-*facing ordinary-homology* corpus, not a list of all
chromatic objects. `BP`, `E(n)`, `K(n)`, `tmf`, Brown--Gitler spectra, and the
stable Smith--Toda spectra are spectra, not spaces, so they are deliberately not
smuggled into a space table. Hopkins--Smith make finite spectra and their type
filtration structurally central to chromatic homotopy, while Ravenel constructs
`MU`, `BP`, and the Adams--Novikov machinery from Thom spectra; the two unstable
`V(1)` rows below are the honest spatial bridge to that story
([Hopkins--Smith, *Nilpotence and stable homotopy theory II*, pp. 1--49](https://annals.math.princeton.edu/articles/12974);
[Ravenel, Chapters 1 and 4](https://www.sas.rochester.edu/mth/sites/doug-ravenel/mybooks/ravenel.pdf)).

The recommendation has **40 directly reproducible cellular/bundle/quotient
models** and **two mapping-cone models whose Adams attaching maps must be pinned
as source artifacts before they can be called Model-qualified**. The latter are
good conceptual-space records immediately, but not computation evidence until
that pin exists.

## Conventions

- All Homology below is unreduced singular Homology with coefficients in
  `Z`. For a connected nonempty space, `H_0 = Z`. Every group not explicitly
  listed is zero.
- `Z/m` means the finite cyclic group of order `m`, not a coefficient ring.
- `P^d(p) = S^(d-1) cup_p e^d` is the `d`-dimensional mod-`p` Moore space, so
  its only nonzero reduced integral group is `H_(d-1) = Z/p`.
- `p_n(k)` is the number of partitions of `k` with at most `n` parts
  (equivalently, with all parts at most `n`); `p_n(0)=1`.
- `gamma_n` is the universal complex `n`-plane bundle over `BU(n)`, and
  `gamma` is the tautological complex line bundle over `CP^m`.
- A model is not qualified merely because the formula is cited. The importer
  still has to preserve an attaching-map/quotient/bundle recipe, produce a
  neutral artifact when finite, run the owned integral chain computation, and
  compare the result with the cited assertion.

The basic CW and chain formulas are all visible in Hatcher's author-hosted text:
spheres and projective cells in Examples 0.3--0.6 (pp. 5--7), cyclic Moore
spaces in Example 2.40 (pp. 143--144), `RP^n` and lens cellular differentials in
Examples 2.42--2.43 (pp. 144--146), and quaternionic projective cells after
Theorem 3.19 (p. 222)
([Hatcher, *Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf)).

## Recommended 42-instance manifest

### A. Spheres: 5 instances

**Instances:** `sphere:0`, `sphere:1`, `sphere:2`, `sphere:3`, `sphere:7`.

**Why these:** the sphere spectrum is the target of chromatic stable-homotopy
calculations; this small unstable slice also checks disconnected degree zero,
the first three attaching dimensions, and the classical `S^7` edge case.

**Model:** `S^n = D^n / boundary(D^n)`, with one `0`-cell and one `n`-cell for
`n>0`; use the two-point simplicial model for `S^0`. This is Hatcher Example
0.3, p. 5.

**Integral Homology:**

- `H_0(S^0) = Z^2` (and reduced `H_0 = Z`);
- for `n>0`, `H_i(S^n)=Z` for `i=0,n` and is zero otherwise.

The cellular differential is forced to vanish. The same source gives both the
model and the computation route.

### B. Cyclic Moore spaces: 8 instances

**Instances:**
`moore:3:1`, `moore:4:1`, `moore:5:1`, `moore:8:1`, `moore:9:1`,
`moore:2:2`, `moore:3:2`, `moore:5:2`, where `moore:m:n` denotes
`M(Z/m,n)`.

**Why these:** the family isolates torsion in a chosen degree. The slice covers
the primes `2,3,5`, the prime powers `4,8,9`, and a degree shift. Moore
cofibres are the spatial input to the mod-`p` Moore spectrum `V(0)` and its
periodic self maps; Ravenel starts the geometric Greek-letter construction from
the cofiber sequence `S^0 --p--> S^0 -> V(0)` and then constructs `V(1)` from a
`v_1` self map (Section 1.3, pp. 18--19 of the
[author edition](https://www.sas.rochester.edu/mth/sites/doug-ravenel/mybooks/ravenel.pdf)).

**Model:**
`M(Z/m,n) = S^n cup_(degree m) e^(n+1)`. It has cells in degrees `0,n,n+1`
and cellular differential `d_(n+1)=[m]`. This is exactly Hatcher Example 2.40,
pp. 143--144.

**Integral Homology:** `H_0=Z`, `H_n=Z/m`, and all other groups are zero.

Do not add `M(Z/2,1)` separately: with this model it is `RP^2`, already present
below, so a second row would violate conceptual-space deduplication.

### C. Finite real projective spaces: 4 instances

**Instances:** `real_projective:2`, `real_projective:3`,
`real_projective:4`, `real_projective:5`.

**Why these:** these are finite skeleta of `B C_2`; adjacent even/odd top
dimensions expose orientability and the truncation boundary, while every odd
interior dimension carries `2`-torsion.

**Model:** `RP^n = S^n/(x~-x)`, filtered by one cell in each degree `0..n`.
Hatcher Example 0.4 (pp. 6--7) gives the attaching maps, and Example 2.42
(p. 144) computes `d_k=2` for even `k` and `d_k=0` for odd `k`.

**Integral Homology:**

`H_i(RP^n)=Z` for `i=0` and also for `i=n` when `n` is odd;
`H_i=Z/2` for odd `i` with `0<i<n`; all remaining groups are zero.

### D. Finite complex and quaternionic projective spaces: 4 instances

**Instances:** `complex_projective:2`, `complex_projective:3`,
`complex_projective:4`, `quaternionic_projective:2`.

**Why these:** `CP^n` is the finite complex-orientation test object, and `HP^2`
adds the first quaternionic-oriented two-stage example. The three consecutive
complex dimensions catch upper-bound errors and distinguish additive Homology
from the multiplicative data a future cohomology product will need.

**Models:** `CP^n` is the quotient of `S^(2n+1)` by scalar `S^1`, with one cell
in each degree `0,2,...,2n` (Hatcher Example 0.6, pp. 6--7). `HP^n` has one
cell in each degree `0,4,...,4n` (Hatcher p. 222, immediately after Theorem
3.19). These even-only cell structures have zero cellular differentials.

**Integral Homology:**

- `H_i(CP^n)=Z` when `i=2j`, `0<=j<=n`;
- `H_i(HP^n)=Z` when `i=4j`, `0<=j<=n`.

There is no torsion. The selected `HP^2` therefore has `Z` in degrees `0,4,8`.

### E. Finite lens spaces: 3 instances

**Instances:** `lens:p=3:dim=3:weights=1`,
`lens:p=5:dim=3:weights=1`, `lens:p=3:dim=5:weights=1`.

Here `weights=1` means the diagonal scalar action; it is part of the identity,
not display metadata.

**Why these:** lens spaces are finite skeleta of `B C_p`. The two 3-dimensional
rows distinguish `3`- from `5`-primary torsion, and the 5-dimensional row tests
two torsion degrees at the same prime. Hatcher notes explicitly that lens spaces
can share integral Homology without sharing homotopy type (pp. 145--146), making
them useful guards against identity-by-Homology.

**Model:** for `r>=2`,
`L_p^(2r-1)=S^(2r-1)/C_p` under diagonal multiplication by a primitive
`p`th root of unity. It has one cell in every degree `0..2r-1`; its cellular
differentials alternate `0,p,0,p,...,0`. Hatcher Example 2.43, pp. 144--146,
constructs the quotient cells and computes those differentials.

**Integral Homology:** `H_0=H_(2r-1)=Z`,
`H_i=Z/p` for odd `i` with `0<i<2r-1`, and zero otherwise.

Thus the selected 3-spaces have `Z/p` in degree 1, while the selected 5-space
has `Z/3` in degrees 1 and 3.

### F. Cyclic classifying spaces: 3 instances

**Instances:** `classifying:cyclic:2`, `classifying:cyclic:3`,
`classifying:cyclic:5`, representing `B C_p`.

**Why these:** cyclic classifying spaces are the infinite lens spaces on which a
complex-oriented theory sees the `p`-series of its formal group law. They are
also direct inputs to chromatic calculations: Ravenel explicitly points to the
Conner--Floyd problem for `BP_*(B(Z/p)^n)` in Section 4.2 (p. 116), while his
height discussion defines the formal-group `p`-series in Section 1.4
([Ravenel](https://www.sas.rochester.edu/mth/sites/doug-ravenel/mybooks/ravenel.pdf)).

**Model:** `B C_p = S^infinity/C_p = colim_r L_p^(2r-1)`, one cell in every
nonnegative dimension, with differentials alternating `0` and `p`. It is a
finite-type CW complex, not a finite one. Hatcher Example 1B.4 (p. 88) identifies
the quotient as `K(Z/p,1)`; Example 2.43 (p. 146) gives the CW filtration and
chain complex. For `p=2`, retain `RP^infinity` as an alias, not another space.

**Integral Homology:** `H_0=Z`, `H_i=Z/p` for every positive odd `i`, and
`H_i=0` for every positive even `i`.

### G. Infinite projective orientation spaces: 2 instances

**Instances:** `complex_projective:infinity` and
`quaternionic_projective:infinity`.

**Why these:** `CP^infinity = BU(1)` is the universal complex-line and formal
group-law test object; `HP^infinity` is the analogous quaternionic-line space.
Keeping them distinct from finite truncations is essential: a family formula
must not silently turn a finite Snapshot into an infinite one.

**Models:** the colimits of the standard projective filtrations. `CP^infinity`
has one cell in each nonnegative even degree (Hatcher Example 0.6, p. 7), and
`HP^infinity` has one cell in each degree divisible by four (Hatcher p. 222).
Both are finite-type CW complexes.

**Integral Homology:**

- `H_i(CP^infinity)=Z` for every even `i>=0`, zero for odd `i`;
- `H_i(HP^infinity)=Z` for `i` divisible by four, zero otherwise.

### H. Finite-rank unitary classifying spaces: 2 instances

**Instances:** `unitary_classifying:2` and `unitary_classifying:3`, representing
`BU(2)` and `BU(3)`.

**Why these:** they are the first universal bases where more than the line-bundle
Chern class appears. They provide the bases of the next Thom-space rows and a
compact test of partition-valued ranks.

**Model:** `BU(n)=Gr_n(C^infinity)`, the colimit of complex Grassmannians with
their Schubert CW structures. Cells are indexed by partitions `lambda` with at
most `n` parts and have real dimension `2|lambda|`. Hatcher constructs these
cells in *Vector Bundles & K-Theory*, Section 1.2, pp. 31--34, and proves
`H^*(BU(n);Z)=Z[c_1,...,c_n]`, `|c_i|=2i`, in Theorem 3.9, pp. 84--85
([author PDF](https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf)).

**Integral Homology:** `H_(2k)(BU(n)) = Z^(p_n(k))` and odd Homology is zero.
There is no torsion. This follows directly from the even Schubert cells (or,
additively, from the cited polynomial cohomology and universal coefficients).

### I. The first three complex-cobordism Thom spaces: 3 instances

**Instances:** `complex_cobordism_thom:1`,
`complex_cobordism_thom:2`, `complex_cobordism_thom:3`, representing the
spaces `MU(1)`, `MU(2)`, and `MU(3)`, not the spectrum named `MU`.

**Why these:** these are the actual spaces assembled into the complex cobordism
spectrum that underlies the Adams--Novikov spectral sequence and chromatic
height. Ravenel defines `MU(n)=Th(gamma_n)` and the structure maps
`Sigma^2 MU(n)->MU(n+1)` in Chapter 4, Section 1, p. 103
([author PDF](https://www.sas.rochester.edu/mth/sites/doug-ravenel/mybooks/ravenel.pdf)).

**Model:** `MU(n)=D(gamma_n)/S(gamma_n)` over the Schubert CW model of
`BU(n)`. It is a finite-type based CW complex whose non-basepoint cells are the
Schubert cells shifted upward by the real bundle rank `2n`. Hatcher defines Thom
spaces and proves the integral Thom isomorphism for oriented bundles in
Corollary 4D.9 and Theorem 4D.10, pp. 441--443
([*Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf)).

**Integral Homology:** `H_0=Z` and
`reduced H_(2n+2k)(MU(n)) = Z^(p_n(k))` for `k>=0`; all other reduced groups
are zero. Complex bundles are canonically oriented as real bundles, so there is
no integral Thom twist and no torsion.

### J. Finite Thom-space truncations: 3 instances

**Instances:** `thom_cp:k=2:m=2`, `thom_cp:k=3:m=3`,
`thom_cp:k=4:m=4`, representing `Th(k gamma -> CP^m)`.

**Why these:** they are finite, exact checks of the Thom degree shift used by
`MU(n)`. They also give compact Atiyah--Hirzebruch and orientation fixtures
without adding another invariant to the database.

**Model:** the quotient `D(gamma^oplus k)/S(gamma^oplus k)` over the standard
finite CW model of `CP^m`. Filter by the projective skeleta; the Thom cells occur
in dimensions `2k,2k+2,...,2k+2m`. The quotient definition is Hatcher,
*Vector Bundles & K-Theory*, Section 4.1, pp. 112--113, and the cell degrees and
Homology follow from the projective cells plus the integral Thom isomorphism
cited above.

**Integral Homology:** `H_0=Z` and
`reduced H_(2k+2j)=Z` for `0<=j<=m`; every other reduced group is zero.
There is no torsion.

### K. Unstable `V(1)` four-cell spaces: 2 instances

**Instances:** `unstable_v1:p=5:N=14` and
`unstable_v1:p=7:N=18`.

**Why these:** Moore spaces see chromatic type 1; the cofiber of an Adams
`v_1` map is the first type-2 Smith--Toda construction. These two rows keep that
chromatic transition visible while remaining spaces rather than finite spectra.
Ravenel's stable construction is the cofiber
`Sigma^(2p-2)V(0) --v_1--> V(0) -> V(1)` for odd `p` (Section 1.3,
pp. 18--19). Shiina works with its unstable Moore-space model and explicitly
defines `V^N` as the mapping cone of an Adams map
`A:P^(N-1)(p)->P^(N-2p+1)(p)`
([Shiina, Introduction and Section 2, pp. 169--172](https://intlpress.com/site/pub/files/_fulltext/journals/hha/2006/0008/0001/HHA-2006-0008-0001-f001.pdf)).

**Model:** `V_p^N = Cof(A:P^(N-1)(p)->P^(N-2p+1)(p))`. It has cells in
degrees `N-2p`, `N-2p+1`, `N-1`, and `N` (plus the basepoint). Shiina states
that the unstable Adams map exists when the target Moore dimension is greater
than 3; both selected pairs have target `N-2p+1=5`.

**Integral Homology:** the map connects Moore groups in disjoint degrees, so
the cofiber long exact sequence gives
`H_0=Z`, `reduced H_(N-2p)=Z/p`, and
`reduced H_(N-1)=Z/p`, with all other reduced groups zero. Thus:

- `V_5^14` has `Z/5` in degrees 4 and 13;
- `V_7^18` has `Z/7` in degrees 4 and 17.

**Qualification hold:** Shiina works in the `p`-local category. Before either
row supplies database computation evidence, pin a concrete integral
representative of `A`, its convention, and the neutral four-cell attaching data;
then recompute the integral cellular boundary. Until then the cited formula is a
literature assertion and the conceptual-space row is useful, but `Model status`
must remain unqualified.

### L. James models for loop spaces of spheres: 3 instances

**Instances:** `loop_sphere:2`, `loop_sphere:3`, `loop_sphere:4`, represented
by `Omega S^2`, `Omega S^3`, and `Omega S^4`.

**Why these:** loop spaces of spheres are basic unstable inputs to periodic
families, EHP methods, and power operations. They also ensure that “finite type”
is implemented honestly rather than confused with “finite dimensional.”

**Model:** use the James reduced product `J(S^n)`, words in `S^n` with the
basepoint deleted, filtered by word length. It is a CW complex with one cell in
each degree `kn`, `k>=0`, and `J(S^n)->Omega S^(n+1)` is a weak homotopy
equivalence. Hatcher constructs the CW model in Section 3.2, pp. 223--224,
computes its Homology in Proposition 3C.8, pp. 288--289, and gives the loop-space
equivalence in Theorem 4J.1, pp. 470--473. The original source is
[I. M. James, “Reduced product spaces,” *Annals of Mathematics* 62 (1955), 170--197](https://www.mathnet.ru/eng/mat15).

**Integral Homology:** for `n>=1`,
`H_*(Omega S^(n+1);Z) = T_Z(x_n)` as a Pontryagin algebra. Additively this is
`H_(kn)=Z` for every `k>=0` and zero in all other degrees. There is no torsion.

## Count and coverage audit

| Block | Count | Finite / finite-type | Torsion contribution |
|---|---:|---|---|
| Spheres | 5 | finite | none |
| Moore spaces | 8 | finite | `2,3,4,5,8,9`; degrees 1 and 2 |
| Finite `RP` | 4 | finite | `Z/2` in odd interior degrees |
| Finite `CP`/`HP` | 4 | finite | none |
| Finite lens | 3 | finite | `Z/3`, `Z/5`; one or two odd degrees |
| `B C_p` | 3 | finite type | `Z/p` in every positive odd degree |
| `CP^infinity`, `HP^infinity` | 2 | finite type | none |
| `BU(2)`, `BU(3)` | 2 | finite type | none |
| `MU(1)`, `MU(2)`, `MU(3)` | 3 | finite type | none |
| Finite Thom truncations | 3 | finite | none |
| Unstable `V(1)` | 2 | finite construction; attaching-map pin held | `Z/5` or `Z/7` in two separated degrees |
| James loop models | 3 | finite type | none |
| **Total** | **42** | **29 finite, 13 finite-type** | **2-, 3-, 5-, and 7-primary; prime powers and shifted degrees** |

The “29 finite” total counts the two four-cell `V(1)` constructions as finite
conceptual models while preserving their qualification hold. If “ready to emit a
neutral artifact today” is the count, it is 27 finite plus 13 finite-type, with
two held models.

## Computation sketches and ingestion rules

1. **Direct cellular Smith normal form:** spheres, Moore, `RP`, and lens rows.
   Store the integer boundary (`m`, alternating `0/2`, or alternating `0/p`)
   rather than just the answer. This is the strongest torsion fixture in the set.
2. **Even-cell zero differential:** `CP`, `HP`, and complex Grassmann rows.
   Generate cells from the stated index set, do not create zero assertions merely
   from a missing cell row, and record the completeness range.
3. **Thom shift:** derive a separate assertion from the qualified base plus a
   pinned oriented-bundle/Thom dependency. A cited Thom theorem is not a chain
   computation, and `MU(n)` must not be conflated with the `MU` spectrum.
4. **Mapping-cone long exact sequence:** use it as literature-level support for
   the two `V(1)` formulas, but require an actual Adams-map artifact before an
   owned computation can be promoted.
5. **Filtered colimit / finite type:** `B C_p`, infinite projective, `BU`, `MU`,
   and James rows need a parameterized answer contract. A query for degree `i`
   must name a finite skeleton/filtration stage that already contains the relevant
   chain groups; “infinite formula” is not a finite Model.
6. **Identity safety:** select aliases `RP^infinity = B C_2` and
   `CP^infinity = BU(1)` explicitly. Do not duplicate them. Do not identify lens
   spaces, wedges of Moore spaces, or `V(1)` spaces merely because their integral
   Homology agrees in selected degrees.

## Source ledger

| Key | Primary/author-owned source | Locators used here |
|---|---|---|
| H-AT | [Allen Hatcher, *Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf) | Examples 0.3--0.6, pp. 5--7; Example 1B.4, p. 88; Examples 2.40, 2.42, 2.43, pp. 143--146; Theorem 3.19 and following paragraph, pp. 221--222; Proposition 3C.8, pp. 288--289; Thom isomorphism, pp. 441--443; Theorem 4J.1, pp. 470--473 |
| H-VB | [Allen Hatcher, *Vector Bundles & K-Theory*](https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf) | complex Grassmann CW structures, Section 1.2, pp. 31--34; Theorem 3.9, pp. 84--85; Thom spaces, pp. 112--113 |
| R-CSH | [Douglas Ravenel, *Complex Cobordism and Stable Homotopy Groups of Spheres*](https://www.sas.rochester.edu/mth/sites/doug-ravenel/mybooks/ravenel.pdf) | Moore/`V(1)` cofibres, Section 1.3, pp. 18--19; formal-group height, Section 1.4; `MU(n)` and `MU`, Chapter 4, Section 1, pp. 103--104; `BP_*(B(Z/p)^n)` context, p. 116 |
| HS | [Michael Hopkins and Jeffrey H. Smith, “Nilpotence and stable homotopy theory II”](https://annals.math.princeton.edu/articles/12974) | *Annals of Mathematics* 148 (1998), 1--49; finite-spectrum type/periodicity context |
| S-V1 | [Takahisa Shiina, “Unstable splitting of `V(1) smash V(1)` and its applications”](https://intlpress.com/site/pub/files/_fulltext/journals/hha/2006/0008/0001/HHA-2006-0008-0001-f001.pdf) | *Homology, Homotopy and Applications* 8 (2006), 169--186; definition and existence range on pp. 169--172 |
| J-RP | [I. M. James, “Reduced product spaces”](https://www.mathnet.ru/eng/mat15) | *Annals of Mathematics* 62 (1955), 170--197; reduced-product/loop-space model, cross-checked against H-AT |

## Recommended first implementation cut

Keep the public corpus at all 42 conceptual identities, but stage Model evidence
in this order:

1. direct finite CW rows (spheres, Moore, finite projective, finite lens);
2. the three finite Thom bundles;
3. filtration-backed finite-type rows (`B C_p`, projective infinity, `BU`, `MU`,
   James), with explicit degree/skeleton bounds; and
4. the two `V(1)` rows only after the Adams maps are pinned and independently
   checked.

That order delivers torsion and a substantially more chromatic product early,
without presenting literature formulas as though the database had already run
the relevant Model.
