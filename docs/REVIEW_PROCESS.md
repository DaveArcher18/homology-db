# Append-only review process

This file records mathematical, provenance, and product review of Homology DB.
It is designed to remain readable by a person and mechanically extractable by
later automation. Entries are appended in chronological order. A correction
adds a new entry that names the earlier record; it never edits the earlier
review verdict or erases the evidence that produced it.

This is a process log, not a source of mathematical truth. A reviewed claim
still belongs in the assertion ledger with its own evidence and lifecycle. A
review entry records what a reviewer saw, how they evaluated it, and what must
happen next.

## Record shapes

Every entry declares a `record_kind`. A `database-run` records all fields
below, using `unknown` or `not-applicable` rather than silently omitting a
value:

```text
review_id:
record_kind: database-run
recorded_at:
reviewer:
reviewer_role: human / agent / deterministic-check
agent_runtime:
repository_commit:
reviewed_content_hashes:
working_tree_state:
snapshot_id:
cohort_or_manifest:
prompt_or_protocol:
exact_commands:
public_operations:
source_pins:
assertion_ids:
evidence_ids:
typed_limitations:
capability_states:
claim_or_edge_verdicts:
follow_up_tickets:
supersedes_or_corrects:
notes:
```

A `human-concern` instead records the reviewer, commit and Snapshot seen,
claim under review, verdict, trigger, follow-up, and correction link. A
`source-audit` records the reviewer/runtime, commit, exact source coordinates,
audit conclusion, human-review state, follow-up, and correction link. A
`product-feedback` record preserves the reviewer, exact message times when
known, source, suggestions, disposition, and follow-up without pretending it
is a mathematical verdict. A `decision` records its owner, inputs, chosen
policy and gates. These entry types do not invent database fields that do not
apply to them.

For each substantive mathematical claim or proposed implication edge, a human
reviewer records exactly one of:

- `accept`: clear and adequately grounded for the stated Snapshot and scope;
- `reject`: false, unsafe, conventionally wrong, or contradicted by evidence;
  or
- `needs-evidence`: possibly correct, but not adequately grounded.

`pending-human-review` is a workflow state, not a verdict. Automated checks
may establish that an envelope is complete or a command succeeded, but they
do not silently supply the human verdict. A later review appends the missing
claim-level verdicts.

An implication-edge record additionally names its source nodes, target node,
relation, hypotheses, cited justification, and whether each hypothesis was
actually established. Equal invariants alone never create an identity,
homeomorphism, or homotopy-equivalence edge.

## Correction and concurrency rules

1. Never change or delete an earlier review entry after it has been shared.
2. Append a correction with a new `review_id` and
   `supersedes_or_corrects: <old-id>`.
3. Retain rejected claims, typed limitations, conflicting verdicts, and the
   exact evidence originally reviewed.
4. Bind every database review to one `snapshot_id`; a mismatch is an integrity
   failure, not a result to reconcile manually.
5. Record the repository commit and prompt/protocol version separately from
   the Snapshot. They are different reproducibility axes.
6. Never infer an absent identifier. Use `none-returned` or `unknown`.
7. Give independent reviewers independent records even when they inspect the
   same claim.

## Review `review-2026-07-12-001`: fixed database-connected run

```text
review_id: review-2026-07-12-001
record_kind: database-run
recorded_at: 2026-07-12T11:29:54+02:00
reviewer: Codex database-connected review agent
reviewer_role: agent
agent_runtime: Codex task; exact model/runtime identifier not retained
repository_commit: e7ff854 (review pack prepared); completion recorded by aa18ebe
reviewed_content_hashes: qa/review/questions-v1.json sha256 3dfea7332cb0aac7c11cec172cbc9b481b75b847dfefda2a97b4fa5862827562; docs/REVIEW_AGENT_RUN.md sha256 0256f57ef0559eea04f820be173f40800693becb4df335d391db2a17289e2791
working_tree_state: clean before and after
snapshot_id: preview-5ea7db464f937061
cohort_or_manifest: local-preview-60; qa/review/questions-v1.json schema version 1
prompt_or_protocol: docs/REVIEW_AGENT_RUN.md
exact_commands: preflight below; exact chronological JSON payload trace not retained in the repository
public_operations: resolve_subject, read_homology, query_examples, expand_evidence
source_pins: not-applicable; the answer agent was prohibited from web retrieval
assertion_ids: grounding inventory below
evidence_ids: grounding inventory below
typed_limitations: unsupported_coefficient; not_found; subject_not_resolved
capability_states: exact or explicit not_computed representatives; identity-only maps; nonidentity maps not_computed
claim_or_edge_verdicts: R01-R12 pending-human-review
human_review_state: pending-human-review
follow_up_tickets: ticket 08; ticket 12
supersedes_or_corrects: none
notes: full readable answer retained in the named Codex task
```

Exact preflight commands:

```bash
python3 -m unittest discover -s tests -v
python3 -m homology_db --db /tmp/homology-db-review.sqlite3 demo
```

Every mathematical call used the same database path and this shell envelope:

```bash
python3 -m homology_db --db /tmp/homology-db-review.sqlite3 tool '<JSON>'
```

The run answered R01--R12 in order, reported 12/12 tests passing, used one
Snapshot throughout, and expanded every evidence record used in a lookup or
comparison. Its final response is retained in Codex task
`019f55a2-6b0b-7711-86cf-e716981cb01e`, titled `Review Homology DB answers`.
That task is the complete human-readable claim-to-ID audit; this entry records
its reproducibility coordinates without pretending the agent approved itself.
Its final response lists the operations used for each question, but that
presentation can repeat an earlier shared lookup and is not an exact
chronological tool trace. Review `review-2026-07-12-005` is a
coverage-equivalent replay, not evidence of review 001's original call order.

### Grounding inventory

The following exact assertion IDs grounded displayed group claims:

- R01: `preview:assertion:nonorientable_surface:2:Z:u:0` through
  `preview:assertion:nonorientable_surface:2:Z:u:2`.
- R02: `preview:assertion:real_projective_space:4:Z:u:0` through
  `preview:assertion:real_projective_space:4:Z:u:4`, and
  `preview:assertion:real_projective_space:4:F2:u:0` through
  `preview:assertion:real_projective_space:4:F2:u:4`.
- R03: `preview:assertion:lens:5:2:F5:r:0` through
  `preview:assertion:lens:5:2:F5:r:3`.
- R04: `preview:assertion:torus:4:Z:u:0` through
  `preview:assertion:torus:4:Z:u:4`.
- R05: `preview:assertion:orientable_surface_circle:3:Z:u:0` through
  `preview:assertion:orientable_surface_circle:3:Z:u:3`.
- R06: `preview:assertion:sphere_product:2:4:Z:u:0` through
  `preview:assertion:sphere_product:2:4:Z:u:6`.
- R07: `preview:assertion:disk:4:Z:u:0` through
  `preview:assertion:disk:4:Z:u:4`.
- R08: `preview:assertion:lens:10:1:Z:u:1`,
  `preview:assertion:lens:5:1:Z:u:1`, and
  `preview:assertion:lens:5:2:Z:u:1`.
- R09: `preview:assertion:lens:5:1:Z:u:0` through
  `preview:assertion:lens:5:1:Z:u:3` and
  `preview:assertion:lens:5:2:Z:u:0` through
  `preview:assertion:lens:5:2:Z:u:3`.
- R10: `preview:assertion:sphere:3:Z:r:0` through
  `preview:assertion:sphere:3:Z:r:3`.
- R11: no rational assertion returned; the supported integral lookup was used
  only to obtain subject evidence and was not substituted for the request.
- R12: no assertion returned because the subject did not resolve.

Here “through” is compact notation over the final degree suffix while every
preceding identifier component remains fixed. The exact evidence IDs expanded
were:

```text
preview:evidence:nonorientable_surface:2
preview:evidence:real_projective_space:4
preview:evidence:lens:5:2
preview:evidence:torus:4
preview:evidence:orientable_surface_circle:3
preview:evidence:sphere_product:2:4
preview:evidence:disk:4
preview:evidence:lens:10:1
preview:evidence:lens:5:1
preview:evidence:sphere:3
preview:evidence:sphere:2
```

All expansions named algorithm
`owned-smith-minors-and-modular-rank/0-preview`, an exact chain SHA-256, an
`exact` or explicit `not_computed` representative state, and
`identity_only;nonidentity_not_computed` for induced maps.

Typed limitations retained:

- R11 returned `unsupported_coefficient` for `Q`; this was not reported as
  absence or zero.
- R12 returned `not_found` and `subject_not_resolved` for `CP^2`; no group,
  assertion ID, or evidence ID was invented.
- The `D^4` subject returned `homotopy_equivalent_chain_model`, which the
  answer retained rather than presenting as a counted homeomorphic disk
  presentation.
- Equal integral Homology for `L(5,1)` and `L(5,2)` was not promoted to an
  identity, homeomorphism, or homotopy equivalence.

Claim-level human verdicts remain pending. Passing the deterministic and
agent-envelope checks is not mathematical or UX approval.

## Review `review-2026-07-12-002`: corpus-representativeness concern

```text
review_id: review-2026-07-12-002
record_kind: human-concern
recorded_at: 2026-07-12 (Africa/Johannesburg; exact time not retained)
reviewer: project owner
reviewer_role: human
repository_commit: aa18ebe
snapshot_id: preview-5ea7db464f937061
claim_under_review: the 60-subject preview is representative enough for an external first impression
verdict: needs-evidence
trigger: CP^2 returned a typed missing-subject outcome
follow_up_tickets: ticket 08; external reviewer handoff
supersedes_or_corrects: none
```

The concern did not reject the typed outcome: unresolved `CP^2` was the honest
answer for that Snapshot. It questioned the selection's external usefulness
and prompted a primary-source survey of recognizable examples. The requested
direction is to give Gabriel Ong and Dan Isaksen a reviewable artifact before
hosting, then use their recorded feedback to prioritize polish.

## Review `review-2026-07-12-003`: common-example source audit

```text
review_id: review-2026-07-12-003
record_kind: source-audit
recorded_at: 2026-07-12 (Africa/Johannesburg; exact time not retained)
reviewer: Codex primary-source research pass
reviewer_role: agent
agent_runtime: Codex background research agent; exact model/runtime identifier not retained
repository_commit: aa18ebe
snapshot_id: not-applicable (source/corpus audit, not a database run)
source_pins: repository corpus contract and source-lock audit; Hatcher; May; Sage topology catalog; Isaksen--Wang--Xu
human_review_state: pending-human-review
follow_up_tickets: ticket 08; ticket 12
supersedes_or_corrects: none
```

The audit established a repository fact: `CP^2` is already selected in the
planned 174-space corpus and has a pinned SageMath 10.9 route to a literal
9-vertex, 36-facet triangulation. It is missing only from the deliberately
hand-built `local-preview-60`; it has not yet passed through neutral export,
qualification, owned general-chain computation, and Snapshot assertion
creation. Familiar mathematical knowledge is not a substitute for that path.

The concrete source coordinates used by the audit were:

- SageMath release `10.9`, commit
  `686dc1a8d420c2e0aabadd4f602d9a0aa4690c50`, callable
  `simplicial_complexes.ComplexProjectivePlane()` in
  `src/sage/topology/simplicial_complex_examples.py`;
- [Sage's topology-example documentation](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_complex_examples.html);
- [Hatcher, *Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html);
- [May, *A Concise Course in Algebraic Topology*](https://www.math.uchicago.edu/~may/CONCISE/ConciseRevised.pdf); and
- [Isaksen--Wang--Xu, *Stable homotopy groups of spheres*](https://arxiv.org/abs/2001.04247).

No neutral `CP^2` artifact hash exists yet because materialization is the
uncompleted work being gated. The repository source-lock audit pins the recipe
without pretending that its output has already been ingested or qualified.

The resulting priority order is recorded in
[Common-example priorities](research/common-examples-review.md): `CP^2` and a
small Moore-space slice, the Poincare homology sphere, then K3 and `HP^2`,
followed by finite constructions. `BG`, `K(A,n)`, Thom spaces, and spectra
remain later bounded or newly modeled objects rather than mislabeled finite
Models. This is a qualitative reference-utility survey, not a citation-count
measurement.

## Decision `decision-2026-07-12-001`: external review before hosting

```text
record_kind: decision
recorded_at: 2026-07-12 (Africa/Johannesburg; exact time not retained)
decision_owner: project owner
decision: send the local preview to Gabriel Ong and Dan Isaksen before public hosting
inputs: review-2026-07-12-001 through review-2026-07-12-003
hosting_gate: at least one recorded external review and no open critical mathematical-safety or provenance defect
first_polish_blocker: qualify CP^2 through the pinned Model and owned general-chain path
cohort_policy: preserve local-preview-60; create a separately named external-review cohort
```

The reviewer procedure and feedback form are in
[External review](EXTERNAL_REVIEW.md). A later entry must record each external
review independently, including the commit, Snapshot, exact prompt and
commands, agent/runtime when visible, claim-level verdicts, and follow-up
tickets. No favorable verdict is assumed here.

## Review `review-2026-07-12-004`: adversarial-prompt verification

```text
review_id: review-2026-07-12-004
record_kind: database-run
recorded_at: 2026-07-12T12:48:58+02:00
reviewer: Codex implementation verification pass
reviewer_role: agent
agent_runtime: Codex task; exact model/runtime identifier not retained
repository_commit: aa18ebe (base commit before the documentation change)
reviewed_content_hashes: docs/EXTERNAL_REVIEW.md sha256 6fac8c38f916103cf11fd4c88ee178588f90ff562ed670ed3c9caeb500fdeca7; qa/review/questions-v1.json sha256 3dfea7332cb0aac7c11cec172cbc9b481b75b847dfefda2a97b4fa5862827562
working_tree_state: same intended documentation changes before and after
snapshot_id: preview-5ea7db464f937061
cohort_or_manifest: local-preview-60
prompt_or_protocol: docs/EXTERNAL_REVIEW.md adversarial prompt
exact_commands: preflight in TESTLOG.md; ordered JSON payloads below
public_operations: resolve_subject, read_homology, query_examples, expand_evidence
source_pins: not-applicable; the answer agent was prohibited from web retrieval
assertion_ids: preview:assertion:sphere:2:Z:u:0 through preview:assertion:sphere:2:Z:u:2; preview:assertion:lens:5:1:Z:u:0 through preview:assertion:lens:5:1:Z:u:3; preview:assertion:lens:5:2:Z:u:0 through preview:assertion:lens:5:2:Z:u:3; preview:assertion:lens:5:2:F5:r:0 through preview:assertion:lens:5:2:F5:r:3; preview:assertion:lens:10:1:Z:u:0 through preview:assertion:lens:10:1:Z:u:3
evidence_ids: preview:evidence:sphere:2; preview:evidence:lens:5:1; preview:evidence:lens:5:2; preview:evidence:lens:10:1
typed_limitations: CP^2 not_found and subject_not_resolved; Q unsupported_coefficient
capability_states: explicit exact/not_computed representatives; identity-only maps; nonidentity maps not_computed
claim_or_edge_verdicts: adversarial cases 1-6 pending-human-review
human_review_state: pending-human-review
follow_up_tickets: ticket 08; external reviewer feedback
supersedes_or_corrects: none
notes: verification of prompt behavior, not external approval
```

The prompt was manually replayed against exactly one database built by:

```bash
python3 -m homology_db --db /tmp/homology-db-adversarial-review.sqlite3 demo
```

Every subsequent operation used that path and the documented JSON `tool`
envelope. This is the exact ordered payload trace:

```jsonl
01 {"tool":"resolve_subject","arguments":{"query":"CP^2"}}
02 {"tool":"read_homology","arguments":{"subject":"CP^2","coefficient":"Z"}}
03 {"tool":"resolve_subject","arguments":{"query":"S^2"}}
04 {"tool":"read_homology","arguments":{"subject":"S^2","coefficient":"Q"}}
05 {"tool":"read_homology","arguments":{"subject":"sphere:2","coefficient":"Z"}}
06 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:sphere:2"]}}
07 {"tool":"resolve_subject","arguments":{"query":"L(5,1)"}}
08 {"tool":"resolve_subject","arguments":{"query":"L(5,2)"}}
09 {"tool":"read_homology","arguments":{"subject":"lens:5:1","coefficient":"Z"}}
10 {"tool":"read_homology","arguments":{"subject":"lens:5:2","coefficient":"Z"}}
11 {"tool":"read_homology","arguments":{"subject":"lens:5:2","coefficient":"F5","reduced":true}}
12 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:lens:5:1","preview:evidence:lens:5:2"]}}
13 {"tool":"query_examples","arguments":{"pattern":{"degree":1,"torsion_prime":5,"limit":20}}}
14 {"tool":"read_homology","arguments":{"subject":"lens:10:1","coefficient":"Z"}}
15 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:lens:10:1","preview:evidence:lens:5:1","preview:evidence:lens:5:2"]}}
```

The replay observed:

1. `CP^2`: `not_found` followed by `subject_not_resolved`, with no invented
   assertion or evidence;
2. rational `S^2`: `unsupported_coefficient`, followed only by a supported
   integral lookup to expand `preview:evidence:sphere:2`;
3. `L(5,1)` versus `L(5,2)`: separately resolved integral groups and expanded
   evidence, with equality not promoted to an equivalence;
4. reduced `F5` Homology of `L(5,2)`: four exact returned groups with the
   reduced convention retained;
5. the 5-primary degree-one query: exactly three proven matches, no unresolved
   candidates, and expanded evidence for all three subjects; and
6. representative and induced-map capability states: every
   `not_computed` value remained explicit.

All responses used Snapshot `preview-5ea7db464f937061`. The unit preflight
again passed 12/12 tests. This verifies that the copy-paste prompt exercises
the intended seams; it is not a substitute for Gabriel's or Dan's verdict.

## Review `review-2026-07-12-005`: starting-prompt verification

```text
review_id: review-2026-07-12-005
record_kind: database-run
recorded_at: 2026-07-12T12:53:23+02:00
reviewer: Codex implementation verification pass
reviewer_role: agent
agent_runtime: Codex task; exact model/runtime identifier not retained
repository_commit: aa18ebe (base commit before the documentation change)
reviewed_content_hashes: docs/EXTERNAL_REVIEW.md sha256 6fac8c38f916103cf11fd4c88ee178588f90ff562ed670ed3c9caeb500fdeca7; qa/review/questions-v1.json sha256 3dfea7332cb0aac7c11cec172cbc9b481b75b847dfefda2a97b4fa5862827562
working_tree_state: same intended documentation changes before and after
snapshot_id: preview-5ea7db464f937061
cohort_or_manifest: local-preview-60; qa/review/questions-v1.json schema version 1
prompt_or_protocol: docs/EXTERNAL_REVIEW.md starting prompt plus its free-form continuation
exact_commands: preflight and ordered JSON payloads below
public_operations: resolve_subject, read_homology, query_examples, expand_evidence
source_pins: not-applicable; the answer agent was prohibited from web retrieval
assertion_ids: review-2026-07-12-001 grounding inventory, plus preview:assertion:nonorientable_surface:3:Z:u:0 through preview:assertion:nonorientable_surface:3:Z:u:2 and preview:assertion:real_projective_space:4:F3:r:0 through preview:assertion:real_projective_space:4:F3:r:4
evidence_ids: review-2026-07-12-001 grounding inventory, plus preview:evidence:nonorientable_surface:3
typed_limitations: Q unsupported_coefficient; CP^2 and CP^3 not_found and subject_not_resolved
capability_states: exact or explicit not_computed representatives; identity-only maps; nonidentity maps not_computed
claim_or_edge_verdicts: R01-R12 and free-form questions 1-3 pending-human-review
human_review_state: pending-human-review
follow_up_tickets: ticket 08; external reviewer feedback
supersedes_or_corrects: none
notes: verifies both fixed and free-form phases; not external approval
```

The exact preflight was:

```bash
git status --short
python3 -m unittest discover -s tests -v
python3 -m homology_db --db /tmp/homology-db-external-review.sqlite3 demo
```

The database was built exactly once. Every later command used this envelope
and the same database path:

```bash
python3 -m homology_db --db /tmp/homology-db-external-review.sqlite3 tool '<JSON>'
```

The exact ordered payloads for R01--R12 were:

```jsonl
01 {"tool":"resolve_subject","arguments":{"query":"Klein bottle"}}
02 {"tool":"read_homology","arguments":{"subject":"Klein bottle","coefficient":"Z"}}
03 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:nonorientable_surface:2"]}}
04 {"tool":"resolve_subject","arguments":{"query":"RP^4"}}
05 {"tool":"read_homology","arguments":{"subject":"RP^4","coefficient":"Z"}}
06 {"tool":"read_homology","arguments":{"subject":"RP^4","coefficient":"F2"}}
07 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:real_projective_space:4"]}}
08 {"tool":"resolve_subject","arguments":{"query":"L(5,2)"}}
09 {"tool":"read_homology","arguments":{"subject":"L(5,2)","coefficient":"F5","reduced":true}}
10 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:lens:5:2"]}}
11 {"tool":"resolve_subject","arguments":{"query":"T^4"}}
12 {"tool":"read_homology","arguments":{"subject":"T^4","coefficient":"Z"}}
13 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:torus:4"]}}
14 {"tool":"resolve_subject","arguments":{"query":"Sigma_3 x S^1"}}
15 {"tool":"read_homology","arguments":{"subject":"Sigma_3 x S^1","coefficient":"Z"}}
16 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:orientable_surface_circle:3"]}}
17 {"tool":"resolve_subject","arguments":{"query":"S^2 x S^4"}}
18 {"tool":"read_homology","arguments":{"subject":"S^2 x S^4","coefficient":"Z"}}
19 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:sphere_product:2:4"]}}
20 {"tool":"resolve_subject","arguments":{"query":"D^4"}}
21 {"tool":"read_homology","arguments":{"subject":"D^4","coefficient":"Z"}}
22 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:disk:4"]}}
23 {"tool":"query_examples","arguments":{"pattern":{"degree":1,"torsion_prime":5,"limit":20}}}
24 {"tool":"read_homology","arguments":{"subject":"lens:10:1","coefficient":"Z"}}
25 {"tool":"read_homology","arguments":{"subject":"lens:5:1","coefficient":"Z"}}
26 {"tool":"read_homology","arguments":{"subject":"lens:5:2","coefficient":"Z"}}
27 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:lens:10:1","preview:evidence:lens:5:1","preview:evidence:lens:5:2"]}}
28 {"tool":"resolve_subject","arguments":{"query":"L(5,1)"}}
29 {"tool":"resolve_subject","arguments":{"query":"L(5,2)"}}
30 {"tool":"resolve_subject","arguments":{"query":"S^3"}}
31 {"tool":"read_homology","arguments":{"subject":"S^3","coefficient":"Z","reduced":true}}
32 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:sphere:3"]}}
33 {"tool":"resolve_subject","arguments":{"query":"S^2"}}
34 {"tool":"read_homology","arguments":{"subject":"S^2","coefficient":"Q"}}
35 {"tool":"read_homology","arguments":{"subject":"sphere:2","coefficient":"Z"}}
36 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:sphere:2"]}}
37 {"tool":"resolve_subject","arguments":{"query":"CP^2"}}
38 {"tool":"read_homology","arguments":{"subject":"CP^2","coefficient":"Z"}}
```

The free-form continuation reused the same database and Snapshot. Its three
questions were integral Homology of `N_3`, reduced `F3` Homology of `RP^4`,
and integral Homology of missing subject `CP^3`. Exact payloads:

```jsonl
39 {"tool":"resolve_subject","arguments":{"query":"N_3"}}
40 {"tool":"read_homology","arguments":{"subject":"N_3","coefficient":"Z"}}
41 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:nonorientable_surface:3"]}}
42 {"tool":"resolve_subject","arguments":{"query":"RP^4"}}
43 {"tool":"read_homology","arguments":{"subject":"RP^4","coefficient":"F3","reduced":true}}
44 {"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:real_projective_space:4"]}}
45 {"tool":"resolve_subject","arguments":{"query":"CP^3"}}
46 {"tool":"read_homology","arguments":{"subject":"CP^3","coefficient":"Z"}}
```

All 46 responses used Snapshot `preview-5ea7db464f937061`. The two supported
free-form lookups returned exact grounded groups and complete evidence
expansions. `CP^3` returned `not_found` and `subject_not_resolved`, with no
invented assertion or evidence. The final status matched the initial intended
documentation changes.

## Product direction to revisit: a cited implication graph

The intended long-term interface is a graph whose nodes are cited assertions
and whose directed edges are cited implications, constructions, or
invariant-preservation steps. It is optimized for efficient human review:
reviewers should be able to inspect a claim, its incoming justifications, the
status of their hypotheses, competing claims, uncertainty, and correction
history without reading an agent transcript end to end.

This differs deliberately from a proof-assistant workflow whose successful
kernel check is intended to remove the need for human confirmation. The graph
does not replace mathematical judgment. It makes the agent's claimed route
auditable and corrigible. An accepted edge means a named reviewer accepted
that cited implication in its stated scope; rejection or later correction
remains visible.

No graph schema, inference language, trust policy, or UI is fixed by this
entry. Those decisions require a separate design discussion. Until then:

- never materialize an implication without named sources and hypotheses;
- never silently turn an implication into identity or merge its nodes;
- distinguish source testimony, owned computation, deterministic presentation
  rules, and agent-proposed reasoning;
- preserve `unknown`, `not_computed`, conflict, and missing hypotheses; and
- append review and correction events rather than overwriting accepted or
  rejected history.

## Automation checklist for the next review

- Allocate a stable `review_id` before running commands.
- Record commit, clean-tree state, prompt hash/version, agent/runtime, and the
  one Snapshot ID.
- Capture ordered public-operation requests and responses without SQL,
  filesystem lookup, or web retrieval by the answer agent.
- Extract every mathematical claim and require its exact assertion/evidence
  grounding or a typed unsupported outcome.
- Expand evidence once per discussed subject and retain capability states.
- Present claim and implication-edge blocks for human verdicts.
- Append the completed verdicts and new follow-up tickets to this file or its
  future structured successor; do not mutate prior entries.
- Gate hosting on recorded external review and resolution of every critical
  safety or provenance defect.

## Decision `decision-2026-07-12-002`: postpone external review

```text
record_kind: decision
recorded_at: 2026-07-12 (Africa/Johannesburg; exact time not retained)
decision_owner: project owner
repository_commit: 9676d6f (named-atlas execution map)
decision: do not invite Gabriel Ong, Dan Isaksen, or another external mathematical reviewer until named-atlas-review-v1 passes
inputs: review-2026-07-12-001 through review-2026-07-12-005; CP^2 corpus-representativeness concern; production-schema concern
review_gate: grounded RP^0..12 and CP^0..12, named corpus, production-like schema, qualified cross-model slice, definition seam, and adversarial QA with no critical mathematical-safety, schema, or provenance defect
cohort_policy: preserve local-preview-60 unchanged as a regression fixture; it is not the proposed reviewer experience
supersedes_or_corrects: decision-2026-07-12-001 timing and cohort recommendation only
```

This entry preserves the earlier decision rather than rewriting it. Informal
product feedback may still be recorded while the gate is closed; it is not a
database review or an invitation to endorse the current Snapshot.

## Feedback `review-2026-07-12-006`: Gabriel Ong on LMFDB and knowls

```text
review_id: review-2026-07-12-006
record_kind: product-feedback
recorded_at: 2026-07-12T13:32:02+02:00, 2026-07-12T13:42:59+02:00, and 2026-07-12T14:00:30+02:00
reviewer: Gabriel Ong
reviewer_role: human product adviser; not a database reviewer in this entry
repository_commit: 9676d6f
snapshot_id: not-applicable
source: private messages quoted by the project owner; ICERM video https://icerm.brown.edu/video_archive/4709
feedback: study the LMFDB talk's lessons about setting up a mathematical database, naming, useful graphical representations, and ease of use; prioritize LMFDB knowls as expandable definitions; graphics may come later
verdict: not-applicable (product feedback, not a claim-level mathematical review)
disposition: accepted as named-atlas schema/API/QA input; inline browser rendering and mathematical graphics remain later UI work
follow_up: docs/research/icerm-lmfdb-knowl-review.md; production-schema, public-operation, QA, and final-audit tickets in named-atlas-review-v1
supersedes_or_corrects: none
```

The term is **knowl** (plural **knowls**). The recording's caption track
misrecognizes it as “nulls”; the presenter-authored slides and official LMFDB
documentation confirm the spelling.

## Review `review-2026-07-12-007`: ICERM/LMFDB source audit

```text
review_id: review-2026-07-12-007
record_kind: source-audit
recorded_at: 2026-07-12T14:24:16+02:00
reviewer: Codex primary-source research pass
reviewer_role: agent
agent_runtime: Codex background research agent plus primary-agent transcript/PDF verification; exact model identifier not retained
repository_commit: 9676d6f (base before this documentation change)
snapshot_id: not-applicable
reviewed_content_hashes: ICERM slide PDF sha256 81a84879ec99e2b7749abda21b4f25fc90bf0abc3f3f7065b095b5f54304133d; research report sha256 2dcab6bda3d23e342df28fb49d3132de504144d8a159638c981196da2afae249
source_pins: ICERM schedule/recording/slides for David Roe, Building mathematical databases, 2026-06-24; official LMFDB repository cbcdaee01f1a698eb44a011b8f4290e294a5a7a1
audit_conclusion: knowls are stable reusable inline exposition with revision/review history; meaningful persistent labels, scoped completeness, source/reliability disclosure, stored searchable computations, and mathematically encoded graphics are relevant design precedents
project_disposition: require versioned Snapshot-selected definition records and knowledge references in the existing four operation envelopes; never treat definition prose as assertion evidence; defer inline dropdowns and graphics to the later UI tier
human_review_state: pending-human-review
follow_up: named-atlas-review-v1 tickets 03, 08, 09, and 10
supersedes_or_corrects: none
```

The complete source-role analysis, recording timestamps, implementation
inspection, and project-specific recommendations are in
[ICERM/LMFDB lessons for Homology DB](research/icerm-lmfdb-knowl-review.md).

## Communication plan `review-2026-07-12-008`: reviewer Loom walkthrough

```text
review_id: review-2026-07-12-008
record_kind: external-review-communication-plan
recorded_at: 2026-07-12 (Africa/Johannesburg; exact time retained in Git history)
reviewer: project owner and Codex planning pass
reviewer_role: communication planning; not mathematical review
repository_commit: 33e91c2 (atlas checkpoint before this communication-plan commit)
snapshot_id: not-applicable
artifact: docs/LOOM_WALKTHROUGH.md
audience: Gabriel Ong and Dan Isaksen
plan: rehearse internally against local-preview-60; record and send the external cut only after named-atlas-review-v1 passes
video_thesis: AI navigates four read-only operations over an immutable human-reviewable graph of cited claims and implications
required_demonstrations: grounded CP^2; CP^12/CP^13 materialization boundary; equal-Homology comparison safety; Snapshot-bounded torsion search; typed unsupported/not_computed outcome; reviewed definition distinct from assertion evidence
email_assets: Loom URL, public repository URL, pinned commit, copy-paste read-only reviewer prompt, role-specific requests, and explicit request for reject/needs-evidence verdicts
send_gate: append-only decision superseding decision-2026-07-12-002 after all named-atlas critical gates pass
current_disposition: planned, not recorded, not sent
supersedes_or_corrects: none
```

The detailed [reviewer Loom walkthrough plan](LOOM_WALKTHROUGH.md) includes a
timed storyboard, internal-rehearsal substitutions, final recording checklist,
email draft, reviewer prompt, and the metadata block to append after recording.
Preparing the communication does not reopen the external-review gate.

## Correction `review-2026-07-12-009`: simplify the Loom to four minutes

```text
review_id: review-2026-07-12-009
record_kind: external-review-communication-plan-correction
recorded_at: 2026-07-12 (Africa/Johannesburg; exact time retained in Git history)
decision_owner: project owner
artifact: docs/LOOM_WALKTHROUGH.md
decision: replace the 7--9 minute multi-demonstration storyboard with a four-minute development preview
timing: 0:00--2:00 current capabilities and explicit absences; 2:00--3:00 one named-space/coefficient lookup; 3:00--4:00 one Snapshot-bounded Homology-pattern example search
deferred_extension: example retrieval by Homotopy data, and later combined Homology/Homotopy/spectral-sequence patterns
sharing_semantics: before named-atlas-review-v1 passes, the Loom may orient informal product testing but is not the external mathematical review or corpus-approval request
supersedes_or_corrects: review-2026-07-12-008 storyboard, email, and recording scope only; decision-2026-07-12-002 review gate remains in force
```

The revised plan intentionally omits schema, migration, knowl, implication-
graph, family-boundary, and adversarial-review tours. Those topics made the
orientation obscure the two interactions being tested.

## Communication artifact `review-2026-07-12-010`: no-terminal Codex workspace

```text
review_id: review-2026-07-12-010
record_kind: external-review-communication-artifact
recorded_at: 2026-07-12 (Africa/Johannesburg; exact time retained in Git history)
decision_owner: project owner
artifact: LOOM_START_HERE.md
purpose: let the presenter prepare and run the four-minute Loom entirely through Codex without personally invoking Python or terminal commands
preflight: one read-only Codex prompt runs 41 tests, builds /tmp/homology-db-loom.sqlite3 once, verifies the 60-subject Snapshot, and returns a compact READY FOR LOOM card
spoken_script: 264-word introduction describing current and absent capabilities
on_camera_prompts: coefficient-qualified RP^4/F2 lookup; Snapshot-bounded 5-primary H_1 example search
fallback: one compression prompt preserves grounding and coverage while shortening an unexpectedly long Codex answer
supersedes_or_corrects: implements review-2026-07-12-009; does not change the mathematical-review gate
```
