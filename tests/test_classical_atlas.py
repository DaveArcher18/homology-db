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
        self.assertEqual(len(recorded), 189)
        for space in recorded:
            sourced = {row["coefficient"] for row in space["cohomology"]
                       if row["provenance"]["kind"] == "literature"}
            computed = {row["coefficient"] for row in space["cohomology"]
                        if row["provenance"]["kind"] == "external_engine_computation"}
            self.assertTrue(sourced or computed)
            if sourced:
                self.assertEqual(sourced, {"Q", "F2", "F3", "F5", "F7"})
            if computed:
                self.assertEqual(computed, {"Z", "Q", "F2", "F3", "F5", "F7"})
            for record in space["cohomology"]:
                rows = {
                    row["degree"]: row["group"]
                    for row in space["homology"]
                    if not row["reduced"] and row["coefficient_ring"] == record["coefficient"]
                }
                for group in record["groups"]:
                    with self.subTest(space=space["id"], coefficient=record["coefficient"],
                                      degree=group["degree"]):
                        degree = group["degree"]
                        if record["coefficient"] != "Z":
                            self.assertEqual(group["dimension"], rows[degree]["dimension"])
                            continue
                        # Universal coefficients: the integral ring in degree n must have the
                        # free rank of H_n and the torsion of H_{n-1}, checked against this
                        # repository's own cellular homology rather than the imported record.
                        self.assertEqual(group["free_rank"], rows[degree]["free_rank"])
                        below = rows[degree - 1]["torsion_orders"] if degree else []
                        self.assertEqual(group["torsion_orders"], sorted(below))

    def test_noncore_and_integral_absence_is_not_zero(self):
        noncore = [space for space in self.atlas["conceptual_spaces"] if not space["classical_core"]]
        self.assertEqual(len(noncore), 199)
        self.assertEqual(sum(not space["cohomology"] for space in noncore), 23)
        for space in self.atlas["conceptual_spaces"]:
            self.assertTrue(any(row["coefficient_ring"] == "Z" for row in space["homology"]))
            integral = [row for row in space["cohomology"] if row["coefficient"] == "Z"]
            computed = [row for row in space["cohomology"]
                        if row["provenance"]["kind"] == "external_engine_computation"]
            self.assertEqual(bool(integral), bool(computed))
            for row in integral:
                self.assertEqual(row["provenance"]["kind"], "external_engine_computation")
                self.assertEqual(row["provenance"]["review_state"], "imported_unreviewed")
        sourced_only = [space for space in self.atlas["conceptual_spaces"]
                        if space["cohomology"] and not any(
                            row["provenance"]["kind"] == "external_engine_computation"
                            for row in space["cohomology"])]
        self.assertEqual(len(sourced_only), 3)
        for space in sourced_only:
            self.assertFalse(any(row["coefficient"] == "Z" for row in space["cohomology"]))

    def test_a_cited_text_takes_precedence_over_a_machine_computation(self):
        """Where both exist, the sourced ring leads and the computed one corroborates."""
        shared = 0
        for space in self.atlas["conceptual_spaces"]:
            by_coefficient = {}
            for record in space["cohomology"]:
                by_coefficient.setdefault(record["coefficient"], []).append(record)
            for coefficient, entries in by_coefficient.items():
                kinds = [record["provenance"]["kind"] for record in entries]
                if "literature" not in kinds or len(entries) < 2:
                    continue
                shared += 1
                with self.subTest(space=space["id"], coefficient=coefficient):
                    # literature first, so a consumer reading in order gets the citation
                    self.assertEqual(kinds[0], "literature")
                    self.assertIn("external_engine_computation", kinds[1:])
                    # and the records must actually agree before either is preferred
                    for record in entries[1:]:
                        self.assertEqual(record["groups"], entries[0]["groups"])
        self.assertEqual(shared, 60)

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
            space = next(space for space in atlas["conceptual_spaces"]
                         if space["id"] == "sphere_wedge:2:4")
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
