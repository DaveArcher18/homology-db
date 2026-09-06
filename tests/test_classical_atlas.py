"""Cross-check sourced cohomology against the independent homology projection."""

import copy
import tempfile
import unittest
from pathlib import Path

from homology_db.chromatic import ChromaticDatabase
from scripts.export_static_atlas import build_read_model, validate_read_model


class ClassicalAtlasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.database = Path(cls.directory.name) / "atlas.sqlite3"
        ChromaticDatabase.build(cls.database)
        cls.atlas = build_read_model(cls.database)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_five_field_dimensions_match_independent_cellular_homology(self):
        core = [space for space in self.atlas["conceptual_spaces"] if space["classical_core"]]
        self.assertEqual(len(core), 13)
        self.assertEqual(self.atlas["classical"]["record_count"], 75)
        recorded = [space for space in self.atlas["conceptual_spaces"] if space["cohomology"]]
        self.assertEqual(len(recorded), 15)
        for space in recorded:
            self.assertEqual({row["coefficient"] for row in space["cohomology"]},
                             {"Q", "F2", "F3", "F5", "F7"})
            for record in space["cohomology"]:
                homology = {
                    row["degree"]: row["group"]["dimension"]
                    for row in space["homology"]
                    if not row["reduced"] and row["coefficient_ring"] == record["coefficient"]
                }
                for group in record["groups"]:
                    with self.subTest(space=space["id"], coefficient=record["coefficient"],
                                      degree=group["degree"]):
                        self.assertEqual(group["dimension"], homology[group["degree"]])

    def test_noncore_and_integral_absence_is_not_zero(self):
        noncore = [space for space in self.atlas["conceptual_spaces"] if not space["classical_core"]]
        self.assertEqual(len(noncore), 29)
        self.assertEqual(sum(not space["cohomology"] for space in noncore), 27)
        for space in self.atlas["conceptual_spaces"]:
            self.assertTrue(any(row["coefficient_ring"] == "Z" for row in space["homology"]))
            self.assertFalse(any(row["coefficient"] == "Z" for row in space["cohomology"]))

    def test_classical_content_and_source_catalog_are_bound(self):
        for mutate in (
            lambda atlas: atlas["classical"].update(content_sha256="0" * 64),
            lambda atlas: atlas["classical"].update(sources={}),
            lambda atlas: atlas["snapshot"]["classical_cohomology"].update(record_count=0),
        ):
            atlas = copy.deepcopy(self.atlas)
            mutate(atlas)
            with self.assertRaises(ValueError):
                validate_read_model(atlas)

    def test_classical_projection_is_deterministic_and_definitions_are_exposition(self):
        other = build_read_model(self.database)
        self.assertEqual(self.atlas["classical"], other["classical"])
        required = {"ordinary-cohomology", "cup-product", "generator-degree",
                    "ring-relation", "coefficient-field"}
        definitions = {definition["id"]: definition for definition in self.atlas["definitions"]}
        self.assertTrue(required <= definitions.keys())
        self.assertTrue(all(not definitions[key]["assertion_evidence"] for key in required))

    def test_rational_rows_reject_missing_values_and_unbound_derivations(self):
        for mutation in ("missing", "dimension", "input"):
            atlas = copy.deepcopy(self.atlas)
            space = next(space for space in atlas["conceptual_spaces"] if space["id"] == "point")
            rational = next(row for row in space["homology"] if row["coefficient_ring"] == "Q")
            if mutation == "missing":
                space["homology"] = [row for row in space["homology"] if row["coefficient_ring"] != "Q"]
            elif mutation == "dimension":
                rational["group"]["dimension"] = 999
            else:
                rational["derivation"]["input_assertion_id"] = "missing-assertion"
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, "rational homology"):
                validate_read_model(atlas)

    def test_matching_but_false_metadata_is_rejected(self):
        atlas = copy.deepcopy(self.atlas)
        atlas["classical"]["record_count"] = 0
        atlas["snapshot"]["classical_cohomology"]["record_count"] = 0
        with self.assertRaisesRegex(ValueError, "classical metadata"):
            validate_read_model(atlas)


if __name__ == "__main__":
    unittest.main()
