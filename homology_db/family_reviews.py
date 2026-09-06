"""Maintainer-published, exact-rule human reviews; never inferred from tests."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from urllib.parse import urlparse

REVIEW_PATH = Path(__file__).resolve().parents[1] / "docs/reviews/family-reviews.json"
SCHEMA = "homology-db.family-reviews/1"
SCOPED_SCHEMA = "homology-db.family-reviews/2"
COEFFICIENTS = frozenset({"Z", "Q", "F2", "F3", "F5", "F7", "F11"})
COMPONENTS = frozenset({"homology", "cohomology", "multiplication"})


def _bounds(value: object, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"min", "max"}:
        raise ValueError(f"{label} requires min and max")
    for key in ("min", "max"):
        bound = value[key]
        if key == "max" and bound is None:
            continue
        if not isinstance(bound, str) or not re.fullmatch(r"0|[1-9][0-9]*", bound):
            raise ValueError(f"{label} bounds must be canonical nonnegative decimal strings")
    lower, upper = value["min"], value["max"]
    # Compare arbitrarily large decimal integers without Python's int-string limit.
    if upper is not None and (len(lower), lower) > (len(upper), upper):
        raise ValueError(f"{label} min must not exceed max")


def validate_scope(scope: object, *, allow_scoped: bool = True) -> None:
    """Validate exact inclusive ordinary-unreduced scope, not review authority."""
    if scope == "entire_rule":
        return
    if not allow_scoped or not isinstance(scope, dict):
        raise ValueError("narrow review scope requires the version 2 structured format")
    if set(scope) != {"parameters", "coefficients", "degrees", "components"}:
        raise ValueError("narrow scope requires parameters, coefficients, degrees and components")
    parameters = scope["parameters"]
    if not isinstance(parameters, dict) or set(parameters) != {"n"}:
        raise ValueError("family review parameters require exactly n")
    _bounds(parameters["n"], "parameter n")
    _bounds(scope["degrees"], "degrees")
    for key, supported in (("coefficients", COEFFICIENTS), ("components", COMPONENTS)):
        values = scope[key]
        if not isinstance(values, list) or not values or any(not isinstance(v, str) for v in values):
            raise ValueError(f"scope {key} requires a nonempty list")
        if len(set(values)) != len(values) or not set(values) <= supported:
            raise ValueError(f"scope {key} contains duplicate or unsupported selections")


def validate_reviews(document: dict) -> list[dict]:
    if not isinstance(document, dict) or set(document) != {"schema_version", "reviews"} or not isinstance(document["schema_version"], str) or document["schema_version"] not in {SCHEMA, SCOPED_SCHEMA}:
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
        for key in required - {"supersedes", "scope"}:
            if not isinstance(review[key], str) or not review[key].strip():
                raise ValueError(f"family review needs {key}")
        if review["id"] in seen or review["reviewer_role"] != "human":
            raise ValueError("family reviews require unique IDs and explicit human authorship")
        if review["verdict"] not in {"accept", "reject", "needs-evidence"}:
            raise ValueError("invalid family review verdict")
        validate_scope(review["scope"], allow_scoped=document["schema_version"] == SCOPED_SCHEMA)
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
        whole = [review for review in matching if review["scope"] == "entire_rule"]
        scoped = [review for review in matching if review["scope"] != "entire_rule"]
        for review in scoped:
            if not set(review["scope"]["coefficients"]) <= set(rule.get("coefficients", COEFFICIENTS)):
                raise ValueError("review coefficients fall outside the exact rule coverage")
        # Keep the old fields strictly whole-rule: partial acceptance can never
        # upgrade old clients' whole-rule badges.
        rule["human_reviews"] = copy.deepcopy(whole)
        rule["scoped_human_reviews"] = copy.deepcopy(scoped)
        verdicts = {review["verdict"] for review in whole}
        rule["human_review_state"] = (
            "human_concern" if verdicts & {"reject", "needs-evidence"}
            else "human_reviewed" if "accept" in verdicts
            else "human_review_pending"
        )
        scoped_verdicts = {review["verdict"] for review in scoped}
        rule["scoped_review_state"] = (
            "scoped_human_concern" if scoped_verdicts & {"reject", "needs-evidence"}
            else "scoped_human_reviewed" if "accept" in scoped_verdicts
            else "none"
        )
    return result


def validate_review_append(previous: dict, current: dict) -> None:
    """Validate a registry revision against its prior trusted revision.

    A standalone JSON file cannot prove history. Maintainer/release tooling can
    supply the prior committed document to reject deletion, mutation, reorder,
    and schema downgrade while permitting the additive /1 -> /2 transition.
    """
    old = validate_reviews(previous)
    new = validate_reviews(current)
    if current["schema_version"] == SCHEMA and previous["schema_version"] == SCOPED_SCHEMA:
        raise ValueError("family review schema cannot be downgraded")
    if new[:len(old)] != old:
        raise ValueError("family review history must be preserved exactly as an append-only prefix")
