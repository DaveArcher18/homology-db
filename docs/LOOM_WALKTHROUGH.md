# Reviewer Loom walkthrough plan

Status: planned; external recording and email remain gated by
`named-atlas-review-v1`

Audience: Gabriel Ong and Dan Isaksen

Target length: 7--9 minutes

## Purpose

The Loom should make one idea immediately legible: an AI may help formulate a
query and explain a result, but the mathematical answer comes from one
immutable database Snapshot whose claims, evidence, dependencies, conventions,
reviews, and explicit gaps can be inspected by a human.

The video is not a product launch or a request for endorsement. It is a short
orientation before Gabriel or Dan clones the repository and tries to break the
review candidate themselves.

## Recording and sending gate

Prepare two cuts:

1. **Internal rehearsal.** Record or rehearse against `local-preview-60` to
   test the pacing, terminal legibility, and explanation. Do not send this cut
   as the atlas review. `CP^2` must remain a visibly unresolved safety example.
2. **External reviewer cut.** Record from a clean checkout only after
   `named-atlas-review-v1` passes its schema, named-corpus, source-pin,
   deterministic-rebuild, and adversarial-agent gates with no critical defect.
   This cut must use the final named-atlas Snapshot and show grounded `CP^2`.

Before sending the external cut, update every placeholder in this document,
reactivate the external-review guide through an append-only decision, and
record the exact repository commit, Snapshot, prompt version, and Loom URL in
`docs/REVIEW_PROCESS.md`.

## The story in one sentence

> Homology DB is a human-reviewable graph of cited mathematical claims and
> cited implications, exposed through four read-only operations so an AI can
> help navigate the graph without silently becoming the source of truth.

## Screen and terminal preparation

- Use a clean clone of `https://github.com/DaveArcher18/homology-db` in a new
  directory; do not record the development worktree.
- Turn off notifications and hide bookmarks, tokens, shell history, unrelated
  tabs, and personal paths.
- Use a large terminal font and a narrow enough window that JSON remains
  readable in the recording.
- Keep the repository page, terminal, and one plain-text prompt ready. Avoid a
  fast tour through many editor tabs.
- Pin the exact commit in the opening minute and show `git status --short`
  before and after the test.
- Build one disposable database once. Reuse its one `snapshot_id` throughout.
- Never cut from one Snapshot to another while presenting the run as a single
  review.
- Do not simulate a knowl dropdown or implication-graph UI. Show the underlying
  reviewed definition/dependency records; the browser presentation is later
  work.

## Run of show

### 0:00--0:50 — Why this exists

Camera on briefly, repository page visible.

Say:

> Stable homotopy calculations constantly depend on small facts, conventions,
> examples, and implications that are easy for an AI to state fluently and
> hard for a human to audit quickly. This project is an experiment in making
> those answers inspectable: every displayed group is a stored assertion in one
> Snapshot, with evidence and dependencies you can expand.

State the boundary: ordinary Homology first; spectral sequences and stable
stems are later. State that the requested output is criticism, not approval.

### 0:50--1:35 — Show the trust boundary

Show the four operation names in `README.md` or `docs/TEST_DRIVE.md`:

- `resolve_subject`;
- `read_homology`;
- `query_examples`; and
- `expand_evidence`.

Explain that the AI translates prose into these calls. It may not query SQL,
invent a missing specialization, treat a definition as mathematical evidence,
or complete an unsupported answer from memory.

Use this verbal picture:

```text
topologist's question
        |
        v
AI chooses one of four read-only operations
        |
        v
immutable Snapshot -> selected assertion -> evidence/dependency expansion
        |
        v
human accepts, rejects, requests evidence, or records a correction
```

### 1:35--2:15 — Clean build and deterministic identity

Run:

```bash
git rev-parse HEAD
git status --short
python3 -m unittest discover -s tests -v
python3 -m homology_db --db /tmp/homology-db-loom.sqlite3 demo
```

Pause on the test count, corpus label, and `snapshot_id`. Explain that the
SQLite file is disposable but the selected logical Snapshot is citable and
deterministically rebuildable.

For the external cut, replace the demo command if the named-atlas candidate
uses a versioned build command. Do not retain the preview's `60 subjects`
headline in the final recording.

### 2:15--3:40 — One familiar named space, fully grounded

The external cut should use `CP^2` because its earlier absence exposed the
difference between familiar mathematics and admitted, sourced database data.

Show, through public operations only:

1. resolution to the permanent Conceptual-space identity and aliases;
2. integral Homology with degrees, convention, completeness, and immutable
   assertion IDs;
3. the cited family theorem and materialized specialization edge;
4. literature reference, revision, pinpoint, and source hash; and
5. the independent qualified Model computations and their agreement record.

Say explicitly that equal outputs from the finite simplicial-set Model and the
9-vertex triangulation corroborate Homology; they do not merge the Models or
prove an unstated equivalence.

Internal rehearsal substitution: resolve and read the Klein bottle, expand its
evidence, then resolve `CP^2` and show the typed missing-subject outcome. Say
that this is exactly why the rehearsal must not be sent as the named atlas.

### 3:40--4:35 — Bounded family coverage and honest absence

For the external cut, compare `CP^12` and `CP^13`:

- `CP^12` returns materialized, cited assertions;
- `CP^13` returns `outside_materialized_range`; and
- neither result depends on evaluating a family formula at query time.

Briefly distinguish `outside_materialized_range`, `model_not_qualified`,
`not_computed`, `unsupported_coefficient`, and `not_found`. None means a zero
group.

Internal rehearsal substitution: request `S^2` over `Q` and show
`unsupported_coefficient` without supplied groups.

### 4:35--5:35 — A mathematically dangerous comparison

For the external cut, compare the Poincaré homology sphere with `S^3`. Expand
both evidence chains. The answer may say their integral Homology agrees, but
must refuse to infer identity, homeomorphism, or homotopy equivalence without
a separate selected relation assertion.

This is the clearest demonstration of the product philosophy: the agent's
reasoning is useful only when its claimed implication edges are visible and
corrigible.

Internal rehearsal substitution: compare `L(5,1)` and `L(5,2)` only as graded
Homology and state the same restriction.

### 5:35--6:20 — Search and scoped completeness

Ask for materialized examples with 5-primary torsion in degree one. Show that:

- every match has its own assertion and evidence ID;
- truncation and total matches are explicit; and
- the response says it searches selected Snapshot assertions, not all spaces
  in mathematics.

This is where to mention future spectral-sequence use: a computation system
needs dependable example retrieval and explicit gaps, not plausible semantic
similarity.

### 6:20--7:10 — Knowls and review history

Show one reviewed, Snapshot-selected definition record and its role as
`exposition`. Then show the distinct evidence record for a mathematical claim.
Explain Gabriel's knowl suggestion: terms should expand in place later, but the
definition prose must never count as proof of the assertion it explains.

Show or describe append-only correction and conflict behavior: a correction
creates a new assertion/event; it does not overwrite the prior claim.

If the named-atlas public operations cannot yet expose this distinction, do
not record the external cut.

### 7:10--8:15 — Hand the test to them

Show the short clone/test prompt below. Ask Gabriel and Dan to try familiar,
annoying, and adversarial questions. Specifically invite them to flag:

- mathematically correct answers whose evidence is too weak or too hard to
  inspect;
- convention ambiguity;
- unearned identity or equivalence claims;
- misleading completeness language;
- missing named examples; and
- implication edges that would be genuinely useful to review.

End with:

> I would much rather get a `reject` or `needs-evidence` verdict than a polite
> endorsement. The experiment is whether this makes expert review faster and
> corrections durable.

Run `git status --short` again and show the clean result.

## Copy-paste reviewer prompt for the email

Replace `<REVIEW_COMMIT>`, `<SNAPSHOT_BUILD_COMMAND>`, `<STARTING_GUIDE>`, and
`<REVIEW_MANIFEST>` only after the named-atlas gate passes.

```text
Clone https://github.com/DaveArcher18/homology-db and check out
<REVIEW_COMMIT>. Read AGENTS.md, README.md, <STARTING_GUIDE>, and the review
manifest at <REVIEW_MANIFEST> completely before answering anything.

This is a read-only mathematical and provenance review. Do not edit files,
commit, push, query SQLite directly, or browse the web. Run the unit suite,
then build one disposable database exactly once with:

<SNAPSHOT_BUILD_COMMAND>

Use that database and exactly one snapshot_id throughout. Answer only through
resolve_subject, read_homology, query_examples, and expand_evidence. Expand the
evidence for every subject you discuss. Every Homology-group claim must retain
the exact assertion, evidence, source, and dependency IDs returned by the
database. Never fill an unsupported, outside-range, unresolved, not-found,
model-not-qualified, or not-computed result from memory.

Start with CP^2, the CP^12/CP^13 boundary, the Poincare homology sphere versus
S^3, one reduced or field-coefficient question, one torsion-pattern search,
and one request for a representative or induced map. Then ask three questions
of your own. For each substantive claim, give separate mathematical and
provenance verdicts: accept, reject, or needs-evidence. Finish by running
git status --short and reporting any change.
```

## Draft email

Subject: Homology DB prototype — short walkthrough and adversarial test

```text
Hi Gabriel and Dan,

I have a review candidate for the first small part of the topology database
idea: ordinary Homology of a bounded named atlas, with an AI acting only as a
client of a cited assertion/evidence database.

This short Loom shows the intended workflow:
<LOOM_URL>

Repository and pinned review commit:
https://github.com/DaveArcher18/homology-db
<REVIEW_COMMIT>

I am not looking for an endorsement. I would like you to try to make it give a
mathematically unsafe, weakly grounded, conventionally ambiguous, or annoying
answer. In particular, a correct answer with evidence that is difficult to
audit should be marked needs-evidence rather than accepted.

The README links the short setup guide. The copy-paste reviewer prompt is below.

<REVIEWER_PROMPT>

Gabriel: your LMFDB/knowl comments shaped the definition and provenance split;
I would especially value whether the result feels inspectable and usable.

Dan: I would especially value cold mathematical questions that expose bad
examples, hidden assumptions, or unjustified implications.

Thanks,
David
```

## Final recording checklist

- [ ] `named-atlas-review-v1` gate is recorded as passed.
- [ ] No critical mathematical-safety, schema, provenance, or migration defect
      remains open.
- [ ] The external-review hold is superseded by a new append-only decision.
- [ ] Recording uses a clean clone at one pinned public commit.
- [ ] One final Snapshot is built once and named throughout.
- [ ] `CP^2` is grounded by literature specialization and independent Models.
- [ ] The materialized family boundary is shown without query-time invention.
- [ ] Equal Homology is not promoted to equivalence.
- [ ] At least one typed unsupported/not-computed outcome is retained.
- [ ] A knowl-like definition is visibly separate from assertion evidence.
- [ ] Every displayed mathematical claim retains grounding IDs.
- [ ] Terminal text and JSON are legible at normal playback speed.
- [ ] No secrets, unrelated tabs, personal messages, or private paths appear.
- [ ] The opening and closing `git status --short` outputs are clean.
- [ ] Loom captions and transcript have been checked for mathematical notation
      and the spelling **knowl**.
- [ ] Loom URL, commit, Snapshot, prompt version, and recipients are appended to
      `docs/REVIEW_PROCESS.md` before the email is sent.

## Recording log template

Append the completed values to `docs/REVIEW_PROCESS.md`; do not rewrite this
plan with mutable run data.

```text
record_kind: external-review-walkthrough
recorded_at:
recorded_by:
loom_url:
repository_url: https://github.com/DaveArcher18/homology-db
repository_commit:
snapshot_id:
snapshot_build_command:
review_prompt_path_and_hash:
walkthrough_plan_path_and_hash:
caption_reviewed_by:
recipients:
sent_at:
review_gate_decision:
known_limitations_disclosed:
follow_up_review_ids:
```
