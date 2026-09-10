import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from homology_db.chromatic import ChromaticDatabase
from homology_db.steenrod import CW49_SPECTRUM_IDS
from scripts.verify_steenrod_release import MAX_ATLAS_BYTES


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "verify_steenrod_release.py"
EXPORTER = ROOT / "scripts" / "export_static_atlas.py"


def acceptance_text(acceptance: dict) -> str:
    return json.dumps(acceptance, indent=2, sort_keys=True) + "\n"


def embedded_atlas(path: Path) -> dict:
    match = re.search(
        r'<script id="atlas-data" type="application/json">(.*?)</script>',
        path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("generated atlas has no embedded data")
    return json.loads(match.group(1))


def spectrum(index: int) -> dict:
    spectrum_id = CW49_SPECTRUM_IDS[index]
    slug = "-".join(
        part
        for part in "".join(
            character if character.isalnum() else "-" for character in spectrum_id
        )
        .casefold()
        .split("-")
        if part
    )
    is_tmf = spectrum_id == "tmf"
    module = {
        "schema_version": "homology-db.steenrod-module/1",
        "module_type": "profile" if is_tmf else "finite_basis",
        "coefficient_field": "F2",
        "category": "stable",
        "grading_convention": "cohomological",
        "suspension_shift": 0,
        "source_snapshot": "cw49-v126.3",
        "review_state": "accepted",
        "evidence": {"review_state": "imported_unreviewed"},
        "content_sha256": f"{index:064x}",
    }
    if is_tmf:
        module["profile"] = {
            "basis": "milnor",
            "truncated": True,
            "p_part": [3, 2, 1],
        }
    else:
        module.update(
            {
                "basis_version": "v1",
                "basis": [
                    {"basis_id": "b0", "name": "x0", "degree": 0, "ordinal": 0}
                ],
                "actions": [],
                "completeness": {"knowledge_state": "exact", "slots": []},
            }
        )
    return {
        "spectrum_id": spectrum_id,
        "slug": slug,
        "name": {"plain": spectrum_id, "tex": ""},
        "object_kind": "ring_spectrum" if is_tmf else "module_spectrum",
        "source_decode_state": "complete",
        "review_state": "accepted",
        "module": module,
    }


def cw49_atlas(spectra: list[dict]) -> dict:
    return {
        "snapshot": {
            "spectrum_source": {"normalization_state": "complete"},
            "source_database_hash_kind": "homology-db.sqlite-logical/1",
            "source_database_sha256": "a" * 64,
        },
        "conceptual_spectra": spectra,
    }


def html_with_atlas(atlas: dict) -> str:
    return (
        '<!doctype html><script id="atlas-data" type="application/json">'
        + json.dumps(atlas, sort_keys=True, separators=(",", ":"))
        + "</script>"
    )


class SteenrodReleaseGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture_directory = tempfile.TemporaryDirectory()
        directory = Path(cls.fixture_directory.name)
        database_path = directory / "chromatic.sqlite3"
        candidate_path = directory / "candidate.html"
        packet_path = directory / "candidate.review.json"
        coverage_path = directory / "candidate.coverage.md"
        acceptance_path = directory / "dan-acceptance.json"
        accepted_path = directory / "accepted.html"
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
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if candidate.returncode != 0:
            raise AssertionError(candidate.stderr)
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
                "spectrum_snapshot_id": projection["spectrum_snapshot"]["snapshot_id"],
                "spectrum_snapshot_manifest_sha256": projection[
                    "spectrum_snapshot"
                ]["manifest_sha256"],
                "spectrum_count": 49,
                "assertion_review_count": projection["assertion_reviews"]["count"],
                "assertion_review_manifest_sha256": projection[
                    "assertion_reviews"
                ]["manifest_sha256"],
                "editorial_admission_count": projection["editorial_admissions"][
                    "count"
                ],
                "editorial_admission_manifest_sha256": projection[
                    "editorial_admissions"
                ]["manifest_sha256"],
                "tmf_profile_module_content_sha256": projection[
                    "editorial_admissions"
                ]["profile_module_content_sha256"],
            },
        }
        acceptance_path.write_text(acceptance_text(acceptance), encoding="utf-8")
        accepted = subprocess.run(
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
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if accepted.returncode != 0:
            raise AssertionError(accepted.stderr)
        cls.valid_atlas_path = accepted_path
        cls.valid_acceptance_path = acceptance_path
        cls.valid_atlas = embedded_atlas(accepted_path)
        cls.valid_acceptance = acceptance

        preview_path = directory / "preview.html"
        preview = subprocess.run(
            [
                sys.executable,
                str(EXPORTER),
                "--database",
                str(database_path),
                "--output",
                str(preview_path),
                "--steenrod-review-candidate",
                "--allow-public-review-preview",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if preview.returncode != 0:
            raise AssertionError(preview.stderr)
        cls.valid_preview_path = preview_path
        cls.valid_preview = embedded_atlas(preview_path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture_directory.cleanup()

    def accepted_fixture(self) -> tuple[dict, dict]:
        return copy.deepcopy(self.valid_atlas), copy.deepcopy(self.valid_acceptance)

    def run_gate(
        self,
        atlas: dict,
        review: dict | None = None,
        *,
        padding_bytes: int = 0,
        allow_public_review_preview: bool = False,
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            atlas_path = directory / "atlas.html"
            review_path = directory / "review.json"
            atlas_path.write_text(
                html_with_atlas(atlas) + (" " * padding_bytes), encoding="utf-8"
            )
            command = [sys.executable, str(GATE), "--atlas", str(atlas_path)]
            if allow_public_review_preview:
                command.append("--allow-public-review-preview")
            if review is not None:
                review_path.write_text(acceptance_text(review), encoding="utf-8")
                command.extend(["--review", str(review_path)])
            return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    def test_space_only_release_does_not_require_a_steenrod_review(self) -> None:
        completed = self.run_gate({"conceptual_spaces": [{"id": "sphere:1"}]})

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["state"], "legacy_space_only")

    def test_null_spectrum_payload_is_not_a_legacy_release(self) -> None:
        completed = self.run_gate(
            {
                "snapshot": {
                    "conceptual_spectrum_count": 0,
                    "spectrum_release_status": "withheld_pending_review",
                },
                "conceptual_spectra": None,
            }
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("conceptual_spectra must be a list", completed.stderr)

    def test_null_spectrum_record_is_rejected_cleanly(self) -> None:
        spectra = [spectrum(index) for index in range(49)]
        spectra[12] = None

        completed = self.run_gate(cw49_atlas(spectra))

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("every spectrum must be an object", completed.stderr)

    def test_empty_spectra_require_an_explicit_withheld_snapshot(self) -> None:
        malformed = self.run_gate({"conceptual_spectra": []})

        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("explicitly withheld", malformed.stderr)

        withheld = self.run_gate(
            {
                "snapshot": {
                    "conceptual_spectrum_count": 0,
                    "spectrum_release_status": "withheld_pending_review",
                },
                "conceptual_spectra": [],
            }
        )

        self.assertEqual(withheld.returncode, 0, withheld.stderr)
        self.assertEqual(json.loads(withheld.stdout)["state"], "withheld_space_only")

    def test_unreviewed_spectrum_release_is_rejected(self) -> None:
        completed = self.run_gate(cw49_atlas([spectrum(0)]))

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("requires exactly 49 spectra", completed.stderr)

    def test_public_review_preview_requires_explicit_gate_flag(self) -> None:
        completed = self.run_gate(copy.deepcopy(self.valid_preview))

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("public review preview is not enabled", completed.stderr)

    def test_exact_public_review_preview_passes_without_acceptance(self) -> None:
        completed = self.run_gate(
            copy.deepcopy(self.valid_preview),
            allow_public_review_preview=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["state"], "public_review_preview")
        self.assertEqual(summary["conceptual_spectrum_count"], 49)
        self.assertEqual(summary["finite_module_count"], 48)
        self.assertEqual(summary["profile_module_count"], 1)
        self.assertNotIn("reviewer", summary)

    def test_public_review_preview_rebuild_is_deterministic(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(GATE),
                "--atlas",
                str(self.valid_preview_path),
                "--allow-public-review-preview",
                "--verify-rebuild",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertTrue(summary["deterministic_rebuild_verified"])
        self.assertRegex(summary["canonical_atlas_sha256"], r"^[0-9a-f]{64}$")

    def test_public_review_preview_preserves_import_evidence_state(self) -> None:
        atlas = copy.deepcopy(self.valid_preview)
        atlas["conceptual_spectra"][0]["module"]["evidence"][
            "review_state"
        ] = "accepted"

        completed = self.run_gate(
            atlas,
            allow_public_review_preview=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("import evidence", completed.stderr)
        self.assertIn("must remain imported_unreviewed", completed.stderr)

    def test_public_review_preview_rejects_finalization_metadata(self) -> None:
        for key in (
            "spectrum_acceptance",
            "spectrum_snapshot",
            "spectrum_database_hash_kind",
            "spectrum_database_sha256",
            "spectrum_materialization",
        ):
            with self.subTest(key=key):
                atlas = copy.deepcopy(self.valid_preview)
                atlas["snapshot"][key] = {"forged": True}

                completed = self.run_gate(
                    atlas,
                    allow_public_review_preview=True,
                )

                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(
                    "must not embed acceptance or finalization metadata",
                    completed.stderr,
                )

    def test_exact_reviewed_cw49_release_passes(self) -> None:
        atlas, review = self.accepted_fixture()

        completed = self.run_gate(atlas, review)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["state"], "reviewed_cw49")
        self.assertEqual(
            summary["candidate_sha256"],
            review["bindings"]["candidate_sha256"],
        )
        self.assertEqual(summary["finite_module_count"], 48)
        self.assertEqual(summary["profile_module_count"], 1)
        self.assertEqual(summary["assertion_review_count"], 5828)
        self.assertEqual(summary["editorial_admission_count"], 5829)
        self.assertEqual(
            summary["spectrum_database_hash_kind"],
            "homology-db.sqlite-logical/2",
        )
        self.assertRegex(summary["spectrum_database_sha256"], r"^[0-9a-f]{64}$")

    def test_deployment_gate_rebuilds_the_accepted_atlas_deterministically(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(GATE),
                "--atlas",
                str(self.valid_atlas_path),
                "--review",
                str(self.valid_acceptance_path),
                "--verify-rebuild",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertTrue(summary["deterministic_rebuild_verified"])
        self.assertRegex(summary["canonical_atlas_sha256"], r"^[0-9a-f]{64}$")

    def test_deployment_rebuild_rejects_inert_wrapper_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            drifted_path = Path(temporary_directory) / "accepted-drifted.html"
            drifted_path.write_bytes(self.valid_atlas_path.read_bytes() + b"\n")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--atlas",
                    str(drifted_path),
                    "--review",
                    str(self.valid_acceptance_path),
                    "--verify-rebuild",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("canonical accepted rebuild", completed.stderr)

    def test_review_for_different_candidate_is_rejected(self) -> None:
        atlas, review = self.accepted_fixture()
        review["bindings"]["candidate_sha256"] = "0" * 64

        completed = self.run_gate(atlas, review)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("binding mismatch for candidate_sha256", completed.stderr)

    def test_wrong_cw49_identity_is_rejected_even_at_the_right_count(self) -> None:
        atlas, review = self.accepted_fixture()
        atlas["conceptual_spectra"][0]["spectrum_id"] = "not-cw49"
        atlas["conceptual_spectra"][0]["slug"] = "not-cw49"

        completed = self.run_gate(atlas, review)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("exact cw49 spectrum identity projection", completed.stderr)

    def test_stale_source_inputs_are_rejected(self) -> None:
        atlas, review = self.accepted_fixture()
        atlas["snapshot"]["source_inputs_sha256"] = "c" * 64

        completed = self.run_gate(atlas, review)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("stale source inputs", completed.stderr)

    def test_fabricated_review_and_admission_counts_are_rejected(self) -> None:
        atlas, review = self.accepted_fixture()
        review["bindings"]["assertion_review_count"] = 5829
        review["bindings"]["editorial_admission_count"] = 5830

        completed = self.run_gate(atlas, review)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("binding mismatch for assertion_review_count", completed.stderr)

    def test_fabricated_review_and_admission_manifests_are_rejected(self) -> None:
        atlas, review = self.accepted_fixture()
        review["bindings"]["assertion_review_manifest_sha256"] = "d" * 64
        review["bindings"]["editorial_admission_manifest_sha256"] = "e" * 64

        completed = self.run_gate(atlas, review)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "binding mismatch for assertion_review_manifest_sha256",
            completed.stderr,
        )

    def test_every_release_axis_is_bound_to_the_acceptance(self) -> None:
        mutations = {
            "spectrum_source_sha256": "1" * 64,
            "source_commit": "2" * 40,
            "source_inputs_sha256": "3" * 64,
            "source_database_hash_kind": "sqlite-file-sha256",
            "source_database_sha256": "4" * 64,
            "review_packet_sha256": "5" * 64,
            "coverage_report_sha256": "6" * 64,
            "spectrum_snapshot_id": "steenrod-cw49-v1-wrong",
            "spectrum_snapshot_manifest_sha256": "7" * 64,
            "tmf_profile_module_content_sha256": "8" * 64,
        }
        for key, value in mutations.items():
            with self.subTest(binding=key):
                atlas, review = self.accepted_fixture()
                review["bindings"][key] = value

                completed = self.run_gate(atlas, review)

                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(f"binding mismatch for {key}", completed.stderr)

    def test_tampered_module_and_download_projection_is_rejected(self) -> None:
        atlas, review = self.accepted_fixture()
        finite = next(
            spectrum
            for spectrum in atlas["conceptual_spectra"]
            if spectrum["module"]["module_type"] == "finite_basis"
            and spectrum["downloads"]["sseq"]["status"] == "ready"
        )
        finite["module"]["content_sha256"] = "f" * 64
        finite["downloads"]["sseq"]["manifest"]["payload_sha256"] = "0" * 64

        completed = self.run_gate(atlas, review)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("exact pinned cw49 projection", completed.stderr)

    def test_tampered_materialized_spectrum_database_is_rejected(self) -> None:
        atlas, review = self.accepted_fixture()
        atlas["snapshot"]["spectrum_database_sha256"] = "0" * 64

        completed = self.run_gate(atlas, review)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("materialized spectrum database", completed.stderr)

    def test_partially_decoded_corpus_is_rejected(self) -> None:
        spectra = [spectrum(index) for index in range(49)]
        spectra[17]["source_decode_state"] = "partial"

        completed = self.run_gate(cw49_atlas(spectra))

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("not completely decoded", completed.stderr)

    def test_incomplete_source_normalization_is_rejected(self) -> None:
        atlas = cw49_atlas([spectrum(index) for index in range(49)])
        atlas["snapshot"]["spectrum_source"]["normalization_state"] = "partial"

        completed = self.run_gate(atlas)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("normalization is incomplete", completed.stderr)

    def test_physical_database_identity_cannot_gate_a_spectrum_release(self) -> None:
        atlas = cw49_atlas([spectrum(index) for index in range(49)])
        atlas["snapshot"]["source_database_hash_kind"] = "sqlite-file-sha256"

        completed = self.run_gate(atlas)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("canonical logical database hash", completed.stderr)

    def test_malformed_logical_database_hash_is_rejected(self) -> None:
        atlas = cw49_atlas([spectrum(index) for index in range(49)])
        atlas["snapshot"]["source_database_sha256"] = "not-a-sha256"

        completed = self.run_gate(atlas)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("valid logical database SHA-256", completed.stderr)

    def test_oversized_artifact_is_rejected(self) -> None:
        completed = self.run_gate(
            {"conceptual_spaces": [{"id": "sphere:1"}]},
            padding_bytes=MAX_ATLAS_BYTES,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(f"{MAX_ATLAS_BYTES // (1024 * 1024)} MiB", completed.stderr)


if __name__ == "__main__":
    unittest.main()
