#!/usr/bin/env python3
"""Export the Chromatic Homology Atlas as one self-contained document."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from collections import defaultdict
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from homology_db.chromatic import COEFFICIENTS, ChromaticTools


SOURCE_DIRECTORY = REPOSITORY_ROOT / "static_atlas"
READ_MODEL_VERSION = "homology-db.static-atlas/3"
THEORY_ID = "ordinary_homology"
MAX_HTML_BYTES = 5 * 1024 * 1024
DEFINITION_REVISION = 1
DEFINITIONS = (
    {
        "id": "conceptual-space",
        "term": "Conceptual space",
        "body": (
            "The mathematical subject being studied, independently of any particular "
            "presentation used to calculate it. Atlas editorial glossary v1; this "
            "explanation is not Evidence for a database assertion."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "ordinary-homology",
        "term": "Ordinary homology",
        "body": (
            "A sequence of abelian groups, or modules after choosing coefficients, that "
            "records holes in each degree and is invariant under homotopy equivalence. "
            "Atlas editorial glossary v1; this general explanation does not supply the "
            "Snapshot's missing versioned homology-convention metadata and is not Evidence "
            "for a database assertion."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "coefficient-ring",
        "term": "Coefficient ring",
        "body": (
            "The ring used for the homology groups shown in a table, such as the integers "
            "or a finite field. Atlas editorial glossary v1; this explanation is not "
            "Evidence for a database assertion."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "reduced-homology",
        "term": "Reduced homology",
        "body": (
            "The based normalization of ordinary homology that removes the distinguished "
            "degree-zero free summand of a nonempty connected space. Atlas editorial "
            "glossary v1; this explanation is not Evidence for a database assertion or a "
            "replacement for versioned convention metadata."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "finite-cw-space",
        "term": "Finite CW space",
        "body": (
            "A space presented by attaching finitely many cells in increasing dimensions. "
            "Atlas editorial glossary v1; this explanation is not Evidence that a "
            "particular recorded Model is finite or qualified."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "direct-sum-notation",
        "term": "Direct-sum notation",
        "body": (
            "The superscript 'direct sum r' on a group or module A means the direct sum "
            "of r copies of A. Atlas editorial glossary v1; this notation guide is not "
            "Evidence for any displayed multiplicity."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "model",
        "term": "Model",
        "body": (
            "A concrete CW, simplicial, or other qualified presentation used to calculate "
            "properties of a Conceptual space. Atlas editorial glossary v1; this "
            "explanation is not itself a qualified Model or Evidence for an assertion."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "evidence",
        "term": "Evidence",
        "body": (
            "A provenance record that connects a database assertion to a qualified Model, "
            "calculation, and citations. Atlas editorial glossary v1; this explanatory "
            "definition is not itself Evidence for another assertion."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "coverage",
        "term": "Homology coverage",
        "body": (
            "The degree range for which the Snapshot records homology, together with any "
            "explicit upper-vanishing claim. Atlas editorial glossary v1; this explanation "
            "is not Evidence for a particular exhaustive or bounded coverage record."
        ),
        "scope": "exposition",
        "assertion_evidence": False,
    },
)
SOURCE_REVISION_INPUTS = (
    "corpus/chromatic-v1/manifest.json",
    "corpus/chromatic-v1/poincare-sphere-facets.json",
    "homology_db/__init__.py",
    "homology_db/chromatic.py",
    "homology_db/preview.py",
    "scripts/export_static_atlas.py",
    "static_atlas/atlas.css",
    "static_atlas/atlas.js",
    "static_atlas/index.template.html",
    "static_atlas/presentation.js",
)


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_inputs_sha256() -> str:
    """Hash exact input paths and bytes, including uncommitted content."""
    hasher = hashlib.sha256()
    for relative_path in SOURCE_REVISION_INPUTS:
        encoded_path = relative_path.encode("utf-8")
        contents = (REPOSITORY_ROOT / relative_path).read_bytes()
        hasher.update(len(encoded_path).to_bytes(8, "big"))
        hasher.update(encoded_path)
        hasher.update(len(contents).to_bytes(8, "big"))
        hasher.update(contents)
    return hasher.hexdigest()


def source_tree_state() -> str:
    completed = subprocess.run(
        [
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            *SOURCE_REVISION_INPUTS,
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return "unknown"
    return "dirty" if completed.stdout.strip() else "clean"


def source_revision(format_string: str) -> str | None:
    completed = subprocess.run(
        [
            "git",
            "log",
            "-1",
            f"--format={format_string}",
            "--",
            *SOURCE_REVISION_INPUTS,
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def source_commit() -> str | None:
    return source_revision("%H")


def source_commit_timestamp() -> int | None:
    timestamp = source_revision("%ct")
    if timestamp is None:
        return None
    try:
        return int(timestamp)
    except ValueError:
        return None


def build_current_database(database_path: Path) -> None:
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "from homology_db.chromatic import ChromaticDatabase; "
                "ChromaticDatabase.build(Path(__import__('sys').argv[1]))"
            ),
            str(database_path),
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "could not build current Snapshot")


def slug_from_id(stable_id: str) -> str:
    slug = "".join(character if character.isalnum() else "-" for character in stable_id)
    return "-".join(part for part in slug.casefold().split("-") if part)


def conceptual_space_tex(space: dict[str, Any]) -> str:
    """Return a deterministic TeX display name for a curated Conceptual space."""
    family = space["family"]
    parameters = space["parameters"]

    if family == "point":
        return r"\ast"
    if family == "sphere":
        return rf"S^{{{int(parameters['n'])}}}"
    if family == "homology_sphere":
        return r"\Sigma_{\mathrm{P}}^{3}"
    if family == "wedge":
        return rf"S^{{{int(parameters['a'])}}}\vee S^{{{int(parameters['b'])}}}"
    if family == "surface":
        if parameters["kind"] == "torus":
            return r"T^{2}"
        if parameters["kind"] == "klein_bottle":
            return r"\mathrm{K}"
    if family == "real_projective_space":
        return rf"\mathbb{{R}}P^{{{int(parameters['n'])}}}"
    if family == "hopf_projective_plane":
        algebra = {
            "complex": "C",
            "quaternionic": "H",
            "octonionic": "O",
        }.get(parameters["division_algebra"])
        if algebra is not None:
            return rf"\mathbb{{{algebra}}}P^{{2}}"
    if family == "moore_space":
        return (
            rf"M(\mathbb{{Z}}/{int(parameters['m'])},"
            rf"{int(parameters['n'])})"
        )
    if family == "lens_space":
        weights = ",".join(str(int(weight)) for weight in parameters["weights"])
        return rf"L^{{{int(space['dimension'])}}}({int(parameters['p'])};{weights})"
    if family == "stunted_projective_space":
        field = "R" if parameters["kind"] == "real" else "C"
        bottom = int(parameters["bottom"])
        top = int(parameters["top"])
        return (
            rf"\mathbb{{{field}}}P^{{{top}}}/"
            rf"\mathbb{{{field}}}P^{{{bottom - 1}}}"
        )
    if family == "compact_lie_group":
        return rf"\mathrm{{{parameters['group']}}}({int(parameters['rank'])})"
    if family == "schubert_space":
        if parameters["kind"] == "complete_flag_c3":
            return r"\mathrm{Fl}_{3}(\mathbb{C})"
        if parameters["kind"] == "grassmannian_2_c4":
            return r"\mathrm{Gr}_{2}(\mathbb{C}^{4})"
    if family == "cyclic_classifying_space":
        return rf"B(C_{{{int(parameters['p'])}}})"
    if family == "elementary_abelian_classifying_space":
        return (
            rf"B(C_{{{int(parameters['p'])}}}"
            rf"^{{{int(parameters['rank'])}}})"
        )
    if family == "infinite_projective_space":
        field = "C" if parameters["division_algebra"] == "complex" else "H"
        return rf"\mathbb{{{field}}}P^{{\infty}}"
    if family == "unitary_classifying_space":
        return rf"BU({int(parameters['n'])})"
    if family == "thom_space":
        rank = int(parameters["rank"])
        return rf"\operatorname{{Th}}(\gamma_{{{rank}}}\to BU({rank}))"
    raise ValueError(
        f"no TeX display-name rule for Conceptual space {space['space_id']}"
    )


def group_projection(group: dict[str, Any], coefficient: str) -> dict[str, Any]:
    knowledge_state = group["knowledge_state"]
    if knowledge_state != "exact":
        return {
            "state": knowledge_state,
            "plain": knowledge_state.replace("_", " "),
        }
    value = group["value"]
    if coefficient == "Z":
        return {
            "state": "exact",
            "plain": value["display"],
            "free_rank": value["free_rank"],
            "torsion_orders": value["torsion_orders"],
        }
    return {
        "state": "exact",
        "plain": value["display"],
        "dimension": value["dimension"],
    }


def validate_read_model(
    atlas: dict[str, Any], *, allow_malformed_for_review: bool = False
) -> None:
    definitions = atlas.get("definitions")
    if not isinstance(definitions, list) or not definitions:
        raise ValueError("static atlas needs a nonempty definitions catalog")
    required_definition_fields = {
        "id",
        "term",
        "body",
        "scope",
        "assertion_evidence",
        "revision",
        "selected_for_snapshot_id",
    }
    definition_ids: list[str] = []
    for definition in definitions:
        if not isinstance(definition, dict) or set(definition) != required_definition_fields:
            raise ValueError("static atlas contains a malformed definition")
        definition_id = definition["id"]
        if not isinstance(definition_id, str) or re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", definition_id
        ) is None:
            raise ValueError("static atlas contains an invalid definition ID")
        definition_ids.append(definition_id)
        if not all(
            isinstance(definition[field], str) and bool(definition[field].strip())
            for field in ("term", "body")
        ):
            raise ValueError(f"definition {definition_id} is missing explanatory text")
        if (
            definition["scope"] != "exposition"
            or definition["assertion_evidence"] is not False
        ):
            raise ValueError(
                f"definition {definition_id} must remain non-evidentiary exposition"
            )
        if definition["revision"] != DEFINITION_REVISION:
            raise ValueError(
                f"definition {definition_id} has an unsupported editorial revision"
            )
        if definition["selected_for_snapshot_id"] != atlas["snapshot"]["snapshot_id"]:
            raise ValueError(
                f"definition {definition_id} is not selected for this Snapshot"
            )
    if len(definition_ids) != len(set(definition_ids)):
        raise ValueError("static atlas contains duplicate definition IDs")

    conceptual_spaces = atlas["conceptual_spaces"]
    conceptual_space_ids = [item["id"] for item in conceptual_spaces]
    slugs = [item["slug"] for item in conceptual_spaces]
    if len(conceptual_space_ids) != len(set(conceptual_space_ids)):
        raise ValueError("static atlas contains duplicate stable Conceptual-space IDs")
    if len(slugs) != len(set(slugs)):
        raise ValueError("static atlas contains duplicate Conceptual-space slugs")
    required_fields = (
        "id",
        "slug",
        "kind",
        "name",
        "summary",
        "chromatic_relevance",
        "taxonomy",
        "homology",
        "homology_coverage",
    )
    malformed_spaces = []
    for conceptual_space in conceptual_spaces:
        missing = [field for field in required_fields if not conceptual_space.get(field)]
        if missing:
            malformed_spaces.append(f"{conceptual_space.get('id', '<missing id>')}: {missing}")
        name = conceptual_space.get("name")
        if not isinstance(name, dict) or not all(
            isinstance(name.get(field), str) and bool(name[field].strip())
            for field in ("plain", "tex")
        ):
            malformed_spaces.append(
                f"{conceptual_space.get('id', '<missing id>')}: invalid display name"
            )
        if conceptual_space["data_quality"]["missing_required_fields"]:
            malformed_spaces.append(
                f"{conceptual_space['id']}: "
                f"{conceptual_space['data_quality']['missing_required_fields']}"
            )
    if malformed_spaces and not allow_malformed_for_review:
        raise ValueError(f"malformed Conceptual-space records: {malformed_spaces}")

    sections = atlas["sections"]
    section_ids = [section["id"] for section in sections]
    if len(section_ids) != len(set(section_ids)):
        raise ValueError("static atlas contains duplicate family section IDs")
    sections_by_id = {section["id"]: section for section in sections}
    for section in sections:
        if not all(
            isinstance(section.get(field), str) and bool(section[field])
            for field in ("id", "label", "summary", "chromatic_relevance")
        ):
            raise ValueError(f"family section {section.get('id')} is malformed")
    known_ids = set(conceptual_space_ids)
    relation_ids: set[str] = set()
    section_space_ids = [
        conceptual_space_id
        for section in sections
        for conceptual_space_id in section["conceptual_space_ids"]
    ]
    if len(section_space_ids) != len(set(section_space_ids)):
        raise ValueError("static atlas family sections contain a Conceptual space more than once")
    if sorted(section_space_ids) != sorted(conceptual_space_ids):
        raise ValueError("static atlas sections must contain every Conceptual space exactly once")
    for conceptual_space in conceptual_spaces:
        family = conceptual_space["taxonomy"]["family"]
        if family not in sections_by_id:
            raise ValueError(
                f"Conceptual space {conceptual_space['id']} belongs to unknown family {family}"
            )
        if conceptual_space["id"] not in sections_by_id[family]["conceptual_space_ids"]:
            raise ValueError(
                f"Conceptual space {conceptual_space['id']} is not in its family section {family}"
            )

        dimension = next(
            (
                property_["value"]
                for property_ in conceptual_space["properties"]
                if property_["key"] == "dimension"
            ),
            None,
        )
        coverage = conceptual_space["homology_coverage"]
        computed_through_degree = coverage["computed_through_degree"]
        if (
            not isinstance(computed_through_degree, int)
            or isinstance(computed_through_degree, bool)
            or computed_through_degree < 0
        ):
            raise ValueError(
                f"Conceptual space {conceptual_space['id']} has an invalid coverage bound"
            )
        if conceptual_space["infinite_finite_type"]:
            if dimension is not None:
                raise ValueError(
                    f"finite-type space {conceptual_space['id']} must have null dimension"
                )
            if coverage["kind"] != "bounded_through_degree":
                raise ValueError(
                    f"finite-type space {conceptual_space['id']} has invalid coverage kind"
                )
            if coverage["upper_vanishing_starts_at"] is not None:
                raise ValueError(
                    f"finite-type space {conceptual_space['id']} makes an upper-vanishing claim"
                )
            if computed_through_degree != atlas["snapshot"]["materialized_through_degree"]:
                raise ValueError(
                    f"finite-type space {conceptual_space['id']} disagrees with the Snapshot bound"
                )
        else:
            if not isinstance(dimension, int) or isinstance(dimension, bool):
                raise ValueError(
                    f"finite CW space {conceptual_space['id']} needs an integer dimension"
                )
            if coverage["kind"] != "complete_finite_cw":
                raise ValueError(
                    f"finite CW space {conceptual_space['id']} has invalid coverage kind"
                )
            if coverage["upper_vanishing_starts_at"] != dimension + 1:
                raise ValueError(
                    f"finite CW space {conceptual_space['id']} has an invalid "
                    "upper-vanishing bound"
                )
            if computed_through_degree != dimension:
                raise ValueError(
                    f"finite CW space {conceptual_space['id']} has incomplete degree coverage"
                )

        for row in conceptual_space["homology"]:
            group = row.get("group")
            if not isinstance(group, dict) or group.get("state") != row.get(
                "knowledge_state"
            ):
                raise ValueError(
                    f"Conceptual space {conceptual_space['id']} has a malformed "
                    "Homology group projection"
                )
            if group["state"] != "exact":
                if not isinstance(group.get("plain"), str) or not group["plain"]:
                    raise ValueError(
                        f"Conceptual space {conceptual_space['id']} has an invalid "
                        "non-exact Homology state"
                    )
                continue
            if row["coefficient_ring"] == "Z":
                free_rank = group.get("free_rank")
                torsion_orders = group.get("torsion_orders")
                if (
                    not isinstance(free_rank, int)
                    or isinstance(free_rank, bool)
                    or free_rank < 0
                    or not isinstance(torsion_orders, list)
                    or any(
                        not isinstance(order, int)
                        or isinstance(order, bool)
                        or order < 2
                        for order in torsion_orders
                    )
                ):
                    raise ValueError(
                        f"Conceptual space {conceptual_space['id']} has malformed "
                        "exact integral Homology data"
                    )
            else:
                field_dimension = group.get("dimension")
                if (
                    not isinstance(field_dimension, int)
                    or isinstance(field_dimension, bool)
                    or field_dimension < 0
                ):
                    raise ValueError(
                        f"Conceptual space {conceptual_space['id']} has malformed "
                        "exact field Homology data"
                    )

        expected_degrees = set(range(computed_through_degree + 1))
        for coefficient in atlas["snapshot"]["supported_coefficients"]:
            for reduced in (False, True):
                recorded_degrees = {
                    row["degree"]
                    for row in conceptual_space["homology"]
                    if row["coefficient_ring"] == coefficient
                    and row["reduced"] is reduced
                }
                if recorded_degrees != expected_degrees:
                    raise ValueError(
                        f"Conceptual space {conceptual_space['id']} has incomplete "
                        f"{coefficient} homology through degree {computed_through_degree}"
                    )

        if not conceptual_space["models"]:
            raise ValueError(f"Conceptual space {conceptual_space['id']} has no qualified Model")
        if not conceptual_space["evidence"]:
            raise ValueError(f"Conceptual space {conceptual_space['id']} has no Evidence")

    evidence_ids = {
        evidence["id"] for item in conceptual_spaces for evidence in item["evidence"]
    }
    evidence_id_list = [
        evidence["id"] for item in conceptual_spaces for evidence in item["evidence"]
    ]
    if len(evidence_id_list) != len(evidence_ids):
        raise ValueError("static atlas contains duplicate Evidence IDs")
    referenced_evidence = {
        evidence_id
        for item in conceptual_spaces
        for row in item["homology"]
        for evidence_id in row["evidence_ids"]
    }
    missing_evidence = sorted(referenced_evidence - evidence_ids)
    if missing_evidence:
        raise ValueError(f"unresolved evidence references: {missing_evidence}")
    computation_ids = {
        computation["id"]
        for item in conceptual_spaces
        for computation in item["computations"]
    }
    computation_id_list = [
        computation["id"]
        for item in conceptual_spaces
        for computation in item["computations"]
    ]
    if len(computation_id_list) != len(computation_ids):
        raise ValueError("static atlas contains duplicate Computation IDs")
    referenced_computations = {
        computation_id
        for item in conceptual_spaces
        for row in item["homology"]
        for computation_id in row["computation_ids"]
    }
    missing_computations = sorted(referenced_computations - computation_ids)
    if missing_computations:
        raise ValueError(f"unresolved computation references: {missing_computations}")

    for conceptual_space in conceptual_spaces:
        model_by_id = {model["id"]: model for model in conceptual_space["models"]}
        if len(model_by_id) != len(conceptual_space["models"]):
            raise ValueError(
                f"Conceptual space {conceptual_space['id']} contains duplicate Model IDs"
            )
        local_evidence_ids = {evidence["id"] for evidence in conceptual_space["evidence"]}
        for relation in conceptual_space["relations"]:
            required_relation_fields = (
                "id",
                "source_id",
                "type",
                "target_id",
                "detail",
            )
            if any(not relation.get(field) for field in required_relation_fields):
                raise ValueError(
                    f"relation {relation.get('id', '<missing id>')} is malformed"
                )
            if relation["id"] in relation_ids:
                raise ValueError(f"duplicate relation ID {relation['id']}")
            relation_ids.add(relation["id"])
            if relation["source_id"] != conceptual_space["id"]:
                raise ValueError(
                    f"relation {relation['id']} is attached to the wrong source space"
                )
            unresolved_evidence = sorted(
                set(relation["evidence_ids"]) - local_evidence_ids
            )
            if unresolved_evidence:
                raise ValueError(
                    f"relation {relation['id']} references unresolved Evidence: "
                    + ", ".join(unresolved_evidence)
                )
        for model in conceptual_space["models"]:
            if model["space_id"] != conceptual_space["id"]:
                raise ValueError(
                    f"Model {model['id']} is attached to the wrong Conceptual space"
                )
            if model["status"] != "qualified":
                raise ValueError(f"Model {model['id']} is not qualified")
            required_model_fields = (
                "id",
                "space_id",
                "kind",
                "status",
                "name",
                "construction",
                "cell_degrees",
                "attaching_map",
                "boundary_formula",
                "chain_sha256",
                "model_scope",
            )
            if any(not model.get(field) for field in required_model_fields):
                raise ValueError(f"Model {model['id']} is missing required data")
            if model["artifact_path"] is not None:
                artifact_sha256 = model["artifact_sha256"]
                if (
                    not isinstance(artifact_sha256, str)
                    or len(artifact_sha256) != 64
                    or any(
                        character not in "0123456789abcdef"
                        for character in artifact_sha256
                    )
                ):
                    raise ValueError(f"Model {model['id']} has an invalid artifact SHA-256")
                artifact_path = (REPOSITORY_ROOT / model["artifact_path"]).resolve()
                if (
                    not artifact_path.is_relative_to(REPOSITORY_ROOT)
                    or not artifact_path.is_file()
                ):
                    raise ValueError(f"Model {model['id']} has an unresolved artifact path")
                if file_sha256(artifact_path) != artifact_sha256:
                    raise ValueError(f"Model {model['id']} artifact SHA-256 does not match")
        for evidence in conceptual_space["evidence"]:
            if evidence["space_id"] != conceptual_space["id"]:
                raise ValueError(
                    f"Evidence {evidence['id']} is attached to the wrong Conceptual space"
                )
            model = model_by_id.get(evidence["model_id"])
            if model is None:
                raise ValueError(
                    f"Evidence {evidence['id']} references an unresolved Model"
                )
            if evidence["chain_sha256"] != model["chain_sha256"]:
                raise ValueError(
                    f"Evidence {evidence['id']} and Model {model['id']} disagree on input SHA-256"
                )
            if not evidence["citations"]:
                raise ValueError(f"Evidence {evidence['id']} has no cited source")
            if not evidence["kind"] or not evidence["computation_sketch"]:
                raise ValueError(f"Evidence {evidence['id']} lacks its kind or sketch")
            for citation in evidence["citations"]:
                if not all(
                    citation.get(field)
                    for field in ("id", "authors", "title", "year", "source_kind")
                ):
                    raise ValueError(
                        f"citation {citation.get('id')} is missing required metadata"
                    )
                parsed_url = urlparse(citation["url"])
                if parsed_url.scheme != "https" or not parsed_url.netloc:
                    raise ValueError(
                        f"citation {citation['id']} has a non-HTTPS source URL"
                    )
                if not citation["locator"] or not citation["role"]:
                    raise ValueError(
                        f"citation {citation['id']} lacks a role or source locator"
                    )
        for computation in conceptual_space["computations"]:
            if computation["evidence_id"] not in local_evidence_ids:
                raise ValueError(
                    f"Computation {computation['id']} references unresolved Evidence"
                )
            evidence = next(
                item
                for item in conceptual_space["evidence"]
                if item["id"] == computation["evidence_id"]
            )
            if computation["input_sha256"] != evidence["chain_sha256"]:
                raise ValueError(
                    f"Computation {computation['id']} and its Evidence disagree on input SHA-256"
                )

    unresolved_relations = [
        relation
        for item in conceptual_spaces
        for relation in item["relations"]
        if relation.get("target_id") not in known_ids
    ]
    atlas["snapshot"]["unresolved_reference_count"] = len(unresolved_relations)


def _citation_projection(reference: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": reference["reference_id"],
        "authors": reference["authors"],
        "title": reference["title"],
        "year": reference["year"],
        "url": reference["url"],
        "source_kind": reference["source_kind"],
        "role": reference["role"],
        "locator": reference["locator"],
    }


def _model_projection(model: dict[str, Any], space_id: str) -> dict[str, Any]:
    return {
        "id": model["model_id"],
        "space_id": space_id,
        "kind": model["kind"],
        "status": model["status"],
        "name": model["name"],
        "construction": model["construction"],
        "cell_degrees": model["cell_degrees"],
        "cell_formula": model["cell_formula"],
        "attaching_map": model["attaching_map"],
        "boundary_formula": model["boundary_formula"],
        "chain_sha256": model["chain_sha256"],
        "model_scope": model["model_scope"],
        "artifact_path": model["artifact_path"],
        "artifact_sha256": model["artifact_sha256"],
    }


def build_read_model(
    database_path: Path, *, allow_malformed_for_review: bool = False
) -> dict[str, Any]:
    if not database_path.exists():
        raise FileNotFoundError(database_path)
    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"SQLite integrity failure: {integrity}")
        foreign_key_failures = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_failures:
            raise ValueError(
                "SQLite foreign-key failure: "
                + repr([tuple(row) for row in foreign_key_failures])
            )
        model_evidence_mismatches = connection.execute(
            """
            SELECT e.evidence_id, m.model_id
            FROM evidence e JOIN model m USING(model_id)
            WHERE e.space_id != m.space_id OR e.chain_sha256 != m.chain_sha256
            ORDER BY e.evidence_id
            """
        ).fetchall()
        if model_evidence_mismatches:
            raise ValueError(
                "Model/Evidence input mismatch: "
                + repr([tuple(row) for row in model_evidence_mismatches])
            )
        malformed_artifacts = connection.execute(
            """
            SELECT model_id
            FROM model
            WHERE (artifact_path IS NULL) != (artifact_sha256 IS NULL)
            ORDER BY model_id
            """
        ).fetchall()
        if malformed_artifacts:
            raise ValueError(
                "Model artifact path/hash mismatch: "
                + repr([row["model_id"] for row in malformed_artifacts])
            )
        snapshot_rows = connection.execute("SELECT * FROM snapshot").fetchall()
        if len(snapshot_rows) != 1:
            raise ValueError("static atlas requires exactly one Snapshot")
        snapshot_row = dict(snapshot_rows[0])
        families = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM family ORDER BY sort_order, family_id"
            )
        ]
        spaces = [
            dict(row)
            for row in connection.execute(
                """
                SELECT s.*
                FROM space s JOIN family f ON f.family_id = s.family
                ORDER BY f.sort_order, s.label, s.space_id
                """
            )
        ]
        aliases_by_space: dict[str, list[str]] = defaultdict(list)
        for row in connection.execute(
            "SELECT space_id, display_alias FROM alias ORDER BY display_alias, space_id"
        ):
            aliases_by_space[row["space_id"]].append(row["display_alias"])
        coverage_by_space = {
            row["space_id"]: {
                "kind": row["coverage_kind"],
                "computed_through_degree": row["computed_through_degree"],
                "upper_vanishing_starts_at": row["upper_vanishing_starts_at"],
                "detail": row["detail"],
            }
            for row in connection.execute(
                "SELECT * FROM homology_coverage ORDER BY space_id"
            )
        }
        relations_by_space: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in connection.execute(
            """
            SELECT relation_id, source_space_id, relation_type,
                   target_space_id, evidence_id, detail
            FROM space_relation
            ORDER BY source_space_id, relation_id
            """
        ):
            relations_by_space[row["source_space_id"]].append(
                {
                    "id": row["relation_id"],
                    "source_id": row["source_space_id"],
                    "type": row["relation_type"],
                    "target_id": row["target_space_id"],
                    "evidence_ids": [row["evidence_id"]],
                    "detail": row["detail"],
                }
            )

    conceptual_spaces: list[dict[str, Any]] = []
    evidence_total = 0
    homology_total = 0
    computation_total = 0
    model_total = 0
    citation_total = 0
    relation_total = 0
    with ChromaticTools(database_path) as tools:
        summary = tools.corpus_summary()
        if summary["subject_count"] != len(spaces):
            raise ValueError("Snapshot subject count does not match enumerated spaces")

        for raw_space in spaces:
            space = dict(raw_space)
            space["infinite_finite_type"] = bool(
                space["infinite_finite_type"]
            )
            space["parameters"] = json.loads(space.pop("parameters_json"))
            space["tags"] = json.loads(space.pop("tags_json"))
            space_id = space["space_id"]
            coverage = coverage_by_space.get(space_id)
            if coverage is None:
                raise ValueError(f"missing homology coverage for {space_id}")
            aliases = sorted(
                {
                    alias
                    for alias in aliases_by_space[space_id]
                    if alias not in {space_id, space["label"]}
                },
                key=lambda value: (value.casefold(), value),
            )
            homology: list[dict[str, Any]] = []
            raw_homology: list[dict[str, Any]] = []
            space_evidence_ids: set[str] = set()
            for coefficient in COEFFICIENTS:
                for reduced in (False, True):
                    response = tools.read_homology(
                        space_id, coefficient=coefficient, reduced=reduced
                    )
                    if response["outcome"] != "selected":
                        raise ValueError(
                            f"could not export {space_id} ({coefficient}, reduced={reduced})"
                        )
                    if response["subject"] != space:
                        raise ValueError(
                            f"homology response selected the wrong space for {space_id}"
                        )
                    if response["coverage"] != coverage:
                        raise ValueError(
                            "homology response coverage disagrees with the Snapshot "
                            f"for {space_id}"
                        )
                    raw_homology.append(response)
                    for group in response["groups"]:
                        space_evidence_ids.add(group["evidence_id"])
                        homology.append(
                            {
                                "theory": THEORY_ID,
                                "coefficient_ring": coefficient,
                                "coefficient_system": f"constant:{coefficient}",
                                "homology_convention": None,
                                "convention_state": "not_recorded_in_database_schema",
                                "reduced": reduced,
                                "degree": group["degree"],
                                "group": group_projection(group, coefficient),
                                "knowledge_state": group["knowledge_state"],
                                "value_scope": group["value_scope"],
                                "evidence_ids": [group["evidence_id"]],
                                "computation_ids": [],
                                "assertion_id": group["assertion_id"],
                            }
                        )

            expanded = tools.expand_evidence(sorted(space_evidence_ids))
            if expanded["outcome"] != "complete":
                raise ValueError(
                    f"unresolved evidence for {space_id}: {expanded['missing_evidence_ids']}"
                )
            evidence: list[dict[str, Any]] = []
            models_by_id: dict[str, dict[str, Any]] = {}
            computations: list[dict[str, Any]] = []
            citations_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
            computation_ids_by_evidence: dict[str, list[str]] = defaultdict(list)
            for item in expanded["evidence"]:
                model = _model_projection(item["model"], space_id)
                previous_model = models_by_id.setdefault(model["id"], model)
                if previous_model != model:
                    raise ValueError(f"conflicting Model projections for {model['id']}")
                citations = sorted(
                    (_citation_projection(reference) for reference in item["references"]),
                    key=lambda citation: (
                        citation["role"],
                        citation["id"],
                        citation["locator"],
                    ),
                )
                for citation in citations:
                    citations_by_key[
                        (citation["id"], citation["role"], citation["locator"])
                    ] = citation
                evidence.append(
                    {
                        "id": item["evidence_id"],
                        "space_id": item["space_id"],
                        "model_id": model["id"],
                        "kind": item["evidence_kind"],
                        "citation": "; ".join(
                            citation["title"] for citation in citations
                        ),
                        "citations": citations,
                        "locator": "; ".join(
                            citation["locator"] for citation in citations
                        ),
                        "reliability": item["reliability"],
                        "release_status": summary["release_status"],
                        "algorithm_id": item["algorithm_id"],
                        "chain_sha256": item["chain_sha256"],
                        "computation_sketch": item["computation_sketch"],
                        "representatives_state": item["representatives_state"],
                        "induced_maps_state": item["induced_maps_state"],
                    }
                )
                computation = item["computation"]
                if computation is not None:
                    computation_record = {
                        "id": computation["computation_id"],
                        "evidence_id": item["evidence_id"],
                        "algorithm_id": computation["algorithm_id"],
                        "input_sha256": computation["input_sha256"],
                        "parameters": computation["parameters"],
                        "output_scope": computation["output_scope"],
                        "status": computation["status"],
                    }
                    computations.append(computation_record)
                    computation_ids_by_evidence[item["evidence_id"]].append(
                        computation_record["id"]
                    )

            evidence.sort(key=lambda item: item["id"])
            models = sorted(models_by_id.values(), key=lambda item: item["id"])
            computations.sort(key=lambda item: item["id"])
            citations = sorted(
                citations_by_key.values(),
                key=lambda citation: (
                    citation["role"], citation["id"], citation["locator"]
                ),
            )
            for row in homology:
                row["computation_ids"] = sorted(
                    {
                        computation_id
                        for evidence_id in row["evidence_ids"]
                        for computation_id in computation_ids_by_evidence[evidence_id]
                    }
                )

            missing_required_fields = [
                field
                for field in (
                    "space_id",
                    "label",
                    "family",
                    "summary",
                    "chromatic_relevance",
                    "equivalence_kind",
                )
                if space.get(field) is None or space.get(field) == ""
            ]
            conceptual_space_record = {
                "id": space_id,
                "slug": slug_from_id(space_id),
                "kind": "conceptual_space",
                "name": {
                    "plain": space["label"],
                    "tex": conceptual_space_tex(space),
                },
                "aliases": aliases,
                "summary": space["summary"],
                "chromatic_relevance": space["chromatic_relevance"],
                "parameters": space["parameters"],
                "infinite_finite_type": space["infinite_finite_type"],
                "taxonomy": {
                    "family": space["family"],
                    "tags": space["tags"],
                },
                "properties": [
                    {
                        "key": "dimension",
                        "label": "dimension",
                        "value": space["dimension"],
                    },
                    {
                        "key": "connected_components",
                        "label": "connected components",
                        "value": space["connected_components"],
                    },
                    {
                        "key": "equivalence_kind",
                        "label": "model equivalence",
                        "value": space["equivalence_kind"],
                    },
                ],
                "homology_coverage": coverage,
                "homology": homology,
                "models": models,
                "relations": relations_by_space[space_id],
                "evidence": evidence,
                "citations": citations,
                "computations": computations,
                "data_quality": {
                    "state": "valid" if not missing_required_fields else "malformed",
                    "missing_required_fields": missing_required_fields,
                    "malformed_fields": [],
                },
                "raw": {
                    "subject": space,
                    "aliases": aliases,
                    "homology_coverage": coverage,
                    "homology_responses": raw_homology,
                    "evidence_response": expanded,
                    "relations": relations_by_space[space_id],
                },
            }
            conceptual_spaces.append(conceptual_space_record)
            evidence_total += len(evidence)
            homology_total += len(homology)
            computation_total += len(computations)
            model_total += len(models)
            citation_total += len(citations)
            relation_total += len(relations_by_space[space_id])

    conceptual_space_ids_by_family: dict[str, list[str]] = defaultdict(list)
    for item in conceptual_spaces:
        conceptual_space_ids_by_family[item["taxonomy"]["family"]].append(item["id"])
    sections = [
        {
            "id": family["family_id"],
            "label": family["label"],
            "summary": family["summary"],
            "chromatic_relevance": family["chromatic_relevance"],
            "conceptual_space_ids": conceptual_space_ids_by_family[family["family_id"]],
        }
        for family in families
    ]
    modified_at = datetime.fromtimestamp(database_path.stat().st_mtime, UTC).replace(
        microsecond=0
    )
    tree_state = source_tree_state()
    atlas = {
        "snapshot": {
            "snapshot_id": snapshot_row["snapshot_id"],
            "snapshot_name": snapshot_row["snapshot_name"],
            "snapshot_version": snapshot_row["schema_version"],
            "schema_version": READ_MODEL_VERSION,
            "generated_at": modified_at.isoformat().replace("+00:00", "Z"),
            "conceptual_space_count": len(conceptual_spaces),
            "evidence_count": evidence_total,
            "model_count": model_total,
            "citation_count": citation_total,
            "relation_count": relation_total,
            "computation_count": computation_total,
            "homology_row_count": homology_total,
            "source_database_bytes": database_path.stat().st_size,
            "source_database_sha256": file_sha256(database_path),
            "source_commit": source_commit(),
            "source_revision_inputs": list(SOURCE_REVISION_INPUTS),
            "source_inputs_sha256": source_inputs_sha256(),
            "source_tree_state": tree_state,
            "source_inputs_dirty": (
                tree_state == "dirty" if tree_state != "unknown" else None
            ),
            "release_status": summary["release_status"],
            "manifest_sha256": snapshot_row["manifest_sha256"],
            "scope_note": snapshot_row["scope_note"],
            "materialized_through_degree": snapshot_row[
                "materialized_through_degree"
            ],
            "supported_coefficients": list(COEFFICIENTS),
            "homology_theory": THEORY_ID,
            "homology_conventions": [],
            "homology_convention_state": "not_recorded_in_database_schema",
        },
        "definitions": [
            {
                **definition,
                "revision": DEFINITION_REVISION,
                "selected_for_snapshot_id": snapshot_row["snapshot_id"],
            }
            for definition in DEFINITIONS
        ],
        "sections": sections,
        "conceptual_spaces": conceptual_spaces,
    }
    validate_read_model(atlas, allow_malformed_for_review=allow_malformed_for_review)
    return atlas


def safe_embedded_json(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_atlas(atlas: dict[str, Any]) -> str:
    template = (SOURCE_DIRECTORY / "index.template.html").read_text(encoding="utf-8")
    css = (SOURCE_DIRECTORY / "atlas.css").read_text(encoding="utf-8")
    presentation_javascript = (SOURCE_DIRECTORY / "presentation.js").read_text(
        encoding="utf-8"
    )
    javascript = (SOURCE_DIRECTORY / "atlas.js").read_text(encoding="utf-8")
    replacements = {
        "/*__ATLAS_CSS__*/": css,
        "/*__ATLAS_PRESENTATION_JS__*/": presentation_javascript,
        "__ATLAS_JSON__": safe_embedded_json(atlas),
        "/*__ATLAS_JS__*/": javascript,
    }
    for marker, replacement in replacements.items():
        if template.count(marker) != 1:
            raise ValueError(f"template must contain marker exactly once: {marker}")
        template = template.replace(marker, replacement)
    return template


def export_atlas(
    database_path: Path,
    output_path: Path,
    *,
    allow_malformed_for_review: bool = False,
) -> dict[str, Any]:
    atlas = build_read_model(
        database_path, allow_malformed_for_review=allow_malformed_for_review
    )
    html = render_atlas(atlas)
    html_bytes = len(html.encode("utf-8"))
    if html_bytes > MAX_HTML_BYTES:
        raise ValueError(
            f"static atlas is {html_bytes} bytes; limit is {MAX_HTML_BYTES}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8", newline="\n")
    return {
        "conceptual_space_count": atlas["snapshot"]["conceptual_space_count"],
        "evidence_count": atlas["snapshot"]["evidence_count"],
        "model_count": atlas["snapshot"]["model_count"],
        "citation_count": atlas["snapshot"]["citation_count"],
        "relation_count": atlas["snapshot"]["relation_count"],
        "computation_count": atlas["snapshot"]["computation_count"],
        "homology_row_count": atlas["snapshot"]["homology_row_count"],
        "unresolved_reference_count": atlas["snapshot"]["unresolved_reference_count"],
        "html_bytes": output_path.stat().st_size,
        "source_database_bytes": atlas["snapshot"]["source_database_bytes"],
        "source_database_sha256": atlas["snapshot"]["source_database_sha256"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--database", type=Path, help="existing chromatic SQLite Snapshot")
    source.add_argument(
        "--snapshot",
        choices=["current"],
        help="build the current disposable chromatic Snapshot before export",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--allow-malformed-for-review",
        action="store_true",
        help="emit malformed records with diagnostics instead of failing the normal build",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.database:
        summary = export_atlas(
            args.database.resolve(),
            args.output.resolve(),
            allow_malformed_for_review=args.allow_malformed_for_review,
        )
    else:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "homology-db-chromatic.sqlite3"
            build_current_database(database_path)
            commit_timestamp = source_commit_timestamp()
            if commit_timestamp is not None:
                os.utime(database_path, (commit_timestamp, commit_timestamp))
            summary = export_atlas(
                database_path,
                args.output.resolve(),
                allow_malformed_for_review=args.allow_malformed_for_review,
            )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
