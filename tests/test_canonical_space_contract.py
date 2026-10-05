"""Guard the representative records used by the page review slice."""

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CanonicalSpaceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        html = (ROOT / "dist" / "atlas.html").read_text(encoding="utf-8")
        match = re.search(
            r'<script id="atlas-data" type="application/json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        assert match is not None
        cls.atlas = json.loads(match.group(1))
        cls.spaces = {space["id"]: space for space in cls.atlas["conceptual_spaces"]}

    def test_shared_notation_display_covers_all_space_labels(self) -> None:
        script = r"""
const assert = require('assert');
const p = require('./static_atlas/presentation.js');
const atlas = JSON.parse(require('fs').readFileSync(0, 'utf8'));
let count = 0;
for (const space of atlas.conceptual_spaces) {
  for (const label of [space.name.plain, ...space.aliases]) {
    const parts = p.spaceLabelPresentation(space, label);
    for (const part of parts) {
      if (part.tex) { assert(p.parseTex(part.tex), label); count++; }
      else assert(!/[A-Z]\^\d|twist|[A-Z]_\d/.test(part.text), label);
    }
  }
}
assert(count > 150);
const twisted = atlas.conceptual_spaces.find(s => s.slug === 'connected-sum-s2-twist-s1-sum-2');
assert.deepStrictEqual(p.spaceLabelPresentation(twisted)[0], {text:'Connected sum '});
assert.equal(p.spaceLabelPresentation(twisted, twisted.aliases[0])[0].tex, twisted.name.tex);
assert.equal(p.presentationPlainText(p.spaceLabelPresentation(twisted)), 'Connected sum 2(S²×̃S¹)');
for (const text of ['Sphere S^12', 'Product S^2xS^1', 'Twisted S^3twistS^1', 'T^2', 'M_26', 'S^2 x R', 'H^2 x R', '$H^2(X)$']) {
  const parts = p.notationTextPresentation(text);
  assert(parts.some(part => part.tex && p.parseTex(part.tex)), text);
  assert(!parts.some(part => part.text && /\^|twist/.test(part.text)), text);
}
assert.deepStrictEqual(p.notationTextPresentation('unknown data remain unknown'), [{text:'unknown data remain unknown'}]);
assert.deepStrictEqual(p.spaceLabelPresentation(twisted, 'a different record'), [{text:'a different record'}]);
"""
        subprocess.run(["node", "-e", script], input=json.dumps(self.atlas),
                       text=True, cwd=ROOT, check=True, capture_output=True)

    def test_review_records_cover_distinct_states(self) -> None:
        self.assertEqual(len(self.spaces), 194)
        review_ids = {
            "point",
            "sphere:0",
            "real_projective_space:4",
            "torus:2",
            "four_manifold:k3",
            "connected_sum:s2xs1-sum-19",
            "orientable_surface:26",
        }
        self.assertTrue(review_ids <= self.spaces.keys())
        self.assertEqual(self.spaces["point"]["properties"][0]["value"], 0)
        computed = set(self.atlas["computed_rings"]["space_ids"])
        self.assertIn("four_manifold:k3", computed)
        self.assertIn("real_projective_space:4", computed)
        self.assertIn("torus:2", computed)
        self.assertNotIn("sphere:0", computed)
        self.assertNotIn("orientable_surface:26", computed)
        self.assertTrue(self.spaces["sphere:0"]["cohomology"])
        self.assertEqual(self.spaces["orientable_surface:26"]["cohomology"], [])

    def test_k3_direct_sum_and_large_basis(self) -> None:
        k3 = self.spaces["four_manifold:k3"]
        for coefficient in ("Z", "F2", "F3", "F5", "F7", "F11"):
            row = next(
                row for row in k3["homology"]
                if row["coefficient_ring"] == coefficient
                and row["reduced"] is False
                and row["degree"] == 2
            )
            self.assertEqual(row["knowledge_state"], "exact")
            if coefficient == "Z":
                self.assertEqual(row["group"]["free_rank"], 22)
            else:
                self.assertEqual(row["group"]["dimension"], 22)
        large = self.spaces["connected_sum:s2xs1-sum-19"]
        self.assertEqual(
            max(len(record["algebra"]["basis"]) for record in large["cohomology"]),
            40,
        )

    def test_point_is_a_space_not_a_browsable_family(self) -> None:
        renderer = (ROOT / "static_atlas" / "atlas.js").read_text(encoding="utf-8")
        self.assertIn('const browsableSections = sections.filter((section) => section.id !== "point")', renderer)
        self.assertIn('if (section?.id === "point")', renderer)
        self.assertIn('redirectHash: `#space=${point.slug}`', renderer)

    def test_triangulation_introductions_render_math_without_guessing_unknown_data(self) -> None:
        completed = subprocess.run(["node", "-e", r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const p = require('./static_atlas/presentation.js');
const html = fs.readFileSync('dist/atlas.html', 'utf8');
const atlas = JSON.parse(html.match(/<script id="atlas-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const spaces = new Map(atlas.conceptual_spaces.map(s => [s.id, s]));
let checked = 0;
for (const entry of atlas.teaching.entries) {
  if (!entry.introduction.includes('-facet triangulation, with integral homology ')) continue;
  const result = p.triangulationIntroductionPresentation(spaces.get(entry.space_id), entry.introduction);
  assert.ok(result, entry.space_id);
  assert.ok(result.groups.length);
  result.groups.forEach(g => assert.ok(p.isSupportedTex(g.tex), g.tex));
  checked++;
}
assert.ok(checked > 100, 'Cover the imported triangulation introductions');
const space = spaces.get('connected_sum:s2-twist-s1-sum-2');
const intro = atlas.teaching.entries.find(e => e.space_id === space.id).introduction;
const result = p.triangulationIntroductionPresentation(space, intro);
assert.deepEqual(result.groups.map(g => g.tex), ['\\mathbb{Z}', '\\mathbb{Z}^{\\oplus 2}', '\\mathbb{Z}\\oplus \\mathbb{Z}/2\\mathbb{Z}', '0']);
assert.equal(result.nameTex, space.name.tex);
assert.equal(p.triangulationIntroductionPresentation(space, intro.replace('Z^2', 'not recorded')), null);
assert.equal(p.triangulationIntroductionPresentation(space, intro.replace('Z/2', 'Z/1')), null);
assert.equal(p.triangulationIntroductionPresentation(space, intro.replace('Z^2', 'Z^9007199254740993')), null);
assert.equal(p.triangulationIntroductionPresentation(space, 'An ordinary prose introduction.'), null);
console.log(`Checked ${checked} imported introductions, mixed groups and unknown-state rejection.`);
"""], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_every_recorded_space_uses_the_table_first_page(self) -> None:
        renderer = (ROOT / "static_atlas" / "atlas.js").read_text(encoding="utf-8")
        self.assertIn("function buildSpaceView(space) {\n    return buildCanonicalSpaceView(space);", renderer)
        self.assertNotIn("canonicalReviewSpaces", renderer)
        self.assertIn('detailsBlock("Coverage, conventions & availability")', renderer)
        self.assertIn('element("section", "canonical-section canonical-ring")', renderer)
        self.assertIn('element("h2", "", "Cohomology ring")', renderer)
        self.assertIn('"canonical-ring-content"', renderer)
        self.assertIn('"canonical-generator-degrees"', renderer)
        self.assertIn('"ring-algebra-convention"', renderer)
        self.assertIn('detailsBlock("Generators, relations & full record")', renderer)
        self.assertNotIn('detailsBlock("Cohomology ring & cup products")', renderer)
        self.assertIn('detailsBlock("Sources, models & provenance")', renderer)
        self.assertIn('citations.forEach((citation) => sourceList.append(renderCitation(citation)))', renderer)
        self.assertNotIn('citations.slice(0, 3)', renderer)
        self.assertIn('detailsBlock("What to notice")', renderer)
        self.assertIn('detailsBlock("Why ring structure matters")', renderer)


if __name__ == "__main__":
    unittest.main()
