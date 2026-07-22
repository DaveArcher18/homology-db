# Chromatic gateway 42 corpus contract

Status: implemented development corpus; not externally reviewed release evidence

Machine source: [`corpus/chromatic-v1/manifest.json`](../../corpus/chromatic-v1/manifest.json)

Public read model: `homology-db.static-atlas/2`

## Purpose and boundary

This Snapshot is a compact ordinary-Homology atlas of spaces that are either
standard topology examples or geometric inputs to chromatic homotopy theory.
It contains 42 named CW spaces in 17 families: 32 finite CW complexes and 10
infinite finite-type CW complexes. Twenty-one spaces have integral torsion.

The word “chromatic” records why the examples are useful; ordinary Homology
does not determine chromatic type. Spectra such as `BP`, `E(n)`, `K(n)`, `tmf`,
the sphere spectrum, and stable Smith--Toda complexes are not entered as
ordinary spaces. Moore spaces are recorded as unstable CW cofibers; their
suspension spectra provide the connection to `V(0)`.

## Identity and evidence rules

- A cellular boundary matrix is a computation certificate, not a complete CW
  Model. Quotient constructions, attaching maps, Schubert recipes, product
  recipes, or a pinned triangulation remain attached to every record.
- Exact Homology rows cite one evidence record. That record identifies its
  Model, computation sketch, sources, and an optional local computation run.
  No run is synthesized when the result is citation-backed.
- Finite CW records are complete and assert zero above their dimension.
  Infinite finite-type records are materialized through degree 24 and make no
  assertion above that degree.
- Parameters such as `m`, `n`, `p`, rank, and lens weights are concrete parts
  of identity and computation, never display-only notation.

## Selected spaces and calculations

| Family | Instances | Count | Model and integral-Homology calculation |
|---|---|---:|---|
| Point | `*` | 1 | One 0-cell; `H_0=Z`. |
| Spheres | `S^0` through `S^4` | 5 | Standard two-cell CW models (two points for `S^0`); free classes in degrees 0 and `n`. |
| Homology sphere | Poincare homology 3-sphere | 1 | Pinned Sage 16-vertex, 90-facet triangulation; cited `H_0=H_3=Z`. |
| Wedge | `S^2 v S^4` | 1 | Basepoints identified; free classes in degrees 0, 2, and 4. |
| Surfaces | `T^2`, Klein bottle | 2 | One 2-cell attached by `[a,b]` or `aba^-1b`; the latter has `d_2(1)=2b` and `H_1=Z + Z/2`. |
| Real projective | `RP^2`, `RP^3`, `RP^4` | 3 | One cell in each degree with `d_k=2` for positive even `k` and zero for odd `k`. |
| Hopf projective planes | `CP^2`, `HP^2`, `OP^2` | 3 | Top cells attach by `eta`, `nu`, and `sigma`; cellular differentials vanish but attaching maps remain part of the Models. |
| Moore | `M(Z/3,1)`, `M(Z/4,1)`, `M(Z/5,2)`, `M(Z/9,2)`, `M(Z/7,3)`, `M(Z/8,4)` | 6 | `C_(n+1) --m--> C_n`; reduced `H_n=Z/m`. |
| Lens | `L^3(3;1,1)`, `L^3(5;1,1)`, `L^3(5;1,2)`, `L^5(3;1,1,1)` | 4 | Weighted free `C_p` sphere quotients; one cell per degree, `d_even=p`, `d_odd=0`. |
| Stunted projective | `RP^6/RP^2`, `CP^4/CP^1` | 2 | Relative projective CW chains; the real example has `Z/2` in degrees 3 and 5, while the complex example is free in degrees 4, 6, and 8. |
| Compact Lie | `SU(3)`, `Sp(2)` | 2 | Cited cells in degrees `0,3,5,8` and `0,3,7,10`; the lower attachments retain `eta` and a generator of `pi_6(S^3)=Z/12`. |
| Schubert | `Fl_3(C)`, `Gr_2(C^4)` | 2 | Even Schubert cells with ranks `1,2,2,1` and `1,1,2,1,1`; zero cellular differentials. |
| Cyclic classifying | `BC_2`, `BC_3`, `BC_5` | 3 | Infinite lens-space CW model; alternating `0/p` chain, materialized through degree 24. |
| Elementary-abelian classifying | `B(C_2^2)`, `B(C_3^2)`, `B(C_2^3)` | 3 | Product CW model with signed tensor differential, materialized through degree 24. |
| Infinite projective | `CP^infinity`, `HP^infinity` | 2 | One cell in degrees `2k` or `4k`; zero differentials, materialized through degree 24. |
| Unitary classifying | `BU(2)` | 1 | Infinite Grassmannian Schubert model; `rank H_(2k)=floor(k/2)+1` through degree 24. |
| Universal Thom | `Th(gamma_2 -> BU(2))` (the space convention for `MU(2)`) | 1 | Thom cells shift the `BU(2)` Schubert cells by real degree 4; materialized through degree 24. |

The Poincare artifact is
[`poincare-sphere-facets.json`](../../corpus/chromatic-v1/poincare-sphere-facets.json).
The builder verifies its 16 vertices, 90 facets, and f-vector
`(16,106,180,90)` before admitting the record.

## Parameterized formulas

For a cyclic Moore space,

```text
M(Z/m,n) = Cofib(S^n --degree m--> S^n),
H_i(M;Z) = Z       i=0,
             Z/m     i=n,
             0       otherwise.
```

For a `(2r-1)`-dimensional weighted lens space with prime `p`, the preferred
cellular chain has one generator in every degree, multiplication by `p` in
positive even degrees, and zero in odd degrees. Thus `H_(2j-1)=Z/p` below the
top degree and `H_(2r-1)=Z`.

For `B(C_p^r)`, the product CW chain has

```text
rank C_n = binomial(n+r-1, r-1),
a_0 = 0,
a_n = rank C_n - a_(n-1),
H_n(B(C_p^r);Z) = (Z/p)^(a_n) for n>0.
```

The builder materializes the signed tensor-product differential through degree
25 so the incoming differential needed for degree 24 is present and `d^2=0`
is checked sparsely.

Field Homology is derived from exact integral rows with the Universal
Coefficient Theorem:

```text
dim H_n(X;F_p)
  = rank H_n(X;Z)
  + number of p-divisible cyclic factors in H_n(X;Z)
  + number of p-divisible cyclic factors in H_(n-1)(X;Z).
```

Consequently `M(Z/9,2)` has one mod-3 class in each of degrees 2 and 3, and
the Klein bottle has mod-2 dimensions `1,2,1` in degrees `0,1,2`.

## Deliberate identity guards

- `CP^2` and `S^2 v S^4` have identical ordinary cellular chain groups and
  Homology, but the former retains the Hopf attaching map `eta`.
- The Poincare homology sphere and `S^3` have identical integral Homology, but
  the former retains its actual triangulation and nontrivial fundamental group.
- `L^3(5;1,1)` and `L^3(5;1,2)` have identical cellular Homology but distinct
  weight data and are not collapsed into one Conceptual-space identity.

## Primary sources

- Allen Hatcher, [*Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf): CW, Moore, projective, lens, Hopf, and Thom calculations, with pinpoints in the manifest.
- Allen Hatcher, [*Vector Bundles and K-Theory*](https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf): Schubert, `BU(n)`, and bundle/Thom models.
- Alexander Postnikov, [*Enumeration in Algebra and Geometry*](https://math.mit.edu/~apost/papers/thesis.pdf), Section 2.2.1: complete-flag Schubert cells indexed by permutations.
- SageMath, [pinned Poincare-sphere source](https://github.com/sagemath/sage/blob/686dc1a8d420c2e0aabadd4f602d9a0aa4690c50/src/sage/topology/simplicial_complex_examples.py#L610-L653).
- Walker and Wood, [low-codimensional embeddings of `Sp(n)` and `SU(n)`](https://doi.org/10.1017/S0013091500022082), and Fernandez-Suarez et al., [`Sp(3)` category paper](https://arxiv.org/abs/math/0111263): low-rank Lie-group cells.
- Hopkins--Kuhn--Ravenel, [generalized group characters](https://people.math.rochester.edu/faculty/doug/mypapers/hkr.pdf): chromatic role of finite-group classifying spaces and complex-oriented theories.
- Douglas Ravenel, [*Complex Cobordism and Stable Homotopy Groups of Spheres*](https://www.sas.rochester.edu/mth/sites/doug-ravenel/mybooks/ravenel.pdf): Moore/`V(0)` and `MU(n)` context.

Exact source roles and page/section locators are data in the machine manifest
and are exported beside each space; this prose list is not a substitute for
those records.
