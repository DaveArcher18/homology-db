from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from homology_db import atlas_schema
from homology_db.atlas_schema import AtlasSchema


class AtlasSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.database_path = Path(self.temporary_directory.name) / "atlas.sqlite3"
        self.schema_version = AtlasSchema.build(self.database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.addCleanup(self.connection.close)
        self.connection.execute("PRAGMA foreign_keys = ON")

    def insert_snapshot(self, snapshot_id: str) -> None:
        self.connection.execute(
            "INSERT INTO snapshot VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (snapshot_id, self.schema_version, "policy:test", "a" * 64,
             None, None, None, None),
        )

    def finalize_snapshot(self, snapshot_id: str) -> None:
        self.connection.execute(
            "UPDATE snapshot SET canonical_manifest_sha256 = ?, "
            "current_projection_sha256 = ?, finalized_at = ?, record_sha256 = ? "
            "WHERE snapshot_id = ?",
            ("b" * 64, "c" * 64, "2026-07-12T00:00:00Z", "d" * 64, snapshot_id),
        )

    def insert_space(self, space_id: str = "space:test", label: str = "Test space") -> None:
        self.connection.execute(
            "INSERT INTO conceptual_space VALUES (?, ?, ?)",
            (space_id, label, "0" * 64),
        )

    def insert_knowledge(self, suffix: str) -> tuple[str, str, str]:
        entry_id = f"knowledge:{suffix}"
        revision_id = f"knowledge-revision:{suffix}:1"
        review_id = f"knowledge-review:{suffix}:1"
        self.connection.execute(
            "INSERT INTO knowledge_entry VALUES (?, ?, ?, ?)",
            (entry_id, f"term {suffix}", "definition", "e" * 64),
        )
        self.connection.execute(
            "INSERT INTO knowledge_revision VALUES (?, ?, 1, ?, ?, 'markdown/1', ?, ?, ?, ?)",
            (revision_id, entry_id, f"Term {suffix}", f"Definition {suffix}.",
             "author", "2026-07-12T00:00:00Z", "f" * 64, "1" * 64),
        )
        self.connection.execute(
            "INSERT INTO knowledge_review VALUES (?, ?, ?, 'accept', ?, ?, ?)",
            (review_id, revision_id, "reviewer", "2026-07-12T00:01:00Z", "checked", "2" * 64),
        )
        return entry_id, revision_id, review_id

    def test_migrations_separate_the_production_domain_layers(self) -> None:
        self.assertEqual(self.schema_version, "homology-db.atlas-schema/4")
        tables = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        required = {
            "conceptual_space",
            "space_name",
            "family_definition",
            "family_instance_expression",
            "model",
            "source_artifact",
            "model_artifact",
            "derived_artifact",
            "reference",
            "computation_run",
            "knowledge_entry",
            "knowledge_revision",
            "knowledge_review",
            "assertion",
            "homology_assertion",
            "completeness_assertion",
            "assertion_evidence",
            "assertion_dependency",
            "editorial_event",
            "conflict_set",
            "snapshot",
            "snapshot_knowledge_selection",
            "current_homology",
        }
        self.assertTrue(required <= tables, sorted(required - tables))
        self.assertNotIn("space", tables)
        self.assertNotIn("homology", tables)
        applied = self.connection.execute(
            "SELECT version FROM schema_migration ORDER BY version"
        ).fetchall()
        self.assertEqual(applied, [(1,), (2,), (3,), (4,)])

    def test_snapshot_knowledge_selection_requires_matching_review_and_entry(self) -> None:
        entry_a, revision_a, review_a = self.insert_knowledge("a")
        _, _, review_b = self.insert_knowledge("b")
        self.insert_snapshot("snapshot:valid")
        self.connection.execute(
            "INSERT INTO snapshot_knowledge_selection VALUES (?, ?, ?, ?)",
            ("snapshot:valid", entry_a, revision_a, review_a),
        )
        self.insert_snapshot("snapshot:mismatched")
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO snapshot_knowledge_selection VALUES (?, ?, ?, ?)",
                ("snapshot:mismatched", entry_a, revision_a, review_b),
            )

    def test_knowledge_revision_cannot_be_used_as_assertion_evidence(self) -> None:
        _, revision_id, _ = self.insert_knowledge("evidence-boundary")
        self.insert_space()
        self.connection.execute(
            "INSERT INTO assertion VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("assertion:test", "homology", "conceptual_space", "space:test",
             "slot:test", "exact", "fingerprint:test", "3" * 64, "4" * 64),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO assertion_evidence VALUES (?, ?, 'supports')",
                ("assertion:test", revision_id),
            )
        self.connection.execute(
            "INSERT INTO evidence VALUES (?, 'literature', ?)",
            ("evidence:test", "5" * 64),
        )
        self.connection.execute(
            "INSERT INTO assertion_evidence VALUES (?, ?, 'supports')",
            ("assertion:test", "evidence:test"),
        )

    def test_assertions_and_knowledge_revisions_are_append_only(self) -> None:
        _, revision_id, _ = self.insert_knowledge("immutable")
        self.insert_space()
        self.connection.execute(
            "INSERT INTO assertion VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("assertion:immutable", "homology", "conceptual_space", "space:test",
             "slot:test", "exact", "fingerprint:test", "6" * 64, "7" * 64),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_assertion"):
            self.connection.execute(
                "UPDATE assertion SET knowledge_state = 'unknown' WHERE assertion_id = ?",
                ("assertion:immutable",),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_assertion"):
            self.connection.execute(
                "DELETE FROM assertion WHERE assertion_id = ?", ("assertion:immutable",)
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_knowledge_revision"):
            self.connection.execute(
                "UPDATE knowledge_revision SET body = 'rewritten' WHERE knowledge_revision_id = ?",
                (revision_id,),
            )

    def test_claim_components_reviews_and_events_are_append_only(self) -> None:
        _, _, knowledge_review_id = self.insert_knowledge("component-immutability")
        self.connection.execute(
            "INSERT INTO conceptual_space VALUES (?, ?, ?)",
            ("space:immutable", "Immutable space", "a" * 64),
        )
        self.connection.execute(
            "INSERT INTO assertion VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("assertion:component", "homology", "conceptual_space", "space:immutable",
             "slot:component", "unknown", "fingerprint:component", "b" * 64, "c" * 64),
        )
        self.connection.execute(
            "INSERT INTO homology_assertion VALUES (?, 'ordinary_homology', 'Z', ?, 0, 2, 'literature')",
            ("assertion:component", "convention:test"),
        )
        self.connection.execute(
            "INSERT INTO editorial_event VALUES (?, 'admit', ?, ?, ?, 0, ?)",
            ("event:immutable", "editor", "initial", "2026-07-12T00:00:00Z", "d" * 64),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_homology_assertion"):
            self.connection.execute(
                "UPDATE homology_assertion SET degree = 3 WHERE assertion_id = ?",
                ("assertion:component",),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_knowledge_review"):
            self.connection.execute(
                "UPDATE knowledge_review SET verdict = 'reject' WHERE knowledge_review_id = ?",
                (knowledge_review_id,),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_editorial_event"):
            self.connection.execute(
                "UPDATE editorial_event SET reason = 'rewritten' WHERE event_id = ?",
                ("event:immutable",),
            )

    def test_nonexact_homology_assertion_cannot_carry_a_group_value(self) -> None:
        self.insert_space()
        self.connection.execute(
            "INSERT INTO assertion VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("assertion:unknown", "homology", "conceptual_space", "space:test",
             "slot:unknown", "unknown", "fingerprint:unknown", "8" * 64, "9" * 64),
        )
        self.connection.execute(
            "INSERT INTO homology_assertion VALUES (?, 'ordinary_homology', 'Z', ?, 0, 2, 'literature')",
            ("assertion:unknown", "convention:test"),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO integer_group VALUES (?, 0)", ("assertion:unknown",)
            )

    def test_current_projection_selects_only_snapshot_member_in_the_same_slot(self) -> None:
        self.insert_space()
        self.connection.execute(
            "INSERT INTO assertion VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("assertion:selected", "homology", "conceptual_space", "space:test",
             "slot:selected", "exact", "fingerprint:selected", "a" * 64, "b" * 64),
        )
        self.connection.execute(
            "INSERT INTO homology_assertion VALUES (?, 'ordinary_homology', 'Z', ?, 0, 2, 'literature')",
            ("assertion:selected", "convention:test"),
        )
        self.connection.execute("INSERT INTO integer_group VALUES (?, 1)", ("assertion:selected",))
        self.connection.execute(
            "INSERT INTO \"reference\" VALUES (?, ?, ?, ?, ?, ?)",
            ("reference:test", "Test source", "https://example.test/source", "v1",
             "1" * 64, "2" * 64),
        )
        self.connection.execute(
            "INSERT INTO evidence VALUES (?, 'literature', ?)",
            ("evidence:selected", "3" * 64),
        )
        self.connection.execute(
            "INSERT INTO literature_evidence VALUES (?, ?, ?)",
            ("evidence:selected", "reference:test", "p. 1"),
        )
        self.connection.execute(
            "INSERT INTO assertion_evidence VALUES (?, ?, 'supports')",
            ("assertion:selected", "evidence:selected"),
        )
        self.connection.execute(
            "INSERT INTO assertion_review VALUES (?, ?, ?, 'accept', ?, ?, ?)",
            ("assertion-review:selected", "assertion:selected", "reviewer",
             "2026-07-12T00:00:00Z", "checked", "4" * 64),
        )
        self.connection.execute(
            "INSERT INTO editorial_event VALUES (?, 'admit', ?, ?, ?, 0, ?)",
            ("event:admit:selected", "editor", "grounded and reviewed",
             "2026-07-12T00:01:00Z", "5" * 64),
        )
        self.connection.execute(
            "INSERT INTO editorial_event_effect VALUES (?, ?, 'admit', 0)",
            ("event:admit:selected", "assertion:selected"),
        )
        self.insert_snapshot("snapshot:closure")
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO current_homology VALUES (?, ?, 'selected', ?, NULL, ?)",
                ("snapshot:closure", "slot:selected", "assertion:selected", "c" * 64),
            )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES (?, 'assertion', ?, ?)",
            ("snapshot:closure", "assertion:selected", "b" * 64),
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES (?, 'evidence', ?, ?)",
            ("snapshot:closure", "evidence:selected", "3" * 64),
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES (?, 'assertion_review', ?, ?)",
            ("snapshot:closure", "assertion-review:selected", "4" * 64),
        )
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES (?, 'editorial_event', ?, ?)",
            ("snapshot:closure", "event:admit:selected", "5" * 64),
        )
        self.connection.execute(
            "INSERT INTO current_homology VALUES (?, ?, 'selected', ?, NULL, ?)",
            ("snapshot:closure", "slot:selected", "assertion:selected", "c" * 64),
        )
        self.finalize_snapshot("snapshot:closure")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "snapshot_finalized"):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, 'assertion', ?, ?)",
                ("snapshot:closure", "assertion:selected", "b" * 64),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_current_homology"):
            self.connection.execute(
                "UPDATE current_homology SET projection_outcome = 'absent', "
                "selected_assertion_id = NULL WHERE snapshot_id = ? AND slot_key = ?",
                ("snapshot:closure", "slot:selected"),
            )

    def test_1159_model_workload_has_insertion_order_independent_canonical_export(self) -> None:
        forward_path = Path(self.temporary_directory.name) / "forward.sqlite3"
        reverse_path = Path(self.temporary_directory.name) / "reverse.sqlite3"
        forward = AtlasSchema.build_model_workload(forward_path, 1159, reverse=False)
        reverse = AtlasSchema.build_model_workload(reverse_path, 1159, reverse=True)
        self.assertEqual(forward["model_count"], 1159)
        self.assertEqual(forward["model_artifact_count"], 1159)
        self.assertEqual(forward["first_model_id"], "model:0000")
        self.assertEqual(forward["last_model_id"], "model:1158")
        self.assertEqual(forward["canonical_sha256"], reverse["canonical_sha256"])
        self.assertEqual(forward["canonical_bytes"], reverse["canonical_bytes"])

    def test_byte_identical_artifacts_do_not_merge_distinct_models(self) -> None:
        for suffix in ("a", "b"):
            self.connection.execute(
                "INSERT INTO model VALUES (?, 'finite_simplicial', 2, 'candidate', ?)",
                (f"model:{suffix}", suffix * 64),
            )
            self.connection.execute(
                "INSERT INTO model_artifact VALUES (?, ?, NULL, 'prototype/json', ?, ?)",
                (f"artifact:{suffix}", f"model:{suffix}", "f" * 64, suffix * 64),
            )
        rows = self.connection.execute(
            "SELECT model_id FROM model_artifact WHERE content_sha256 = ? ORDER BY model_id",
            ("f" * 64,),
        ).fetchall()
        self.assertEqual(rows, [("model:a",), ("model:b",)])

    def test_applied_migration_hashes_cannot_be_rewritten(self) -> None:
        migration_directory = Path(self.temporary_directory.name) / "migrations"
        migration_directory.mkdir()
        copied_migrations = []
        for source in atlas_schema._migration_files():
            destination = migration_directory / source.name
            destination.write_bytes(source.read_bytes())
            copied_migrations.append(destination)
        database_path = Path(self.temporary_directory.name) / "hash-guard.sqlite3"
        with mock.patch.object(atlas_schema, "_migration_files", return_value=copied_migrations):
            AtlasSchema.migrate(database_path)
            copied_migrations[0].write_text(
                copied_migrations[0].read_text(encoding="utf-8") + "\n-- rewritten\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "migration 1 hash changed"):
                AtlasSchema.migrate(database_path)

    def test_committed_v3_database_upgrades_without_rewriting_prior_migrations(self) -> None:
        migration_directory = Path(self.temporary_directory.name) / "upgrade-migrations"
        migration_directory.mkdir()
        copied_migrations = []
        for source in atlas_schema._migration_files():
            destination = migration_directory / source.name
            destination.write_bytes(source.read_bytes())
            copied_migrations.append(destination)
        database_path = Path(self.temporary_directory.name) / "upgrade.sqlite3"
        with mock.patch.object(
            atlas_schema, "_migration_files", return_value=copied_migrations[:3]
        ):
            self.assertEqual(
                AtlasSchema.migrate(database_path),
                "homology-db.atlas-schema/3",
            )
        with sqlite3.connect(database_path) as connection:
            prior_hashes = connection.execute(
                "SELECT version, sha256 FROM schema_migration ORDER BY version"
            ).fetchall()
        with mock.patch.object(atlas_schema, "_migration_files", return_value=copied_migrations):
            self.assertEqual(
                AtlasSchema.migrate(database_path),
                "homology-db.atlas-schema/4",
            )
        with sqlite3.connect(database_path) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT version, sha256 FROM schema_migration WHERE version <= 3 "
                    "ORDER BY version"
                ).fetchall(),
                prior_hashes,
            )
            conflict_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(conflict_set)")
            }
            self.assertNotIn("resolved_event_id", conflict_columns)
            self.assertIsNone(
                connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'conflict_member'"
                ).fetchone()
            )

    def test_v4_rejects_populated_v3_conflicts_instead_of_inventing_history(self) -> None:
        migration_directory = Path(self.temporary_directory.name) / "conflict-migrations"
        migration_directory.mkdir()
        copied_migrations = []
        for source in atlas_schema._migration_files():
            destination = migration_directory / source.name
            destination.write_bytes(source.read_bytes())
            copied_migrations.append(destination)
        database_path = Path(self.temporary_directory.name) / "populated-v3.sqlite3"
        with mock.patch.object(
            atlas_schema, "_migration_files", return_value=copied_migrations[:3]
        ):
            AtlasSchema.migrate(database_path)
        with sqlite3.connect(database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "INSERT INTO conceptual_space VALUES (?, ?, ?)",
                ("space:legacy", "Legacy space", "1" * 64),
            )
            connection.execute(
                "INSERT INTO assertion VALUES (?, 'homology', 'conceptual_space', ?, ?, "
                "'unknown', ?, ?, ?)",
                ("assertion:legacy", "space:legacy", "slot:legacy", "fingerprint:legacy",
                 "2" * 64, "3" * 64),
            )
            connection.execute(
                "INSERT INTO editorial_event VALUES (?, 'declare_conflict', ?, ?, ?, 0, ?)",
                ("event:legacy", "editor", "legacy conflict", "2026-07-12T00:00:00Z",
                 "4" * 64),
            )
            connection.execute(
                "INSERT INTO editorial_event_effect VALUES (?, ?, 'conflict_add', 0)",
                ("event:legacy", "assertion:legacy"),
            )
            connection.execute(
                "INSERT INTO conflict_set VALUES (?, ?, ?, NULL, ?)",
                ("conflict:legacy", "slot:legacy", "event:legacy", "5" * 64),
            )
            connection.execute(
                "INSERT INTO conflict_member VALUES (?, ?)",
                ("conflict:legacy", "assertion:legacy"),
            )
            connection.commit()
        with mock.patch.object(atlas_schema, "_migration_files", return_value=copied_migrations):
            with self.assertRaisesRegex(
                sqlite3.IntegrityError,
                "populated_v3_conflict_requires_editorial_migration",
            ):
                AtlasSchema.migrate(database_path)
        with sqlite3.connect(database_path) as connection:
            self.assertEqual(
                connection.execute("SELECT MAX(version) FROM schema_migration").fetchone()[0],
                3,
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM conflict_member").fetchone()[0],
                1,
            )

    def test_failed_v4_upgrade_rolls_back_every_schema_change(self) -> None:
        migration_directory = Path(self.temporary_directory.name) / "rollback-migrations"
        migration_directory.mkdir()
        copied_migrations = []
        for source in atlas_schema._migration_files():
            destination = migration_directory / source.name
            destination.write_bytes(source.read_bytes())
            copied_migrations.append(destination)
        database_path = Path(self.temporary_directory.name) / "rollback-v3.sqlite3"
        with mock.patch.object(
            atlas_schema, "_migration_files", return_value=copied_migrations[:3]
        ):
            AtlasSchema.migrate(database_path)
        with sqlite3.connect(database_path) as connection:
            connection.execute(
                "INSERT INTO derived_artifact VALUES (?, NULL, 'chains', "
                "'application/json', ?, ?)",
                ("derived-artifact:legacy-unbound", "e" * 64, "f" * 64),
            )
            connection.commit()
        with mock.patch.object(atlas_schema, "_migration_files", return_value=copied_migrations):
            with self.assertRaises(sqlite3.IntegrityError):
                AtlasSchema.migrate(database_path)
        with sqlite3.connect(database_path) as connection:
            self.assertEqual(
                connection.execute("SELECT MAX(version) FROM schema_migration").fetchone()[0],
                3,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT model_id FROM derived_artifact WHERE derived_artifact_id = ?",
                    ("derived-artifact:legacy-unbound",),
                ).fetchone(),
                (None,),
            )
            self.assertIsNone(
                connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'index' "
                    "AND name = 'model_artifact_content_idx'"
                ).fetchone()
            )

    def test_computation_inputs_require_a_typed_hash_matching_artifact(self) -> None:
        self.connection.execute(
            "INSERT INTO algorithm VALUES (?, ?, ?, ?, ?, ?)",
            ("algorithm:test", "test", "1", "local", "1" * 64, "2" * 64),
        )
        self.connection.execute(
            "INSERT INTO computation_environment VALUES (?, ?, ?, ?)",
            ("environment:test", "{}", "3" * 64, "4" * 64),
        )
        self.connection.execute(
            "INSERT INTO computation_run VALUES (?, ?, ?, ?, NULL, 'running', '{}', ?)",
            ("run:test", "algorithm:test", "environment:test",
             "2026-07-12T00:00:00Z", "5" * 64),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "invalid_run_input_artifact"):
            self.connection.execute(
                "INSERT INTO run_input VALUES (?, 'source_artifact', ?, ?, 0)",
                ("run:test", "source-artifact:missing", "6" * 64),
            )
        self.connection.execute(
            "INSERT INTO source_artifact VALUES (?, NULL, ?, ?, 1, ?)",
            ("source-artifact:test", "application/json", "7" * 64, "8" * 64),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "invalid_run_input_artifact"):
            self.connection.execute(
                "INSERT INTO run_input VALUES (?, 'source_artifact', ?, ?, 0)",
                ("run:test", "source-artifact:test", "9" * 64),
            )
        self.connection.execute(
            "INSERT INTO run_input VALUES (?, 'source_artifact', ?, ?, 0)",
            ("run:test", "source-artifact:test", "7" * 64),
        )

    def test_knowledge_links_require_a_typed_existing_target(self) -> None:
        self.connection.execute(
            "INSERT INTO knowledge_entry VALUES (?, ?, ?, ?)",
            ("knowledge:source", "source", "definition", "1" * 64),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "invalid_knowledge_link_target"):
            self.connection.execute(
                "INSERT INTO knowledge_link VALUES (?, ?, 'conceptual_space', ?, ?, ?)",
                ("knowledge-link:missing", "knowledge:source", "space:missing", "defines",
                 "2" * 64),
            )
        self.insert_space("space:linked", "Linked space")
        self.connection.execute(
            "INSERT INTO knowledge_link VALUES (?, ?, 'conceptual_space', ?, ?, ?)",
            ("knowledge-link:valid", "knowledge:source", "space:linked", "defines",
             "3" * 64),
        )

    def test_byte_identical_derived_artifacts_keep_model_provenance(self) -> None:
        for suffix in ("a", "b"):
            self.connection.execute(
                "INSERT INTO model VALUES (?, 'finite_simplicial', 2, 'candidate', ?)",
                (f"derived-model:{suffix}", suffix * 64),
            )
            self.connection.execute(
                "INSERT INTO derived_artifact VALUES (?, ?, 'chains', 'application/json', ?, ?)",
                (f"derived-artifact:{suffix}", f"derived-model:{suffix}", "e" * 64,
                 suffix * 64),
            )
        rows = self.connection.execute(
            "SELECT model_id FROM derived_artifact WHERE content_sha256 = ? ORDER BY model_id",
            ("e" * 64,),
        ).fetchall()
        self.assertEqual(rows, [("derived-model:a",), ("derived-model:b",)])

    def test_derived_artifact_requires_a_model(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO derived_artifact VALUES (?, NULL, 'chains', 'application/json', ?, ?)",
                ("derived-artifact:unbound", "e" * 64, "f" * 64),
            )

    def test_snapshot_records_require_a_known_hash_matching_target(self) -> None:
        self.insert_snapshot("snapshot:records")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "snapshot_record_not_resolved"):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, 'invented_kind', ?, ?)",
                ("snapshot:records", "anything", "1" * 64),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "snapshot_record_not_resolved"):
            self.connection.execute(
                "INSERT INTO snapshot_record VALUES (?, 'assertion', ?, ?)",
                ("snapshot:records", "assertion:missing", "2" * 64),
            )
        self.insert_space("space:snapshot-member", "Snapshot member")
        self.connection.execute(
            "INSERT INTO snapshot_record VALUES (?, 'conceptual_space', ?, ?)",
            ("snapshot:records", "space:snapshot-member", "0" * 64),
        )

    def test_finalized_snapshot_rejects_every_late_projection_insert(self) -> None:
        self.insert_snapshot("snapshot:sealed")
        self.connection.execute(
            "INSERT INTO canonical_export VALUES (?, 'snapshot_manifest', 'application/json', ?, 2)",
            ("snapshot:sealed", "1" * 64),
        )
        self.finalize_snapshot("snapshot:sealed")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "snapshot_finalized"):
            self.connection.execute(
                "INSERT INTO canonical_export VALUES (?, 'current_projection', "
                "'application/json', ?, 2)",
                ("snapshot:sealed", "2" * 64),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_snapshot"):
            self.finalize_snapshot("snapshot:sealed")

    def test_schema_migration_ledger_is_append_only(self) -> None:
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable_schema_migration"):
            self.connection.execute(
                "UPDATE schema_migration SET sha256 = ? WHERE version = 1",
                ("f" * 64,),
            )


if __name__ == "__main__":
    unittest.main()
