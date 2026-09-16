from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_static_bundle import build_bundle, read_atlas


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class StaticBundleTest(unittest.TestCase):
    def test_checked_atlas_partitions_deterministically_and_without_record_loss(self) -> None:
        atlas_path = REPOSITORY_ROOT / "dist" / "atlas.html"
        _html, original = read_atlas(atlas_path)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            first_manifest = build_bundle(atlas_path, first)
            second_manifest = build_bundle(atlas_path, second)

            self.assertEqual(first_manifest, second_manifest)
            first_files = {
                path.relative_to(first): path.read_bytes()
                for path in first.rglob("*") if path.is_file()
            }
            second_files = {
                path.relative_to(second): path.read_bytes()
                for path in second.rglob("*") if path.is_file()
            }
            self.assertEqual(first_files, second_files)
            self.assertLess(
                (first / "index.html").stat().st_size,
                atlas_path.stat().st_size // 4,
            )

            manifest = json.loads((first / "data" / "manifest.json").read_text())
            self.assertEqual(
                manifest["counts"]["spaces"], len(original["conceptual_spaces"])
            )
            self.assertEqual(
                manifest["counts"]["spectra"], len(original["conceptual_spectra"])
            )
            catalog = json.loads((first / "data" / "catalog.json").read_text())["payload"]
            primary = original["conceptual_spaces"]
            self.assertTrue(all(space["primary_atlas_eligible"] for space in primary))
            self.assertEqual(
                len(catalog["conceptual_spaces"]), len(primary)
            )
            self.assertNotIn("homology", catalog["conceptual_spaces"][0])

            reconstructed_spaces = []
            for entry in catalog["conceptual_spaces"]:
                document = json.loads((first / entry["_document_path"]).read_text())
                reconstructed_spaces.append(document["payload"])
            self.assertEqual(reconstructed_spaces, primary)
            space_documents = [
                item for item in manifest["files"]
                if item["document_kind"] == "space"
            ]
            self.assertEqual(len(space_documents), len(original["conceptual_spaces"]))
            self.assertFalse((first / "data" / "spaces" / "cayley-plane-2.json").exists())

            computed_document = json.loads(
                (first / "data" / "shared" / "computed-rings.json").read_text()
            )
            self.assertEqual(computed_document["document_kind"], "computed_rings")
            computed = computed_document["payload"]
            self.assertEqual(computed, original["computed_rings"])
            self.assertEqual(len(computed["models"]), 11)
            self.assertEqual(computed["record_count"], 1309)
            self.assertEqual(computed["space_count"], 187)

            sources = {
                **original["classical"]["sources"],
                **computed["sources"],
            }
            shipped_source_ids = {
                reference["source_id"]
                for space in reconstructed_spaces
                for record in space.get("cohomology", [])
                for reference in record.get("sources", [])
            }
            self.assertEqual(shipped_source_ids - sources.keys(), set())
            self.assertTrue(all(
                source.get("title")
                and source.get("url", "").startswith("https://")
                for source_id, source in sources.items()
                if source_id in shipped_source_ids
            ))
            self.assertIn("Wern Juin Gabriel Ong", sources["cohomology-tables"]["authors"])
            self.assertIn("cohomology rings", sources["cohomology-tables"]["title"])
            self.assertIn("The OSCAR Team", sources["oscar"]["authors"])
            self.assertIn("OSCAR", sources["oscar"]["title"])
            self.assertIn("f-vectors of 3-manifolds", sources["lutz-sulanke-swartz-3manifolds"]["title"])

            computed_space_ids = set(computed["space_ids"])
            shipped_space_ids = {space["id"] for space in reconstructed_spaces}
            self.assertEqual(len(shipped_space_ids), 194)
            self.assertEqual(len(computed_space_ids), 187)
            self.assertEqual(len(shipped_space_ids - computed_space_ids), 7)
            self.assertTrue(all(space["primary_atlas_eligible"] for space in reconstructed_spaces))
            self.assertNotIn("cayley_plane:2", shipped_space_ids)

    def test_unsafe_slug_is_rejected(self) -> None:
        atlas_path = REPOSITORY_ROOT / "dist" / "atlas.html"
        html, atlas = read_atlas(atlas_path)
        atlas["conceptual_spaces"][0]["slug"] = "../escape"
        marker = '<script id="atlas-data" type="application/json">'
        start = html.index(marker) + len(marker)
        end = html.index("</script>", start)
        malformed = html[:start] + json.dumps(atlas) + html[end:]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "atlas.html"
            source.write_text(malformed)
            with self.assertRaisesRegex(ValueError, "unsafe"):
                build_bundle(source, root / "site")


if __name__ == "__main__":
    unittest.main()
