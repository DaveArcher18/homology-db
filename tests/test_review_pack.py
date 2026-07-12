from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "qa" / "review" / "questions-v1.json"


class ReviewPackTests(unittest.TestCase):
    def test_review_pack_is_fixed_complete_and_diverse(self) -> None:
        data = json.loads(PACK.read_text(encoding="utf-8"))
        questions = data["questions"]
        self.assertEqual(data["snapshot_policy"], "one_snapshot_only")
        self.assertEqual([item["id"] for item in questions], [f"R{index:02d}" for index in range(1, 13)])
        self.assertEqual(len({item["question"] for item in questions}), 12)
        self.assertGreaterEqual(len({item["category"] for item in questions}), 8)
        self.assertIn("unsupported_input", {item["category"] for item in questions})
        self.assertIn("missing_subject", {item["category"] for item in questions})


if __name__ == "__main__":
    unittest.main()
