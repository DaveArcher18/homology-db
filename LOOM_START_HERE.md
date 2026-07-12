# Loom recording workspace

You do not need to run Python or use the terminal yourself. Open this repository
as a workspace in Codex and keep this file visible beside the Codex task.

The recording has three parts:

1. read the two-minute introduction below;
2. paste the direct-lookup prompt into Codex;
3. paste the example-search prompt into the same Codex task.

## Before recording: prepare Codex

Open a fresh Codex task in this repository and paste the following prompt. Let
Codex finish before starting Loom.

```text
Prepare this Homology DB workspace for a four-minute Loom recording. This is a
read-only preparation task: do not edit repository files, commit, push, or
browse the web. You may write only the disposable database under /tmp.

Read AGENTS.md and docs/LOOM_WALKTHROUGH.md. Confirm the Git working tree is
clean. Run the full unit suite. Then build the preview database exactly once at
/tmp/homology-db-loom.sqlite3 using the documented demo command. If that exact
disposable file exists from an earlier rehearsal, delete only that file first.
Verify that the new database contains 60 subjects and record its snapshot_id.
Do not rebuild it after this.

Reply with only this compact card; do not repeat the mathematical demo:

READY FOR LOOM
commit: <full commit>
tests: <passed count>/<total count>
database: /tmp/homology-db-loom.sqlite3
snapshot_id: <snapshot id>
working tree: clean / not clean

Then wait for my first on-camera question.
```

Check that Codex says `READY FOR LOOM`, reports 41/41 tests, names Snapshot
`preview-5ea7db464f937061`, and says the working tree is clean. If any value is
different, do not start recording; ask Codex to explain the discrepancy.

## 0:00--2:00: spoken introduction

Read this naturally. It is intentionally conversational rather than a complete
technical description.

> Hi Gabriel, hi Dan. This is a very quick look at an early prototype of
> Homology DB.
>
> The longer-term idea is to let an AI retrieve mathematical facts and useful
> examples while keeping the database—not the AI's memory—as the source of
> truth. A mathematician should be able to inspect and challenge the answer.
>
> What exists today is small. It is a local, deterministic preview with sixty
> named manifold examples. It currently supports ordinary Homology over the
> integers and over F2, F3, F5, and F7. Codex can resolve the name of a space,
> ask for its Homology with specified coefficients, search for examples with a
> specified Homology pattern, and inspect evidence. Results carry Snapshot,
> assertion, and evidence identifiers, so they are tied to stored data rather
> than silently filled in by the language model.
>
> What does not exist yet is just as important. This is not the full named
> atlas. CP n and many other standard examples still need to be added with
> proper provenance. There is no hosted interface, general rational
> coefficients, cohomology-ring support, stable-stems database, or
> spectral-sequence database. Representatives and nonidentity induced maps are
> generally not computed.
>
> I only want to show two interactions. First: tell me the Homology of a named
> space with chosen coefficients. Second: give me examples of spaces whose
> Homology has a pattern I care about. Extending that search to Homotopy data is
> an obvious next step, but it is not implemented yet.

## 2:00--3:00: use case 1

Paste this into the same prepared Codex task:

```text
Using the existing /tmp/homology-db-loom.sqlite3 database without rebuilding
it, use only the public Homology DB operations to tell me H_*(RP^4; F2).

Give me a compact on-camera answer: a degree/value table, the one snapshot_id,
the assertion IDs, and the common evidence ID. Do not query SQL, browse the
web, or add facts not returned by the database. Keep the answer short enough to
read in under one minute.
```

After Codex answers, say:

> So this is the direct lookup direction: a named space and chosen
> coefficients, with the answer tied back to one stored Snapshot.

## 3:00--4:00: use case 2

Paste this into the same Codex task:

```text
Using the same /tmp/homology-db-loom.sqlite3 database and the same snapshot_id,
use only the public Homology DB operations to find examples with 5-primary
torsion in H_1.

Give me a compact on-camera answer: list the matched spaces and their H_1
groups, retain their assertion and evidence IDs, and state the search coverage.
Make clear that these are the proven matches in this Snapshot, not a
classification of every space in mathematics. Keep the answer short enough to
read in under one minute.
```

Finish with:

> That is the reverse direction: start with a Homology pattern and retrieve
> examples. Later I would like to extend this to Homotopy and eventually to
> combinations of Homology, Homotopy, and spectral-sequence information. For
> now I mainly want to know whether these two basic interactions feel useful,
> and which missing examples or awkward answers you notice first.

## If Codex gives an unexpectedly long answer

Paste:

```text
Compress that to what can be read on screen in 30 seconds. Preserve the
snapshot_id, mathematical values, assertion IDs, evidence IDs, and coverage
qualification; remove implementation commentary.
```
