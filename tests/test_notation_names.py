"""Display identities stay readable without altering frozen record names."""

import json
import subprocess
import unittest
from pathlib import Path

from homology_db.chromatic import load_manifest, materialize_specs
from scripts.export_static_atlas import conceptual_space_tex


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class NotationNameTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Exercise the same names/aliases projected by the exporter, without
        # rebuilding algebra records merely to test display normalization.
        corpus = REPOSITORY_ROOT / "corpus" / "computed-rings-v1"
        descriptors = json.loads((corpus / "manifest.json").read_text())["models"]
        descriptors += json.loads((corpus / "imported-models.json").read_text())["models"]
        primary_ids = {model["space_id"] for model in descriptors}
        cls.spaces = [
            {
                "id": spec["key"],
                "name": {"plain": spec["label"], "tex": conceptual_space_tex(spec)},
                "aliases": spec["aliases"],
            }
            for spec in materialize_specs(load_manifest())
            if spec["key"] in primary_ids
        ]

    def evaluate(self, script):
        completed = subprocess.run(
            ["node", "-e", 'const p = require("./static_atlas/presentation.js");\n'
             'const spaces = JSON.parse(require("fs").readFileSync(0,"utf8"));\n' + script],
            cwd=REPOSITORY_ROOT,
            input=json.dumps(self.spaces),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_brieskorn_display_uses_each_explicit_tuple(self):
        result = self.evaluate(r"""
console.log(JSON.stringify(spaces.filter(s => s.name.plain.startsWith("Brieskorn "))
  .map(s => ({original:s.name.tex, ...p.spaceNamePresentation(s),
    label:p.presentationPlainText(p.spaceLabelPresentation(s))}))));
""")
        self.assertEqual(len(result), 6)
        tuples = ["2,3,7", "2,5,7", "3,4,5", "3,4,7", "3,5,7", "4,5,7"]
        self.assertEqual({item["tex"] for item in result}, {rf"\Sigma({t})" for t in tuples})
        for item in result:
            self.assertEqual(item["original"], r"\Sigma_{\mathrm{P}}^{3}")
            self.assertNotIn("subscript P", item["spoken"])
            self.assertIn("Brieskorn homology sphere Σ(", item["label"])

    def test_all_repeated_sums_explain_multiplicity_and_share_alias_display(self):
        result = self.evaluate(r"""
console.log(JSON.stringify(spaces.filter(s => /^\d+\(/.test(s.name.tex)).map(s => ({
  id:s.id, ...p.spaceNamePresentation(s),
  label:p.presentationPlainText(p.spaceLabelPresentation(s)),
  aliases:s.aliases.map(a => p.presentationPlainText(p.spaceLabelPresentation(s,a)))
}))));
""")
        self.assertEqual(len(result), 48)
        for item in result:
            self.assertRegex(item["spoken"], r"^Connected sum of \d+ copies of ")
            self.assertRegex(item["label"], r"^Connected sum of \d+ copies of ")
            self.assertNotRegex(item["tex"], r"^\d+\(")
            self.assertIn("# denotes connected sum", item["explanation"])
            self.assertIn(item["label"], item["aliases"])
        two = next(item for item in result if item["id"] == "connected_sum:s2-twist-s1-sum-2")
        self.assertEqual(two["tex"].count(r"\widetilde{\times}"), 2)
        self.assertIn(r"\mathbin{\#}", two["tex"])
        self.assertIn("2 copies of S² twisted product S¹", two["spoken"])
        nineteen = next(item for item in result if item["id"] == "connected_sum:s2xs1-sum-19")
        self.assertTrue(nineteen["tex"].startswith(r"\#^{19}("))

    def test_mixed_sums_retain_extra_factors(self):
        result = self.evaluate(r"""
console.log(JSON.stringify(spaces.filter(s => /sum-2-sum-(rp3|l31)$/.test(s.id))
  .map(s => ({id:s.id, ...p.spaceNamePresentation(s)}))));
""")
        self.assertEqual(len(result), 4)
        for item in result:
            self.assertIn("2 copies of", item["spoken"])
            if item["id"].endswith("rp3"):
                self.assertTrue(item["tex"].endswith(r"\mathbb{R}P^{3}"))
                self.assertTrue(item["spoken"].endswith(" and ℝP³"))
            else:
                self.assertTrue(item["tex"].endswith("L(3,1)"))
                self.assertTrue(item["spoken"].endswith(" and L(3,1)"))

    def test_all_primary_names_parse_and_frozen_inputs_are_untouched(self):
        result = self.evaluate(r"""
const before = JSON.stringify(spaces);
const failures = [];
for (const space of spaces) {
  const shown = p.spaceNamePresentation(space);
  if (!p.parseTex(shown.tex)) failures.push(space.id);
  for (const label of [space.name.plain,...space.aliases]) {
    for (const part of p.spaceLabelPresentation(space,label)) {
      if (part.tex && !p.parseTex(part.tex)) failures.push(`${space.id}:${label}`);
    }
  }
}
console.log(JSON.stringify({count:spaces.length, failures, unchanged:before === JSON.stringify(spaces)}));
""")
        self.assertEqual(result["count"], 194)
        self.assertEqual(result["failures"], [])
        self.assertTrue(result["unchanged"])

    def test_only_recorded_connected_sum_names_receive_sum_normalization(self):
        result = self.evaluate(r"""
console.log(JSON.stringify(p.spaceNamePresentation({name:{plain:"Two times M",tex:"2(M)"}})));
""")
        self.assertEqual(result["tex"], "2(M)")
        self.assertEqual(result["explanation"], "")

    def test_literal_source_keys_are_not_reinterpreted_in_prose(self):
        result = self.evaluate(r"""
const literal = "homology_3spheres.txt: Sigma_2_3_7";
console.log(JSON.stringify({
  literal:p.presentationPlainText(p.notationTextPresentation(literal)),
  explicit:p.presentationPlainText(p.notationTextPresentation("$\\Sigma(2,3,7)$"))
}));
""")
        self.assertEqual(result["literal"], "homology_3spheres.txt: Sigma_2_3_7")
        self.assertEqual(result["explicit"], "Σ(2,3,7)")

    def test_nonleading_and_multiple_repeated_terms_are_explained(self):
        result = self.evaluate(r"""
const recorded = spaces.find(s => s.id === "four_manifold:rp4-sum-11-s2xs2");
const multiple = {name:{plain:"Connected sum 3(M) # 4(N)",tex:"3(M)\\#4(N)"},aliases:[]};
console.log(JSON.stringify({recorded:p.spaceNamePresentation(recorded),
  multiple:p.spaceNamePresentation(multiple)}));
""")
        self.assertIn(r"\#^{11}(S^{2}\times S^{2})", result["recorded"]["tex"])
        self.assertEqual(result["recorded"]["spoken"], "Connected sum of ℝP⁴ and 11 copies of S²× S²")
        self.assertIn("number of copies", result["recorded"]["explanation"])
        self.assertEqual(result["multiple"]["spoken"], "Connected sum of 3 copies of M and 4 copies of N")
        self.assertIn(r"\#^{3}(M)", result["multiple"]["tex"])
        self.assertIn(r"\#^{4}(N)", result["multiple"]["tex"])

    def test_every_repeated_connected_sum_term_is_normalized(self):
        result = self.evaluate(r"""
const candidates = spaces.filter(s => s.name.plain.startsWith("Connected sum ")
  && /(?:^|\\#)\d+\(/.test(s.name.tex));
console.log(JSON.stringify({count:candidates.length,unfixed:candidates.filter(s =>
  !p.spaceNamePresentation(s).explanation || /(?:^|\\#)\d+\(/.test(p.spaceNamePresentation(s).tex)
).map(s=>s.id)}));
""")
        self.assertEqual(result["count"], 49)
        self.assertEqual(result["unfixed"], [])
