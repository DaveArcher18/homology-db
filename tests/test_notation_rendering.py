"""Exercise the actual atlas display seams without booting the full application."""
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NotationRenderingTest(unittest.TestCase):
    def test_literal_provenance_and_authored_math_use_separate_rendering_seams(self):
        script = r'''
const fs = require("node:fs");
const vm = require("node:vm");
const p = require("./static_atlas/presentation.js");
const source = fs.readFileSync("./static_atlas/atlas.js", "utf8");
// Run the production functions, retaining their real call paths. The minimal
// DOM records text and math spans; it does not duplicate the formatter logic.
function productionFunction(name) {
  const start = source.indexOf(`  function ${name}(`);
  if (start < 0) throw new Error(`Missing display seam: ${name}`);
  const end = source.indexOf("\n  }\n", start);
  return source.slice(start, end + 5);
}
class Node {
  constructor(tagName = "", text = "") {
    this.tagName = tagName;
    this.children = [];
    this.literal = text;
    this.dataset = {};
    this.attributes = {};
    this.className = "";
    this.classList = {add: name => { this.className += ` ${name}`; }};
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.literal = ""; this.children = children; }
  setAttribute(key, value) { this.attributes[key] = value; }
  set textContent(value) { this.literal = String(value); this.children = []; }
  get textContent() { return this.literal + this.children.map(n => typeof n === "string" ? n : n.textContent).join(""); }
}
const document = {createElement: tag => new Node(tag), createTextNode: text => new Node("#text", String(text))};
const context = vm.createContext({document, URL, ...p});
vm.runInContext([
  "element", "asArray", "humanize", "displayValue", "appendDefinition",
  "appendRecordedDefinition", "modelRecords", "renderCellDescription",
  "renderModels", "safeHttpsUrl", "outboundLink", "citationTitle", "renderCitation",
  "renderTex", "renderGroup", "appendNotation", "notationElement", "spaceLabel",
  "readableSpaceName", "mathName", "distinctSpaceAliases",
].map(productionFunction).join("\n"), context);
function mathNodes(node) {
  return [node, ...node.children.flatMap(n => typeof n === "string" ? [] : mathNodes(n))]
    .filter(n => n.attributes.role === "math");
}
const identifier = "homology_3spheres.txt: Sigma_2_3_7";
const model = {model_id: "Sigma_2_3_7", name: "Sigma_2_3_7",
  construction: identifier, attaching_map: identifier};
const models = new Node("div");
context.renderModels({models: [model]}, models);
const citation = context.renderCitation({title: "A source about Sigma_2_3_7",
  locator: identifier, url: "https://example.org/source"});
const narrative = context.notationElement("p", "", "The bundle S^2twistS^1 has $H^1$. Source: Sigma_2_3_7.");
const operator = context.renderTex("\\widetilde{\\times}", "twisted product");
const brieskorn = {name: {plain: "Brieskorn homology sphere Sigma(2,3,7)", tex: "\\Sigma_{\\mathrm{P}}^{3}"}, aliases: ["Sigma(2,3,7)"]};
const connected = {name: {plain: "Connected sum (S^2twistS^1)#2", tex: "2(S^2\\widetilde{\\times}S^1)"}, aliases: ["(S^2twistS^1)#2"]};
const before = JSON.stringify([brieskorn, connected]);
const display = [brieskorn, connected].map(space => ({tex: context.mathName(space).dataset.tex,
  readable: context.readableSpaceName(space), aliases: context.distinctSpaceAliases(space)}));
const group = context.renderGroup(p.groupPresentation({coefficient_ring: "Z", knowledge_state: "exact", group: {state: "exact", free_rank: 2, torsion_orders: []}}), "math-inline");
const classes = node => [node.className, ...node.children.flatMap(n => typeof n === "string" ? [] : classes(n))];
console.log(JSON.stringify({modelText: models.textContent, modelMath: mathNodes(models).length,
  citationText: citation.textContent, citationMath: mathNodes(citation).length,
  authoredTex: mathNodes(narrative).map(n => n.dataset.tex),
  authoredText: narrative.textContent, operatorClasses: classes(operator), display,
  sourceUnchanged: before === JSON.stringify([brieskorn, connected]),
  groupClass: group.className, groupTex: group.dataset.tex,
  workbenchGroupClass: context.renderTex(group.dataset.tex, "group", "group-math").className}));
'''
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, text=True,
                                   capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertIn("homology_3spheres.txt: Sigma_2_3_7", result["modelText"])
        self.assertIn("Sigma_2_3_7", result["modelText"])
        self.assertEqual(result["modelMath"], 0)
        self.assertIn("A source about Sigma_2_3_7", result["citationText"])
        self.assertIn("homology_3spheres.txt: Sigma_2_3_7", result["citationText"])
        self.assertEqual(result["citationMath"], 0)
        self.assertEqual(result["authoredTex"], [r"S^{2}\widetilde{\times}S^{1}", "H^1"])
        self.assertNotIn("twist", result["authoredText"])
        self.assertIn("Sigma_2_3_7", result["authoredText"])
        self.assertTrue(any("tex-widetilde-operator" in c for c in result["operatorClasses"]))
        self.assertEqual(result["display"][0]["tex"], r"\Sigma(2,3,7)")
        self.assertIn(r"\#", result["display"][1]["tex"])
        self.assertFalse(result["display"][1]["tex"].startswith("2("))
        self.assertIn("Connected sum of 2 copies", result["display"][1]["readable"])
        self.assertEqual([item["aliases"] for item in result["display"]], [[], []])
        self.assertTrue(result["sourceUnchanged"])
        self.assertIn("math-group", result["groupClass"].split())
        self.assertIn("math-inline", result["groupClass"].split())
        self.assertIn("math-group", result["workbenchGroupClass"].split())
        self.assertEqual(result["groupTex"], r"\mathbb{Z}^{\oplus 2}")

    def test_all_explicit_space_formula_seams_use_the_shared_canonical_name(self):
        source = (ROOT / "static_atlas" / "atlas.js").read_text()
        # Retained source TeX stays in searchValues; formulas may not use it.
        self.assertNotIn("${space.name.tex}", source)
        self.assertIn("spaceNamePresentation(space).tex", source)
        self.assertIn("distinctSpaceAliases(space)", source)


if __name__ == "__main__":
    unittest.main()
