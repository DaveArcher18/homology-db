import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from homology_db.chromatic import ChromaticDatabase


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPORTER = REPOSITORY_ROOT / "scripts" / "export_static_atlas.py"


class StaticAtlasTest(unittest.TestCase):
    def test_pages_actions_are_pinned_to_full_commit_shas(self) -> None:
        workflow = (
            REPOSITORY_ROOT / ".github" / "workflows" / "deploy-atlas-pages.yml"
        ).read_text(encoding="utf-8")
        action_revisions = re.findall(r"^\s*uses:\s+[^@\s]+@([^\s]+)", workflow, re.MULTILINE)
        self.assertEqual(len(action_revisions), 4)
        self.assertTrue(
            all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in action_revisions)
        )

    def test_exporter_generates_complete_self_contained_atlas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            snapshot_id = ChromaticDatabase.build(database_path)

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
            build_summary = json.loads(completed.stdout)
            self.assertEqual(build_summary["relation_count"], 11)
            self.assertGreater(build_summary["source_database_bytes"], 0)
            html = output_path.read_text(encoding="utf-8")
            embedded = re.search(
                r'<script id="atlas-data" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            self.assertIsNotNone(embedded)
            atlas = json.loads(embedded.group(1))
            self.assertEqual(atlas["snapshot"]["snapshot_id"], snapshot_id)
            self.assertEqual(atlas["snapshot"]["schema_version"], "homology-db.static-atlas/2")
            self.assertEqual(
                atlas["snapshot"]["source_revision_inputs"],
                [
                    "corpus/chromatic-v1/manifest.json",
                    "corpus/chromatic-v1/poincare-sphere-facets.json",
                    "homology_db/__init__.py",
                    "homology_db/chromatic.py",
                    "homology_db/preview.py",
                    "scripts/export_static_atlas.py",
                    "static_atlas/atlas.css",
                    "static_atlas/atlas.js",
                    "static_atlas/index.template.html",
                ],
            )
            self.assertRegex(
                atlas["snapshot"]["source_inputs_sha256"], r"^[0-9a-f]{64}$"
            )
            self.assertIn(atlas["snapshot"]["source_tree_state"], {"clean", "dirty"})
            self.assertEqual(
                atlas["snapshot"]["source_inputs_dirty"],
                atlas["snapshot"]["source_tree_state"] == "dirty",
            )
            self.assertEqual(atlas["snapshot"]["conceptual_space_count"], 42)
            self.assertEqual(atlas["snapshot"]["relation_count"], 11)
            self.assertEqual(len(atlas["conceptual_spaces"]), 42)
            self.assertEqual(len({item["id"] for item in atlas["conceptual_spaces"]}), 42)
            self.assertIn("nonorientable surface genus 2", next(
                item["aliases"] for item in atlas["conceptual_spaces"]
                if item["id"] == "klein_bottle"
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
                homology_row["convention_state"], "not_recorded_in_database_schema"
            )
            self.assertNotIn("reliability", homology_row)
            self.assertEqual(
                projective_space["evidence"][0]["reliability"],
                "exact_owned_computation_with_cited_family_cross_check",
            )
            self.assertEqual(len(projective_space["computations"]), 1)
            self.assertTrue(projective_space["models"])
            self.assertEqual(projective_space["data_quality"]["state"], "valid")

            complex_projective_plane = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "complex_projective_space:2"
            )
            self.assertEqual(
                complex_projective_plane["parameters"],
                {"division_algebra": "complex"},
            )
            self.assertIn("hopf_invariant_one", complex_projective_plane["taxonomy"]["tags"])
            self.assertIn("projective planes", complex_projective_plane["summary"])
            self.assertIn("attaching maps", complex_projective_plane["chromatic_relevance"])
            self.assertEqual(
                complex_projective_plane["models"][0]["attaching_map"],
                "Attach e^4 to S^2 by the Hopf map eta.",
            )
            self.assertTrue(complex_projective_plane["evidence"][0]["citations"])
            self.assertEqual(
                complex_projective_plane["relations"],
                [
                    {
                        "detail": "The standard three-cell CW model is the 4-skeleton of the projective filtration of CP^infinity.",
                        "evidence_ids": [
                            "chromatic:evidence:complex_projective_space:2"
                        ],
                        "id": "relation:cp2:finite-skeleton:cp-infinity",
                        "source_id": "complex_projective_space:2",
                        "target_id": "complex_projective_space:infinity",
                        "type": "finite_skeleton_of",
                    }
                ],
            )
            self.assertTrue(all(
                citation["url"].startswith("https://")
                for evidence in complex_projective_plane["evidence"]
                for citation in evidence["citations"]
            ))

            cyclic_classifying_space = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "classifying_space:cyclic:3"
            )
            self.assertIsNone(next(
                property_["value"]
                for property_ in cyclic_classifying_space["properties"]
                if property_["key"] == "dimension"
            ))
            self.assertTrue(cyclic_classifying_space["infinite_finite_type"])
            self.assertEqual(
                cyclic_classifying_space["homology_coverage"]["kind"],
                "bounded_through_degree",
            )
            self.assertEqual(
                cyclic_classifying_space["homology_coverage"]["computed_through_degree"],
                24,
            )
            self.assertIsNone(
                cyclic_classifying_space["homology_coverage"]["upper_vanishing_starts_at"]
            )

            poincare_sphere = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "poincare_homology_sphere:3"
            )
            self.assertEqual(poincare_sphere["computations"], [])
            self.assertEqual(
                poincare_sphere["models"][0]["artifact_path"],
                "corpus/chromatic-v1/poincare-sphere-facets.json",
            )
            self.assertRegex(
                poincare_sphere["models"][0]["artifact_sha256"],
                r"^[0-9a-f]{64}$",
            )
            self.assertEqual(
                poincare_sphere["evidence"][0]["kind"],
                "official_model_and_cited_computation",
            )
            self.assertNotIn("<script src=", html)
            self.assertNotRegex(html, r'<link[^>]+rel=["\']stylesheet["\']')
            self.assertNotRegex(html, r"url\(\s*[\"']?https?://")

    def test_generated_atlas_exposes_the_browse_and_review_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
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
                'id="reliability-filter"',
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
                "Source: ${sourceTitle}",
                'detailsBlock("Evidence, sketches & citations", evidence.length, true)',
                "JSON.stringify(space.raw",
            ):
                self.assertIn(required_control, html)

    def test_generated_atlas_supports_progressive_filters_and_theme_preferences(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
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
            for theme_contract in (
                '<meta name="color-scheme" content="light dark">',
                'id="theme-select"',
                '<option value="system">System</option>',
                '<option value="light">Light</option>',
                '<option value="dark">Dark</option>',
                "homology-atlas-theme-v1",
                "prefers-color-scheme: dark",
                'window.addEventListener("storage"',
            ):
                self.assertIn(theme_contract, html)
            for progressive_control in (
                'id="filter-disclosure"',
                'id="active-filter-count"',
                'id="index-close"',
                'id="index-backdrop"',
                'tabindex="-1" aria-label="Close atlas index"',
                'aria-controls="snapshot-about"',
                "backgroundInertTargets",
                'atlasIndex.setAttribute("aria-modal"',
                "filterDisclosure.open = false",
                '"h4", "details-heading"',
                'setAttribute("headers"',
            ):
                self.assertIn(progressive_control, html)

    def test_export_is_deterministic_for_one_database_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            first_output = directory / "first.html"
            second_output = directory / "second.html"
            ChromaticDatabase.build(database_path)

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
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
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

    def test_export_fails_when_homology_evidence_integrity_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute("PRAGMA foreign_keys = OFF")
                connection.execute(
                    "DELETE FROM evidence WHERE evidence_id = ?",
                    ("chromatic:evidence:sphere:1",),
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
            self.assertIn("foreign-key failure", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_fails_when_model_and_evidence_inputs_disagree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    "UPDATE model SET chain_sha256 = ? WHERE space_id = 'sphere:1'",
                    ("0" * 64,),
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
            self.assertIn("Model/Evidence input mismatch", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_rejects_relation_evidence_from_another_space(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    """
                    UPDATE space_relation
                    SET evidence_id = 'chromatic:evidence:complex_projective_space:infinity'
                    WHERE relation_id = 'relation:cp2:finite-skeleton:cp-infinity'
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
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("references unresolved Evidence", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_rejects_non_https_citation_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    "UPDATE reference SET url = 'http://example.test/source' "
                    "WHERE reference_id = 'hatcher-at'"
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
            self.assertIn("non-HTTPS source URL", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_fails_with_a_precise_malformed_record_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
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
