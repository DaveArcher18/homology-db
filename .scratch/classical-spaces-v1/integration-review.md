# Independent classical integration review

Reviewer: `/root/math_review`; no implementation files authored by reviewer.
Date: 2026-09-06. State: all four findings repaired and independently rechecked;
no remaining integration blocker.

## Findings and resolutions

1. **Accepted spectrum release exceeds the existing size cap.** The public
   preview fits, but `test_structured_acceptance_build_is_deterministic_and_gate_ready`
   fails because the accepted export is 5,243,059 bytes against a 5,242,880-byte
   limit. The accepted path must retain enough headroom for its additional
   evidence rather than relying on the preview's smaller size.
   **Resolved:** unused styling was removed; the accepted-release regression
   now passes through both deterministic builds and the release gate.
2. **Downloaded space JSON omits the new source context.** The initial
   `serializedSpaceRecord` serializes the space alone. Its cohomology records
   reference `hatcher2002`, while the source catalog and rational derivation
   rule are only present in the enclosing atlas. The download needs additive
   source and snapshot context so these references remain resolvable.
   **Resolved:** the serializer adds `export_context` with the complete classical
   source catalog, rationalization rule, snapshot ID, and source hashes while
   preserving existing space fields at the top level.
3. **Q completeness/provenance are not validated.** Mutating the candidate to
   delete all Q rows, replace one dimension with 999, or replace a Q row's
   `input_assertion_id` with `missing-assertion` each passes `validate_read_model`.
   The legacy coefficient loop excludes Q. Validate the core Q projection
   against its integral inputs, including convention, IDs, and evidence.
   **Resolved:** the validator compares every core Q row against the exact
   regenerated integral projection and disallows undeclared noncore Q rows.
4. **Classical metadata equality is weaker than correctness.** Setting
   `record_count=0` in both metadata copies passes validation. The known
   record/space counts, IDs, coefficients, schema, and review state should be
   checked against the validated corpus rather than just compared between copies.
   **Resolved:** both copies must match metadata freshly derived from the
   validated corpus and the fixed qualified source catalog.

Actual formulas and Q dimensions in the reviewed candidate are correct. The
third and fourth findings concern the reliability of the release integrity gate.

## Checks already passed

- Reviewed all mathematical records, as documented in `mathematical-review.md`.
- Parsed 343 exported classical formula, relation, and basis TeX strings using
  the actual frontend parser; none require unsupported commands.
- Reviewed missing-data display: an absent ring becomes “Not recorded”, numeric
  zero requires exact group data, and cohomology is independent of reduced
  homology. The complete finite ring coverage is validated server-side.
- Confirmed the new Python data file is included in the implementation source
  hash and that the spectrum acceptance still binds the candidate source inputs.
- Inspected the shortened source/derivation prose; mathematical locators,
  characteristic qualifications, and human-review-pending state are preserved.

## Closure evidence

- `python3 -m unittest discover -s tests -p 'test_classical*.py' -v`:
  **15 passed**, including the reproduced Q and metadata mutation cases.
- `python3 -m unittest discover -s tests -p 'test_steenrod_static_atlas.py'
  -k structured_acceptance -v`: **passed** in 41.658 seconds. This independently
  exercises two accepted exports, byte equality, source/evidence bindings,
  materialization, the existing size cap, and the accepted release gate.
- Executed the actual `serializedSpaceRecord` function against all 42 candidate
  spaces: preserved identity and context in every download; all **65 ring source
  references and 88 Q parent assertions/rule references resolve**.
- JavaScript syntax checks pass. Candidate validation passes. The candidate's
  source-input hash equals the current implementation hash, and its classical
  content hash equals the final generated records.

Reviewed preview: `/tmp/homology-classical-candidate.html`, **5,238,233 bytes**,
SHA-256 `f716c594a65917fc68fe8fdd5a89c3f4189a5448a07471fb49c9a845f50d5cb1`.

Exact final implementation input SHA-256:
`8234c3794ca3d18070a9eb50161ba251da30dff75b6d55469ac4c2c714676388`.

Final small follow-up: `.textbook-space-link` adds `gap: 0.35rem` to separate
the symbol and label. Removing just that line from the current CSS reproduces
the previously reviewed CSS hash exactly; all other reviewed source-file
hashes remain unchanged. This spacing-only change has no mathematical or
release-path effect. The parent run will rebuild and check the final artifact;
the preview hash above identifies the preceding fully exercised candidate.

```text
homology_db/classical.py
e4d9cf5287f6825e3d8136b8994296de5e351677bb88dccde65a52f99b38ca57
scripts/export_static_atlas.py
dfa12299b07dad4c0e3c66b6eeec7900863c38705ee5d434b03cfe0f879b6a15
static_atlas/atlas.js
06fb406a65d55c1242090013abc977460f6f23b2a4816138475378b214a8c756
static_atlas/presentation.js
45b0f0563226037e5e7845507cd09db73c561e6e50661ab58343292f9b8df1c7
static_atlas/atlas.css
928b040a1943c91e1f01caec41d23ef17e704b49110f5a853248cb80ca4f05ff
static_atlas/index.template.html
1829956df2731fa86540fbcdaa311bd2f059f6924f8380c087dffb4412318dbf
```

Browser behavior and the full regression run remain with the coordinating
agent; this review does not independently claim those results. A final clean
source commit will intentionally change source revision/time metadata in the
published artifact; preserve the implementation input hash or re-review changed
inputs. Human mathematical review remains pending.
