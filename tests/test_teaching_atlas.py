"""Teaching coverage is derived, source-bound and independent of human review."""

import copy
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from homology_db.chromatic import ChromaticDatabase
from scripts.export_static_atlas import build_read_model, validate_read_model


class TeachingAtlasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.database = Path(cls.directory.name) / "atlas.sqlite3"
        ChromaticDatabase.build(cls.database)
        cls.atlas = build_read_model(cls.database)

    def test_exact_coverage_without_core_inflation(self):
        entries = self.atlas["teaching"]["entries"]
        self.assertEqual(len(entries), 56)
        self.assertEqual(Counter(e["coverage"]["kind"] for e in entries),
                         {"general_family": 10, "core_ring": 4, "extension_ring": 2,
                          "computed_ring": 13, "homology_only": 27})
        self.assertEqual(sum(s["classical_core"] for s in self.atlas["conceptual_spaces"]), 13)
        self.assertEqual(len(self.atlas["classical"]["space_ids"]), 15)
        self.assertEqual(len(self.atlas["classical"]["core_space_ids"]), 13)
        self.assertTrue(all(e["coverage"]["human_review_state"] == "human_review_pending" for e in entries))
        self.assertTrue(all(e["space_slug"] for e in entries))

    def test_exposition_coverage_and_snapshot_binding_reject_drift(self):
        for mutate in (
            lambda a: a["teaching"]["entries"][0].update(introduction="invented"),
            lambda a: a["teaching"]["entries"][0]["coverage"].update(kind="invented"),
            lambda a: a["teaching"].update(content_sha256="0" * 64),
            lambda a: a["snapshot"].update(teaching_sha256="0" * 64),
            lambda a: a.pop("teaching"),
        ):
            atlas = copy.deepcopy(self.atlas)
            mutate(atlas)
            with self.assertRaisesRegex(ValueError, "teaching"):
                validate_read_model(atlas)

    def test_teaching_projection_is_deterministic(self):
        other = build_read_model(self.database)
        self.assertEqual(other["teaching"], self.atlas["teaching"])
        self.assertEqual(other["snapshot"]["teaching_sha256"], self.atlas["teaching"]["content_sha256"])


if __name__ == "__main__":
    unittest.main()
