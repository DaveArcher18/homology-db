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
COMPUTED_HOMOLOGY_SCHEMA_VERSION = "homology-db.computed-homology/1"
COMPUTED_RINGS_MANIFEST_VERSION = "homology-db.computed-rings-manifest/1"
SIMPLICIAL_MODEL_VERSION = "homology-db.simplicial-model/1"
COMPUTED_RINGS_REVIEW_STATE = "imported_unreviewed"
CANONICALIZATION = "cohomology-tables/canonical-facets/1"

IMPORTED_MODELS_VERSION = "homology-db.imported-models/1"

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
    "lutz-manifold-page": {
        "title": "Frank H. Lutz, The Manifold Page: geometric 3-manifold catalogues",
        "authors": ["Frank H. Lutz"],
        "publication_year": 2017,
        "url": "https://www3.math.tu-berlin.de/IfM/Nachrufe/Frank_Lutz/stellar/",
        "source_kind": "unlicensed_author_catalogue",
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

    # Models whose source states no licence are identified, never shipped, so there
    # is no facet list to re-derive here (ADR 0005, point 4). What can still be
    # checked is that the descriptor is well formed and that its f-vector Euler
    # characteristic matches the alternating sum of its Betti numbers.
    identified_path = manifest.get("identified_models_path")
    if identified_path:
        payload = json.loads((_ROOT / identified_path).read_text())
        if payload.get("schema_version") != IMPORTED_MODELS_VERSION:
            raise ValueError("unsupported imported-model schema version")
        for model in payload["models"]:
            space_id = model["space_id"]
            if space_id in models:
                raise ValueError(f"{space_id} is both checked in and identified only")
            descriptor = model["model"]
            if descriptor.get("redistribution") != "identified_not_redistributed":
                raise ValueError(f"identified model {space_id} does not declare its redistribution")
            f_vector = descriptor["f_vector"]
            euler_faces = sum((-1) ** degree * count for degree, count in enumerate(f_vector))
            euler_groups = sum((-1) ** row["degree"] * row["free_rank"]
                               for row in model["integral_homology"])
            if euler_faces != euler_groups:
                raise ValueError(
                    f"identified model {space_id} has f-vector Euler characteristic "
                    f"{euler_faces} but recorded Betti numbers give {euler_groups}")
            models[space_id] = {
                "model_id": descriptor["model_id"],
                "space_id": space_id,
                "facets_sha256": descriptor["facets_sha256"],
                "f_vector": f_vector,
                "vertices": descriptor["vertices"],
                "redistribution": "identified_only",
            }

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

    homology: dict[str, list[dict[str, Any]]] = {}
    for record in corpus.get("homology", []):
        validate_computed_homology_record(record, COMPUTED_RING_SOURCES)
        space_id = record["space_id"]
        if space_id not in models:
            raise ValueError(f"computed homology for {space_id} has no pinned model")
        homology.setdefault(space_id, []).append(record)
    for space_id, entries in homology.items():
        if sorted(record["coefficient"] for record in entries) != sorted(COHOMOLOGY_RING_COEFFICIENTS):
            raise ValueError(f"computed homology for {space_id} does not cover every coefficient once")
    if set(homology) != set(records):
        raise ValueError("every space with computed rings must carry computed homology")

    # Every identified model is available to bind a record, but only the ones a
    # record actually names are part of the corpus the atlas projects.
    used = {model_id: summary for model_id, summary in models.items() if model_id in records}
    missing = sorted(set(records) - set(used))
    if missing:
        raise ValueError(f"computed rings without a pinned model: {missing}")
    return {"manifest": manifest, "models": used, "records": records, "homology": homology}


def computed_ring_records() -> dict[str, list[dict[str, Any]]]:
    """Fresh, validated computed records keyed by space; callers cannot mutate a cache."""
    return load_computed_rings()["records"]


def validate_computed_homology_record(record: dict[str, Any], sources: dict[str, Any]) -> None:
    """Check an imported homology record for internal consistency.

    This never establishes the homology of a space. The atlas computes that from
    its own cellular models; an imported record is a second, independent
    calculation from a pinned triangulation, and its value is precisely that it
    can disagree. Agreement is checked against the owned rows elsewhere.
    """
    if record.get("schema_version") != COMPUTED_HOMOLOGY_SCHEMA_VERSION:
        raise ValueError("unsupported computed homology schema version")
    coefficient = record.get("coefficient")
    if coefficient not in COHOMOLOGY_RING_COEFFICIENTS:
        raise ValueError("unsupported computed homology coefficient")
    characteristic = 0 if coefficient in ("Z", "Q") else int(coefficient[1:])
    if _integer(record.get("characteristic"), "characteristic", 0) != characteristic:
        raise ValueError("coefficient characteristic mismatch")
    space_id = record.get("space_id")
    if record.get("record_id") != f"computed-homology:{space_id}:{coefficient}:v1":
        raise ValueError("record identity mismatch")
    if (record.get("theory"), record.get("convention"), record.get("knowledge_state")) != (
        "ordinary_homology", "unreduced", "exact"
    ):
        raise ValueError("ordinary unreduced exact homology is required")
    coverage = record["coverage"]
    through = _integer(coverage.get("through_degree"), "coverage through_degree", 0)
    if coverage != {"kind": "complete_finite", "through_degree": through,
                    "upper_vanishing_starts_at": through + 1}:
        raise ValueError("complete finite coverage must declare its upper vanishing bound")
    groups = record["groups"]
    if [group["degree"] for group in groups] != list(range(through + 1)):
        raise ValueError("homology degrees must be dense and ordered through the coverage")
    for group in groups:
        if coefficient == "Z":
            _integer(group["free_rank"], "free rank", 0)
            for order in group["torsion_orders"]:
                _integer(order, "torsion order", 2)
            if "dimension" in group:
                raise ValueError("integral homology reports free rank and torsion, not a dimension")
        else:
            _integer(group["dimension"], "dimension", 0)
            if "torsion_orders" in group:
                raise ValueError("field homology carries no torsion")
    provenance = record["provenance"]
    if provenance.get("kind") != "external_engine_computation":
        raise ValueError("the computed corpus is the machine-computed subset")
    if provenance.get("review_state") != COMPUTED_RINGS_REVIEW_STATE:
        raise ValueError("importing is not reviewing; the review state may not be promoted here")
    if not record.get("sources"):
        raise ValueError("a computed homology record must cite its evidence")
    for source in record["sources"]:
        if source.get("source_id") not in sources:
            raise ValueError("source requires a resolvable ID")


def compare_homology_to_owned(
    imported: dict[tuple[str, str], list[dict[str, Any]]],
    owned: dict[tuple[str, str], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Confirm each imported homology matches the atlas's own, and refuse drift.

    The imported calculation runs on a triangulation while the atlas computes
    from a cellular model, so agreement is real evidence that the pinned model
    presents the space the rings are attached to. Disagreement is a conflict
    about that binding and fails the build rather than being ranked away.
    """
    confirmed = []
    for key in sorted(imported):
        if key not in owned:
            raise ValueError(f"imported homology for {key[0]} over {key[1]} has no owned rows to check")
        if imported[key] != owned[key]:
            raise ValueError(
                f"imported homology for {key[0]} over {key[1]} disagrees with this repository's "
                f"own cellular homology; the model binding is in conflict and must be resolved"
            )
        confirmed.append({"space_id": key[0], "coefficient": key[1]})
    return confirmed


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
