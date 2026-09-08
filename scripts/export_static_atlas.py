#!/usr/bin/env python3
"""Export the Chromatic Homology Atlas as one self-contained document."""

from __future__ import annotations

import argparse
import copy
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
from homology_db.classical import (
    CLASSICAL_COEFFICIENTS,
    CLASSICAL_SCHEMA_VERSION,
    CLASSICAL_SOURCES,
    CLASSICAL_SPACE_IDS,
    CLASSICAL_EXTENSION_SPACE_IDS,
    classical_records,
    validate_classical_records,
)
from homology_db.families import family_catalog
from homology_db.family_reviews import reviewed_family_catalog
from homology_db.teaching import teaching_catalog


SOURCE_DIRECTORY = REPOSITORY_ROOT / "static_atlas"
PUBLIC_ATLAS_PATH = REPOSITORY_ROOT / "dist" / "atlas.html"
READ_MODEL_VERSION = "homology-db.static-atlas/5"
THEORY_ID = "ordinary_homology"
# Bounded symbolic family data adds little to the retained stable-spectrum corpus.
# Keep direct-file/offline compatibility; the new workbench budget is 6 MiB.
MAX_HTML_BYTES = 6 * 1024 * 1024
DEFINITION_REVISION = 1
DEFINITIONS = (
    {
        "id": "ordinary-cohomology",
        "term": "Ordinary cohomology",
        "body": "Cohomology assigns groups H^n(X; R) to a space and coefficient ring. The cup product combines them into a graded ring H*(X; R). This atlas shows ordinary unreduced cohomology rings, including the unit in degree zero.",
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "cup-product",
        "term": "Cup product",
        "body": "The cup product multiplies a class of degree p and a class of degree q to give one of degree p+q. It records information beyond the additive groups. For ordinary cohomology with commutative coefficients, swapping the factors multiplies the answer by (-1)^(pq).",
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "generator-degree",
        "term": "Generator degree",
        "body": "A homogeneous ring generator is a class in one cohomological degree from which other classes can be built by sums, scalar multiples, and products, together with the unit. Its degree is not its multiplicity. Degrees add under multiplication.",
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "ring-relation",
        "term": "Ring relation",
        "body": "Relations specify equations satisfied by ring generators. In $R[x]/(x^3)$, powers of $x$ generate the ring and $x^3$ is zero. The generator degree must also be given. A displayed zero relation is a recorded mathematical assertion; absent ring data is not a zero ring.",
        "scope": "exposition",
        "assertion_evidence": False,
    },
    {
        "id": "coefficient-field",
        "term": "Coefficient field",
        "body": "$\\mathbb{Q}$ is the field of rational numbers; $\\mathbb{F}_{p}$ is the field with p elements for a prime p. Cohomology over a field has vector spaces as its additive groups. Changing the field can change both those groups and their products. $\\mathbb{Z}$ denotes integral coefficients and is not a field.",
        "scope": "exposition",
        "assertion_evidence": False,
    },
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
    "corpus/steenrod-cw49-v1/corpus.json",
    "corpus/steenrod-cw49-v1/upstream-adams.json",
    "homology_db/__init__.py",
    "homology_db/atlas_schema.py",
    "homology_db/chromatic.py",
    "homology_db/classical.py",
    "homology_db/cohomology_rings.py",
    "homology_db/families.py",
    "homology_db/family_reviews.py",
    "homology_db/teaching.py",
    "docs/reviews/family-reviews.json",
    "homology_db/migrations/0005_stable_steenrod_modules.sql",
    "homology_db/preview.py",
    "homology_db/steenrod.py",
    "homology_db/steenrod_snapshot.py",
    "scripts/export_static_atlas.py",
    "scripts/materialize_steenrod_snapshot.py",
    "scripts/verify_steenrod_release.py",
    "static_atlas/atlas.css",
    "static_atlas/atlas.js",
    "static_atlas/index.template.html",
    "static_atlas/presentation.js",
    "static_atlas/families.js",
    "static_atlas/workbench.js",
)


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _legacy_logical_database_sha256(path: Path) -> str:
    """Hash ordered schema and row values, independent of SQLite page layout."""

    def quoted(identifier: str) -> str:
        return '"' + identifier.replace('"', '""') + '"'

    def json_value(value: Any) -> Any:
        if isinstance(value, bytes):
            return {"sqlite_blob_hex": value.hex()}
        return value

    with closing(sqlite3.connect(path)) as connection:
        schema_objects = [
            {
                "type": row[0],
                "name": row[1],
                "table": row[2],
                "sql": row[3],
            }
            for row in connection.execute(
                """
                SELECT type, name, tbl_name, sql
                FROM sqlite_master
                WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL
                ORDER BY type, name, tbl_name, sql
                """
            )
        ]
        tables: list[dict[str, Any]] = []
        table_names = [
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )
        ]
        for table_name in table_names:
            columns = [
                {
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "not_null": row[3],
                    "default": row[4],
                    "primary_key_order": row[5],
                }
                for row in connection.execute(
                    f"PRAGMA table_info({quoted(table_name)})"
                )
            ]
            column_names = [column["name"] for column in columns]
            projection = ", ".join(quoted(name) for name in column_names)
            order = ", ".join(quoted(name) for name in column_names)
            rows = [
                [json_value(value) for value in row]
                for row in connection.execute(
                    f"SELECT {projection} FROM {quoted(table_name)} ORDER BY {order}"
                )
            ]
            tables.append(
                {
                    "name": table_name,
                    "columns": columns,
                    "rows": rows,
                }
            )
    logical_bytes = json.dumps(
        {
            "schema_version": "homology-db.sqlite-logical/1",
            "schema_objects": schema_objects,
            "tables": tables,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(logical_bytes).hexdigest()


def logical_database_sha256(path: Path) -> str:
    """Return the canonical v2 logical identity for a SQLite database."""

    # Lazy by design: the stable-ledger materializer imports release-contract
    # helpers from this script, so importing it at module load would form a cycle.
    from homology_db.steenrod_snapshot import canonical_logical_database_sha256

    return canonical_logical_database_sha256(path)


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


def _canonical_download_payload(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def _spectrum_downloads(spectrum: dict[str, Any]) -> dict[str, dict[str, Any]]:
    from homology_db.steenrod import (
        UnsupportedExportError,
        export_bruner,
        export_manifest,
        export_sseq,
        export_sseqcpp,
    )

    downloads: dict[str, dict[str, Any]] = {}
    adapters = (
        ("bruner", export_bruner, ".def", "text/plain"),
        ("sseq", export_sseq, ".sseq.json", "application/json"),
        ("sseqcpp", export_sseqcpp, ".adams.json", "application/json"),
    )
    for format_name, exporter, suffix, media_type in adapters:
        try:
            payload = _canonical_download_payload(exporter(spectrum))
        except UnsupportedExportError as error:
            downloads[format_name] = {
                "status": "unsupported",
                "reason": error.reason,
            }
            continue
        manifest = export_manifest(spectrum, format_name, payload)
        downloads[format_name] = {
            "status": "ready",
            "filename": f"{spectrum['slug']}{suffix}",
            "media_type": media_type,
            "payload": payload,
            "manifest": manifest,
        }
    return downloads


def _atlas_module_projection(module: dict[str, Any]) -> dict[str, Any]:
    """Drop only completeness slots derivable from explicit canonical actions."""

    if module["module_type"] != "finite_basis":
        return module
    completeness = module["completeness"]
    slots = completeness["slots"]
    if len(slots) != len(module["actions"]):
        raise ValueError("finite Steenrod actions do not match their completeness slots")
    if any(action["knowledge_state"] != "exact" for action in module["actions"]):
        raise ValueError("finite Steenrod atlas projection requires exact action images")
    return {
        **module,
        "actions": [
            {
                key: value
                for key, value in action.items()
                if key != "knowledge_state"
            }
            for action in module["actions"]
        ],
        "action_knowledge_state_default": "exact",
        "completeness": {
            "knowledge_state": completeness["knowledge_state"],
            "slot_count": len(slots),
        },
    }


def build_spectrum_read_model() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from homology_db.steenrod import load_cw49_corpus, validate_module

    corpus = load_cw49_corpus()
    if corpus.get("schema_version") != "homology-db.steenrod-corpus/1":
        raise ValueError("unsupported Steenrod corpus schema")
    source = corpus.get("source")
    if not isinstance(source, dict) or source.get("review_state") != "imported_unreviewed":
        raise ValueError("Steenrod review candidate must retain imported-unreviewed provenance")
    raw_spectra = corpus.get("spectra")
    if not isinstance(raw_spectra, list) or len(raw_spectra) != 49:
        raise ValueError("Steenrod review candidate must contain all 49 cw49 spectra")

    spectra: list[dict[str, Any]] = []
    for raw_spectrum in raw_spectra:
        if not isinstance(raw_spectrum, dict):
            raise ValueError("Steenrod corpus contains a malformed spectrum")
        validate_module(raw_spectrum["module"])
        spectrum = {
            "id": raw_spectrum["spectrum_id"],
            "spectrum_id": raw_spectrum["spectrum_id"],
            "slug": raw_spectrum["slug"],
            "kind": "conceptual_spectrum",
            "name": raw_spectrum["name"],
            "object_kind": raw_spectrum["object_kind"],
            "search_aliases": (
                ["projective", "real projective space"]
                if raw_spectrum["spectrum_id"].startswith("RP")
                else []
            ),
            "source_decode_state": raw_spectrum["source_decode_state"],
            "review_state": raw_spectrum["review_state"],
            "module": _atlas_module_projection(raw_spectrum["module"]),
            "provenance_ref": "cw49",
            "downloads": _spectrum_downloads(raw_spectrum),
        }
        spectra.append(spectrum)

    spectrum_ids = [spectrum["id"] for spectrum in spectra]
    slugs = [spectrum["slug"] for spectrum in spectra]
    if len(spectrum_ids) != len(set(spectrum_ids)):
        raise ValueError("Steenrod corpus contains duplicate Conceptual-spectrum IDs")
    if len(slugs) != len(set(slugs)):
        raise ValueError("Steenrod corpus contains duplicate Conceptual-spectrum slugs")
    spectra.sort(key=lambda spectrum: (spectrum["name"]["plain"].casefold(), spectrum["id"]))
    return spectra, source


def _without_review_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_review_metadata(item)
            for key, item in value.items()
            if key not in {"review", "review_state"}
        }
    if isinstance(value, list):
        return [_without_review_metadata(item) for item in value]
    return value


def steenrod_candidate_sha256(spectra: list[dict[str, Any]]) -> str:
    payload = json.dumps(
        _without_review_metadata(spectra),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _steenrod_build_bindings(atlas: dict[str, Any]) -> dict[str, Any]:
    snapshot = atlas["snapshot"]
    source = snapshot["spectrum_source"]
    return {
        "source_commit": snapshot["source_commit"],
        "source_inputs_sha256": snapshot["source_inputs_sha256"],
        "source_database_hash_kind": snapshot["source_database_hash_kind"],
        "source_database_sha256": snapshot["source_database_sha256"],
        "spectrum_source_sha256": _canonical_sha256(source),
    }


def _steenrod_assertion_targets(
    spectra: list[dict[str, Any]],
) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    for spectrum in sorted(spectra, key=lambda item: item["spectrum_id"]):
        spectrum_id = spectrum["spectrum_id"]
        module = spectrum["module"]
        module_hash = module["content_sha256"]
        if module["module_type"] == "profile":
            continue

        for action in sorted(
            module["actions"],
            key=lambda item: (
                item["source_basis_id"],
                item["square_degree"],
                tuple(item["target_basis_ids"]),
            ),
        ):
            claim = {
                "assertion_kind": "steenrod_action",
                "spectrum_id": spectrum_id,
                "module_content_sha256": module_hash,
                "source_basis_id": action["source_basis_id"],
                "square_degree": action["square_degree"],
                "target_basis_ids": action["target_basis_ids"],
                "knowledge_state": module["action_knowledge_state_default"],
            }
            targets.append(
                {
                    "assertion_id": (
                        f"steenrod-action:{spectrum_id}:"
                        f"{action['source_basis_id']}:Sq{action['square_degree']}"
                    ),
                    "assertion_kind": "steenrod_action",
                    "claim_sha256": _canonical_sha256(claim),
                }
            )

        completeness = module["completeness"]
        completeness_claim = {
            "assertion_kind": "steenrod_action_completeness",
            "spectrum_id": spectrum_id,
            "module_content_sha256": module_hash,
            "basis_version": module["basis_version"],
            "knowledge_state": completeness["knowledge_state"],
            "slot_count": completeness["slot_count"],
        }
        targets.append(
            {
                "assertion_id": (
                    f"steenrod-completeness:{spectrum_id}:{module['basis_version']}"
                ),
                "assertion_kind": "steenrod_action_completeness",
                "claim_sha256": _canonical_sha256(completeness_claim),
            }
        )
    targets.sort(key=lambda item: item["assertion_id"])
    return targets


def build_steenrod_release_projection(atlas: dict[str, Any]) -> dict[str, Any]:
    spectra = atlas["conceptual_spectra"]
    candidate_hash = steenrod_candidate_sha256(spectra)
    assertion_targets = _steenrod_assertion_targets(spectra)
    assertion_reviews = {
        "schema_version": "homology-db.steenrod-assertion-review-manifest/1",
        "count": len(assertion_targets),
        "manifest_sha256": _canonical_sha256(
            {
                "schema_version": "homology-db.steenrod-assertion-review-manifest/1",
                "targets": assertion_targets,
            }
        ),
    }
    profile_spectra = [
        spectrum
        for spectrum in spectra
        if spectrum["module"]["module_type"] == "profile"
    ]
    if len(profile_spectra) != 1 or profile_spectra[0]["spectrum_id"] != "tmf":
        raise ValueError("cw49 release projection requires exactly the tmf profile module")
    tmf_module_hash = profile_spectra[0]["module"]["content_sha256"]
    admission_targets = [
        {
            "record_kind": "assertion",
            "record_id": target["assertion_id"],
            "record_sha256": target["claim_sha256"],
            "decision": "admit",
        }
        for target in assertion_targets
    ]
    admission_targets.append(
        {
            "record_kind": "steenrod_module",
            "record_id": "steenrod-module:tmf:cw49-v126.3",
            "record_sha256": tmf_module_hash,
            "decision": "admit",
        }
    )
    admission_targets.sort(key=lambda item: (item["record_kind"], item["record_id"]))
    editorial_admissions = {
        "schema_version": "homology-db.steenrod-editorial-admission-manifest/1",
        "count": len(admission_targets),
        "profile_module_content_sha256": tmf_module_hash,
        "manifest_sha256": _canonical_sha256(
            {
                "schema_version": "homology-db.steenrod-editorial-admission-manifest/1",
                "targets": admission_targets,
            }
        ),
    }
    record_counts = {
        "spectrum_count": len(spectra),
        "module_count": len(spectra),
        "basis_element_count": sum(
            len(spectrum["module"].get("basis", [])) for spectrum in spectra
        ),
        "action_assertion_count": sum(
            len(spectrum["module"].get("actions", [])) for spectrum in spectra
        ),
        "completeness_assertion_count": sum(
            spectrum["module"]["module_type"] == "finite_basis"
            for spectrum in spectra
        ),
        "profile_module_admission_count": 1,
        "assertion_review_count": assertion_reviews["count"],
        "editorial_admission_count": editorial_admissions["count"],
    }
    snapshot_id = f"steenrod-cw49-v1-{candidate_hash[:16]}"
    snapshot_manifest = {
        "schema_version": "homology-db.steenrod-snapshot-manifest/1",
        "snapshot_id": snapshot_id,
        "candidate_sha256": candidate_hash,
        "build": _steenrod_build_bindings(atlas),
        "record_counts": record_counts,
        "assertion_reviews": assertion_reviews,
        "editorial_admissions": editorial_admissions,
        "spectra": [
            {
                "spectrum_id": spectrum["spectrum_id"],
                "slug": spectrum["slug"],
                "module_type": spectrum["module"]["module_type"],
                "module_content_sha256": spectrum["module"]["content_sha256"],
            }
            for spectrum in sorted(spectra, key=lambda item: item["spectrum_id"])
        ],
    }
    spectrum_snapshot = {
        "schema_version": snapshot_manifest["schema_version"],
        "snapshot_id": snapshot_id,
        "candidate_sha256": candidate_hash,
        "record_counts": record_counts,
        "manifest_sha256": _canonical_sha256(snapshot_manifest),
    }
    return {
        "schema_version": "homology-db.steenrod-release-projection/1",
        "spectrum_snapshot": spectrum_snapshot,
        "assertion_reviews": assertion_reviews,
        "editorial_admissions": editorial_admissions,
    }


def render_steenrod_review_packet(packet: dict[str, Any]) -> str:
    return json.dumps(
        packet,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def materialize_accepted_steenrod_database(
    database_path: Path,
    packet: dict[str, Any],
    coverage_report: str,
    acceptance_record_path: Path,
) -> dict[str, Any]:
    """Build the separate finalized v5 spectrum ledger for an accepted release."""

    # Lazy by design; see logical_database_sha256() for the dependency direction.
    from homology_db.steenrod_snapshot import materialize_steenrod_snapshot

    review_packet_path = database_path.with_suffix(".review.json")
    coverage_report_path = database_path.with_suffix(".coverage.md")
    review_packet_path.write_text(
        render_steenrod_review_packet(packet),
        encoding="utf-8",
        newline="\n",
    )
    coverage_report_path.write_text(
        coverage_report,
        encoding="utf-8",
        newline="\n",
    )
    return materialize_steenrod_snapshot(
        database_path,
        review_packet_path,
        coverage_report_path,
        acceptance_record_path,
    )


def expected_steenrod_acceptance_bindings(
    packet: dict[str, Any], coverage_report: str
) -> dict[str, Any]:
    build = packet["build"]
    projection = packet["release_projection"]
    return {
        "candidate_sha256": packet["candidate_sha256"],
        "spectrum_source_sha256": build["spectrum_source_sha256"],
        "source_commit": build["source_commit"],
        "source_inputs_sha256": build["source_inputs_sha256"],
        "source_database_hash_kind": build["source_database_hash_kind"],
        "source_database_sha256": build["source_database_sha256"],
        "review_packet_sha256": hashlib.sha256(
            render_steenrod_review_packet(packet).encode("utf-8")
        ).hexdigest(),
        "coverage_report_sha256": hashlib.sha256(
            coverage_report.encode("utf-8")
        ).hexdigest(),
        "spectrum_snapshot_id": projection["spectrum_snapshot"]["snapshot_id"],
        "spectrum_snapshot_manifest_sha256": projection["spectrum_snapshot"][
            "manifest_sha256"
        ],
        "spectrum_count": packet["coverage"]["spectrum_count"],
        "assertion_review_count": projection["assertion_reviews"]["count"],
        "assertion_review_manifest_sha256": projection["assertion_reviews"][
            "manifest_sha256"
        ],
        "editorial_admission_count": projection["editorial_admissions"]["count"],
        "editorial_admission_manifest_sha256": projection["editorial_admissions"][
            "manifest_sha256"
        ],
        "tmf_profile_module_content_sha256": projection["editorial_admissions"][
            "profile_module_content_sha256"
        ],
    }


def _require_lower_hex(value: Any, length: int, label: str) -> None:
    if not isinstance(value, str) or re.fullmatch(
        rf"[0-9a-f]{{{length}}}", value
    ) is None:
        raise ValueError(f"{label} must be {length} lowercase hexadecimal characters")


def validate_steenrod_acceptance_record(
    acceptance: Any,
    packet: dict[str, Any],
    coverage_report: str,
) -> dict[str, Any]:
    if not isinstance(acceptance, dict):
        raise ValueError("Steenrod acceptance record must be an object")
    if acceptance.get("schema_version") != "homology-db.steenrod-acceptance/1":
        raise ValueError("Steenrod acceptance record has an unsupported schema")
    if (
        acceptance.get("reviewer") != "Dan Isaksen"
        or acceptance.get("verdict") != "accept"
    ):
        raise ValueError("Steenrod acceptance record is not Dan Isaksen's acceptance")
    reviewed_at = acceptance.get("reviewed_at")
    if not isinstance(reviewed_at, str):
        raise ValueError("Steenrod acceptance record requires a review timestamp")
    try:
        parsed_reviewed_at = datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Steenrod acceptance timestamp must be RFC 3339") from error
    if parsed_reviewed_at.tzinfo is None:
        raise ValueError("Steenrod acceptance timestamp must include a timezone")

    evidence = acceptance.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("Steenrod acceptance record requires structured evidence")
    if evidence.get("kind") != "written_acceptance":
        raise ValueError("Steenrod acceptance evidence must be written_acceptance")
    if not isinstance(evidence.get("locator"), str) or not evidence["locator"].strip():
        raise ValueError("Steenrod acceptance evidence requires a retained locator")
    _require_lower_hex(evidence.get("sha256"), 64, "acceptance evidence SHA-256")
    if not isinstance(acceptance.get("editorial_actor"), str) or not acceptance[
        "editorial_actor"
    ].strip():
        raise ValueError("Steenrod acceptance record requires an editorial actor")

    expected = expected_steenrod_acceptance_bindings(packet, coverage_report)
    _require_lower_hex(expected["source_commit"], 40, "bound source commit")
    for key in (
        "candidate_sha256",
        "spectrum_source_sha256",
        "source_inputs_sha256",
        "source_database_sha256",
        "review_packet_sha256",
        "coverage_report_sha256",
        "spectrum_snapshot_manifest_sha256",
        "assertion_review_manifest_sha256",
        "editorial_admission_manifest_sha256",
        "tmf_profile_module_content_sha256",
    ):
        _require_lower_hex(expected[key], 64, key)
    bindings = acceptance.get("bindings")
    if not isinstance(bindings, dict):
        raise ValueError("Steenrod acceptance record requires structured bindings")
    if set(bindings) != set(expected):
        raise ValueError("Steenrod acceptance bindings have missing or unexpected fields")
    for key, expected_value in expected.items():
        if bindings[key] != expected_value:
            raise ValueError(f"Steenrod acceptance binding mismatch for {key}")
    return expected


def _accept_spectrum_records(
    spectra: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Accept spectrum/module assertions without rewriting import evidence."""

    accepted = copy.deepcopy(spectra)
    for spectrum in accepted:
        spectrum["review_state"] = "accepted"
        spectrum["module"]["review_state"] = "accepted"
    return accepted


def finalize_steenrod_atlas(
    atlas: dict[str, Any],
    packet: dict[str, Any],
    coverage_report: str,
    acceptance: Any,
    acceptance_record_sha256: str,
) -> dict[str, Any]:
    bindings = validate_steenrod_acceptance_record(
        acceptance,
        packet,
        coverage_report,
    )
    candidate_hash = packet["candidate_sha256"]
    original_content_hashes = {
        spectrum["spectrum_id"]: spectrum["module"]["content_sha256"]
        for spectrum in atlas["conceptual_spectra"]
    }
    accepted = copy.deepcopy(atlas)
    accepted["conceptual_spectra"] = _accept_spectrum_records(
        accepted["conceptual_spectra"]
    )
    snapshot = accepted["snapshot"]
    snapshot["spectrum_review_candidate"] = False
    snapshot["spectrum_release_status"] = "accepted_finalized"
    projection = packet["release_projection"]
    snapshot["spectrum_snapshot"] = {
        **projection["spectrum_snapshot"],
        "finalized_at": acceptance["reviewed_at"],
        "assertion_reviews": projection["assertion_reviews"],
        "editorial_admissions": projection["editorial_admissions"],
    }
    snapshot["spectrum_acceptance"] = {
        "schema_version": acceptance["schema_version"],
        "record_sha256": acceptance_record_sha256,
        "reviewer": acceptance["reviewer"],
        "verdict": acceptance["verdict"],
        "reviewed_at": acceptance["reviewed_at"],
        "evidence": acceptance["evidence"],
        "editorial_actor": acceptance["editorial_actor"],
        "bindings": bindings,
    }
    accepted_content_hashes = {
        spectrum["spectrum_id"]: spectrum["module"]["content_sha256"]
        for spectrum in accepted["conceptual_spectra"]
    }
    if accepted_content_hashes != original_content_hashes:
        raise ValueError("Steenrod acceptance changed canonical module content hashes")
    if steenrod_candidate_sha256(accepted["conceptual_spectra"]) != candidate_hash:
        raise ValueError("Steenrod acceptance changed the reviewed candidate")
    return accepted


def build_steenrod_review_packet(
    atlas: dict[str, Any], html: str
) -> dict[str, Any]:
    spectra = atlas["conceptual_spectra"]
    decode_state_counts: dict[str, int] = defaultdict(int)
    spectrum_summaries: list[dict[str, Any]] = []
    basis_element_count = 0
    action_slot_count = 0
    exact_zero_action_count = 0
    exact_nonzero_action_count = 0
    finite_module_count = 0
    profile_module_count = 0

    for spectrum in spectra:
        module = spectrum["module"]
        decode_state_counts[spectrum["source_decode_state"]] += 1
        basis = module.get("basis", [])
        actions = module.get("actions", [])
        zero_count = sum(not action["target_basis_ids"] for action in actions)
        nonzero_count = len(actions) - zero_count
        basis_element_count += len(basis)
        action_slot_count += len(actions)
        exact_zero_action_count += zero_count
        exact_nonzero_action_count += nonzero_count
        if module["module_type"] == "finite_basis":
            finite_module_count += 1
        else:
            profile_module_count += 1

        exports: dict[str, dict[str, Any]] = {}
        for format_name, download in sorted(spectrum["downloads"].items()):
            if download["status"] == "ready":
                exports[format_name] = {
                    "status": "ready",
                    "payload_sha256": download["manifest"]["payload_sha256"],
                }
            else:
                exports[format_name] = {
                    "status": "unsupported",
                    "reason": download["reason"],
                }
        spectrum_summaries.append(
            {
                "spectrum_id": spectrum["spectrum_id"],
                "slug": spectrum["slug"],
                "name": spectrum["name"],
                "source_decode_state": spectrum["source_decode_state"],
                "review_state": spectrum["review_state"],
                "module_type": module["module_type"],
                "basis_version": module["basis_version"],
                "module_content_sha256": module["content_sha256"],
                "evidence": module["evidence"],
                "basis_element_count": len(basis),
                "action_slot_count": len(actions),
                "exact_zero_action_count": zero_count,
                "exact_nonzero_action_count": nonzero_count,
                "exports": exports,
            }
        )

    coverage = {
        "spectrum_count": len(spectra),
        "finite_module_count": finite_module_count,
        "profile_module_count": profile_module_count,
        "basis_element_count": basis_element_count,
        "action_slot_count": action_slot_count,
        "exact_zero_action_count": exact_zero_action_count,
        "exact_nonzero_action_count": exact_nonzero_action_count,
        "decode_state_counts": dict(sorted(decode_state_counts.items())),
    }
    if coverage != {
        "spectrum_count": 49,
        "finite_module_count": 48,
        "profile_module_count": 1,
        "basis_element_count": 942,
        "action_slot_count": 5780,
        "exact_zero_action_count": 3277,
        "exact_nonzero_action_count": 2503,
        "decode_state_counts": {"complete": 49},
    }:
        raise ValueError("cw49 review coverage does not match the pinned candidate")
    return {
        "schema_version": "homology-db.steenrod-review-packet/1",
        "candidate_sha256": steenrod_candidate_sha256(spectra),
        "atlas_html_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "review_state": "imported_unreviewed",
        "acceptance_recorded": False,
        "requested_reviewer": "Dan Isaksen",
        "source": atlas["snapshot"]["spectrum_source"],
        "build": _steenrod_build_bindings(atlas),
        "release_projection": build_steenrod_release_projection(atlas),
        "coverage": coverage,
        "spectra": spectrum_summaries,
    }


def render_steenrod_coverage_report(packet: dict[str, Any]) -> str:
    coverage = packet["coverage"]
    source = packet["source"]
    lines = [
        "# cw49 Steenrod review coverage",
        "",
        f"Review state: `{packet['review_state']}`. No acceptance is recorded.",
        "",
        f"- Candidate SHA-256: `{packet['candidate_sha256']}`",
        f"- Atlas HTML SHA-256: `{packet['atlas_html_sha256']}`",
        (
            f"- Spectra: {coverage['spectrum_count']} "
            f"({coverage['finite_module_count']} finite basis; "
            f"{coverage['profile_module_count']} profile)"
        ),
        f"- Basis elements: {coverage['basis_element_count']:,}",
        (
            f"- Exact actions: {coverage['action_slot_count']:,} "
            f"({coverage['exact_nonzero_action_count']:,} nonzero; "
            f"{coverage['exact_zero_action_count']:,} zero)"
        ),
        f"- cw49 index commit: `{source['index_commit']}`",
        f"- SSeqCpp commit: `{source['sseqcpp_commit']}`",
        f"- sseq commit: `{source['sseq_commit']}`",
        f"- Zenodo source: `{source['zenodo_doi']}` / `{source['zenodo_version']}`",
        f"- License: `{source['dataset_license']}`",
        "",
        "| Spectrum | Decode | Module | Basis | Actions | Nonzero | Zero | Bruner | sseq | SSeqCpp |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for spectrum in packet["spectra"]:
        statuses = {
            format_name: export["status"]
            for format_name, export in spectrum["exports"].items()
        }
        lines.append(
            "| "
            + " | ".join(
                [
                    spectrum["spectrum_id"].replace("|", "\\|"),
                    spectrum["source_decode_state"],
                    spectrum["module_type"],
                    str(spectrum["basis_element_count"]),
                    str(spectrum["action_slot_count"]),
                    str(spectrum["exact_nonzero_action_count"]),
                    str(spectrum["exact_zero_action_count"]),
                    statuses["bruner"],
                    statuses["sseq"],
                    statuses["sseqcpp"],
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


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


def rational_homology_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extend integral homology to Q without changing the historical database."""
    derived = []
    for row in rows:
        if row["coefficient_ring"] != "Z":
            continue
        group = row["group"]
        if group["state"] == "exact":
            rank = group["free_rank"]
            projected = {"state": "exact", "dimension": rank,
                         "plain": "0" if rank == 0 else "Q" if rank == 1 else f"Q^{rank}"}
        else:
            projected = {"state": group["state"], "plain": group["plain"]}
        derived.append({
            **row,
            "coefficient_ring": "Q",
            "coefficient_system": "constant:Q",
            "group": projected,
            "assertion_id": row["assertion_id"].replace(
                "chromatic:assertion:", "classical:assertion:", 1
            ).replace(":Z:", ":Q:"),
            "computation_ids": [],
            "derivation": {"rule": "rational-extension-of-scalars/1",
                           "input_assertion_id": row["assertion_id"]},
        })
    return derived


def classical_projection_metadata(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "schema_version": CLASSICAL_SCHEMA_VERSION,
        "space_ids": sorted(records),
        "core_space_ids": list(CLASSICAL_SPACE_IDS),
        "extension_space_ids": list(CLASSICAL_EXTENSION_SPACE_IDS),
        "coefficients": list(CLASSICAL_COEFFICIENTS),
        "space_count": len(records),
        "record_count": sum(len(items) for items in records.values()),
        "content_sha256": _canonical_sha256(records),
        "review_state": "human_review_pending",
        "rational_homology_derivation": {
            "id": "rational-extension-of-scalars/1",
            "kind": "derived_from_integral_homology",
            "statement": "Tensor integral homology with Q; torsion vanishes and free rank becomes dimension.",
            "source_url": "https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=275",
            "locator": "Corollary 3A.6(a), p. 266: rational homology and integral rank",
        },
    }


def teaching_projection(spaces: list[dict[str, Any]]) -> dict[str, Any]:
    """Bind exposition to actual recorded coverage, without inventing review."""
    catalog = copy.deepcopy(teaching_catalog())
    by_id = {space["id"]: space for space in spaces}
    entries = catalog["entries"]
    family_rules = reviewed_family_catalog(family_catalog())["rules"]
    if len(entries) != len(by_id) or {entry["space_id"] for entry in entries} != set(by_id):
        raise ValueError("teaching inventory must cover each retained space exactly once")
    for entry in entries:
        space = by_id[entry["space_id"]]
        family = re.fullmatch(r"(sphere|real_projective_space|complex_projective_space):[0-9]+", space["id"])
        if family:
            kind, label = "general_family", "General family · all degrees"
            coefficients = ["Z", "Q", "F2", "F3", "F5", "F7", "F11"]
        elif space["id"] in CLASSICAL_SPACE_IDS:
            kind, label = "core_ring", "Textbook core · five-field rings"
            coefficients = [record["coefficient"] for record in space.get("cohomology", [])]
        elif space.get("cohomology"):
            kind, label = "extension_ring", "Projective-plane extension · five-field rings"
            coefficients = [record["coefficient"] for record in space["cohomology"]]
        else:
            kind, label = "homology_only", "Homology recorded · cohomology rings not recorded"
            coefficients = []
        entry["space_slug"] = space["slug"]
        rule = next((rule for rule in family_rules if family and rule["family"] == family.group(1)), None)
        entry["coverage"] = {"kind": kind, "label": label, "coefficients": coefficients,
                             "human_review_state": rule["human_review_state"] if rule else "human_review_pending"}
    catalog["content_sha256"] = _canonical_sha256(catalog)
    return catalog


def validate_read_model(
    atlas: dict[str, Any], *, allow_malformed_for_review: bool = False
) -> None:
    if atlas.get("snapshot", {}).get("schema_version") == READ_MODEL_VERSION:
        if atlas.get("family_rules") != reviewed_family_catalog(family_catalog()):
            raise ValueError("family rules or human reviews differ from exact source-bound catalog")
    elif "family_rules" in atlas:
        raise ValueError("family rules require the version 5 read-model contract")
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
    if "teaching" in atlas or "teaching_sha256" in atlas.get("snapshot", {}):
        expected_teaching = teaching_projection(conceptual_spaces)
        if atlas.get("teaching") != expected_teaching or atlas["snapshot"].get("teaching_sha256") != expected_teaching["content_sha256"]:
            raise ValueError("teaching exposition or coverage differs from source-bound catalog")
    if atlas["snapshot"].get("schema_version") in {"homology-db.static-atlas/4", READ_MODEL_VERSION}:
        projected_classical = {
            item["id"]: item["cohomology"]
            for item in conceptual_spaces
            if item.get("cohomology")
        }
        validate_classical_records(projected_classical)
        if any(
            item.get("classical_core") != (item["id"] in CLASSICAL_SPACE_IDS)
            for item in conceptual_spaces
        ):
            raise ValueError("classical core labels disagree with cohomology coverage")
        classical = atlas.get("classical", {})
        expected_metadata = classical_projection_metadata(projected_classical)
        if classical != {**expected_metadata, "sources": CLASSICAL_SOURCES}:
            raise ValueError("classical metadata or sources disagree with the validated corpus")
        if expected_metadata != atlas["snapshot"].get("classical_cohomology"):
            raise ValueError("classical cohomology snapshot metadata mismatch")
        for space in conceptual_spaces:
            actual_q = [row for row in space["homology"] if row["coefficient_ring"] == "Q"]
            expected_q = rational_homology_rows(space["homology"]) if space.get("cohomology") else []
            if actual_q != expected_q:
                raise ValueError(f"rational homology does not match integral inputs: {space['id']}")
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
    database_path: Path,
    *,
    allow_malformed_for_review: bool = False,
    steenrod_review_candidate: bool = False,
) -> dict[str, Any]:
    if not database_path.exists():
        raise FileNotFoundError(database_path)
    cohomology_records = classical_records()
    validate_classical_records(cohomology_records)
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

            if space_id in cohomology_records:
                homology.extend(rational_homology_rows(homology))

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
                "classical_core": space_id in CLASSICAL_SPACE_IDS,
                "cohomology": cohomology_records.get(space_id, []),
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
    revision_timestamp = source_commit_timestamp()
    generated_at = datetime.fromtimestamp(revision_timestamp or 0, UTC).replace(
        microsecond=0
    )
    tree_state = source_tree_state()
    conceptual_spectra: list[dict[str, Any]] = []
    spectrum_source: dict[str, Any] | None = None
    if steenrod_review_candidate:
        conceptual_spectra, spectrum_source = build_spectrum_read_model()

    classical_metadata = classical_projection_metadata(cohomology_records)
    teaching = teaching_projection(conceptual_spaces)

    atlas = {
        "snapshot": {
            "snapshot_id": snapshot_row["snapshot_id"],
            "snapshot_name": snapshot_row["snapshot_name"],
            "snapshot_version": snapshot_row["schema_version"],
            "schema_version": READ_MODEL_VERSION,
            "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
            "conceptual_space_count": len(conceptual_spaces),
            "conceptual_spectrum_count": len(conceptual_spectra),
            "spectrum_review_candidate": steenrod_review_candidate,
            "spectrum_release_status": (
                "imported_unreviewed_review_candidate"
                if steenrod_review_candidate
                else "withheld_pending_review"
            ),
            "spectrum_source": spectrum_source,
            "evidence_count": evidence_total,
            "model_count": model_total,
            "citation_count": citation_total,
            "relation_count": relation_total,
            "computation_count": computation_total,
            "homology_row_count": homology_total,
            "source_database_hash_kind": "homology-db.sqlite-logical/1",
            "source_database_sha256": _legacy_logical_database_sha256(database_path),
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
            "classical_cohomology": classical_metadata,
            "teaching_sha256": teaching["content_sha256"],
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
        "conceptual_spectra": conceptual_spectra,
        "classical": {**classical_metadata, "sources": CLASSICAL_SOURCES},
        "family_rules": reviewed_family_catalog(family_catalog()),
        "teaching": teaching,
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
        "/*__FAMILIES_JS__*/": (SOURCE_DIRECTORY / "families.js").read_text(encoding="utf-8"),
        "/*__WORKBENCH_JS__*/": (SOURCE_DIRECTORY / "workbench.js").read_text(encoding="utf-8"),
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
    steenrod_review_candidate: bool = False,
    steenrod_review_packet_path: Path | None = None,
    steenrod_coverage_report_path: Path | None = None,
    steenrod_acceptance_record_path: Path | None = None,
    allow_public_review_preview: bool = False,
) -> dict[str, Any]:
    if allow_public_review_preview and not steenrod_review_candidate:
        raise ValueError(
            "public Steenrod preview requires --steenrod-review-candidate"
        )
    if (
        steenrod_review_candidate
        and output_path.resolve() == PUBLIC_ATLAS_PATH.resolve()
        and not allow_public_review_preview
    ):
        raise ValueError(
            "an unreviewed Steenrod candidate cannot target dist/atlas.html"
        )
    if (
        steenrod_review_packet_path is not None
        or steenrod_coverage_report_path is not None
    ) and not steenrod_review_candidate:
        raise ValueError("Steenrod review materials require a review-candidate atlas")
    if steenrod_review_candidate and steenrod_acceptance_record_path is not None:
        raise ValueError(
            "Steenrod review-candidate and accepted-release builds are mutually exclusive"
        )
    include_steenrod = (
        steenrod_review_candidate or steenrod_acceptance_record_path is not None
    )
    atlas = build_read_model(
        database_path,
        allow_malformed_for_review=allow_malformed_for_review,
        steenrod_review_candidate=include_steenrod,
    )
    if allow_public_review_preview:
        atlas["snapshot"]["spectrum_release_status"] = "public_review_preview"
    candidate_html = render_atlas(atlas)
    packet: dict[str, Any] | None = None
    coverage_report: str | None = None
    if include_steenrod:
        packet = build_steenrod_review_packet(atlas, candidate_html)
        coverage_report = render_steenrod_coverage_report(packet)
    acceptance_record_sha256: str | None = None
    if steenrod_acceptance_record_path is not None:
        acceptance_bytes = steenrod_acceptance_record_path.read_bytes()
        acceptance = json.loads(acceptance_bytes)
        acceptance_record_sha256 = hashlib.sha256(acceptance_bytes).hexdigest()
        if packet is None or coverage_report is None:
            raise AssertionError("accepted Steenrod build lacks its candidate materials")
        atlas = finalize_steenrod_atlas(
            atlas,
            packet,
            coverage_report,
            acceptance,
            acceptance_record_sha256,
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            spectrum_database_path = (
                Path(temporary_directory) / "steenrod-cw49-v1.sqlite3"
            )
            spectrum_materialization = materialize_accepted_steenrod_database(
                spectrum_database_path,
                packet,
                coverage_report,
                steenrod_acceptance_record_path,
            )
        atlas["snapshot"].update(
            {
                "spectrum_database_hash_kind": spectrum_materialization[
                    "logical_database_hash_kind"
                ],
                "spectrum_database_sha256": spectrum_materialization[
                    "logical_database_sha256"
                ],
                "spectrum_materialization": spectrum_materialization,
            }
        )
        html = render_atlas(atlas)
    else:
        html = candidate_html
    html_bytes = len(html.encode("utf-8"))
    if html_bytes > MAX_HTML_BYTES:
        raise ValueError(
            f"static atlas is {html_bytes} bytes; limit is {MAX_HTML_BYTES}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8", newline="\n")
    summary = {
        "conceptual_space_count": atlas["snapshot"]["conceptual_space_count"],
        "conceptual_spectrum_count": atlas["snapshot"]["conceptual_spectrum_count"],
        "evidence_count": atlas["snapshot"]["evidence_count"],
        "model_count": atlas["snapshot"]["model_count"],
        "citation_count": atlas["snapshot"]["citation_count"],
        "relation_count": atlas["snapshot"]["relation_count"],
        "computation_count": atlas["snapshot"]["computation_count"],
        "homology_row_count": atlas["snapshot"]["homology_row_count"],
        "unresolved_reference_count": atlas["snapshot"]["unresolved_reference_count"],
        "html_bytes": output_path.stat().st_size,
        "source_database_bytes": database_path.stat().st_size,
        "source_database_hash_kind": atlas["snapshot"]["source_database_hash_kind"],
        "source_database_sha256": atlas["snapshot"]["source_database_sha256"],
        "source_database_physical_sha256": file_sha256(database_path),
    }
    if (
        steenrod_review_packet_path is not None
        or steenrod_coverage_report_path is not None
    ):
        if packet is None or coverage_report is None:
            raise AssertionError("Steenrod review materials lack a candidate packet")
        if steenrod_review_packet_path is not None:
            packet_text = render_steenrod_review_packet(packet)
            steenrod_review_packet_path.parent.mkdir(parents=True, exist_ok=True)
            steenrod_review_packet_path.write_text(
                packet_text,
                encoding="utf-8",
                newline="\n",
            )
            summary["steenrod_review_packet_sha256"] = hashlib.sha256(
                packet_text.encode("utf-8")
            ).hexdigest()
        if steenrod_coverage_report_path is not None:
            steenrod_coverage_report_path.parent.mkdir(parents=True, exist_ok=True)
            steenrod_coverage_report_path.write_text(
                coverage_report,
                encoding="utf-8",
                newline="\n",
            )
            summary["steenrod_coverage_report_sha256"] = hashlib.sha256(
                coverage_report.encode("utf-8")
            ).hexdigest()
    if acceptance_record_sha256 is not None:
        spectrum_snapshot = atlas["snapshot"]["spectrum_snapshot"]
        summary.update(
            {
                "steenrod_acceptance_record_sha256": acceptance_record_sha256,
                "steenrod_candidate_sha256": packet["candidate_sha256"],
                "steenrod_spectrum_snapshot_id": spectrum_snapshot["snapshot_id"],
                "steenrod_spectrum_snapshot_sha256": spectrum_snapshot[
                    "manifest_sha256"
                ],
                "steenrod_assertion_review_count": spectrum_snapshot[
                    "assertion_reviews"
                ]["count"],
                "steenrod_assertion_review_manifest_sha256": spectrum_snapshot[
                    "assertion_reviews"
                ]["manifest_sha256"],
                "steenrod_editorial_admission_count": spectrum_snapshot[
                    "editorial_admissions"
                ]["count"],
                "steenrod_editorial_admission_manifest_sha256": spectrum_snapshot[
                    "editorial_admissions"
                ]["manifest_sha256"],
                "spectrum_database_hash_kind": atlas["snapshot"][
                    "spectrum_database_hash_kind"
                ],
                "spectrum_database_sha256": atlas["snapshot"][
                    "spectrum_database_sha256"
                ],
                "steenrod_materialization_sha256": atlas["snapshot"][
                    "spectrum_materialization"
                ]["materialization_sha256"],
            }
        )
    return summary


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
    steenrod_release = parser.add_mutually_exclusive_group()
    steenrod_release.add_argument(
        "--steenrod-review-candidate",
        action="store_true",
        help=(
            "include the imported-unreviewed cw49 spectrum corpus in a local "
            "review artifact; ordinary exports keep it withheld"
        ),
    )
    steenrod_release.add_argument(
        "--steenrod-acceptance-record",
        type=Path,
        help=(
            "build the accepted cw49 artifact only when the supplied structured "
            "Dan Isaksen acceptance matches the exact candidate and release manifests"
        ),
    )
    parser.add_argument(
        "--allow-public-review-preview",
        action="store_true",
        help=(
            "explicitly allow the imported-unreviewed review candidate to target "
            "the public atlas; the UI keeps its awaiting-review labels"
        ),
    )
    parser.add_argument(
        "--steenrod-review-packet",
        type=Path,
        help="write the deterministic imported-unreviewed packet for Dan Isaksen",
    )
    parser.add_argument(
        "--steenrod-coverage-report",
        type=Path,
        help="write a deterministic human-readable cw49 coverage report",
    )
    args = parser.parse_args()
    if (
        args.steenrod_review_packet is not None
        or args.steenrod_coverage_report is not None
    ) and not args.steenrod_review_candidate:
        parser.error("Steenrod review outputs require --steenrod-review-candidate")
    if args.allow_public_review_preview and not args.steenrod_review_candidate:
        parser.error(
            "--allow-public-review-preview requires --steenrod-review-candidate"
        )
    return args


def main() -> int:
    args = parse_args()
    if args.database:
        summary = export_atlas(
            args.database.resolve(),
            args.output.resolve(),
            allow_malformed_for_review=args.allow_malformed_for_review,
            steenrod_review_candidate=args.steenrod_review_candidate,
            steenrod_review_packet_path=(
                args.steenrod_review_packet.resolve()
                if args.steenrod_review_packet
                else None
            ),
            steenrod_coverage_report_path=(
                args.steenrod_coverage_report.resolve()
                if args.steenrod_coverage_report
                else None
            ),
            steenrod_acceptance_record_path=(
                args.steenrod_acceptance_record.resolve()
                if args.steenrod_acceptance_record
                else None
            ),
            allow_public_review_preview=args.allow_public_review_preview,
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
                steenrod_review_candidate=args.steenrod_review_candidate,
                steenrod_review_packet_path=(
                    args.steenrod_review_packet.resolve()
                    if args.steenrod_review_packet
                    else None
                ),
                steenrod_coverage_report_path=(
                    args.steenrod_coverage_report.resolve()
                    if args.steenrod_coverage_report
                    else None
                ),
                steenrod_acceptance_record_path=(
                    args.steenrod_acceptance_record.resolve()
                    if args.steenrod_acceptance_record
                    else None
                ),
                allow_public_review_preview=args.allow_public_review_preview,
            )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
