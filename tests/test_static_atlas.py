import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from homology_db.preview import PreviewDatabase


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPORTER = REPOSITORY_ROOT / "scripts" / "export_static_atlas.py"


class StaticAtlasTest(unittest.TestCase):
    def test_exporter_generates_complete_self_contained_atlas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "preview.sqlite3"
            output_path = directory / "atlas.html"
            snapshot_id = PreviewDatabase.build(database_path)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            html = output_path.read_text(encoding="utf-8")
            embedded = re.search(
                r'<script id="atlas-data" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            self.assertIsNotNone(embedded)
            atlas = json.loads(embedded.group(1))
            self.assertEqual(atlas["snapshot"]["snapshot_id"], snapshot_id)
            self.assertEqual(atlas["snapshot"]["conceptual_space_count"], 60)
            self.assertEqual(len(atlas["conceptual_spaces"]), 60)
            self.assertEqual(len({item["id"] for item in atlas["conceptual_spaces"]}), 60)
            self.assertIn("Klein bottle", next(
                item["aliases"] for item in atlas["conceptual_spaces"]
                if item["id"] == "nonorientable_surface:2"
            ))
            projective_aliases = next(
                item["aliases"]
                for item in atlas["conceptual_spaces"]
                if item["id"] == "real_projective_space:4"
            )
            self.assertIn("RP4", [alias.replace("^", "") for alias in projective_aliases])
            projective_space = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "real_projective_space:4"
            )
            homology_row = projective_space["homology"][0]
            self.assertEqual(homology_row["theory"], "ordinary_homology")
            self.assertIsNone(homology_row["homology_convention"])
            self.assertEqual(
                homology_row["convention_state"], "not_recorded_in_preview_schema"
            )
            self.assertNotIn("reliability", homology_row)
            self.assertIsNone(projective_space["evidence"][0]["reliability"])
            self.assertEqual(projective_space["computations"], [])
            self.assertEqual(projective_space["data_quality"]["state"], "valid")
            self.assertNotIn("<script src=", html)
            self.assertNotRegex(html, r'<link[^>]+rel=["\']stylesheet["\']')
            self.assertNotRegex(html, r"url\(\s*[\"']?https?://")

    def test_generated_atlas_exposes_the_browse_and_review_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "preview.sqlite3"
            output_path = directory / "atlas.html"
            PreviewDatabase.build(database_path)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            html = output_path.read_text(encoding="utf-8")
            for required_control in (
                'id="atlas-search"',
                'id="coefficient-filter"',
                'id="reduced-filter"',
                'id="review-toggle"',
                'id="browse-control"',
                'id="about-toggle"',
                'id="atlas-index"',
                'id="atlas-document"',
                'id="result-status"',
                'id="generated-at"',
                "Copy link",
                "Copy JSON",
                "Download JSON",
                "Computation runs",
                "Data quality",
                "Source locator",
                "JSON.stringify(space.raw",
            ):
                self.assertIn(required_control, html)

    def test_export_is_deterministic_for_one_database_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "preview.sqlite3"
            first_output = directory / "first.html"
            second_output = directory / "second.html"
            PreviewDatabase.build(database_path)

            for output_path in (first_output, second_output):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(EXPORTER),
                        "--database",
                        str(database_path),
                        "--output",
                        str(output_path),
                    ],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

            self.assertEqual(first_output.read_bytes(), second_output.read_bytes())

    def test_current_snapshot_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            first_output = directory / "first.html"
            second_output = directory / "second.html"

            for output_path in (first_output, second_output):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(EXPORTER),
                        "--snapshot",
                        "current",
                        "--output",
                        str(output_path),
                    ],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

            self.assertEqual(first_output.read_bytes(), second_output.read_bytes())

    def test_checked_in_artifact_matches_the_current_source_build(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "atlas.html"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--snapshot",
                    "current",
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                (REPOSITORY_ROOT / "dist" / "atlas.html").read_bytes(),
                output_path.read_bytes(),
            )

    def test_nonexact_homology_state_is_not_exported_as_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "preview.sqlite3"
            output_path = directory / "atlas.html"
            PreviewDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    """
                    UPDATE homology
                    SET knowledge_state = 'not_computed', free_rank = 0, torsion_json = '[]'
                    WHERE space_id = 'sphere:1'
                      AND coefficient = 'Z'
                      AND reduced = 0
                      AND degree = 1
                    """
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            html = output_path.read_text(encoding="utf-8")
            embedded = re.search(
                r'<script id="atlas-data" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            atlas = json.loads(embedded.group(1))
            sphere = next(item for item in atlas["conceptual_spaces"] if item["id"] == "sphere:1")
            row = next(
                group for group in sphere["homology"]
                if group["coefficient_ring"] == "Z"
                and group["reduced"] is False
                and group["degree"] == 1
            )
            self.assertEqual(row["group"]["state"], "not_computed")
            self.assertEqual(row["group"]["plain"], "not computed")
            self.assertNotEqual(row["group"]["plain"], "0")

    def test_export_fails_when_homology_evidence_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "preview.sqlite3"
            output_path = directory / "atlas.html"
            PreviewDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute("PRAGMA foreign_keys = OFF")
                connection.execute(
                    "DELETE FROM evidence WHERE evidence_id = ?",
                    ("preview:evidence:sphere:1",),
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("unresolved evidence", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_fails_with_a_precise_malformed_record_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "preview.sqlite3"
            output_path = directory / "atlas.html"
            PreviewDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    "UPDATE space SET label = '' WHERE space_id = 'sphere:1'"
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("malformed Conceptual-space records", completed.stderr)
            self.assertIn("label", completed.stderr)
            self.assertFalse(output_path.exists())

            review_completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                    "--allow-malformed-for-review",
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(review_completed.returncode, 0, review_completed.stderr)
            html = output_path.read_text(encoding="utf-8")
            embedded = re.search(
                r'<script id="atlas-data" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            atlas = json.loads(embedded.group(1))
            malformed_space = next(
                item for item in atlas["conceptual_spaces"] if item["id"] == "sphere:1"
            )
            self.assertEqual(malformed_space["data_quality"]["state"], "malformed")
            self.assertEqual(
                malformed_space["data_quality"]["missing_required_fields"], ["label"]
            )


if __name__ == "__main__":
    unittest.main()
