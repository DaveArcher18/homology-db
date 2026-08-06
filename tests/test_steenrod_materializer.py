from __future__ import annotations

import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from homology_db.atlas_schema import AtlasSchema
from homology_db.steenrod_snapshot import (
    DuplicateSteenrodMaterializationError,
    LOGICAL_DATABASE_HASH_KIND,
    SteenrodMaterializationError,
    canonical_logical_database_sha256,
    materialize_steenrod_snapshot,
)
from scripts.export_static_atlas import (
    build_spectrum_read_model,
    build_steenrod_review_packet,
    expected_steenrod_acceptance_bindings,
    render_steenrod_coverage_report,
    render_steenrod_review_packet,
    source_commit,
    source_inputs_sha256,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SteenrodMaterializerTests(unittest.TestCase):
    def test_logical_hash_excludes_only_migration_runtime_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.sqlite3"
            second = root / "second.sqlite3"
            AtlasSchema.build(first)
            with closing(sqlite3.connect(first)) as connection:
                first_timestamp = connection.execute(
                    "SELECT MAX(applied_at) FROM schema_migration"
                ).fetchone()[0]
            time.sleep(1.05)
            AtlasSchema.build(second)
            with closing(sqlite3.connect(second)) as connection:
                second_timestamp = connection.execute(
                    "SELECT MAX(applied_at) FROM schema_migration"
                ).fetchone()[0]
            self.assertNotEqual(first_timestamp, second_timestamp)
            self.assertEqual(
                canonical_logical_database_sha256(first),
                canonical_logical_database_sha256(second),
            )

    def _write_test_review(self, root: Path) -> tuple[Path, Path, Path]:
        spectra, source = build_spectrum_read_model()
        atlas = {
            "conceptual_spectra": spectra,
            "snapshot": {
                "spectrum_source": source,
                "source_commit": source_commit(),
                "source_inputs_sha256": source_inputs_sha256(),
                "source_database_hash_kind": "homology-db.sqlite-logical/1",
                "source_database_sha256": "3" * 64,
            },
        }
        packet = build_steenrod_review_packet(atlas, "<test-only-candidate>")
        coverage = render_steenrod_coverage_report(packet)
        acceptance = {
            "schema_version": "homology-db.steenrod-acceptance/1",
            "reviewer": "Dan Isaksen",
            "verdict": "accept",
            "reviewed_at": "2026-08-05T12:34:56Z",
            "evidence": {
                "kind": "written_acceptance",
                "locator": "test-only://synthetic-dan-acceptance",
                "sha256": "4" * 64,
            },
            "editorial_actor": "test-suite",
            "bindings": expected_steenrod_acceptance_bindings(packet, coverage),
        }
        packet_path = root / "review-packet.json"
        coverage_path = root / "coverage.md"
        acceptance_path = root / "acceptance.json"
        packet_path.write_text(
            render_steenrod_review_packet(packet), encoding="utf-8", newline="\n"
        )
        coverage_path.write_text(coverage, encoding="utf-8", newline="\n")
        acceptance_path.write_text(
            json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return packet_path, coverage_path, acceptance_path

    def test_full_materialization_and_transactional_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet_path, coverage_path, acceptance_path = self._write_test_review(root)
            database_path = root / "atlas.sqlite3"
            AtlasSchema.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    "INSERT INTO conceptual_spectrum VALUES (?, ?, ?)",
                    ("unrelated", "Unrelated spectrum", "8" * 64),
                )
                connection.execute(
                    """
                    INSERT INTO spectrum_name VALUES (
                        ?, ?, ?, ?, 'label', NULL, ?
                    )
                    """,
                    (
                        "spectrum-name:unrelated:label",
                        "unrelated",
                        "unrelated spectrum",
                        "Unrelated spectrum",
                        "9" * 64,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO steenrod_module VALUES (
                        'steenrod-module:unrelated:v1', 'conceptual_spectrum',
                        'unrelated', 'profile', 'stable', 2, 1,
                        'cohomological', 0, 'homology-db.steenrod-module/1',
                        'v1', NULL, '{}', ?
                    )
                    """,
                    ("a" * 64,),
                )
                connection.execute(
                    "INSERT INTO evidence VALUES ("
                    "'evidence:unrelated-import', 'derivation', ?)",
                    ("b" * 64,),
                )
                connection.execute(
                    "INSERT INTO derivation_evidence VALUES ("
                    "'evidence:unrelated-import', 'other-normalizer', '1', ?)",
                    ("c" * 64,),
                )
                connection.execute(
                    "INSERT INTO steenrod_import_evidence VALUES ("
                    "'evidence:unrelated-import', 'other:snapshot', "
                    "'other:locator', ?)",
                    ("a" * 64,),
                )
                connection.execute(
                    "INSERT INTO steenrod_module_evidence VALUES ("
                    "'steenrod-module:unrelated:v1', "
                    "'evidence:unrelated-import', 'derives')"
                )
                connection.commit()
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/materialize_steenrod_snapshot.py",
                    "--database",
                    str(database_path),
                    "--review-packet",
                    str(packet_path),
                    "--coverage-report",
                    str(coverage_path),
                    "--acceptance-record",
                    str(acceptance_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            summary = json.loads(completed.stdout)
            self.assertEqual(summary["schema_version"], "homology-db.steenrod-materialization/1")
            self.assertEqual(summary["record_counts"]["spectrum_count"], 49)
            self.assertEqual(summary["record_counts"]["module_count"], 49)
            self.assertEqual(summary["record_counts"]["basis_element_count"], 942)
            self.assertEqual(summary["record_counts"]["action_assertion_count"], 5_780)
            self.assertEqual(summary["record_counts"]["action_term_count"], 2_503)
            self.assertEqual(summary["record_counts"]["completeness_assertion_count"], 48)
            self.assertEqual(summary["record_counts"]["assertion_review_count"], 5_828)
            self.assertEqual(summary["record_counts"]["current_action_count"], 5_780)
            self.assertEqual(summary["record_counts"]["current_completeness_count"], 48)
            self.assertEqual(summary["record_counts"]["snapshot_record_count"], 12_795)
            self.assertEqual(
                summary["snapshot_record_counts_by_kind"],
                {
                    "assertion": 5_828,
                    "assertion_review": 5_828,
                    "conceptual_spectrum": 49,
                    "editorial_event": 1,
                    "evidence": 49,
                    "spectrum_name": 49,
                    "steenrod_basis_element": 942,
                    "steenrod_module": 49,
                },
            )
            self.assertEqual(
                summary["logical_database_hash_kind"], LOGICAL_DATABASE_HASH_KIND
            )
            self.assertRegex(summary["materialization_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(summary["logical_database_sha256"], r"^[0-9a-f]{64}$")

            with closing(sqlite3.connect(database_path)) as connection:
                self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(list(connection.execute("PRAGMA foreign_key_check")), [])
                snapshot = connection.execute(
                    """
                    SELECT finalized_at, canonical_manifest_sha256,
                           current_projection_sha256, record_sha256
                    FROM snapshot WHERE snapshot_id = ?
                    """,
                    (summary["snapshot_id"],),
                ).fetchone()
                self.assertEqual(snapshot[0], "2026-08-05T12:34:56Z")
                self.assertEqual(snapshot[1], summary["canonical_manifest_sha256"])
                self.assertEqual(snapshot[2], summary["current_projection_sha256"])
                self.assertEqual(snapshot[3], summary["snapshot_record_sha256"])
                self.assertEqual(
                    connection.execute(
                        """
                        SELECT COUNT(*) FROM snapshot_admitted_steenrod_module
                        WHERE snapshot_id = ?
                          AND module_id = 'steenrod-module:tmf:cw49-v126.3'
                        """,
                        (summary["snapshot_id"],),
                    ).fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT position FROM steenrod_module_editorial_effect"
                    ).fetchone()[0],
                    5_828,
                )
                self.assertEqual(
                    connection.execute(
                        """
                        SELECT COUNT(*) FROM steenrod_module_evidence link
                        JOIN steenrod_module module USING(module_id)
                        WHERE module.subject_id <> 'unrelated'
                        """
                    ).fetchone()[0],
                    49,
                )
                self.assertEqual(
                    connection.execute(
                        """
                        SELECT imported.source_snapshot, imported.source_locator,
                               imported.normalized_module_sha256,
                               module.record_sha256
                        FROM steenrod_module_evidence link
                        JOIN steenrod_module module USING(module_id)
                        JOIN steenrod_import_evidence imported USING(evidence_id)
                        WHERE module.subject_id = 'tmf'
                        """
                    ).fetchone(),
                    (
                        "zenodo:14875701:v126.3.cw49",
                        "sseqcpp:23d12c973db2b294a6c00c15bd106e70b0af3fa6:Adams/complexes.cpp#tmf",
                        json.loads(acceptance_path.read_text(encoding="utf-8"))[
                            "bindings"
                        ]["tmf_profile_module_content_sha256"],
                        json.loads(acceptance_path.read_text(encoding="utf-8"))[
                            "bindings"
                        ]["tmf_profile_module_content_sha256"],
                    ),
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM conceptual_spectrum WHERE spectrum_id = 'unrelated'"
                    ).fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute(
                        """
                        SELECT COUNT(*) FROM snapshot_record
                        WHERE snapshot_id = ? AND record_id = 'unrelated'
                        """,
                        (summary["snapshot_id"],),
                    ).fetchone()[0],
                    0,
                )
                before = {
                    table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    for table in (
                        "conceptual_spectrum",
                        "assertion",
                        "assertion_review",
                        "editorial_event_effect",
                        "snapshot",
                        "snapshot_record",
                        "current_steenrod_action",
                        "current_completeness",
                    )
                }

            with self.assertRaises(DuplicateSteenrodMaterializationError):
                materialize_steenrod_snapshot(
                    database_path, packet_path, coverage_path, acceptance_path
                )

            bad_acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            bad_acceptance = copy.deepcopy(bad_acceptance)
            bad_acceptance["bindings"]["candidate_sha256"] = "0" * 64
            bad_path = root / "bad-acceptance.json"
            bad_path.write_text(
                json.dumps(bad_acceptance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaises(SteenrodMaterializationError):
                materialize_steenrod_snapshot(
                    database_path, packet_path, coverage_path, bad_path
                )

            with closing(sqlite3.connect(database_path)) as connection:
                after = {
                    table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    for table in before
                }
            self.assertEqual(after, before)

            rollback_database = root / "rollback.sqlite3"
            with patch(
                "homology_db.steenrod_snapshot._insert_snapshot_and_projection",
                side_effect=RuntimeError("test-only late failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "test-only late failure"):
                    materialize_steenrod_snapshot(
                        rollback_database,
                        packet_path,
                        coverage_path,
                        acceptance_path,
                    )
            with closing(sqlite3.connect(rollback_database)) as connection:
                self.assertEqual(
                    connection.execute(
                        "SELECT MAX(version) FROM schema_migration"
                    ).fetchone()[0],
                    5,
                )
                for table in (
                    "conceptual_spectrum",
                    "spectrum_name",
                    "steenrod_module",
                    "steenrod_basis_element",
                    "evidence",
                    "assertion",
                    "assertion_review",
                    "editorial_event",
                    "snapshot",
                    "snapshot_record",
                    "current_steenrod_action",
                    "current_completeness",
                ):
                    self.assertEqual(
                        connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0],
                        0,
                        table,
                    )


if __name__ == "__main__":
    unittest.main()
