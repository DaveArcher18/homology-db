"""Materialize an accepted cw49 Steenrod review into the v5 atlas ledger.

This module is deliberately acceptance-gated.  It does not create or infer a
review decision: callers must provide the exact deterministic review packet,
its coverage report, and a structured Dan Isaksen acceptance record bound to
both artifacts.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from homology_db.atlas_schema import AtlasSchema, SCHEMA_VERSION
from homology_db.steenrod import CW49_SPECTRUM_IDS
from scripts.export_static_atlas import (
    _canonical_sha256,
    _steenrod_assertion_targets,
    build_spectrum_read_model,
    build_steenrod_review_packet,
    render_steenrod_coverage_report,
    render_steenrod_review_packet,
    source_commit,
    source_inputs_sha256,
    validate_steenrod_acceptance_record,
)


MATERIALIZATION_SCHEMA_VERSION = "homology-db.steenrod-materialization/1"
SELECTION_POLICY_ID = "homology-db.steenrod-accepted-exact/1"
LOGICAL_DATABASE_HASH_KIND = "homology-db.sqlite-logical/2"


class SteenrodMaterializationError(ValueError):
    """The accepted review cannot be materialized exactly."""


class DuplicateSteenrodMaterializationError(SteenrodMaterializationError):
    """The bound spectrum Snapshot is already present."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def canonical_logical_database_sha256(path: Path) -> str:
    """Hash ordered SQLite content while excluding runtime diagnostics.

    ``schema_migration.applied_at`` records when one physical file happened to
    be built. It is useful diagnostic metadata, but is not part of logical
    database identity. Every other value remains semantic and is hashed.
    """

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
                SELECT name FROM sqlite_master
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
            rows: list[list[Any]] = []
            for raw_row in connection.execute(
                f"SELECT {projection} FROM {quoted(table_name)} ORDER BY {order}"
            ):
                row = [json_value(value) for value in raw_row]
                if table_name == "schema_migration" and "applied_at" in column_names:
                    row[column_names.index("applied_at")] = {
                        "runtime_diagnostic": "excluded"
                    }
                rows.append(row)
            tables.append({"name": table_name, "columns": columns, "rows": rows})
    logical_bytes = _canonical_json(
        {
            "schema_version": LOGICAL_DATABASE_HASH_KIND,
            "schema_objects": schema_objects,
            "tables": tables,
        }
    ).encode("utf-8")
    return hashlib.sha256(logical_bytes).hexdigest()


def _read_json_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SteenrodMaterializationError(f"{label} is not valid JSON") from error
    if not isinstance(value, dict):
        raise SteenrodMaterializationError(f"{label} must be a JSON object")
    return value, raw


def _current_packet_projection(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Rebuild every packet field except the reviewed HTML byte hash."""

    build = packet.get("build")
    if not isinstance(build, Mapping):
        raise SteenrodMaterializationError("review packet requires build bindings")
    spectra, source = build_spectrum_read_model()
    atlas = {
        "conceptual_spectra": spectra,
        "snapshot": {
            "spectrum_source": source,
            "source_commit": build.get("source_commit"),
            "source_inputs_sha256": build.get("source_inputs_sha256"),
            "source_database_hash_kind": build.get("source_database_hash_kind"),
            "source_database_sha256": build.get("source_database_sha256"),
        },
    }
    expected = build_steenrod_review_packet(atlas, "")
    expected["atlas_html_sha256"] = packet.get("atlas_html_sha256")
    return expected


def _validate_inputs(
    review_packet_path: Path,
    coverage_report_path: Path,
    acceptance_record_path: Path,
) -> tuple[
    dict[str, Any],
    str,
    dict[str, Any],
    str,
    list[dict[str, Any]],
]:
    packet, packet_bytes = _read_json_object(review_packet_path, "review packet")
    canonical_packet = render_steenrod_review_packet(packet).encode("utf-8")
    if packet_bytes != canonical_packet:
        raise SteenrodMaterializationError(
            "review packet bytes are not the exact deterministic packet"
        )

    try:
        coverage_report = coverage_report_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise SteenrodMaterializationError(
            "coverage report is not valid UTF-8"
        ) from error
    expected_coverage = render_steenrod_coverage_report(packet)
    if coverage_report != expected_coverage:
        raise SteenrodMaterializationError(
            "coverage report does not exactly match the review packet"
        )

    current_packet = _current_packet_projection(packet)
    if packet != current_packet:
        raise SteenrodMaterializationError(
            "review packet is stale or does not match the canonical cw49 candidate"
        )
    if packet["build"]["source_inputs_sha256"] != source_inputs_sha256():
        raise SteenrodMaterializationError(
            "review packet is stale relative to the current release inputs"
        )
    if packet["build"]["source_commit"] != source_commit():
        raise SteenrodMaterializationError(
            "review packet is bound to a different source commit"
        )

    acceptance, acceptance_bytes = _read_json_object(
        acceptance_record_path, "acceptance record"
    )
    try:
        validate_steenrod_acceptance_record(
            acceptance,
            packet,
            coverage_report,
        )
    except ValueError as error:
        raise SteenrodMaterializationError(str(error)) from error

    spectra, _source = build_spectrum_read_model()
    acceptance_sha256 = hashlib.sha256(acceptance_bytes).hexdigest()
    return packet, coverage_report, acceptance, acceptance_sha256, spectra


@dataclass(frozen=True)
class _EvidenceRow:
    evidence_id: str
    record_sha256: str
    rule_source_sha256: str
    source_snapshot: str
    source_locator: str
    normalized_module_sha256: str


@dataclass(frozen=True)
class _AssertionRow:
    assertion_id: str
    assertion_kind: str
    spectrum_id: str
    module_id: str
    slot_key: str
    claim_sha256: str
    evidence_id: str
    source_basis_element_id: str | None = None
    operation_degree: int | None = None
    target_basis_element_ids: tuple[str, ...] = ()
    source_position_start: int | None = None
    source_position_end: int | None = None
    maximum_operation_degree: int | None = None
    region_json: str | None = None


def _module_id(spectrum_id: str, basis_version: str) -> str:
    module_version = basis_version.split(":", 1)[0]
    return f"steenrod-module:{spectrum_id}:{module_version}"


def _make_records(
    packet: Mapping[str, Any], spectra: list[dict[str, Any]]
) -> tuple[list[_EvidenceRow], list[_AssertionRow]]:
    target_rows = _steenrod_assertion_targets(spectra)
    target_hash_by_id = {
        row["assertion_id"]: row["claim_sha256"] for row in target_rows
    }
    if len(target_hash_by_id) != 5_828:
        raise SteenrodMaterializationError(
            "canonical release projection does not contain 5,828 assertions"
        )

    evidence_rows: list[_EvidenceRow] = []
    assertion_rows: list[_AssertionRow] = []
    for spectrum in sorted(spectra, key=lambda item: item["spectrum_id"]):
        spectrum_id = spectrum["spectrum_id"]
        module = spectrum["module"]
        module_id = _module_id(spectrum_id, module["basis_version"])
        evidence_payload = {
            "evidence_kind": "derivation",
            "spectrum_id": spectrum_id,
            "module_content_sha256": module["content_sha256"],
            "source_snapshot": module["source_snapshot"],
            "source_locator": module["source_locator"],
            "rule_id": "cw49-pinned-source-normalization",
            "rule_version": "v126.3",
        }
        evidence_rows.append(
            _EvidenceRow(
                evidence_id=f"steenrod-source-derivation:{spectrum_id}",
                record_sha256=_sha256(evidence_payload),
                rule_source_sha256=packet["build"]["source_inputs_sha256"],
                source_snapshot=module["source_snapshot"],
                source_locator=module["source_locator"],
                normalized_module_sha256=module["content_sha256"],
            )
        )
        if module["module_type"] == "profile":
            continue

        basis_position = {
            element["basis_id"]: position
            for position, element in enumerate(module["basis"])
        }
        evidence_id = evidence_rows[-1].evidence_id
        for action in module["actions"]:
            assertion_id = (
                f"steenrod-action:{spectrum_id}:"
                f"{action['source_basis_id']}:Sq{action['square_degree']}"
            )
            claim = {
                "assertion_kind": "steenrod_action",
                "spectrum_id": spectrum_id,
                "module_content_sha256": module["content_sha256"],
                "source_basis_id": action["source_basis_id"],
                "square_degree": action["square_degree"],
                "target_basis_ids": action["target_basis_ids"],
                "knowledge_state": module["action_knowledge_state_default"],
            }
            claim_sha256 = _canonical_sha256(claim)
            if target_hash_by_id.get(assertion_id) != claim_sha256:
                raise SteenrodMaterializationError(
                    f"release projection mismatch for {assertion_id}"
                )
            targets = tuple(
                sorted(
                    action["target_basis_ids"],
                    key=basis_position.__getitem__,
                )
            )
            assertion_rows.append(
                _AssertionRow(
                    assertion_id=assertion_id,
                    assertion_kind="steenrod_action",
                    spectrum_id=spectrum_id,
                    module_id=module_id,
                    slot_key=(
                        f"{module_id}|{action['source_basis_id']}|"
                        f"Sq{action['square_degree']}"
                    ),
                    claim_sha256=claim_sha256,
                    evidence_id=evidence_id,
                    source_basis_element_id=action["source_basis_id"],
                    operation_degree=action["square_degree"],
                    target_basis_element_ids=targets,
                )
            )

        completeness = module["completeness"]
        completeness_id = (
            f"steenrod-completeness:{spectrum_id}:{module['basis_version']}"
        )
        completeness_claim = {
            "assertion_kind": "steenrod_action_completeness",
            "spectrum_id": spectrum_id,
            "module_content_sha256": module["content_sha256"],
            "basis_version": module["basis_version"],
            "knowledge_state": completeness["knowledge_state"],
            "slot_count": completeness["slot_count"],
        }
        completeness_sha256 = _canonical_sha256(completeness_claim)
        if target_hash_by_id.get(completeness_id) != completeness_sha256:
            raise SteenrodMaterializationError(
                f"release projection mismatch for {completeness_id}"
            )
        maximum_operation_degree = max(
            (action["square_degree"] for action in module["actions"]),
            default=1,
        )
        region = {
            "basis_positions": [0, len(module["basis"]) - 1],
            "maximum_operation_degree": maximum_operation_degree,
        }
        assertion_rows.append(
            _AssertionRow(
                assertion_id=completeness_id,
                assertion_kind="steenrod_action_completeness",
                spectrum_id=spectrum_id,
                module_id=module_id,
                slot_key=f"{module_id}|steenrod-action-completeness",
                claim_sha256=completeness_sha256,
                evidence_id=evidence_id,
                source_position_start=0,
                source_position_end=len(module["basis"]) - 1,
                maximum_operation_degree=maximum_operation_degree,
                region_json=_canonical_json(region),
            )
        )

    assertion_rows.sort(key=lambda row: row.assertion_id)
    if len(evidence_rows) != 49 or len(assertion_rows) != 5_828:
        raise SteenrodMaterializationError("canonical cw49 record counts changed")
    if {spectrum["spectrum_id"] for spectrum in spectra} != set(CW49_SPECTRUM_IDS):
        raise SteenrodMaterializationError("canonical cw49 spectrum identities changed")
    if packet["release_projection"]["assertion_reviews"]["count"] != len(
        assertion_rows
    ):
        raise SteenrodMaterializationError("review manifest assertion count mismatch")
    return evidence_rows, assertion_rows


def _insert_subjects_and_modules(
    connection: sqlite3.Connection,
    spectra: Iterable[dict[str, Any]],
) -> None:
    for spectrum in sorted(spectra, key=lambda item: item["spectrum_id"]):
        spectrum_id = spectrum["spectrum_id"]
        permanent_label = spectrum["name"]["plain"]
        spectrum_hash = _sha256(
            {
                "record_kind": "conceptual_spectrum",
                "spectrum_id": spectrum_id,
                "permanent_label": permanent_label,
            }
        )
        connection.execute(
            "INSERT INTO conceptual_spectrum VALUES (?, ?, ?)",
            (spectrum_id, permanent_label, spectrum_hash),
        )
        name_id = f"spectrum-name:{spectrum_id}:label"
        name_hash = _sha256(
            {
                "record_kind": "spectrum_name",
                "name_id": name_id,
                "spectrum_id": spectrum_id,
                "normalized_name": permanent_label.casefold(),
                "display_name": permanent_label,
                "name_kind": "label",
            }
        )
        connection.execute(
            """
            INSERT INTO spectrum_name(
                name_id, spectrum_id, normalized_name, display_name,
                name_kind, identity_assertion_id, record_sha256
            ) VALUES (?, ?, ?, ?, 'label', NULL, ?)
            """,
            (
                name_id,
                spectrum_id,
                permanent_label.casefold(),
                permanent_label,
                name_hash,
            ),
        )

        module = spectrum["module"]
        module_id = _module_id(spectrum_id, module["basis_version"])
        module_kind = module["module_type"]
        connection.execute(
            """
            INSERT INTO steenrod_module(
                module_id, subject_kind, subject_id, module_kind,
                module_category, coefficient_prime, reduced,
                grading_convention, suspension_shift, format_version,
                module_version, basis_version, profile_json, record_sha256
            ) VALUES (
                ?, 'conceptual_spectrum', ?, ?, ?, 2, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                module_id,
                spectrum_id,
                module_kind,
                module["category"],
                int(module["reduced"]),
                module["grading_convention"],
                module["suspension_shift"],
                module["schema_version"],
                module["basis_version"].split(":", 1)[0],
                module["basis_version"] if module_kind == "finite_basis" else None,
                (
                    _canonical_json(module["profile"])
                    if module_kind == "profile"
                    else None
                ),
                module["content_sha256"],
            ),
        )
        for position, element in enumerate(module.get("basis", [])):
            basis_hash = _sha256(
                {
                    "record_kind": "steenrod_basis_element",
                    "module_id": module_id,
                    "basis_element_id": element["basis_id"],
                    "basis_key": element["name"],
                    "degree": element["degree"],
                    "position": position,
                    "degree_ordinal": element["ordinal"],
                }
            )
            connection.execute(
                """
                INSERT INTO steenrod_basis_element(
                    basis_element_id, module_id, basis_key, display_name,
                    degree, position, degree_ordinal, record_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    element["basis_id"],
                    module_id,
                    element["name"],
                    element["name"],
                    element["degree"],
                    position,
                    element["ordinal"],
                    basis_hash,
                ),
            )


def _insert_evidence(
    connection: sqlite3.Connection, evidence_rows: Iterable[_EvidenceRow]
) -> None:
    for row in evidence_rows:
        connection.execute(
            "INSERT INTO evidence VALUES (?, 'derivation', ?)",
            (row.evidence_id, row.record_sha256),
        )
        connection.execute(
            "INSERT INTO derivation_evidence VALUES (?, ?, ?, ?)",
            (
                row.evidence_id,
                "cw49-pinned-source-normalization",
                "v126.3",
                row.rule_source_sha256,
            ),
        )
        connection.execute(
            "INSERT INTO steenrod_import_evidence VALUES (?, ?, ?, ?)",
            (
                row.evidence_id,
                row.source_snapshot,
                row.source_locator,
                row.normalized_module_sha256,
            ),
        )


def _insert_module_evidence(
    connection: sqlite3.Connection,
    spectra: Iterable[dict[str, Any]],
    evidence_rows: Iterable[_EvidenceRow],
) -> None:
    evidence_by_hash = {
        row.normalized_module_sha256: row.evidence_id for row in evidence_rows
    }
    for spectrum in spectra:
        module = spectrum["module"]
        module_id = _module_id(spectrum["spectrum_id"], module["basis_version"])
        connection.execute(
            "INSERT INTO steenrod_module_evidence VALUES (?, ?, 'derives')",
            (module_id, evidence_by_hash[module["content_sha256"]]),
        )


def _insert_assertions(
    connection: sqlite3.Connection, assertion_rows: Iterable[_AssertionRow]
) -> None:
    for row in assertion_rows:
        connection.execute(
            """
            INSERT INTO assertion(
                assertion_id, assertion_kind, subject_kind, subject_id,
                slot_key, knowledge_state, claim_fingerprint,
                payload_sha256, record_sha256
            ) VALUES (?, ?, 'conceptual_spectrum', ?, ?, 'exact', ?, ?, ?)
            """,
            (
                row.assertion_id,
                row.assertion_kind,
                row.spectrum_id,
                row.slot_key,
                row.claim_sha256,
                row.claim_sha256,
                row.claim_sha256,
            ),
        )
        if row.assertion_kind == "steenrod_action":
            connection.execute(
                "INSERT INTO steenrod_action_assertion VALUES (?, ?, ?, ?)",
                (
                    row.assertion_id,
                    row.module_id,
                    row.source_basis_element_id,
                    row.operation_degree,
                ),
            )
            for position, target_basis_id in enumerate(
                row.target_basis_element_ids
            ):
                connection.execute(
                    "INSERT INTO steenrod_action_term VALUES (?, ?, ?, ?)",
                    (
                        row.assertion_id,
                        row.module_id,
                        target_basis_id,
                        position,
                    ),
                )
        else:
            connection.execute(
                "INSERT INTO completeness_assertion VALUES (?, ?, ?)",
                (
                    row.assertion_id,
                    row.region_json,
                    "steenrod_action_coverage",
                ),
            )
            connection.execute(
                """
                INSERT INTO steenrod_action_completeness_assertion
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row.assertion_id,
                    row.module_id,
                    row.source_position_start,
                    row.source_position_end,
                    row.maximum_operation_degree,
                ),
            )
        connection.execute(
            "INSERT INTO assertion_evidence VALUES (?, ?, 'derives')",
            (row.assertion_id, row.evidence_id),
        )


def _insert_reviews_and_admissions(
    connection: sqlite3.Connection,
    assertion_rows: list[_AssertionRow],
    spectra: list[dict[str, Any]],
    packet: Mapping[str, Any],
    acceptance: Mapping[str, Any],
    acceptance_sha256: str,
) -> tuple[str, dict[str, tuple[str, str]]]:
    reviews: dict[str, tuple[str, str]] = {}
    evidence_locator = acceptance["evidence"]["locator"]
    for row in assertion_rows:
        review_id = f"steenrod-review:{row.assertion_id}"
        review_hash = _sha256(
            {
                "assertion_review_id": review_id,
                "assertion_id": row.assertion_id,
                "assertion_record_sha256": row.claim_sha256,
                "reviewer": "Dan Isaksen",
                "verdict": "accept",
                "reviewed_at": acceptance["reviewed_at"],
                "acceptance_record_sha256": acceptance_sha256,
                "acceptance_evidence_sha256": acceptance["evidence"]["sha256"],
            }
        )
        note = (
            "Accepted through the bound cw49 review packet; retained written "
            f"acceptance: {evidence_locator}"
        )
        connection.execute(
            "INSERT INTO assertion_review VALUES (?, ?, ?, 'accept', ?, ?, ?)",
            (
                review_id,
                row.assertion_id,
                "Dan Isaksen",
                acceptance["reviewed_at"],
                note,
                review_hash,
            ),
        )
        reviews[row.assertion_id] = (review_id, review_hash)

    snapshot_id = packet["release_projection"]["spectrum_snapshot"]["snapshot_id"]
    event_id = f"steenrod-admission:{snapshot_id}"
    event_hash = _sha256(
        {
            "event_id": event_id,
            "event_kind": "admit",
            "actor": acceptance["editorial_actor"],
            "occurred_at": acceptance["reviewed_at"],
            "acceptance_record_sha256": acceptance_sha256,
            "editorial_admission_manifest_sha256": packet["release_projection"][
                "editorial_admissions"
            ]["manifest_sha256"],
        }
    )
    connection.execute(
        "INSERT INTO editorial_event VALUES (?, 'admit', ?, ?, ?, 0, ?)",
        (
            event_id,
            acceptance["editorial_actor"],
            "Admit the assertions and tmf profile bound by Dan Isaksen's acceptance",
            acceptance["reviewed_at"],
            event_hash,
        ),
    )
    for position, row in enumerate(assertion_rows):
        connection.execute(
            "INSERT INTO editorial_event_effect VALUES (?, ?, 'admit', ?)",
            (event_id, row.assertion_id, position),
        )

    tmf = next(item for item in spectra if item["spectrum_id"] == "tmf")
    tmf_module_id = _module_id("tmf", tmf["module"]["basis_version"])
    projected_tmf_hash = packet["release_projection"]["editorial_admissions"][
        "profile_module_content_sha256"
    ]
    if (
        tmf_module_id != "steenrod-module:tmf:cw49-v126.3"
        or tmf["module"]["content_sha256"] != projected_tmf_hash
    ):
        raise SteenrodMaterializationError(
            "tmf module admission does not match the release projection"
        )
    connection.execute(
        "INSERT INTO steenrod_module_editorial_effect VALUES (?, ?, 'admit', ?)",
        (event_id, tmf_module_id, len(assertion_rows)),
    )
    return event_id, reviews


def _insert_snapshot_and_projection(
    connection: sqlite3.Connection,
    packet: Mapping[str, Any],
    acceptance: Mapping[str, Any],
    spectra: list[dict[str, Any]],
    evidence_rows: list[_EvidenceRow],
    assertion_rows: list[_AssertionRow],
    reviews: Mapping[str, tuple[str, str]],
    event_id: str,
) -> dict[str, Any]:
    spectrum_snapshot = packet["release_projection"]["spectrum_snapshot"]
    snapshot_id = spectrum_snapshot["snapshot_id"]
    selection_policy_sha256 = _sha256(
        {
            "selection_policy_id": SELECTION_POLICY_ID,
            "candidate_sha256": packet["candidate_sha256"],
            "assertion_review_manifest_sha256": packet["release_projection"][
                "assertion_reviews"
            ]["manifest_sha256"],
            "editorial_admission_manifest_sha256": packet["release_projection"][
                "editorial_admissions"
            ]["manifest_sha256"],
        }
    )
    connection.execute(
        """
        INSERT INTO snapshot(
            snapshot_id, schema_version, selection_policy_id,
            selection_policy_sha256, canonical_manifest_sha256,
            current_projection_sha256, finalized_at, record_sha256
        ) VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL)
        """,
        (snapshot_id, SCHEMA_VERSION, SELECTION_POLICY_ID, selection_policy_sha256),
    )

    records: list[tuple[str, str, str]] = []
    for spectrum in spectra:
        spectrum_id = spectrum["spectrum_id"]
        spectrum_hash = connection.execute(
            "SELECT record_sha256 FROM conceptual_spectrum WHERE spectrum_id = ?",
            (spectrum_id,),
        ).fetchone()[0]
        records.append(("conceptual_spectrum", spectrum_id, spectrum_hash))
        name_id = f"spectrum-name:{spectrum_id}:label"
        name_hash = connection.execute(
            "SELECT record_sha256 FROM spectrum_name WHERE name_id = ?", (name_id,)
        ).fetchone()[0]
        records.append(("spectrum_name", name_id, name_hash))
        module_id = _module_id(spectrum_id, spectrum["module"]["basis_version"])
        records.append(
            ("steenrod_module", module_id, spectrum["module"]["content_sha256"])
        )
        records.extend(
            (
                "steenrod_basis_element",
                basis_id,
                record_sha256,
            )
            for basis_id, record_sha256 in connection.execute(
                """
                SELECT basis_element_id, record_sha256
                FROM steenrod_basis_element
                WHERE module_id = ? ORDER BY position
                """,
                (module_id,),
            )
        )
    records.extend(
        ("evidence", row.evidence_id, row.record_sha256) for row in evidence_rows
    )
    for row in assertion_rows:
        records.append(("assertion", row.assertion_id, row.claim_sha256))
        review_id, review_hash = reviews[row.assertion_id]
        records.append(("assertion_review", review_id, review_hash))
    event_hash = connection.execute(
        "SELECT record_sha256 FROM editorial_event WHERE event_id = ?", (event_id,)
    ).fetchone()[0]
    records.sort(key=lambda item: (item[0], item[1]))
    for record_kind, record_id, record_sha256 in records:
        connection.execute(
            "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
            (snapshot_id, record_kind, record_id, record_sha256),
        )
    # The shared event is last: its typed tmf effect requires the module and
    # Conceptual-spectrum members to be closed in this Snapshot first.
    connection.execute(
        "INSERT INTO snapshot_record VALUES (?, 'editorial_event', ?, ?)",
        (snapshot_id, event_id, event_hash),
    )

    action_rows = [
        row for row in assertion_rows if row.assertion_kind == "steenrod_action"
    ]
    for row in action_rows:
        projection_hash = _sha256(
            {
                "snapshot_id": snapshot_id,
                "slot_key": row.slot_key,
                "projection_outcome": "selected",
                "selected_assertion_id": row.assertion_id,
                "selected_assertion_sha256": row.claim_sha256,
            }
        )
        connection.execute(
            """
            INSERT INTO current_steenrod_action(
                snapshot_id, slot_key, module_id, source_basis_element_id,
                operation_degree, projection_outcome, selected_assertion_id,
                conflict_set_id, projection_sha256
            ) VALUES (?, ?, ?, ?, ?, 'selected', ?, NULL, ?)
            """,
            (
                snapshot_id,
                row.slot_key,
                row.module_id,
                row.source_basis_element_id,
                row.operation_degree,
                row.assertion_id,
                projection_hash,
            ),
        )

    completeness_rows = [
        row
        for row in assertion_rows
        if row.assertion_kind == "steenrod_action_completeness"
    ]
    for row in completeness_rows:
        projection_hash = _sha256(
            {
                "snapshot_id": snapshot_id,
                "subject_kind": "steenrod_module",
                "subject_id": row.module_id,
                "assertion_id": row.assertion_id,
                "assertion_sha256": row.claim_sha256,
            }
        )
        connection.execute(
            "INSERT INTO current_completeness VALUES (?, 'steenrod_module', ?, ?, ?)",
            (snapshot_id, row.module_id, row.assertion_id, projection_hash),
        )

    projection_rows = [
        list(row)
        for row in connection.execute(
            """
            SELECT slot_key, module_id, source_basis_element_id,
                   operation_degree, projection_outcome,
                   selected_assertion_id, projection_sha256
            FROM current_steenrod_action
            WHERE snapshot_id = ?
            ORDER BY slot_key
            """,
            (snapshot_id,),
        )
    ]
    completeness_projection_rows = [
        list(row)
        for row in connection.execute(
            """
            SELECT subject_kind, subject_id, assertion_id, projection_sha256
            FROM current_completeness
            WHERE snapshot_id = ? AND subject_kind = 'steenrod_module'
            ORDER BY subject_id, assertion_id
            """,
            (snapshot_id,),
        )
    ]
    current_projection_sha256 = _sha256(
        {
            "schema_version": "homology-db.steenrod-current-projection/1",
            "actions": projection_rows,
            "completeness": completeness_projection_rows,
        }
    )
    manifest_sha256 = spectrum_snapshot["manifest_sha256"]
    snapshot_record_sha256 = _sha256(
        {
            "snapshot_id": snapshot_id,
            "schema_version": SCHEMA_VERSION,
            "selection_policy_id": SELECTION_POLICY_ID,
            "selection_policy_sha256": selection_policy_sha256,
            "canonical_manifest_sha256": manifest_sha256,
            "current_projection_sha256": current_projection_sha256,
            "finalized_at": acceptance["reviewed_at"],
        }
    )
    connection.execute(
        """
        UPDATE snapshot
        SET canonical_manifest_sha256 = ?, current_projection_sha256 = ?,
            finalized_at = ?, record_sha256 = ?
        WHERE snapshot_id = ?
        """,
        (
            manifest_sha256,
            current_projection_sha256,
            acceptance["reviewed_at"],
            snapshot_record_sha256,
            snapshot_id,
        ),
    )
    return {
        "snapshot_id": snapshot_id,
        "canonical_manifest_sha256": manifest_sha256,
        "current_projection_sha256": current_projection_sha256,
        "snapshot_record_sha256": snapshot_record_sha256,
    }


def _materialization_counts(
    connection: sqlite3.Connection, snapshot_id: str, event_id: str
) -> dict[str, int]:
    spectrum_placeholders = ",".join("?" for _ in CW49_SPECTRUM_IDS)

    def scalar(sql: str, parameters: tuple[Any, ...] = ()) -> int:
        return int(connection.execute(sql, parameters).fetchone()[0])

    return {
        "spectrum_count": scalar(
            f"SELECT COUNT(*) FROM conceptual_spectrum WHERE spectrum_id IN ({spectrum_placeholders})",
            CW49_SPECTRUM_IDS,
        ),
        "spectrum_name_count": scalar(
            f"SELECT COUNT(*) FROM spectrum_name WHERE spectrum_id IN ({spectrum_placeholders})",
            CW49_SPECTRUM_IDS,
        ),
        "module_count": scalar(
            f"""
            SELECT COUNT(*) FROM steenrod_module
            WHERE subject_kind = 'conceptual_spectrum'
              AND subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "basis_element_count": scalar(
            f"""
            SELECT COUNT(*) FROM steenrod_basis_element basis
            JOIN steenrod_module module USING(module_id)
            WHERE module.subject_kind = 'conceptual_spectrum'
              AND module.subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "action_assertion_count": scalar(
            f"""
            SELECT COUNT(*) FROM steenrod_action_assertion action
            JOIN steenrod_module module USING(module_id)
            WHERE module.subject_kind = 'conceptual_spectrum'
              AND module.subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "action_term_count": scalar(
            f"""
            SELECT COUNT(*) FROM steenrod_action_term term
            JOIN steenrod_module module USING(module_id)
            WHERE module.subject_kind = 'conceptual_spectrum'
              AND module.subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "completeness_assertion_count": scalar(
            f"""
            SELECT COUNT(*) FROM steenrod_action_completeness_assertion completeness
            JOIN steenrod_module module USING(module_id)
            WHERE module.subject_kind = 'conceptual_spectrum'
              AND module.subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "source_derivation_evidence_count": scalar(
            f"""
            SELECT COUNT(DISTINCT item.evidence_id)
            FROM steenrod_module_evidence link
            JOIN steenrod_module module USING(module_id)
            JOIN evidence item USING(evidence_id)
            WHERE module.subject_kind = 'conceptual_spectrum'
              AND module.subject_id IN ({spectrum_placeholders})
              AND item.evidence_kind = 'derivation'
            """,
            CW49_SPECTRUM_IDS,
        ),
        "steenrod_import_evidence_count": scalar(
            f"""
            SELECT COUNT(DISTINCT imported.evidence_id)
            FROM steenrod_module_evidence link
            JOIN steenrod_module module USING(module_id)
            JOIN steenrod_import_evidence imported USING(evidence_id)
            WHERE module.subject_kind = 'conceptual_spectrum'
              AND module.subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "module_evidence_link_count": scalar(
            f"""
            SELECT COUNT(*) FROM steenrod_module_evidence link
            JOIN steenrod_module module USING(module_id)
            WHERE module.subject_kind = 'conceptual_spectrum'
              AND module.subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "assertion_review_count": scalar(
            f"""
            SELECT COUNT(*) FROM assertion_review review
            JOIN assertion claim USING(assertion_id)
            WHERE claim.subject_kind = 'conceptual_spectrum'
              AND claim.subject_id IN ({spectrum_placeholders})
            """,
            CW49_SPECTRUM_IDS,
        ),
        "assertion_editorial_admission_count": scalar(
            """
            SELECT COUNT(*) FROM editorial_event_effect
            WHERE event_id = ? AND effect_kind = 'admit'
            """,
            (event_id,),
        ),
        "profile_module_editorial_admission_count": scalar(
            """
            SELECT COUNT(*) FROM steenrod_module_editorial_effect
            WHERE event_id = ? AND effect_kind = 'admit'
            """,
            (event_id,),
        ),
        "snapshot_record_count": scalar(
            "SELECT COUNT(*) FROM snapshot_record WHERE snapshot_id = ?",
            (snapshot_id,),
        ),
        "current_action_count": scalar(
            "SELECT COUNT(*) FROM current_steenrod_action WHERE snapshot_id = ?",
            (snapshot_id,),
        ),
        "current_completeness_count": scalar(
            """
            SELECT COUNT(*) FROM current_completeness
            WHERE snapshot_id = ? AND subject_kind = 'steenrod_module'
            """,
            (snapshot_id,),
        ),
    }


def _snapshot_record_counts_by_kind(
    connection: sqlite3.Connection, snapshot_id: str
) -> dict[str, int]:
    return {
        kind: int(count)
        for kind, count in connection.execute(
            """
            SELECT record_kind, COUNT(*) FROM snapshot_record
            WHERE snapshot_id = ? GROUP BY record_kind ORDER BY record_kind
            """,
            (snapshot_id,),
        )
    }


def _assert_sparse_terms(
    connection: sqlite3.Connection, assertion_rows: Iterable[_AssertionRow]
) -> None:
    expected = [
        (row.assertion_id, position, target_basis_id)
        for row in assertion_rows
        if row.assertion_kind == "steenrod_action"
        for position, target_basis_id in enumerate(row.target_basis_element_ids)
    ]
    expected.sort()
    actual = list(
        connection.execute(
            """
            SELECT term.assertion_id, term.position, term.target_basis_element_id
            FROM steenrod_action_term term
            JOIN assertion claim USING(assertion_id)
            WHERE claim.subject_kind = 'conceptual_spectrum'
              AND claim.subject_id IN ({})
            ORDER BY term.assertion_id, term.position
            """.format(",".join("?" for _ in CW49_SPECTRUM_IDS)),
            CW49_SPECTRUM_IDS,
        )
    )
    if actual != expected:
        raise SteenrodMaterializationError(
            "materialized sparse action terms differ from the reviewed claims"
        )


def materialize_steenrod_snapshot(
    database_path: Path,
    review_packet_path: Path,
    coverage_report_path: Path,
    acceptance_record_path: Path,
) -> dict[str, Any]:
    """Materialize the exact accepted cw49 candidate and finalize its Snapshot."""

    database_path = Path(database_path)
    packet, _coverage, acceptance, acceptance_sha256, spectra = _validate_inputs(
        Path(review_packet_path),
        Path(coverage_report_path),
        Path(acceptance_record_path),
    )
    evidence_rows, assertion_rows = _make_records(packet, spectra)

    AtlasSchema.migrate(database_path)
    snapshot_id = packet["release_projection"]["spectrum_snapshot"]["snapshot_id"]
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute(
            "SELECT 1 FROM snapshot WHERE snapshot_id = ?", (snapshot_id,)
        ).fetchone():
            raise DuplicateSteenrodMaterializationError(
                f"Steenrod Snapshot already materialized: {snapshot_id}"
            )
        if connection.execute(
            "SELECT 1 FROM conceptual_spectrum WHERE spectrum_id IN ({}) LIMIT 1".format(
                ",".join("?" for _ in CW49_SPECTRUM_IDS)
            ),
            CW49_SPECTRUM_IDS,
        ).fetchone():
            raise SteenrodMaterializationError(
                "target database already contains cw49 spectrum identities"
            )

        _insert_subjects_and_modules(connection, spectra)
        _insert_evidence(connection, evidence_rows)
        _insert_module_evidence(connection, spectra, evidence_rows)
        _insert_assertions(connection, assertion_rows)
        event_id, reviews = _insert_reviews_and_admissions(
            connection,
            assertion_rows,
            spectra,
            packet,
            acceptance,
            acceptance_sha256,
        )
        snapshot_summary = _insert_snapshot_and_projection(
            connection,
            packet,
            acceptance,
            spectra,
            evidence_rows,
            assertion_rows,
            reviews,
            event_id,
        )
        counts = _materialization_counts(connection, snapshot_id, event_id)
        _assert_sparse_terms(connection, assertion_rows)
        snapshot_counts_by_kind = _snapshot_record_counts_by_kind(
            connection, snapshot_id
        )
        expected_counts = {
            "spectrum_count": 49,
            "spectrum_name_count": 49,
            "module_count": 49,
            "basis_element_count": 942,
            "action_assertion_count": 5_780,
            "action_term_count": 2_503,
            "completeness_assertion_count": 48,
            "source_derivation_evidence_count": 49,
            "steenrod_import_evidence_count": 49,
            "module_evidence_link_count": 49,
            "assertion_review_count": 5_828,
            "assertion_editorial_admission_count": 5_828,
            "profile_module_editorial_admission_count": 1,
            "snapshot_record_count": 12_795,
            "current_action_count": 5_780,
            "current_completeness_count": 48,
        }
        for key, expected in expected_counts.items():
            if counts[key] != expected:
                raise SteenrodMaterializationError(
                    f"materialized {key}={counts[key]}, expected {expected}"
                )
        expected_snapshot_counts = {
            "assertion": 5_828,
            "assertion_review": 5_828,
            "conceptual_spectrum": 49,
            "editorial_event": 1,
            "evidence": 49,
            "spectrum_name": 49,
            "steenrod_basis_element": 942,
            "steenrod_module": 49,
        }
        if snapshot_counts_by_kind != expected_snapshot_counts:
            raise SteenrodMaterializationError(
                "Snapshot membership does not close every cw49 record kind"
            )
        foreign_key_errors = list(connection.execute("PRAGMA foreign_key_check"))
        if foreign_key_errors:
            raise SteenrodMaterializationError(
                f"foreign-key check failed: {foreign_key_errors[0]}"
            )
        admitted_tmf = connection.execute(
            """
            SELECT COUNT(*) FROM snapshot_admitted_steenrod_module
            WHERE snapshot_id = ? AND module_id = 'steenrod-module:tmf:cw49-v126.3'
            """,
            (snapshot_id,),
        ).fetchone()[0]
        if admitted_tmf != 1:
            raise SteenrodMaterializationError(
                "finalized Snapshot does not admit the bound tmf profile"
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    logical_summary = {
        "schema_version": MATERIALIZATION_SCHEMA_VERSION,
        "candidate_sha256": packet["candidate_sha256"],
        "acceptance_record_sha256": acceptance_sha256,
        **snapshot_summary,
        "record_counts": counts,
        "snapshot_record_counts_by_kind": snapshot_counts_by_kind,
    }
    return {
        **logical_summary,
        "materialization_sha256": _sha256(logical_summary),
        "logical_database_hash_kind": LOGICAL_DATABASE_HASH_KIND,
        "logical_database_sha256": canonical_logical_database_sha256(database_path),
    }


__all__ = [
    "DuplicateSteenrodMaterializationError",
    "LOGICAL_DATABASE_HASH_KIND",
    "MATERIALIZATION_SCHEMA_VERSION",
    "SteenrodMaterializationError",
    "canonical_logical_database_sha256",
    "materialize_steenrod_snapshot",
]
