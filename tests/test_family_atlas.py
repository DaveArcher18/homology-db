"""Integration of source-bound family rules with the frozen legacy corpus."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from homology_db.chromatic import ChromaticDatabase
from homology_db.families import family_catalog
from homology_db.family_reviews import reviewed_family_catalog
from scripts.export_static_atlas import build_read_model, validate_read_model

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


class FamilyAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.database = Path(cls.directory.name) / "atlas.sqlite3"
        ChromaticDatabase.build(cls.database)
        cls.atlas = build_read_model(cls.database)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_export_embeds_exact_rules_without_claiming_human_review(self):
        self.assertEqual(self.atlas["family_rules"], reviewed_family_catalog(family_catalog()))
        self.assertEqual(self.atlas["family_rules"]["review_history"], [])
        for rule in self.atlas["family_rules"]["rules"]:
            self.assertEqual(rule["human_reviews"], [])
            self.assertEqual(rule["human_review_state"], "human_review_pending")
        validate_read_model(self.atlas)

    def test_modified_rule_catalog_and_reviews_are_rejected(self):
        mutations = {
            "missing_catalog": lambda atlas: atlas.pop("family_rules"),
            "missing_rule": lambda atlas: atlas["family_rules"]["rules"].pop(),
            "hash": lambda atlas: atlas["family_rules"]["rules"][0].update(content_sha256="0" * 64),
            "scope": lambda atlas: atlas["family_rules"]["rules"][0].update(parameter_scope="all infinite dimensions"),
            "coefficients": lambda atlas: atlas["family_rules"]["rules"][0]["coefficients"].append("F13"),
            "review_state": lambda atlas: atlas["family_rules"]["rules"][0].update(human_review_state="human_reviewed"),
            "review": lambda atlas: atlas["family_rules"]["rules"][0]["human_reviews"].append({"reviewer":"Fabricated", "verdict":"accept"}),
            "history": lambda atlas: atlas["family_rules"]["review_history"].append({"reviewer":"Fabricated"}),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                atlas = copy.deepcopy(self.atlas)
                mutate(atlas)
                with self.assertRaisesRegex(ValueError, "family rules or human reviews"):
                    validate_read_model(atlas)

    def test_legacy_classical_integrity_and_family_schema_downgrade(self):
        atlas = copy.deepcopy(self.atlas)
        atlas["snapshot"]["schema_version"] = "homology-db.static-atlas/4"
        with self.assertRaises(ValueError):
            validate_read_model(atlas)
        atlas.pop("family_rules")
        validate_read_model(atlas)
        atlas["classical"]["content_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "classical metadata"):
            validate_read_model(atlas)

    @unittest.skipUnless(NODE, "Node is required for crosschecking the browser evaluator")
    def test_family_homology_matches_every_existing_instance_row(self):
        inputs, expected = [], []
        for space in self.atlas["conceptual_spaces"]:
            prefix, separator, parameter = space["id"].partition(":")
            if not separator or prefix not in {"sphere", "real_projective_space", "complex_projective_space"}:
                continue
            if parameter == "infinity":
                continue  # This cycle's evaluator deliberately covers finite n only.
            self.assertTrue(parameter.isdecimal())
            for row in space["homology"]:
                if row["reduced"]:
                    continue
                inputs.append([prefix, parameter, row["coefficient_ring"], {"start":str(row["degree"]), "count":1}])
                expected.append((space["id"], row))
        script = """const fs=require('node:fs');const f=require('./static_atlas/families.js');
        const inputs=JSON.parse(fs.readFileSync(0,'utf8'));
        process.stdout.write(JSON.stringify(inputs.map(args=>f.evaluate(...args).rows[0].homology)));"""
        actual = json.loads(subprocess.run([NODE, "-e", script], input=json.dumps(inputs), text=True,
                                          capture_output=True, cwd=ROOT, check=True).stdout)
        self.assertGreater(len(actual), 100)
        self.assertEqual(len(actual), len(expected))
        for computed, (space_id, row) in zip(actual, expected):
            with self.subTest(space=space_id, coefficient=row["coefficient_ring"], degree=row["degree"]):
                group = row["group"]
                rank = group["free_rank"] if row["coefficient_ring"] == "Z" else group["dimension"]
                torsion = group["torsion_orders"] if row["coefficient_ring"] == "Z" else []
                self.assertEqual(computed["free_rank"], str(rank))
                self.assertEqual(computed["torsion_orders"], [str(order) for order in torsion])


if __name__ == "__main__":
    unittest.main()
