# First implementation tasks

The first milestone is a **queryable homology kernel**: a small, correct, reproducible database whose schema and API have already been tested against the downstream work we expect. A public website comes later.

## Architectural decision for the first milestone

Use PostgreSQL with two result layers:

1. append-only, provenance-rich result assertions;
2. a rebuildable current-homology projection optimized for reads.

The projection is not a second source of truth. It is selected deterministically from assertions and can be dropped and rebuilt. This lets consumers ask ordinary mathematical questions without joining the full editorial history, while preserving every correction and conflict.

Use integer database keys for efficient joins and separate immutable public IDs such as `ATSP-000001`. Do not put mathematical meaning into primary keys.

## Task 1: define the downstream query contract

Before designing tables, write the queries the project must make cheap. Each query needs:

- a name and motivating downstream workflow;
- inputs and coefficient/reduced-homology conventions;
- expected result shape and stable ordering;
- whether it reads the current release or assertion history;
- expected selectivity and batch size;
- an initial performance target on documented hardware;
- a correctness fixture.

The first query set should include:

1. resolve one public ID, external ID, or alias;
2. resolve a batch of public IDs without one query per ID;
3. return all known `H_n(X; Z)` for one space or model;
4. return `H_n(X; F_p)` for specified `n` and `p`;
5. find spaces with a specified Betti number in degree `n`;
6. find spaces with `p`-torsion in degree `n`;
7. find spaces with a specified primary summand `(p^e)^m`;
8. find spaces having an exact integral homology signature over a degree range;
9. find candidate spaces satisfying a partial homology pattern, including required, forbidden, and unknown degrees;
10. rank candidate spaces sharing part or all of a known homology signature and explain every match;
11. distinguish trivial, unknown, not computed, conflicting, and not applicable results;
12. list every concrete model of a conceptual space;
13. trace the source and computation run behind one displayed group;
14. retrieve a computation-ready model/chain-complex bundle with explicit conventions;
15. find computed model results that have not been promoted to their conceptual space;
16. retrieve all changes between two published snapshots;
17. stream a complete release or a filtered result set without offset pagination.

Initial acceptance criterion: these queries and result shapes are checked into the repository before the physical schema is treated as stable.

## Task 2: freeze the MVP mathematical encodings

Define and validate:

- subjects: conceptual space versus concrete model;
- coefficient systems: only `Z` and prime fields `F_p` initially;
- reduced versus unreduced homology;
- nonnegative degree;
- finitely generated abelian groups over `Z`;
- finite-dimensional vector spaces over `F_p`;
- explicit knowledge states;
- exact versus bound or conjectural assertions;
- model-to-space promotion requirements.

For integral homology, keep two equivalent canonical forms:

- interchange/display: free rank plus torsion invariant factors;
- indexed read projection: free rank plus primary summand rows `(prime, exponent, multiplicity)`.

Required validators include:

- invariant factors are greater than one and each divides the next;
- primary summands reconstruct the same finite group;
- primes are actually prime, exponents and multiplicities are positive;
- field dimensions and free ranks are nonnegative;
- `exact` results have a value while non-value states do not masquerade as SQL `NULL`;
- the Euler–Poincaré check holds when the necessary finite data are complete.

Acceptance criterion: valid examples round-trip between encodings; deliberately invalid fixtures fail with specific errors.

## Task 3: build the PostgreSQL schema spike

The spike needs only the tables required for the query contract:

- `objects` and `object_names`;
- `models` and `model_of_assertions`;
- `coefficient_systems`;
- append-only `result_assertions`;
- `computation_runs` and `references`;
- `current_homology_groups`;
- `current_homology_primary_summands`;
- `snapshots` and snapshot membership/change metadata.

Important constraints:

- one selected current row per subject, coefficient system, reduced convention, and degree;
- current rows point back to their selected assertion;
- primary summands cannot exist for a non-exact or non-integral result;
- aliases are unique within a documented namespace;
- public IDs are immutable and unique;
- source assertions are never updated in place to rewrite mathematical history.

Initial index candidates, to be justified by query plans:

- current group lookup on `(subject_id, coefficient_system_id, reduced, degree)`;
- search on `(coefficient_system_id, reduced, degree, free_rank)`;
- primary torsion lookup on `(prime, exponent, multiplicity, homology_group_id)`;
- model lookup on `object_id` through the selected model-of relation;
- public and external identifier lookup;
- current-status and snapshot indexes needed by the query contract.

Do not partition tables yet. Add partitioning only when measured data volume and query plans justify the operational cost.

Acceptance criterion: migrations build an empty database, seed fixtures load transactionally, the current projection rebuilds deterministically, and every priority query has a captured plan.

## Task 4: create a small adversarial seed corpus

Start with roughly 20 spaces and 30 models, chosen for coverage rather than size:

- point, empty space, and contractible but nontrivial complexes;
- spheres in several dimensions;
- circle, torus, and products of spheres;
- orientable and nonorientable surfaces;
- real projective spaces and a lens space for torsion;
- wedges and a suspension;
- two nonidentical models of the same conceptual space;
- one conflicting imported assertion;
- one unknown result, one not-computed result, and one not-applicable field;
- one corrected/superseded assertion;
- both reduced and unreduced values where degree zero exposes the difference.

Keep this corpus human-reviewable and checked into version control. Every record should state whether it is hand-curated, literature-sourced, or computed.

Acceptance criterion: each branch of the mathematical state model and each priority query is exercised by at least one fixture.

## Task 5: add a synthetic scale and benchmark harness

Correct small fixtures do not reveal bad query plans. Generate deterministic synthetic data at increasing tiers while clearly marking it as non-mathematical test data.

Measure:

- point lookup and batch lookup;
- first-page selective searches;
- torsion searches at common and rare primes;
- exact signature matching;
- current-projection rebuild time;
- snapshot diff and bulk export throughput;
- index sizes and load time.

Capture the database version, schema commit, dataset seed and size, hardware, cache state, timings, and `EXPLAIN` plans. Prefer cursor/keyset pagination. A performance number without its environment is not an acceptance test.

Acceptance criterion: the repository contains a repeatable command that loads a chosen scale tier and produces a machine-readable benchmark report.

## Task 6: specify the read API from the query contract

Design `/api/v1` only after the SQL workload works. The first API should provide:

- object and model lookup;
- batch lookup;
- homology search with explicit coefficient and reduced conventions;
- provenance expansion on request;
- cursor pagination with deterministic sorting;
- projection/field selection;
- snapshot selection;
- streamed bulk export in a documented format;
- schema version and release metadata in responses.

The API must never return a bare group without its coefficient system, degree, reduced convention, status, and snapshot context.

Acceptance criterion: each endpoint maps to a named query-contract item and has example requests, responses, and error cases.

## Task 7: implement the first computation adapter

After the data kernel is stable, build a Sage adapter that:

- receives a versioned model artifact;
- emits or references a versioned chain complex with ordered bases and boundary matrices when supported;
- computes ordinary homology under explicit conventions;
- records the full run manifest and exact input/output hashes;
- emits the versioned interchange schema rather than writing SQL directly;
- is idempotent on the same input and algorithm version;
- never promotes model results to a conceptual space by itself.

Then add one independent validation path using HAP or simpcomp for a deliberately small subset.

Acceptance criterion: a clean run regenerates the seed results, repeated imports do not duplicate assertions, and disagreements are stored as conflicts.

## Immediate working order

The first development cycle should complete tasks 1–4 in this order:

1. query contract;
2. mathematical encodings and fixtures;
3. PostgreSQL schema spike;
4. adversarial seed corpus and captured query plans.

Tasks 5–7 follow once the shape of real queries is stable enough to benchmark. A web UI is intentionally absent from this cycle.

## Decisions that can remain deferred

- public project name and visual design;
- frontend framework;
- generalized homology theories;
- user accounts and public submissions;
- large object storage provider;
- table partitioning and distributed databases;
- formal proof certificates;
- official LMFDB integration.
