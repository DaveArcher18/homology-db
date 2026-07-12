# Four-minute Homology DB Loom

Status: ready to rehearse as an honest development preview

Audience: Gabriel Ong and Dan Isaksen

Target length: 4 minutes

## What the video should accomplish

Keep this deliberately small. The video should establish only three things:

1. what exists today and what does not;
2. how to ask for the Homology of one named space with chosen coefficients;
3. how to ask for examples of spaces matching a Homology pattern.

Do not tour the schema, migration history, source research, knowls, planned UI,
or the full review process. Those can be discovered later if the basic idea is
useful.

The current repository is still a development preview, not the named-atlas
review candidate. If this Loom is shared before `named-atlas-review-v1` passes,
say that explicitly and ask for informal product testing rather than a verdict
on corpus completeness.

## Before recording

- Open the repository README and one terminal in a clean checkout.
- Increase the terminal font so the commands and short answers are readable.
- Before recording, build one disposable database with the command below, note
  its `snapshot_id`, and clear the terminal. Do not show the mathematical tour
  on camera because it would preview and duplicate both use cases. Reuse the
  same database throughout.

```bash
python3 -m homology_db --db /tmp/homology-db-loom.sqlite3 demo
```
- Keep notifications, tokens, unrelated tabs, and personal paths off screen.
- Do not show raw SQL or implementation files. The point is the user workflow.

## Four-minute run of show

### 0:00--2:00 — What exists and what does not

Suggested script:

> This is a very early prototype of a database for algebraic topology. The
> long-term idea is that an AI should be able to retrieve mathematical facts
> and useful examples without the AI itself being the source of truth.
>
> What exists today is a local, deterministic SQLite preview containing 60
> named manifold examples. It supports ordinary Homology over the integers and
> the fields F2, F3, F5, and F7. An agent can resolve a name, read Homology,
> search for examples matching a structured Homology pattern, and expand the
> evidence behind an answer. Returned groups carry assertion and evidence IDs,
> and unsupported requests remain explicit instead of being filled in from the
> model's memory.
>
> What does not exist yet is equally important. This is not the full named
> atlas: CP^n and many other standard spaces are still being added with proper
> provenance. There is no hosted interface, no graphical implication view, no
> general rational coefficients, no cohomology rings, and no stable stems or
> spectral-sequence database. Representatives and nonidentity induced maps are
> also generally not computed.
>
> For now there are two useful interactions. First: tell me the Homology of a
> named space with specified coefficients. Second: give me examples of spaces
> whose Homology has a specified pattern.

While speaking, show only the README. Do not run a mathematical command during
these two minutes. Say that the prebuilt database has 60 subjects and one
Snapshot, and point to the four operation names and the statement that this is
a local preview rather than a qualified release.

### 2:00--3:00 — Use case 1: one space and chosen coefficients

Say:

> The first use case is a direct lookup: tell me the Homology of this space
> with these coefficients. For example, ask for RP^4 with F2 coefficients.

If using an AI coding agent, type:

```text
Using only the Homology DB public operations, tell me H_*(RP^4; F2). Show the
snapshot, assertion IDs, and evidence ID. Do not add facts that are not returned
by the database.
```

The underlying database call is:

```bash
python3 -m homology_db --db /tmp/homology-db-loom.sqlite3 tool \
'{"tool":"read_homology","arguments":{"subject":"RP^4","coefficient":"F2"}}'
```

Point out only that the answer has one `F2` generator in degrees 0 through 4
and that every displayed group is tied to stored IDs. Do not spend the minute
reading JSON field by field.

### 3:00--4:00 — Use case 2: find examples matching a pattern

Say:

> The second use case goes in the other direction: give me examples of spaces
> with Homology like this. Here I will ask for spaces in the current Snapshot
> with 5-primary torsion in degree one.

If using an AI coding agent, type:

```text
Using only the Homology DB public operations, find examples in this Snapshot
with 5-primary torsion in H_1. State that the search is Snapshot-bounded, keep
the assertion and evidence IDs, and do not present the result as a
classification of all spaces.
```

The underlying database call is:

```bash
python3 -m homology_db --db /tmp/homology-db-loom.sqlite3 tool \
'{"tool":"query_examples","arguments":{"pattern":{"degree":1,"torsion_prime":5,"limit":20}}}'
```

Point out the three current matches: `L(5,1)`, `L(5,2)`, and `L(10,1)`. Also
point out the coverage statement: these are the proven matches in this
Snapshot, not every mathematical example.

Finish with:

> The obvious future extension is to ask for examples matching Homotopy data
> too, and later combinations of Homology, Homotopy, and spectral-sequence
> information. That does not exist yet; this prototype is testing whether the
> basic lookup and example-retrieval workflow is useful and trustworthy.

## Minimal rehearsal checklist

- [ ] The recording is between 3:30 and 4:30.
- [ ] The first two minutes clearly separate present and absent capabilities.
- [ ] Only the two requested use cases are demonstrated.
- [ ] One database path and one Snapshot are used throughout.
- [ ] The lookup names coefficients explicitly.
- [ ] The example search is described as Snapshot-bounded.
- [ ] Homotopy search is described as future work, not a hidden capability.
- [ ] `CP^n`, hosting, UI, representatives, maps, and spectral sequences are
      not implied to exist today.
- [ ] Commands and output are legible without pausing the video.
- [ ] No secrets, unrelated tabs, or personal paths appear.

## Short email wrapper

```text
Hi Gabriel and Dan,

Here is a four-minute overview of the current Homology DB prototype:
<LOOM_URL>

The repository is:
https://github.com/DaveArcher18/homology-db

The video shows the two things that currently work: asking for the Homology of
a named space with chosen coefficients, and asking for examples matching a
Homology pattern. Homotopy-pattern search is a later extension.

This is still a development preview rather than the complete named atlas. If
you try it, I would especially like to know whether the answers and their
evidence are easy to inspect, and which basic examples you immediately miss.

Thanks,
David
```

## Recording log

After recording, append the completed values to `docs/REVIEW_PROCESS.md`:

```text
record_kind: development-preview-walkthrough
recorded_at:
recorded_by:
loom_url:
repository_commit:
snapshot_id:
recipients:
sent_at:
limitations_disclosed:
follow_up_review_ids:
```
