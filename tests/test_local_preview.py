from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from homology_db.preview import PreviewDatabase, Tools


ROOT = Path(__file__).resolve().parents[1]


class LocalPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.database_path = Path(self.temporary_directory.name) / "preview.sqlite3"
        self.snapshot_id = PreviewDatabase.build(self.database_path)
        self.tools = Tools(self.database_path)

    def test_builds_the_fixed_sixty_subject_snapshot_deterministically(self) -> None:
        self.assertEqual(self.tools.corpus_summary()["subject_count"], 60)
        second_path = Path(self.temporary_directory.name) / "second.sqlite3"
        self.assertEqual(PreviewDatabase.build(second_path), self.snapshot_id)

    def test_klein_bottle_integral_homology_is_grounded(self) -> None:
        answer = self.tools.read_homology("Klein bottle", coefficient="Z")
        self.assertEqual(answer["outcome"], "selected")
        self.assertEqual(
            [(group["degree"], group["value"]["free_rank"], group["value"]["torsion_orders"])
             for group in answer["groups"]],
            [(0, 1, []), (1, 1, [2]), (2, 0, [])],
        )
        self.assertTrue(all(group["assertion_id"] for group in answer["groups"]))
        self.assertTrue(all(group["evidence_id"] for group in answer["groups"]))

    def test_rp4_mod_two_homology_has_one_generator_in_each_degree(self) -> None:
        answer = self.tools.read_homology("RP^4", coefficient="F2")
        self.assertEqual(
            [(group["degree"], group["value"]["dimension"]) for group in answer["groups"]],
            [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)],
        )

    def test_reduced_mod_five_lens_homology_includes_tor_degree(self) -> None:
        answer = self.tools.read_homology("L(5,2)", coefficient="F5", reduced=True)
        self.assertEqual(
            [(group["degree"], group["value"]["dimension"]) for group in answer["groups"]],
            [(0, 0), (1, 1), (2, 1), (3, 1)],
        )

    def test_structured_torsion_query_returns_proven_examples(self) -> None:
        answer = self.tools.query_examples({"degree": 1, "torsion_prime": 5, "limit": 20})
        self.assertEqual(answer["outcome"], "proven_matches")
        self.assertEqual(
            {match["space_id"] for match in answer["matches"]},
            {"lens:5:1", "lens:5:2", "lens:10:1"},
        )
        self.assertEqual(answer["unresolved_candidates"], [])

    def test_evidence_expansion_discloses_missing_capabilities(self) -> None:
        homology = self.tools.read_homology("Klein bottle")
        evidence_id = homology["groups"][1]["evidence_id"]
        answer = self.tools.expand_evidence([evidence_id])
        self.assertEqual(answer["outcome"], "complete")
        self.assertIn("not_computed", answer["evidence"][0]["representatives_state"])
        self.assertEqual(
            answer["evidence"][0]["induced_maps_state"],
            "identity_only;nonidentity_not_computed",
        )

    def test_unsupported_coefficient_is_not_reported_as_absent_or_zero(self) -> None:
        answer = self.tools.read_homology("S^2", coefficient="Q")
        self.assertEqual(answer["outcome"], "unsupported_coefficient")
        self.assertNotIn("groups", answer)

    def test_unknown_subject_preserves_the_resolver_outcome(self) -> None:
        answer = self.tools.call({
            "tool": "read_homology",
            "arguments": {"subject": "definitely not a known space", "coefficient": "Z"},
        })
        self.assertEqual(answer["outcome"], "subject_not_resolved")
        self.assertEqual(answer["resolution"]["outcome"], "not_found")
        self.assertNotIn("groups", answer)

    def test_malformed_agent_envelope_returns_a_typed_error(self) -> None:
        answer = self.tools.call(["read_homology"])  # type: ignore[arg-type]
        self.assertEqual(answer["outcome"], "invalid_request")
        self.assertIn("JSON object", answer["reason"])

    def test_cli_executes_the_same_json_tool_interface(self) -> None:
        request = {"tool": "read_homology", "arguments": {"subject": "S^2", "coefficient": "Z"}}
        completed = subprocess.run(
            [sys.executable, "-m", "homology_db", "--db", str(self.database_path),
             "tool", json.dumps(request)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        answer = json.loads(completed.stdout)
        self.assertEqual(answer["outcome"], "selected")
        self.assertEqual(answer["groups"][2]["value"]["display"], "Z")

    def test_demo_is_a_concise_human_mathematical_tour(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "homology_db", "--db", str(self.database_path), "demo"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn("Quick mathematical tour", completed.stdout)
        self.assertIn("Klein bottle: H_0 = Z; H_1 = Z + Z/2; H_2 = 0", completed.stdout)
        self.assertIn("Agent interface", completed.stdout)
        self.assertLess(len(completed.stdout.splitlines()), 40)


if __name__ == "__main__":
    unittest.main()
