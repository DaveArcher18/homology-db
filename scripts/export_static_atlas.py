#!/usr/bin/env python3
"""Export the Homology DB preview as one self-contained atlas document."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from homology_db.preview import COEFFICIENTS, Tools


SOURCE_DIRECTORY = REPOSITORY_ROOT / "static_atlas"
READ_MODEL_VERSION = "homology-db.static-atlas/1"
THEORY_ID = "ordinary_homology"


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_commit() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def source_commit_timestamp() -> int | None:
    completed = subprocess.run(
        ["git", "show", "-s", "--format=%ct", "HEAD"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    try:
        return int(completed.stdout.strip())
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
                "from homology_db.preview import PreviewDatabase; "
                "PreviewDatabase.build(Path(__import__('sys').argv[1]))"
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


def homology_convention_id(snapshot_version: str, reduced: bool) -> str:
    convention = "reduced" if reduced else "unreduced"
    return f"{snapshot_version}#ordinary-homology-{convention}"


def validate_read_model(atlas: dict[str, Any]) -> None:
    conceptual_spaces = atlas["conceptual_spaces"]
    conceptual_space_ids = [item["id"] for item in conceptual_spaces]
    slugs = [item["slug"] for item in conceptual_spaces]
    if len(conceptual_space_ids) != len(set(conceptual_space_ids)):
        raise ValueError("static atlas contains duplicate stable Conceptual-space IDs")
    if len(slugs) != len(set(slugs)):
        raise ValueError("static atlas contains duplicate Conceptual-space slugs")
    required_fields = ("id", "slug", "kind", "name", "taxonomy", "homology")
    malformed_spaces = []
    for conceptual_space in conceptual_spaces:
        missing = [field for field in required_fields if not conceptual_space.get(field)]
        if missing:
            malformed_spaces.append(f"{conceptual_space.get('id', '<missing id>')}: {missing}")
        if conceptual_space["data_quality"]["missing_required_fields"]:
            malformed_spaces.append(
                f"{conceptual_space['id']}: "
                f"{conceptual_space['data_quality']['missing_required_fields']}"
            )
    if malformed_spaces:
        raise ValueError(f"malformed Conceptual-space records: {malformed_spaces}")
    evidence_ids = {
        evidence["id"] for item in conceptual_spaces for evidence in item["evidence"]
    }
    referenced_evidence = {
        evidence_id
        for item in conceptual_spaces
        for row in item["homology"]
        for evidence_id in row["evidence_ids"]
    }
    missing_evidence = sorted(referenced_evidence - evidence_ids)
    if missing_evidence:
        raise ValueError(f"unresolved evidence references: {missing_evidence}")
    known_ids = set(conceptual_space_ids)
    unresolved_relations = [
        relation
        for item in conceptual_spaces
        for relation in item["relations"]
        if relation.get("target_id") not in known_ids
    ]
    atlas["snapshot"]["unresolved_reference_count"] = len(unresolved_relations)
    section_ids = [conceptual_space_id for section in atlas["sections"] for conceptual_space_id in section["conceptual_space_ids"]]
    if sorted(section_ids) != sorted(conceptual_space_ids):
        raise ValueError("static atlas sections must contain every Conceptual space exactly once")


def build_read_model(database_path: Path) -> dict[str, Any]:
    if not database_path.exists():
        raise FileNotFoundError(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"SQLite integrity failure: {integrity}")
        snapshot_rows = connection.execute("SELECT * FROM snapshot").fetchall()
        if len(snapshot_rows) != 1:
            raise ValueError("static atlas requires exactly one Snapshot")
        snapshot_row = dict(snapshot_rows[0])
        spaces = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM space ORDER BY family, label, space_id"
            )
        ]
        aliases_by_space: dict[str, list[str]] = defaultdict(list)
        for row in connection.execute(
            "SELECT space_id, display_alias FROM alias ORDER BY display_alias, space_id"
        ):
            aliases_by_space[row["space_id"]].append(row["display_alias"])

    tools = Tools(database_path)
    summary = tools.corpus_summary()
    if summary["subject_count"] != len(spaces):
        raise ValueError("Snapshot subject count does not match enumerated spaces")

    conceptual_spaces: list[dict[str, Any]] = []
    evidence_total = 0
    homology_total = 0
    for space in spaces:
        aliases = sorted(
            {
                alias
                for alias in aliases_by_space[space["space_id"]]
                if alias not in {space["space_id"], space["label"]}
            },
            key=lambda value: (value.casefold(), value),
        )
        homology: list[dict[str, Any]] = []
        raw_homology: list[dict[str, Any]] = []
        space_evidence_ids: set[str] = set()
        for coefficient in COEFFICIENTS:
            for reduced in (False, True):
                response = tools.read_homology(
                    space["space_id"], coefficient=coefficient, reduced=reduced
                )
                if response["outcome"] != "selected":
                    raise ValueError(
                        f"could not export {space['space_id']} ({coefficient}, reduced={reduced})"
                    )
                raw_homology.append(response)
                for group in response["groups"]:
                    space_evidence_ids.add(group["evidence_id"])
                    homology.append(
                        {
                            "theory": THEORY_ID,
                            "coefficient_ring": coefficient,
                            "coefficient_system": f"preview:{coefficient}",
                            "homology_convention": homology_convention_id(
                                snapshot_row["schema_version"], reduced
                            ),
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
                f"unresolved evidence for {space['space_id']}: {expanded['missing_evidence_ids']}"
            )
        evidence = [
            {
                "id": item["evidence_id"],
                "kind": "owned_computation_evidence",
                "citation": None,
                "locator": None,
                "reliability": None,
                "release_status": summary["release_status"],
                "algorithm_id": item["algorithm_id"],
                "chain_sha256": item["chain_sha256"],
                "representatives_state": item["representatives_state"],
                "induced_maps_state": item["induced_maps_state"],
            }
            for item in expanded["evidence"]
        ]
        missing_required_fields = [
            field
            for field in ("space_id", "label", "family", "dimension")
            if space.get(field) is None or space.get(field) == ""
        ]
        conceptual_space_record = {
            "id": space["space_id"],
            "slug": slug_from_id(space["space_id"]),
            "kind": "conceptual_space",
            "name": {"plain": space["label"], "tex": None},
            "aliases": aliases,
            "summary": "",
            "taxonomy": {"family": space["family"], "tags": []},
            "properties": [
                {"key": "dimension", "label": "dimension", "value": space["dimension"]},
                {
                    "key": "equivalence_kind",
                    "label": "preview model relation",
                    "value": space["equivalence_kind"],
                },
            ],
            "homology": homology,
            "models": [],
            "relations": [],
            "evidence": evidence,
            "computations": [],
            "data_quality": {
                "state": "valid" if not missing_required_fields else "malformed",
                "missing_required_fields": missing_required_fields,
                "malformed_fields": [],
            },
            "raw": {
                "subject": space,
                "aliases": aliases,
                "homology_responses": raw_homology,
                "evidence_response": expanded,
            },
        }
        conceptual_spaces.append(conceptual_space_record)
        evidence_total += len(evidence)
        homology_total += len(homology)
    tools.connection.close()

    sections_by_family: dict[str, list[str]] = defaultdict(list)
    for item in conceptual_spaces:
        sections_by_family[item["taxonomy"]["family"]].append(item["id"])
    sections = [
        {
            "id": family,
            "label": family.replace("_", " ").title(),
            "conceptual_space_ids": conceptual_space_ids,
        }
        for family, conceptual_space_ids in sorted(sections_by_family.items())
    ]
    modified_at = datetime.fromtimestamp(database_path.stat().st_mtime, UTC).replace(
        microsecond=0
    )
    atlas = {
        "snapshot": {
            "snapshot_id": snapshot_row["snapshot_id"],
            "snapshot_version": snapshot_row["schema_version"],
            "schema_version": READ_MODEL_VERSION,
            "generated_at": modified_at.isoformat().replace("+00:00", "Z"),
            "conceptual_space_count": len(conceptual_spaces),
            "evidence_count": evidence_total,
            "homology_row_count": homology_total,
            "source_database_bytes": database_path.stat().st_size,
            "source_database_sha256": file_sha256(database_path),
            "source_commit": source_commit(),
            "release_status": summary["release_status"],
            "supported_coefficients": list(COEFFICIENTS),
            "homology_theory": THEORY_ID,
            "homology_conventions": [
                homology_convention_id(snapshot_row["schema_version"], reduced)
                for reduced in (False, True)
            ],
        },
        "sections": sections,
        "conceptual_spaces": conceptual_spaces,
    }
    validate_read_model(atlas)
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
    javascript = (SOURCE_DIRECTORY / "atlas.js").read_text(encoding="utf-8")
    replacements = {
        "/*__ATLAS_CSS__*/": css,
        "__ATLAS_JSON__": safe_embedded_json(atlas),
        "/*__ATLAS_JS__*/": javascript,
    }
    for marker, replacement in replacements.items():
        if template.count(marker) != 1:
            raise ValueError(f"template must contain marker exactly once: {marker}")
        template = template.replace(marker, replacement)
    return template


def export_atlas(database_path: Path, output_path: Path) -> dict[str, Any]:
    atlas = build_read_model(database_path)
    html = render_atlas(atlas)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8", newline="\n")
    return {
        "conceptual_space_count": atlas["snapshot"]["conceptual_space_count"],
        "evidence_count": atlas["snapshot"]["evidence_count"],
        "unresolved_reference_count": atlas["snapshot"]["unresolved_reference_count"],
        "html_bytes": output_path.stat().st_size,
        "source_database_sha256": atlas["snapshot"]["source_database_sha256"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--database", type=Path, help="existing preview SQLite Snapshot")
    source.add_argument(
        "--snapshot",
        choices=["current"],
        help="build the current disposable preview Snapshot before export",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.database:
        summary = export_atlas(args.database.resolve(), args.output.resolve())
    else:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "homology-db-preview.sqlite3"
            build_current_database(database_path)
            commit_timestamp = source_commit_timestamp()
            if commit_timestamp is not None:
                os.utime(database_path, (commit_timestamp, commit_timestamp))
            summary = export_atlas(database_path, args.output.resolve())
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
