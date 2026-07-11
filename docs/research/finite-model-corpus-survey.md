# Finite-model corpus survey for Homology DB 0.0.1

Date: 2026-07-11
Status: ticket-03 research result; source qualification, not an ingestion or licensing decision

## Answer

There is enough reconstructible upstream material to make the 1,000-model
release floor realistic, but there is no single source that honestly supplies
the whole release.

Use the versioned **Stellar v6 archive** as the leading bulk-source candidate.
It contains explicit triangulations at a frozen DOI with per-file checksums and
sidecars. Use live **polyDB** as the queryable, structured view of substantially
the same Lutz enumeration and as a cross-check, not as a second independent
corpus. Use **simpcomp** for a smaller, named, higher-dimensional and
torsion-bearing library. Use pinned **SageMath** constructors for transparent
generated families and as an external homology oracle. Use **HAP** for a small
set of valuable simplicial/regular-CW fixtures and differential validation, not
for scale. Keep **Regina** generalized triangulations outside the first model
boundary until conversion semantics are decided.

The bulk data prove that the finite-simplicial floor is easy. They prove the
regular-CW floor only if ticket 04 accepts a neutral, reconstructible regular-CW
face/incidence representation derived from a disjoint set of triangulations.
The same source artifact must never count in both buckets. If ticket 04 rejects
that representation, this survey has not found 400 already-materialized
regular-CW artifacts; they will need an owned generator or another source.

No upstream homology value becomes canonical. Every counted artifact must pass
our owned parse, chain construction, `d^2 = 0`, and integral Smith-normal-form
pipeline. Upstream homology is comparison evidence with explicit conventions.

## Role assignment

| Source | Verified shape and volume | Stable locator and update path | Reconstructible? | Recommended 0.0.1 role |
|---|---|---|---|---|
| [Stellar v6](https://zenodo.org/records/17495553) | Frozen text triangulations: 42,426 exact-ten-vertex 2-manifold records, 249,015 exact-ten-vertex 3-manifold records, and a separate 4,787-record small-valence file, plus homology/type sidecars | DOI version, file name, advertised MD5, our SHA-256 and row number/hash; new Zenodo version is a new upstream snapshot | Yes: mixed-lexicographic records encode the triangulations | Primary frozen bulk candidate; select a small deterministic, stratified manifest and deduplicate across files/sources |
| [polyDB `Manifolds.DIM2_3`](https://polydb.org/rest/current/collection/Manifolds/DIM2_3) | 293,497 current records: 43,138 IDs with the dimension-2 prefix and 250,359 with the dimension-3 prefix; each has `FACETS`, `F_VECTOR`, and `HOMOLOGY` | Unique `_id`, collection/schema and record version, retrieval time, raw hash; `current` is moving | Yes: complete abstract-simplicial facets | Structured browse/query cross-check and possible supplement; not a second corpus beside Stellar |
| [simpcomp at `aff7cf2`](https://github.com/simpcomp-team/simpcomp/tree/aff7cf2bcef0828fb4d02296cf276b777705274b/complexes) | 648 `.scb` files: 422 transitive, 181 named manifolds, 45 pseudomanifolds | Git commit + relative path + raw hash; numeric library index is not stable across re-sorts | Yes after executing the pinned decoder; `.scb` itself is engine-native GAP pickle data | Named/torsion-rich seeds, attribution fixtures, and independent isomorphism checks |
| [SageMath 10.9](https://github.com/sagemath/sage/releases/tag/10.9) | 52 catalog bindings but only four standalone Kenzo topology files; mostly constructors, not stored models | Release commit + qualified constructor + canonical arguments + exported hash | Yes for deterministic outputs exported to neutral facets/face tables/cubes | Owned-manifest generator seed and external deterministic homology oracle; never canonical persistence/query runtime |
| [HAP 1.76](https://github.com/gap-packages/hap/releases/tag/v1.76) | Four literal named triangulations plus one tutorial Klein bottle; 25 cube items and many others are recipes, not stored decoded spaces | Release commit/archive hash + source path + recipe/arguments + normalized output hash | Yes for the literal lists and materialized deterministic recipes | Small high-value regular-CW/simplicial fixtures and differential oracle; not corpus backbone |
| [Regina supporting data](https://regina-normal.github.io/data.html) | Large 3-manifold censuses, including 11,031 orientable and 18 non-orientable closed hyperbolic entries | Census file/version plus Regina isomorphism signature | Yes as generalized face-pairing triangulations | Later source/oracle; not an abstract-simplicial or agreed regular-CW model without a validated conversion |

Counts are upstream records, not yet release-countable models. They have not
passed our importer, duplicate detection, equivalence review, or release gates.

## Method and confidence

This survey used official repositories, release records, documentation, REST
schemas, and dataset files. Counts marked as verified were obtained by direct
file/manifest enumeration or read-only API counts. Source-code examples and
doctest homology values were not promoted to computation results. The locally
installed `sage` command points to a missing Sage 9.6 application, so Sage 10.9
was source-audited but not executed.

The relevant immutable anchors are:

- Sage 10.9 tag commit `686dc1a8d420c2e0aabadd4f602d9a0aa4690c50`.
- HAP 1.76 tag commit `6677964ab9ca90ecfff0cc920bcb0be1e0ae130f`;
  release archive SHA-256
  `442c6972115e24cec60f12f7fb59c62f2623daa8524b9e262d21de067d007e48`.
- simpcomp audited commit
  `aff7cf2bcef0828fb4d02296cf276b777705274b`; its package metadata still
  identifies version 2.1.14 dated 2022, so the commit is the reliable pin.
- Stellar v6 DOI `10.5281/zenodo.17495553`, published 2025-10-31.
- polyDB live counts were retrieved 2026-07-11 and must be time-stamped rather
  than treated as a frozen release.

## Stellar and polyDB: scale, with one provenance lineage

### Stellar v6

The [Zenodo record](https://zenodo.org/records/17495553) identifies Bastian
Rieck as data curator and Frank H. Lutz as data collector. It preserves the
Manifold Page triangulations in mixed lexicographic format. Direct record
enumeration found:

- `2_manifolds_10_all.txt`: 42,426 records;
- `3_manifolds_10_all.txt`: 249,015 records;
- `manifolds_lex_d3_deg5.txt`: 4,787 records.

The archive supplies corresponding homology/type sidecars. Zenodo advertises,
among others, MD5
`199ac551cb69dd7e0337d50f90ac7840` for the 2-manifold file,
`a4ea3a512a7f3f315ecf78b725c2a3f0` for the 3-manifold file, and
`6ac6d25927ef9bab753e418c91c4db38` for the small-valence file. The record
documents a syntax-only repair to 26 lines of the small-valence file and the
addition of its torsion-bearing homology sidecar. Version 6 also repairs a
missing newline between two records in `2_manifolds.txt`. Those are editorial
events we must retain, not silently erase.

The 4,787-record collection can overlap the enumerations and the named
collections. Counts must therefore be deduplicated after decoding; they must
not simply be added. A raw source locator should contain DOI version, file,
record ordinal, raw-record hash, and full-file hashes. A normalized model gets
a separate canonical-byte hash and decoder version.

The record states CC BY 4.0 and names the curator/collector. That is a recorded
source fact, not a project licensing decision.

### polyDB

The live [collection metadata](https://polydb.org/rest/current/collection/Manifolds/DIM2_3)
describes combinatorial 2- and 3-manifolds with at most ten vertices, computed
by Frank Lutz; it names Frank Lutz and Constantin Fischer as authors and
Andreas Paffenholz as maintainer. The
[schema](https://polydb.org/rest/current/schema/Manifolds/DIM2_3) requires
`_type = topaz::SimplicialComplex`, `FACETS`, `F_VECTOR`, and `HOMOLOGY`.
These are reconstructible model records, not invariant-only rows.

Read-only counts against the current API returned:

- all records: 293,497;
- `_id` matching `^manifold_2_`: 43,138;
- `_id` matching `^manifold_3_`: 250,359;
- non-empty `HOMOLOGY.1.0`: 39,718;
- an exact order-2 element in `HOMOLOGY.1.0`: 39,718;
- an exact order-2 element in `HOMOLOGY.2.0`: 616;
- exact order 3, 4, 5, or 7 elements in `HOMOLOGY.1.0`: zero.

The homology array is convention-sensitive and the query language follows
Mongo missing-field behavior. A broad `$ne: []` predicate is not sufficient
evidence unless field existence and array shape are also checked. We sampled
records with explicit `Z/2` in degree 2 to validate the 616 count.

The current collection therefore gives abundant 2-primary torsion but cannot
meet the release's 3-, 5-, and 7-primary coverage by itself. Its identifiers
are model identifiers, not curated identities for mathematical spaces. Unnamed
records may satisfy the model floor; they do not become curated spaces without
separate identity/equivalence evidence.

[polyDB's REST guide](https://polymake.org/doku.php/polydb/rest/intro) and
[polymake API guide](https://polymake.org/doku.php/user_guide/howto/polydb_api)
describe cursor-based access. For every selected row, freeze the exact raw
JSON and hash; a query against `/current/` is not a reproducible snapshot.

### Overlap rule

Stellar, polyDB, and simpcomp all contain Lutz material. They are not three
independent votes. Normalized facet hashes catch byte-identical relabelings
only after canonical relabeling; combinatorial isomorphism checks are still
needed. Duplicate artifacts retain all provenance assertions but count once.
The first manifest should prefer one frozen Stellar record when it exists,
then attach polyDB/simpcomp locators as corroborating provenance.

## simpcomp: the named library

The audited repository contains exactly 648 `.scb` artifacts:

| Subtree | Files |
|---|---:|
| `transitive` | 422 |
| `manifolds` | 181 |
| `pseudomanifolds` | 45 |

The named manifold files span dimensions 2 through 6; the transitive library
also reaches dimension 8. The library includes triangulations named
`L_3_1`, `L_4_1`, `L_5_1`, `L_5_2`, `L_6_1`, `L_7_1`, `L_7_2`,
`L_8_1`, `L_8_3`, `L_9_1`, `L_9_2`, `L_10_1`, and `L_10_3`, as well as
connected sums and mapping-cylinder examples. These make simpcomp a strong
place to seek named 3-, 5-, and 7-primary fixtures.

The files are GAP `IO_Pickle` artifacts, as shown by the pinned
[I/O implementation](https://github.com/simpcomp-team/simpcomp/blob/aff7cf2bcef0828fb4d02296cf276b777705274b/lib/io.gi).
They are reconstructible through a pinned GAP/simpcomp runtime, but not a
neutral or durable canonical format. Preserve each `.scb` as the source blob;
the adapter must emit a versioned, canonical facet-list document.

The binary `complexes.idxb` carries name, f-vector, homology, and source-file
properties. Global library numbers are sorted by f-vector and can change when
the library changes. The stable source key is therefore commit + relative path
+ raw hash; the library number and display name are aliases.

There is an upstream inconsistency worth preserving: direct enumeration and
the generated index/documentation give 648 artifacts, while a doctest in
`lib/lib.gi` prints 7,648. Treat the latter as a documentation defect, not a
hidden corpus. The package declares GPL-2.0-or-later for code; no separate
per-artifact data statement was found in the audited tree. Record both facts
without making policy here.

## SageMath: generator and oracle, not corpus

The [10.9 simplicial-complex catalog](https://github.com/sagemath/sage/blob/686dc1a8d420c2e0aabadd4f602d9a0aa4690c50/src/sage/topology/simplicial_complex_catalog.py)
has 29 exported names but 28 distinct callables because `ProjectivePlane`
aliases `RealProjectivePlane`. Across simplicial complexes, simplicial sets,
delta complexes, and cubical complexes there are 52 catalog bindings. Most are
parameterized recipes; two simplicial-complex constructors are random.

Only four standalone topology artifacts occur in
[`src/sage/ext_data/kenzo`](https://github.com/sagemath/sage/tree/686dc1a8d420c2e0aabadd4f602d9a0aa4690c50/src/sage/ext_data/kenzo):
finite simplicial-set descriptions for `CP2`, `CP3`, `CP4`, and `S4`, with 9,
84, 1,189, and 2 nondegenerate simplices respectively. The README describes
the CP artifacts as homotopy-equivalent models, not triangulations; the model
relationship must retain that level.

Neutral exports are practical:

- a `SimplicialComplex` from canonically relabeled maximal facets;
- a `DeltaComplex` from dimension-indexed ordered face tables;
- a `CubicalComplex` from maximal elementary integer cubes;
- a finite simplicial set from indexed nondegenerate simplices and ordered
  face/degeneracy data.

Sage `.sobj` persistence is pickle-based and the
[official persistence documentation](https://doc.sagemath.org/html/en/reference/misc/sage/misc/persist.html)
warns about compatibility after drastic internal changes. It cannot be the
canonical format.

The [`MooreSpace(q)` constructor](https://github.com/sagemath/sage/blob/686dc1a8d420c2e0aabadd4f602d9a0aa4690c50/src/sage/topology/simplicial_complex_examples.py#L466-L522)
provides reduced `H_1 = Z/q`; suspensions move torsion to higher degrees and
wedges create controlled multiplicity. Projective spaces, matching complexes,
and
[`SumComplex`](https://github.com/sagemath/sage/blob/686dc1a8d420c2e0aabadd4f602d9a0aa4690c50/src/sage/topology/simplicial_complex_examples.py#L1262-L1363)
add independent families. The 10.9 `SumComplex` doctest itself contains a
discrepancy: it prints `C146989209` and then factors `1648910295`. Doctest
expected values are assertions to check, not truth to import.

External validation must make Sage's defaults explicit:

```python
C = X.chain_complex(base_ring=ZZ, augmented=False, check=True)
H_n = C.homology(n, algorithm="pari")
```

Topology `homology()` is reduced by default, while topology
`chain_complex()` defaults to `check=False`. Canonical groups must be compared
structurally, never by parsing printed strings.

## HAP: valuable semantics, surprisingly little ordinary-space data

HAP 1.76's
[`manifolds.gi`](https://github.com/gap-packages/hap/blob/v1.76/lib/Manifolds/manifolds.gi)
contains four literal named maximal-simplex lists: torus, `RP2`, `CP2`, and
K3. A [tutorial fixture](https://github.com/gap-packages/hap/blob/v1.76/tutorial/tutex/1.1.txt)
adds a literal Klein bottle. These are genuine reconstructible source recipes,
but they are not a corpus.

Other large-looking HAP directories must not inflate the release count:

- 25 cube-manifold items are deterministic recipes/transcripts, not stored
  decoded CW artifacts;
- 801 prime-knot entries are reconstructible cubical arc recipes, but as
  ordinary spaces the knots are circles and add almost no homology diversity;
- 819 knot-census rows are identification signatures, not models;
- 124 compressed arithmetic G-complex files have only 108 distinct
  decompressed payloads and describe equivariant orbit/stabilizer data for
  generally infinite contractible G-CW complexes, not finite ordinary spaces.

For regular CW export, retain an ordered cell basis by dimension, immediate
face indices, and parallel incidence signs. HAP's boundary arrays and
orientation arrays can reconstruct this shape, but the importer must validate
indices, closure conditions, dimensions, and `d^2 = 0`; HAP constructors are
not themselves proof of validity.

Useful attributed computation fixtures include `RP2`, the Klein bottle,
selected cube quotients, lens-space recipes, and the Seifert--Weber
dodecahedral example with an upstream claim of `H_1 = (Z/5)^3`. They count only
after deterministic materialization and owned verification. HAP encodes a free
`Z` summand as `0`, a torsion invariant as an integer greater than one, and the
zero group as `[]`. Missing or failed computation must never be mapped to
`[]`. The documented probabilistic `HomologyPb` routines have nonzero error
probability and are excluded from release evidence.

HAP's package metadata declares GPL-2.0-or-later and the documentation page
declares GFDL for docs; contributed data lack a separate per-file statement in
the audited tree. Preserve source-specific attribution without deciding policy.

## Regina: large, but a different model category

Regina's [triangulation documentation](https://regina-normal.github.io/docs/triangulations.html)
uses generalized triangulations built from top-dimensional simplices with
facet pairings. Faces may be identified with each other, so this is not
automatically an abstract simplicial complex. Regina isomorphism signatures
are canonical for combinatorial isomorphism and can reconstruct a
triangulation.

This makes Regina an excellent later generalized-triangulation source and an
independent 3-manifold homology/isomorphism oracle. It does not discharge the
current simplicial or regular-CW floor unless ticket 04 admits this category or
we specify and validate a subdivision/conversion that preserves the intended
space and provenance.

A direct audit of Regina's official `closed-or-census.rga` found 14,720
triangulation packets (embedded engine version 5.96), with file SHA-256
`e5fb88e2bd969645fba57f1d2fe8e1398efb52718664fa626b399da4ef95d76a`.
Its cached first-homology factors include 3-, 5-, and 7-primary torsion and
prime powers. These are useful comparison assertions, not canonical values.

## Coverage against the observable contract

| Release need | What this survey establishes | Remaining proof obligation |
|---|---|---|
| 1,000 reconstructible models | Stellar/polyDB alone provide orders of magnitude more explicit simplicial records | Exact deterministic manifest; successful decoder/round-trip; duplicate accounting |
| 400 finite-simplicial artifacts | Clearly feasible from a frozen, stratified Stellar selection | Owned parser, canonical bytes, hashes, validation |
| 400 finite/regular-CW artifacts | Feasible only if a neutral face/incidence representation of a disjoint triangulation selection is admitted as a counted model | Ticket-04 boundary decision and an executable reconstruction prototype; otherwise find/generate another corpus |
| 100 curated spaces / 12 families | Named simpcomp/Sage/HAP examples and Stellar type sidecars provide seeds | Identity/equivalence review, family caps, references, exact 100-space manifest |
| 2-, 3-, 5-, 7-primary torsion | polyDB supplies abundant 2-primary; Sage Moore spaces and simpcomp lens spaces deliberately supply other primes; HAP adds fixtures | Owned computations, degree/power/multiplicity counts, no generator monoculture |
| Torsion above degree 1 | Sage suspension and documented higher-degree examples make this constructible | Explicit models and independent recomputation |
| Independent validation | Sage deterministic SNF, HAP deterministic integral homology, simpcomp/Regina isomorphism tools | Pinned runnable environments, adapters, run manifests, structural comparison |
| Attribution and updates | Every leading source has a pinning mechanism; Stellar is especially strong as a DOI snapshot | Per-record source assertions, citations, correction events, refresh policy after 0.0.1 |

## First manifest hypothesis, not yet a decision

Ticket 07 should test this shape rather than silently adopting it:

1. Pin Stellar v6 and implement a streaming decoder for a tiny fixture first.
2. Select at least 1,000 source records by a deterministic stratified rule over
   dimension, vertex/facet counts, homology sidecars, and source file; do not
   hand-pick only easy rows.
3. Assign each selected source record to exactly one counted storage/model
   format. Never count a facet document and its face-poset expansion twice.
4. Add named simpcomp, Sage, and HAP fixtures for curated identity, prime
   coverage, higher dimensions, multiple presentations, and differential
   validation. Deduplicate all Lutz overlaps.
5. Keep original blobs, advertised checksums, our SHA-256 values, decoder
   version, normalized bytes/hash, source metadata, and every validation run.
6. Recompute all homology. Store upstream values as separately attributed
   assertions, including conflicts and convention mismatches.
7. Keep Sage, GAP/HAP, simpcomp, and Regina off the query path. The release
   database contains neutral owned data and evidence bundles.

## Fog exposed for later tickets

- Ticket 04 must decide whether face-poset/incidence data are a regular-CW
  Model or only a derived artifact, and what exact reconstruction promise is
  testable.
- Ticket 07 must choose exact records and demonstrate family/identity diversity;
  raw record volume cannot substitute for curated mathematical breadth.
- Canonical relabeling and combinatorial-isomorphism detection need a measured
  prototype on real Stellar/polyDB/simpcomp overlaps before being specified.
- The mixed-lexicographic decoder must be tested against malformed/truncated
  rows and the documented 26-line repair.
- Exact equivalence claims (`isomorphic presentation`, `PL-homeomorphic`,
  `homeomorphic`, `homotopy-equivalent`) need source-level review.
- Source license and redistribution facts have been recorded where visible,
  but policy remains deliberately outside this ticket and release map.
