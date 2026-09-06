# Publishing a human family review

The workbench's **Review this family** link opens a prefilled GitHub Issue form.
The reviewer signs in and submits it themselves. Opening the form, submitting
feedback, running tests or receiving an agent report never changes human status.

## Maintainer checklist

1. Read the original issue on this repository. Confirm the actual human author,
   their intended display identity and verdict; do not attribute an agent's text
   or a quotation to a human who has not endorsed it.
2. Compare the rule ID, version and SHA-256 against the downloaded workbench
   rule. Confirm the review covers all listed n, degrees, coefficients, additive
   groups, ring products and completeness claims. A narrower review remains
   useful feedback but does not count as whole-rule acceptance in this version.
3. Append (never overwrite) a record to `family-reviews.json`, with these fields:
   `id`, `rule_id`, `rule_version` (string), `content_sha256`, `reviewer`,
   `reviewer_role: "human"`, `verdict` (`accept`, `reject`, `needs-evidence`),
   `scope: "entire_rule"`, `rationale`, `source_url` (original repository issue),
   `reviewed_at`, `maintainer`, `validated_at` (timezone-qualified ISO timestamps),
   and `supersedes` (`null` unless correcting an earlier record by that human).
4. Review the diff, run `python3 -m unittest tests.test_family_reviews`, rebuild
   the atlas, run the normal deterministic release checks and publish.

Schema validation checks integrity, not identity or mathematical expertise. The
maintainer must verify authorship and scope in step 1; there is no automatic
issue ingestion, trusted-user token or automatic approval workflow.

Only current, non-superseded reviews matching the exact rule version and content
hash apply. Changed rules return to **Human review pending**; older reviews stay
in the downloadable history. A matching rejection or needs-evidence verdict is
displayed as a human concern even when another reviewer accepted the rule.

The mathematical hash includes the evaluator implementation and cited rule
metadata. Implementation changes may conservatively require fresh review even
when an author believes the mathematics unchanged. Presentation-only changes
outside that binding do not silently erase mathematical reviews.

## Gabriel feedback for this cycle

David supplied a screenshot of Gabriel Ong requesting typeset knowls (including
Q and F_p), multiplication tables and exhaustiveness labels, and explicitly
asked to include it in this cycle. This is **product feedback**, not acceptance
of any mathematical rule or coverage claim. No human mathematical review has
been manufactured from the screenshot; the initial registry is empty.
