from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

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
             "b" * 64, "c" * 64, "2026-07-12T00:00:00Z", "d" * 64),
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
        self.assertEqual(self.schema_version, "homology-db.atlas-schema/3")
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
        self.assertEqual(applied, [(1,), (2,), (3,)])

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

    def test_nonexact_homology_assertion_cannot_carry_a_group_value(self) -> None:
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
        self.connection.execute(
            "INSERT INTO conceptual_space VALUES (?, ?, ?)",
            ("space:test", "Test space", "0" * 64),
        )
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


if __name__ == "__main__":
    unittest.main()
