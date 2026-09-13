#!/usr/bin/env python3
"""Local Homology DB preview: owned chains, SQLite, and four QA tools.

This is a durable test drive of the validated prototype interface. It is not a
qualified 0.0.1 release and its computed rows are not release-ledger evidence.
The local database is rebuilt deterministically and may be deleted at any time.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sqlite3
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DB = Path("/tmp/homology-db-preview.sqlite3")
COEFFICIENTS = {"Z": None, "F2": 2, "F3": 3, "F5": 5, "F7": 7}
ALGORITHM_ID = "owned-smith-minors-and-modular-rank/0-preview"
SCHEMA_VERSION = "homology-db.preview/1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def dense_matrix(boundary: dict[str, Any]) -> list[list[int]]:
    matrix = [[0 for _ in range(boundary["cols"])] for _ in range(boundary["rows"])]
    for row, col, value in boundary["entries"]:
        matrix[row][col] = value
    return matrix


def rational_rank(matrix: list[list[int]]) -> int:
    if not matrix or not matrix[0]:
        return 0
    work = [[Fraction(value) for value in row] for row in matrix]
    rows, cols = len(work), len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][col]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][col]:
                continue
            scale = work[row][col]
            work[row] = [a - scale * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def modular_rank(matrix: list[list[int]], prime: int) -> int:
    if not matrix or not matrix[0]:
        return 0
    work = [[value % prime for value in row] for row in matrix]
    rows, cols = len(work), len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][col], -1, prime)
        work[pivot_row] = [(value * inverse) % prime for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][col]:
                continue
            scale = work[row][col]
            work[row] = [
                (left - scale * right) % prime
                for left, right in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def determinant(matrix: list[list[int]]) -> int:
    size = len(matrix)
    if size == 0:
        return 1
    work = [row[:] for row in matrix]
    sign, previous = 1, 1
    for pivot_index in range(size - 1):
        pivot_row = next(
            (row for row in range(pivot_index, size) if work[row][pivot_index]), None
        )
        if pivot_row is None:
            return 0
        if pivot_row != pivot_index:
            work[pivot_index], work[pivot_row] = work[pivot_row], work[pivot_index]
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for col in range(pivot_index + 1, size):
                numerator = work[row][col] * pivot - work[row][pivot_index] * work[pivot_index][col]
                work[row][col] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def smith_invariants(matrix: list[list[int]]) -> list[int]:
    """Return nonzero Smith invariants via determinantal divisors.

    This is intentionally small-matrix prototype code. It is exact, but not a
    viable release algorithm for large sparse corpus matrices.
    """
    rank = rational_rank(matrix)
    if rank == 0:
        return []
    row_count, col_count = len(matrix), len(matrix[0])
    divisors = [1]
    for size in range(1, rank + 1):
        minor_gcd = 0
        for rows in itertools.combinations(range(row_count), size):
            for cols in itertools.combinations(range(col_count), size):
                minor = [[matrix[row][col] for col in cols] for row in rows]
                minor_gcd = math.gcd(minor_gcd, abs(determinant(minor)))
        if minor_gcd == 0:
            raise ValueError("rank/minor inconsistency")
        divisors.append(minor_gcd)
    return [divisors[index] // divisors[index - 1] for index in range(1, len(divisors))]


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if not left:
        return []
    if not right:
        return [[] for _ in left]
    return [
        [sum(left[row][inner] * right[inner][col] for inner in range(len(right)))
         for col in range(len(right[0]))]
        for row in range(len(left))
    ]


def zero_boundary(rows: int, cols: int) -> dict[str, Any]:
    return {"rows": rows, "cols": cols, "entries": []}


def make_chain(ranks: dict[int, int], nonzero: dict[int, list[tuple[int, int, int]]] | None = None) -> dict[str, Any]:
    dimension = max(ranks, default=-1)
    complete_ranks = {degree: ranks.get(degree, 0) for degree in range(dimension + 1)}
    boundaries: dict[int, dict[str, Any]] = {}
    for degree in range(1, dimension + 1):
        boundary = zero_boundary(complete_ranks[degree - 1], complete_ranks[degree])
        boundary["entries"] = [list(entry) for entry in (nonzero or {}).get(degree, [])]
        boundaries[degree] = boundary
    chain = {
        "basis": {
            str(degree): [f"c{degree}:{index}" for index in range(rank)]
            for degree, rank in complete_ranks.items()
        },
        "ranks": {str(degree): rank for degree, rank in complete_ranks.items()},
        "boundaries": {str(degree): value for degree, value in boundaries.items()},
    }
    validate_chain(chain)
    return chain


def validate_chain(chain: dict[str, Any]) -> None:
    ranks = {int(key): value for key, value in chain["ranks"].items()}
    boundaries = {int(key): value for key, value in chain["boundaries"].items()}
    for degree, boundary in boundaries.items():
        if boundary["rows"] != ranks[degree - 1] or boundary["cols"] != ranks[degree]:
            raise ValueError(f"boundary {degree} shape does not match ordered bases")
        for row, col, _ in boundary["entries"]:
            if not (0 <= row < boundary["rows"] and 0 <= col < boundary["cols"]):
                raise ValueError(f"boundary {degree} entry lies outside its matrix")
    for degree in range(2, max(ranks, default=0) + 1):
        composition = multiply(dense_matrix(boundaries[degree - 1]), dense_matrix(boundaries[degree]))
        if any(value for row in composition for value in row):
            raise ValueError(f"d_{degree - 1} d_{degree} is not zero")


def compute_integral_homology(chain: dict[str, Any], declared_dimension: int) -> list[dict[str, Any]]:
    ranks = {int(key): value for key, value in chain["ranks"].items()}
    boundaries = {int(key): value for key, value in chain["boundaries"].items()}
    results = []
    for degree in range(declared_dimension + 1):
        chain_rank = ranks.get(degree, 0)
        down = dense_matrix(boundaries.get(degree, zero_boundary(ranks.get(degree - 1, 0), chain_rank)))
        up = dense_matrix(boundaries.get(degree + 1, zero_boundary(chain_rank, ranks.get(degree + 1, 0))))
        down_rank, up_rank = rational_rank(down), rational_rank(up)
        if down_rank and up_rank:
            raise NotImplementedError(
                "prototype only supports separated nonzero boundaries; release needs kernel-basis transforms"
            )
        smith = smith_invariants(up)
        results.append({
            "degree": degree,
            "free_rank": chain_rank - down_rank - up_rank,
            "torsion_orders": [value for value in smith if value > 1],
            "smith_diagonal_of_incoming_boundary": smith,
            "representatives": (
                {"state": "exact", "basis": chain["basis"].get(str(degree), [])}
                if down_rank == 0 and up_rank == 0
                else {"state": "not_computed", "reason": "smith_basis_transforms_not_captured"}
            ),
        })
    return results


def compute_field_homology(chain: dict[str, Any], declared_dimension: int, prime: int) -> list[dict[str, Any]]:
    ranks = {int(key): value for key, value in chain["ranks"].items()}
    boundaries = {int(key): value for key, value in chain["boundaries"].items()}
    output = []
    for degree in range(declared_dimension + 1):
        chain_rank = ranks.get(degree, 0)
        down = dense_matrix(boundaries.get(degree, zero_boundary(ranks.get(degree - 1, 0), chain_rank)))
        up = dense_matrix(boundaries.get(degree + 1, zero_boundary(chain_rank, ranks.get(degree + 1, 0))))
        dimension = chain_rank - modular_rank(down, prime) - modular_rank(up, prime)
        output.append({"degree": degree, "dimension": dimension})
    return output


def prime_parts(order: int) -> Iterable[tuple[int, int]]:
    divisor = 2
    while divisor * divisor <= order:
        exponent = 0
        while order % divisor == 0:
            exponent += 1
            order //= divisor
        if exponent:
            yield divisor, exponent
        divisor += 1
    if order > 1:
        yield order, 1


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    return all(value % divisor for divisor in range(2, math.isqrt(value) + 1))


def manifold_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []

    def add(key: str, label: str, family: str, dimension: int, ranks: dict[int, int],
            nonzero: dict[int, list[tuple[int, int, int]]] | None = None,
            aliases: list[str] | None = None, equivalence: str = "cellular_model") -> None:
        specs.append({
            "key": key, "label": label, "family": family, "dimension": dimension,
            "chain": make_chain(ranks, nonzero), "aliases": aliases or [],
            "equivalence": equivalence,
        })

    for n in range(1, 9):
        add(f"sphere:{n}", f"Sphere S^{n}", "sphere", n, {0: 1, n: 1},
            aliases=[f"S^{n}", f"S{n}"])
    for genus in range(2, 10):
        add(f"orientable_surface:{genus}", f"Orientable surface genus {genus}",
            "orientable_surface", 2, {0: 1, 1: 2 * genus, 2: 1}, aliases=[f"Sigma_{genus}"])
    for genus in range(2, 10):
        entries = [(row, 0, 2) for row in range(genus)]
        aliases = [f"N_{genus}"] + (["Klein bottle"] if genus == 2 else [])
        add(f"nonorientable_surface:{genus}", f"Nonorientable surface genus {genus}",
            "nonorientable_surface", 2, {0: 1, 1: genus, 2: 1}, {2: entries}, aliases)
    for n in range(2, 6):
        add(f"torus:{n}", f"Torus T^{n}", "torus", n,
            {degree: math.comb(n, degree) for degree in range(n + 1)}, aliases=[f"T^{n}", f"T{n}"])
    for n in (2, 4, 5, 6):
        nonzero = {degree: [(0, 0, 2)] for degree in range(2, n + 1, 2)}
        add(f"real_projective_space:{n}", f"Real projective space RP^{n}",
            "real_projective_space", n, {degree: 1 for degree in range(n + 1)},
            nonzero, aliases=[f"RP^{n}", f"RP{n}"])
    lens_pairs = [(3, 1), (4, 1), (5, 1), (5, 2), (6, 1), (7, 1),
                  (7, 2), (8, 1), (8, 3), (9, 1), (9, 2), (10, 1)]
    for p, q in lens_pairs:
        add(f"lens:{p}:{q}", f"Lens space L({p},{q})", "lens_space", 3,
            {0: 1, 1: 1, 2: 1, 3: 1}, {2: [(0, 0, p)]}, aliases=[f"L({p},{q})", f"L{p}_{q}"])
    sphere_pairs = [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 2), (2, 3), (2, 4)]
    for a, b in sphere_pairs:
        ranks: dict[int, int] = {0: 1}
        for degree in (a, b, a + b):
            ranks[degree] = ranks.get(degree, 0) + 1
        add(f"sphere_product:{a}:{b}", f"Sphere product S^{a} x S^{b}",
            "sphere_product", a + b, ranks, aliases=[f"S^{a} x S^{b}"])
    for n in range(1, 5):
        add(f"disk:{n}", f"Disk D^{n}", "disk", n, {0: 1}, aliases=[f"D^{n}", f"D{n}"],
            equivalence="homotopy_equivalent_chain_model")
    for genus in range(2, 6):
        add(f"orientable_surface_circle:{genus}", f"Orientable surface genus {genus} x S^1",
            "orientable_surface_circle", 3,
            {0: 1, 1: 2 * genus + 1, 2: 2 * genus + 1, 3: 1},
            aliases=[f"Sigma_{genus} x S^1"])
    if len(specs) != 60:
        raise AssertionError(f"expected 60 QA subjects, generated {len(specs)}")
    return specs


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE snapshot(snapshot_id TEXT PRIMARY KEY, schema_version TEXT NOT NULL, corpus_count INTEGER NOT NULL);
CREATE TABLE space(space_id TEXT PRIMARY KEY, label TEXT NOT NULL, family TEXT NOT NULL, dimension INTEGER NOT NULL, equivalence_kind TEXT NOT NULL, chain_sha256 TEXT NOT NULL);
CREATE TABLE alias(normalized_alias TEXT NOT NULL, space_id TEXT NOT NULL REFERENCES space(space_id), display_alias TEXT NOT NULL, PRIMARY KEY(normalized_alias, space_id));
CREATE INDEX alias_space_idx ON alias(space_id);
CREATE TABLE evidence(evidence_id TEXT PRIMARY KEY, space_id TEXT NOT NULL REFERENCES space(space_id), algorithm_id TEXT NOT NULL, chain_sha256 TEXT NOT NULL, chain_json TEXT NOT NULL, representatives_state TEXT NOT NULL, induced_maps_state TEXT NOT NULL);
CREATE TABLE homology(assertion_id TEXT PRIMARY KEY, snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id), space_id TEXT NOT NULL REFERENCES space(space_id), coefficient TEXT NOT NULL, reduced INTEGER NOT NULL, degree INTEGER NOT NULL, free_rank INTEGER NOT NULL, torsion_json TEXT NOT NULL, knowledge_state TEXT NOT NULL, value_scope TEXT NOT NULL, evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id), UNIQUE(snapshot_id, space_id, coefficient, reduced, degree));
CREATE INDEX homology_lookup_idx ON homology(snapshot_id, space_id, coefficient, reduced, degree);
CREATE INDEX homology_pattern_idx ON homology(snapshot_id, coefficient, reduced, degree, free_rank);
CREATE TABLE primary_summand(assertion_id TEXT NOT NULL REFERENCES homology(assertion_id), prime INTEGER NOT NULL, exponent INTEGER NOT NULL, multiplicity INTEGER NOT NULL, PRIMARY KEY(assertion_id, prime, exponent));
CREATE INDEX primary_query_idx ON primary_summand(prime, exponent, multiplicity, assertion_id);
"""


def build_database(path: Path) -> str:
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    specs = manifold_specs()
    snapshot_payload = [{"space": spec["key"], "chain": digest(spec["chain"])} for spec in specs]
    snapshot_id = f"preview-{digest(snapshot_payload)[:16]}"
    connection.execute("INSERT INTO snapshot VALUES (?, ?, ?)", (snapshot_id, SCHEMA_VERSION, len(specs)))
    for spec in specs:
        chain_hash = digest(spec["chain"])
        connection.execute("INSERT INTO space VALUES (?, ?, ?, ?, ?, ?)",
                           (spec["key"], spec["label"], spec["family"], spec["dimension"], spec["equivalence"], chain_hash))
        for alias in {spec["key"], spec["label"], *spec["aliases"]}:
            connection.execute("INSERT OR IGNORE INTO alias VALUES (?, ?, ?)",
                               (normalize_name(alias), spec["key"], alias))
        integral = compute_integral_homology(spec["chain"], spec["dimension"])
        evidence_id = f"preview:evidence:{spec['key']}"
        representative_states = {item["representatives"]["state"] for item in integral}
        connection.execute("INSERT INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (evidence_id, spec["key"], ALGORITHM_ID, chain_hash,
                            canonical_json(spec["chain"]),
                            "exact_or_explicit_not_computed:" + ",".join(sorted(representative_states)),
                            "identity_only;nonidentity_not_computed"))
        coefficient_rows: dict[str, list[dict[str, Any]]] = {"Z": integral}
        for coefficient, prime in COEFFICIENTS.items():
            if prime is not None:
                coefficient_rows[coefficient] = compute_field_homology(
                    spec["chain"], spec["dimension"], prime
                )
        for coefficient, rows in coefficient_rows.items():
            for reduced in (False, True):
                for row in rows:
                    degree = row["degree"]
                    free_rank = row.get("free_rank", row.get("dimension", 0))
                    torsion = row.get("torsion_orders", []) if coefficient == "Z" else []
                    if reduced and degree == 0:
                        free_rank = max(0, free_rank - 1)
                    assertion_id = f"preview:assertion:{spec['key']}:{coefficient}:{'r' if reduced else 'u'}:{degree}"
                    connection.execute(
                        "INSERT INTO homology VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'exact', 'complete_group', ?)",
                        (assertion_id, snapshot_id, spec["key"], coefficient, int(reduced), degree,
                         free_rank, canonical_json(torsion), evidence_id),
                    )
                    if coefficient == "Z":
                        counts: dict[tuple[int, int], int] = {}
                        for order in torsion:
                            for prime, exponent in prime_parts(order):
                                counts[(prime, exponent)] = counts.get((prime, exponent), 0) + 1
                        for (prime, exponent), multiplicity in counts.items():
                            connection.execute("INSERT INTO primary_summand VALUES (?, ?, ?, ?)",
                                               (assertion_id, prime, exponent, multiplicity))
    connection.commit()
    connection.close()
    return snapshot_id


class PreviewDatabase:
    """One-operation builder for the disposable, immutable preview Snapshot."""

    @staticmethod
    def build(path: Path = DEFAULT_DB) -> str:
        return build_database(path)


class Tools:
    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.snapshot_id = self.connection.execute("SELECT snapshot_id FROM snapshot").fetchone()[0]

    def corpus_summary(self) -> dict[str, Any]:
        subject_count = self.connection.execute("SELECT corpus_count FROM snapshot").fetchone()[0]
        return {
            "snapshot_id": self.snapshot_id,
            "subject_count": subject_count,
            "supported_tools": ["resolve_subject", "read_homology", "query_examples", "expand_evidence"],
            "release_status": "local_preview_not_release_evidence",
        }

    def resolve_subject(self, query: str) -> dict[str, Any]:
        if not isinstance(query, str) or not query.strip():
            return {"tool": "resolve_subject", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": "query must be a nonempty string"}
        normalized = normalize_name(query)
        rows = self.connection.execute(
            "SELECT DISTINCT s.space_id, s.label, s.family FROM alias a JOIN space s USING(space_id) WHERE a.normalized_alias = ? ORDER BY s.space_id",
            (normalized,),
        ).fetchall()
        if not rows:
            rows = self.connection.execute(
                "SELECT DISTINCT s.space_id, s.label, s.family FROM alias a JOIN space s USING(space_id) WHERE a.normalized_alias LIKE ? ORDER BY s.label LIMIT 8",
                (f"%{normalized}%",),
            ).fetchall()
            return {"tool": "resolve_subject", "snapshot_id": self.snapshot_id,
                    "outcome": "not_found", "suggestions": [dict(row) for row in rows]}
        return {"tool": "resolve_subject", "snapshot_id": self.snapshot_id,
                "outcome": "resolved" if len(rows) == 1 else "ambiguous",
                "candidates": [dict(row) for row in rows]}

    def read_homology(self, subject: str, coefficient: str = "Z", reduced: bool = False) -> dict[str, Any]:
        if not isinstance(subject, str) or not subject.strip():
            return {"tool": "read_homology", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": "subject must be a nonempty string"}
        if not isinstance(coefficient, str):
            return {"tool": "read_homology", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": "coefficient must be a string"}
        if not isinstance(reduced, bool):
            return {"tool": "read_homology", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": "reduced must be a boolean"}
        if coefficient not in COEFFICIENTS:
            return {"tool": "read_homology", "snapshot_id": self.snapshot_id,
                    "outcome": "unsupported_coefficient", "supported": list(COEFFICIENTS)}
        resolution = self.resolve_subject(subject)
        if resolution["outcome"] != "resolved":
            return {"tool": "read_homology", "snapshot_id": self.snapshot_id,
                    "outcome": "subject_not_resolved", "resolution": resolution}
        space_id = resolution["candidates"][0]["space_id"]
        space = dict(self.connection.execute("SELECT * FROM space WHERE space_id = ?", (space_id,)).fetchone())
        rows = self.connection.execute(
            "SELECT assertion_id, degree, free_rank, torsion_json, knowledge_state, value_scope, evidence_id FROM homology WHERE snapshot_id = ? AND space_id = ? AND coefficient = ? AND reduced = ? ORDER BY degree",
            (self.snapshot_id, space_id, coefficient, int(reduced)),
        ).fetchall()
        groups = []
        for row in rows:
            torsion = json.loads(row["torsion_json"])
            if coefficient == "Z":
                display_parts = (["Z"] * row["free_rank"]) + [f"Z/{order}" for order in torsion]
                display = "0" if not display_parts else " + ".join(display_parts)
                value = {"free_rank": row["free_rank"], "torsion_orders": torsion, "display": display}
            else:
                value = {"dimension": row["free_rank"], "display": "0" if row["free_rank"] == 0 else coefficient + (f"^{row['free_rank']}" if row["free_rank"] > 1 else "")}
            groups.append({"degree": row["degree"], "value": value, "knowledge_state": row["knowledge_state"],
                           "value_scope": row["value_scope"], "assertion_id": row["assertion_id"],
                           "evidence_id": row["evidence_id"]})
        return {"tool": "read_homology", "snapshot_id": self.snapshot_id, "outcome": "selected",
                "subject": space, "coefficient": coefficient, "reduced": reduced,
                "groups": groups, "upper_vanishing_starts_at": space["dimension"] + 1}

    def query_examples(self, pattern: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(pattern, dict):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": "pattern must be a JSON object"}
        allowed = {"family", "coefficient", "reduced", "degree", "torsion_prime",
                   "contains_torsion_order", "free_rank_at_least", "limit"}
        unknown = set(pattern) - allowed
        if unknown:
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "unknown_fields": sorted(unknown)}
        if "family" in pattern and (
            not isinstance(pattern["family"], str) or not pattern["family"]
        ):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "family must be a nonempty string"}
        if "coefficient" in pattern and not isinstance(pattern["coefficient"], str):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "coefficient must be a string"}
        if "reduced" in pattern and not isinstance(pattern["reduced"], bool):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "reduced must be a boolean"}
        if "degree" in pattern and (
            not isinstance(pattern["degree"], int)
            or isinstance(pattern["degree"], bool)
            or pattern["degree"] < 0
        ):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "degree must be a nonnegative integer"}
        if "torsion_prime" in pattern and (
            not isinstance(pattern["torsion_prime"], int)
            or isinstance(pattern["torsion_prime"], bool)
            or not is_prime(pattern["torsion_prime"])
        ):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "torsion_prime must be a prime integer"}
        if "limit" in pattern and (
            not isinstance(pattern["limit"], int)
            or isinstance(pattern["limit"], bool)
            or not 1 <= pattern["limit"] <= 100
        ):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "limit must be an integer from 1 through 100"}
        if "contains_torsion_order" in pattern and (
            not isinstance(pattern["contains_torsion_order"], int)
            or isinstance(pattern["contains_torsion_order"], bool)
            or pattern["contains_torsion_order"] <= 1
        ):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "contains_torsion_order must be an integer greater than 1"}
        if "free_rank_at_least" in pattern and (
            not isinstance(pattern["free_rank_at_least"], int)
            or isinstance(pattern["free_rank_at_least"], bool)
            or pattern["free_rank_at_least"] < 0
        ):
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern", "reason": "free_rank_at_least must be a nonnegative integer"}
        coefficient = pattern.get("coefficient", "Z")
        if coefficient not in COEFFICIENTS:
            return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                    "outcome": "unsupported_coefficient", "supported": list(COEFFICIENTS)}
        clauses = ["h.snapshot_id = ?", "h.coefficient = ?", "h.reduced = ?"]
        parameters: list[Any] = [self.snapshot_id, coefficient, int(pattern.get("reduced", False))]
        joins = ""
        if "family" in pattern:
            clauses.append("s.family = ?")
            parameters.append(pattern["family"])
        if "degree" in pattern:
            clauses.append("h.degree = ?")
            parameters.append(int(pattern["degree"]))
        if "free_rank_at_least" in pattern:
            clauses.append("h.free_rank >= ?")
            parameters.append(int(pattern["free_rank_at_least"]))
        if "torsion_prime" in pattern:
            if coefficient != "Z":
                return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                        "outcome": "invalid_pattern", "reason": "torsion filters require coefficient Z"}
            joins += " JOIN primary_summand p ON p.assertion_id = h.assertion_id"
            clauses.append("p.prime = ?")
            parameters.append(int(pattern["torsion_prime"]))
        if "contains_torsion_order" in pattern:
            if coefficient != "Z":
                return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                        "outcome": "invalid_pattern", "reason": "torsion filters require coefficient Z"}
            clauses.append("EXISTS (SELECT 1 FROM json_each(h.torsion_json) WHERE value = ?)")
            parameters.append(int(pattern["contains_torsion_order"]))
        selected_columns = (
            "s.space_id, s.label, s.family, h.degree, h.free_rank, "
            "h.torsion_json, h.assertion_id, h.evidence_id"
        )
        from_where = (
            " FROM homology h JOIN space s USING(space_id)" + joins
            + " WHERE " + " AND ".join(clauses)
        )
        total_matches = self.connection.execute(
            "SELECT COUNT(*) FROM (SELECT DISTINCT " + selected_columns
            + from_where + ") AS candidates",
            parameters,
        ).fetchone()[0]
        limit = pattern.get("limit", 20)
        rows = self.connection.execute(
            "SELECT DISTINCT " + selected_columns + from_where
            + " ORDER BY s.family, s.label, h.degree LIMIT ?",
            (*parameters, limit),
        ).fetchall()
        matches = []
        for row in rows:
            torsion = json.loads(row["torsion_json"])
            matches.append({**dict(row), "torsion_orders": torsion})
            matches[-1].pop("torsion_json")
        subject_count = self.connection.execute(
            "SELECT corpus_count FROM snapshot WHERE snapshot_id = ?", (self.snapshot_id,)
        ).fetchone()[0]
        return {"tool": "query_examples", "snapshot_id": self.snapshot_id,
                "outcome": "proven_matches", "pattern": pattern, "matches": matches,
                "total_matches": total_matches, "truncated": len(matches) < total_matches,
                "coverage": {"scope": "selected_snapshot_assertions",
                             "subject_count": subject_count, "globally_exhaustive": False},
                "unresolved_candidates": []}

    def expand_evidence(self, evidence_ids: list[str]) -> dict[str, Any]:
        if not isinstance(evidence_ids, list) or not evidence_ids:
            return {"tool": "expand_evidence", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": "evidence_ids must be a nonempty array"}
        if any(not isinstance(evidence_id, str) or not evidence_id for evidence_id in evidence_ids):
            return {"tool": "expand_evidence", "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": "every evidence_id must be a nonempty string"}
        placeholders = ",".join("?" for _ in evidence_ids)
        rows = self.connection.execute(
            f"SELECT evidence_id, space_id, algorithm_id, chain_sha256, representatives_state, induced_maps_state FROM evidence WHERE evidence_id IN ({placeholders}) ORDER BY evidence_id",
            evidence_ids,
        ).fetchall()
        found = {row["evidence_id"] for row in rows}
        return {"tool": "expand_evidence", "snapshot_id": self.snapshot_id,
                "outcome": "complete" if found == set(evidence_ids) else "partial",
                "evidence": [dict(row) for row in rows],
                "missing_evidence_ids": sorted(set(evidence_ids) - found)}

    def call(self, request: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(request, dict):
            return {"outcome": "invalid_request", "snapshot_id": self.snapshot_id,
                    "reason": "tool request must be a JSON object"}
        tool = request.get("tool")
        arguments = request.get("arguments", {})
        if not isinstance(arguments, dict):
            return {"tool": tool, "outcome": "invalid_request", "snapshot_id": self.snapshot_id,
                    "reason": "arguments must be a JSON object"}
        dispatch = {
            "resolve_subject": self.resolve_subject,
            "read_homology": self.read_homology,
            "query_examples": self.query_examples,
            "expand_evidence": self.expand_evidence,
        }
        if tool is None:
            return {"outcome": "invalid_request", "snapshot_id": self.snapshot_id,
                    "reason": "tool is required"}
        if not isinstance(tool, str):
            return {"outcome": "invalid_request", "snapshot_id": self.snapshot_id,
                    "reason": "tool must be a string"}
        if tool not in dispatch:
            return {"tool": tool, "outcome": "unknown_tool", "snapshot_id": self.snapshot_id,
                    "supported_tools": sorted(dispatch)}
        try:
            return dispatch[tool](**arguments)
        except (TypeError, ValueError) as error:
            return {"tool": tool, "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_request", "reason": str(error)}


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def demo(path: Path) -> None:
    snapshot_id = build_database(path)
    tools = Tools(path)
    print(f"Homology DB local preview ready: 60 subjects, snapshot {snapshot_id}")
    print(f"Scratch database: {path} (safe to delete; rebuilt on every run)\n")
    klein = tools.read_homology("Klein bottle", coefficient="Z")
    klein_groups = "; ".join(
        f"H_{group['degree']} = {group['value']['display']}" for group in klein["groups"]
    )
    rp4 = tools.read_homology("RP^4", coefficient="F2")
    rp4_degrees = ", ".join(str(group["degree"]) for group in rp4["groups"] if group["value"]["dimension"])
    search = tools.query_examples({"degree": 1, "torsion_prime": 5, "limit": 8})
    labels = ", ".join(match["label"] for match in search["matches"])
    evidence_id = klein["groups"][1]["evidence_id"]
    evidence = tools.expand_evidence([evidence_id])["evidence"][0]

    print("Quick mathematical tour")
    print(f"  Klein bottle: {klein_groups}")
    print(f"  RP^4 over F2: one generator in degrees {rp4_degrees}")
    print(f"  Proven H_1 examples with 5-primary torsion: {labels}")
    print(f"  Evidence algorithm: {evidence['algorithm_id']}")
    print("  Capability: group structure exact; some representative bases and nonidentity maps not computed")
    print("  All returned groups name assertion and evidence IDs from this one snapshot.\n")

    request = {"tool": "read_homology", "arguments": {"subject": "Klein bottle", "coefficient": "Z"}}
    print("Agent interface")
    print("  The same four tools return stable JSON: resolve_subject, read_homology,")
    print("  query_examples, and expand_evidence.")
    print("  Try:")
    print(f"  python3 -m homology_db tool '{canonical_json(request)}'")
    print("\nThis is a local preview, not the qualified 0.0.1 release.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Local Homology DB test drive")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="disposable SQLite path")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="rebuild the 60-subject snapshot and show four calls")
    tool_parser = subparsers.add_parser("tool", help="execute one stable JSON tool request")
    tool_parser.add_argument("request", help='JSON object with "tool" and "arguments"')
    args = parser.parse_args()
    if args.command == "demo":
        demo(args.db)
        return 0
    if not args.db.exists():
        PreviewDatabase.build(args.db)
    with sqlite3.connect(args.db) as connection:
        snapshot_id = connection.execute("SELECT snapshot_id FROM snapshot").fetchone()[0]
    try:
        request = json.loads(args.request)
    except json.JSONDecodeError as error:
        print_json({"outcome": "invalid_json", "snapshot_id": snapshot_id,
                    "reason": str(error)})
        return 2
    print_json(Tools(args.db).call(request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
