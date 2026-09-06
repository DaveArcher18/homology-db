"""Independent cellular-chain and multiplication oracle for family rules."""

import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
COEFFICIENTS = ("Z", "Q", "F2", "F3", "F5", "F7", "F11")


def evaluate_many(requests):
    script = """const f=require('./static_atlas/families.js');
    const requests=JSON.parse(require('fs').readFileSync(0,'utf8'));
    process.stdout.write(JSON.stringify(requests.map(r=>f.evaluate(...r))));"""
    return json.loads(subprocess.check_output(
        [NODE, "-e", script], input=json.dumps(requests), text=True, cwd=ROOT))


def rp_cellular_group(n, degree, coefficient, cohomology=False):
    """Kernel/image of adjacent 1x1 maps, not a tabulated parity formula."""
    def boundary(d):
        return 2 if 0 < d <= n and d % 2 == 0 else 0

    if not 0 <= degree <= n:
        return "0", []
    incoming, outgoing = boundary(degree + 1), boundary(degree)
    if cohomology:
        incoming, outgoing = outgoing, incoming
    if coefficient == "Z":
        if outgoing:
            return "0", []
        return ("0", [str(incoming)]) if incoming else ("1", [])
    prime = 0 if coefficient == "Q" else int(coefficient[1:])
    rank = lambda value: int(value != 0 and (prime == 0 or value % prime != 0))
    return str(1 - rank(incoming) - rank(outgoing)), []


@unittest.skipUnless(NODE, "Node required for independent shipped-evaluator audit")
class IndependentFamilyMathematics(unittest.TestCase):
    def test_formula_and_glossary_tex_is_supported(self):
        script = r"""const f=require('./static_atlas/families.js');
        const p=require('./static_atlas/presentation.js'), assert=require('assert/strict');
        for(const family of f.families) for(const n of ['0','1','2','3','4','13','1'+'0'.repeat(100)])
          for(const c of f.coefficients) {
            const r=f.evaluate(family,n,c);
            for(const key of ['homology','cohomology','ring'])
              assert(p.isSupportedTex(r.formulas[key]), `${family} ${n} ${c} ${key}`);
            for(const row of r.rows) for(const key of ['homology','cohomology'])
              assert(p.isSupportedTex(row[key].tex));
          }
        const source=require('fs').readFileSync('./static_atlas/workbench.js','utf8');
        const entries=require('vm').runInNewContext(source.match(/const glossary = (\[[\s\S]*?\n  \]);/)[1]);
        for(const entry of entries) for(const index of [2,4])
          assert(p.isSupportedTex(entry[index]), entry[0]);
        assert.equal(p.isSupportedTex('<script>'),false);
        """
        subprocess.run([NODE, "-e", script], cwd=ROOT, check=True)

    def test_rp_cellular_kernel_image_oracle(self):
        requests = [["real_projective_space", str(n), c, {"count": n + 4}]
                    for n in range(30) for c in COEFFICIENTS]
        for request, result in zip(requests, evaluate_many(requests)):
            n, coefficient = int(request[1]), request[2]
            for row in result["rows"]:
                for theory in ("homology", "cohomology"):
                    expected = rp_cellular_group(n, int(row["degree"]), coefficient,
                                                 theory == "cohomology")
                    observed = row[theory]
                    self.assertEqual((observed["free_rank"], observed["torsion_orders"]),
                                     expected, (request, row["degree"], theory))

    def test_all_small_products_and_additive_orders(self):
        requests = [[family, str(n), c] for family in
                    ("sphere", "complex_projective_space", "real_projective_space")
                    for n in range(11) for c in COEFFICIENTS]
        for result in evaluate_many(requests):
            generators = result["generators"]
            self.assertTrue(result["display"]["multiplication_complete"])
            by_degree = {int(g["degree"]): g for g in generators}
            for i, left in enumerate(generators):
                for j, right in enumerate(generators):
                    if i == 0:
                        expected = right["tex"]
                    elif j == 0:
                        expected = left["tex"]
                    elif result["family"] == "sphere":
                        expected = "e" if result["n"] == "0" else "0"
                    else:
                        # Every supported projective ring has at most one
                        # additive generator per degree. Positive products
                        # hit it precisely when that sum-degree is supported.
                        target = by_degree.get(int(left["degree"]) + int(right["degree"]))
                        expected = target["tex"] if target else "0"
                    self.assertEqual(result["multiplication"][i][j], expected, result)
                    if result["coefficient"] == "Z" and expected != "0":
                        target = next(g for g in generators if g["tex"] == expected)
                        if left["order"] == "2" or right["order"] == "2":
                            self.assertEqual(target["order"], "2")

    def test_huge_parity_top_degree_and_exact_windows(self):
        huge = 10**100
        requests = [["real_projective_space", str(n), c,
                     {"start": str(n - 2), "count": 5, "generatorStart": str(n // 2)}]
                    for n in (huge, huge + 1) for c in COEFFICIENTS]
        for request, result in zip(requests, evaluate_many(requests)):
            n, c = int(request[1]), request[2]
            for row in result["rows"]:
                for theory in ("homology", "cohomology"):
                    actual = row[theory]
                    self.assertEqual((actual["free_rank"], actual["torsion_orders"]),
                                     rp_cellular_group(n, int(row["degree"]), c,
                                                       theory == "cohomology"))
            for coverage in result["coverage"].values():
                self.assertEqual(coverage["kind"], "complete_all_degrees")
