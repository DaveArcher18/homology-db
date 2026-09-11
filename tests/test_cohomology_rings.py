from __future__ import annotations

import copy
import unittest

from homology_db.cohomology_rings import validate_cohomology_ring_record


def integral_torsion_ring(*, product_order: int) -> dict:
    """A tiny graded ring with a degree-two element a of additive order two."""
    return {
        "schema_version": "homology-db.cohomology-rings/1",
        "record_id": "computed:test-space:Z:v1",
        "space_id": "test-space",
        "coefficient": "Z",
        "characteristic": 0,
        "theory": "ordinary_cohomology",
        "convention": "unreduced",
        "knowledge_state": "exact",
        "algebra": {
            "kind": "graded_structure_constants",
            "generators": [],
            "relations": [],
            "unit": "1",
            "basis": [
                {"id": "1", "degree": 0, "order": 0, "powers": {}},
                {"id": "a", "degree": 2, "order": 2, "powers": {}},
                {"id": "b", "degree": 4, "order": product_order, "powers": {}},
            ],
            "products": [
                {
                    "left": "a",
                    "right": "a",
                    "result": [{"basis": "b", "coefficient": 1}],
                }
            ],
            "multiplication": {
                "complete": True,
                "omitted_products": "zero",
                "scope": "all_nonunit_ordered_basis_pairs",
                "unit_products": "identity",
            },
        },
        "coverage": {
            "kind": "complete_finite",
            "through_degree": 4,
            "upper_vanishing_starts_at": 5,
        },
        "groups": [
            {"degree": 0, "free_rank": 1, "torsion_orders": []},
            {"degree": 1, "free_rank": 0, "torsion_orders": []},
            {"degree": 2, "free_rank": 0, "torsion_orders": [2]},
            {"degree": 3, "free_rank": 0, "torsion_orders": []},
            {
                "degree": 4,
                "free_rank": int(product_order == 0),
                "torsion_orders": [product_order] if product_order else [],
            },
        ],
        "sources": [{"source_id": "test-source", "locator": "test", "role": "computation"}],
        "provenance": {
            "kind": "external_engine_computation",
            "review_state": "imported_unreviewed",
            "derivation": "test fixture",
            "model_id": "test-model",
            "engine": "test-engine",
            "engine_version": "1",
            "source_locator": "test",
            "model_facets_sha256": "0" * 64,
        },
        "presentation": {},
    }


class CohomologyRingValidatorTests(unittest.TestCase):
    def test_integral_product_respects_torsion_factor_order(self) -> None:
        valid = integral_torsion_ring(product_order=2)
        validate_cohomology_ring_record(valid, {"test-source": {}})

        invalid = copy.deepcopy(valid)
        invalid["algebra"]["basis"][2]["order"] = 0
        invalid["groups"][4] = {"degree": 4, "free_rank": 1, "torsion_orders": []}
        with self.assertRaisesRegex(ValueError, "additive order of a torsion factor"):
            validate_cohomology_ring_record(invalid, {"test-source": {}})


if __name__ == "__main__":
    unittest.main()
