"""Maintainer-published, exact-rule human reviews; never inferred from tests."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from urllib.parse import urlparse

REVIEW_PATH = Path(__file__).resolve().parents[1] / "docs/reviews/family-reviews.json"
SCHEMA = "homology-db.family-reviews/1"


def validate_reviews(document: dict) -> list[dict]:
    if set(document) != {"schema_version", "reviews"} or document["schema_version"] != SCHEMA:
        raise ValueError("invalid family review document")
    if not isinstance(document["reviews"], list):
        raise ValueError("family reviews must be an append-only list")
    seen = {}
    for review in document["reviews"]:
        required = {"id", "rule_id", "rule_version", "content_sha256", "reviewer",
                    "reviewer_role", "verdict", "scope", "rationale", "source_url",
                    "reviewed_at", "maintainer", "validated_at", "supersedes"}
        if not isinstance(review, dict) or set(review) != required:
            raise ValueError("invalid family review fields")
        for key in required - {"supersedes"}:
            if not isinstance(review[key], str) or not review[key].strip():
                raise ValueError(f"family review needs {key}")
        if review["id"] in seen or review["reviewer_role"] != "human":
            raise ValueError("family reviews require unique IDs and explicit human authorship")
        if review["verdict"] not in {"accept", "reject", "needs-evidence"}:
            raise ValueError("invalid family review verdict")
        if review["scope"] != "entire_rule":
            raise ValueError("this review interface supports whole-rule reviews only")
        if not re.fullmatch(r"[0-9a-f]{64}", review["content_sha256"]):
            raise ValueError("family review must bind an exact content hash")
        parsed = urlparse(review["source_url"])
        if parsed.scheme != "https" or parsed.netloc != "github.com" or not re.fullmatch(
            r"/DaveArcher18/homology-db/issues/[1-9][0-9]*", parsed.path, re.IGNORECASE
        ) or parsed.query or parsed.username:
            raise ValueError("family review must cite its repository GitHub issue")
        for key in ("reviewed_at", "validated_at"):
            from datetime import datetime
            try:
                timestamp = datetime.fromisoformat(review[key].replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError("missing timezone")
            except ValueError as error:
                raise ValueError("family review timestamps require ISO dates with timezone") from error
        prior = review["supersedes"]
        if prior is not None and (
            not isinstance(prior, str) or prior not in seen
            or seen[prior]["rule_id"] != review["rule_id"]
            or seen[prior]["reviewer"] != review["reviewer"]
        ):
            raise ValueError("review corrections must identify an earlier review by the same human")
        seen[review["id"]] = review
    return document["reviews"]


def reviewed_family_catalog(catalog: dict, document: dict | None = None) -> dict:
    if document is None:
        document = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    reviews = validate_reviews(document)
    superseded = {review["supersedes"] for review in reviews}
    result = copy.deepcopy(catalog)
    result["review_history"] = copy.deepcopy(reviews)
    for rule in result["rules"]:
        matching = [review for review in reviews if review["id"] not in superseded
                    and review["rule_id"] == rule["id"]
                    and review["rule_version"] == str(rule["version"])
                    and review["content_sha256"] == rule["content_sha256"]]
        rule["human_reviews"] = copy.deepcopy(matching)
        verdicts = {review["verdict"] for review in matching}
        rule["human_review_state"] = (
            "human_concern" if verdicts & {"reject", "needs-evidence"}
            else "human_reviewed" if "accept" in verdicts
            else "human_review_pending"
        )
    return result
