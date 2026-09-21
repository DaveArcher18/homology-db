"""Guard the six genuinely different records used by the page review slice."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CanonicalSpaceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        html = (ROOT / "dist" / "atlas.html").read_text(encoding="utf-8")
        match = re.search(
            r'<script id="atlas-data" type="application/json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        assert match is not None
        cls.atlas = json.loads(match.group(1))
        cls.spaces = {space["id"]: space for space in cls.atlas["conceptual_spaces"]}

    def test_review_records_cover_distinct_states(self) -> None:
        self.assertEqual(len(self.spaces), 194)
        review_ids = {
            "sphere:0",
            "real_projective_space:4",
            "torus:2",
            "four_manifold:k3",
            "connected_sum:s2xs1-sum-19",
            "orientable_surface:26",
        }
        self.assertTrue(review_ids <= self.spaces.keys())
        computed = set(self.atlas["computed_rings"]["space_ids"])
        self.assertIn("four_manifold:k3", computed)
        self.assertIn("real_projective_space:4", computed)
        self.assertIn("torus:2", computed)
        self.assertNotIn("sphere:0", computed)
        self.assertNotIn("orientable_surface:26", computed)
        self.assertTrue(self.spaces["sphere:0"]["cohomology"])
        self.assertEqual(self.spaces["orientable_surface:26"]["cohomology"], [])

    def test_k3_direct_sum_and_large_basis(self) -> None:
        k3 = self.spaces["four_manifold:k3"]
        for coefficient in ("Z", "F2", "F3", "F5", "F7", "F11"):
            row = next(
                row for row in k3["homology"]
                if row["coefficient_ring"] == coefficient
                and row["reduced"] is False
                and row["degree"] == 2
            )
            self.assertEqual(row["knowledge_state"], "exact")
            if coefficient == "Z":
                self.assertEqual(row["group"]["free_rank"], 22)
            else:
                self.assertEqual(row["group"]["dimension"], 22)
        large = self.spaces["connected_sum:s2xs1-sum-19"]
        self.assertEqual(
            max(len(record["algebra"]["basis"]) for record in large["cohomology"]),
            40,
        )


if __name__ == "__main__":
    unittest.main()
