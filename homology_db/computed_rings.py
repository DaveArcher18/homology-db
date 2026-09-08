"""The machine-computed subset of the cohomology ring corpus.

These rings were computed by an external computer algebra system from explicit
finite simplicial models, and are imported rather than reproduced here.  The
model each ring was computed from is checked in beside it, because the Sage
constructors that generate these surfaces do not reproduce their vertex
labelling between processes: pinning the recipe alone would not identify the
model, so the facets themselves are pinned, following the precedent of
`corpus/chromatic-v1/poincare-sphere-facets.json`.

What this module derives rather than trusts is the integrity of each model --
canonical facet order, the recomputed facet hash, and that the simplicial
boundary squares to zero -- while the ring axioms are checked by the shared
validator in `cohomology_rings`.  What is left over, that these structure
constants really are the cup product of that model, stays imported evidence.
It is never recorded as this repository's own result, and importing is never
promoted into human review.
"""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from .cohomology_rings import (
    COHOMOLOGY_RING_COEFFICIENTS,
    validate_cohomology_ring_record,
)

COMPUTED_RINGS_CORPUS_VERSION = "homology-db.computed-rings-corpus/1"
COMPUTED_RINGS_MANIFEST_VERSION = "homology-db.computed-rings-manifest/1"
SIMPLICIAL_MODEL_VERSION = "homology-db.simplicial-model/1"
COMPUTED_RINGS_REVIEW_STATE = "imported_unreviewed"
CANONICALIZATION = "cohomology-tables/canonical-facets/1"

COMPUTED_RING_SOURCES = {
    "cohomology-tables": {
        "title": "cohomology-tables: cohomology rings and cup product tables for simplicial complexes",
        "authors": ["Wern Juin Gabriel Ong"],
        "publication_year": 2026,
        "url": "https://github.com/wgabrielong/cohomology-tables",
        "source_kind": "official_software_source",
    },
    "oscar": {
        "title": "OSCAR: Open Source Computer Algebra Research system",
        "authors": ["The OSCAR Team"],
        "publication_year": 2026,
        "url": "https://github.com/oscar-system/Oscar.jl",
        "source_kind": "official_software_source",
    },
    "sagemath": {
        "title": "SageMath simplicial complex examples",
        "authors": ["The SageMath Developers"],
        "publication_year": 2024,
        "url": "https://github.com/sagemath/sage",
        "source_kind": "official_software_source",
    },
}

_ROOT = Path(__file__).resolve().parents[1]
_CORPUS = _ROOT / "corpus" / "computed-rings-v1"


def _integer(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError(f"{label} must be an integer" + (f" >= {minimum}" if minimum is not None else ""))
    return value


def canonical_facets(facets: list[list[int]]) -> list[tuple[int, ...]]:
    """Facets as sorted vertex tuples in sorted order; duplicates are an error."""
    normalized = []
    for facet in facets:
        vertices = tuple(sorted(_integer(vertex, "facet vertex", 0) for vertex in facet))
        if len(set(vertices)) != len(vertices):
            raise ValueError("a facet repeats a vertex")
        normalized.append(vertices)
    if len(set(normalized)) != len(normalized):
        raise ValueError("the facet list repeats a facet")
    return sorted(normalized)


def facets_sha256(facets: list[tuple[int, ...]]) -> str:
    """The producer's canonical facet hash, recomputed here rather than trusted."""
    text = "\n".join(",".join(str(vertex) for vertex in facet) for facet in facets)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def face_complex(facets: list[tuple[int, ...]]) -> dict[int, list[tuple[int, ...]]]:
    """Every face of every facet, grouped by dimension and ordered."""
    faces: dict[int, set[tuple[int, ...]]] = {}
    for facet in facets:
        for size in range(1, len(facet) + 1):
            faces.setdefault(size - 1, set()).update(combinations(facet, size))
    return {degree: sorted(values) for degree, values in faces.items()}


def boundary_matrices(faces: dict[int, list[tuple[int, ...]]]) -> dict[int, list[list[int]]]:
    """d_n from n-faces to (n-1)-faces, with the alternating simplicial signs."""
    matrices: dict[int, list[list[int]]] = {}
    for degree in sorted(faces):
        if degree == 0:
            continue
        below = {face: index for index, face in enumerate(faces[degree - 1])}
        matrix = [[0] * len(faces[degree]) for _ in range(len(faces[degree - 1]))]
        for column, face in enumerate(faces[degree]):
            for position in range(len(face)):
                target = face[:position] + face[position + 1:]
                matrix[below[target]][column] += (-1) ** position
        matrices[degree] = matrix
    return matrices


def validate_simplicial_model(model: dict[str, Any]) -> dict[str, Any]:
    """Re-derive a checked-in triangulation rather than trusting its metadata."""
    if model.get("schema_version") != SIMPLICIAL_MODEL_VERSION:
        raise ValueError("unsupported simplicial model schema version")
    if model.get("canonicalization") != CANONICALIZATION:
        raise ValueError("unsupported facet canonicalization rule")
    facets = canonical_facets(model["facets"])
    if facets != [tuple(facet) for facet in model["facets"]]:
        raise ValueError("checked-in facets are not in canonical order")
    vertices = sorted({vertex for facet in facets for vertex in facet})
    if vertices != list(range(len(vertices))):
        raise ValueError("canonical models use consecutive 0-based vertex labels")
    if _integer(model["vertices"], "vertex count", 0) != len(vertices):
        raise ValueError("recorded vertex count does not match the facet list")
    if facets_sha256(facets) != model.get("facets_sha256"):
        raise ValueError("recomputed facet hash does not match the recorded one")
    faces = face_complex(facets)
    matrices = boundary_matrices(faces)
    for degree in sorted(matrices):
        if degree - 1 not in matrices:
            continue
        lower, upper = matrices[degree - 1], matrices[degree]
        for column in range(len(upper[0]) if upper else 0):
            for row in range(len(lower)):
                if sum(lower[row][k] * upper[k][column] for k in range(len(upper))):
                    raise ValueError(f"d_{degree - 1} d_{degree} is not zero")
    return {
        "model_id": model["model_id"],
        "space_id": model["space_id"],
        "facets_sha256": model["facets_sha256"],
        "f_vector": [len(faces[degree]) for degree in sorted(faces)],
    }


def load_computed_rings() -> dict[str, Any]:
    """Load, re-verify and return the computed corpus with its pinned models."""
    manifest = json.loads((_CORPUS / "manifest.json").read_text())
    if manifest.get("schema_version") != COMPUTED_RINGS_MANIFEST_VERSION:
        raise ValueError("unsupported computed rings manifest version")
    if manifest.get("review_state") != COMPUTED_RINGS_REVIEW_STATE:
        raise ValueError("importing is not reviewing; the corpus review state may not be promoted")

    rings_path = _ROOT / manifest["rings_path"]
    rings_bytes = rings_path.read_bytes()
    if hashlib.sha256(rings_bytes).hexdigest() != manifest["rings_sha256"]:
        raise ValueError("computed rings file does not match the hash pinned in its manifest")
    corpus = json.loads(rings_bytes)
    if corpus.get("schema_version") != COMPUTED_RINGS_CORPUS_VERSION:
        raise ValueError("unsupported computed rings corpus version")

    models = {}
    for entry in manifest["models"]:
        path = _ROOT / entry["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"model artifact {entry['path']} does not match its pinned hash")
        summary = validate_simplicial_model(json.loads(path.read_text()))
        if summary["facets_sha256"] != entry["facets_sha256"]:
            raise ValueError(f"model {summary['model_id']} disagrees with the manifest facet hash")
        models[summary["space_id"]] = summary

    records: dict[str, list[dict[str, Any]]] = {}
    for record in corpus["records"]:
        validate_cohomology_ring_record(record, COMPUTED_RING_SOURCES)
        space_id = record["space_id"]
        if space_id not in models:
            raise ValueError(f"computed ring for {space_id} has no pinned model")
        provenance = record["provenance"]
        if provenance["model_id"] != models[space_id]["model_id"]:
            raise ValueError(f"computed ring for {space_id} names an unknown model")
        if provenance["model_facets_sha256"] != models[space_id]["facets_sha256"]:
            raise ValueError(f"computed ring for {space_id} is bound to a different model")
        records.setdefault(space_id, []).append(record)

    for space_id, entries in records.items():
        coefficients = [record["coefficient"] for record in entries]
        if sorted(coefficients) != sorted(COHOMOLOGY_RING_COEFFICIENTS):
            raise ValueError(f"computed rings for {space_id} do not cover every coefficient once")

    return {"manifest": manifest, "models": models, "records": records}


def computed_ring_records() -> dict[str, list[dict[str, Any]]]:
    """Fresh, validated computed records keyed by space; callers cannot mutate a cache."""
    return load_computed_rings()["records"]


def validate_computed_projection(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Validate computed records as they appear in the atlas, not as stored.

    The exporter embeds these records verbatim, so re-validating the projection
    catches an atlas whose rings drifted from the corpus that produced them.
    """
    for space_id, entries in records.items():
        coefficients = [record["coefficient"] for record in entries]
        if sorted(coefficients) != sorted(COHOMOLOGY_RING_COEFFICIENTS):
            raise ValueError(f"computed rings for {space_id} do not cover every coefficient once")
        for record in entries:
            if record["space_id"] != space_id:
                raise ValueError("computed record is attached to the wrong space")
            if record["provenance"]["kind"] != "external_engine_computation":
                raise ValueError("the computed corpus is the machine-computed subset")
            validate_cohomology_ring_record(record, COMPUTED_RING_SOURCES)
    return {
        "space_count": len(records),
        "record_count": sum(len(items) for items in records.values()),
        "review_state": COMPUTED_RINGS_REVIEW_STATE,
    }
