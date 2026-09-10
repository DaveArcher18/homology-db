"""The imported ring corpus must re-derive what it can and refuse to overclaim."""

import copy
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from homology_db.cohomology_rings import (
    check_corroborating_records,
    validate_cohomology_ring_record,
)
from homology_db.computed_rings import (
    COMPUTED_RING_SOURCES,
    compare_homology_to_owned,
    validate_computed_homology_record,
    canonical_facets,
    facets_sha256,
    load_computed_rings,
    validate_simplicial_model,
)

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
CORPUS = ROOT / "corpus" / "computed-rings-v1"


class ComputedRingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load_computed_rings()
        cls.model = json.loads((CORPUS / "triangulations" / "orientable_surface-3.json").read_text())

    def test_corpus_covers_every_surface_over_every_coefficient(self):
        self.assertEqual(len(self.corpus["models"]), 172)
        self.assertEqual(sum(len(v) for v in self.corpus["records"].values()), 990)
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
        base = copy.deepcopy(next(
            record for record in self.corpus["records"]["orientable_surface:2"]
            if record["coefficient"] == "Z"))
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

    def test_basis_names_follow_the_shared_display_convention(self):
        """Renaming these silently once left the atlas printing raw ids like b1_1.

        static_atlas/presentation.js turns x<degree> and x<degree>_<index> into a
        subscripted name, the same way the Steenrod modules are displayed. A basis
        id that does not match that shape falls through to its raw text, so the
        producer's names are kept rather than renumbered on import.
        """
        pattern = re.compile(r"^(?:1|x\d+(?:_\d+)?)$")
        for space_id, entries in self.corpus["records"].items():
            for record in entries:
                for item in record["algebra"]["basis"]:
                    with self.subTest(space=space_id, basis=item["id"]):
                        self.assertRegex(item["id"], pattern)
                degrees = {}
                for item in record["algebra"]["basis"]:
                    degrees.setdefault(item["degree"], []).append(item["id"])
                for degree, ids in degrees.items():
                    if degree and len(ids) > 1:
                        # indices are 1-based and dense, matching the display parser
                        # (sorted numerically: x1_10 must not sort before x1_2)
                        self.assertEqual(
                            sorted(ids, key=lambda name: int(name.split("_")[1])),
                            [f"x{degree}_{i + 1}" for i in range(len(ids))])

    def test_cohomology_vanishes_above_the_dimension_and_says_so(self):
        """A finite complex has no cohomology above its dimension, so every record
        here is exhaustive and must be displayed as such.

        The display check previously demanded a `dimension` on every group, which
        integral records do not carry, so integral rings were shown as "recorded
        degrees only" -- understating a vanishing the record does establish.
        """
        for space_id, entries in self.corpus["records"].items():
            for record in entries:
                through = record["coverage"]["through_degree"]
                with self.subTest(space=space_id, coefficient=record["coefficient"]):
                    self.assertEqual(record["coverage"]["kind"], "complete_finite")
                    self.assertEqual(record["coverage"]["upper_vanishing_starts_at"], through + 1)
                    # The coverage bound is the model's own dimension, not a
                    # corpus-wide constant: this corpus now holds 3-manifolds too.
                    self.assertEqual(
                        through,
                        len(self.corpus["models"][space_id]["f_vector"]) - 1,
                        "coverage must reach exactly the model's dimension",
                    )
                    self.assertEqual([g["degree"] for g in record["groups"]],
                                     list(range(through + 1)))

    @unittest.skipUnless(NODE, "node is required to exercise the shipped display code")
    def test_the_shipped_display_states_vanishing_for_every_coefficient(self):
        script = """
        const assert = require('node:assert/strict');
        const p = require('./static_atlas/presentation.js');
        const field = {coverage:{kind:'complete_finite',through_degree:2,upper_vanishing_starts_at:3},
                       knowledge_state:'exact',
                       groups:[{degree:0,dimension:1},{degree:1,dimension:4},{degree:2,dimension:1}]};
        const integral = {coverage:{kind:'complete_finite',through_degree:2,upper_vanishing_starts_at:3},
                          knowledge_state:'exact',
                          groups:[{degree:0,free_rank:1,torsion_orders:[]},
                                  {degree:1,free_rank:4,torsion_orders:[]},
                                  {degree:2,free_rank:0,torsion_orders:[2]}]};
        assert.equal(p.cohomologyCoveragePresentation(field).complete, true);
        assert.equal(p.cohomologyCoveragePresentation(integral).complete, true,
          'an integral record must state its vanishing too');
        const partial = {...integral, groups:[integral.groups[0], integral.groups[2]]};
        assert.equal(p.cohomologyCoveragePresentation(partial).complete, false,
          'a gap in the recorded degrees must not claim vanishing');
        """
        subprocess.run([NODE, "-e", script], cwd=ROOT, check=True)

    def test_imported_homology_covers_every_surface_and_coefficient(self):
        homology = self.corpus["homology"]
        # Rings imply homology, not the reverse: a space whose upstream table was
        # incomplete, or whose structure constants left Z, carries homology alone.
        self.assertLessEqual(set(self.corpus["records"]), set(homology))
        self.assertEqual(sorted(set(homology) - set(self.corpus["records"])), [
            "connected_sum:s2-twist-s1-sum-20", "connected_sum:s2xs1-sum-20",
            "four_manifold:k3", "hadamard_torsion_complex:32",
            "hom_complex:c6-compl-k5-small", "orientable_surface:26",
            "random_2_complex:25",
        ])
        self.assertEqual(sum(len(v) for v in homology.values()), 1032)
        for entries in homology.values():
            self.assertEqual(sorted(record["coefficient"] for record in entries),
                             sorted(["Z", "Q", "F2", "F3", "F5", "F7"]))

    def test_imported_homology_matches_this_repositorys_own(self):
        """The point of importing it is that it could disagree. It must not."""
        import json as _json
        import sqlite3
        import tempfile
        from homology_db.chromatic import build_database

        database = Path(tempfile.mkdtemp()) / "chromatic.sqlite3"
        build_database(database)
        connection = sqlite3.connect(database)
        checked = 0
        for space_id, entries in self.corpus["homology"].items():
            for record in entries:
                coefficient = record["coefficient"]
                stored = "Z" if coefficient == "Q" else coefficient
                rows = connection.execute(
                    "SELECT degree, free_rank, torsion_json FROM homology "
                    "WHERE space_id=? AND coefficient=? AND reduced=0 ORDER BY degree",
                    (space_id, stored)).fetchall()
                self.assertTrue(rows, f"no owned homology for {space_id}")
                if coefficient == "Z":
                    owned = [{"degree": d, "free_rank": f,
                              "torsion_orders": _json.loads(t)} for d, f, t in rows]
                elif coefficient == "Q":
                    owned = [{"degree": d, "dimension": f} for d, f, _ in rows]
                else:
                    owned = [{"degree": d, "dimension": f} for d, f, _ in rows]
                with self.subTest(space=space_id, coefficient=coefficient):
                    self.assertEqual(record["groups"], owned)
                checked += 1
        connection.close()
        database.unlink()
        self.assertEqual(checked, 1032)

    def test_a_disagreeing_homology_is_a_conflict_not_a_ranking(self):
        imported = {("orientable_surface:2", "Z"): [{"degree": 0, "free_rank": 1,
                                                     "torsion_orders": []}]}
        self.assertEqual(compare_homology_to_owned(imported, dict(imported)),
                         [{"space_id": "orientable_surface:2", "coefficient": "Z"}])
        owned = {("orientable_surface:2", "Z"): [{"degree": 0, "free_rank": 2,
                                                  "torsion_orders": []}]}
        with self.assertRaisesRegex(ValueError, "model binding is in conflict"):
            compare_homology_to_owned(imported, owned)
        with self.assertRaisesRegex(ValueError, "no owned rows"):
            compare_homology_to_owned(imported, {})

    def test_homology_records_are_internally_checked(self):
        base = copy.deepcopy(next(
            record for record in self.corpus["homology"]["nonorientable_surface:3"]
            if record["coefficient"] == "Z"))
        for mutate, message in (
            (lambda r: r["groups"].pop(1), "dense and ordered"),
            (lambda r: r["groups"][1].update(free_rank=-1), "free rank"),
            (lambda r: r["groups"][1].update(dimension=1), "not a dimension"),
            (lambda r: r["provenance"].update(review_state="human_reviewed"), "promoted"),
            (lambda r: r.update(theory="ordinary_cohomology"), "ordinary unreduced exact homology"),
            (lambda r: r["coverage"].update(upper_vanishing_starts_at=99), "upper vanishing"),
            (lambda r: r["sources"].clear(), "cite its evidence"),
        ):
            record = copy.deepcopy(base)
            mutate(record)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_computed_homology_record(record, COMPUTED_RING_SOURCES)


if __name__ == "__main__":
    unittest.main()
