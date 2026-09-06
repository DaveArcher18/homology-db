import copy
import unittest

from homology_db.family_reviews import reviewed_family_catalog, validate_reviews, SCHEMA


class FamilyReviewTest(unittest.TestCase):
    def setUp(self):
        self.catalog = {"rules": [{"id": "sphere", "version": "1", "content_sha256": "a" * 64}]}
        self.review = dict(id="review-1", rule_id="sphere", rule_version="1",
                           content_sha256="a" * 64, reviewer="Test human", reviewer_role="human",
                           verdict="accept", scope="entire_rule", rationale="Fixture only",
                           source_url="https://github.com/DaveArcher18/homology-db/issues/1",
                           reviewed_at="2026-09-06T10:00:00Z", maintainer="Test maintainer",
                           validated_at="2026-09-06T11:00:00Z", supersedes=None)

    def project(self, reviews):
        return reviewed_family_catalog(self.catalog, {"schema_version": SCHEMA, "reviews": reviews})

    def test_pending_is_independent_of_exact_coverage(self):
        self.assertEqual(self.project([])["rules"][0]["human_review_state"], "human_review_pending")

    def test_only_exact_human_review_applies(self):
        self.assertEqual(self.project([self.review])["rules"][0]["human_review_state"], "human_reviewed")
        self.catalog["rules"][0]["content_sha256"] = "b" * 64
        projected = self.project([self.review])
        self.assertEqual(projected["rules"][0]["human_review_state"], "human_review_pending")
        self.assertEqual(len(projected["review_history"]), 1)

    def test_concerns_are_not_hidden_by_acceptance(self):
        concern = {**self.review, "id": "review-2", "reviewer": "Another human", "verdict": "reject"}
        self.assertEqual(self.project([self.review, concern])["rules"][0]["human_review_state"], "human_concern")

    def test_correction_preserves_history(self):
        correction = {**self.review, "id": "review-2", "supersedes": "review-1", "verdict": "needs-evidence"}
        projected = self.project([self.review, correction])
        self.assertEqual(len(projected["review_history"]), 2)
        self.assertEqual(projected["rules"][0]["human_reviews"], [correction])

    def test_invalid_reviews_fail_closed(self):
        for patch in ({"reviewer_role": "agent"}, {"maintainer": ""}, {"content_sha256": ""},
                      {"source_url": "javascript:alert(1)"}, {"scope": "n=2 only"},
                      {"supersedes": "missing"}, {"verdict": "pending"}, {"reviewed_at": "today"}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.project([{**self.review, **patch}])


if __name__ == "__main__":
    unittest.main()
