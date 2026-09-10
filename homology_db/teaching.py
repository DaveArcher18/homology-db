"""Selected, source-linked teaching inventory; not an exhaustive textbook index."""

from __future__ import annotations

import json
from pathlib import Path

from .classical import CLASSICAL_SPACE_IDS, CLASSICAL_EXTENSION_SPACE_IDS

SCHEMA_VERSION = "homology-db.teaching/1"
AT = "https://pi.math.cornell.edu/~hatcher/AT/AT.pdf"
VB = "https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf"


def _source(locator: str, page: int, *, url: str = AT, title: str = "Hatcher, Algebraic Topology") -> dict:
    offset = 9 if url == AT else 4 if url == VB else 1
    return {"title": title, "url": f"{url}#page={page+offset}", "locator": locator}


LUTZ_S2XR = {'title': 'Frank H. Lutz, The Manifold Page (geometric 3-manifold catalogues)', 'url': 'https://www3.math.tu-berlin.de/IfM/Nachrufe/Frank_Lutz/stellar/', 'locator': 'S2xR_spaces.txt, the four closed S^2 x R manifolds'}



IMPORTED_COVERAGE = (
    "Homology and cup-product rings over Z, Q, F2, F3, F5 and F7 are imported from an "
    "external computation on a simplicial model identified by hash. That model's source "
    "states no licence, so it is named and counted here but not redistributed, and nothing "
    "below its f-vector is re-derived. Not human-reviewed."
)
_IMPORTED_MODELS = Path(__file__).resolve().parents[1] / "corpus" / "computed-rings-v1" / "imported-models.json"
_LUTZ = {
    "title": "Frank H. Lutz, The Manifold Page (geometric 3-manifold catalogues)",
    "url": "https://www3.math.tu-berlin.de/IfM/Nachrufe/Frank_Lutz/stellar/",
}
_CHAPTER = {
    "prism_polyhedral_3manifold": "Supplement . Spherical 3-manifolds",
    "flat_3manifold": "Supplement . Flat 3-manifolds",
    "nil_3manifold": "Supplement . Nil 3-manifolds",
    "h2xr_3manifold": "Supplement . Surface bundles",
    "hyperbolic_3manifold": "Supplement . Hyperbolic 3-manifolds",
    "connected_sum_3manifold": "Supplement . Connected sums",
    "four_manifold": "Supplement . Closed 4-manifolds",
    "five_manifold": "Supplement . Closed 5-manifolds",
    "combinatorial_complex": "Supplement . Combinatorial complexes",
}



_SAGE = {"title": "SageMath simplicial complex examples",
         "url": "https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html"}
_PRODUCER = {"title": "cohomology-tables (Wern Juin Gabriel Ong)",
             "url": "https://github.com/wgabrielong/cohomology-tables"}


def _model_source(retrieval):
    """Cite the catalogue the model actually came from, not always Lutz's.

    The chessboard, matching and Hom complexes are Sage constructors; citing the
    Manifold Page for them would attribute the model to the wrong author.
    """
    if retrieval["how"] == "file":
        return dict(_LUTZ, locator=f"{retrieval['file']}: {retrieval['label']}")
    if retrieval["how"] == "eprint":
        return {"title": f"arXiv:{retrieval['eprint']}", "url": retrieval["url"],
                "locator": "facet list read from the e-print source"}
    if retrieval["catalog"] == "sagemath":
        return dict(_SAGE, locator=f"{retrieval['constructor']} in {retrieval.get('version', 'SageMath')}")
    return dict(_PRODUCER, locator=retrieval["constructor"])


def _group_text(rows):
    """`Z, Z^2 + Z/2, 0` from the recorded integral homology."""
    parts = []
    for row in rows:
        pieces = []
        if row["free_rank"] == 1:
            pieces.append("Z")
        elif row["free_rank"] > 1:
            pieces.append(f"Z^{row['free_rank']}")
        pieces += [f"Z/{order}" for order in row["torsion_orders"]]
        parts.append(" + ".join(pieces) if pieces else "0")
    return ", ".join(parts)


def _imported_teaching():
    """One sourced entry per imported space, keyed off what its record says."""
    models = json.loads(_IMPORTED_MODELS.read_text(encoding="utf-8"))["models"]
    entries = []
    for model in models:
        family = model["family"]
        chapter = _CHAPTER.get(family)
        if chapter is None:
            continue
        descriptor = model["model"]
        name = model["source_space"]
        groups = _group_text(model["integral_homology"])
        introduction = (
            f"{model['label']} is recorded here from a {descriptor['vertices']}-vertex, "
            f"{descriptor['facets']}-facet triangulation, with integral homology {groups}."
        )
        point = _POINT[family](model, groups)
        entries.append({
            "space_id": model["space_id"], "chapter": chapter,
            "introduction": introduction, "point": point,
            "source": _model_source(descriptor["retrieval"]),
        })
    return sorted(entries, key=lambda entry: entry["space_id"])


_POINT = {
    "prism_polyhedral_3manifold": lambda model, groups:
        "A finite fundamental group leaves only torsion in the first homology; compare the coefficient fields that divide those orders with the ones that do not.",
    "flat_3manifold": lambda model, groups:
        "Whether the top group is Z or zero is exactly whether this quotient of Euclidean space is orientable.",
    "nil_3manifold": lambda model, groups:
        "The torsion in the first homology is the Euler number of the circle bundle, read straight off the group.",
    "h2xr_3manifold": lambda model, groups:
        "Check the groups against the Kunneth formula applied to the surface factor and the circle.",
    "hyperbolic_3manifold": lambda model, groups:
        "Volume determines this manifold but homology does not; look for the other entries in this family sharing its first homology.",
    "connected_sum_3manifold": lambda model, groups:
        "Homology adds over a connected sum away from the top degree; the relations on this page name the summands the sum is built from.",
    "four_manifold": lambda model, groups:
        "In dimension four the cup product on the middle degree is the intersection form, and it separates spaces this table cannot.",
    "five_manifold": lambda model, groups:
        "Read the middle-degree class first: in dimension five that is where a product or a twisting shows itself.",
    "combinatorial_complex": lambda model, groups:
        "The torsion here comes from the combinatorics rather than from any geometry, so its orders are arbitrary and worth changing coefficients against.",
}


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
    for n in range(7):
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
    for genus in (15, 26):
        add(f"orientable_surface:{genus}", "2.2 / 3.2 . Surfaces",
            rf"The genus-{genus} orientable surface is the connected sum of {genus} tori.",
            "At this genus the first homology has rank in the dozens while the ring stays the same symplectic shape; growth in the groups is not growth in structure.",
            _source("Example 2.36, p. 141", 141),
            coverage=IMPORTED_COVERAGE)
    for triple in ((2,3,7),(2,5,7),(3,4,5),(3,4,7),(3,5,7),(4,5,7)):
        p_value, q_value, r_value = triple
        add(f"brieskorn_sphere:{p_value}:{q_value}:{r_value}",
            "Supplement . Homology does not identify a space",
            rf"The Brieskorn sphere $\Sigma({p_value},{q_value},{r_value})$ is the link of a singularity, and has the integral homology of the 3-sphere.",
            "Every group on this page agrees with those of S^3 and with the other Brieskorn spheres; homology cannot separate any of them.",
            dict(_LUTZ, locator="homology_3spheres.txt: Sigma_%d_%d_%d" % triple),
            coverage=IMPORTED_COVERAGE)
    for entry in _imported_teaching():
        add(entry["space_id"], entry["chapter"], entry["introduction"], entry["point"],
            dict(entry["source"]), coverage=IMPORTED_COVERAGE)
    for space, introduction, point in (
        ("s2xr:s2xs1",
         r"The product $S^{2}\times S^{1}$ is the orientable sphere bundle over the circle.",
         "Kunneth gives a free class in every degree; compare it with the twisted bundle, which has the same first Betti number and different torsion."),
        ("s2xr:s2-twist-s1",
         r"Gluing $S^{2}\times[0,1]$ by a reflection gives the nonorientable sphere bundle over the circle.",
         r"Reversing orientation replaces the top class by $\mathbb{Z}/2$ in degree two: orientability is visible in homology alone here."),
        ("s2xr:rp2xs1",
         r"The product $\mathbb{R}P^{2}\times S^{1}$ carries torsion in two consecutive degrees.",
         "Change coefficients to F2 and watch both torsion classes and their universal-coefficient shadows appear at once."),
        ("s2xr:rp3-sum-rp3",
         r"The connected sum $\mathbb{R}P^{3}\mathbin{\#}\mathbb{R}P^{3}$ is the one reducible manifold in this geometry.",
         "Each summand contributes one order-two class to the first homology; the sum is orientable although a single projective plane factor is not."),
    ):
        add(space, "Supplement . Geometric 3-manifolds", introduction, point, dict(LUTZ_S2XR),
            coverage="Homology and cup-product rings over Z, Q, F2, F3, F5, F7 are imported from an external computation on a hash-identified triangulation that is not redistributed here. Not human-reviewed.")
    for n in (2,3,4,5):
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
    for m,dimension,weights in ((3,3,"1-1"),(4,3,"1-1"),(5,3,"1-1"),(5,3,"1-2"),
                                (6,3,"1-1"),(7,3,"1-1"),(7,3,"1-2"),(8,3,"1-1"),
                                (8,3,"1-3"),(9,3,"1-1"),(9,3,"1-2"),(10,3,"1-1"),
                                (10,3,"1-3"),(3,5,"1-1-1")):
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
            "scope_note":"A selected Hatcher-oriented inventory of all 212 retained spaces, with clearly marked supplementary sources—not an exhaustive index of Hatcher. Teaching exposition and new records remain human-review-pending.",
            "entries":entries,"comparisons":comparisons}
