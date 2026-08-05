from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock

from homology_db import atlas_schema
from homology_db.atlas_schema import AtlasSchema


class SteenrodSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.database_path = Path(self.temporary_directory.name) / "atlas.sqlite3"
        self.schema_version = AtlasSchema.build(self.database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.addCleanup(self.connection.close)
        self.connection.execute("PRAGMA foreign_keys = ON")

    def insert_spectrum(
        self,
        spectrum_id: str = "spectrum:S0",
        permanent_label: str = "Sphere spectrum",
    ) -> None:
        self.connection.execute(
            "INSERT INTO conceptual_spectrum(spectrum_id, permanent_label, record_sha256) "
            "VALUES (?, ?, ?)",
            (spectrum_id, permanent_label, "1" * 64),
        )

    def insert_finite_module(
        self,
        module_id: str = "steenrod-module:S0:v1",
        *,
        subject_kind: str = "conceptual_spectrum",
        subject_id: str = "spectrum:S0",
        module_category: str = "stable",
    ) -> None:
        self.connection.execute(
            "INSERT INTO steenrod_module("
            "module_id, subject_kind, subject_id, module_kind, module_category, "
            "coefficient_prime, reduced, grading_convention, suspension_shift, "
            "format_version, module_version, basis_version, profile_json, record_sha256"
            ") VALUES (?, ?, ?, 'finite_basis', ?, 2, 1, 'cohomological/1', 0, "
            "'homology-db.steenrod-module/1', 'v1', 'basis-v1', NULL, ?)",
            (module_id, subject_kind, subject_id, module_category, "2" * 64),
        )

    def insert_basis_element(
        self,
        basis_element_id: str,
        degree: int,
        position: int,
        *,
        module_id: str = "steenrod-module:S0:v1",
        degree_ordinal: int = 0,
    ) -> None:
        self.connection.execute(
            "INSERT INTO steenrod_basis_element("
            "basis_element_id, module_id, basis_key, display_name, degree, position, "
            "degree_ordinal, record_sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                basis_element_id,
                module_id,
                basis_element_id.rsplit(":", 1)[-1],
                basis_element_id.rsplit(":", 1)[-1],
                degree,
                position,
                degree_ordinal,
                "6" * 64,
            ),
        )

    def insert_action(
        self,
        assertion_id: str,
        source_basis_element_id: str,
        operation_degree: int,
        *,
        knowledge_state: str = "exact",
        module_id: str = "steenrod-module:S0:v1",
        subject_kind: str = "conceptual_spectrum",
        subject_id: str = "spectrum:S0",
    ) -> None:
        self.connection.execute(
            "INSERT INTO assertion("
            "assertion_id, assertion_kind, subject_kind, subject_id, slot_key, "
            "knowledge_state, claim_fingerprint, payload_sha256, record_sha256"
            ") VALUES (?, 'steenrod_action', ?, ?, ?, ?, ?, ?, ?)",
            (
                assertion_id,
                subject_kind,
                subject_id,
                f"{module_id}|{source_basis_element_id}|Sq{operation_degree}",
                knowledge_state,
                f"fingerprint:{assertion_id}",
                "7" * 64,
                "8" * 64,
            ),
        )
        self.connection.execute(
            "INSERT INTO steenrod_action_assertion("
            "assertion_id, module_id, source_basis_element_id, operation_degree"
            ") VALUES (?, ?, ?, ?)",
            (assertion_id, module_id, source_basis_element_id, operation_degree),
        )

    def insert_snapshot(self, snapshot_id: str = "snapshot:steenrod") -> None:
        self.connection.execute(
            "INSERT INTO snapshot("
            "snapshot_id, schema_version, selection_policy_id, selection_policy_sha256, "
            "canonical_manifest_sha256, current_projection_sha256, finalized_at, record_sha256"
            ") VALUES (?, ?, 'policy:test', ?, NULL, NULL, NULL, NULL)",
            (snapshot_id, self.schema_version, "9" * 64),
        )

    def insert_action_grounding(
        self,
        assertion_id: str,
        snapshot_id: str = "snapshot:steenrod",
        suffix: str = "sq",
        *,
        include_snapshot_records: bool = True,
    ) -> None:
        self.connection.execute(
            "INSERT INTO evidence VALUES (?, 'derivation', ?)",
            (f"evidence:{suffix}", "a" * 64),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES (?, "
            "'imported-generator-action', '1', ?)",
            (f"evidence:{suffix}", "b" * 64),
        )
        self.connection.execute(
            "INSERT INTO assertion_evidence VALUES (?, ?, 'derives')",
            (assertion_id, f"evidence:{suffix}"),
        )
        self.connection.execute(
            "INSERT INTO assertion_review VALUES ("
            "?, ?, 'reviewer', 'accept', "
            "'2026-08-05T00:00:00Z', 'checked', ?)",
            (f"assertion-review:{suffix}", assertion_id, "c" * 64),
        )
        self.connection.execute(
            "INSERT INTO editorial_event VALUES ("
            "?, 'admit', 'editor', 'reviewed', "
            "'2026-08-05T00:01:00Z', 0, ?)",
            (f"event:admit:{suffix}", "d" * 64),
        )
        self.connection.execute(
            "INSERT INTO editorial_event_effect VALUES (?, ?, 'admit', 0)",
            (f"event:admit:{suffix}", assertion_id),
        )
        if include_snapshot_records:
            self.insert_grounding_snapshot_records(snapshot_id, suffix)

    def insert_grounding_snapshot_records(
        self, snapshot_id: str, suffix: str = "sq"
    ) -> None:
        for record_kind, record_id, record_hash in (
            ("evidence", f"evidence:{suffix}", "a" * 64),
            ("assertion_review", f"assertion-review:{suffix}", "c" * 64),
            ("editorial_event", f"event:admit:{suffix}", "d" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                (snapshot_id, record_kind, record_id, record_hash),
            )

    def test_unstable_generator_actions_above_source_degree_must_vanish(self) -> None:
        self.connection.execute(
            "INSERT INTO conceptual_space VALUES ('space:X', 'Space X', ?)",
            ("1" * 64,),
        )
        self.insert_finite_module(
            "steenrod-module:X:v1",
            subject_kind="conceptual_space",
            subject_id="space:X",
            module_category="unstable",
        )
        self.insert_basis_element(
            "basis:X:x0", 0, 0, module_id="steenrod-module:X:v1"
        )
        self.insert_basis_element(
            "basis:X:x1", 1, 1, module_id="steenrod-module:X:v1"
        )
        self.insert_action(
            "assertion:X:sq1",
            "basis:X:x0",
            1,
            module_id="steenrod-module:X:v1",
            subject_kind="conceptual_space",
            subject_id="space:X",
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "unstable_steenrod_action_must_vanish"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_term VALUES ("
                "'assertion:X:sq1', 'steenrod-module:X:v1', 'basis:X:x1', 0)"
            )

    def test_v5_adds_stable_spectrum_and_steenrod_projection_tables(self) -> None:
        self.assertEqual(self.schema_version, "homology-db.atlas-schema/5")
        tables = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        self.assertTrue(
            {
                "conceptual_spectrum",
                "spectrum_name",
                "steenrod_module",
                "steenrod_module_editorial_effect",
                "steenrod_import_evidence",
                "steenrod_module_evidence",
                "steenrod_basis_element",
                "steenrod_action_assertion",
                "steenrod_action_term",
                "steenrod_action_completeness_assertion",
                "current_steenrod_action",
            }
            <= tables
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT version FROM schema_migration ORDER BY version"
            ).fetchall(),
            [(1,), (2,), (3,), (4,), (5,)],
        )

    def test_populated_v4_upgrades_without_changing_prior_migration_identity(self) -> None:
        upgrade_path = Path(self.temporary_directory.name) / "upgrade.sqlite3"
        migration_files = atlas_schema._migration_files()
        with mock.patch.object(
            atlas_schema, "_migration_files", return_value=migration_files[:4]
        ):
            self.assertEqual(
                AtlasSchema.migrate(upgrade_path), "homology-db.atlas-schema/4"
            )
        with closing(sqlite3.connect(upgrade_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "INSERT INTO conceptual_space VALUES "
                "('space:legacy', 'Legacy space', ?)",
                ("a" * 64,),
            )
            connection.execute(
                "INSERT INTO assertion VALUES ("
                "'assertion:legacy', 'homology', 'conceptual_space', 'space:legacy', "
                "'slot:legacy', 'unknown', 'fingerprint:legacy', ?, ?)",
                ("b" * 64, "c" * 64),
            )
            prior_hashes = connection.execute(
                "SELECT version, sha256 FROM schema_migration WHERE version <= 4 "
                "ORDER BY version"
            ).fetchall()
            connection.commit()

        self.assertEqual(AtlasSchema.migrate(upgrade_path), "homology-db.atlas-schema/5")
        self.assertEqual(AtlasSchema.migrate(upgrade_path), "homology-db.atlas-schema/5")
        with closing(sqlite3.connect(upgrade_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            self.assertEqual(
                connection.execute(
                    "SELECT version, sha256 FROM schema_migration WHERE version <= 4 "
                    "ORDER BY version"
                ).fetchall(),
                prior_hashes,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT subject_kind, subject_id FROM assertion "
                    "WHERE assertion_id = 'assertion:legacy'"
                ).fetchone(),
                ("conceptual_space", "space:legacy"),
            )
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_spectrum_identity_is_typed_and_module_subjects_must_resolve(self) -> None:
        self.connection.execute(
            "INSERT INTO conceptual_space(space_id, permanent_label, record_sha256) "
            "VALUES ('subject:sphere', 'Sphere', ?)",
            ("3" * 64,),
        )
        self.insert_spectrum("subject:sphere", "Sphere")

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_module_subject_not_found"
        ):
            self.insert_finite_module(subject_id="spectrum:missing")

        self.insert_finite_module(subject_id="subject:sphere")
        self.connection.execute(
            "INSERT INTO assertion("
            "assertion_id, assertion_kind, subject_kind, subject_id, slot_key, "
            "knowledge_state, claim_fingerprint, payload_sha256, record_sha256"
            ") VALUES ('assertion:sq1', 'steenrod_action', 'conceptual_spectrum', "
            "'subject:sphere', 'sq1:x0', 'exact', 'fingerprint:sq1', ?, ?)",
            ("4" * 64, "5" * 64),
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT subject_kind, subject_id FROM assertion WHERE assertion_id = ?",
                ("assertion:sq1",),
            ).fetchone(),
            ("conceptual_spectrum", "subject:sphere"),
        )

    def test_exact_empty_action_is_zero_but_unknown_and_uncovered_slots_are_not(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_basis_element("basis:x1", 1, 1)
        self.insert_basis_element("basis:x2", 2, 2)
        self.insert_action("assertion:zero", "basis:x0", 1)
        self.insert_action(
            "assertion:unknown", "basis:x1", 1, knowledge_state="unknown"
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_terms_require_exact_assertion"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_term("
                "assertion_id, module_id, target_basis_element_id, position"
                ") VALUES ('assertion:unknown', 'steenrod-module:S0:v1', 'basis:x2', 0)"
            )

        rows = self.connection.execute(
            "SELECT action.source_basis_element_id, claim.knowledge_state, "
            "COUNT(term.target_basis_element_id) "
            "FROM steenrod_action_assertion action "
            "JOIN assertion claim USING(assertion_id) "
            "LEFT JOIN steenrod_action_term term USING(assertion_id) "
            "GROUP BY action.assertion_id ORDER BY action.assertion_id"
        ).fetchall()
        self.assertEqual(
            rows,
            [("basis:x1", "unknown", 0), ("basis:x0", "exact", 0)],
        )
        self.assertIsNone(
            self.connection.execute(
                "SELECT assertion_id FROM steenrod_action_assertion "
                "WHERE module_id = 'steenrod-module:S0:v1' "
                "AND source_basis_element_id = 'basis:x2' AND operation_degree = 1"
            ).fetchone()
        )

    def test_action_assertion_resolves_its_typed_spectrum_and_source_basis(self) -> None:
        self.insert_spectrum()
        self.insert_spectrum("spectrum:other", "Other spectrum")
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.connection.execute(
            "INSERT INTO assertion("
            "assertion_id, assertion_kind, subject_kind, subject_id, slot_key, "
            "knowledge_state, claim_fingerprint, payload_sha256, record_sha256"
            ") VALUES ('assertion:mismatch', 'steenrod_action', "
            "'conceptual_spectrum', 'spectrum:other', 'sq1:x0', 'exact', "
            "'fingerprint:mismatch', ?, ?)",
            ("9" * 64, "a" * 64),
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_assertion_subject_mismatch"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_assertion("
                "assertion_id, module_id, source_basis_element_id, operation_degree"
                ") VALUES ('assertion:mismatch', 'steenrod-module:S0:v1', 'basis:x0', 1)"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO steenrod_action_assertion("
                "assertion_id, module_id, source_basis_element_id, operation_degree"
                ") VALUES ('assertion:mismatch', 'steenrod-module:S0:v1', 'basis:missing', 1)"
            )

    def test_action_terms_enforce_degree_same_module_and_mod2_uniqueness(self) -> None:
        self.insert_spectrum()
        self.insert_spectrum("spectrum:other", "Other spectrum")
        self.insert_finite_module()
        self.insert_finite_module(
            "steenrod-module:other:v1", subject_id="spectrum:other"
        )
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_basis_element("basis:x1", 1, 1)
        self.insert_basis_element("basis:x1b", 1, 2, degree_ordinal=1)
        self.insert_basis_element("basis:x2", 2, 3)
        self.insert_basis_element(
            "basis:y1", 1, 0, module_id="steenrod-module:other:v1"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_basis_element("basis:duplicate-position", 3, 1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_basis_element("basis:duplicate-ordinal", 1, 4)

        self.insert_action("assertion:sq1", "basis:x0", 1)
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_target_degree_mismatch"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_term VALUES "
                "('assertion:sq1', 'steenrod-module:S0:v1', 'basis:x2', 0)"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO steenrod_action_term VALUES "
                "('assertion:sq1', 'steenrod-module:S0:v1', 'basis:y1', 0)"
            )

        self.connection.execute(
            "INSERT INTO steenrod_action_term VALUES "
            "('assertion:sq1', 'steenrod-module:S0:v1', 'basis:x1', 0)"
        )
        self.connection.execute(
            "INSERT INTO steenrod_action_term VALUES "
            "('assertion:sq1', 'steenrod-module:S0:v1', 'basis:x1b', 1)"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO steenrod_action_term VALUES "
                "('assertion:sq1', 'steenrod-module:S0:v1', 'basis:x1', 2)"
            )

    def test_profile_modules_do_not_acquire_a_finite_basis(self) -> None:
        self.insert_spectrum("spectrum:tmf", "tmf")
        self.connection.execute(
            "INSERT INTO steenrod_module("
            "module_id, subject_kind, subject_id, module_kind, module_category, "
            "coefficient_prime, reduced, grading_convention, suspension_shift, "
            "format_version, module_version, basis_version, profile_json, record_sha256"
            ") VALUES ('steenrod-module:tmf:v1', 'conceptual_spectrum', 'spectrum:tmf', "
            "'profile', 'stable', 2, 1, 'cohomological/1', 0, "
            "'homology-db.steenrod-module/1', 'v1', NULL, ?, ?)",
            ('{"milnor_profile":[3,2,1]}', "b" * 64),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_basis_requires_finite_module"
        ):
            self.insert_basis_element(
                "basis:tmf:x0", 0, 0, module_id="steenrod-module:tmf:v1"
            )

        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO steenrod_module("
                "module_id, subject_kind, subject_id, module_kind, module_category, "
                "coefficient_prime, reduced, grading_convention, suspension_shift, "
                "format_version, module_version, basis_version, profile_json, "
                "record_sha256) VALUES ("
                "'steenrod-module:tmf:bad', 'conceptual_spectrum', 'spectrum:tmf', "
                "'profile', 'stable', 2, 1, 'cohomological/1', 0, "
                "'homology-db.steenrod-module/1', 'bad', NULL, 'not json', ?) ",
                ("c" * 64,),
            )

    def test_basis_positions_follow_degree_and_contiguous_ordinal_order(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x1", 1, 0)

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_basis_not_canonically_ordered"
        ):
            self.insert_basis_element("basis:x0", 0, 1)
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_basis_not_canonically_ordered"
        ):
            self.insert_basis_element("basis:x1-gap", 1, 2, degree_ordinal=2)
        self.insert_basis_element("basis:x1-next", 1, 1, degree_ordinal=1)

    def test_action_completeness_is_an_exact_separate_coverage_claim(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:complete', 'steenrod_action_completeness', "
            "'conceptual_spectrum', 'spectrum:S0', 'complete:S0', 'exact', "
            "'fingerprint:complete', ?, ?)",
            ("c" * 64, "d" * 64),
        )
        self.connection.execute(
            "INSERT INTO completeness_assertion VALUES ("
            "'assertion:complete', "
            "'{\"basis_positions\":[0,0],\"maximum_operation_degree\":1}', "
            "'steenrod_action_coverage')"
        )
        self.connection.execute(
            "INSERT INTO steenrod_action_completeness_assertion VALUES ("
            "'assertion:complete', 'steenrod-module:S0:v1', 0, 0, 1)"
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT COUNT(*) FROM steenrod_action_assertion"
            ).fetchone(),
            (0,),
        )

        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:incomplete', 'steenrod_action_completeness', "
            "'conceptual_spectrum', 'spectrum:S0', 'complete:S0:unknown', 'unknown', "
            "'fingerprint:incomplete', ?, ?)",
            ("e" * 64, "f" * 64),
        )
        self.connection.execute(
            "INSERT INTO completeness_assertion VALUES ("
            "'assertion:incomplete', "
            "'{\"basis_positions\":[0,0],\"maximum_operation_degree\":1}', "
            "'steenrod_action_coverage')"
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_completeness_requires_exact_assertion"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_completeness_assertion VALUES ("
                "'assertion:incomplete', 'steenrod-module:S0:v1', 0, 0, 1)"
            )

        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:mismatched-region', 'steenrod_action_completeness', "
            "'conceptual_spectrum', 'spectrum:S0', 'complete:S0:mismatch', "
            "'exact', 'fingerprint:mismatched-region', ?, ?)",
            ("1" * 64, "2" * 64),
        )
        self.connection.execute(
            "INSERT INTO completeness_assertion VALUES ("
            "'assertion:mismatched-region', "
            "'{\"basis_positions\":[0,0],\"maximum_operation_degree\":2}', "
            "'steenrod_action_coverage')"
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_completeness_requires_exact_assertion"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_completeness_assertion VALUES ("
                "'assertion:mismatched-region', 'steenrod-module:S0:v1', 0, 0, 1)"
            )

    def test_current_steenrod_completeness_requires_reviewed_snapshot_closure(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:complete', 'steenrod_action_completeness', "
            "'conceptual_spectrum', 'spectrum:S0', 'complete:S0', 'exact', "
            "'fingerprint:complete', ?, ?)",
            ("c" * 64, "d" * 64),
        )
        self.connection.execute(
            "INSERT INTO completeness_assertion VALUES ("
            "'assertion:complete', "
            "'{\"basis_positions\":[0,0],\"maximum_operation_degree\":1}', "
            "'steenrod_action_coverage')"
        )
        self.connection.execute(
            "INSERT INTO steenrod_action_completeness_assertion VALUES ("
            "'assertion:complete', 'steenrod-module:S0:v1', 0, 0, 1)"
        )
        self.insert_snapshot("snapshot:complete")
        self.insert_action_grounding(
            "assertion:complete",
            "snapshot:complete",
            include_snapshot_records=False,
        )
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
            ("assertion", "assertion:complete", "d" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:complete", record_kind, record_id, record_hash),
            )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "current_steenrod_completeness_not_grounded_in_snapshot",
        ):
            self.connection.execute(
                "INSERT INTO current_completeness VALUES ("
                "'snapshot:complete', 'steenrod_module', 'steenrod-module:S0:v1', "
                "'assertion:complete', ?)",
                ("e" * 64,),
            )
        self.insert_grounding_snapshot_records("snapshot:complete")
        self.connection.execute(
            "INSERT INTO current_completeness VALUES ("
            "'snapshot:complete', 'steenrod_module', 'steenrod-module:S0:v1', "
            "'assertion:complete', ?)",
            ("e" * 64,),
        )

    def test_current_completeness_requires_every_in_support_exact_action(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_basis_element("basis:x1", 1, 1)
        self.insert_action("assertion:zero", "basis:x0", 1)
        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:complete-actions', 'steenrod_action_completeness', "
            "'conceptual_spectrum', 'spectrum:S0', 'complete:S0:actions', "
            "'exact', 'fingerprint:complete-actions', ?, ?)",
            ("c" * 64, "d" * 64),
        )
        self.connection.execute(
            "INSERT INTO completeness_assertion VALUES ("
            "'assertion:complete-actions', "
            "'{\"basis_positions\":[0,1],\"maximum_operation_degree\":1}', "
            "'steenrod_action_coverage')"
        )
        self.connection.execute(
            "INSERT INTO steenrod_action_completeness_assertion VALUES ("
            "'assertion:complete-actions', 'steenrod-module:S0:v1', 0, 1, 1)"
        )
        self.insert_snapshot("snapshot:complete-actions")
        self.insert_action_grounding(
            "assertion:zero",
            "snapshot:complete-actions",
            suffix="complete-action-zero",
            include_snapshot_records=False,
        )
        self.insert_action_grounding(
            "assertion:complete-actions",
            "snapshot:complete-actions",
            suffix="complete-action-coverage",
            include_snapshot_records=False,
        )
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
            ("steenrod_basis_element", "basis:x1", "6" * 64),
            ("assertion", "assertion:zero", "8" * 64),
            ("assertion", "assertion:complete-actions", "d" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:complete-actions", record_kind, record_id, record_hash),
            )
        self.insert_grounding_snapshot_records(
            "snapshot:complete-actions", "complete-action-zero"
        )
        self.insert_grounding_snapshot_records(
            "snapshot:complete-actions", "complete-action-coverage"
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "current_steenrod_completeness_not_grounded_in_snapshot",
        ):
            self.connection.execute(
                "INSERT INTO current_completeness VALUES ("
                "'snapshot:complete-actions', 'steenrod_module', "
                "'steenrod-module:S0:v1', 'assertion:complete-actions', ?)",
                ("e" * 64,),
            )
        slot = "steenrod-module:S0:v1|basis:x0|Sq1"
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:complete-actions', ?, 'steenrod-module:S0:v1', "
            "'basis:x0', 1, 'selected', 'assertion:zero', NULL, ?)",
            (slot, "f" * 64),
        )
        self.connection.execute(
            "INSERT INTO current_completeness VALUES ("
            "'snapshot:complete-actions', 'steenrod_module', "
            "'steenrod-module:S0:v1', 'assertion:complete-actions', ?)",
            ("e" * 64,),
        )

    def test_current_projection_requires_reviewed_snapshot_closure_and_preserves_absence(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_basis_element("basis:x1", 1, 1)
        self.insert_action("assertion:zero", "basis:x0", 1)
        self.insert_action(
            "assertion:unknown", "basis:x1", 1, knowledge_state="unknown"
        )
        self.insert_snapshot()
        self.insert_action_grounding(
            "assertion:zero", include_snapshot_records=False
        )
        self.insert_action_grounding(
            "assertion:unknown", suffix="unknown", include_snapshot_records=False
        )
        action_slot = "steenrod-module:S0:v1|basis:x0|Sq1"
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
            ("steenrod_basis_element", "basis:x1", "6" * 64),
            ("assertion", "assertion:zero", "8" * 64),
            ("assertion", "assertion:unknown", "8" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:steenrod", record_kind, record_id, record_hash),
            )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "selected_steenrod_action_not_grounded_in_snapshot",
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:steenrod', ?, 'steenrod-module:S0:v1', 'basis:x0', 1, "
                "'selected', 'assertion:zero', NULL, ?)",
                (action_slot, "e" * 64),
            )

        self.insert_grounding_snapshot_records("snapshot:steenrod")
        self.insert_grounding_snapshot_records("snapshot:steenrod", "unknown")
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:steenrod', ?, 'steenrod-module:S0:v1', 'basis:x0', 1, "
            "'selected', 'assertion:zero', NULL, ?)",
            (action_slot, "e" * 64),
        )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:steenrod', ?, 'steenrod-module:S0:v1', 'basis:x1', 1, "
            "'selected', 'assertion:unknown', NULL, ?)",
            ("steenrod-module:S0:v1|basis:x1|Sq1", "e" * 64),
        )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:steenrod', ?, 'steenrod-module:S0:v1', 'basis:x0', 2, "
            "'absent', NULL, NULL, ?)",
            ("steenrod-module:S0:v1|basis:x0|Sq2", "f" * 64),
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT current.projection_outcome, current.selected_assertion_id, "
                "claim.knowledge_state FROM current_steenrod_action current "
                "LEFT JOIN assertion claim "
                "ON claim.assertion_id = current.selected_assertion_id "
                "ORDER BY current.slot_key"
            ).fetchall(),
            [
                ("selected", "assertion:zero", "exact"),
                ("absent", None, None),
                ("selected", "assertion:unknown", "unknown"),
            ],
        )

        self.connection.execute(
            "UPDATE snapshot SET canonical_manifest_sha256 = ?, "
            "current_projection_sha256 = ?, finalized_at = ?, record_sha256 = ? "
            "WHERE snapshot_id = 'snapshot:steenrod'",
            ("1" * 64, "2" * 64, "2026-08-05T00:02:00Z", "3" * 64),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "snapshot_finalized"):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:steenrod', 'later', 'steenrod-module:S0:v1', 'basis:x0', "
                "4, 'absent', NULL, NULL, ?)",
                ("4" * 64,),
            )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "immutable_current_steenrod_action"
        ):
            self.connection.execute(
                "UPDATE current_steenrod_action SET projection_sha256 = ? "
                "WHERE snapshot_id = 'snapshot:steenrod' AND slot_key = ?",
                ("5" * 64, action_slot),
            )

    def test_action_terms_and_basis_are_sealed_before_review_or_snapshot_use(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_basis_element("basis:x1", 1, 1)
        self.insert_action("assertion:zero", "basis:x0", 1)
        self.connection.execute(
            "INSERT INTO assertion_review VALUES ("
            "'assertion-review:zero', 'assertion:zero', 'reviewer', 'accept', "
            "'2026-08-05T00:00:00Z', 'checked', ?)",
            ("a" * 64,),
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_action_assertion"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_term VALUES ("
                "'assertion:zero', 'steenrod-module:S0:v1', 'basis:x1', 0)"
            )

        self.insert_snapshot("snapshot:sealed-module")
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:sealed-module', 'steenrod_module', "
            "'steenrod-module:S0:v1', ?)",
            ("2" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_module_basis"
        ):
            self.insert_basis_element("basis:x2", 2, 2)

    def test_steenrod_subtypes_cannot_be_attached_after_parent_review(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:late-action', 'steenrod_action', 'conceptual_spectrum', "
            "'spectrum:S0', 'steenrod-module:S0:v1|basis:x0|Sq1', 'exact', "
            "'fingerprint:late-action', ?, ?)",
            ("1" * 64, "2" * 64),
        )
        self.connection.execute(
            "INSERT INTO assertion_review VALUES ("
            "'review:late-action', 'assertion:late-action', 'reviewer', 'accept', "
            "'2026-08-05T00:00:00Z', 'checked', ?)",
            ("3" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_action_assertion"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_assertion VALUES ("
                "'assertion:late-action', 'steenrod-module:S0:v1', 'basis:x0', 1)"
            )

        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:late-completeness', 'steenrod_action_completeness', "
            "'conceptual_spectrum', 'spectrum:S0', 'complete:S0', 'exact', "
            "'fingerprint:late-completeness', ?, ?)",
            ("4" * 64, "5" * 64),
        )
        self.connection.execute(
            "INSERT INTO completeness_assertion VALUES ("
            "'assertion:late-completeness', "
            "'{\"basis_positions\":[0,0],\"maximum_operation_degree\":1}', "
            "'steenrod_action_coverage')"
        )
        self.connection.execute(
            "INSERT INTO assertion_review VALUES ("
            "'review:late-completeness', 'assertion:late-completeness', "
            "'reviewer', 'accept', '2026-08-05T00:00:00Z', 'checked', ?)",
            ("6" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_completeness_assertion"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_completeness_assertion VALUES ("
                "'assertion:late-completeness', 'steenrod-module:S0:v1', 0, 0, 1)"
            )

    def test_steenrod_action_subtype_requires_the_canonical_parent_slot(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:wrong-slot', 'steenrod_action', 'conceptual_spectrum', "
            "'spectrum:S0', 'wrong-slot', 'exact', 'fingerprint:wrong-slot', ?, ?)",
            ("1" * 64, "2" * 64),
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_assertion_subject_mismatch"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_assertion VALUES ("
                "'assertion:wrong-slot', 'steenrod-module:S0:v1', 'basis:x0', 1)"
            )

    def test_sparse_action_terms_use_contiguous_canonical_basis_order(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_basis_element("basis:x1a", 1, 1, degree_ordinal=0)
        self.insert_basis_element("basis:x1b", 1, 2, degree_ordinal=1)
        self.insert_action("assertion:sum-bad", "basis:x0", 1)

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_terms_not_canonical"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_term VALUES ("
                "'assertion:sum-bad', 'steenrod-module:S0:v1', 'basis:x1a', 1)"
            )
        self.connection.execute(
            "INSERT INTO steenrod_action_term VALUES ("
            "'assertion:sum-bad', 'steenrod-module:S0:v1', 'basis:x1b', 0)"
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_terms_not_canonical"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_action_term VALUES ("
                "'assertion:sum-bad', 'steenrod-module:S0:v1', 'basis:x1a', 1)"
            )

        self.insert_action("assertion:sum-good", "basis:x0", 1)
        self.connection.execute(
            "INSERT INTO steenrod_action_term VALUES ("
            "'assertion:sum-good', 'steenrod-module:S0:v1', 'basis:x1a', 0)"
        )
        self.connection.execute(
            "INSERT INTO steenrod_action_term VALUES ("
            "'assertion:sum-good', 'steenrod-module:S0:v1', 'basis:x1b', 1)"
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT target_basis_element_id FROM steenrod_action_term "
                "WHERE assertion_id = 'assertion:sum-good' ORDER BY position"
            ).fetchall(),
            [("basis:x1a",), ("basis:x1b",)],
        )

    def test_every_current_action_outcome_requires_snapshot_slot_closure(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_snapshot("snapshot:absent")
        slot = "steenrod-module:S0:v1|basis:x0|Sq1"

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_slot_not_grounded_in_snapshot"
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:absent', ?, 'steenrod-module:S0:v1', 'basis:x0', 1, "
                "'absent', NULL, NULL, ?)",
                (slot, "e" * 64),
            )

        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:absent", record_kind, record_id, record_hash),
            )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:absent', ?, 'steenrod-module:S0:v1', 'basis:x0', 1, "
            "'absent', NULL, NULL, ?)",
            (slot, "e" * 64),
        )

        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:late-member', 'derivation', ?)",
            ("a" * 64,),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:late-member', 'rule', '1', ?)",
            ("b" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "snapshot_steenrod_projection_started"
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES ("
                "'snapshot:absent', 'evidence', 'evidence:late-member', ?)",
                ("a" * 64,),
            )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_slot_not_grounded_in_snapshot"
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:absent', 'wrong-slot', 'steenrod-module:S0:v1', "
                "'basis:x0', 2, 'absent', NULL, NULL, ?)",
                ("f" * 64,),
            )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_conflict_projection_not_supported"
        ):
            self.connection.execute(
                "INSERT INTO editorial_event VALUES ("
                "'event:conflict', 'declare_conflict', 'editor', 'test', "
                "'2026-08-05T00:00:00Z', 0, ?)",
                ("7" * 64,),
            )
            self.connection.execute(
                "INSERT INTO conflict_set VALUES ("
                "'conflict:test', ?, 'event:conflict', ?)",
                ("steenrod-module:S0:v1|basis:x0|Sq2", "8" * 64),
            )
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:absent', 'steenrod-module:S0:v1|basis:x0|Sq2', "
                "'steenrod-module:S0:v1', 'basis:x0', 2, 'conflicting', NULL, "
                "'conflict:test', ?)",
                ("9" * 64,),
            )

    def test_absent_and_unresolved_outcomes_match_snapshot_candidates(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_snapshot("snapshot:candidates")
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:candidates", record_kind, record_id, record_hash),
            )

        self.insert_action(
            "assertion:candidate-sq1", "basis:x0", 1, knowledge_state="unknown"
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:candidates', 'assertion', 'assertion:candidate-sq1', ?)",
            ("8" * 64,),
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_candidate_not_found"
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:candidates', 'steenrod-module:S0:v1|basis:x0|Sq2', "
                "'steenrod-module:S0:v1', 'basis:x0', 2, "
                "'unresolved_selection', NULL, NULL, ?)",
                ("b" * 64,),
            )

        self.insert_action(
            "assertion:candidate-sq2", "basis:x0", 2, knowledge_state="unknown"
        )
        self.insert_action_grounding(
            "assertion:candidate-sq2", "snapshot:candidates", suffix="candidate-sq2-a"
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:candidates', 'assertion', 'assertion:candidate-sq2', ?)",
            ("8" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "steenrod_action_candidate_not_found"
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:candidates', 'steenrod-module:S0:v1|basis:x0|Sq2', "
                "'steenrod-module:S0:v1', 'basis:x0', 2, "
                "'unresolved_selection', NULL, NULL, ?)",
                ("c" * 64,),
            )

        self.insert_action(
            "assertion:candidate-sq2-b", "basis:x0", 2, knowledge_state="unknown"
        )
        self.insert_action_grounding(
            "assertion:candidate-sq2-b",
            "snapshot:candidates",
            suffix="candidate-sq2-b",
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:candidates', 'assertion', 'assertion:candidate-sq2-b', ?)",
            ("8" * 64,),
        )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:candidates', 'steenrod-module:S0:v1|basis:x0|Sq1', "
            "'steenrod-module:S0:v1', 'basis:x0', 1, 'absent', NULL, NULL, ?)",
            ("a" * 64,),
        )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:candidates', 'steenrod-module:S0:v1|basis:x0|Sq2', "
            "'steenrod-module:S0:v1', 'basis:x0', 2, "
            "'unresolved_selection', NULL, NULL, ?)",
            ("d" * 64,),
        )

    def test_current_reducer_rejects_competing_or_retired_selection(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_snapshot("snapshot:reducer")
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:reducer", record_kind, record_id, record_hash),
            )

        for suffix in ("a", "b"):
            assertion_id = f"assertion:competing-{suffix}"
            self.insert_action(assertion_id, "basis:x0", 1, knowledge_state="unknown")
            self.insert_action_grounding(
                assertion_id, "snapshot:reducer", suffix=f"competing-{suffix}"
            )
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES ("
                "'snapshot:reducer', 'assertion', ?, ?)",
                (assertion_id, "8" * 64),
            )

        self.insert_action(
            "assertion:retired", "basis:x0", 2, knowledge_state="unknown"
        )
        self.insert_action_grounding(
            "assertion:retired", "snapshot:reducer", suffix="retired"
        )
        self.connection.execute(
            "INSERT INTO editorial_event VALUES ("
            "'event:retire', 'retract', 'editor', 'retired', "
            "'2026-08-05T00:02:00Z', 1, ?)",
            ("c" * 64,),
        )
        self.connection.execute(
            "INSERT INTO editorial_event_effect VALUES ("
            "'event:retire', 'assertion:retired', 'retire', 0)"
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:reducer', 'assertion', 'assertion:retired', ?)",
            ("8" * 64,),
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:reducer', 'editorial_event', 'event:retire', ?)",
            ("c" * 64,),
        )

        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "selected_steenrod_action_not_grounded_in_snapshot"
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:reducer', 'steenrod-module:S0:v1|basis:x0|Sq1', "
                "'steenrod-module:S0:v1', 'basis:x0', 1, 'selected', "
                "'assertion:competing-a', NULL, ?)",
                ("a" * 64,),
            )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:reducer', 'steenrod-module:S0:v1|basis:x0|Sq1', "
            "'steenrod-module:S0:v1', 'basis:x0', 1, 'unresolved_selection', "
            "NULL, NULL, ?)",
            ("b" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "selected_steenrod_action_not_grounded_in_snapshot"
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:reducer', 'steenrod-module:S0:v1|basis:x0|Sq2', "
                "'steenrod-module:S0:v1', 'basis:x0', 2, 'selected', "
                "'assertion:retired', NULL, ?)",
                ("d" * 64,),
            )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:reducer', 'steenrod-module:S0:v1|basis:x0|Sq2', "
            "'steenrod-module:S0:v1', 'basis:x0', 2, 'absent', NULL, NULL, ?)",
            ("e" * 64,),
        )

    def test_later_snapshot_can_retract_an_assertion_selected_earlier(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_action("assertion:lifecycle", "basis:x0", 1)
        self.insert_snapshot("snapshot:before-retire")
        self.insert_action_grounding(
            "assertion:lifecycle", "snapshot:before-retire", suffix="lifecycle"
        )
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
            ("assertion", "assertion:lifecycle", "8" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:before-retire", record_kind, record_id, record_hash),
            )
        slot = "steenrod-module:S0:v1|basis:x0|Sq1"
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:before-retire', ?, 'steenrod-module:S0:v1', 'basis:x0', "
            "1, 'selected', 'assertion:lifecycle', NULL, ?)",
            (slot, "e" * 64),
        )
        self.connection.execute(
            "UPDATE snapshot SET canonical_manifest_sha256 = ?, "
            "current_projection_sha256 = ?, finalized_at = ?, record_sha256 = ? "
            "WHERE snapshot_id = 'snapshot:before-retire'",
            ("1" * 64, "2" * 64, "2026-08-05T00:02:00Z", "3" * 64),
        )

        self.connection.execute(
            "INSERT INTO editorial_event VALUES ("
            "'event:later-retire', 'retract', 'editor', 'later correction', "
            "'2026-08-05T00:03:00Z', 1, ?)",
            ("f" * 64,),
        )
        self.connection.execute(
            "INSERT INTO editorial_event_effect VALUES ("
            "'event:later-retire', 'assertion:lifecycle', 'retire', 0)"
        )

        self.insert_snapshot("snapshot:after-retire")
        self.insert_grounding_snapshot_records("snapshot:after-retire", "lifecycle")
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
            ("assertion", "assertion:lifecycle", "8" * 64),
            ("editorial_event", "event:later-retire", "f" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:after-retire", record_kind, record_id, record_hash),
            )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "selected_steenrod_action_not_grounded_in_snapshot"
        ):
            self.connection.execute(
                "INSERT INTO current_steenrod_action VALUES ("
                "'snapshot:after-retire', ?, 'steenrod-module:S0:v1', 'basis:x0', "
                "1, 'selected', 'assertion:lifecycle', NULL, ?)",
                (slot, "a" * 64),
            )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:after-retire', ?, 'steenrod-module:S0:v1', 'basis:x0', "
            "1, 'absent', NULL, NULL, ?)",
            (slot, "b" * 64),
        )

    def test_module_admission_and_later_retirement_are_snapshot_scoped(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:module-source', 'derivation', ?)",
            ("e" * 64,),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:module-source', 'normalizer', '1', ?)",
            ("f" * 64,),
        )
        self.connection.execute(
            "INSERT INTO steenrod_import_evidence VALUES ("
            "'evidence:module-source', 'source:v1', 'source:module', ?)",
            ("2" * 64,),
        )
        self.connection.execute(
            "INSERT INTO steenrod_module_evidence VALUES ("
            "'steenrod-module:S0:v1', 'evidence:module-source', 'derives')"
        )
        self.connection.execute(
            "INSERT INTO editorial_event VALUES ("
            "'event:module-admit', 'admit', 'editor', 'profile accepted', "
            "'2026-08-05T00:00:00Z', 0, ?)",
            ("a" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "steenrod_module_editorial_effect_kind_mismatch",
        ):
            self.connection.execute(
                "INSERT INTO steenrod_module_editorial_effect VALUES ("
                "'event:module-admit', 'steenrod-module:S0:v1', 'retire', 0)"
            )
        self.connection.execute(
            "INSERT INTO steenrod_module_editorial_effect VALUES ("
            "'event:module-admit', 'steenrod-module:S0:v1', 'admit', 0)"
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_module_basis"
        ):
            self.insert_basis_element("basis:x1", 1, 1)

        self.insert_snapshot("snapshot:module-admitted")
        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "steenrod_module_editorial_target_not_in_snapshot",
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES ("
                "'snapshot:module-admitted', 'editorial_event', "
                "'event:module-admit', ?)",
                ("a" * 64,),
            )
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:module-admitted", record_kind, record_id, record_hash),
            )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "steenrod_module_editorial_target_not_in_snapshot",
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES ("
                "'snapshot:module-admitted', 'editorial_event', "
                "'event:module-admit', ?)",
                ("a" * 64,),
            )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:module-admitted', 'evidence', "
            "'evidence:module-source', ?)",
            ("e" * 64,),
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:module-admitted', 'editorial_event', "
            "'event:module-admit', ?)",
            ("a" * 64,),
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT module_id FROM snapshot_admitted_steenrod_module "
                "WHERE snapshot_id = 'snapshot:module-admitted'"
            ).fetchall(),
            [("steenrod-module:S0:v1",)],
        )
        self.connection.execute(
            "UPDATE snapshot SET canonical_manifest_sha256 = ?, "
            "current_projection_sha256 = ?, finalized_at = ?, record_sha256 = ? "
            "WHERE snapshot_id = 'snapshot:module-admitted'",
            ("1" * 64, "2" * 64, "2026-08-05T00:01:00Z", "3" * 64),
        )

        self.connection.execute(
            "INSERT INTO editorial_event VALUES ("
            "'event:module-retire', 'retract', 'editor', 'profile corrected', "
            "'2026-08-05T00:02:00Z', 1, ?)",
            ("b" * 64,),
        )
        self.connection.execute(
            "INSERT INTO steenrod_module_editorial_effect VALUES ("
            "'event:module-retire', 'steenrod-module:S0:v1', 'retire', 0)"
        )
        self.insert_snapshot("snapshot:module-retired")
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("evidence", "evidence:module-source", "e" * 64),
            ("editorial_event", "event:module-admit", "a" * 64),
            ("editorial_event", "event:module-retire", "b" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:module-retired", record_kind, record_id, record_hash),
            )
        self.assertEqual(
            self.connection.execute(
                "SELECT module_id FROM snapshot_admitted_steenrod_module "
                "WHERE snapshot_id = 'snapshot:module-retired'"
            ).fetchall(),
            [],
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_module_editorial_effect"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_module_editorial_effect VALUES ("
                "'event:module-retire', 'steenrod-module:S0:v1', 'retire', 1)"
            )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "immutable_steenrod_module_editorial_effect"
        ):
            self.connection.execute(
                "UPDATE steenrod_module_editorial_effect SET position = 2 "
                "WHERE event_id = 'event:module-retire'"
            )

    def test_profile_admission_requires_linked_snapshot_import_evidence(self) -> None:
        self.insert_spectrum("spectrum:tmf", "tmf")
        self.connection.execute(
            """
            INSERT INTO steenrod_module VALUES (
                'steenrod-module:tmf:v1', 'conceptual_spectrum', 'spectrum:tmf',
                'profile', 'stable', 2, 1, 'cohomological/1', 0,
                'homology-db.steenrod-module/1', 'v1', NULL,
                '{"basis":"milnor"}', ?
            )
            """,
            ("2" * 64,),
        )
        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:orphan-import', 'derivation', ?)",
            ("e" * 64,),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:orphan-import', 'normalizer', '1', ?)",
            ("f" * 64,),
        )
        self.connection.execute(
            "INSERT INTO steenrod_import_evidence VALUES ("
            "'evidence:orphan-import', 'source:v1', 'source:tmf', ?)",
            ("2" * 64,),
        )
        self.connection.execute(
            "INSERT INTO editorial_event VALUES ("
            "'event:tmf-admit', 'admit', 'editor', 'accepted', "
            "'2026-08-05T00:00:00Z', 0, ?)",
            ("a" * 64,),
        )
        self.connection.execute(
            "INSERT INTO steenrod_module_editorial_effect VALUES ("
            "'event:tmf-admit', 'steenrod-module:tmf:v1', 'admit', 0)"
        )
        self.insert_snapshot("snapshot:tmf-orphan")
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:tmf", "1" * 64),
            ("steenrod_module", "steenrod-module:tmf:v1", "2" * 64),
            ("evidence", "evidence:orphan-import", "e" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:tmf-orphan", record_kind, record_id, record_hash),
            )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "steenrod_module_editorial_target_not_in_snapshot",
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES ("
                "'snapshot:tmf-orphan', 'editorial_event', "
                "'event:tmf-admit', ?)",
                ("a" * 64,),
            )
        self.assertEqual(
            self.connection.execute(
                "SELECT * FROM snapshot_admitted_steenrod_module"
            ).fetchall(),
            [],
        )

    def test_module_import_evidence_identity_and_sealing_are_enforced(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:mismatch', 'derivation', ?)",
            ("a" * 64,),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:mismatch', 'normalizer', '1', ?)",
            ("b" * 64,),
        )
        self.connection.execute(
            "INSERT INTO steenrod_import_evidence VALUES ("
            "'evidence:mismatch', 'source:v1', 'source:bad', ?)",
            ("3" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "steenrod_module_evidence_identity_mismatch",
        ):
            self.connection.execute(
                "INSERT INTO steenrod_module_evidence VALUES ("
                "'steenrod-module:S0:v1', 'evidence:mismatch', 'derives')"
            )

        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:late-link', 'derivation', ?)",
            ("c" * 64,),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:late-link', 'normalizer', '1', ?)",
            ("d" * 64,),
        )
        self.connection.execute(
            "INSERT INTO steenrod_import_evidence VALUES ("
            "'evidence:late-link', 'source:v1', 'source:good', ?)",
            ("2" * 64,),
        )
        self.insert_snapshot("snapshot:module-evidence-sealed")
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("evidence", "evidence:late-link", "c" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                (
                    "snapshot:module-evidence-sealed",
                    record_kind,
                    record_id,
                    record_hash,
                ),
            )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_module_evidence"
        ):
            self.connection.execute(
                "INSERT INTO steenrod_module_evidence VALUES ("
                "'steenrod-module:S0:v1', 'evidence:late-link', 'derives')"
            )

        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:late-import', 'derivation', ?)",
            ("e" * 64,),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:late-import', 'normalizer', '1', ?)",
            ("f" * 64,),
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:module-evidence-sealed', 'evidence', "
            "'evidence:late-import', ?)",
            ("e" * 64,),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "sealed_snapshot_evidence"):
            self.connection.execute(
                "INSERT INTO steenrod_import_evidence VALUES ("
                "'evidence:late-import', 'source:v1', 'source:late', ?)",
                ("2" * 64,),
            )

    def test_snapshot_evidence_requires_its_typed_subtype_and_then_seals_it(self) -> None:
        self.insert_snapshot("snapshot:evidence")
        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:late', 'derivation', ?)",
            ("a" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "snapshot_evidence_subtype_missing"
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES ("
                "'snapshot:evidence', 'evidence', 'evidence:late', ?)",
                ("a" * 64,),
            )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:late', 'rule', '1', ?)",
            ("b" * 64,),
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:evidence', 'evidence', 'evidence:late', ?)",
            ("a" * 64,),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_snapshot_evidence"
        ):
            self.connection.execute(
                "INSERT INTO literature_evidence VALUES ("
                "'evidence:late', 'reference:missing', 'late')"
            )

    def test_steenrod_evidence_and_lifecycle_links_seal_before_projection(self) -> None:
        self.insert_spectrum()
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_action("assertion:late-links", "basis:x0", 1)
        self.connection.execute(
            "INSERT INTO evidence VALUES ('evidence:late-links', 'derivation', ?)",
            ("a" * 64,),
        )
        self.connection.execute(
            "INSERT INTO derivation_evidence VALUES ("
            "'evidence:late-links', 'rule', '1', ?)",
            ("b" * 64,),
        )
        self.connection.execute(
            "INSERT INTO assertion_review VALUES ("
            "'review:late-links', 'assertion:late-links', 'reviewer', 'accept', "
            "'2026-08-05T00:00:00Z', 'checked', ?)",
            ("c" * 64,),
        )
        self.connection.execute(
            "INSERT INTO editorial_event VALUES ("
            "'event:late-links', 'admit', 'editor', 'late', "
            "'2026-08-05T00:01:00Z', 0, ?)",
            ("d" * 64,),
        )
        self.insert_snapshot("snapshot:late-links")
        for record_kind, record_id, record_hash in (
            ("conceptual_spectrum", "spectrum:S0", "1" * 64),
            ("steenrod_module", "steenrod-module:S0:v1", "2" * 64),
            ("steenrod_basis_element", "basis:x0", "6" * 64),
            ("assertion", "assertion:late-links", "8" * 64),
            ("evidence", "evidence:late-links", "a" * 64),
            ("assertion_review", "review:late-links", "c" * 64),
            ("editorial_event", "event:late-links", "d" * 64),
        ):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, ?, ?, ?)",
                ("snapshot:late-links", record_kind, record_id, record_hash),
            )
        self.connection.execute(
            "INSERT INTO current_steenrod_action VALUES ("
            "'snapshot:late-links', 'steenrod-module:S0:v1|basis:x0|Sq1', "
            "'steenrod-module:S0:v1', 'basis:x0', 1, 'absent', NULL, NULL, ?)",
            ("e" * 64,),
        )
        self.connection.execute(
            "UPDATE snapshot SET canonical_manifest_sha256 = ?, "
            "current_projection_sha256 = ?, finalized_at = ?, record_sha256 = ? "
            "WHERE snapshot_id = 'snapshot:late-links'",
            ("1" * 64, "2" * 64, "2026-08-05T00:02:00Z", "3" * 64),
        )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_assertion_evidence"
        ):
            self.connection.execute(
                "INSERT INTO assertion_evidence VALUES ("
                "'assertion:late-links', 'evidence:late-links', 'derives')"
            )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "sealed_steenrod_editorial_effect"
        ):
            self.connection.execute(
                "INSERT INTO editorial_event_effect VALUES ("
                "'event:late-links', 'assertion:late-links', 'admit', 0)"
            )

    def test_knowledge_links_and_snapshot_records_resolve_new_typed_records(self) -> None:
        self.insert_spectrum()
        self.connection.execute(
            "INSERT INTO spectrum_name VALUES ("
            "'spectrum-name:S0', 'spectrum:S0', 'sphere spectrum', "
            "'Sphere spectrum', 'label', NULL, ?)",
            ("0" * 64,),
        )
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.connection.execute(
            "INSERT INTO knowledge_entry VALUES ("
            "'knowledge:steenrod', 'Steenrod module', 'definition', ?)",
            ("1" * 64,),
        )
        for position, (target_kind, target_id) in enumerate(
            (
                ("conceptual_spectrum", "spectrum:S0"),
                ("steenrod_module", "steenrod-module:S0:v1"),
                ("steenrod_basis_element", "basis:x0"),
            )
        ):
            self.connection.execute(
                "INSERT INTO knowledge_link VALUES (?, 'knowledge:steenrod', ?, ?, "
                "'describes', ?)",
                (
                    f"knowledge-link:{position}",
                    target_kind,
                    target_id,
                    str(position) * 64,
                ),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "invalid_knowledge_link_target"):
            self.connection.execute(
                "INSERT INTO knowledge_link VALUES ("
                "'knowledge-link:missing', 'knowledge:steenrod', 'conceptual_spectrum', "
                "'spectrum:missing', 'describes', ?)",
                ("4" * 64,),
            )

        self.insert_snapshot("snapshot:records")
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES ("
            "'snapshot:records', 'spectrum_name', 'spectrum-name:S0', ?)",
            ("0" * 64,),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "snapshot_record_not_resolved"):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES ("
                "'snapshot:records', 'steenrod_module', 'steenrod-module:S0:v1', ?)",
                ("f" * 64,),
            )

    def test_spectrum_and_steenrod_records_are_append_only(self) -> None:
        self.insert_spectrum()
        self.connection.execute(
            "INSERT INTO spectrum_name VALUES ("
            "'spectrum-name:S0', 'spectrum:S0', 'sphere spectrum', "
            "'Sphere spectrum', 'label', NULL, ?)",
            ("0" * 64,),
        )
        self.insert_finite_module()
        self.insert_basis_element("basis:x0", 0, 0)
        self.insert_basis_element("basis:x1", 1, 1)
        self.insert_action("assertion:sq1", "basis:x0", 1)
        self.connection.execute(
            "INSERT INTO steenrod_action_term VALUES ("
            "'assertion:sq1', 'steenrod-module:S0:v1', 'basis:x1', 0)"
        )
        self.connection.execute(
            "INSERT INTO assertion VALUES ("
            "'assertion:complete', 'steenrod_action_completeness', "
            "'conceptual_spectrum', 'spectrum:S0', 'complete:S0', 'exact', "
            "'fingerprint:complete', ?, ?)",
            ("c" * 64, "d" * 64),
        )
        self.connection.execute(
            "INSERT INTO completeness_assertion VALUES ("
            "'assertion:complete', "
            "'{\"basis_positions\":[0,1],\"maximum_operation_degree\":1}', "
            "'steenrod_action_coverage')"
        )
        self.connection.execute(
            "INSERT INTO steenrod_action_completeness_assertion VALUES ("
            "'assertion:complete', 'steenrod-module:S0:v1', 0, 1, 1)"
        )

        updates = (
            ("conceptual_spectrum", "permanent_label = 'rewritten'", "spectrum_id = 'spectrum:S0'"),
            ("spectrum_name", "display_name = 'rewritten'", "name_id = 'spectrum-name:S0'"),
            ("steenrod_module", "suspension_shift = 1", "module_id = 'steenrod-module:S0:v1'"),
            ("steenrod_basis_element", "display_name = 'rewritten'", "basis_element_id = 'basis:x0'"),
            ("steenrod_action_assertion", "operation_degree = 2", "assertion_id = 'assertion:sq1'"),
            ("steenrod_action_term", "position = 1", "assertion_id = 'assertion:sq1'"),
            (
                "steenrod_action_completeness_assertion",
                "maximum_operation_degree = 2",
                "assertion_id = 'assertion:complete'",
            ),
        )
        for table, assignment, predicate in updates:
            with self.subTest(table=table):
                with self.assertRaisesRegex(sqlite3.IntegrityError, f"immutable_{table}"):
                    self.connection.execute(
                        f"UPDATE {table} SET {assignment} WHERE {predicate}"
                    )
        with self.assertRaisesRegex(
            sqlite3.IntegrityError, "immutable_steenrod_action_term"
        ):
            self.connection.execute(
                "DELETE FROM steenrod_action_term WHERE assertion_id = 'assertion:sq1'"
            )


if __name__ == "__main__":
    unittest.main()
