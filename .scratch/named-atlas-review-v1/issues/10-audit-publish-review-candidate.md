Type: task
Status: open
Claimed by:
Claimed at:
Blocked by: 09

# Audit and publish the review candidate

## Question

Does a clean checkout pass migrations, deterministic rebuild and export,
schema and SQLite integrity, source-pin and grounding audits, the 1,159-Model
workload, full tests, code review, and the adversarial QA gate with no open
critical defect, so the onboarding can be updated and reviewers invited?

## Acceptance criteria

- A clean checkout rebuilds a byte-identical Snapshot and Current projection.
- Every selected source, artifact, computation run, assertion, and dependency
  hash resolves from that checkout.
- Migration, schema-integrity, corpus-count, source-pin, grounding,
  performance, unit, and adversarial-agent checks pass with no unsupported
  mathematical claim or open critical defect.
- The naming audit proves permanent public labels, documented label syntax,
  alias/identity separation, and stable definition references across a
  deterministic rebuild.
- Only after this audit passes may onboarding invite Gabriel Ong or Dan
  Isaksen; the hosted form remains a separate later decision.
