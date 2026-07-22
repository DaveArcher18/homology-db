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
            self.assertEqual(atlas["snapshot"]["object_count"], 60)
            self.assertEqual(len(atlas["objects"]), 60)
            self.assertEqual(len({item["id"] for item in atlas["objects"]}), 60)
            self.assertIn("Klein bottle", next(
                item["aliases"] for item in atlas["objects"]
                if item["id"] == "nonorientable_surface:2"
            ))
            projective_aliases = next(
                item["aliases"]
                for item in atlas["objects"]
                if item["id"] == "real_projective_space:4"
            )
            self.assertIn("RP4", [alias.replace("^", "") for alias in projective_aliases])
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
                'id="atlas-index"',
                'id="object-list"',
                'id="result-status"',
                "Copy link",
                "Copy JSON",
                "Download JSON",
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
            sphere = next(item for item in atlas["objects"] if item["id"] == "sphere:1")
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


if __name__ == "__main__":
    unittest.main()
