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
            self.assertEqual(manifest["counts"]["spaces"], 42)
            self.assertEqual(manifest["counts"]["spectra"], 49)
            catalog = json.loads((first / "data" / "catalog.json").read_text())["payload"]
            self.assertEqual(len(catalog["conceptual_spaces"]), 42)
            self.assertNotIn("homology", catalog["conceptual_spaces"][0])

            reconstructed_spaces = []
            for entry in catalog["conceptual_spaces"]:
                document = json.loads((first / entry["_document_path"]).read_text())
                reconstructed_spaces.append(document["payload"])
            self.assertEqual(reconstructed_spaces, original["conceptual_spaces"])

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
