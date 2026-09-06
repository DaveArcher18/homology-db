# Selected textbook coverage and next collection

Prepared by the coverage/content agent on 2026-09-06 for F-01. This is a
selected teaching trail through the **42 retained spaces**, not an inventory of
all examples in Hatcher and not evidence of human mathematical acceptance.
Machine-readable introductions, locators, and three guided comparisons are in
`homology_db/teaching.py`; tests require exactly the retained 42 identities.

## What the current inventory means

There are 32 finite and 10 infinite finite-type entries. The original 13-space
five-field ring core retains its identity; nine of those entries redirect into
the general sphere/RP/CP workbench. Two existing projective-plane entries receive
the selected extension described below. The other 27 entries do not acquire ring
records from their inclusion in the teaching map. All infinite entries retain
degree-24 homology bounds; source-known general theorems do not silently enlarge
those stored tables. Family rules and finite classical records remain separate.

| Selected topic and exact retained instances | Count | Source trail and next step |
| --- | ---: | --- |
| Point; S⁰, S¹, S², S³, S⁴ | 6 | Hatcher Cor. 2.14 p.114 and Prop.2.8 p.110; original core, spheres generalize in workbench. |
| Poincaré homology three-sphere | 1 | Supplement: official SageMath PoincareHomologyThreeSphere documentation. Homology retained; ring deferred. |
| S² ∨ S⁴ | 1 | Hatcher Ex.3.14 pp.213–214; original core, compare with CP². |
| T²; Klein bottle | 2 | Ex.2.36–2.37 p.141, Ex.3.7–3.8 pp.207–208; original core. |
| RP², RP³, RP⁴ | 3 | Ex.2.42 p.144, Thm.3.19 p.220; original core and general-family rule. |
| CP², HP², OP² | 3 | pp.220–222 and §4.B p.427; CP² original core, HP²/OP² selected extension. |
| M(Z/3,1), M(Z/4,1), M(Z/5,2), M(Z/7,3), M(Z/8,4), M(Z/9,2) | 6 | Ex.2.40 pp.143–144; retain torsion tests, defer rings. |
| L³(3;1,1), L³(5;1,1), L³(5;1,2), L⁵(3;1,1,1) | 4 | Ex.2.43 pp.144–146; weights remain distinct, rings deferred. |
| CP⁴/CP¹; RP⁶/RP² | 2 | CW quotients p.8 and relative cellular theory pp.138–139, using projective skeleta; rings deferred. |
| SU(3); Sp(2) | 2 | Cor.4D.3 p.434; source-known exterior algebras are a possible later finite collection, not encoded now. |
| Fl₃(C); Gr₂(C⁴) | 2 | Supplements: Postnikov §2.2.1 pp.53–54; Hatcher VBKT §1.2 pp.31–34. Schubert multiplication normalization deferred. |
| BC₂, BC₃, BC₅ | 3 | Ex.1B.3–1B.4 p.88; infinite, homology through24 only; ring encoding deferred. |
| B(C₂²), B(C₂³), B(C₃²) | 3 | Ex.1B.5 p.88 and §3.B; infinite, homology through24 only; integral product/Tor encoding deferred. |
| CP∞; HP∞ | 2 | Thm.3.19 pp.220–222; source-known infinite polynomial rings not yet encoded on these entries. |
| BU(2) | 1 | Hatcher VBKT §1.2 pp.27–34 and Thm.3.9 pp.84–85; characteristic-class ring encoding deferred. |
| Th(γ₂→BU(2)) | 1 | Hatcher VBKT Thom spaces pp.112–113; reduced Thom shifts do not remove ordinary H₀. Products deferred. |

## Selected next collection: HP² and OP²

The user approved a bounded, independently reviewed extension from existing
spaces. These two planes explain a common cup-square pattern while differing in
grading, and require only a small three-element additive basis.

- **HP²:** Hatcher explicitly gives H*(HPⁿ;Z)=Z[α]/(α^(n+1)), |α|=4,
  following Theorem 3.19 on printed p.222. Example 3.12 p.213 also explicitly
  allows any commutative coefficient ring in the complex/quaternionic cases.
- **OP²:** Example 4.47 p.379 identifies its 0,8,16-cell construction using the
  octonionic Hopf map. The Hopf invariant discussion on printed p.427 explicitly
  states H*(OP²;Z)=Z[α]/(α³). It is not merely inferred from cell ranks.
- **Field extension deduction:** both integral rings have free groups in the
  three indicated degrees. The coefficient maps preserve cup products (p.222);
  their generators remain generators under coefficient extension. Thus for each
  k=Q,F₂,F₃,F₅,F₇, record k[x]/(x³), with |x|=4 for HP² and |x|=8 for OP².
  The additive basis is 1,x,x²; x·x=x², unit multiplication is identity, and all
  other positive products vanish. No integral/F₁₁ classical records are added.

These are ten new field records, giving 75 finite field records on 15 spaces,
without renaming the original 13-space core. Both are human-review-pending.
Consistency tests include degrees, truncation, all ordered products, and
independent comparison with the retained cellular homology via UCT. Independent
candidate review is still required; this document was written by the author of
the new records and therefore is not their independent acceptance report.

## Guided comparisons

1. CP² versus S² ∨ S⁴: same additive groups, different degree-two squares.
2. RP² across Z, Q, F₂ and odd fields: coefficient dependence and torsion's
   degree shift between integral homology and cohomology.
3. CP², HP², OP²: same truncated-polynomial shape but generator degrees 2,4,8.

Steps link to existing routes and tell readers which coefficient to compare.
The original hypothesis of a Poincaré/S³ guided comparison was replaced by the
three-plane trail because it directly exercises the newly encoded ring content;
the Poincaré introduction still warns that homology does not identify a space.

## Source acquisition and limitations

On 2026-09-06 the agent read primary author-hosted PDFs using the web PDF text
extractor:

- [Hatcher, Algebraic Topology](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf):
  560 PDF pages, printed page p maps to one-based PDF page p+9. Read the cited
  projective/Hopf passages, Moore/lens constructions, classifying-space product
  examples, and Cor.4D.3. Earlier qualified core locators are retained from
  `.scratch/classical-spaces-v1/sources.md`.
- [Hatcher, Vector Bundles and K-Theory v2.2](https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf):
  124 PDF pages, printed page p maps to PDF page p+4. Read Grassmannian cells and
  the disk/sphere-bundle definition of Thom spaces. The ordinary cohomology
  shift is separately sourced to AT Cor.4D.9 p.441 and the Thom-space
  interpretation/Theorem 4D.10 p.442, read after independent review flagged
  that VBKT's later K-theory discussion alone was insufficient. These are explicitly
  supplementary reading, not alleged AT example numbers.
- [Postnikov, Enumeration in Algebra and Geometry](https://math.mit.edu/~apost/papers/thesis.pdf):
  §2.2.1 printed53 is zero-indexed PDF53, hence link #page54. Read complete-flag
  definition and Schubert additive-basis statement; no new Schubert ring encoded.
- [Official SageMath topology documentation](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html#sage.topology.simplicial_complex_examples.PoincareHomologyThreeSphere):
  PoincareHomologyThreeSphere states equal integral homology to S³ and
  non-simple-connectivity. Direct web retrieval of the existing pinned GitHub
  source failed with cache misses; the checked-in model is unchanged, and this
  current official documentation supports only the reader-facing introduction.

No source was treated as human review. No new source adapter, backend, formal
proof system, or exhaustive textbook index was implemented.
