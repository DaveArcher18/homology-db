"""The imported ring corpus must re-derive what it can and refuse to overclaim."""

import copy
import json
import unittest
from pathlib import Path

from homology_db.cohomology_rings import (
    check_corroborating_records,
    validate_cohomology_ring_record,
)
from homology_db.computed_rings import (
    COMPUTED_RING_SOURCES,
    canonical_facets,
    facets_sha256,
    load_computed_rings,
    validate_simplicial_model,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "computed-rings-v1"


class ComputedRingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load_computed_rings()
        cls.model = json.loads((CORPUS / "triangulations" / "orientable_surface-3.json").read_text())

    def test_corpus_covers_every_surface_over_every_coefficient(self):
        self.assertEqual(len(self.corpus["models"]), 11)
        self.assertEqual(sum(len(v) for v in self.corpus["records"].values()), 66)
        for space_id, entries in self.corpus["records"].items():
            self.assertEqual(
                sorted(record["coefficient"] for record in entries),
                sorted(["Z", "Q", "F2", "F3", "F5", "F7"]),
            )
            for record in entries:
                self.assertEqual(record["provenance"]["review_state"], "imported_unreviewed")
                self.assertEqual(record["provenance"]["model_id"],
                                 self.corpus["models"][space_id]["model_id"])

    def test_models_are_re_derived_not_trusted(self):
        summary = validate_simplicial_model(self.model)
        self.assertEqual(summary["f_vector"], [15, 57, 38])
        # Euler characteristic of the genus-three orientable surface is 2 - 2g.
        vertices, edges, faces = summary["f_vector"]
        self.assertEqual(vertices - edges + faces, -4)
        self.assertEqual(facets_sha256(canonical_facets(self.model["facets"])),
                         self.model["facets_sha256"])

    def test_tampered_model_is_rejected(self):
        for mutate, message in (
            (lambda m: m.update(facets_sha256="0" * 64), "recomputed facet hash"),
            (lambda m: m.update(vertices=99), "vertex count"),
            (lambda m: m["facets"].reverse(), "canonical order"),
            (lambda m: m["facets"].append(m["facets"][0]), "repeats a facet"),
            (lambda m: m.update(canonicalization="other/1"), "canonicalization"),
            (lambda m: m.update(schema_version="other/1"), "schema version"),
        ):
            model = copy.deepcopy(self.model)
            mutate(model)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_simplicial_model(model)

    def test_a_non_complex_is_rejected(self):
        model = copy.deepcopy(self.model)
        # Drop one triangle's vertex so the boundary no longer squares to zero.
        model["facets"] = [f for f in model["facets"] if len(f) == 3]
        model["facets"][0] = [model["facets"][0][0], model["facets"][0][1], 99]
        model["facets"] = sorted(sorted(f) for f in model["facets"])
        model["facets_sha256"] = facets_sha256([tuple(f) for f in model["facets"]])
        model["vertices"] = len({v for f in model["facets"] for v in f})
        with self.assertRaises(ValueError):
            validate_simplicial_model(model)

    def test_importing_is_never_promoted_into_review(self):
        record = copy.deepcopy(next(iter(self.corpus["records"].values()))[0])
        record["provenance"]["review_state"] = "human_reviewed"
        with self.assertRaisesRegex(ValueError, "promoted review state"):
            validate_cohomology_ring_record(record, COMPUTED_RING_SOURCES)

    def test_ring_axioms_are_enforced_on_imported_tables(self):
        base = copy.deepcopy(self.corpus["records"]["orientable_surface:2"][0])
        self.assertEqual(base["coefficient"], "Z")
        for mutate, message in (
            (lambda r: r["algebra"]["products"][0]["result"][0].update(coefficient=3),
             "graded commutativity"),
            (lambda r: r["algebra"]["products"][0].update(right=r["algebra"]["products"][0]["left"]),
             "grading|commutativity|unique ordered"),
            (lambda r: r["groups"][1].update(free_rank=99), "additive groups"),
            (lambda r: r["coverage"].update(upper_vanishing_starts_at=99), "upper vanishing"),
            (lambda r: r["sources"].clear(), "cite its evidence"),
            (lambda r: r["algebra"]["basis"][1].update(degree=99), "grading|coverage|additive"),
        ):
            record = copy.deepcopy(base)
            mutate(record)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_cohomology_ring_record(record, COMPUTED_RING_SOURCES)

    def test_corroborating_records_must_agree_and_are_not_merged(self):
        torus = self.corpus["records"]["torus:2"]
        from homology_db.classical import classical_records
        merged = {"torus:2": list(torus) + classical_records()["torus:2"]}
        slots = check_corroborating_records(merged)
        self.assertEqual(len(slots), 5)
        for slot in slots:
            self.assertEqual(slot["provenance_kinds"],
                             ["external_engine_computation", "literature"])
            self.assertEqual(len(slot["record_ids"]), 2)
        conflicted = copy.deepcopy(merged)
        field = next(r for r in conflicted["torus:2"]
                     if r["coefficient"] == "F2" and r["provenance"]["kind"] == "literature")
        field["groups"][1]["dimension"] = 99
        with self.assertRaisesRegex(ValueError, "disagree on the additive groups"):
            check_corroborating_records(conflicted)


if __name__ == "__main__":
    unittest.main()
