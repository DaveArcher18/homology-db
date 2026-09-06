# Independent integration review

Reviewer: `/root/family_engine` (agent; not a human mathematical reviewer).
Scope: root-authored review registry validation, GitHub review form and maintainer guide,
exporter `/5` integration, and the 6 MiB release budget. Read-only source audit;
UI and mathematical evaluator are outside this report's independent scope.

Audited file SHA-256 values:

- `homology_db/family_reviews.py`: `c147e114a4252270564839f06d61ebfee92db5e0ebba69c5fd9e0a3ee26274e5`
- `.github/ISSUE_TEMPLATE/family-review.yml`: `dc5d1b926aa761645e14c6d79816d0b92750efe8c53c08162b9080501c9ef51b`
- `docs/reviews/FAMILY_REVIEW_GUIDE.md`: `d3635a1ddd7050bad2b1cd79ae1f30e0a2a887c2dc3657bbc63a0587494f8d79`
- `scripts/export_static_atlas.py`: `456ca2b6c402c2465a09078e29a72443682e6ad17a514b8546d6180287ef0c94`
- `scripts/verify_steenrod_release.py`: `e88813d4d0c6ad809086528a781f72de51b4d717e33189c966362120f1c213b6`

## Finding requiring correction

1. **Legacy `/4` classical metadata validation regressed.**
   `validate_read_model` guards classical validation with equality to
   `READ_MODEL_VERSION`, now `/5`. The checked-in `/4` atlas with its
   `classical.content_sha256` replaced by 64 zeroes is accepted. Preserve the
   classical checks for both `/4` and `/5`. Retain family checks on `/5` and
   reject family data on older schemas so a schema downgrade cannot bypass the
   new binding. This is an integrity regression rather than evidence that the
   current default `/5` build contains false data.

## Checks and conclusions

- Exact rule ID, version, and content hash qualify active human reviews.
  Changed hashes return to pending; prior reviews remain in exported history.
- Rejections and needs-evidence verdicts take precedence over acceptance.
  Corrections must reference earlier records by the same named human and rule.
- The registry starts empty. Schema validation cannot prove identity or
  expertise; the guide explicitly requires maintainer confirmation of actual
  authorship, scope and endorsement. There is no automatic issue ingestion or
  status-changing client write. GitHub-form text is feedback until publication.
- Sources and rule evaluator content are bound independently of review state.
  Review registry and validation code are also release source-hash inputs.
- The form requests exact IDs/hash, scope, references, verdict and reasoning;
  it does not claim submission itself constitutes published acceptance.
- Gabriel's screenshot is explicitly treated as product feedback, not a
  mathematical verdict. Spectrum acceptance authority is unchanged.
- Exporter and spectrum gate share the 6 MiB cap. The static single-file delivery
  remains intact; no external loading or newly privileged dependency is added.
- `python3 -m unittest tests.test_family_reviews tests.test_family_atlas -v`:
  8 tests pass, including current-catalog tamper rejection and pending status.
  Those tests did not detect the historical-schema regression; a regression
  case is needed alongside its correction.

## Correction verification

The primary agent corrected the legacy-schema guard. The final exporter hash
is `456ca2b6c402c2465a09078e29a72443682e6ad17a514b8546d6180287ef0c94`
(the hash inventory was captured after that concurrent correction).
An added regression test proves that `/4` still validates its classical corpus,
rejects a forged classical hash, and cannot carry `/5` family data. The combined
review/integration suite now passes **9 tests**. Additional direct checks reject
cross-author and cross-rule supersession, and show that a correction bound to a
different hash cannot leave the old version marked reviewed; both records remain
in history. Ordering is append order, not an inference from user-entered dates;
date truth and reviewer identity remain the explicit maintainer responsibility.

Outcome: **no remaining identified integration blocker** within this scope.
Only this report and the separately authorized integration regression test were
edited by the reviewer. This is independent agent integration review, not human
mathematical acceptance or a whole-product/browser verification.
