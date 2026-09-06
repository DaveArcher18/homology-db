Type: task
Status: resolved
Claimed by: /root
Claimed at: 2026-09-06T09:01:41Z
Blocked by:

# Build, verify, and publish the classical student reference

Implement the accepted spec end to end: 65 field-cohomology records on 13 existing
spaces, a rings-first student interface, preserved existing homology and stable
routes, deterministic export, and publication to the existing Pages site.

Ownership: cohomology_data owns the algebra module and tests; student_ui owns
static interface sources; math_review independently qualifies and reviews the
mathematics; root owns exporter integration, cross-system verification and release.

User authority covers commits, push/merge and deployment after primary-source
qualification, automated checks and independent agent review. Human review is
pending, not a release gate. No external outreach or purchases.

Acceptance is the spec's test and browser checklist, an independently reviewed
candidate, a clean deterministic source-bound artifact under 5 MiB, the existing
stable-preview release gate, and a verified live response matching the committed
artifact. Preserve unrelated untracked scratch artifacts.

## Answer

Completed and published. Source `2e576bd` plus the one-line icon packaging fix
`a59e40a`; final artifact `0cc3e66`. PR #3 and Pages run `34025164986` succeeded.
The live file matches the committed artifact at SHA-256
`04e7a9d069eb1939e422f7110834fa4acbf76a996c1b2f6967e5047f7e80b3aa`.
The 169-test suite passes with three optional-consumer skips; the final icon change
also passes 17 static tests and deterministic release checks. All 65 field views,
42 space routes, 49 spectrum routes and responsive browser checks pass live with
no console errors. Mathematical/integration/packaging review passed independently.
Human mathematical review remains pending. No core ring gaps remain.
