"""Teaching inventory completeness is relative to the retained atlas, not a book."""
import json
import unittest

from homology_db.chromatic import load_manifest, materialize_specs
from homology_db.classical import CLASSICAL_SPACE_IDS, CLASSICAL_EXTENSION_SPACE_IDS
from homology_db.teaching import teaching_catalog


class TeachingTests(unittest.TestCase):
    def test_all_retained_spaces_and_no_exhaustiveness_claim(self):
        catalog = teaching_catalog()
        retained = {space["key"] for space in materialize_specs(load_manifest())}
        entries = catalog["entries"]
        self.assertEqual(len(entries), 56)
        self.assertEqual({entry["space_id"] for entry in entries}, retained)
        self.assertIn("not an exhaustive index", catalog["scope_note"])
        self.assertIn("human-review-pending", catalog["scope_note"])
        self.assertEqual(len(CLASSICAL_SPACE_IDS), 13)
        self.assertEqual(len(CLASSICAL_EXTENSION_SPACE_IDS), 2)

    def test_every_introduction_is_sourced_and_gaps_are_explicit(self):
        entries = teaching_catalog()["entries"]
        for entry in entries:
            for key in ("chapter", "locator", "introduction", "teaching_point", "coverage_note"):
                self.assertTrue(entry[key], (entry["space_id"], key))
            self.assertTrue(entry["sources"])
            for source in entry["sources"]:
                self.assertTrue(source["url"].startswith("https://"))
                self.assertTrue(source["title"] and source["locator"])
        infinite = [e for e in entries if e["space_id"].startswith(("classifying_space:", "unitary_classifying_space:", "universal_complex_thom:")) or e["space_id"].endswith(":infinity")]
        self.assertEqual(len(infinite),10)
        self.assertTrue(all("24" in entry["coverage_note"] for entry in infinite))

    def test_guided_comparisons_have_local_steps_and_evidence(self):
        comparisons = teaching_catalog()["comparisons"]
        self.assertEqual(len(comparisons),3)
        self.assertEqual(len({x["id"] for x in comparisons}),3)
        for comparison in comparisons:
            self.assertTrue(comparison["sources"] and comparison["takeaway"])
            self.assertGreaterEqual(len(comparison["steps"]),2)
            self.assertTrue(all(step["href"].startswith(("#space=", "#workbench?")) and step["text"] for step in comparison["steps"]))

    def test_fresh_deterministic_content(self):
        first=teaching_catalog()
        serialized=json.dumps(first,sort_keys=True)
        first["entries"][0]["introduction"]="changed"
        self.assertEqual(json.dumps(teaching_catalog(),sort_keys=True),serialized)
