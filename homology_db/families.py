"""Versioned, source-bound ordinary family rules (not human acceptance)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

FAMILY_SCHEMA_VERSION = "homology-db.family-rules/1"
FAMILY_COEFFICIENTS = ("Z", "Q", "F2", "F3", "F5", "F7", "F11")
_ROOT = Path(__file__).resolve().parents[1]
_SOURCE_URL = "https://pi.math.cornell.edu/~hatcher/AT/AT.pdf"


def family_catalog() -> dict:
    """Bind every mathematical rule to metadata and the exact evaluator bytes.

    Human review records are maintained independently by the release layer;
    this function never treats source provenance as a reviewer verdict.
    """
    evaluator = (_ROOT / "static_atlas" / "families.js").read_bytes()
    descriptions = (
        ("sphere", "Spheres", "Corollary 2.14, p. 114; Examples 3.12–3.14, pp. 213–214",
         "Sphere homology, the coefficient theorem, and degree constraints give the positive-dimensional square-zero ring. S^0 has two points and the product ring R × R, with e=(1,0) and unit=(1,1)."),
        ("real_projective_space", "Real projective spaces", "Example 2.42, p. 144; Theorems 3.1 and 3.5, pp. 198, 203; Example 3.12, p. 213; Theorem 3.19, p. 220; coefficient exact sequence §3.E, p. 303; Corollary 3E.4, p. 306",
         "The cellular differential alternates 0 and 2, determining integral groups and their coefficient changes. Mod-2 cup products are truncated polynomial. The integral ring is a deduction: the coefficient exact sequence makes reduction injective on the positive even-degree Z/2 groups (there is no 4-torsion). The integral degree-2 class therefore reduces to the nonzero square of the mod-2 degree-1 class, so its nonvanishing powers give the even-degree order-two classes through dimension n. Odd-dimensional real projective space also has a free integral top class; dimension forces its positive-degree products to vanish. Odd-characteristic and rational results follow by inverting 2."),
        ("complex_projective_space", "Complex projective spaces", "Example 2.35, p. 140; Example 3.12, p. 213; Theorem 3.19, p. 220; Corollary 3A.6(a), p. 266",
         "One cell in each even degree through 2n gives free integral homology. The integral degree-2 cup generator has powers through degree 2n; truncation occurs at its (n+1)st power. Freeness gives the same truncated polynomial presentation after changing coefficients."),
    )
    rules = []
    for family, name, locator, derivation in descriptions:
        rule = {
            "id": f"ordinary-{family}", "family": family, "version": "1", "name": name,
            "parameter_scope": "Every finite nonnegative integer n; every nonnegative degree d",
            "coefficients": list(FAMILY_COEFFICIENTS),
            "convention": "ordinary_unreduced",
            "coverage": {key: "complete_all_degrees" for key in ("homology", "cohomology", "multiplication")},
            "sources": [{"title": "Allen Hatcher, Algebraic Topology (2002)", "url": _SOURCE_URL, "locator": locator}],
            "derivation": derivation,
            "evaluator_sha256": hashlib.sha256(evaluator).hexdigest(),
        }
        canonical = json.dumps(rule, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        rule["content_sha256"] = hashlib.sha256(canonical + b"\n" + evaluator).hexdigest()
        rules.append(rule)
    return {"schema_version": FAMILY_SCHEMA_VERSION, "rules": rules}
