"""One corpus of ordinary cohomology rings, split by evidence rather than model.

A cohomology ring is an invariant of the space.  How it was established --
read out of the literature, or computed by a machine from some finite model --
is provenance, not a different kind of object, so both live here under one
schema and one validator.  `classical` supplies the literature-evidenced
records; `corpus/computed-rings-v1` supplies the machine-computed ones.

The validator checks what a ring must satisfy to be a ring at all: grading, the
unit law, graded commutativity, associativity, and agreement between the stated
additive groups and the basis.  A record presented with generators and
relations is additionally required to have a monomial basis and a display
string derived from its own structure.  Neither check establishes that the
table is the cohomology of any particular space; that is what the provenance
records, and it is never upgraded here into a claim of human review.

Two records may describe the same space and coefficient with different
evidence.  They are kept as separate corroborating assertions and are never
merged; if their additive groups disagree the corpus refuses to build rather
than choosing a winner.
"""

from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Any

COHOMOLOGY_RING_SCHEMA_VERSION = "homology-db.cohomology-rings/1"
COHOMOLOGY_RING_COEFFICIENTS = ("Z", "Q", "F2", "F3", "F5", "F7")
FIELD_COEFFICIENTS = ("Q", "F2", "F3", "F5", "F7")
ALGEBRA_KINDS = ("graded_commutative", "graded_structure_constants")
PROVENANCE_KINDS = ("literature", "external_engine_computation")
REVIEW_STATES = {
    "literature": "human_review_pending",
    "external_engine_computation": "imported_unreviewed",
}
RECORD_PREFIX = {"literature": "classical", "external_engine_computation": "computed"}
MULTIPLICATION_SCOPE = {
    "complete": True, "omitted_products": "zero",
    "scope": "all_nonunit_ordered_basis_pairs", "unit_products": "identity",
}


def _integer(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError(f"{label} must be an integer" + (f" >= {minimum}" if minimum is not None else ""))
    return value


def characteristic_of(coefficient: str) -> int:
    return 0 if coefficient in ("Z", "Q") else int(coefficient[1:])


def validate_cohomology_ring_record(record: dict[str, Any], sources: dict[str, Any]) -> None:
    """Reject a malformed or internally inconsistent cohomology ring record."""
    if record.get("schema_version") != COHOMOLOGY_RING_SCHEMA_VERSION:
        raise ValueError("unsupported cohomology ring schema version")
    coefficient = record.get("coefficient")
    if coefficient not in COHOMOLOGY_RING_COEFFICIENTS:
        raise ValueError("unsupported cohomology ring coefficient")
    characteristic = characteristic_of(coefficient)
    if _integer(record.get("characteristic"), "characteristic", 0) != characteristic:
        raise ValueError("coefficient characteristic mismatch")
    space_id = record.get("space_id")
    if not isinstance(space_id, str) or not space_id:
        raise ValueError("a cohomology ring record needs a space identity")
    provenance = record["provenance"]
    kind = provenance.get("kind")
    if kind not in PROVENANCE_KINDS:
        raise ValueError("unsupported cohomology ring provenance")
    if record.get("record_id") != f"{RECORD_PREFIX[kind]}:{space_id}:{coefficient}:v1":
        raise ValueError("record identity mismatch")
    if (record.get("theory"), record.get("convention"), record.get("knowledge_state")) != (
        "ordinary_cohomology", "unreduced", "exact"
    ):
        raise ValueError("ordinary unreduced exact cohomology is required")

    algebra = record["algebra"]
    if algebra.get("kind") not in ALGEBRA_KINDS:
        raise ValueError("unsupported algebra kind")
    if algebra.get("multiplication") != MULTIPLICATION_SCOPE:
        raise ValueError("multiplication requires explicit complete all-basis coverage")

    basis_list = algebra["basis"]
    basis = {item["id"]: item for item in basis_list}
    if not basis or len(basis) != len(basis_list):
        raise ValueError("basis IDs must be nonempty and unique")
    for item in basis_list:
        _integer(item["degree"], "basis degree", 0)
        order = _integer(item["order"], "basis order", 0)
        if order == 1:
            raise ValueError("a trivial summand must not be recorded as a basis element")
        if characteristic and order:
            raise ValueError("prime-field records carry free summands only")
        if coefficient == "Q" and order:
            raise ValueError("rational records carry free summands only")
    unit = algebra.get("unit")
    if unit != "1" or unit not in basis or basis[unit]["degree"] != 0 or basis[unit]["order"] != 0:
        raise ValueError("the unit must be the free degree-zero basis element 1")

    def modulus(key: str) -> int:
        return basis[key]["order"] or characteristic

    def normalize(vector: dict[str, int]) -> dict[str, int]:
        reduced = {}
        for key, value in vector.items():
            bound = modulus(key)
            scalar = value % bound if bound else value
            if scalar:
                reduced[key] = scalar
        return reduced

    table: dict[tuple[str, str], dict[str, int]] = {(unit, key): {key: 1} for key in basis}
    table.update({(key, unit): {key: 1} for key in basis})
    for entry in algebra["products"]:
        pair = (entry["left"], entry["right"])
        if pair in table or any(key not in basis for key in pair):
            raise ValueError("product input must be a unique ordered non-unit basis pair")
        value: dict[str, int] = {}
        for term in entry["result"]:
            key = term["basis"]
            scalar = _integer(term["coefficient"], "product scalar")
            if key not in basis or key in value:
                raise ValueError("product result requires unique known basis elements")
            if basis[key]["degree"] != sum(basis[item]["degree"] for item in pair):
                raise ValueError("product violates grading")
            value[key] = scalar
        reduced = normalize(value)
        if not reduced:
            raise ValueError("sparse table must omit zero products")
        table[pair] = reduced

    def multiply(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
        result: Counter[str] = Counter()
        for a, x in left.items():
            for b, y in right.items():
                for key, scalar in table.get((a, b), {}).items():
                    result[key] += x * y * scalar
        return normalize(dict(result))

    for key in basis:
        if table.get((unit, key)) != {key: 1} or table.get((key, unit)) != {key: 1}:
            raise ValueError("multiplication violates the unit law")
    for left, right in product(basis, repeat=2):
        sign = (-1) ** (basis[left]["degree"] * basis[right]["degree"])
        mirrored = normalize({k: sign * v for k, v in table.get((right, left), {}).items()})
        if table.get((left, right), {}) != mirrored:
            raise ValueError("multiplication violates graded commutativity")
        value = table.get((left, right), {})
        for factor in (left, right):
            order = basis[factor]["order"]
            if order and normalize({key: order * scalar for key, scalar in value.items()}):
                raise ValueError(
                    "multiplication does not respect the additive order of a torsion factor"
                )
    for a, b, c in product(basis, repeat=3):
        if multiply(table.get((a, b), {}), {c: 1}) != multiply({a: 1}, table.get((b, c), {})):
            raise ValueError("multiplication violates associativity")

    if algebra["kind"] == "graded_commutative":
        _validate_presentation(record, algebra, basis, unit, multiply, normalize, characteristic)

    coverage = record["coverage"]
    through = _integer(coverage.get("through_degree"), "coverage through_degree", 0)
    if coverage != {"kind": "complete_finite", "through_degree": through,
                    "upper_vanishing_starts_at": through + 1}:
        raise ValueError("complete finite coverage must declare its upper vanishing bound")
    if max(item["degree"] for item in basis_list) > through:
        raise ValueError("a basis element lies above the stated coverage")
    if record["groups"] != expected_groups(basis_list, through, coefficient):
        raise ValueError("additive groups must explicitly agree with the basis in every covered degree")

    if not record.get("sources"):
        raise ValueError("a cohomology ring record must cite its evidence")
    for source in record["sources"]:
        if source.get("source_id") not in sources or not source.get("locator") or not source.get("role"):
            raise ValueError("source requires a resolvable ID, locator and role")
    if provenance.get("review_state") != REVIEW_STATES[kind]:
        raise ValueError("provenance may not carry a promoted review state")
    if not provenance.get("derivation"):
        raise ValueError("provenance must say how the ring was established")
    if kind == "external_engine_computation":
        for field in ("model_id", "engine", "engine_version", "source_locator", "model_facets_sha256"):
            if not provenance.get(field):
                raise ValueError(f"computed provenance needs {field}")


def expected_groups(basis_list: list[dict[str, Any]], through: int, coefficient: str) -> list[dict[str, Any]]:
    """Additive groups implied by the basis, in the read model's own shape.

    Integral records report free rank and torsion the way integral homology rows
    do; field and rational records report a dimension.  This mirrors the
    existing homology projection rather than inventing a third spelling.
    """
    groups = []
    for degree in range(through + 1):
        summands = [item for item in basis_list if item["degree"] == degree]
        if coefficient == "Z":
            groups.append({
                "degree": degree,
                "free_rank": sum(1 for item in summands if item["order"] == 0),
                "torsion_orders": sorted(item["order"] for item in summands if item["order"] > 1),
            })
        else:
            groups.append({"degree": degree, "dimension": len(summands)})
    return groups


def _validate_presentation(record, algebra, basis, unit, multiply, normalize, characteristic):
    """Generators, relations and a monomial basis, for records that claim one."""
    generators = {item["id"]: item for item in algebra["generators"]}
    if len(generators) != len(algebra["generators"]):
        raise ValueError("generator IDs must be unique")
    for key, generator in generators.items():
        _integer(generator["degree"], "generator degree", 0)
        if key == unit or key not in basis or generator["degree"] != basis[key]["degree"]:
            raise ValueError("generator must name a basis element of the same degree")

    def monomial(powers: dict[str, int]) -> tuple[int, dict[str, int]]:
        if not isinstance(powers, dict) or any(key not in generators for key in powers):
            raise ValueError("monomial contains an unknown generator")
        result, degree = {unit: 1}, 0
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
        if not relation["terms"]:
            raise ValueError("relation must have terms")
        degrees: set[int] = set()
        total: Counter[str] = Counter()
        for term in relation["terms"]:
            scalar = _integer(term["coefficient"], "relation scalar")
            if not (scalar % characteristic if characteristic else scalar):
                raise ValueError("relation scalar must be nonzero in the coefficient ring")
            degree, value = monomial(term["powers"])
            degrees.add(degree)
            for key, value_scalar in value.items():
                total[key] += scalar * value_scalar
        if len(degrees) != 1:
            raise ValueError("relation is not homogeneous")
        if normalize(dict(total)):
            raise ValueError("relation is not satisfied by the multiplication table")
