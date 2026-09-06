# Publishing a human family review

The workbench's review panel opens a prefilled GitHub Issue form or copies a
review packet for discussion. A copied packet is not a published review.
Normally the reviewer signs in and submits it themselves; the explicitly
endorsed relay exception is described below. Opening the form, submitting
feedback, running tests or receiving an agent report never changes human status.

## Maintainer checklist

1. Read the original issue on this repository. Confirm the actual human author,
   their intended display identity and verdict; do not attribute an agent's text
   or a quotation to a human who has not endorsed it.
2. Compare the rule ID, version and SHA-256 against the downloaded workbench
   rule. Confirm the exact n interval, coefficients, degrees and components the
   human actually checked. Do not widen their scope while recording it. A
   narrower review is published with its scope, never as whole-rule acceptance.
3. Append (never overwrite) a record to `family-reviews.json`, with these fields:
   `id`, `rule_id`, `rule_version` (string), `content_sha256`, `reviewer`,
   `reviewer_role: "human"`, `verdict` (`accept`, `reject`, `needs-evidence`),
   `scope` (see below), `rationale`, `source_url` (original repository issue),
   `reviewed_at`, `maintainer`, `validated_at` (timezone-qualified ISO timestamps),
   and `supersedes` (`null` unless correcting an earlier record by that human).
4. Review the diff, run `python3 -m unittest tests.test_family_reviews`, rebuild
   the atlas, run the normal deterministic release checks and publish.

When validating a registry edit, pass the previous committed JSON and the new
JSON to `validate_review_append(previous, current)`. It verifies that the old
record list is an unchanged prefix, permits `/1` → `/2`, and rejects deletion,
rewriting, reordering or schema downgrade. A standalone current JSON file cannot
establish append-only history; the previous document must come from trusted
version control, not the proposed submission.

Schema validation checks integrity, not identity or mathematical expertise. The
maintainer must verify authorship and scope in step 1; there is no automatic
issue ingestion, trusted-user token or automatic approval workflow.

Only current, non-superseded reviews matching the exact rule version and content
hash apply. Changed rules return to **Human review pending**; older reviews stay
in the downloadable history. A matching rejection or needs-evidence verdict is
displayed as a human concern even when another reviewer accepted the rule.

## Additive review format and narrow scope

Existing `homology-db.family-reviews/1` documents and their `"entire_rule"`
records remain valid unchanged. To append a structured narrow review, change
only the document schema marker to `homology-db.family-reviews/2`, retaining
every old record exactly, and append the new record. Version 2 accepts both
old whole-rule scopes and structured scopes. Version 1 rejects structured scopes
so old clients cannot silently interpret them as whole-rule acceptance.

For example, a review of RP⁴ over ℤ and F₂, in degrees 0–8:

```json
{
  "parameters": {"n": {"min": "4", "max": "4"}},
  "coefficients": ["Z", "F2"],
  "degrees": {"min": "0", "max": "8"},
  "components": ["homology", "cohomology", "multiplication"]
}
```

- All four scope fields are required. Bounds are inclusive canonical decimal
  strings (no signs/leading zeros); `max: null` means every integer above min.
  Equal n bounds describe one instance. These are finite n, even when the range
  is unbounded; n=∞ is not part of the rule.
- Coefficients are a nonempty, duplicate-free subset of Z, Q, F2, F3, F5, F7,
  F11. Components are a nonempty subset of homology, cohomology, multiplication.
- Homology/cohomology mean the ordinary **unreduced** groups in the selected
  degrees. A review packet from a reduced display must state this explicitly.
  For multiplication, the degree interval covers pairs whose two input degrees
  **and output degree** lie in that interval. It does not claim products with
  inputs or outputs outside it. Ring presentations/all-degree rules require
  the corresponding full scope, not an inference from a small product table.
- Each scope includes exactness/coverage only within its declared region.
  Arbitrary subset patterns, local systems, reduced claims, and other parameters
  are not supported by this format; preserve those as feedback instead.
- Only the explicit string `"entire_rule"` contributes to whole-rule status.
  Structured scopes remain separate even if one scope or several scopes could
  cover the whole rule; the projection does not infer a union-based approval.

The exported `human_reviews` and `human_review_state` remain whole-rule-only
for old consumers. New `scoped_human_reviews` contains exact current narrow
records; `scoped_review_state` is `none`, `scoped_human_reviewed`, or
`scoped_human_concern`. A narrow rejection/needs-evidence takes precedence over
narrow acceptance, but is not falsely presented as a whole-rule review. Always
display the narrow record's actual scope and verdict. If a whole-rule acceptance
coexists with a scoped concern, both must be visible; do not show an unqualified
green approval and hide the concern. Never apply a narrow verdict to the current
display without checking every scope axis.

Corrections append a new ID and use `supersedes` to retire the earlier complete
review record by that same human on that same rule. A correction may narrow
scope, but the old larger acceptance is then retired entirely; it is not kept
active in a residual region. Old, stale and superseded reviews stay in history.
No identity is established by setting `reviewer_role: "human"`: the maintainer
must verify the human's original endorsement and exact scope. If a human cannot
use GitHub, the packet may be relayed into a repository issue only with their
explicit endorsement of the published text and attribution. Do not fabricate
reviews from an agent-written packet or an informal conversation.

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
