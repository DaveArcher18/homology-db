#!/usr/bin/env python3
"""Curated finite-CW corpus for the public Chromatic Homology Atlas.

The historical ``preview`` module remains frozen as a replayable audit fixture.
This module is the current product database: a manifest-driven, disposable
SQLite Snapshot whose cellular chains, models, references, and computations are
all materialized together.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path
from typing import Any

from .preview import (
    COEFFICIENTS,
    canonical_json,
    compute_integral_homology,
    digest,
    is_prime,
    make_chain,
    normalize_name,
    prime_parts,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "corpus" / "chromatic-v1" / "manifest.json"
DEFAULT_DB = Path("/tmp/homology-db-chromatic.sqlite3")
SCHEMA_VERSION = "homology-db.chromatic/1"
ALGORITHM_ID = "owned-cellular-smith-and-modular-rank/1"
RELEASE_STATUS = "development_corpus_not_external_reviewed"


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE snapshot(
    snapshot_id TEXT PRIMARY KEY,
    snapshot_name TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    corpus_count INTEGER NOT NULL,
    manifest_sha256 TEXT NOT NULL,
    scope_note TEXT NOT NULL,
    materialized_through_degree INTEGER NOT NULL
);
CREATE TABLE family(
    family_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    summary TEXT NOT NULL,
    chromatic_relevance TEXT NOT NULL,
    sort_order INTEGER NOT NULL UNIQUE
);
CREATE TABLE reference(
    reference_id TEXT PRIMARY KEY,
    authors_json TEXT NOT NULL,
    title TEXT NOT NULL,
    publication_year INTEGER NOT NULL,
    url TEXT NOT NULL,
    source_kind TEXT NOT NULL
);
CREATE TABLE space(
    space_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    family TEXT NOT NULL REFERENCES family(family_id),
    dimension INTEGER,
    infinite_finite_type INTEGER NOT NULL,
    connected_components INTEGER NOT NULL,
    parameters_json TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    summary TEXT NOT NULL,
    chromatic_relevance TEXT NOT NULL,
    equivalence_kind TEXT NOT NULL,
    chain_sha256 TEXT NOT NULL
);
CREATE TABLE alias(
    normalized_alias TEXT NOT NULL,
    space_id TEXT NOT NULL REFERENCES space(space_id),
    display_alias TEXT NOT NULL,
    PRIMARY KEY(normalized_alias, space_id)
);
CREATE INDEX alias_space_idx ON alias(space_id);
CREATE TABLE model(
    model_id TEXT PRIMARY KEY,
    space_id TEXT NOT NULL REFERENCES space(space_id),
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    name TEXT NOT NULL,
    construction TEXT NOT NULL,
    cell_degrees_json TEXT NOT NULL,
    cell_formula TEXT,
    attaching_map TEXT NOT NULL,
    boundary_formula TEXT NOT NULL,
    chain_sha256 TEXT NOT NULL,
    model_scope TEXT NOT NULL,
    artifact_path TEXT,
    artifact_sha256 TEXT,
    UNIQUE(space_id)
);
CREATE TABLE evidence(
    evidence_id TEXT PRIMARY KEY,
    space_id TEXT NOT NULL REFERENCES space(space_id),
    model_id TEXT NOT NULL REFERENCES model(model_id),
    evidence_kind TEXT NOT NULL,
    algorithm_id TEXT NOT NULL,
    chain_sha256 TEXT NOT NULL,
    chain_json TEXT NOT NULL,
    computation_sketch TEXT NOT NULL,
    reliability TEXT NOT NULL,
    representatives_state TEXT NOT NULL,
    induced_maps_state TEXT NOT NULL
);
CREATE TABLE evidence_reference(
    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
    reference_id TEXT NOT NULL REFERENCES reference(reference_id),
    role TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(evidence_id, reference_id, role, locator)
);
CREATE TABLE computation_run(
    computation_id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
    algorithm_id TEXT NOT NULL,
    input_sha256 TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    output_scope TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE homology_coverage(
    space_id TEXT PRIMARY KEY REFERENCES space(space_id),
    coverage_kind TEXT NOT NULL,
    computed_through_degree INTEGER NOT NULL,
    upper_vanishing_starts_at INTEGER,
    detail TEXT NOT NULL
);
CREATE TABLE homology(
    assertion_id TEXT PRIMARY KEY,
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    space_id TEXT NOT NULL REFERENCES space(space_id),
    coefficient TEXT NOT NULL,
    reduced INTEGER NOT NULL,
    degree INTEGER NOT NULL,
    free_rank INTEGER NOT NULL,
    torsion_json TEXT NOT NULL,
    knowledge_state TEXT NOT NULL,
    value_scope TEXT NOT NULL,
    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
    UNIQUE(snapshot_id, space_id, coefficient, reduced, degree)
);
CREATE INDEX homology_lookup_idx
    ON homology(snapshot_id, space_id, coefficient, reduced, degree);
CREATE INDEX homology_pattern_idx
    ON homology(snapshot_id, coefficient, reduced, degree, free_rank);
CREATE TABLE primary_summand(
    assertion_id TEXT NOT NULL REFERENCES homology(assertion_id),
    prime INTEGER NOT NULL,
    exponent INTEGER NOT NULL,
    multiplicity INTEGER NOT NULL,
    PRIMARY KEY(assertion_id, prime, exponent)
);
CREATE INDEX primary_query_idx
    ON primary_summand(prime, exponent, multiplicity, assertion_id);
"""


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "homology-db.chromatic-corpus/2":
        raise ValueError("unsupported chromatic corpus manifest version")
    bound = manifest.get("materialized_through_degree")
    if not isinstance(bound, int) or isinstance(bound, bool) or bound < 1:
        raise ValueError("chromatic corpus needs a positive materialization bound")
    reference_ids = [reference["id"] for reference in manifest["references"]]
    if len(reference_ids) != len(set(reference_ids)):
        raise ValueError("chromatic corpus contains duplicate reference IDs")
    known_references = set(reference_ids)
    for reference in manifest["references"]:
        if (
            not isinstance(reference.get("authors"), list)
            or not reference["authors"]
            or not all(
                isinstance(author, str) and author.strip()
                for author in reference["authors"]
            )
            or not isinstance(reference.get("title"), str)
            or not reference["title"].strip()
            or not isinstance(reference.get("year"), int)
            or isinstance(reference["year"], bool)
            or not isinstance(reference.get("url"), str)
            or not reference["url"].startswith("https://")
            or not isinstance(reference.get("source_kind"), str)
            or not reference["source_kind"].strip()
        ):
            raise ValueError(f"reference {reference.get('id')} is malformed")
    family_ids = [family["id"] for family in manifest["families"]]
    if len(family_ids) != len(set(family_ids)):
        raise ValueError("chromatic corpus contains duplicate family IDs")
    used_references: set[str] = set()
    for family in manifest["families"]:
        if not all(
            isinstance(family.get(field), str) and bool(family[field].strip())
            for field in (
                "id",
                "label",
                "summary",
                "chromatic_relevance",
                "model_formula",
            )
        ):
            raise ValueError(f"family {family.get('id')} is malformed")
        if not family.get("sources"):
            raise ValueError(f"family {family['id']} has no source")
        for source in family["sources"]:
            if source["reference_id"] not in known_references:
                raise ValueError(
                    f"family {family['id']} cites unknown reference "
                    f"{source['reference_id']}"
                )
            if not all(
                isinstance(source.get(field), str) and bool(source[field].strip())
                for field in ("role", "locator")
            ):
                raise ValueError(f"family {family['id']} has malformed source data")
            applies_to = source.get("applies_to", {})
            if not isinstance(applies_to, dict) or any(
                not isinstance(key, str) for key in applies_to
            ):
                raise ValueError(
                    f"family {family['id']} has malformed source applicability"
                )
            used_references.add(source["reference_id"])
    if used_references != known_references:
        raise ValueError(
            "chromatic corpus has unused references: "
            + ", ".join(sorted(known_references - used_references))
        )
    artifact_paths: set[str] = set()
    for artifact in manifest.get("artifacts", []):
        artifact_path_text = artifact.get("path")
        artifact_sha256 = artifact.get("sha256")
        if (
            not isinstance(artifact_path_text, str)
            or artifact_path_text in artifact_paths
            or not isinstance(artifact_sha256, str)
            or len(artifact_sha256) != 64
            or any(character not in "0123456789abcdef" for character in artifact_sha256)
            or artifact.get("reference_id") not in known_references
        ):
            raise ValueError("chromatic corpus has malformed artifact metadata")
        artifact_paths.add(artifact_path_text)
        artifact_path = (REPOSITORY_ROOT / artifact_path_text).resolve()
        if not artifact_path.is_relative_to(REPOSITORY_ROOT) or not artifact_path.is_file():
            raise ValueError(f"chromatic corpus artifact is unresolved: {artifact_path_text}")
        if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != artifact_sha256:
            raise ValueError(f"chromatic corpus artifact hash mismatch: {artifact_path_text}")
    return manifest


def _parameter_instances(family: dict[str, Any]) -> list[dict[str, Any]]:
    if "instances" in family:
        return [dict(instance) for instance in family["instances"]]
    parameters = family["parameters"]
    order = family.get("parameter_order", list(parameters))
    if set(order) != set(parameters):
        raise ValueError(f"family {family['id']} has inconsistent parameter order")
    return [
        dict(zip(order, values, strict=True))
        for values in itertools.product(*(parameters[name] for name in order))
    ]


def _cell_degrees(ranks: dict[int, int]) -> list[dict[str, int]]:
    return [
        {"degree": degree, "count": count}
        for degree, count in sorted(ranks.items())
        if count
    ]


def _applicable_sources(
    family: dict[str, Any], parameters: dict[str, Any]
) -> list[dict[str, str]]:
    sources = []
    for source in family["sources"]:
        applies_to = source.get("applies_to", {})
        if all(parameters.get(key) == value for key, value in applies_to.items()):
            sources.append(
                {
                    "reference_id": source["reference_id"],
                    "role": source["role"],
                    "locator": source["locator"],
                }
            )
    return sources


def _base_spec(
    family: dict[str, Any],
    parameters: dict[str, Any],
    *,
    key: str,
    label: str,
    dimension: int | None,
    aliases: list[str],
    ranks: dict[int, int],
    nonzero: dict[int, list[tuple[int, int, int]]] | None,
    attaching_map: str,
    boundary_formula: str,
    computation_sketch: str,
    tags: list[str],
    computed_through_degree: int | None = None,
    connected_components: int = 1,
    model_kind: str = "finite_cw",
    model_status: str = "qualified",
    construction: str | None = None,
    cell_formula: str | None = None,
    model_cell_degrees: list[dict[str, int]] | None = None,
    model_scope: str | None = None,
    artifact_path: str | None = None,
    artifact_sha256: str | None = None,
    chain_override: dict[str, Any] | None = None,
    integral_override: list[dict[str, Any]] | None = None,
    evidence_kind: str = "owned_computation",
    algorithm_id: str = ALGORITHM_ID,
    run_recorded: bool = True,
) -> dict[str, Any]:
    chain = chain_override or make_chain(ranks, nonzero)
    chain_sha256 = digest(chain)
    model_id = f"cw:{key}"
    infinite_finite_type = dimension is None
    if computed_through_degree is None:
        if dimension is None:
            raise ValueError(f"finite-type space {key} needs a materialization bound")
        computed_through_degree = dimension
    coverage_kind = (
        "bounded_through_degree"
        if infinite_finite_type
        else "complete_finite_cw"
    )
    return {
        "key": key,
        "label": label,
        "family": family["id"],
        "dimension": dimension,
        "infinite_finite_type": infinite_finite_type,
        "connected_components": connected_components,
        "computed_through_degree": computed_through_degree,
        "coverage_kind": coverage_kind,
        "upper_vanishing_starts_at": (
            None if infinite_finite_type else dimension + 1
        ),
        "parameters": parameters,
        "aliases": aliases,
        "tags": sorted(
            {
                "finite_type_cw" if infinite_finite_type else "finite_cw",
                "chromatic_gateway",
                *tags,
            }
        ),
        "summary": family["summary"],
        "chromatic_relevance": family["chromatic_relevance"],
        "equivalence": "homeomorphic_cw_model",
        "chain": chain,
        "model": {
            "id": model_id,
            "kind": model_kind,
            "status": model_status,
            "name": f"Standard CW model for {label}",
            "construction": construction or attaching_map,
            "cell_degrees": model_cell_degrees or _cell_degrees(ranks),
            "cell_formula": cell_formula,
            "attaching_map": attaching_map,
            "boundary_formula": boundary_formula,
            "chain_sha256": chain_sha256,
            "model_scope": model_scope
            or (
                "The construction and CW cells are explicit. The calculation chain "
                "records cellular incidence degrees; attaching data remains separately "
                "identified because a boundary matrix is not a complete CW model."
            ),
            "artifact_path": artifact_path,
            "artifact_sha256": artifact_sha256,
        },
        "sources": _applicable_sources(family, parameters),
        "computation_sketch": computation_sketch,
        "integral_override": integral_override,
        "evidence_kind": evidence_kind,
        "algorithm_id": algorithm_id,
        "run_recorded": run_recorded,
    }


def _integral_rows(
    maximum_degree: int,
    groups: dict[int, tuple[int, list[int]]],
) -> list[dict[str, Any]]:
    return [
        {
            "degree": degree,
            "free_rank": groups.get(degree, (0, []))[0],
            "torsion_orders": list(groups.get(degree, (0, []))[1]),
            "smith_diagonal_of_incoming_boundary": [],
            "representatives": {
                "state": "not_computed",
                "reason": "formula_or_cited_model_does_not_retain_basis_transforms",
            },
        }
        for degree in range(maximum_degree + 1)
    ]


def _partition_count(total: int, maximum_part: int) -> int:
    counts = [0] * (total + 1)
    counts[0] = 1
    for part in range(1, maximum_part + 1):
        for value in range(part, total + 1):
            counts[value] += counts[value - part]
    return counts[total]


def _compositions(total: int, length: int) -> list[tuple[int, ...]]:
    if length == 1:
        return [(total,)]
    return [
        (first, *tail)
        for first in range(total + 1)
        for tail in _compositions(total - first, length - 1)
    ]


def _sparse_chain(
    ranks: dict[int, int],
    nonzero: dict[int, list[tuple[int, int, int]]],
) -> dict[str, Any]:
    """Build and validate a sparse chain without dense cubic composition.

    The historical preview validator is intentionally a tiny dense prototype.
    Product models in this corpus have hundreds of cells by degree, so the
    current builder checks their sparse compositions directly instead.
    """

    dimension = max(ranks, default=-1)
    complete_ranks = {
        degree: ranks.get(degree, 0) for degree in range(dimension + 1)
    }
    boundaries: dict[int, dict[str, Any]] = {}
    entries_by_degree: dict[int, dict[tuple[int, int], int]] = {}
    for degree in range(1, dimension + 1):
        entries: dict[tuple[int, int], int] = {}
        for row, column, value in nonzero.get(degree, []):
            if not (
                0 <= row < complete_ranks[degree - 1]
                and 0 <= column < complete_ranks[degree]
            ):
                raise ValueError(f"boundary {degree} entry lies outside its matrix")
            entries[(row, column)] = entries.get((row, column), 0) + value
        entries = {position: value for position, value in entries.items() if value}
        entries_by_degree[degree] = entries
        boundaries[degree] = {
            "rows": complete_ranks[degree - 1],
            "cols": complete_ranks[degree],
            "entries": [
                [row, column, value]
                for (row, column), value in sorted(entries.items())
            ],
        }
    for degree in range(2, dimension + 1):
        lower_by_column: dict[int, list[tuple[int, int]]] = {}
        for (row, column), value in entries_by_degree[degree - 1].items():
            lower_by_column.setdefault(column, []).append((row, value))
        composition: Counter[tuple[int, int]] = Counter()
        for (middle, source), upper_value in entries_by_degree[degree].items():
            for target, lower_value in lower_by_column.get(middle, []):
                composition[(target, source)] += lower_value * upper_value
        if any(composition.values()):
            raise ValueError(f"d_{degree - 1} d_{degree} is not zero")
    return {
        "basis": {
            str(degree): [f"c{degree}:{index}" for index in range(rank)]
            for degree, rank in complete_ranks.items()
        },
        "ranks": {
            str(degree): rank for degree, rank in complete_ranks.items()
        },
        "boundaries": {
            str(degree): boundary for degree, boundary in boundaries.items()
        },
    }


def _elementary_abelian_chain(
    prime: int, rank: int, maximum_degree: int
) -> dict[str, Any]:
    bases = {
        degree: _compositions(degree, rank)
        for degree in range(maximum_degree + 1)
    }
    nonzero: dict[int, list[tuple[int, int, int]]] = {}
    for degree in range(1, maximum_degree + 1):
        target_index = {basis: index for index, basis in enumerate(bases[degree - 1])}
        entries: Counter[tuple[int, int]] = Counter()
        for column, basis in enumerate(bases[degree]):
            prefix_degree = 0
            for factor, factor_degree in enumerate(basis):
                if factor_degree > 0 and factor_degree % 2 == 0:
                    target = list(basis)
                    target[factor] -= 1
                    sign = -1 if prefix_degree % 2 else 1
                    entries[(target_index[tuple(target)], column)] += sign * prime
                prefix_degree += factor_degree
        nonzero[degree] = [
            (row, column, value)
            for (row, column), value in sorted(entries.items())
            if value
        ]
    ranks = {degree: len(basis) for degree, basis in bases.items()}
    return _sparse_chain(ranks, nonzero)


def _poincare_artifact() -> tuple[str, list[dict[str, int]]]:
    path = REPOSITORY_ROOT / "corpus" / "chromatic-v1" / "poincare-sphere-facets.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    if (
        artifact.get("schema_version") != "homology-db.simplicial-model/1"
        or artifact.get("model_id")
        != "simplicial:poincare-homology-sphere:sage-686dc1a8"
        or artifact.get("source", {}).get("commit")
        != "686dc1a8d420c2e0aabadd4f602d9a0aa4690c50"
        or artifact.get("source", {}).get("constructor")
        != "PoincareHomologyThreeSphere"
    ):
        raise ValueError("pinned Poincare-sphere artifact has unexpected provenance")
    facets = artifact["facets"]
    if artifact["vertices"] != 16 or len(facets) != 90:
        raise ValueError("pinned Poincare-sphere artifact has unexpected size")
    normalized_facets = [tuple(sorted(facet)) for facet in facets]
    if len(set(normalized_facets)) != len(normalized_facets):
        raise ValueError("pinned Poincare-sphere artifact contains duplicate facets")
    if {vertex for facet in normalized_facets for vertex in facet} != set(range(1, 17)):
        raise ValueError("pinned Poincare-sphere artifact has unexpected vertices")
    faces_by_dimension: list[set[tuple[int, ...]]] = [set() for _ in range(4)]
    for facet in normalized_facets:
        if len(facet) != 4 or len(set(facet)) != 4:
            raise ValueError("pinned Poincare-sphere artifact has a malformed facet")
        for size in range(1, 5):
            faces_by_dimension[size - 1].update(itertools.combinations(sorted(facet), size))
    f_vector = [len(faces) for faces in faces_by_dimension]
    if f_vector != [16, 106, 180, 90]:
        raise ValueError(f"unexpected Poincare-sphere f-vector {f_vector}")
    return hashlib.sha256(path.read_bytes()).hexdigest(), [
        {"degree": degree, "count": count}
        for degree, count in enumerate(f_vector)
    ]


def _materialize_family(
    family: dict[str, Any], parameters: dict[str, Any], *, bound: int
) -> dict[str, Any]:
    formula = family["model_formula"]
    if formula == "point_one_cell":
        return _base_spec(
            family,
            parameters,
            key="point",
            label="Point",
            dimension=0,
            aliases=["*", "pt", "contractible point"],
            ranks={0: 1},
            nonzero=None,
            attaching_map="One 0-cell and no higher cells.",
            boundary_formula="The cellular chain is C_0 = Z with no differential.",
            computation_sketch="The one-cell chain gives H_0 = Z and no positive homology.",
            tags=["contractible", "torsion_free", "calibration"],
        )
    if formula == "sphere_standard":
        n = int(parameters["n"])
        ranks = {0: 2} if n == 0 else {0: 1, n: 1}
        return _base_spec(
            family,
            parameters,
            key=f"sphere:{n}",
            label=f"Sphere S^{n}",
            dimension=n,
            aliases=[f"S^{n}", f"S{n}"],
            ranks=ranks,
            nonzero=None,
            attaching_map=(
                "Use the two-point simplicial model."
                if n == 0
                else f"Attach one {n}-cell to the basepoint by the constant map."
            ),
            boundary_formula="All cellular differentials are zero.",
            computation_sketch=(
                "The two 0-cells give H_0 = Z^2 and reduced H_0 = Z."
                if n == 0
                else f"C_0 and C_{n} are Z with zero differential, so H_0 and H_{n} are Z."
            ),
            tags=["torsion_free", "sphere_spectrum_input", "calibration"],
            connected_components=2 if n == 0 else 1,
            model_kind="finite_simplicial_complex" if n == 0 else "finite_cw",
        )
    if formula == "poincare_simplicial":
        artifact_sha256, cell_degrees = _poincare_artifact()
        return _base_spec(
            family,
            parameters,
            key="poincare_homology_sphere:3",
            label="Poincare homology 3-sphere",
            dimension=3,
            aliases=["Poincare sphere", "Poincare dodecahedral space", "Sigma^3_P"],
            ranks={0: 1, 3: 1},
            nonzero=None,
            attaching_map=(
                "The checked-in 16-vertex, 90-facet simplicial complex is the pinned "
                "Bjorner-Lutz triangulation distributed by SageMath."
            ),
            boundary_formula=(
                "The actual model uses oriented simplicial face maps; the small calculation "
                "certificate records the cited resulting homology, not a replacement CW model."
            ),
            computation_sketch=(
                "Sage's pinned source identifies this triangulation as a Poincare homology "
                "sphere and verifies that its integral homology equals that of S^3."
            ),
            tags=["homology_sphere", "same_homology_guard", "nontrivial_pi1"],
            model_kind="finite_simplicial_complex",
            construction="Use all facets in corpus/chromatic-v1/poincare-sphere-facets.json.",
            model_cell_degrees=cell_degrees,
            artifact_path="corpus/chromatic-v1/poincare-sphere-facets.json",
            artifact_sha256=artifact_sha256,
            integral_override=_integral_rows(3, {0: (1, []), 3: (1, [])}),
            evidence_kind="official_model_and_cited_computation",
            algorithm_id="pinned-sage-poincare-model/686dc1a8",
            run_recorded=False,
        )
    if formula == "sphere_wedge":
        a, b = int(parameters["a"]), int(parameters["b"])
        ranks: dict[int, int] = {0: 1}
        for degree in (a, b):
            ranks[degree] = ranks.get(degree, 0) + 1
        return _base_spec(
            family,
            parameters,
            key=f"sphere_wedge:{a}:{b}",
            label=f"Sphere wedge S^{a} v S^{b}",
            dimension=max(a, b),
            aliases=[f"S^{a} wedge S^{b}", f"S^{a} v S^{b}"],
            ranks=ranks,
            nonzero=None,
            attaching_map="Identify the basepoints of the two standard sphere CW complexes.",
            boundary_formula="All cellular differentials vanish.",
            computation_sketch=f"The reduced cellular chain is Z in degrees {a} and {b}.",
            tags=["torsion_free", "same_chain_guard", "calibration"],
        )
    if formula == "closed_surface_cells":
        kind = parameters["kind"]
        if kind == "torus":
            return _base_spec(
                family,
                parameters,
                key="torus:2",
                label="2-torus T^2",
                dimension=2,
                aliases=["T^2", "torus"],
                ranks={0: 1, 1: 2, 2: 1},
                nonzero=None,
                attaching_map="Attach the 2-cell to the wedge a v b by the commutator aba^-1b^-1.",
                boundary_formula="The abelianized attaching word gives d_2 = 0.",
                computation_sketch="The zero cellular differential gives H_0=Z, H_1=Z^2, H_2=Z.",
                tags=["surface", "orientable", "torsion_free"],
            )
        if kind == "klein_bottle":
            return _base_spec(
                family,
                parameters,
                key="klein_bottle",
                label="Klein bottle",
                dimension=2,
                aliases=["K", "nonorientable surface genus 2"],
                ranks={0: 1, 1: 2, 2: 1},
                nonzero={2: [(1, 0, 2)]},
                attaching_map="Attach the 2-cell to a v b by aba^-1b.",
                boundary_formula="Abelianizing the attaching word gives d_2(1)=2b.",
                computation_sketch="Smith reduction of the column (0,2) gives H_1=Z + Z/2 and H_2=0.",
                tags=["surface", "nonorientable", "2_primary", "torsion"],
            )
        raise ValueError(f"unknown surface kind {kind}")
    if formula == "real_projective_standard_cw":
        n = int(parameters["n"])
        ranks = {degree: 1 for degree in range(n + 1)}
        nonzero = {degree: [(0, 0, 2)] for degree in range(2, n + 1, 2)}
        return _base_spec(
            family,
            parameters,
            key=f"real_projective_space:{n}",
            label=f"Real projective space RP^{n}",
            dimension=n,
            aliases=[f"RP^{n}", f"RP{n}"]
            + (["M(Z/2,1)"] if n == 2 else [])
            + (["SO(3)", "L^3(2;1,1)"] if n == 3 else []),
            ranks=ranks,
            nonzero=nonzero,
            attaching_map=f"Iterate the antipodal quotient S^(k-1) -> RP^(k-1) through k={n}.",
            boundary_formula="d_k = 1 + (-1)^k: multiplication by 2 for even k and 0 for odd k.",
            computation_sketch=f"Apply the alternating 0/2 differential through degree {n} and reduce each 1x1 block.",
            tags=["2_primary", "projective", "torsion", "bc2_skeleton"],
        )
    if formula == "hopf_projective_plane":
        division_algebra = parameters["division_algebra"]
        data = {
            "complex": ("complex_projective_space:2", "Complex projective plane CP^2", 2, 4, "eta", ["CP^2", "CP2", "C_eta"]),
            "quaternionic": ("quaternionic_projective_space:2", "Quaternionic projective plane HP^2", 4, 8, "nu", ["HP^2", "HP2", "C_nu"]),
            "octonionic": ("cayley_plane:2", "Cayley plane OP^2", 8, 16, "sigma", ["OP^2", "OP2", "C_sigma"]),
        }
        if division_algebra not in data:
            raise ValueError(f"unknown division algebra {division_algebra}")
        key, label, middle, top, hopf_map, aliases = data[division_algebra]
        return _base_spec(
            family,
            parameters,
            key=key,
            label=label,
            dimension=top,
            aliases=aliases,
            ranks={0: 1, middle: 1, top: 1},
            nonzero=None,
            attaching_map=f"Attach e^{top} to S^{middle} by the Hopf map {hopf_map}.",
            boundary_formula="All cellular differentials vanish by the gaps between cell degrees.",
            computation_sketch=f"The three cells in degrees 0,{middle},{top} give one free class in each degree.",
            tags=["torsion_free", "projective_plane", "hopf_invariant_one", division_algebra],
        )
    if formula == "cyclic_moore_degree_m":
        m, n = int(parameters["m"]), int(parameters["n"])
        primary_tags = [f"{prime}_primary" for prime, _ in prime_parts(m)]
        return _base_spec(
            family,
            parameters,
            key=f"moore:{m}:{n}",
            label=f"Moore space M(Z/{m},{n})",
            dimension=n + 1,
            aliases=[f"M(Z/{m},{n})", f"M({m},{n})", f"P^{n + 1}({m})"],
            ranks={0: 1, n: 1, n + 1: 1},
            nonzero={n + 1: [(0, 0, m)]},
            attaching_map=f"Attach e^{n + 1} to S^{n} by a degree-{m} map.",
            boundary_formula=f"The only nonzero differential is d_{n + 1}=[{m}].",
            computation_sketch=f"Smith reduction of [{m}] gives reduced H_{n}=Z/{m}.",
            tags=[*primary_tags, "torsion", "moore", "v0_input"],
        )
    if formula == "weighted_lens_cw":
        p = int(parameters["p"])
        weights = [int(weight) for weight in parameters["weights"]]
        if not is_prime(p) or any(weight % p == 0 for weight in weights):
            raise ValueError("lens weights must be units modulo the prime p")
        dimension = 2 * len(weights) - 1
        ranks = {degree: 1 for degree in range(dimension + 1)}
        nonzero = {degree: [(0, 0, p)] for degree in range(2, dimension + 1, 2)}
        weights_text = ",".join(str(weight) for weight in weights)
        return _base_spec(
            family,
            parameters,
            key=f"lens:{p}:{dimension}:{weights_text.replace(',', '-')}",
            label=f"Lens space L^{dimension}({p};{weights_text})",
            dimension=dimension,
            aliases=[f"L^{dimension}({p};{weights_text})"]
            + ([f"L({p},{weights[1]})"] if len(weights) == 2 and weights[0] == 1 else []),
            ranks=ranks,
            nonzero=nonzero,
            attaching_map=(
                f"Quotient S^{dimension} in C^{len(weights)} by the free action "
                f"z_i -> zeta^ell_i z_i with weights ({weights_text}) modulo {p}."
            ),
            boundary_formula=f"The quotient CW differential is {p} in positive even degrees and 0 in odd degrees.",
            computation_sketch=f"The alternating 0/{p} chain gives Z/{p} in odd degrees below {dimension}.",
            tags=[
                f"{p}_primary",
                "torsion",
                "weighted_quotient",
                *(["bcp_skeleton"] if len(set(weights)) == 1 else []),
            ],
        )
    if formula == "stunted_projective_quotient":
        kind = parameters["kind"]
        bottom, top = int(parameters["bottom"]), int(parameters["top"])
        if kind == "real":
            ranks = {0: 1, **{degree: 1 for degree in range(bottom, top + 1)}}
            nonzero = {
                degree: [(0, 0, 2)]
                for degree in range(bottom + 1, top + 1)
                if degree % 2 == 0
            }
            return _base_spec(
                family,
                parameters,
                key=f"stunted_real_projective:{bottom}:{top}",
                label=f"Stunted real projective space RP^{top}/RP^{bottom - 1}",
                dimension=top,
                aliases=[f"RP^{top}/RP^{bottom - 1}", f"P_{bottom}^{top}"],
                ranks=ranks,
                nonzero=nonzero,
                attaching_map=f"Collapse the subcomplex RP^{bottom - 1} in RP^{top}.",
                boundary_formula="Retained real-projective cells have d_k=2 for even k and 0 for odd k.",
                computation_sketch="Compute the relative cellular chain of the projective CW pair by Smith reduction.",
                tags=["2_primary", "torsion", "stunted", "image_of_j_input"],
            )
        if kind == "complex":
            ranks = {0: 1, **{2 * index: 1 for index in range(bottom, top + 1)}}
            return _base_spec(
                family,
                parameters,
                key=f"stunted_complex_projective:{bottom}:{top}",
                label=f"Stunted complex projective space CP^{top}/CP^{bottom - 1}",
                dimension=2 * top,
                aliases=[f"CP^{top}/CP^{bottom - 1}"],
                ranks=ranks,
                nonzero=None,
                attaching_map=f"Collapse the subcomplex CP^{bottom - 1} in CP^{top}.",
                boundary_formula="The retained cells lie in even degrees, so every cellular differential is zero.",
                computation_sketch="The relative cellular chain has one free generator in each retained even degree.",
                tags=["torsion_free", "stunted", "complex_oriented"],
            )
        raise ValueError(f"unknown stunted projective kind {kind}")
    if formula == "compact_lie_low_rank":
        group, rank = parameters["group"], int(parameters["rank"])
        if (group, rank) == ("SU", 3):
            return _base_spec(
                family,
                parameters,
                key="special_unitary_group:3",
                label="Special unitary group SU(3)",
                dimension=8,
                aliases=["SU(3)", "SU3"],
                ranks={0: 1, 3: 1, 5: 1, 8: 1},
                nonzero=None,
                attaching_map="Attach the 5-cell to S^3 by eta, then attach the top 8-cell as in the cited finite CW decomposition.",
                boundary_formula="All cellular differentials vanish because there are no cells in adjacent dimensions.",
                computation_sketch="The finite CW ranks give Z in degrees 0,3,5,8.",
                tags=["torsion_free", "lie_group", "h_space"],
            )
        if (group, rank) == ("Sp", 2):
            return _base_spec(
                family,
                parameters,
                key="compact_symplectic_group:2",
                label="Compact symplectic group Sp(2)",
                dimension=10,
                aliases=["Sp(2)", "Sp2", "USp(4)"],
                ranks={0: 1, 3: 1, 7: 1, 10: 1},
                nonzero=None,
                attaching_map="Attach the 7-cell by a generator of pi_6(S^3)=Z/12, then use the cited top-cell attachment.",
                boundary_formula="All cellular differentials vanish because there are no cells in adjacent dimensions.",
                computation_sketch="The finite CW ranks give Z in degrees 0,3,7,10.",
                tags=["torsion_free", "lie_group", "h_space"],
            )
        raise ValueError(f"unsupported compact Lie group {group}({rank})")
    if formula == "finite_schubert_cells":
        kind = parameters["kind"]
        if kind == "complete_flag_c3":
            key, label, dimension = "complete_flag:c3", "Complete flag variety Fl_3(C)", 6
            aliases, ranks = ["Fl_3(C)", "U(3)/T^3"], {0: 1, 2: 2, 4: 2, 6: 1}
        elif kind == "grassmannian_2_c4":
            key, label, dimension = "grassmannian:2:4:c", "Complex Grassmannian Gr_2(C^4)", 8
            aliases, ranks = ["Gr_2(C^4)", "Gr(2,4)"], {0: 1, 2: 1, 4: 2, 6: 1, 8: 1}
        else:
            raise ValueError(f"unknown finite Schubert space {kind}")
        return _base_spec(
            family,
            parameters,
            key=key,
            label=label,
            dimension=dimension,
            aliases=aliases,
            ranks=ranks,
            nonzero=None,
            attaching_map="Use the finite Schubert-cell filtration indexed by the relevant Weyl or partition data.",
            boundary_formula="All Schubert cells are even-dimensional, so cellular differentials vanish.",
            computation_sketch="Count Schubert cells in each degree; each supplies one free integral homology generator.",
            tags=["torsion_free", "schubert", "complex_oriented"],
        )
    if formula == "cyclic_classifying_finite_type":
        p = int(parameters["p"])
        ranks = {degree: 1 for degree in range(bound + 2)}
        nonzero = {degree: [(0, 0, p)] for degree in range(2, bound + 2, 2)}
        return _base_spec(
            family,
            parameters,
            key=f"classifying_space:cyclic:{p}",
            label=f"Cyclic classifying space B(C_{p})",
            dimension=None,
            aliases=[f"BC_{p}", f"B(Z/{p})"] + (["RP^infinity", "RP∞"] if p == 2 else []),
            ranks=ranks,
            nonzero=nonzero,
            attaching_map=f"Use the infinite lens-space colimit S^infinity/C_{p} with one cell in every degree.",
            boundary_formula=f"d_k={p} for positive even k and d_k=0 for odd k.",
            computation_sketch=f"Materialize the alternating 0/{p} cellular chain through degree {bound + 1} and compute groups through {bound}.",
            tags=[f"{p}_primary", "torsion", "classifying_space", "formal_group_input"],
            computed_through_degree=bound,
            model_kind="finite_type_cw",
            cell_formula="one cell in every degree k >= 0",
            model_cell_degrees=_cell_degrees({degree: 1 for degree in range(bound + 1)}),
            model_scope=f"Infinite finite-type CW recipe; the checked calculation is complete only through degree {bound}.",
        )
    if formula == "elementary_abelian_classifying_finite_type":
        p, rank = int(parameters["p"]), int(parameters["rank"])
        witness_degree = bound + 1
        chain = _elementary_abelian_chain(p, rank, witness_degree)
        multiplicity: dict[int, int] = {0: 0}
        groups: dict[int, tuple[int, list[int]]] = {0: (1, [])}
        for degree in range(1, bound + 1):
            cell_rank = len(_compositions(degree, rank))
            multiplicity[degree] = cell_rank - multiplicity[degree - 1]
            groups[degree] = (0, [p] * multiplicity[degree])
        cell_ranks = {
            degree: len(_compositions(degree, rank)) for degree in range(bound + 1)
        }
        return _base_spec(
            family,
            parameters,
            key=f"classifying_space:elementary_abelian:{p}:{rank}",
            label=f"Elementary-abelian classifying space B((C_{p})^{rank})",
            dimension=None,
            aliases=[f"B(C_{p}^{rank})", f"B((Z/{p})^{rank})"],
            ranks={
                degree: len(_compositions(degree, rank))
                for degree in range(witness_degree + 1)
            },
            nonzero=None,
            attaching_map=f"Use the product CW model (B(C_{p}))^{rank} with the signed tensor-product differential.",
            boundary_formula=(
                f"C_n has rank binomial(n+{rank - 1},{rank - 1}); the differential is the "
                f"signed tensor product of the alternating 0/{p} cyclic differentials."
            ),
            computation_sketch=(
                f"The Kunneth recurrence a_n=binomial(n+{rank - 1},{rank - 1})-a_(n-1) "
                f"gives H_n=(Z/{p})^a_n through degree {bound}; the explicit tensor chain "
                f"includes the incoming differential through degree {witness_degree}."
            ),
            tags=[f"{p}_primary", "torsion", "classifying_space", "character_theory_input"],
            computed_through_degree=bound,
            model_kind="finite_type_cw",
            cell_formula=f"rank C_n = binomial(n+{rank - 1},{rank - 1})",
            model_cell_degrees=_cell_degrees(cell_ranks),
            model_scope=f"Infinite product CW recipe; the checked formula is materialized only through degree {bound}.",
            chain_override=chain,
            integral_override=_integral_rows(bound, groups),
            evidence_kind="owned_formula_computation",
            algorithm_id="elementary-abelian-kunneth-recurrence/1",
        )
    if formula == "infinite_projective_finite_type":
        division_algebra = parameters["division_algebra"]
        if division_algebra == "complex":
            step, key, label = 2, "complex_projective_space:infinity", "Infinite complex projective space CP^infinity"
            aliases = ["CP^infinity", "CP∞", "BU(1)", "BS^1", "K(Z,2)"]
        elif division_algebra == "quaternionic":
            step, key, label = 4, "quaternionic_projective_space:infinity", "Infinite quaternionic projective space HP^infinity"
            aliases = ["HP^infinity", "HP∞", "BSp(1)"]
        else:
            raise ValueError(f"unknown infinite projective kind {division_algebra}")
        ranks = {degree: 1 for degree in range(0, bound + 1, step)}
        return _base_spec(
            family,
            parameters,
            key=key,
            label=label,
            dimension=None,
            aliases=aliases,
            ranks=ranks,
            nonzero=None,
            attaching_map=f"Take the colimit of standard projective skeleta with one cell in every degree divisible by {step}.",
            boundary_formula="All cellular differentials vanish by degree.",
            computation_sketch=f"Materialize one cell in each multiple of {step} through degree {bound}.",
            tags=["torsion_free", "projective", "orientation_input"],
            computed_through_degree=bound,
            model_kind="finite_type_cw",
            cell_formula=f"one cell in every degree {step}k for k >= 0",
            model_scope=f"Infinite projective filtration; homology is materialized only through degree {bound}.",
        )
    if formula == "unitary_classifying_schubert":
        n = int(parameters["n"])
        ranks = {
            2 * weight: _partition_count(weight, n)
            for weight in range(bound // 2 + 1)
        }
        return _base_spec(
            family,
            parameters,
            key=f"unitary_classifying_space:{n}",
            label=f"Unitary classifying space BU({n})",
            dimension=None,
            aliases=[f"BU({n})", f"Gr_{n}(C^infinity)"],
            ranks=ranks,
            nonzero=None,
            attaching_map="Use the colimit of complex Grassmannians with the partition-indexed Schubert CW filtration.",
            boundary_formula="All Schubert cells are even-dimensional, so cellular differentials vanish.",
            computation_sketch=f"In degree 2k, count partitions of k with at most {n} parts; materialize through degree {bound}.",
            tags=["torsion_free", "classifying_space", "complex_bundles", "schubert"],
            computed_through_degree=bound,
            model_kind="finite_type_cw",
            cell_formula=f"rank C_(2k) = number of partitions of k with at most {n} parts; odd ranks zero",
            model_scope=f"Infinite Schubert CW recipe; homology is materialized only through degree {bound}.",
        )
    if formula == "universal_complex_thom":
        rank = int(parameters["rank"])
        ranks = {0: 1}
        for weight in range((bound - 2 * rank) // 2 + 1):
            ranks[2 * rank + 2 * weight] = _partition_count(weight, rank)
        return _base_spec(
            family,
            parameters,
            key=f"universal_complex_thom:{rank}",
            label=f"Thom space Th(gamma_{rank} -> BU({rank}))",
            dimension=None,
            aliases=[f"MU({rank})", f"Th(gamma_{rank})"],
            ranks=ranks,
            nonzero=None,
            attaching_map=f"Form D(gamma_{rank})/S(gamma_{rank}) over the Schubert CW model of BU({rank}).",
            boundary_formula=f"The Thom cells shift each BU({rank}) Schubert cell upward by real degree {2 * rank}; all differentials vanish.",
            computation_sketch=f"Apply the integral Thom shift to partition-counted BU({rank}) cells through degree {bound}.",
            tags=["torsion_free", "thom", "complex_cobordism_input", "complex_oriented"],
            computed_through_degree=bound,
            model_kind="finite_type_cw",
            cell_formula=f"basepoint plus rank C_(2{rank}+2k) = partitions of k with at most {rank} parts",
            model_scope=f"Infinite Thom-space CW recipe; homology is materialized only through degree {bound}.",
        )
    raise ValueError(f"unknown model formula {formula}")


def materialize_specs(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    bound = int(manifest["materialized_through_degree"])
    specs = [
        _materialize_family(family, parameters, bound=bound)
        for family in manifest["families"]
        for parameters in _parameter_instances(family)
    ]
    space_ids = [spec["key"] for spec in specs]
    if len(space_ids) != len(set(space_ids)):
        raise ValueError("chromatic corpus contains duplicate Conceptual-space IDs")
    if len(specs) != 42:
        raise ValueError(f"expected the curated 42-space corpus, generated {len(specs)}")
    if any(len(spec["sources"]) == 0 for spec in specs):
        raise ValueError("every chromatic space must inherit at least one source")
    return specs


def _insert_homology(
    connection: sqlite3.Connection,
    *,
    snapshot_id: str,
    spec: dict[str, Any],
    evidence_id: str,
) -> None:
    integral = spec["integral_override"] or compute_integral_homology(
        spec["chain"], spec["computed_through_degree"]
    )
    coefficient_rows: dict[str, list[dict[str, Any]]] = {"Z": integral}
    for coefficient, prime in COEFFICIENTS.items():
        if prime is not None:
            field_rows: list[dict[str, Any]] = []
            previous_torsion: list[int] = []
            for row in integral:
                torsion = row.get("torsion_orders", [])
                dimension = (
                    row["free_rank"]
                    + sum(order % prime == 0 for order in torsion)
                    + sum(order % prime == 0 for order in previous_torsion)
                )
                field_rows.append({"degree": row["degree"], "dimension": dimension})
                previous_torsion = torsion
            coefficient_rows[coefficient] = field_rows
    for coefficient, rows in coefficient_rows.items():
        for reduced in (False, True):
            for row in rows:
                degree = row["degree"]
                free_rank = row.get("free_rank", row.get("dimension", 0))
                torsion = row.get("torsion_orders", []) if coefficient == "Z" else []
                if reduced and degree == 0:
                    free_rank = max(0, free_rank - 1)
                assertion_id = (
                    f"chromatic:assertion:{spec['key']}:{coefficient}:"
                    f"{'r' if reduced else 'u'}:{degree}"
                )
                connection.execute(
                    """
                    INSERT INTO homology VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, 'exact', 'complete_group', ?)
                    """,
                    (
                        assertion_id,
                        snapshot_id,
                        spec["key"],
                        coefficient,
                        int(reduced),
                        degree,
                        free_rank,
                        canonical_json(torsion),
                        evidence_id,
                    ),
                )
                if coefficient != "Z":
                    continue
                counts: Counter[tuple[int, int]] = Counter()
                for order in torsion:
                    counts.update(prime_parts(order))
                for (prime, exponent), multiplicity in sorted(counts.items()):
                    connection.execute(
                        "INSERT INTO primary_summand VALUES (?, ?, ?, ?)",
                        (assertion_id, prime, exponent, multiplicity),
                    )


def build_database(path: Path, manifest_path: Path = MANIFEST_PATH) -> str:
    manifest = load_manifest(manifest_path)
    specs = materialize_specs(manifest)
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    builder_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    preview_algorithm_sha256 = hashlib.sha256(
        (REPOSITORY_ROOT / "homology_db" / "preview.py").read_bytes()
    ).hexdigest()
    poincare_sha256 = hashlib.sha256(
        (manifest_path.parent / "poincare-sphere-facets.json").read_bytes()
    ).hexdigest()
    snapshot_payload = {
        "manifest_sha256": manifest_sha256,
        "builder_sha256": builder_sha256,
        "preview_algorithm_sha256": preview_algorithm_sha256,
        "poincare_artifact_sha256": poincare_sha256,
        "schema_version": SCHEMA_VERSION,
    }
    snapshot_id = f"chromatic-{digest(snapshot_payload)[:16]}"
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA)
        connection.execute(
            "INSERT INTO snapshot VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                snapshot_id,
                manifest["snapshot_name"],
                SCHEMA_VERSION,
                len(specs),
                manifest_sha256,
                manifest["scope"],
                manifest["materialized_through_degree"],
            ),
        )
        for order, family in enumerate(manifest["families"]):
            connection.execute(
                "INSERT INTO family VALUES (?, ?, ?, ?, ?)",
                (
                    family["id"],
                    family["label"],
                    family["summary"],
                    family["chromatic_relevance"],
                    order,
                ),
            )
        for reference in manifest["references"]:
            connection.execute(
                "INSERT INTO reference VALUES (?, ?, ?, ?, ?, ?)",
                (
                    reference["id"],
                    canonical_json(reference["authors"]),
                    reference["title"],
                    reference["year"],
                    reference["url"],
                    reference["source_kind"],
                ),
            )
        for spec in specs:
            chain_sha256 = spec["model"]["chain_sha256"]
            connection.execute(
                "INSERT INTO space VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    spec["key"],
                    spec["label"],
                    spec["family"],
                    spec["dimension"],
                    int(spec["infinite_finite_type"]),
                    spec["connected_components"],
                    canonical_json(spec["parameters"]),
                    canonical_json(spec["tags"]),
                    spec["summary"],
                    spec["chromatic_relevance"],
                    spec["equivalence"],
                    chain_sha256,
                ),
            )
            for alias in sorted(
                {spec["key"], spec["label"], *spec["aliases"]},
                key=lambda value: (normalize_name(value), value),
            ):
                connection.execute(
                    "INSERT OR IGNORE INTO alias VALUES (?, ?, ?)",
                    (normalize_name(alias), spec["key"], alias),
                )
            model = spec["model"]
            connection.execute(
                "INSERT INTO model VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    model["id"],
                    spec["key"],
                    model["kind"],
                    model["status"],
                    model["name"],
                    model["construction"],
                    canonical_json(model["cell_degrees"]),
                    model["cell_formula"],
                    model["attaching_map"],
                    model["boundary_formula"],
                    model["chain_sha256"],
                    model["model_scope"],
                    model["artifact_path"],
                    model["artifact_sha256"],
                ),
            )
            integral = spec["integral_override"] or compute_integral_homology(
                spec["chain"], spec["computed_through_degree"]
            )
            representative_states = {
                row["representatives"]["state"] for row in integral
            }
            evidence_id = f"chromatic:evidence:{spec['key']}"
            connection.execute(
                "INSERT INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    evidence_id,
                    spec["key"],
                    model["id"],
                    spec["evidence_kind"],
                    spec["algorithm_id"],
                    chain_sha256,
                    canonical_json(spec["chain"]),
                    spec["computation_sketch"],
                    (
                        "exact_owned_computation_with_cited_family_cross_check"
                        if spec["run_recorded"]
                        else "exact_cited_computation_no_local_run"
                    ),
                    "exact_or_explicit_not_computed:"
                    + ",".join(sorted(representative_states)),
                    "identity_only;nonidentity_not_computed",
                ),
            )
            for source in spec["sources"]:
                connection.execute(
                    "INSERT INTO evidence_reference VALUES (?, ?, ?, ?)",
                    (
                        evidence_id,
                        source["reference_id"],
                        source["role"],
                        source["locator"],
                    ),
                )
            if spec["run_recorded"]:
                computation_id = f"chromatic:computation:{spec['key']}"
                connection.execute(
                    "INSERT INTO computation_run VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        computation_id,
                        evidence_id,
                        spec["algorithm_id"],
                        chain_sha256,
                        canonical_json(
                            {
                                "coefficients": list(COEFFICIENTS),
                                "computed_through_degree": spec[
                                    "computed_through_degree"
                                ],
                                "family_parameters": spec["parameters"],
                            }
                        ),
                        (
                            "complete finite-space groups"
                            if not spec["infinite_finite_type"]
                            else "groups complete only through the declared degree bound"
                        ),
                        "succeeded",
                    ),
                )
            connection.execute(
                "INSERT INTO homology_coverage VALUES (?, ?, ?, ?, ?)",
                (
                    spec["key"],
                    spec["coverage_kind"],
                    spec["computed_through_degree"],
                    spec["upper_vanishing_starts_at"],
                    (
                        f"Complete for this finite CW space; zero above degree {spec['dimension']}."
                        if not spec["infinite_finite_type"]
                        else (
                            "This infinite finite-type CW formula is materialized through "
                            f"degree {spec['computed_through_degree']}; no claim is made above it."
                        )
                    ),
                ),
            )
            _insert_homology(
                connection,
                snapshot_id=snapshot_id,
                spec=spec,
                evidence_id=evidence_id,
            )
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()
    return snapshot_id


class ChromaticDatabase:
    """Build the deterministic current Chromatic Homology Atlas Snapshot."""

    @staticmethod
    def build(path: Path = DEFAULT_DB) -> str:
        return build_database(path)


class ChromaticTools:
    """Four stable JSON operations over one immutable chromatic Snapshot."""

    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.snapshot_id = self.connection.execute(
            "SELECT snapshot_id FROM snapshot"
        ).fetchone()[0]

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> ChromaticTools:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def corpus_summary(self) -> dict[str, Any]:
        snapshot = self.connection.execute("SELECT * FROM snapshot").fetchone()
        counts = {
            row["family"]: row["count"]
            for row in self.connection.execute(
                "SELECT family, COUNT(*) AS count FROM space GROUP BY family ORDER BY family"
            )
        }
        return {
            "snapshot_id": self.snapshot_id,
            "snapshot_name": snapshot["snapshot_name"],
            "subject_count": snapshot["corpus_count"],
            "family_counts": counts,
            "manifest_sha256": snapshot["manifest_sha256"],
            "schema_version": snapshot["schema_version"],
            "materialized_through_degree": snapshot[
                "materialized_through_degree"
            ],
            "scope_note": snapshot["scope_note"],
            "supported_tools": [
                "resolve_subject",
                "read_homology",
                "query_examples",
                "expand_evidence",
            ],
            "release_status": RELEASE_STATUS,
        }

    def resolve_subject(self, query: str) -> dict[str, Any]:
        if not isinstance(query, str) or not query.strip():
            return {
                "tool": "resolve_subject",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "query must be a nonempty string",
            }
        normalized = normalize_name(query)
        if not normalized:
            return {
                "tool": "resolve_subject",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "query must contain at least one letter or digit",
            }
        rows = self.connection.execute(
            """
            SELECT DISTINCT s.space_id, s.label, s.family
            FROM alias a JOIN space s USING(space_id)
            WHERE a.normalized_alias = ? ORDER BY s.space_id
            """,
            (normalized,),
        ).fetchall()
        if not rows:
            escaped = (
                normalized.replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            rows = self.connection.execute(
                """
                SELECT DISTINCT s.space_id, s.label, s.family
                FROM alias a JOIN space s USING(space_id)
                WHERE a.normalized_alias LIKE ? ESCAPE '\\'
                ORDER BY s.label LIMIT 8
                """,
                (f"%{escaped}%",),
            ).fetchall()
            return {
                "tool": "resolve_subject",
                "snapshot_id": self.snapshot_id,
                "outcome": "not_found",
                "suggestions": [dict(row) for row in rows],
            }
        return {
            "tool": "resolve_subject",
            "snapshot_id": self.snapshot_id,
            "outcome": "resolved" if len(rows) == 1 else "ambiguous",
            "candidates": [dict(row) for row in rows],
        }

    def read_homology(
        self, subject: str, coefficient: str = "Z", reduced: bool = False
    ) -> dict[str, Any]:
        if not isinstance(subject, str) or not subject.strip():
            return {
                "tool": "read_homology",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "subject must be a nonempty string",
            }
        if not isinstance(coefficient, str):
            return {
                "tool": "read_homology",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "coefficient must be a string",
            }
        if not isinstance(reduced, bool):
            return {
                "tool": "read_homology",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "reduced must be a boolean",
            }
        if coefficient not in COEFFICIENTS:
            return {
                "tool": "read_homology",
                "snapshot_id": self.snapshot_id,
                "outcome": "unsupported_coefficient",
                "supported": list(COEFFICIENTS),
            }
        resolution = self.resolve_subject(subject)
        if resolution["outcome"] != "resolved":
            return {
                "tool": "read_homology",
                "snapshot_id": self.snapshot_id,
                "outcome": "subject_not_resolved",
                "resolution": resolution,
            }
        space_id = resolution["candidates"][0]["space_id"]
        space = dict(
            self.connection.execute(
                "SELECT * FROM space WHERE space_id = ?", (space_id,)
            ).fetchone()
        )
        space["parameters"] = json.loads(space.pop("parameters_json"))
        space["tags"] = json.loads(space.pop("tags_json"))
        space["infinite_finite_type"] = bool(space["infinite_finite_type"])
        coverage_row = self.connection.execute(
            "SELECT * FROM homology_coverage WHERE space_id = ?", (space_id,)
        ).fetchone()
        if coverage_row is None:
            return {
                "tool": "read_homology",
                "snapshot_id": self.snapshot_id,
                "outcome": "coverage_not_recorded",
                "subject": space,
            }
        coverage = {
            "kind": coverage_row["coverage_kind"],
            "computed_through_degree": coverage_row[
                "computed_through_degree"
            ],
            "upper_vanishing_starts_at": coverage_row[
                "upper_vanishing_starts_at"
            ],
            "detail": coverage_row["detail"],
        }
        rows = self.connection.execute(
            """
            SELECT assertion_id, degree, free_rank, torsion_json, knowledge_state,
                   value_scope, evidence_id
            FROM homology
            WHERE snapshot_id = ? AND space_id = ? AND coefficient = ? AND reduced = ?
            ORDER BY degree
            """,
            (self.snapshot_id, space_id, coefficient, int(reduced)),
        ).fetchall()
        groups = []
        for row in rows:
            torsion = json.loads(row["torsion_json"])
            if coefficient == "Z":
                display_parts = (["Z"] * row["free_rank"]) + [
                    f"Z/{order}" for order in torsion
                ]
                value = {
                    "free_rank": row["free_rank"],
                    "torsion_orders": torsion,
                    "display": "0" if not display_parts else " + ".join(display_parts),
                }
            else:
                dimension = row["free_rank"]
                value = {
                    "dimension": dimension,
                    "display": (
                        "0"
                        if dimension == 0
                        else coefficient + (f"^{dimension}" if dimension > 1 else "")
                    ),
                }
            groups.append(
                {
                    "degree": row["degree"],
                    "value": value,
                    "knowledge_state": row["knowledge_state"],
                    "value_scope": row["value_scope"],
                    "assertion_id": row["assertion_id"],
                    "evidence_id": row["evidence_id"],
                }
            )
        return {
            "tool": "read_homology",
            "snapshot_id": self.snapshot_id,
            "outcome": "selected",
            "subject": space,
            "coefficient": coefficient,
            "reduced": reduced,
            "groups": groups,
            "coverage": coverage,
            # Retained as a nullable compatibility field for the historical
            # read model.  A null value is deliberate for bounded finite-type
            # computations and must never be interpreted as vanishing.
            "upper_vanishing_starts_at": coverage[
                "upper_vanishing_starts_at"
            ],
        }

    def query_examples(self, pattern: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(pattern, dict):
            return {
                "tool": "query_examples",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "pattern must be a JSON object",
            }
        allowed = {
            "family",
            "coefficient",
            "reduced",
            "degree",
            "torsion_prime",
            "contains_torsion_order",
            "free_rank_at_least",
            "limit",
        }
        unknown = set(pattern) - allowed
        if unknown:
            return {
                "tool": "query_examples",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_pattern",
                "unknown_fields": sorted(unknown),
            }
        validators = (
            (
                "family",
                lambda value: isinstance(value, str) and bool(value),
                "family must be a nonempty string",
            ),
            (
                "coefficient",
                lambda value: isinstance(value, str),
                "coefficient must be a string",
            ),
            (
                "reduced",
                lambda value: isinstance(value, bool),
                "reduced must be a boolean",
            ),
            (
                "degree",
                lambda value: isinstance(value, int)
                and not isinstance(value, bool)
                and value >= 0,
                "degree must be a nonnegative integer",
            ),
            (
                "torsion_prime",
                lambda value: isinstance(value, int)
                and not isinstance(value, bool)
                and is_prime(value),
                "torsion_prime must be a prime integer",
            ),
            (
                "contains_torsion_order",
                lambda value: isinstance(value, int)
                and not isinstance(value, bool)
                and value > 1,
                "contains_torsion_order must be an integer greater than 1",
            ),
            (
                "free_rank_at_least",
                lambda value: isinstance(value, int)
                and not isinstance(value, bool)
                and value >= 0,
                "free_rank_at_least must be a nonnegative integer",
            ),
            (
                "limit",
                lambda value: isinstance(value, int)
                and not isinstance(value, bool)
                and 1 <= value <= 100,
                "limit must be an integer from 1 through 100",
            ),
        )
        for field, validator, reason in validators:
            if field in pattern and not validator(pattern[field]):
                return {
                    "tool": "query_examples",
                    "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern",
                    "reason": reason,
                }
        coefficient = pattern.get("coefficient", "Z")
        if coefficient not in COEFFICIENTS:
            return {
                "tool": "query_examples",
                "snapshot_id": self.snapshot_id,
                "outcome": "unsupported_coefficient",
                "supported": list(COEFFICIENTS),
            }
        if "free_rank_at_least" in pattern and coefficient != "Z":
            return {
                "tool": "query_examples",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_pattern",
                "reason": "free_rank_at_least requires coefficient Z",
            }
        clauses = [
            "h.snapshot_id = ?",
            "h.coefficient = ?",
            "h.reduced = ?",
            "h.knowledge_state = 'exact'",
        ]
        parameters: list[Any] = [
            self.snapshot_id,
            coefficient,
            int(pattern.get("reduced", False)),
        ]
        joins = ""
        if "family" in pattern:
            clauses.append("s.family = ?")
            parameters.append(pattern["family"])
        if "degree" in pattern:
            clauses.append("h.degree = ?")
            parameters.append(pattern["degree"])
        if "free_rank_at_least" in pattern:
            clauses.append("h.free_rank >= ?")
            parameters.append(pattern["free_rank_at_least"])
        if "torsion_prime" in pattern:
            if coefficient != "Z":
                return {
                    "tool": "query_examples",
                    "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern",
                    "reason": "torsion filters require coefficient Z",
                }
            joins += " JOIN primary_summand p ON p.assertion_id = h.assertion_id"
            clauses.append("p.prime = ?")
            parameters.append(pattern["torsion_prime"])
        if "contains_torsion_order" in pattern:
            if coefficient != "Z":
                return {
                    "tool": "query_examples",
                    "snapshot_id": self.snapshot_id,
                    "outcome": "invalid_pattern",
                    "reason": "torsion filters require coefficient Z",
                }
            clauses.append(
                "EXISTS (SELECT 1 FROM json_each(h.torsion_json) WHERE value = ?)"
            )
            parameters.append(pattern["contains_torsion_order"])
        selected_columns = (
            "s.space_id, s.label, s.family, h.degree, h.free_rank, "
            "h.torsion_json, h.knowledge_state, h.value_scope, "
            "h.assertion_id, h.evidence_id"
        )
        from_where = (
            " FROM homology h JOIN space s USING(space_id)"
            + joins
            + " WHERE "
            + " AND ".join(clauses)
        )
        total_matches = self.connection.execute(
            "SELECT COUNT(*) FROM (SELECT DISTINCT "
            + selected_columns
            + from_where
            + ") AS candidates",
            parameters,
        ).fetchone()[0]
        limit = pattern.get("limit", 20)
        rows = self.connection.execute(
            "SELECT DISTINCT "
            + selected_columns
            + from_where
            + " ORDER BY s.family, s.label, h.degree LIMIT ?",
            (*parameters, limit),
        ).fetchall()
        matches = []
        for row in rows:
            match = {**dict(row), "torsion_orders": json.loads(row["torsion_json"])}
            match.pop("torsion_json")
            matches.append(match)
        subject_count = self.connection.execute(
            "SELECT corpus_count FROM snapshot WHERE snapshot_id = ?",
            (self.snapshot_id,),
        ).fetchone()[0]
        return {
            "tool": "query_examples",
            "snapshot_id": self.snapshot_id,
            "outcome": "proven_matches",
            "pattern": pattern,
            "matches": matches,
            "total_matches": total_matches,
            "truncated": len(matches) < total_matches,
            "coverage": {
                "scope": "selected_snapshot_assertions",
                "subject_count": subject_count,
                "globally_exhaustive": False,
            },
            "unresolved_candidates": [],
        }

    def expand_evidence(self, evidence_ids: list[str]) -> dict[str, Any]:
        if not isinstance(evidence_ids, list) or not evidence_ids:
            return {
                "tool": "expand_evidence",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "evidence_ids must be a nonempty array",
            }
        if any(
            not isinstance(evidence_id, str) or not evidence_id
            for evidence_id in evidence_ids
        ):
            return {
                "tool": "expand_evidence",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "every evidence_id must be a nonempty string",
            }
        requested = sorted(set(evidence_ids))
        if len(requested) > 100:
            return {
                "tool": "expand_evidence",
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": "at most 100 distinct evidence IDs may be expanded",
            }
        placeholders = ",".join("?" for _ in requested)
        rows = self.connection.execute(
            f"""
            SELECT e.*, m.kind AS model_kind, m.name AS model_name,
                   m.status AS model_status, m.construction,
                   m.cell_degrees_json, m.cell_formula, m.attaching_map,
                   m.boundary_formula, m.model_scope, m.artifact_path,
                   m.artifact_sha256,
                   c.computation_id, c.parameters_json,
                   c.output_scope, c.status AS computation_status
            FROM evidence e
            JOIN model m USING(model_id)
            LEFT JOIN computation_run c USING(evidence_id)
            WHERE e.evidence_id IN ({placeholders})
            ORDER BY e.evidence_id
            """,
            requested,
        ).fetchall()
        found = {row["evidence_id"] for row in rows}
        output = []
        for row in rows:
            references = [
                {
                    "reference_id": reference["reference_id"],
                    "authors": json.loads(reference["authors_json"]),
                    "title": reference["title"],
                    "year": reference["publication_year"],
                    "url": reference["url"],
                    "source_kind": reference["source_kind"],
                    "role": reference["role"],
                    "locator": reference["locator"],
                }
                for reference in self.connection.execute(
                    """
                    SELECT r.*, er.role, er.locator
                    FROM evidence_reference er
                    JOIN reference r USING(reference_id)
                    WHERE er.evidence_id = ?
                    ORDER BY er.role, r.reference_id, er.locator
                    """,
                    (row["evidence_id"],),
                )
            ]
            output.append(
                {
                    "evidence_id": row["evidence_id"],
                    "space_id": row["space_id"],
                    "evidence_kind": row["evidence_kind"],
                    "algorithm_id": row["algorithm_id"],
                    "chain_sha256": row["chain_sha256"],
                    "computation_sketch": row["computation_sketch"],
                    "reliability": row["reliability"],
                    "representatives_state": row["representatives_state"],
                    "induced_maps_state": row["induced_maps_state"],
                    "model": {
                        "model_id": row["model_id"],
                        "kind": row["model_kind"],
                        "name": row["model_name"],
                        "status": row["model_status"],
                        "construction": row["construction"],
                        "cell_degrees": json.loads(row["cell_degrees_json"]),
                        "cell_formula": row["cell_formula"],
                        "attaching_map": row["attaching_map"],
                        "boundary_formula": row["boundary_formula"],
                        "chain_sha256": row["chain_sha256"],
                        "model_scope": row["model_scope"],
                        "artifact_path": row["artifact_path"],
                        "artifact_sha256": row["artifact_sha256"],
                    },
                    "references": references,
                    "computation": (
                        {
                            "computation_id": row["computation_id"],
                            "algorithm_id": row["algorithm_id"],
                            "input_sha256": row["chain_sha256"],
                            "parameters": json.loads(row["parameters_json"]),
                            "output_scope": row["output_scope"],
                            "status": row["computation_status"],
                        }
                        if row["computation_id"] is not None
                        else None
                    ),
                }
            )
        return {
            "tool": "expand_evidence",
            "snapshot_id": self.snapshot_id,
            "outcome": "complete" if found == set(requested) else "partial",
            "evidence": output,
            "missing_evidence_ids": sorted(set(requested) - found),
        }

    def call(self, request: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(request, dict):
            return {
                "outcome": "invalid_request",
                "snapshot_id": self.snapshot_id,
                "reason": "tool request must be a JSON object",
            }
        tool = request.get("tool")
        arguments = request.get("arguments", {})
        if not isinstance(arguments, dict):
            return {
                "tool": tool,
                "outcome": "invalid_request",
                "snapshot_id": self.snapshot_id,
                "reason": "arguments must be a JSON object",
            }
        dispatch = {
            "resolve_subject": self.resolve_subject,
            "read_homology": self.read_homology,
            "query_examples": self.query_examples,
            "expand_evidence": self.expand_evidence,
        }
        if tool is None:
            return {
                "outcome": "invalid_request",
                "snapshot_id": self.snapshot_id,
                "reason": "tool is required",
            }
        if not isinstance(tool, str):
            return {
                "outcome": "invalid_request",
                "snapshot_id": self.snapshot_id,
                "reason": "tool must be a string",
            }
        if tool not in dispatch:
            return {
                "tool": tool,
                "outcome": "unknown_tool",
                "snapshot_id": self.snapshot_id,
                "supported_tools": sorted(dispatch),
            }
        try:
            return dispatch[tool](**arguments)
        except (TypeError, ValueError) as error:
            return {
                "tool": tool,
                "snapshot_id": self.snapshot_id,
                "outcome": "invalid_request",
                "reason": str(error),
            }


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def demo(path: Path) -> None:
    snapshot_id = build_database(path)
    with ChromaticTools(path) as tools:
        moore = tools.read_homology("M(Z/5,2)")
        lens = tools.read_homology("L^5(3;1,1,1)")
        projective = tools.read_homology("CP^2")
        evidence = tools.expand_evidence([moore["groups"][2]["evidence_id"]])
        print(f"Chromatic Homology Atlas ready: 42 spaces, snapshot {snapshot_id}")
        print(f"Scratch database: {path} (safe to delete; rebuilt on every run)\n")
        print("Quick mathematical tour")
        print(f"  M(Z/5,2): H_2 = {moore['groups'][2]['value']['display']}")
        print(f"  L^5(3): H_3 = {lens['groups'][3]['value']['display']}")
        print(f"  CP^2: H_4 = {projective['groups'][4]['value']['display']}")
        print(
            "  CW model: "
            + evidence["evidence"][0]["model"]["attaching_map"]
        )
        print(
            "  Citation: "
            + evidence["evidence"][0]["references"][0]["title"]
        )
        print("\nThe four JSON tools expose the same Snapshot to people and agents.")
        print("This is a development corpus, not external-review-qualified evidence.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Chromatic Homology Atlas")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="rebuild the 42-space snapshot and show a tour")
    tool_parser = subparsers.add_parser("tool", help="execute one stable JSON tool request")
    tool_parser.add_argument("request", help='JSON object with "tool" and "arguments"')
    args = parser.parse_args()
    if args.command == "demo":
        demo(args.db)
        return 0
    if not args.db.exists():
        ChromaticDatabase.build(args.db)
    with closing(sqlite3.connect(args.db)) as connection:
        snapshot_id = connection.execute(
            "SELECT snapshot_id FROM snapshot"
        ).fetchone()[0]
    try:
        request = json.loads(args.request)
    except json.JSONDecodeError as error:
        print_json(
            {
                "outcome": "invalid_json",
                "snapshot_id": snapshot_id,
                "reason": str(error),
            }
        )
        return 2
    with ChromaticTools(args.db) as tools:
        print_json(tools.call(request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
