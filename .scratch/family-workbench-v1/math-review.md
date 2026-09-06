# Independent family mathematics review

Reviewer: `/root/family_math_review` (agent), 2026-09-06.
State: source qualification and exact evaluator/metadata audit passed.
Human review remains pending. Gabriel's screenshot is product feedback, not
mathematical acceptance.

## Source evidence

Read Allen Hatcher's author-hosted [Algebraic Topology](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf)
using the web PDF text extractor on 2026-09-06. The checked file has 560 pages;
printed page p corresponds to the one-based PDF fragment p+9. This uses the
Gather fallback for PDF sources; no new source adapter was implemented.

- [Example 2.42, p.144](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=153): RP cellular boundaries alternate zero (odd degree) and multiplication by two (even degree).
- [Corollary 2.14, p.114](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=123): sphere reduced homology.
- [Theorem 3.5, p.203](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=212): cellular cohomology.
- [Examples 3.12–3.14, p.213](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=222): CP coefficient extension, exterior algebra, and componentwise products for disjoint unions.
- [Theorem 3.19, p.220](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=229): RP mod-two and CP integral polynomial presentations.
- [Section 3.E / Example 3E.1, pp.303–304](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=312): coefficient exact sequence and reduction/Bockstein relationship.
- [Corollary 3E.4, p.306](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=315): reduction is injective on p-torsion when no p-squared torsion exists.

## Qualified formulas and explicit deductions

Let R be Z, Q, F2, F3, F5, F7, or F11. All rings below are ordinary,
unreduced, graded and unital. Negative degrees and degrees above real dimension
are zero. n is a finite nonnegative integer.

**Spheres.** For n>0, both theories are R in degrees 0 and n and zero elsewhere;
the ring is R[x]/(x²), |x|=n. For n=0, both degree-zero groups are R², and the
ring is R[e]/(e²-e), |e|=0. The unit is (1,1), e=(1,0). Thus e is idempotent,
not square-zero. Reduced homology deletes one degree-zero scalar summand only.

**Complex projective spaces.** Both theories are R in each even degree 0..2n
and zero elsewhere. The ring is R[u]/(u^(n+1)), |u|=2. The additive generators
are 1,u,...,u^n; u^i u^j=u^(i+j) if i+j<=n, and zero otherwise. CP0 is a point.

**Real projective spaces over Z.** H_d is Z for d=0 and for d=n odd; Z/2 for
positive odd d<n; zero otherwise. H^d is Z for d=0 and for d=n odd; Z/2 for
positive even d<=n; zero otherwise. These statements follow by taking homology
and cohomology of the sourced alternating cellular complex.

For n=2m, the integral ring is Z[a]/(2a,a^(m+1)), |a|=2.
For n=2m+1, it is Z[a,v]/(2a,a^(m+1),av,v²), |a|=2 and |v|=n.
The positive powers a^j have additive order two; the odd top class v is free.
This notation specializes correctly to n=1 with a=0, and n=0 is simply Z.

The integral RP product claim is a deduction, **not** a direct quotation of
Theorem 3.19: coefficient reduction is injective in positive even degrees
because those groups have only order-two torsion. The nonzero degree-two class
a reduces to t² in the mod-two polynomial ring; therefore a^j reduces to
t^(2j) and is nonzero exactly while 2j<=n. Products involving the positive
odd top class vanish by dimension. This proves the indicated additive
generators, products and truncation without extrapolating finite examples.

**Real projective spaces over fields.** Over F2, both theories have dimension
one in every degree 0..n, with ring F2[t]/(t^(n+1)), |t|=1. When 2 is invertible
(Q or any requested odd field), the alternating cellular maps are isomorphisms
or zero: both theories have only the degree-zero scalar and, when n is odd,
one top class. The ring is the scalar field for even n and k[v]/(v²), |v|=n,
for odd n. RP0 is a point, unlike S0.

## Candidate audit obligations

- Independently compute RP ranks/torsion from adjacent cellular maps rather
  than merely repeating engine conditionals; compare all coefficients and
  dimensions including 0,1,2,3,4,5,12,13 and much larger values.
- Exercise all products of small presentations, especially S0 unit/idempotent,
  integral RP4 a², integral RP5 a² and free v, field RP odd/even, CP truncation.
- Ensure a limited degree/generator window is not reported as limited
  mathematical coverage, nor does a complete rule become human-reviewed.
- Check integer-size limits are explicit. A symbolic all-finite-n theorem
  must not license unsafe JavaScript rounding at large numeric parameters.
- Bind final audit to exact engine and review metadata hashes.

## Exact candidate audit

Audited `static_atlas/families.js` at SHA-256
`3cfea39d6e1cfb1a4ff744d292ef977f58e0daee1cb53e9102bb9c7c1f3bdc32`
and `homology_db/families.py` at SHA-256
`8089e10048c9647f95d8992f734c1144b8ee834506ed1b4afadc88ca663fcf18`.
No remaining mathematical blocker in those exact files.

Two presentation/source findings were corrected before these hashes: integral
RP multiplication prose now excludes the unit from order-two powers and handles
n=0/1 without nonexistent a generators; CP provenance includes the explicit
coefficient-extension locator Example 3.12 p.213.

Executed `python3 -m unittest tests.test_family_math_review -v`: 3 tests passed.
The independent oracle takes kernels/images of adjacent cellular maps for
RP dimensions 0..29 over all seven coefficient rings (including transpose for
cohomology), checks every small-family product and additive order, and exercises
exact 101-digit dimensions on both parity branches around the top degree.
The evaluator uses BigInt for all unbounded parameters and rejects unsafe
numeric Number inputs. Both group and generator windows remain bounded.

A separate read-only comparison against the prior committed `dist/atlas.html`
matched all 192 unreduced homology rows for finite sphere/RP/CP instances,
including existing Z and field rows. Infinite projective instances were excluded
because this cycle only claims finite-n rules. The first comparison attempt
included infinity and was correctly rejected by parameter validation; the
correctly scoped finite comparison passed.

This audit qualifies mathematical engine and source metadata, not final browser
rendering, exporter integration, deployment, or human acceptance. Root must verify
the rendered multiplication/coverage/review distinctions on the release artifact.

## Independent UI mathematical presentation audit

Static/pure-render audit passed after corrections. Exact checked hashes:

- `static_atlas/workbench.js`: `522c8becfa5a41f12dba24748ed7f66e3ed750073aa8cfcd82fe2182efe69897`
- `static_atlas/atlas.js`: `70ecd5c3caa533aa7c9bc026cf5dc824dcfdd1a898dfea9d4ff0bec60edbcef1`
- `static_atlas/presentation.js`: `6e5d2586b4c302a714c75f21bc8854a67c800278e1b5e1eee723dac230a178df`
- Updated evaluator `static_atlas/families.js`: `94221f36302da2132fbab8e7f1663b3c884337670650dedfcd19ea7018b2cd61`
- Metadata `homology_db/families.py` remains `8089e10048c9647f95d8992f734c1144b8ee834506ed1b4afadc88ca663fcf18`.

The prior evaluator hash is superseded only by a rendering repair: literal
less-than signs in the two integral RP group formulas became the supported
`\\lt` command. The original strings were rejected by the safety-conscious
TeX parser and appeared as raw fallback text; the repaired command is emitted
as a text node, without weakening rejection of literal HTML characters.

The workbench also now renders its source derivation, labels all-degree formulas
explicitly unreduced, and distinguishes exported unreduced results from a reduced
display through explicit convention fields. The glossary's field definition now
excludes the zero ring. No remaining mathematical presentation blocker was found.

Pure Node enumeration parsed 3,087 formula/group expressions and all 24 glossary
symbol/example expressions successfully. Added a durable fourth independent test
covering rendered family formulas, glossary expressions, and HTML rejection;
`python3 -m unittest tests.test_family_math_review -v` passes all four tests.

Static inspection confirms reduced display changes only degree-zero homology;
cohomology ring/data stay unreduced. Legacy multiplication uses explicit products
and unit identity, permits omitted zero only under a complete-zero contract, and
otherwise displays Not recorded. New cropped tables distinguish display limits
from complete mathematical rules. Human review is separately read from the
exact-rule catalog and is not inferred from completeness or provenance. This
does not replace the separately assigned visual/keyboard browser verification.
Final workbench hash additionally opens the all-degree rule disclosure by default;
this presentation-only follow-up preserves the audited mathematical content.
