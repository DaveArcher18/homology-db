# Independent scoped review workflow audit

Reviewer: `/root/family_math_review`, 2026-09-06. This agent did not implement
the scoped-review backend or UI. Scope is F-01's human-review workflow only;
this is not acceptance of the same agent's teaching content or new ring records.

## Verdict

PASS for the exact inspected implementation, with the operational limitation
below. No manufactured human verdict exists in the production registry. Browser
interaction and live publishing are assigned separately to root.

## Exact inspected hashes

- `homology_db/family_reviews.py`: `b7ea709c25c394ed774a4dfb6cdc931a6874d5053e700ebcb010a0e0c1aa1467`
- `static_atlas/workbench.js`: `f007a0bfad6bc881fef6d79ba6642b31ad4312810cb58ebd9c38c8e9640ec52c`
- `.github/ISSUE_TEMPLATE/family-review.yml`: `d77f3a96530f4d71ce97a3905790e257c26929a07d7878248d87297cf25d4dba`
- `docs/reviews/FAMILY_REVIEW_GUIDE.md`: `204f3b7d97893311b8888187bb4b7211e7db91b2bfd3a7eebfe27472bdf17ba4`
- `docs/reviews/family-reviews.json`: `86e36696fccac20b63a81f7c4d96923d8aee3ebe2ecc8fdf1ad68142d71cfcba`

## Attempts to falsify

Executed `python3 -m unittest tests.test_family_reviews -v`: 19 tests pass.
Additionally ran independent in-memory fixtures against the actual generated
family catalog: single-instance/single-field/homology-only acceptance leaves
whole-rule status pending; independently changed ID, version, and content hash
each remove applicability without publishing an acceptance. Fixtures were not
persisted. Compared the actual current registry with the trusted HEAD version
through `validate_review_append`; unchanged empty history passes.

Source inspection confirms:

- Exact ID/version/hash and non-superseded membership gate every applicable
  record. Whole-rule fields accept only the explicit entire_rule string; even
  a structured all-axis scope is not promoted implicitly.
- Narrow concerns are not masked by narrow acceptances. Whole acceptance plus
  narrow concern is rendered with a separate top-level concern warning and an
  exact-scope detail record, rather than pretending the concern applies to the
  current instance or omitting it.
- Scoped intervals use canonical arbitrary-size decimal strings and reject
  malformed, reversed, unsupported and duplicate axes. Corrections require an
  earlier same-human/same-rule record, retiring it completely while preserving
  history. Legacy /1 rejects structured scopes; additive /2 preserves old forms.
- UI defaults to the current instance and displayed degree window. Users can
  select coefficient/component subsets or explicitly select the whole rule.
  Invalid/empty selections disable both form link and copy action.
- Copied packets bind the exact rule identity and sources, retain canonical
  scope JSON, explain ordinary unreduced conventions, and specify that
  multiplication requires both input degrees and output degree in the interval.
  Copying does not submit or mutate review state. GitHub submission explicitly
  requires human confirmation and later maintainer validation.
- The guide forbids scope widening, fictitious identity, and acceptance inferred
  from agent feedback. Relay into a public issue requires the human's explicit
  endorsement; current authorization does not send outreach.

## Operational limitation (not a current publication blocker)

Append-only revision comparison is implemented and tested by
`validate_review_append(previous,current)` and documented in the maintainer
checklist. No automatic release-script caller was found. Consequently history
preservation depends on the maintainer supplying the prior trusted version; do
not describe it as an automatic release gate. A current standalone document
cannot prove its own history. The actual production history is empty and
unchanged in this candidate, and its append comparison was checked above.

Schema validation establishes structural integrity, not real-world human
identity, expertise, or review quality. Those remain the explicitly documented
maintainer responsibilities; no authentication/automatic ingestion is claimed.
