# Local Homology DB test drive

This is the shortest path from a clean checkout to a useful conversation with
the database. It uses only the Python standard library and writes its
disposable SQLite file under `/tmp` by default.

## Best experience in Codex

From this repository, tell Codex:

> Run `python3 -m homology_db demo`. Then use the structured Homology DB tools
> to answer three questions I choose. For every group, show me its assertion ID
> and expand its evidence. Tell me explicitly when the preview cannot answer.

Codex can run the command, translate your mathematical question into one of
the four structured calls, and explain the returned record. There is no custom
natural-language parser in the repository: Codex is a client of the same JSON
interface an eventual QA agent will receive.

## One-command tour

```bash
python3 -m homology_db demo
```

Expected headline facts:

- the snapshot contains exactly 60 fixed common-manifold subjects;
- the Klein bottle has `H_0 = Z`, `H_1 = Z + Z/2`, and `H_2 = 0`;
- `RP^4` has one `F_2` generator in degrees 0 through 4;
- the degree-one 5-primary search finds `L(5,1)`, `L(5,2)`, and `L(10,1)`;
- every returned group carries an assertion ID and evidence ID from one
  deterministic snapshot.

## Ask the four tools directly

Resolve a name:

```bash
python3 -m homology_db tool '{"tool":"resolve_subject","arguments":{"query":"Klein bottle"}}'
```

Read complete integral Homology:

```bash
python3 -m homology_db tool '{"tool":"read_homology","arguments":{"subject":"RP^4","coefficient":"Z"}}'
```

Find proven examples with 5-primary torsion in degree one:

```bash
python3 -m homology_db tool '{"tool":"query_examples","arguments":{"pattern":{"degree":1,"torsion_prime":5,"limit":20}}}'
```

Expand evidence returned by the Klein-bottle computation:

```bash
python3 -m homology_db tool '{"tool":"expand_evidence","arguments":{"evidence_ids":["preview:evidence:nonorientable_surface:2"]}}'
```

Supported coefficients are `Z`, `F2`, `F3`, `F5`, and `F7`. Reduced Homology
is selected with `"reduced":true`. Unsupported coefficients, unknown tools,
malformed requests, ambiguous identities, and missing identities return typed
outcomes; they are never changed into empty groups or mathematical zeroes.

To keep a separate disposable database, put `--db PATH` before the subcommand:

```bash
python3 -m homology_db --db /tmp/my-homology-preview.sqlite3 demo
```

## Run the checks

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_manifest_spec.py
```

The first command tests the human CLI and the same four public tool seams used
by agents. The second independently derives the planned release-corpus counts
from the machine manifest.

## What this preview is—and is not

The preview computes from ordered sparse cellular chains over the integers and
the supported finite fields. It uses exact Smith determinantal divisors for
the small integral matrices and direct modular boundary ranks over fields. The
60-subject cohort includes spheres, orientable and nonorientable surfaces,
tori, real projective spaces, lens spaces, sphere products, disks, and
surface-circle products.

It is deliberately not the `0.0.1` release:

- it does not yet ingest or qualify the planned 1,159 reconstructible Models;
- its Smith algorithm is exact but exponential and only accepts the preview's
  separated nonzero-boundary shape;
- Smith basis transformations, general cycle representatives, and nonidentity
  induced maps are explicitly `not_computed`;
- the disk rows use a labelled homotopy-equivalent chain model, not a counted
  homeomorphic disk presentation;
- it has no uncertainty/conflict fixture corpus and has not run the frozen
  100-prompt external-agent acceptance suite; and
- its rows are local preview evidence, not release-ledger assertions.

Those boundaries should be visible during testing. If an answer crosses one,
that is a bug worth reporting rather than something Codex should smooth over.
