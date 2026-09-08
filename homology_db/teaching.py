"""Selected, source-linked teaching inventory; not an exhaustive textbook index."""

from __future__ import annotations

from .classical import CLASSICAL_SPACE_IDS, CLASSICAL_EXTENSION_SPACE_IDS

SCHEMA_VERSION = "homology-db.teaching/1"
AT = "https://pi.math.cornell.edu/~hatcher/AT/AT.pdf"
VB = "https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf"


def _source(locator: str, page: int, *, url: str = AT, title: str = "Hatcher, Algebraic Topology") -> dict:
    offset = 9 if url == AT else 4 if url == VB else 1
    return {"title": title, "url": f"{url}#page={page+offset}", "locator": locator}


def teaching_catalog() -> dict:
    entries = []

    def add(space_id, chapter, introduction, point, source, coverage=""):
        if not coverage:
            if space_id in CLASSICAL_SPACE_IDS:
                coverage = "Original thirteen-space ring core: five-field records retained. General-family instances additionally open the all-degree workbench."
            elif space_id in CLASSICAL_EXTENSION_SPACE_IDS:
                coverage = "Selected projective-plane extension: rings recorded over Q, F2, F3, F5, F7; integral and F11 ring records are not added here."
            else:
                coverage = "Homology retained; cohomology-ring records are not yet included. Not recorded does not mean zero."
        entries.append({"space_id": space_id, "chapter": chapter, "locator": source["locator"],
                        "introduction": introduction, "teaching_point": point,
                        "sources": [source], "coverage_note": coverage})

    add("point", "2.1 · First homology calculations", "A single point is the simplest nonempty space.",
        "Start here to distinguish ordinary degree-zero homology from reduced homology.", _source("Proposition 2.8, p. 110",110))
    for n in range(5):
        add(f"sphere:{n}", "2.1 · First homology calculations",
            "The zero-sphere consists of two points." if n == 0 else f"The {n}-sphere is the unit sphere in real {n+1}-dimensional space.",
            "Count connected components before reducing degree zero." if n == 0 else "A sphere isolates one positive-degree homology class; its cup square vanishes by dimension.",
            _source("Example 0.3, p. 5; Corollary 2.14, p. 114",114))
    add("poincare_homology_sphere:3", "Supplement · Homology does not identify a space",
        "This retained triangulated example has the integral homology of a three-sphere but nontrivial fundamental group.",
        "Equal homology groups do not imply that two spaces are homeomorphic.",
        {"title":"SageMath, PoincareHomologyThreeSphere", "url":"https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html#sage.topology.simplicial_complex_examples.PoincareHomologyThreeSphere", "locator":"PoincareHomologyThreeSphere documentation and examples"})
    add("sphere_wedge:2:4", "3.2 · Cup products",
        "Identify one point of a two-sphere with one point of a four-sphere to form this wedge.",
        "Compare with CP²: equal additive groups, but the degree-two cup square is zero here.", _source("Example 3.14, pp. 213–214",213))
    add("torus:2", "2.2 / 3.2 · Surfaces",
        "The torus is the product of two circles, also obtained by identifying opposite edges of a square.",
        "Its two degree-one cohomology generators multiply to the top class and each squares to zero.", _source("Example 2.36, p. 141; Examples 3.7 and 3.13, pp. 207, 213",207))
    add("klein_bottle", "2.2 / 3.2 · Surfaces",
        "The Klein bottle is a closed nonorientable surface, equivalently the connected sum of two projective planes.",
        "Changing from odd characteristic to F2 reveals a top cohomology class and nonzero degree-one squares.", _source("§1.2, pp. 51–52; Examples 2.37 and 3.8, pp. 141, 208",208))
    for g in range(2, 7):
        add(f"orientable_surface:{g}", "2.2 / 3.2 · Surfaces",
            rf"The genus-{g} orientable surface is the connected sum of {g} tori, the classification of closed surfaces naming it $\Sigma_{{{g}}}$.",
            rf"Its one 2-cell is attached by a product of {g} commutators, which abelianize to zero, so the cellular differential vanishes and $H_1$ is free of rank {2*g}.",
            _source("Example 2.36, p. 141", 141),
            coverage="Homology retained; cup-product rings over Z, Q, F2, F3, F5, F7 are imported from an external computation and are not human-reviewed.")
    for k in range(3, 7):
        add(f"nonorientable_surface:{k}", "2.2 / 3.2 · Surfaces",
            rf"The genus-{k} nonorientable surface is the connected sum of {k} projective planes, written $N_{{{k}}}$ in the classification of closed surfaces.",
            rf"The crosscap word $a_1^2\cdots a_{{{k}}}^2$ abelianizes to twice the sum of the generators, so one order-two class appears no matter how large the genus grows.",
            _source("Example 2.37, p. 141", 141),
            coverage="Homology retained; cup-product rings over Z, Q, F2, F3, F5, F7 are imported from an external computation and are not human-reviewed.")
    for n in (2,3,4):
        add(f"real_projective_space:{n}", "2.2 / 3.2 · Projective spaces",
            rf"$\mathbb{{RP}}^{{{n}}}$ is the space of real lines through the origin in real {n+1}-dimensional space.",
            "Compare the integral torsion degrees in homology and cohomology, then change coefficients.", _source("Examples 0.4 and 2.42, pp. 6, 144; Theorem 3.19, p. 220",144))
    for space, name, degree, page in (("complex_projective_space:2","complex",2,220),
                                     ("quaternionic_projective_space:2","quaternionic",4,222),
                                     ("cayley_plane:2","octonionic",8,427)):
        add(space, "3.2 / 4.B · Projective planes",
            f"The {name} projective plane has one cell in each of dimensions 0, {degree}, and {2*degree}.",
            f"Its degree-{degree} cup generator has a nonzero square: the attaching map matters beyond the cellular boundary.",
            _source("Projective rings, pp. 220–222; Example 4.47, p. 379; Hopf invariant examples, p. 427",page))
    for m,n in ((3,1),(4,1),(5,2),(7,3),(8,4),(9,2)):
        add(f"moore:{m}:{n}", "2.2 · Moore spaces",
            f"Attach an ({n+1})-cell to an {n}-sphere by a degree-{m} map to obtain this Moore space.",
            rf"Its only nonzero reduced integral homology is $\mathbb{{Z}}/{m}\mathbb{{Z}}$ in degree {n}; compare prime coefficients dividing {m} with those that do not.", _source("Example 2.40, pp. 143–144",143))
    for m,dimension,weights in ((3,3,"1-1"),(5,3,"1-1"),(5,3,"1-2"),(3,5,"1-1-1")):
        add(f"lens:{m}:{dimension}:{weights}", "2.2 · Lens spaces",
            f"This lens space is a quotient of the {dimension}-sphere by a free cyclic action of order {m}, with weights {weights.replace('-', ', ')}.",
            "Retain the weights: the cellular homology groups alone do not classify lens spaces.", _source("Example 2.43, pp. 144–146",144))
    for space,name,lower,upper in (("stunted_complex_projective:2:4","complex",1,4),("stunted_real_projective:3:6","real",2,6)):
        add(space, "2.2 · Relative groups and CW quotients",
            f"Collapse the {name} projective {lower}-space inside projective {upper}-space to a single point.",
            "The quotient retains the cells above the collapsed subcomplex; its basepoint still contributes ordinary H0.", _source("CW quotients, p. 8; relative cellular homology, pp. 138–139; Examples 0.4 and 0.6",139))
    add("special_unitary_group:3", "4.D · Lie groups and bundles",
        "SU(3) is the group of complex unitary three-by-three matrices with determinant one.",
        "This is a useful next exterior-algebra example; its ring has not been added to the atlas in this cycle.", _source("Corollary 4D.3, p. 434; Example 4D.7, p. 439",434))
    add("compact_symplectic_group:2", "4.D · Lie groups and bundles",
        "Sp(2) is the compact group of quaternionic unitary two-by-two matrices.",
        "Sphere bundles connect compact Lie groups to the examples already in the atlas.", _source("Corollary 4D.3 and its proof, p. 434",434))
    add("complete_flag:c3", "Supplement · Schubert spaces",
        "A complete flag in complex three-space is a line contained in a plane contained in the whole space.",
        "Schubert cells organize the additive groups; cup products require more information than the cell counts.",
        _source("§2.2.1, Flag manifold and Schubert cells, pp. 53–54",53,url="https://math.mit.edu/~apost/papers/thesis.pdf",title="Postnikov, Enumeration in Algebra and Geometry"))
    add("grassmannian:2:4:c", "Supplement · Schubert spaces",
        "The complex Grassmannian Gr₂(C⁴) parametrizes complex two-dimensional linear subspaces of C⁴.",
        "Its Schubert cells have even real dimensions, so the cellular boundary maps vanish.", _source("§1.2, Cell structures on Grassmannians, pp. 31–34",31,url=VB,title="Hatcher, Vector Bundles and K-Theory"))
    for p in (2,3,5):
        add(f"classifying_space:cyclic:{p}", "1.B / 2.2 · Classifying spaces",
            f"An infinite lens space models the classifying space of the cyclic group of order {p}.",
            "An infinite family of cells must not be confused with a finite table of computed degrees.", _source("Examples 1B.3–1B.4, p. 88; Example 2.43, pp. 144–146",88),
            "Homology is retained through degree 24, not exhaustive in all degrees. Cohomology rings are not recorded here.")
    for p,r in ((2,2),(2,3),(3,2)):
        add(f"classifying_space:elementary_abelian:{p}:{r}", "1.B / 3.B · Products and Künneth",
            f"Take a product of {r} cyclic classifying spaces of order {p} to model the elementary-abelian group.",
            "Products are a setting for the Künneth theorem; integral torsion needs its Tor terms.", _source("Example 1B.5, p. 88; §3.B, pp. 268–269",88),
            "Homology is retained through degree 24. No complete ring record is claimed by this teaching introduction.")
    for field,word,stride in (("complex","complex",2),("quaternionic","quaternionic",4)):
        add(f"{field}_projective_space:infinity", "3.2 · Infinite projective spaces",
            f"The union of finite {word} projective spaces has a cell in each nonnegative dimension divisible by {stride}.",
            "The source gives an unbounded polynomial ring, but this entry's stored homology table remains degree-bounded.", _source("Example 0.6, p. 7; Theorem 3.19 and quaternionic continuation, pp. 220–222",222),
            "Homology is retained through degree 24; the infinite cohomology ring is source-known but not yet encoded here.")
    add("unitary_classifying_space:2", "Supplement · Universal bundles",
        "BU(2) is modeled by the infinite Grassmannian of complex two-planes and classifies complex rank-two bundles.",
        "This connects Grassmannians with characteristic classes rather than just individual manifolds.", _source("§1.2, universal bundle and complex analogue, pp. 27–34; Theorem 3.9, pp. 84–85",27,url=VB,title="Hatcher, Vector Bundles and K-Theory"),
        "Homology is retained through degree 24. The known characteristic-class ring is not encoded in this entry.")
    add("universal_complex_thom:2", "4.D / Supplement · Thom spaces",
        "Collapse the sphere bundle of the universal complex two-plane bundle inside its disk bundle to obtain this Thom space.",
        "The Thom isomorphism shifts into reduced cohomology; do not drop the separate ordinary degree-zero class.", _source("Thom spaces, §4.1, pp. 112–113",112,url=VB,title="Hatcher, Vector Bundles and K-Theory"),
        "Homology is retained through degree 24; cohomology products are not recorded. No all-degree coverage follows from this display.")
    entries[-1]["sources"].append(_source("Corollary 4D.9, p. 441; Thom-space interpretation and Theorem 4D.10, p. 442",441))
    comparisons = [
        {"id":"same-groups-different-rings", "title":"Same groups, different cup products",
         "introduction":r"$\mathbb{CP}^{2}$ and $S^{2}\vee S^{4}$ have equal additive groups over each displayed field. Their rings distinguish them.",
         "steps":[{"text":"Open CP² and find the nonzero square of the degree-two generator.","href":"#space=complex-projective-space-2"},
                  {"text":"Open S² ∨ S⁴ with the same coefficient field: the degree-two square is zero.","href":"#space=sphere-wedge-2-4"}],
         "takeaway":"Equal homology groups are less information than the cohomology ring.",
         "sources":[_source("Example 3.14, pp. 213–214; Theorem 3.19, p. 220",213)]},
        {"id":"coefficients-and-torsion", "title":"Where does the torsion go?",
         "introduction":r"$\mathbb{RP}^{2}$ makes the difference between integral homology and cohomology visible in adjacent degrees.",
         "steps":[{"text":r"In the integral row, compare $H_1=\mathbb{Z}/2\mathbb{Z}$ with $H^{1}=0$ and $H_2=0$ with $H^{2}=\mathbb{Z}/2\mathbb{Z}$.","href":"#workbench?family=real_projective_space&n=2&start=0"},
                  {"text":r"Compare $\mathbb{Q}$, $\mathbb{F}_{2}$, and the odd fields on the same page. Only $\mathbb{F}_{2}$ retains positive-degree groups.","href":"#workbench?family=real_projective_space&n=2&start=0"}],
         "takeaway":"Coefficients change the answer; integral cohomology torsion need not occur in the same degree as homology torsion.",
         "sources":[_source("Example 2.42, p. 144; Theorem 3.5, p. 203; projective rings, pp. 220–222",222)]},
        {"id":"three-projective-planes", "title":"One cup-product pattern, three dimensions",
         "introduction":"The complex, quaternionic, and octonionic projective planes share a truncated-polynomial pattern but not the generator degree.",
         "steps":[{"text":"In CP² the generator has degree two and its square degree four.","href":"#space=complex-projective-space-2"},
                  {"text":"In HP² these degrees are four and eight.","href":"#space=quaternionic-projective-space-2"},
                  {"text":"In OP² they are eight and sixteen. Compare over the same field, for example Q.","href":"#space=cayley-plane-2"}],
         "takeaway":r"Grading is part of the ring: the same-looking relation $x^{3}=0$ can describe differently graded cohomology rings.",
         "sources":[_source("Projective rings, pp. 220–222; Hopf invariant examples, p. 427",427)]},
    ]
    return {"schema_version":SCHEMA_VERSION, "title":"A selected textbook trail",
            "scope_note":"A selected Hatcher-oriented inventory of all 51 retained spaces, with clearly marked supplementary sources—not an exhaustive index of Hatcher. Teaching exposition and new records remain human-review-pending.",
            "entries":entries,"comparisons":comparisons}
