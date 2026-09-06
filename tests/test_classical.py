from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from homology_db.chromatic import ChromaticDatabase, ChromaticTools
from homology_db.classical import (
    CLASSICAL_COEFFICIENTS,
    CLASSICAL_SPACE_IDS,
    classical_records,
    validate_classical_record,
    validate_classical_records,
)


class ClassicalCohomologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        path = Path(cls.temporary.name) / "homology.sqlite3"
        ChromaticDatabase.build(path)
        cls.homology = ChromaticTools(path)
        cls.addClassCleanup(cls.homology.close)

    def setUp(self) -> None:
        self.records = classical_records()

    def record(self, space: str, field: str = "Q") -> dict:
        return next(record for record in self.records[space] if record["coefficient"] == field)

    @staticmethod
    def multiply(record: dict, left: str, right: str) -> dict[str, int]:
        """Read the claimed sparse table without relying on its validator."""
        if left == "1":
            return {right: 1}
        if right == "1":
            return {left: 1}
        entries = [entry for entry in record["algebra"]["products"]
                   if (entry["left"], entry["right"]) == (left, right)]
        if not entries:
            return {}
        characteristic = record["characteristic"]
        return {term["basis"]: term["coefficient"] % characteristic if characteristic else term["coefficient"]
                for term in entries[0]["result"]}

    def test_exact_identity_coverage_sources_and_fresh_deterministic_records(self) -> None:
        summary = validate_classical_records(self.records)
        self.assertEqual((summary["space_count"], summary["record_count"]), (13, 65))
        self.assertEqual(set(self.records), set(CLASSICAL_SPACE_IDS))
        original = json.dumps(self.records, sort_keys=True)
        self.assertEqual(original, json.dumps(classical_records(), sort_keys=True))
        self.records["point"][0]["groups"][0]["dimension"] = 999
        self.assertEqual(original, json.dumps(classical_records(), sort_keys=True))
        for record in classical_records()["point"]:
            self.assertEqual(record["provenance"]["review_state"], "human_review_pending")
            self.assertEqual(record["provenance"]["kind"], "literature")

    def test_additive_dimensions_match_independent_integral_uct_and_existing_field_homology(self) -> None:
        # This derives dimensions from the existing homology corpus, independent
        # of the new ring factories and their multiplication-table validators.
        for space, records in self.records.items():
            integral = self.homology.read_homology(space, coefficient="Z")
            self.assertEqual(integral["outcome"], "selected")
            groups = {row["degree"]: row["value"] for row in integral["groups"]}
            for record in records:
                p = record["characteristic"]
                actual = {row["degree"]: row["dimension"] for row in record["groups"]}
                for degree, dimension in actual.items():
                    current = groups[degree]
                    previous = groups.get(degree - 1, {"torsion_orders": []})
                    expected = current["free_rank"]
                    if p:
                        expected += sum(order % p == 0 for order in current["torsion_orders"])
                        expected += sum(order % p == 0 for order in previous["torsion_orders"])
                    with self.subTest(space=space, field=record["coefficient"], degree=degree):
                        self.assertEqual(dimension, expected)
                if p:
                    existing = self.homology.read_homology(space, coefficient=record["coefficient"])
                    self.assertEqual(actual, {row["degree"]: row["value"]["dimension"] for row in existing["groups"]})

    def test_projective_plane_and_wedge_have_equal_groups_but_different_squares(self) -> None:
        for field in CLASSICAL_COEFFICIENTS:
            cp2 = self.record("complex_projective_space:2", field)
            wedge = self.record("sphere_wedge:2:4", field)
            self.assertEqual(cp2["groups"], wedge["groups"])
            self.assertEqual(self.multiply(cp2, "x", "x"), {"x2": 1})
            self.assertEqual(self.multiply(wedge, "a", "a"), {})
            self.assertEqual(self.multiply(wedge, "a", "b"), {})

    def test_torus_has_exterior_products_and_characteristic_sensitive_signs(self) -> None:
        for field in CLASSICAL_COEFFICIENTS:
            ring = self.record("torus:2", field)
            self.assertEqual(self.multiply(ring, "a", "a"), {})
            self.assertEqual(self.multiply(ring, "b", "b"), {})
            self.assertEqual(self.multiply(ring, "a", "b"), {"w": 1})
            self.assertEqual(self.multiply(ring, "b", "a"), {"w": ring["characteristic"] - 1 if ring["characteristic"] else -1})
            self.assertIn(r"\Lambda", ring["presentation"]["tex"])

    def test_real_projective_dimensions_truncation_and_odd_field_vanishing(self) -> None:
        for n in (2, 3, 4):
            space = f"real_projective_space:{n}"
            mod_two = self.record(space, "F2")
            self.assertEqual([row["dimension"] for row in mod_two["groups"]], [1] * (n + 1))
            self.assertEqual(self.multiply(mod_two, "x", "x"), {"x2": 1})
            self.assertEqual(self.multiply(mod_two, "x", f"x{n}"), {})
            for field in ("Q", "F3", "F5", "F7"):
                expected = [1] + [0] * n
                if n % 2:
                    expected[n] = 1
                self.assertEqual([row["dimension"] for row in self.record(space, field)["groups"]], expected)

    def test_klein_diagonal_crosscap_basis_and_coefficient_change(self) -> None:
        ring = self.record("klein_bottle", "F2")
        self.assertEqual([row["dimension"] for row in ring["groups"]], [1, 2, 1])
        self.assertEqual(self.multiply(ring, "a", "a"), {"w": 1})
        self.assertEqual(self.multiply(ring, "b", "b"), {"w": 1})
        self.assertEqual(self.multiply(ring, "a", "b"), {})
        for field in ("Q", "F3", "F5", "F7"):
            ring = self.record("klein_bottle", field)
            self.assertEqual([row["dimension"] for row in ring["groups"]], [1, 1, 0])
            self.assertEqual(self.multiply(ring, "a", "a"), {})

    def test_disconnected_sphere_has_idempotent_not_square_zero_and_unit_on_both_components(self) -> None:
        for field in CLASSICAL_COEFFICIENTS:
            ring = self.record("sphere:0", field)
            self.assertEqual(ring["groups"], [{"degree": 0, "dimension": 2}])
            self.assertEqual(self.multiply(ring, "e", "e"), {"e": 1})
            self.assertEqual(self.multiply(ring, "1", "e"), {"e": 1})
            self.assertEqual(self.multiply(ring, "1", "1"), {"1": 1})
            self.assertEqual(ring["convention"], "unreduced")
            # Bilinear expansion verifies the complementary component class,
            # including characteristic 2 where subtraction is addition.
            def multiply_vectors(left: dict, right: dict) -> dict:
                result: dict[str, int] = {}
                p = ring["characteristic"]
                for a, scalar_a in left.items():
                    for b, scalar_b in right.items():
                        for key, scalar in self.multiply(ring, a, b).items():
                            result[key] = result.get(key, 0) + scalar_a * scalar_b * scalar
                if p:
                    result = {key: scalar % p for key, scalar in result.items()}
                return {key: scalar for key, scalar in result.items() if scalar}

            complement = {"1": 1, "e": ring["characteristic"] - 1 if ring["characteristic"] else -1}
            self.assertEqual(multiply_vectors({"1": 1, "e": -1}, {"1": 1, "e": -1}), complement)
            self.assertEqual(multiply_vectors({"e": 1}, {"1": 1, "e": -1}), {})

    def test_validator_rejects_wrong_sign_nonassociative_table_and_invalid_relations(self) -> None:
        torus = self.record("torus:2", "F3")
        next(p for p in torus["algebra"]["products"] if p["left"] == "b" and p["right"] == "a")["result"][0]["coefficient"] = 1
        with self.assertRaisesRegex(ValueError, "graded commutativity"):
            validate_classical_record(torus)
        projective = self.record("real_projective_space:4", "F2")
        projective["algebra"]["products"] = [p for p in projective["algebra"]["products"] if (p["left"], p["right"]) != ("x2", "x2")]
        with self.assertRaisesRegex(ValueError, "associativity"):
            validate_classical_record(projective)
        sphere_zero = self.record("sphere:0")
        sphere_zero["algebra"]["relations"][0]["terms"] = [{"coefficient": 1, "powers": {"e": 2}}]
        with self.assertRaisesRegex(ValueError, "not satisfied"):
            validate_classical_record(sphere_zero)
        cp2 = self.record("complex_projective_space:2")
        cp2["algebra"]["relations"][0]["terms"].append({"coefficient": 1, "powers": {"x": 2}})
        with self.assertRaisesRegex(ValueError, "not homogeneous"):
            validate_classical_record(cp2)

    def test_validator_rejects_absence_as_zero_false_coverage_sources_and_display_drift(self) -> None:
        base = self.record("complex_projective_space:2")
        mutations = [
            (lambda r: r["algebra"]["multiplication"].update(complete=False), "explicit complete"),
            (lambda r: r["groups"].pop(1), "every covered degree"),
            (lambda r: r["coverage"].update(upper_vanishing_starts_at=None), "upper vanishing"),
            (lambda r: r["sources"][0].update(source_id="missing"), "resolvable"),
            (lambda r: r["presentation"].update(tex="wrong"), "generated"),
            (lambda r: r["provenance"].update(review_state="human_approved"), "pending human"),
            (lambda r: r["algebra"].update(unit="x"), "unit must"),
            (lambda r: r["algebra"]["basis"][1].update(degree=-1), "basis degree"),
        ]
        for change, message in mutations:
            record = copy.deepcopy(base)
            change(record)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_classical_record(record)
        self.records.pop("sphere:0")
        with self.assertRaisesRegex(ValueError, "exact 13"):
            validate_classical_records(self.records)
        records = classical_records()
        records["point"][0] = records["point"][1]
        with self.assertRaisesRegex(ValueError, "five distinct"):
            validate_classical_records(records)


if __name__ == "__main__":
    unittest.main()
