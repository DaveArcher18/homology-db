# Chromatic Homology Atlas test drive

This is the shortest path from a clean checkout to the current 42-space
development corpus. It uses only the Python standard library and writes a
disposable SQLite database under `/tmp` by default.

## One-command tour

```bash
python3 -m homology_db chromatic demo
```

Expected headline facts:

- the Snapshot contains exactly 42 named CW spaces in 17 families;
- 21 spaces have integral torsion, across primes 2, 3, 5, and 7, including
  `Z/4`, `Z/8`, and `Z/9` examples;
- `M(Z/5,2)` has `H_2 = Z/5`;
- `L^5(3;1,1,1)` has `H_3 = Z/3`;
- `CP^2` has a retained Hopf attaching map, not merely the same zero cellular
  boundary matrices as `S^2 v S^4`; and
- every group carries stable assertion and evidence IDs from one deterministic
  Snapshot.

The unprefixed CLI remains the frozen 60-space preview used by the historical
adversarial audit. Use the `chromatic` prefix for the current product.

## Ask the four tools directly

Resolve a name:

```bash
python3 -m homology_db chromatic tool \
  '{"tool":"resolve_subject","arguments":{"query":"B(C_2^3)"}}'
```

Read integral Homology and its coverage statement:

```bash
python3 -m homology_db chromatic tool \
  '{"tool":"read_homology","arguments":{"subject":"M(Z/9,2)","coefficient":"Z"}}'
```

Read mod-3 Homology. The Universal Coefficient Theorem contributes classes in
degrees 2 and 3, not only degree 2:

```bash
python3 -m homology_db chromatic tool \
  '{"tool":"read_homology","arguments":{"subject":"M(Z/9,2)","coefficient":"F3"}}'
```

Find proven 7-primary examples in degree 3:

```bash
python3 -m homology_db chromatic tool \
  '{"tool":"query_examples","arguments":{"pattern":{"degree":3,"torsion_prime":7,"limit":20}}}'
```

Expand a Model, sources, computation sketch, and optional recorded run:

```bash
python3 -m homology_db chromatic tool \
  '{"tool":"expand_evidence","arguments":{"evidence_ids":["chromatic:evidence:moore:9:2"]}}'
```

Supported coefficients are `Z`, `F2`, `F3`, `F5`, and `F7`. Reduced Homology
is selected with `"reduced":true`. Unsupported coefficients, malformed
requests, ambiguous identities, missing identities, and unsupported query
predicates return typed outcomes; they are never converted into empty groups
or mathematical zeroes.

To keep a separate disposable database, put `--db PATH` after `chromatic` and
before the subcommand:

```bash
python3 -m homology_db chromatic \
  --db /tmp/my-chromatic-homology.sqlite3 demo
```

## Coverage and evidence semantics

Finite CW models return `coverage.kind = complete_finite_cw` and an explicit
upper-vanishing degree. Infinite finite-type spaces such as `BC_3`, `CP^infinity`,
and `BU(2)` return `coverage.kind = bounded_through_degree`, currently through
degree 24, with a null upper-vanishing field. No row above that bound is implied.

The Model is distinct from its cellular boundary certificate. This matters for
spaces with equal ordinary Homology but different topology, including `CP^2`
and `S^2 v S^4`, the Poincare homology sphere and `S^3`, and the two weighted
5-primary lens spaces. An evidence record always supplies a computation sketch
and citations; `computation` is null when no local run was recorded, as for the
pinned Poincare-sphere triangulation.

## Run the checks

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_manifest_spec.py
python3 scripts/export_static_atlas.py \
  --snapshot current --output /tmp/homology-atlas.html
```

The first command includes the frozen preview regression suite and the current
chromatic corpus. The second verifies the older planned release manifest; it is
not the source of the 42-space Snapshot. The exporter builds and validates the
self-contained browser atlas.

## What this corpus is—and is not

This corpus combines exact owned cellular calculations, parameterized formulas,
and cited model calculations. It retains concrete parameters, attaching maps,
quotient or Schubert constructions, sources, and coverage boundaries.

It is deliberately not the qualified `0.0.1` release. It does not claim that
ordinary Homology determines chromatic type, and it does not represent spectra
such as `K(n)`, `E(n)`, `BP`, `tmf`, or finite type-`n` spectra as ordinary
spaces. General cycle representatives and nonidentity induced maps remain
explicitly uncomputed. Those boundaries should stay visible during testing;
if the UI smooths one over, report it with the feedback link on that record.
