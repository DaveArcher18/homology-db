"""Sourced ordinary cohomology rings for the small classical teaching corpus.

These literature records supplement the existing homology Snapshot; they do not
derive cup products from its boundary matrices.  The finite multiplication
tables provide reproducible consistency checks, not a formal proof or a claim
of human mathematical review.  Scalars in this version are integer
representatives in Q or a prime field.
"""

from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Any


CLASSICAL_SCHEMA_VERSION = "homology-db.classical-cohomology/1"
CLASSICAL_COEFFICIENTS = ("Q", "F2", "F3", "F5", "F7")
CLASSICAL_SPACE_IDS = (
    "point", *(f"sphere:{n}" for n in range(5)), "torus:2", "klein_bottle",
    *(f"real_projective_space:{n}" for n in (2, 3, 4)),
    "complex_projective_space:2", "sphere_wedge:2:4",
)
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
    """Reject malformed or internally inconsistent finite graded ring records.

    Checks the full finite algebra (unit, grading, graded commutativity and
    associativity), all stated homogeneous relations, the monomial basis, and
    additive coverage.  It does not prove that the presentation ideal has no
    further independent classes; that assertion remains literature-sourced.
    """
    if record.get("schema_version") != CLASSICAL_SCHEMA_VERSION:
        raise ValueError("unsupported classical schema version")
    if record.get("space_id") not in CLASSICAL_SPACE_IDS:
        raise ValueError("unknown classical space identity")
    coefficient = record.get("coefficient")
    if coefficient not in CLASSICAL_COEFFICIENTS:
        raise ValueError("unsupported classical coefficient")
    p = 0 if coefficient == "Q" else int(coefficient[1:])
    if type(record.get("characteristic")) is not int or record["characteristic"] != p:
        raise ValueError("coefficient characteristic mismatch")
    if record.get("record_id") != f"classical:{record['space_id']}:{coefficient}:v1":
        raise ValueError("record identity mismatch")
    if (record.get("theory"), record.get("convention"), record.get("knowledge_state")) != (
        "ordinary_cohomology", "unreduced", "exact"
    ):
        raise ValueError("ordinary unreduced exact cohomology is required")
    algebra = record["algebra"]
    if algebra.get("kind") != "graded_commutative":
        raise ValueError("unsupported algebra kind")
    if algebra.get("multiplication") != {
        "complete": True, "omitted_products": "zero", "scope": "all_nonunit_ordered_basis_pairs",
        "unit_products": "identity",
    }:
        raise ValueError("multiplication requires explicit complete all-basis coverage")
    basis_list = algebra["basis"]
    basis = {item["id"]: item for item in basis_list}
    if not basis or len(basis) != len(basis_list):
        raise ValueError("basis IDs must be nonempty and unique")
    for item in basis_list:
        _integer(item["degree"], "basis degree", 0)
    unit = algebra.get("unit")
    if unit != "1" or unit not in basis or basis[unit]["degree"] != 0 or basis[unit]["powers"]:
        raise ValueError("unit must be the degree-zero constant basis element 1")
    generators = {item["id"]: item for item in algebra["generators"]}
    if len(generators) != len(algebra["generators"]):
        raise ValueError("generator IDs must be unique")
    for key, generator in generators.items():
        _integer(generator["degree"], "generator degree", 0)
        if key == unit or key not in basis or generator["degree"] != basis[key]["degree"]:
            raise ValueError("generator must name a basis element of the same degree")

    def normalize(vector: dict[str, int]) -> dict[str, int]:
        return {key: (value % p if p else value) for key, value in vector.items()
                if (value % p if p else value)}

    # Unit products are completely specified by the encoding, avoiding their
    # redundant repetition in every coefficient record in the static artifact.
    table: dict[tuple[str, str], dict[str, int]] = {
        (unit, key): {key: 1} for key in basis
    }
    table.update({(key, unit): {key: 1} for key in basis})
    for entry in algebra["products"]:
        pair = (entry["left"], entry["right"])
        if pair in table or any(key not in basis for key in pair):
            raise ValueError("product input must be a unique ordered basis pair")
        value: dict[str, int] = {}
        for term in entry["result"]:
            key = term["basis"]
            scalar = _integer(term["coefficient"], "product scalar")
            if key not in basis or key in value or not normalize({key: scalar}):
                raise ValueError("product result requires unique known basis and nonzero scalars")
            if basis[key]["degree"] != sum(basis[item]["degree"] for item in pair):
                raise ValueError("product violates grading")
            value[key] = scalar
        if not value:
            raise ValueError("sparse table must omit zero products")
        table[pair] = normalize(value)

    def multiply(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
        result: Counter[str] = Counter()
        for a, x in left.items():
            for b, y in right.items():
                for c, z in table.get((a, b), {}).items():
                    result[c] += x * y * z
        return normalize(dict(result))

    for a in basis:
        if table.get((unit, a), {}) != {a: 1} or table.get((a, unit), {}) != {a: 1}:
            raise ValueError("multiplication violates the unit law")
    for a, b in product(basis, repeat=2):
        sign = (-1) ** (basis[a]["degree"] * basis[b]["degree"])
        if table.get((a, b), {}) != normalize({k: sign * v for k, v in table.get((b, a), {}).items()}):
            raise ValueError("multiplication violates graded commutativity")
    for a, b, c in product(basis, repeat=3):
        if multiply(table.get((a, b), {}), {c: 1}) != multiply({a: 1}, table.get((b, c), {})):
            raise ValueError("multiplication violates associativity")

    def monomial(powers: dict[str, int]) -> tuple[int, dict[str, int]]:
        if not isinstance(powers, dict) or any(key not in generators for key in powers):
            raise ValueError("monomial contains an unknown generator")
        result = {unit: 1}
        degree = 0
        for key in generators:
            exponent = _integer(powers.get(key, 0), "monomial exponent", 0)
            degree += generators[key]["degree"] * exponent
            for _ in range(exponent):
                result = multiply(result, {key: 1})
        return degree, result

    for key, element in basis.items():
        degree, value = monomial(element["powers"])
        if degree != element["degree"] or value != {key: 1}:
            raise ValueError("basis monomial does not evaluate to its declared basis element")
    for relation in algebra["relations"]:
        degrees: set[int] = set()
        total: Counter[str] = Counter()
        if not relation["terms"]:
            raise ValueError("relation must have terms")
        for term in relation["terms"]:
            scalar = _integer(term["coefficient"], "relation scalar")
            if not (scalar % p if p else scalar):
                raise ValueError("relation scalar must be nonzero in the field")
            degree, value = monomial(term["powers"])
            degrees.add(degree)
            for key, value_scalar in value.items():
                total[key] += scalar * value_scalar
        if len(degrees) != 1:
            raise ValueError("relation is not homogeneous")
        if normalize(dict(total)):
            raise ValueError("relation is not satisfied by the multiplication table")

    coverage = record["coverage"]
    through = _integer(coverage["through_degree"], "coverage through_degree", 0)
    if coverage != {"kind": "complete_finite", "through_degree": through,
                    "upper_vanishing_starts_at": through + 1}:
        raise ValueError("complete finite coverage must declare its upper vanishing bound")
    counts = Counter(item["degree"] for item in basis_list)
    for group in record["groups"]:
        _integer(group["degree"], "group degree", 0)
        _integer(group["dimension"], "group dimension", 0)
    if max(counts) > through or record["groups"] != [
        {"degree": degree, "dimension": counts[degree]} for degree in range(through + 1)
    ]:
        raise ValueError("additive groups must explicitly agree with the basis in every covered degree")
    if not record["sources"]:
        raise ValueError("literature sources are required")
    for source in record["sources"]:
        if source.get("source_id") not in CLASSICAL_SOURCES or not source.get("locator") or not source.get("role"):
            raise ValueError("source requires a resolvable ID, locator and role")
    provenance = record["provenance"]
    if provenance.get("kind") != "literature" or provenance.get("review_state") != "human_review_pending" or not provenance.get("derivation"):
        raise ValueError("literature provenance and pending human review must remain explicit")
    expected_tex, expected_plain = _presentation(algebra, coefficient)
    if (record["presentation"]["tex"], record["presentation"]["plain"]) != (expected_tex, expected_plain):
        raise ValueError("display presentation must be generated from the structured algebra")


def validate_classical_records(records: dict[str, list[dict[str, Any]]] | None = None) -> dict[str, Any]:
    """Validate exact identity/coefficient coverage as well as each finite ring."""
    records = classical_records() if records is None else records
    if set(records) != set(CLASSICAL_SPACE_IDS):
        raise ValueError("classical corpus requires the exact 13 space identities")
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
        "basis": [{"id": key, "degree": degree, "powers": powers} for key, degree, powers in basis],
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
    records: dict[str, list[dict[str, Any]]] = {space: [] for space in CLASSICAL_SPACE_IDS}
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
    return records
