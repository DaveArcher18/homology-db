from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from homology_db.preview import PreviewDatabase


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "qa" / "audits" / "preview-adversarial-2026-07-12.json"


class AdversarialAuditReplayTests(unittest.TestCase):
    def test_recorded_public_operation_cases_replay_exactly(self) -> None:
        audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(audit["schema_version"], "homology-db.preview-adversarial-audit/1")
        self.assertEqual(len(audit["cases"]), 72)
        self.assertEqual(len({case["id"] for case in audit["cases"]}), 72)
        self.assertEqual(
            hashlib.sha256((ROOT / "homology_db" / "preview.py").read_bytes()).hexdigest(),
            audit["metadata"]["preview_module_sha256"],
        )
        self.assertEqual(
            hashlib.sha256((ROOT / "tests" / "test_local_preview.py").read_bytes()).hexdigest(),
            audit["metadata"]["preview_test_sha256"],
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "preview.sqlite3"
            snapshot_id = PreviewDatabase.build(database_path)
            self.assertEqual(snapshot_id, audit["metadata"]["expected_snapshot_id"])
            for case in audit["cases"]:
                with self.subTest(case_id=case["id"]):
                    answer, exit_code = self._invoke(database_path, case)
                    self.assertEqual(answer.get("snapshot_id"), snapshot_id)
                    self._assert_expected(answer, exit_code, case["expected"])

    @staticmethod
    def _invoke(database_path: Path, case: dict[str, object]) -> tuple[dict[str, object], int]:
        payload = case.get("raw_cli_input")
        if payload is None:
            payload = json.dumps(case["request"], separators=(",", ":"))
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "homology_db",
                "--db",
                str(database_path),
                "tool",
                str(payload),
            ],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        if completed.stderr:
            raise AssertionError(f"unexpected stderr: {completed.stderr}")
        return json.loads(completed.stdout), completed.returncode

    def _assert_expected(
        self,
        answer: dict[str, object],
        exit_code: int,
        expected: dict[str, object],
    ) -> None:
        self.assertEqual(exit_code, expected["exit_code"])
        for key in (
            "outcome",
            "reason",
            "tool",
            "reduced",
            "total_matches",
            "truncated",
            "coverage",
            "missing_evidence_ids",
            "unknown_fields",
        ):
            if key in expected:
                self.assertEqual(answer.get(key), expected[key])
        if "candidate_space_ids" in expected:
            self.assertEqual(
                [candidate["space_id"] for candidate in answer.get("candidates", [])],
                expected["candidate_space_ids"],
            )
        if "reason_prefix" in expected:
            self.assertTrue(str(answer.get("reason", "")).startswith(expected["reason_prefix"]))
        if "group_count" in expected:
            self.assertEqual(len(answer.get("groups", [])), expected["group_count"])
        if "match_count" in expected:
            self.assertEqual(len(answer.get("matches", [])), expected["match_count"])
        if "evidence_count" in expected:
            self.assertEqual(len(answer.get("evidence", [])), expected["evidence_count"])
        if expected.get("all_matches_have_assertion_id"):
            self.assertTrue(all(match.get("assertion_id") for match in answer["matches"]))
        if expected.get("all_matches_have_evidence_id"):
            self.assertTrue(all(match.get("evidence_id") for match in answer["matches"]))


if __name__ == "__main__":
    unittest.main()
