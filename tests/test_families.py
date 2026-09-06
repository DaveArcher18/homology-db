"""Family-rule evaluation through the shipped JavaScript, not a second engine."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from homology_db.families import family_catalog

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


class FamilyCatalogTests(unittest.TestCase):
    def test_source_binding_and_no_fabricated_review(self):
        catalog = family_catalog()
        self.assertEqual(catalog["schema_version"], "homology-db.family-rules/1")
        self.assertEqual(len(catalog["rules"]), 3)
        self.assertEqual(catalog, family_catalog())
        for rule in catalog["rules"]:
            self.assertEqual(len(rule["content_sha256"]), 64)
            self.assertIn("F11", rule["coefficients"])
            self.assertTrue(rule["sources"])
            self.assertNotIn("human_reviews", rule)


@unittest.skipUnless(NODE, "Node is required to execute the browser family evaluator")
class FamilyEvaluationTests(unittest.TestCase):
    def evaluate(self, family, n, coefficient="Z", **options):
        script = "const f=require('./static_atlas/families.js'); console.log(JSON.stringify(f.evaluate(...JSON.parse(process.argv[1]))));"
        return json.loads(subprocess.check_output([NODE, "-e", script, json.dumps([family, str(n), coefficient, options])], cwd=ROOT, text=True))

    def test_integral_projective_torsion_degree_shift(self):
        r = self.evaluate("real_projective_space", 4)
        self.assertEqual([x["homology"]["torsion_orders"] for x in r["rows"][:5]], [[],["2"],[],["2"],[]])
        self.assertEqual([x["cohomology"]["torsion_orders"] for x in r["rows"][:5]], [[],[],["2"],[],["2"]])
        self.assertEqual(r["multiplication"][1][1], "a^{2}")
        self.assertEqual(r["multiplication"][1][2], "0")

    def test_odd_top_integral_class_and_products(self):
        r = self.evaluate("real_projective_space", 5)
        self.assertEqual(r["rows"][5]["cohomology"]["free_rank"], "1")
        self.assertEqual(r["generators"][-1], {"id":"b","tex":"b","degree":"5","order":None})
        self.assertEqual(r["multiplication"][-1][1:], ["0"]*3)

    def test_zero_dimensions_and_sphere_idempotent(self):
        for family in ("real_projective_space", "complex_projective_space"):
            r = self.evaluate(family, 0)
            self.assertEqual(r["generator_total"], "1")
            self.assertEqual(r["rows"][0]["homology"]["free_rank"], "1")
        r = self.evaluate("sphere", 0)
        self.assertEqual(r["rows"][0]["homology"]["free_rank"], "2")
        self.assertEqual(r["multiplication"], [["1","e"],["e","e"]])

    def test_field_characteristics_and_all_coefficients(self):
        for coefficient in ("Z", "Q", "F2", "F3", "F5", "F7", "F11"):
            r = self.evaluate("complex_projective_space", 3, coefficient)
            self.assertEqual([x["cohomology"]["free_rank"] for x in r["rows"]], ["1","0","1","0","1","0","1","0","0"])
            self.assertEqual(r["multiplication"][1][2], "u^{3}")
            self.assertEqual(r["multiplication"][2][2], "0")
        self.assertEqual(self.evaluate("real_projective_space", 4, "F2")["generator_total"], "5")
        self.assertEqual(self.evaluate("real_projective_space", 4, "F11")["generator_total"], "1")
        self.assertEqual(self.evaluate("real_projective_space", 5, "Q")["generator_total"], "2")

    def test_huge_dimensions_and_generator_windows(self):
        n = 10**80 + 1
        r = self.evaluate("complex_projective_space", n, start=str(2*n), generatorStart=str(n-1))
        self.assertEqual(r["dimension"], str(2*n))
        self.assertEqual(r["rows"][0]["homology"]["free_rank"], "1")
        self.assertEqual(r["rows"][1]["homology"]["free_rank"], "0")
        self.assertEqual(len(r["generators"]), 2)
        self.assertFalse(r["display"]["multiplication_complete"])
        self.assertEqual(r["coverage"]["multiplication"]["kind"], "complete_all_degrees")

    def test_window_and_input_guards(self):
        script = """const assert=require('node:assert/strict'), f=require('./static_atlas/families.js');
        for (const n of [-1, '1.2', '01', 'Infinity', 9007199254740992]) assert.throws(()=>f.evaluate('sphere',n,'Z'));
        assert.throws(()=>f.evaluate('sphere','1','F13'));
        assert.throws(()=>f.evaluate('sphere','1','Z',{count:10000}));
        assert.throws(()=>f.evaluate('sphere','1','Z',{generatorCount:13}));
        for(const family of f.families) for(let n=0;n<18;n++) for(const c of f.coefficients){
          const r=f.evaluate(family,String(n),c);
          assert(r.generators.length<=12); assert.equal(r.rows.length,9);
          if(r.display.multiplication_complete) for(let i=0;i<r.generators.length;i++) {
            assert.equal(r.multiplication[0][i],r.generators[i].tex);
            assert.equal(r.multiplication[i][0],r.generators[i].tex);
          }
        }"""
        subprocess.run([NODE, "-e", script], cwd=ROOT, check=True)
