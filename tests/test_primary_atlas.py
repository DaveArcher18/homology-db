from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from homology_db.chromatic import ChromaticDatabase
from homology_db.computed_rings import load_computed_rings, primary_atlas_space_ids
from scripts.build_static_bundle import partition
from scripts.export_static_atlas import build_read_model


class PrimaryAtlasCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.database_path = Path(cls.temporary.name) / "atlas.sqlite3"
        ChromaticDatabase.build(cls.database_path)
        cls.corpus = load_computed_rings()
        cls.atlas = build_read_model(cls.database_path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_eligibility_is_exactly_imported_model_provenance(self) -> None:
        eligible = primary_atlas_space_ids(self.corpus)
        self.assertEqual(eligible, sorted(self.corpus["models"]))
        self.assertEqual(eligible, sorted(self.corpus["homology"]))
        self.assertEqual(self.atlas["primary_atlas"]["space_ids"], eligible)
        self.assertEqual(
            self.atlas["primary_atlas"]["eligibility_rule"],
            "has_gabriel_imported_computational_model_provenance",
        )

    def test_boundary_keeps_withheld_computation_and_excludes_legacy_only_data(self) -> None:
        spaces = {space["id"]: space for space in self.atlas["conceptual_spaces"]}

        self.assertTrue(spaces["torus:2"]["primary_atlas_eligible"])
        self.assertTrue(spaces["moore:11:2"]["primary_atlas_eligible"])

        withheld_ids = sorted(set(self.corpus["homology"]) - set(self.corpus["records"]))
        self.assertEqual(len(withheld_ids), 7)
        self.assertEqual(
            withheld_ids,
            [
                "connected_sum:s2-twist-s1-sum-20",
                "connected_sum:s2xs1-sum-20",
                "hadamard_torsion_complex:32",
                "hom_complex:c6-compl-k5-small",
                "orientable_surface:26",
                "random_2_complex:25",
                "sphere:0",
            ],
        )
        for space_id in withheld_ids:
            self.assertTrue(spaces[space_id]["primary_atlas_eligible"])
            self.assertFalse(
                any(
                    record["provenance"]["kind"] == "imported_computation"
                    for record in spaces[space_id]["cohomology"]
                )
            )

        self.assertEqual(set(spaces), set(primary_atlas_space_ids(self.corpus)))
        self.assertNotIn("grassmannian:2:4:c", spaces)
        self.assertTrue(all(space["primary_atlas_eligible"] for space in spaces.values()))

    def test_only_primary_space_documents_are_shipped(self) -> None:
        documents = partition(self.atlas)
        catalog = documents["data/catalog.json"][1]
        self.assertEqual(
            len(catalog["conceptual_spaces"]),
            len(primary_atlas_space_ids(self.corpus)),
        )
        self.assertIn("data/spaces/orientable-surface-26.json", documents)
        self.assertNotIn("data/spaces/grassmannian-2-4-c.json", documents)
        self.assertEqual(
            sum(kind == "space" for kind, _payload in documents.values()),
            len(self.atlas["conceptual_spaces"]),
        )


if __name__ == "__main__":
    unittest.main()
