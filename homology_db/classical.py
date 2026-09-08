"""The literature-evidenced subset of the cohomology ring corpus.

These records are read out of Hatcher rather than computed: they do not derive
cup products from the homology Snapshot's boundary matrices.  The finite
multiplication tables provide reproducible consistency checks, not a formal
proof or a claim of human mathematical review.  Scalars in this version are
integer representatives in Q or a prime field.

The schema and the ring axioms live in `cohomology_rings`, which the
machine-computed records share; what is specific to this module is the closed
list of identities it curates, its Hatcher source catalogue, and the display
strings it generates from each structured algebra.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .cohomology_rings import (
    COHOMOLOGY_RING_SCHEMA_VERSION,
    validate_cohomology_ring_record,
)

CLASSICAL_SCHEMA_VERSION = COHOMOLOGY_RING_SCHEMA_VERSION
CLASSICAL_COEFFICIENTS = ("Q", "F2", "F3", "F5", "F7")
CLASSICAL_SPACE_IDS = (
    "point", *(f"sphere:{n}" for n in range(5)), "torus:2", "klein_bottle",
    *(f"real_projective_space:{n}" for n in (2, 3, 4)),
    "complex_projective_space:2", "sphere_wedge:2:4",
)
CLASSICAL_EXTENSION_SPACE_IDS = ("quaternionic_projective_space:2", "cayley_plane:2")
CLASSICAL_RECORDED_SPACE_IDS = CLASSICAL_SPACE_IDS + CLASSICAL_EXTENSION_SPACE_IDS
CLASSICAL_SOURCES = {
    "hatcher2002": {
        "title": "Algebraic Topology",
        "authors": ["Allen Hatcher"],
        "publication_year": 2002,
        "url": "https://pi.math.cornell.edu/~hatcher/AT/AT.pdf",
    }
}


def _integer(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError(f"{label} must be an integer" + (f" >= {minimum}" if minimum is not None else ""))
    return value


def validate_classical_record(record: dict[str, Any]) -> None:
    """Validate one literature record, and what is specific to this subset.

    Grading, the unit law, graded commutativity, associativity, the monomial
    basis and the stated relations are checked by the shared cohomology-ring
    validator.  What belongs here is the closed identity list this corpus
    curates and the requirement that the display string be generated from the
    structured algebra rather than authored alongside it.
    """
    if record.get("space_id") not in CLASSICAL_RECORDED_SPACE_IDS:
        raise ValueError("unknown classical space identity")
    if record.get("coefficient") not in CLASSICAL_COEFFICIENTS:
        raise ValueError("unsupported classical coefficient")
    if record["provenance"].get("kind") != "literature":
        raise ValueError("the classical corpus is the literature-evidenced subset")
    validate_cohomology_ring_record(record, CLASSICAL_SOURCES)
    expected_tex, expected_plain = _presentation(record["algebra"], record["coefficient"])
    if (record["presentation"]["tex"], record["presentation"]["plain"]) != (expected_tex, expected_plain):
        raise ValueError("display presentation must be generated from the structured algebra")


def validate_classical_records(records: dict[str, list[dict[str, Any]]] | None = None) -> dict[str, Any]:
    """Validate exact identity/coefficient coverage as well as each finite ring."""
    records = classical_records() if records is None else records
    if set(records) != set(CLASSICAL_RECORDED_SPACE_IDS):
        raise ValueError("classical corpus requires the original 13 and two extension identities")
    for space_id, entries in records.items():
        if len(entries) != len(CLASSICAL_COEFFICIENTS) or {r["coefficient"] for r in entries} != set(CLASSICAL_COEFFICIENTS):
            raise ValueError("classical corpus requires five distinct field records per space")
        for record in entries:
            if record["space_id"] != space_id:
                raise ValueError("classical record is attached to the wrong space")
            validate_classical_record(record)
    return {"space_count": len(records), "record_count": sum(map(len, records.values())),
            "schema_version": CLASSICAL_SCHEMA_VERSION, "review_state": "human_review_pending"}


def _presentation(algebra: dict[str, Any], coefficient: str) -> tuple[str, str]:
    field = r"\mathbb{Q}" if coefficient == "Q" else rf"\mathbb{{F}}_{{{coefficient[1:]}}}"
    generators, relations = algebra["generators"], algebra["relations"]
    if not generators:
        return field, coefficient
    names = ",".join(g["id"] for g in generators)
    exterior_relations = [{"terms": [{"coefficient": 1, "powers": {g["id"]: 2}}]} for g in generators]
    if all(g["degree"] % 2 for g in generators) and relations == exterior_relations:
        return rf"\Lambda_{{{field}}}({names})", f"Exterior_{coefficient}({names})"

    def polynomial(relation: dict[str, Any], tex: bool) -> str:
        rendered = ""
        for term in relation["terms"]:
            scalar = term["coefficient"]
            pieces = []
            for generator in generators:
                key, exponent = generator["id"], term["powers"].get(generator["id"], 0)
                if exponent:
                    pieces.append(key if exponent == 1 else (f"{key}^{{{exponent}}}" if tex else f"{key}^{exponent}"))
            body = "".join(pieces) if tex else "*".join(pieces)
            body = (str(abs(scalar)) if abs(scalar) != 1 or not body else "") + body
            rendered += ((" - " if scalar < 0 else " + ") if rendered else ("-" if scalar < 0 else "")) + body
        return rendered

    return (f"{field}[{names}]/(" + ",".join(polynomial(r, True) for r in relations) + ")",
            f"{coefficient}[{names}]/(" + ", ".join(polynomial(r, False) for r in relations) + ")")


def _relation(*terms: tuple[int, dict[str, int]]) -> dict[str, Any]:
    return {"terms": [{"coefficient": scalar, "powers": powers} for scalar, powers in terms]}


def _record(space: str, coefficient: str, dimension: int, generators: list[tuple[str, int]],
            basis: list[tuple[str, int, dict[str, int]]], relations: list[dict[str, Any]],
            extra_products: list[tuple[str, str, str, int]], locator: str,
            derivation: str, note: str = "") -> dict[str, Any]:
    basis = [("1", 0, {}), *basis]
    algebra = {
        "kind": "graded_commutative",
        "generators": [{"id": key, "degree": degree} for key, degree in generators],
        "relations": relations, "unit": "1",
        "basis": [{"id": key, "degree": degree, "order": 0, "powers": powers}
                  for key, degree, powers in basis],
        "products": [{"left": left, "right": right, "result": [{"basis": result, "coefficient": scalar}]}
                     for left, right, result, scalar in extra_products],
        "multiplication": {"complete": True, "omitted_products": "zero", "scope": "all_nonunit_ordered_basis_pairs",
                           "unit_products": "identity"},
    }
    tex, plain = _presentation(algebra, coefficient)
    counts = Counter(degree for _, degree, _ in basis)
    return {
        "schema_version": CLASSICAL_SCHEMA_VERSION,
        "record_id": f"classical:{space}:{coefficient}:v1", "space_id": space,
        "coefficient": coefficient, "characteristic": 0 if coefficient == "Q" else int(coefficient[1:]),
        "theory": "ordinary_cohomology", "convention": "unreduced", "knowledge_state": "exact",
        "algebra": algebra,
        "groups": [{"degree": degree, "dimension": counts[degree]} for degree in range(dimension + 1)],
        "coverage": {"kind": "complete_finite", "through_degree": dimension, "upper_vanishing_starts_at": dimension + 1},
        "sources": [{"source_id": "hatcher2002", "locator": locator, "role": "ring_and_derivation"}],
        "provenance": {"kind": "literature", "review_state": "human_review_pending", "derivation": derivation},
        "presentation": {"tex": tex, "plain": plain, "notes": [note] if note else []},
    }


def classical_records() -> dict[str, list[dict[str, Any]]]:
    """Return fresh, versioned literature records; callers cannot mutate a cache."""
    records: dict[str, list[dict[str, Any]]] = {space: [] for space in CLASSICAL_RECORDED_SPACE_IDS}
    for field in CLASSICAL_COEFFICIENTS:
        records["point"].append(_record(
            "point", field, 0, [], [], [], [], "Proposition 2.8, p. 110; §3.1, p. 198; §3.2, p. 207",
            "Point cohomology, with the constant unit."))
        records["sphere:0"].append(_record(
            "sphere:0", field, 0, [("e", 0)], [("e", 0, {"e": 1})],
            [_relation((1, {"e": 2}), (-1, {"e": 1}))], [("e", "e", "e", 1)],
            "§3.1, p. 198; Example 3.14, p. 213",
            "Degree-zero functions with coordinatewise products.",
            "The unit is (1,1) and e=(1,0). This ring is the product of two copies of the field."))
        for n in range(1, 5):
            space = f"sphere:{n}"
            records[space].append(_record(
                space, field, n, [("x", n)], [("x", n, {"x": 1})], [_relation((1, {"x": 2}))], [],
                "Corollary 2.14, p. 114; §3.1, p. 198; §3.2, p. 207",
                "Sphere groups; the unit and grading determine products."))
        records["torus:2"].append(_record(
            "torus:2", field, 2, [("a", 1), ("b", 1)],
            [("a", 1, {"a": 1}), ("b", 1, {"b": 1}), ("w", 2, {"a": 1, "b": 1})],
            [_relation((1, {"a": 2})), _relation((1, {"b": 2}))],
            [("a", "b", "w", 1), ("b", "a", "w", 1 if field == "F2" else -1)],
            "Examples 3.7, 3.13, pp. 207–208, 213; Theorem 3.11, p. 210",
            "Exterior algebra on the two circle-factor classes.",
            "Both generators square to zero; ab is the top class and ba=-ab (equal to ab in characteristic 2)."))
        if field == "F2":
            records["klein_bottle"].append(_record(
                "klein_bottle", field, 2, [("a", 1), ("b", 1)],
                [("a", 1, {"a": 1}), ("b", 1, {"b": 1}), ("w", 2, {"a": 2})],
                [_relation((1, {"a": 2}), (1, {"b": 2})), _relation((1, {"a": 1, "b": 1}))],
                [("a", "a", "w", 1), ("b", "b", "w", 1)],
                "§1.2, pp. 51–52; Example 3.8, p. 208",
                "Use the diagonal crosscap basis for the connected sum of two projective planes.",
                "In this basis a²=b²=w is the nonzero top class and ab=0. Other valid bases can give different-looking products."))
        else:
            records["klein_bottle"].append(_record(
                "klein_bottle", field, 2, [("a", 1)], [("a", 1, {"a": 1})], [_relation((1, {"a": 2}))], [],
                "Example 2.37, p. 141; Theorem 3.5, p. 203; §3.2, p. 207",
                "Cellular cochains with 2 invertible; H²=0 forces a²=0."))
        for n in (2, 3, 4):
            space = f"real_projective_space:{n}"
            if field == "F2":
                basis = [("x" if i == 1 else f"x{i}", i, {"x": i}) for i in range(1, n + 1)]
                products = [(left, right, "x" if a + b == 1 else f"x{a + b}", 1)
                            for left, a, _ in basis for right, b, _ in basis if a + b <= n]
                records[space].append(_record(
                    space, field, n, [("x", 1)], basis, [_relation((1, {"x": n + 1}))], products,
                    "Theorem 3.19, p. 220",
                    "The projective polynomial ring, truncated at dimension."))
            else:
                records[space].append(_record(
                    space, field, n, [("x", n)] if n % 2 else [], [("x", n, {"x": 1})] if n % 2 else [],
                    [_relation((1, {"x": 2}))] if n % 2 else [], [],
                    "Example 2.42, p. 144; Theorem 3.5, p. 203; §3.2, p. 207",
                    "Cellular cochains with 2 invertible; products follow by grading."))
        records["complex_projective_space:2"].append(_record(
            "complex_projective_space:2", field, 4, [("x", 2)],
            [("x", 2, {"x": 1}), ("x2", 4, {"x": 2})], [_relation((1, {"x": 3}))], [("x", "x", "x2", 1)],
            "Example 3.12, p. 213; Theorem 3.19, p. 220",
            "Base change of the integral projective ring to the field.",
            "The square x² is nonzero, unlike on S² ∨ S⁴, despite equal additive groups."))
        records["sphere_wedge:2:4"].append(_record(
            "sphere_wedge:2:4", field, 4, [("a", 2), ("b", 4)],
            [("a", 2, {"a": 1}), ("b", 4, {"b": 1})],
            [_relation((1, {"a": 2})), _relation((1, {"a": 1, "b": 1})), _relation((1, {"b": 2}))], [],
            "Example 3.14, pp. 213–214",
            "Sphere wedge products vanish in positive degrees.",
            "All positive-degree products vanish, including a² in degree 4; b is independent."))
        for space, degree, locator in (
            ("quaternionic_projective_space:2", 4, "Example 3.12, p. 213; quaternionic projective rings following Theorem 3.19, p. 222"),
            ("cayley_plane:2", 8, "Example 4.47, p. 379; §4.B, Hopf invariant examples, p. 427; coefficient ring maps, p. 222"),
        ):
            records[space].append(_record(
                space, field, 2 * degree, [("x", degree)],
                [("x", degree, {"x": 1}), ("x2", 2 * degree, {"x": 2})],
                [_relation((1, {"x": 3}))], [("x", "x", "x2", 1)], locator,
                "The cited integral projective-plane ring has a generator whose square is the top generator. Its free integral groups imply that coefficient change carries these generators and their cup product to each requested field. This coefficient-extension step is a deduction, not a new integral record.",
                "A selected extension to the original thirteen-space core. The positive generator squares nontrivially and its cube vanishes by dimension."))
    return records
