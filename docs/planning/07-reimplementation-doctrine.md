# Reimplementation doctrine

## Direction

Reimplement the relevant algebraic-topology and spectral-sequence capabilities as parts of one coherent system.

Existing systems are valuable, but their runtime objects, file formats, convention silos, and computation state should not define the new architecture. They serve as:

- attributed algorithm and design references;
- sources of published datasets and examples;
- behavioral specifications where documentation is incomplete;
- temporary bootstrap/reference backends;
- independent differential-test oracles;
- catalogs of known limitations and failure cases.

The goal is not source-compatible rewrites. The goal is a cleaner mathematical specification, canonical data model, reproducible computation state, and interoperable implementation.

## What the project should own

Over time, the project should own:

- mathematical identities for spaces, models, maps, spectra, and constructions;
- canonical algebraic structures and basis semantics used by the platform;
- chain complexes, filtrations, maps, and homology computation workflows;
- spectral-sequence pages, classes, differentials, products, extensions, and knowledge states;
- computation scheduling, checkpoints, derivations, contradictions, and provenance;
- adapters between canonical records and optimized low-level kernels;
- structured queries, snapshots, exports, and LLM-facing evidence bundles;
- conventions and conversion maps between published bases and notations.

## What the project need not own

Do not reimplement infrastructure whose abstraction is already clear and whose behavior is not specific to the mathematical research harness:

- relational databases;
- operating systems and container runtimes;
- arbitrary-precision integer primitives;
- standard dense/sparse storage formats where suitable;
- mature low-level linear-algebra kernels behind narrow interfaces;
- compilers, language runtimes, and web protocols.

These dependencies must remain replaceable and must not leak engine-specific identities into canonical mathematics.

## Capability workflow

Reimplement one capability at a time:

1. **Specify:** state the mathematical input, output, conventions, partiality, and failure modes independently of code.
2. **Collect fixtures:** gather hand proofs, published data, and outputs from multiple existing systems with attribution.
3. **Normalize:** express all fixtures in the tentative canonical interchange and expose disagreements.
4. **Reference implementation:** write the clearest correct version before optimizing.
5. **Differential testing:** compare against independent systems and published tables over a bounded region.
6. **Invariant testing:** enforce identities such as `d² = 0`, functoriality, Euler–Poincaré checks, and basis-change consistency where applicable.
7. **Optimize:** replace bottlenecks behind stable semantic interfaces, retaining exact comparison tests.
8. **Publish limitations:** record bounded validity, unknown cases, algorithmic assumptions, and performance cliffs.

No imported output becomes canonical merely because two programs agree. Agreement is evidence attached to an assertion.

## Quality bar

A replacement capability is ready only when:

- its mathematical contract is documented without referring to implementation classes;
- outputs are deterministic or record the source of nondeterminism;
- bases, gradings, coefficients, and conventions are explicit;
- it reproduces a declared reference corpus;
- discrepancies with prior systems are investigated and retained;
- every result points to a computation run and algorithm attribution;
- the implementation has property/invariant tests beyond golden-file comparison;
- failure and incomplete-computation states are serializable and queryable;
- performance is measured on representative workloads;
- a future implementation can replace it without changing canonical identities.

## Initial order

The owned capability stack should emerge in the same gentle order as the data:

1. canonical finitely generated abelian groups and finite-dimensional vector spaces;
2. based chain complexes and chain maps;
3. ordinary homology with representatives and induced maps;
4. finite simplicial/CW model translation;
5. filtered complexes and associated graded data;
6. the minimal structures forced by Serre examples;
7. Serre computation capabilities;
8. the algebraic structures forced by Adams examples;
9. Adams computation and deduction capabilities.

This is a direction, not a delivery schedule. Each step should be constrained by examples until its interface is difficult to make simpler.

## Attribution

Reimplementation does not erase ancestry. For each capability, maintain machine-readable and human-readable attribution for:

- originating definitions, theorems, and algorithms;
- prior software implementations and contributors studied;
- datasets and test vectors used;
- basis/convention translations learned from upstream work;
- discovered discrepancies and upstream corrections.

Licensing is deferred. Accurate attribution and source records are still required now because provenance is part of the mathematics and engineering history, not merely a licensing obligation.
