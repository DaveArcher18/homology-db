import copy
import unittest

from homology_db.family_reviews import reviewed_family_catalog, validate_reviews, validate_scope, validate_review_append, SCHEMA, SCOPED_SCHEMA


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


class ScopedFamilyReviewTest(FamilyReviewTest):
    def setUp(self):
        super().setUp()
        self.scope = {"parameters": {"n": {"min": "4", "max": "4"}},
                      "coefficients": ["Z", "F2"], "degrees": {"min": "0", "max": "8"},
                      "components": ["homology", "cohomology", "multiplication"]}

    def project(self, reviews):
        return reviewed_family_catalog(self.catalog, {"schema_version": SCOPED_SCHEMA, "reviews": reviews})

    def partial(self, **changes):
        return {**self.review, "scope": copy.deepcopy(self.scope), **changes}

    def test_partial_acceptance_never_promotes_whole_rule(self):
        r = self.project([self.partial()])["rules"][0]
        self.assertEqual(r["human_review_state"], "human_review_pending")
        self.assertEqual(r["human_reviews"], [])
        self.assertEqual(r["scoped_review_state"], "scoped_human_reviewed")
        self.assertEqual(r["scoped_human_reviews"][0]["scope"], self.scope)
        broad = {"parameters": {"n": {"min": "0", "max": None}},
                 "coefficients": ["Z", "Q", "F2", "F3", "F5", "F7", "F11"],
                 "degrees": {"min": "0", "max": None},
                 "components": ["homology", "cohomology", "multiplication"]}
        # No implicit union/promotion, even if a structured scope covers everything.
        self.assertEqual(self.project([self.partial(scope=broad)])["rules"][0]["human_review_state"], "human_review_pending")

    def test_scoped_concern_stays_visible_beside_whole_acceptance(self):
        concern = self.partial(id="narrow-concern", reviewer="Another human", verdict="reject")
        r = self.project([self.review, concern])["rules"][0]
        self.assertEqual(r["human_review_state"], "human_reviewed")
        self.assertEqual(r["scoped_review_state"], "scoped_human_concern")
        self.assertEqual(r["human_reviews"], [self.review])
        self.assertEqual(r["scoped_human_reviews"], [concern])

    def test_stale_scope_and_corrected_scope_preserve_history(self):
        old = self.partial()
        correction = self.partial(id="review-2", supersedes=old["id"], verdict="needs-evidence")
        r = self.project([old, correction])
        self.assertEqual(r["rules"][0]["scoped_human_reviews"], [correction])
        self.assertEqual(r["review_history"], [old, correction])
        for field, changed in (("content_sha256", "b" * 64), ("version", "2"), ("id", "another-rule")):
            catalog = copy.deepcopy(self.catalog)
            catalog["rules"][0][field] = changed
            r = reviewed_family_catalog(catalog, {"schema_version": SCOPED_SCHEMA, "reviews": [old, correction]})
            self.assertEqual(r["rules"][0]["scoped_human_reviews"], [])
            self.assertEqual(r["rules"][0]["scoped_review_state"], "none")
            self.assertEqual(len(r["review_history"]), 2)

    def test_legacy_document_remains_compatible_but_cannot_smuggle_scope(self):
        old = {"schema_version": SCHEMA, "reviews": [self.review]}
        new = {"schema_version": SCOPED_SCHEMA, "reviews": [self.review]}
        self.assertEqual(reviewed_family_catalog(self.catalog, old), reviewed_family_catalog(self.catalog, new))
        with self.assertRaises(ValueError):
            validate_reviews({"schema_version": SCHEMA, "reviews": [self.partial()]})

    def test_rejects_malformed_or_ambiguous_scope(self):
        changes = [
            {"parameters": {}}, {"parameters": {"n": {"min": "5", "max": "4"}}},
            {"parameters": {"n": {"min": "04", "max": "4"}}},
            {"parameters": {"n": {"min": 4, "max": 4}}},
            {"parameters": {"n": {"min": "4", "max": "4", "step": "2"}}},
            {"parameters": {"n": {"min": "4", "max": "4"}, "m": {"min": "1", "max": "2"}}},
            {"degrees": {"min": "9", "max": "8"}}, {"degrees": {"min": "-1", "max": "8"}},
            {"degrees": {"min": None, "max": "8"}}, {"degrees": {"min": "0", "max": "Infinity"}},
            {"coefficients": []}, {"coefficients": ["F13"]}, {"coefficients": ["Z", "Z"]},
            {"components": []}, {"components": ["ring"]}, {"components": ["homology", "homology"]},
            {"components": [True]}, {"convention": "reduced"},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.project([self.partial(scope={**self.scope, **change})])
        for scope in (None, [], "n=4", {}, {"parameters": self.scope["parameters"]}):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                validate_scope(scope)

    def test_large_bounds_and_component_only_scopes(self):
        huge = "9" * 5000
        scope = copy.deepcopy(self.scope)
        scope["parameters"]["n"] = {"min": huge, "max": None}
        scope["degrees"] = {"min": huge, "max": "1" + "0" * 5000}
        scope["components"] = ["multiplication"]
        self.assertEqual(self.project([self.partial(scope=scope)])["rules"][0]["scoped_human_reviews"][0]["scope"], scope)

    def test_scope_does_not_grant_identity_or_correction_authority(self):
        for patch in ({"reviewer_role": "agent"}, {"reviewer": ""}, {"maintainer": ""},
                      {"validated_at": "2026-09-06"}, {"source_url": "https://example.com/issues/1"}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.project([self.partial(**patch)])
        for patch in ({"reviewer": "Impostor"}, {"rule_id": "another-rule"}):
            with self.assertRaises(ValueError):
                self.project([self.partial(), self.partial(id="review-2", supersedes="review-1", **patch)])
        self.catalog["rules"][0]["coefficients"] = ["Q"]
        with self.assertRaisesRegex(ValueError, "outside the exact rule"):
            self.project([self.partial()])

    def test_json_roundtrip_and_invalid_document_shapes(self):
        import json
        document = {"schema_version": SCOPED_SCHEMA, "reviews": [self.partial()]}
        self.assertEqual(validate_reviews(json.loads(json.dumps(document))), document["reviews"])
        for malformed in (None, [], {}, {"schema_version": [], "reviews": []},
                          {"schema_version": SCOPED_SCHEMA, "reviews": None}):
            with self.subTest(document=malformed), self.assertRaises(ValueError):
                validate_reviews(malformed)

    def test_append_only_transition_and_additive_schema_upgrade(self):
        old = {"schema_version": SCHEMA, "reviews": [self.review]}
        appended = {"schema_version": SCOPED_SCHEMA, "reviews": [self.review, self.partial(id="review-2")]}
        validate_review_append(old, appended)
        validate_review_append(appended, copy.deepcopy(appended))
        for current in (
            {"schema_version": SCOPED_SCHEMA, "reviews": []},
            {"schema_version": SCOPED_SCHEMA, "reviews": [{**self.review, "rationale": "rewritten"}]},
            {"schema_version": SCOPED_SCHEMA, "reviews": list(reversed(appended["reviews"]))},
        ):
            with self.assertRaisesRegex(ValueError, "append-only"):
                validate_review_append(old, current)
        with self.assertRaisesRegex(ValueError, "downgraded"):
            validate_review_append({"schema_version": SCOPED_SCHEMA, "reviews": [self.review]}, old)


if __name__ == "__main__":
    unittest.main()
