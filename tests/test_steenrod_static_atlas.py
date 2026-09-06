import copy
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock

from homology_db.atlas_schema import AtlasSchema
from homology_db.chromatic import ChromaticDatabase
from scripts import export_static_atlas


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPORTER = REPOSITORY_ROOT / "scripts" / "export_static_atlas.py"


def embedded_atlas(path: Path) -> tuple[str, dict]:
    html = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="atlas-data" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("generated atlas has no embedded read model")
    return html, json.loads(match.group(1))


class SteenrodStaticAtlasTest(unittest.TestCase):
    def test_unreviewed_candidate_cannot_target_the_public_atlas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            public_path = directory / "dist" / "atlas.html"
            ChromaticDatabase.build(database_path)
            with mock.patch.object(
                export_static_atlas,
                "PUBLIC_ATLAS_PATH",
                public_path,
                create=True,
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "unreviewed Steenrod candidate cannot target",
                ):
                    export_static_atlas.export_atlas(
                        database_path,
                        public_path,
                        steenrod_review_candidate=True,
                    )
            self.assertFalse(public_path.exists())

    def test_explicit_public_preview_can_target_the_public_atlas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            public_path = directory / "dist" / "atlas.html"
            ChromaticDatabase.build(database_path)
            with mock.patch.object(
                export_static_atlas,
                "PUBLIC_ATLAS_PATH",
                public_path,
                create=True,
            ):
                summary = export_static_atlas.export_atlas(
                    database_path,
                    public_path,
                    steenrod_review_candidate=True,
                    allow_public_review_preview=True,
                )
            _, atlas = embedded_atlas(public_path)
            self.assertEqual(summary["conceptual_spectrum_count"], 49)
            self.assertEqual(
                atlas["snapshot"]["spectrum_release_status"],
                "public_review_preview",
            )
            self.assertIn("Public feedback preview", public_path.read_text(encoding="utf-8"))
            self.assertTrue(atlas["snapshot"]["spectrum_review_candidate"])
            self.assertTrue(
                all(
                    spectrum["review_state"] == "imported_unreviewed"
                    for spectrum in atlas["conceptual_spectra"]
                )
            )

    def test_structured_acceptance_build_is_deterministic_and_gate_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            candidate_path = directory / "candidate.html"
            packet_path = directory / "candidate.review.json"
            coverage_path = directory / "candidate.coverage.md"
            acceptance_path = directory / "dan-acceptance.json"
            ChromaticDatabase.build(database_path)

            candidate = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(candidate_path),
                    "--steenrod-review-candidate",
                    "--steenrod-review-packet",
                    str(packet_path),
                    "--steenrod-coverage-report",
                    str(coverage_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(candidate.returncode, 0, candidate.stderr)
            _, candidate_atlas = embedded_atlas(candidate_path)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            projection = packet["release_projection"]
            build = packet["build"]
            acceptance = {
                "schema_version": "homology-db.steenrod-acceptance/1",
                "reviewer": "Dan Isaksen",
                "verdict": "accept",
                "reviewed_at": "2026-08-05T15:04:05Z",
                "evidence": {
                    "kind": "written_acceptance",
                    "locator": "fixture://dan-isaksen/acceptance",
                    "sha256": "b" * 64,
                },
                "editorial_actor": "Synthetic release editor",
                "bindings": {
                    "candidate_sha256": packet["candidate_sha256"],
                    "spectrum_source_sha256": build["spectrum_source_sha256"],
                    "source_commit": build["source_commit"],
                    "source_inputs_sha256": build["source_inputs_sha256"],
                    "source_database_hash_kind": build["source_database_hash_kind"],
                    "source_database_sha256": build["source_database_sha256"],
                    "review_packet_sha256": hashlib.sha256(
                        packet_path.read_bytes()
                    ).hexdigest(),
                    "coverage_report_sha256": hashlib.sha256(
                        coverage_path.read_bytes()
                    ).hexdigest(),
                    "spectrum_snapshot_id": projection["spectrum_snapshot"][
                        "snapshot_id"
                    ],
                    "spectrum_snapshot_manifest_sha256": projection[
                        "spectrum_snapshot"
                    ]["manifest_sha256"],
                    "spectrum_count": 49,
                    "assertion_review_count": projection["assertion_reviews"]["count"],
                    "assertion_review_manifest_sha256": projection[
                        "assertion_reviews"
                    ]["manifest_sha256"],
                    "editorial_admission_count": projection[
                        "editorial_admissions"
                    ]["count"],
                    "editorial_admission_manifest_sha256": projection[
                        "editorial_admissions"
                    ]["manifest_sha256"],
                    "tmf_profile_module_content_sha256": projection[
                        "editorial_admissions"
                    ]["profile_module_content_sha256"],
                },
            }
            acceptance_path.write_text(
                json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            accepted_paths = []
            for stem in ("accepted-first", "accepted-second"):
                accepted_path = directory / f"{stem}.html"
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(EXPORTER),
                        "--database",
                        str(database_path),
                        "--output",
                        str(accepted_path),
                        "--steenrod-acceptance-record",
                        str(acceptance_path),
                    ],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                accepted_paths.append(accepted_path)

            self.assertEqual(accepted_paths[0].read_bytes(), accepted_paths[1].read_bytes())
            _, accepted_atlas = embedded_atlas(accepted_paths[0])
            accepted_snapshot = accepted_atlas["snapshot"]
            self.assertEqual(
                accepted_snapshot["spectrum_release_status"],
                "accepted_finalized",
            )
            self.assertFalse(accepted_snapshot["spectrum_review_candidate"])
            self.assertEqual(
                accepted_snapshot["spectrum_snapshot"]["finalized_at"],
                acceptance["reviewed_at"],
            )
            self.assertEqual(
                accepted_snapshot["spectrum_snapshot"]["assertion_reviews"],
                projection["assertion_reviews"],
            )
            self.assertEqual(
                accepted_snapshot["spectrum_snapshot"]["editorial_admissions"],
                projection["editorial_admissions"],
            )
            self.assertEqual(
                accepted_snapshot["spectrum_acceptance"]["record_sha256"],
                hashlib.sha256(acceptance_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                accepted_snapshot["spectrum_database_hash_kind"],
                "homology-db.sqlite-logical/2",
            )
            self.assertRegex(
                accepted_snapshot["spectrum_database_sha256"],
                r"^[0-9a-f]{64}$",
            )
            self.assertEqual(
                accepted_snapshot["spectrum_materialization"][
                    "logical_database_sha256"
                ],
                accepted_snapshot["spectrum_database_sha256"],
            )
            self.assertEqual(
                accepted_snapshot["spectrum_materialization"]["record_counts"][
                    "assertion_review_count"
                ],
                5_828,
            )
            self.assertTrue(
                all(
                    spectrum["review_state"] == "accepted"
                    and spectrum["module"]["review_state"] == "accepted"
                    and spectrum["module"]["evidence"]["review_state"]
                    == "imported_unreviewed"
                    for spectrum in accepted_atlas["conceptual_spectra"]
                )
            )
            self.assertEqual(
                accepted_atlas["snapshot"]["spectrum_source"]["review_state"],
                "imported_unreviewed",
            )
            candidate_hashes = {
                spectrum["spectrum_id"]: spectrum["module"]["content_sha256"]
                for spectrum in candidate_atlas["conceptual_spectra"]
            }
            accepted_hashes = {
                spectrum["spectrum_id"]: spectrum["module"]["content_sha256"]
                for spectrum in accepted_atlas["conceptual_spectra"]
            }
            self.assertEqual(accepted_hashes, candidate_hashes)

            gated = subprocess.run(
                [
                    sys.executable,
                    str(REPOSITORY_ROOT / "scripts" / "verify_steenrod_release.py"),
                    "--atlas",
                    str(accepted_paths[0]),
                    "--review",
                    str(acceptance_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(gated.returncode, 0, gated.stderr)
            self.assertEqual(json.loads(gated.stdout)["state"], "reviewed_cw49")

            forged = copy.deepcopy(acceptance)
            forged["bindings"]["candidate_sha256"] = "0" * 64
            acceptance_path.write_text(
                json.dumps(forged, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            forged_output = directory / "forged-accepted.html"
            rejected = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(forged_output),
                    "--steenrod-acceptance-record",
                    str(acceptance_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn(
                "Steenrod acceptance binding mismatch for candidate_sha256",
                rejected.stderr,
            )
            self.assertFalse(forged_output.exists())

    def test_steenrod_sources_participate_in_the_revision_hash(self) -> None:
        required = {
            "corpus/steenrod-cw49-v1/corpus.json",
            "corpus/steenrod-cw49-v1/upstream-adams.json",
            "homology_db/atlas_schema.py",
            "homology_db/migrations/0005_stable_steenrod_modules.sql",
            "homology_db/steenrod.py",
            "homology_db/steenrod_snapshot.py",
            "scripts/materialize_steenrod_snapshot.py",
            "scripts/verify_steenrod_release.py",
        }
        self.assertTrue(required <= set(export_static_atlas.SOURCE_REVISION_INPUTS))

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source.txt"
            source.write_text("first", encoding="utf-8")
            with mock.patch.object(export_static_atlas, "REPOSITORY_ROOT", root), mock.patch.object(
                export_static_atlas, "SOURCE_REVISION_INPUTS", ("source.txt",)
            ):
                first = export_static_atlas.source_inputs_sha256()
                source.write_text("second", encoding="utf-8")
                second = export_static_atlas.source_inputs_sha256()
        self.assertNotEqual(first, second)

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            migration = root / "homology_db" / "migrations" / "0005.sql"
            migration.parent.mkdir(parents=True)
            migration.write_text("first schema", encoding="utf-8")
            with mock.patch.object(export_static_atlas, "REPOSITORY_ROOT", root), mock.patch.object(
                export_static_atlas,
                "SOURCE_REVISION_INPUTS",
                ("homology_db/migrations/0005.sql",),
            ):
                first_schema = export_static_atlas.source_inputs_sha256()
                migration.write_text("changed schema", encoding="utf-8")
                second_schema = export_static_atlas.source_inputs_sha256()
        self.assertNotEqual(first_schema, second_schema)

    def test_review_packet_and_coverage_report_are_deterministic_and_unreviewed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            ChromaticDatabase.build(database_path)
            generated = []
            for stem in ("first", "second"):
                atlas_path = directory / f"{stem}.html"
                packet_path = directory / f"{stem}.review.json"
                coverage_path = directory / f"{stem}.coverage.md"
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(EXPORTER),
                        "--database",
                        str(database_path),
                        "--output",
                        str(atlas_path),
                        "--steenrod-review-candidate",
                        "--steenrod-review-packet",
                        str(packet_path),
                        "--steenrod-coverage-report",
                        str(coverage_path),
                    ],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                summary = json.loads(completed.stdout)
                self.assertEqual(
                    summary["steenrod_review_packet_sha256"],
                    hashlib.sha256(packet_path.read_bytes()).hexdigest(),
                )
                self.assertEqual(
                    summary["steenrod_coverage_report_sha256"],
                    hashlib.sha256(coverage_path.read_bytes()).hexdigest(),
                )
                generated.append((atlas_path, packet_path, coverage_path))

            self.assertEqual(generated[0][0].read_bytes(), generated[1][0].read_bytes())
            self.assertEqual(generated[0][1].read_bytes(), generated[1][1].read_bytes())
            self.assertEqual(generated[0][2].read_bytes(), generated[1][2].read_bytes())

            packet = json.loads(generated[0][1].read_text(encoding="utf-8"))
            _, packet_atlas = embedded_atlas(generated[0][0])
            from scripts.verify_steenrod_release import candidate_sha256

            self.assertEqual(
                packet["schema_version"],
                "homology-db.steenrod-review-packet/1",
            )
            self.assertEqual(packet["review_state"], "imported_unreviewed")
            self.assertFalse(packet["acceptance_recorded"])
            self.assertEqual(packet["requested_reviewer"], "Dan Isaksen")
            self.assertRegex(packet["candidate_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                packet["candidate_sha256"],
                candidate_sha256(packet_atlas["conceptual_spectra"]),
            )
            self.assertEqual(
                packet["atlas_html_sha256"],
                hashlib.sha256(generated[0][0].read_bytes()).hexdigest(),
            )
            self.assertEqual(
                packet["coverage"],
                {
                    "action_slot_count": 5780,
                    "basis_element_count": 942,
                    "decode_state_counts": {"complete": 49},
                    "exact_nonzero_action_count": 2503,
                    "exact_zero_action_count": 3277,
                    "finite_module_count": 48,
                    "profile_module_count": 1,
                    "spectrum_count": 49,
                },
            )
            self.assertEqual(
                packet["source"]["sseqcpp_commit"],
                "23d12c973db2b294a6c00c15bd106e70b0af3fa6",
            )
            build = packet["build"]
            self.assertRegex(build["source_commit"], r"^[0-9a-f]{40}$")
            self.assertRegex(build["source_inputs_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                build["source_database_hash_kind"],
                "homology-db.sqlite-logical/1",
            )
            self.assertRegex(build["source_database_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                build["spectrum_source_sha256"],
                hashlib.sha256(
                    json.dumps(
                        packet["source"],
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
            )
            release_projection = packet["release_projection"]
            self.assertEqual(
                release_projection["schema_version"],
                "homology-db.steenrod-release-projection/1",
            )
            self.assertEqual(
                release_projection["assertion_reviews"]["count"],
                5828,
            )
            self.assertEqual(
                release_projection["editorial_admissions"]["count"],
                5829,
            )
            self.assertRegex(
                release_projection["assertion_reviews"]["manifest_sha256"],
                r"^[0-9a-f]{64}$",
            )
            self.assertRegex(
                release_projection["editorial_admissions"]["manifest_sha256"],
                r"^[0-9a-f]{64}$",
            )
            tmf_summary = next(
                spectrum
                for spectrum in packet["spectra"]
                if spectrum["spectrum_id"] == "tmf"
            )
            self.assertEqual(
                release_projection["editorial_admissions"][
                    "profile_module_content_sha256"
                ],
                tmf_summary["module_content_sha256"],
            )
            spectrum_snapshot = release_projection["spectrum_snapshot"]
            self.assertEqual(
                spectrum_snapshot["snapshot_id"],
                f"steenrod-cw49-v1-{packet['candidate_sha256'][:16]}",
            )
            self.assertRegex(spectrum_snapshot["manifest_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                spectrum_snapshot["record_counts"],
                {
                    "action_assertion_count": 5780,
                    "assertion_review_count": 5828,
                    "basis_element_count": 942,
                    "completeness_assertion_count": 48,
                    "editorial_admission_count": 5829,
                    "module_count": 49,
                    "profile_module_admission_count": 1,
                    "spectrum_count": 49,
                },
            )
            self.assertEqual(len(packet["spectra"]), 49)
            summaries = {item["spectrum_id"]: item for item in packet["spectra"]}
            self.assertEqual(
                set(summaries["S0"]["exports"]),
                {"bruner", "sseq", "sseqcpp"},
            )
            self.assertEqual(
                summaries["S0"]["evidence"]["review_state"],
                "imported_unreviewed",
            )
            self.assertTrue(summaries["S0"]["evidence"]["source_locator"])
            self.assertEqual(
                summaries["tmf"]["exports"]["bruner"],
                {"reason": "infinite_profile", "status": "unsupported"},
            )
            self.assertEqual(
                summaries["tmf"]["exports"]["sseqcpp"],
                {"reason": "infinite_profile", "status": "unsupported"},
            )
            self.assertTrue(
                all(
                    export["status"] != "ready"
                    or re.fullmatch(r"[0-9a-f]{64}", export["payload_sha256"])
                    for spectrum in packet["spectra"]
                    for export in spectrum["exports"].values()
                )
            )

            report = generated[0][2].read_text(encoding="utf-8")
            self.assertIn("# cw49 Steenrod review coverage", report)
            self.assertIn("Review state: `imported_unreviewed`", report)
            self.assertIn("- Spectra: 49 (48 finite basis; 1 profile)", report)
            self.assertIn("- Basis elements: 942", report)
            self.assertIn("- Exact actions: 5,780 (2,503 nonzero; 3,277 zero)", report)
            self.assertIn("| S0 | complete | finite_basis |", report)
            self.assertIn("| tmf | complete | profile |", report)

    def test_artifact_identity_uses_logical_database_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            first_database = directory / "first.sqlite3"
            repacked_database = directory / "repacked.sqlite3"
            first_output = directory / "first.html"
            repacked_output = directory / "repacked.html"
            ChromaticDatabase.build(first_database)
            shutil.copy2(first_database, repacked_database)
            with sqlite3.connect(repacked_database) as connection:
                connection.execute("CREATE TABLE packaging_noise(value TEXT)")
                connection.execute("INSERT INTO packaging_noise VALUES ('ignored')")
                connection.execute("DROP TABLE packaging_noise")
            original_timestamp = first_database.stat().st_mtime
            os.utime(
                repacked_database,
                (original_timestamp + 3600, original_timestamp + 3600),
            )
            self.assertNotEqual(
                first_database.stat().st_mtime,
                repacked_database.stat().st_mtime,
            )

            self.assertNotEqual(
                hashlib.sha256(first_database.read_bytes()).hexdigest(),
                hashlib.sha256(repacked_database.read_bytes()).hexdigest(),
            )
            summaries = []
            for database_path, output_path in (
                (first_database, first_output),
                (repacked_database, repacked_output),
            ):
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
                summaries.append(json.loads(completed.stdout))

            _, first_atlas = embedded_atlas(first_output)
            _, repacked_atlas = embedded_atlas(repacked_output)
            first_snapshot = first_atlas["snapshot"]
            repacked_snapshot = repacked_atlas["snapshot"]
            self.assertEqual(
                first_snapshot["source_database_hash_kind"],
                "homology-db.sqlite-logical/1",
            )
            self.assertEqual(
                first_snapshot["source_database_sha256"],
                repacked_snapshot["source_database_sha256"],
            )
            self.assertEqual(
                first_snapshot["source_database_sha256"],
                export_static_atlas._legacy_logical_database_sha256(first_database),
            )
            self.assertNotEqual(
                first_snapshot["source_database_sha256"],
                export_static_atlas.logical_database_sha256(first_database),
            )
            self.assertNotIn("source_database_physical_sha256", first_snapshot)
            self.assertEqual(
                summaries[0]["source_database_hash_kind"],
                "homology-db.sqlite-logical/1",
            )
            self.assertNotEqual(
                summaries[0]["source_database_physical_sha256"],
                summaries[1]["source_database_physical_sha256"],
            )
            self.assertEqual(first_output.read_bytes(), repacked_output.read_bytes())

    def test_logical_database_hash_excludes_migration_application_time(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            first_database = directory / "first.sqlite3"
            later_database = directory / "later.sqlite3"
            AtlasSchema.build(first_database)
            shutil.copy2(first_database, later_database)
            with closing(sqlite3.connect(later_database)) as connection:
                trigger_sql = connection.execute(
                    "SELECT sql FROM sqlite_master WHERE type = 'trigger' "
                    "AND name = 'schema_migration_u'"
                ).fetchone()[0]
                connection.execute("DROP TRIGGER schema_migration_u")
                connection.execute(
                    "UPDATE schema_migration SET applied_at = ? WHERE version = 5",
                    ("2099-01-01 00:00:00",),
                )
                connection.execute(trigger_sql)
                connection.commit()

            with closing(sqlite3.connect(first_database)) as connection:
                first_applied_at = connection.execute(
                    "SELECT applied_at FROM schema_migration WHERE version = 5"
                ).fetchone()[0]
            with closing(sqlite3.connect(later_database)) as connection:
                later_applied_at = connection.execute(
                    "SELECT applied_at FROM schema_migration WHERE version = 5"
                ).fetchone()[0]
            self.assertNotEqual(first_applied_at, later_applied_at)
            self.assertEqual(
                export_static_atlas.logical_database_sha256(first_database),
                export_static_atlas.logical_database_sha256(later_database),
            )
            self.assertNotEqual(
                export_static_atlas._legacy_logical_database_sha256(first_database),
                export_static_atlas._legacy_logical_database_sha256(later_database),
            )

    def test_review_candidate_is_explicit_and_keeps_public_export_withheld(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            public_path = directory / "public.html"
            review_path = directory / "steenrod-review.html"
            ChromaticDatabase.build(database_path)

            public = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(public_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(public.returncode, 0, public.stderr)
            public_summary = json.loads(public.stdout)
            public_html, public_atlas = embedded_atlas(public_path)
            self.assertEqual(public_summary["conceptual_spectrum_count"], 0)
            self.assertEqual(public_atlas["conceptual_spectra"], [])
            self.assertEqual(
                public_atlas["snapshot"]["spectrum_release_status"],
                "withheld_pending_review",
            )
            self.assertIn('id="nav-spectra"', public_html)
            self.assertIn('id="nav-spectra" class="secondary-resource-link" href="#spectra" hidden', public_html)

            review = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(review_path),
                    "--steenrod-review-candidate",
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(review.returncode, 0, review.stderr)
            review_summary = json.loads(review.stdout)
            review_html, review_atlas = embedded_atlas(review_path)
            spectra = review_atlas["conceptual_spectra"]
            self.assertEqual(review_summary["conceptual_space_count"], 42)
            self.assertEqual(review_summary["conceptual_spectrum_count"], 49)
            self.assertEqual(len(review_atlas["conceptual_spaces"]), 42)
            self.assertEqual(len(spectra), 49)
            self.assertEqual(len({spectrum["id"] for spectrum in spectra}), 49)
            self.assertEqual(
                review_atlas["snapshot"]["spectrum_release_status"],
                "imported_unreviewed_review_candidate",
            )
            self.assertTrue(review_atlas["snapshot"]["spectrum_review_candidate"])
            self.assertTrue(
                all(spectrum["kind"] == "conceptual_spectrum" for spectrum in spectra)
            )
            self.assertTrue(
                all(spectrum["review_state"] == "imported_unreviewed" for spectrum in spectra)
            )
            self.assertTrue(all(spectrum["module"]["reduced"] is True for spectrum in spectra))

            by_slug = {spectrum["slug"]: spectrum for spectrum in spectra}
            projective_spectra = [
                spectrum
                for spectrum in spectra
                if spectrum["spectrum_id"].startswith("RP")
            ]
            self.assertTrue(projective_spectra)
            self.assertTrue(
                all(
                    "projective" in spectrum["search_aliases"]
                    for spectrum in projective_spectra
                )
            )
            sphere = by_slug["s0"]
            self.assertEqual(sphere["module"]["module_type"], "finite_basis")
            self.assertEqual(
                sphere["module"]["basis"],
                [
                    {
                        "basis_id": "S0:b0",
                        "degree": 0,
                        "name": "x0",
                        "ordinal": 0,
                    }
                ],
            )
            self.assertEqual(set(sphere["downloads"]), {"bruner", "sseq", "sseqcpp"})
            for download in sphere["downloads"].values():
                self.assertEqual(download["status"], "ready")
                self.assertRegex(download["manifest"]["payload_sha256"], r"^[0-9a-f]{64}$")
                self.assertEqual(
                    download["manifest"]["payload_sha256"],
                    hashlib.sha256(download["payload"].encode("utf-8")).hexdigest(),
                )

            tmf = by_slug["tmf"]
            self.assertEqual(tmf["module"]["module_type"], "profile")
            self.assertEqual(
                tmf["module"]["profile"],
                {"basis": "milnor", "p_part": [3, 2, 1], "truncated": True},
            )
            self.assertEqual(tmf["downloads"]["sseq"]["status"], "ready")
            self.assertEqual(
                tmf["downloads"]["sseqcpp"],
                {"reason": "infinite_profile", "status": "unsupported"},
            )
            self.assertEqual(
                tmf["downloads"]["bruner"],
                {"reason": "infinite_profile", "status": "unsupported"},
            )
            for route_contract in (
                'href="#spectra"',
                "function buildSpectraView",
                "function buildSpectrumView",
                'hash === "#spectra"',
                '/^#spectrum=(.+)$/',
                "Search all spectra",
                "Steenrod operations",
                "Exact zero",
                "Unknown",
                "Exact zero outside finite support",
                "Imported · awaiting review",
                "Accepted · finalized",
                "spectrumReleaseAccepted",
                "real projective space",
                "overflow-wrap: anywhere",
                "word-break: break-word",
                "Cohomology convention",
                "Download manifest",
                "URL.createObjectURL",
                "spectrum-feedback.yml",
                "spectrum-request.yml",
                "Request a stable spectrum",
                "Stable spectra preview",
                "secondary-resource-link",
                "stable homotopy category",
                "long-term infinity-categorical foundations",
                "cw49 ID",
                "HomologyAtlasMath",
                "spectrumMathName",
                "basisNameSpoken",
                "basisNameTex",
                "basisSumSpoken",
                "basisSumTex",
                "steenrodOperationTex",
                "conceptualSpectra.every",
            ):
                self.assertTrue(route_contract in review_html, route_contract)
            self.assertNotIn(
                'element("h1", "space-title", spectrum.name.plain)',
                review_html,
            )
            self.assertNotIn(
                'element("th", "", "Sq^" + String(squareDegree))',
                review_html,
            )
            self.assertIn(
                'if (reviewState === "accepted") {\n'
                '          return "Accepted · finalized";',
                review_html,
            )
            self.assertEqual(
                review_html.count(
                    'input.placeholder = "Try “tmf”, “projective”, or a basis name";'
                ),
                1,
            )
            self.assertNotIn("<script src=", review_html)
            self.assertLess(
                review_path.stat().st_size,
                6 * 1024 * 1024,
            )


if __name__ == "__main__":
    unittest.main()
