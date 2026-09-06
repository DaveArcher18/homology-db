# Classical core: mathematical source qualification

Qualified by `/root/math_review` on 2026-09-06 against Allen Hatcher's
author-hosted [Algebraic Topology](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf).
This is agent source qualification, not human mathematical acceptance.
All page numbers below are printed pages; a PDF `#page` fragment is printed
page plus 9 in the checked 560-page edition.

## Primary source locators

| Locator | Purpose |
| --- | --- |
| [Proposition 2.8, p. 110](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=119) | Point homology. |
| [Corollary 2.14, p. 114](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=123) | Sphere homology. |
| [Example 2.37, p. 141](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=150) | Nonorientable-surface cellular differential. |
| [Example 2.42, p. 144](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=153) | Real-projective cellular differential. |
| [Section 3.1, p. 198](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=207) | Universal coefficients; degree zero as functions on components. |
| [Theorem 3.5, p. 203](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=212) | Cellular cochains compute cohomology. |
| [Section 3.2, p. 207](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=216) | Cup-product grading and unit. |
| [Examples 3.7–3.8, pp. 207–208](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=216) | Orientable/nonorientable surface products. |
| [Theorem 3.11, p. 210](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=219) | Graded commutativity. |
| [Examples 3.12–3.14, pp. 213–214](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=222) | Projective coefficients, exterior algebra, disjoint unions, wedges. |
| [Theorem 3.15; Example 3.16, p. 216](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=225) | Ring Künneth formula and products of spheres. |
| [Theorem 3.19, p. 220](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=229) | Projective-space ring presentations. |
| [Section 1.2, pp. 51–52](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=60) | Klein bottle equals the genus-two nonorientable surface. |
| [Corollary 3A.6(a), p. 266](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=275) | Rational homology dimension equals integral free rank. |

## Qualified presentations and normalization

Here `k` is any one of Q, F2, F3, F5, F7, and every ring is ordinary
**unreduced, graded, unital** cohomology. Scalars are in degree zero.
Products obey `uv = (-1)^(|u||v|) vu`. The structured record must express
ordered multiplication or an explicit graded-commutative convention; an ordinary
commutative polynomial quotient is not suitable notation for the odd-field torus.

| Space | Ring; generator degrees | Nonzero dimensions of H^d(-;k) |
| --- | --- | --- |
| Point | `k` | d=0: 1 |
| S0 | `k[e]/(e²-e)`, degree(e)=0 | d=0: 2 |
| S1, S2, S3, S4 | `k[x]/(x²)`, degree(x)=1,2,3,4 respectively | d=0,n: 1 |
| T2 | Exterior algebra on a,b, both degree 1 | d=0,1,2: 1,2,1 |
| Klein bottle, k=F2 | `F2[a,b]/(ab,a²+b²,a³,b³)`, both degree 1 | d=0,1,2: 1,2,1 |
| Klein bottle, k=Q,F3,F5,F7 | `k[a]/(a²)`, degree(a)=1 | d=0,1: 1,1 |
| RPn, n=2,3,4, k=F2 | `F2[t]/(t^(n+1))`, degree(t)=1 | Each d=0,...,n: 1 |
| RP2, RP4, k=Q,F3,F5,F7 | `k` | d=0: 1 |
| RP3, k=Q,F3,F5,F7 | `k[v]/(v²)`, degree(v)=3 | d=0,3: 1,1 |
| CP2 | `k[u]/(u³)`, degree(u)=2 | d=0,2,4: 1,1,1 |
| S2 wedge S4 | `k[a,b]/(a²,ab,b²)`, degree(a)=2, degree(b)=4 | d=0,2,4: 1,1,1 |

Omitted degrees in this table are mathematical zero, justified by these complete
finite presentations. This does not authorize converting absent records on
other spaces or coefficients into zero.

The following are our explicit normalizations and deductions from the cited
results, recorded separately from source statements:

- For S0 use the basis `1,e`, with `1=(1,1)` and `e=(1,0)` in `k×k`.
  The second component indicator is `1-e`; its square equals itself and
  `e(1-e)=0`, including characteristic 2. Degree-zero cohomology is not a
  two-dimensional square-zero algebra.
- For positive-dimensional spheres, additive support and cup-product grading
  force `x²=0`. The generator is the dual of an oriented top homology class;
  a choice of its sign does not affect this presentation.
- For the torus choose an ordered pair of circle-factor generators, and put
  `w=ab`. Then `ba=-w`, `a²=b²=0`, and all other positive products vanish.
  In F2, `ba=w`; zero squares are still explicit, since a sign rule alone
  cannot force them in characteristic 2.
- For the Klein bottle in F2 use Hatcher's **crosscap basis** dual to the
  two edges of the `a1² a2²` polygon, not the usual rectangle-edge basis.
  Put `w=a²=b²`; `w` is nonzero and `ab=ba=0`. Products of `w` with positive
  classes vanish. A square-zero nonzero degree-one class also exists: `a+b`.
- For the Klein bottle when 2 is invertible, the cochain differential
  `k² -> k` is `(r,s) -> 2(r+s)`. It is onto, its kernel has dimension one,
  and H² is zero. Thus the only positive generator has degree one and
  its square vanishes. The algebra claim is a cellular/support deduction,
  not an assertion that Example 3.8 covers odd coefficients.
- For RPn with 2 invertible, dualizing the alternating `0,2` cellular
  differential gives only H⁰, plus Hⁿ when n is odd. This yields the
  RP2/RP4 scalar ring and RP3 sphere-shaped ring. The source does not claim
  a polynomial degree-one generator over odd fields.
- For CP2 the cohomology generator `u` is degree two and `u²` is a nonzero
  degree-four generator over each requested field. Example 3.12 explicitly
  extends the complex-projective coefficient ring to any commutative ring.
- For the wedge, restriction to its two sphere summands gives generators
  `a,b`. Their cross product vanishes; `a²` vanishes in the sphere summand
  as well. Add the single ordinary degree-zero unit to the reduced wedge
  product from Example 3.14. It follows that CP2 and this wedge have the
  same additive groups but different graded cohomology rings over every
  requested field.

No integral cohomology-ring records are required for this iteration. No formula
gap remains in the 65 requested field/space combinations. Human review remains
pending, and automated algebra consistency checks are not proofs that a
presentation belongs to the named space.

## Rational homology export qualification

The new Q homology rows can be derived from the existing integral rows by
`dimension = free_rank`. Hatcher Corollary 3A.6(a), p. 266, states the needed
rationalization directly. All 13 spaces have finite CW models, so finite
generation holds degree by degree. The same calculation applies to reduced
homology. Preserve the source integral assertion ID, its evidence, and coverage;
label the new row as derived by rational extension of scalars rather than as an
old stored Q assertion. This adds no new cup-product evidence and does not
change the legacy homology database or its snapshot identity.

## Independent review checklist

Check the implemented records against the table above, verify the coefficient
and basis conventions appear in exported content, and independently compare
field dimensions against existing homology. Specifically exercise S0 idempotents,
torus odd signs, Klein diagonal products, all RP parity changes, and the CP2/wedge
square distinction. Inspect every record's source locator and review status.
