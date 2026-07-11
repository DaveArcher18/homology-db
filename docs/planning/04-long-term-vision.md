# Long-term vision and current scope

## Mission

Build an AI-powered research harness or operating system for stable homotopy theorists: a shared mathematical data substrate that removes routine lookup, translation, example hunting, and computation bookkeeping so researchers can spend more time on creative mathematical work.

The system should eventually make known spectral sequences queryable by both people and LLM tools and support workflows that combine known constraints to force or guide new spectral-sequence computations.

## Staged direction

1. **Homology DB:** queryable spaces, models, maps where required by the core object model, ordinary homology, provenance, computation artifacts, and stable interchange.
2. **Serre data module:** fibrations, coefficient systems and actions, page classes, differentials, multiplicative structure, edge maps, transgressions, extensions, and computation provenance.
3. **Adams data module:** spectra, primes and variants, algebraic input, Ext classes, products and operations, differentials, hidden extensions, convergence targets, and competing conventions.
4. **LLM research interface:** structured natural-language retrieval over known objects, computations, and spectral sequences with inspectable query plans and sourced answers.
5. **Computation-forcing system:** explicit constraint propagation, naturality, multiplicativity, comparison maps, vanishing lines, convergence and extension reasoning, with every inferred constraint recorded and reviewable.

Stages 4 and 5 are long-term research goals. They are not promises of near-term automated theorem proving.

## What “one system” means

One system does not mean one schema table or one program that implements every algorithm. It means:

- one durable namespace for mathematical objects, models, maps, computations, and claims;
- one provenance and review model;
- one versioned interchange and snapshot mechanism;
- one query layer that can join information across domain modules;
- explicit convention and coefficient metadata;
- adapters for independent computation engines;
- no silent copying of values between incompatible conventions;
- shareable exports so data is not trapped in the web application.

Algorithms and mathematical domains can remain modular. Serre and Adams data should share identities and evidence without being forced into the same page/differential representation when their semantics differ.

The project intends to reimplement the relevant mathematical capabilities behind this common semantic boundary, with explicit attribution to algorithms, software, datasets, and contributors. Existing high-level systems are not intended to become permanent runtime foundations merely because they already implement a capability.

“Reimplement” does not mean rebuilding PostgreSQL, arbitrary-precision arithmetic, optimized finite-field kernels, compilers, or every mature low-level library. It means owning the algebraic-topology abstractions, algorithms, computation state, provenance, and user-facing behavior that make the system coherent. Low-level dependencies should have narrow, replaceable interfaces.

Existing systems remain essential as specifications, sources of test vectors, temporary reference backends, and independent differential checks. A unified implementation that cannot reproduce and compare their published results would not be credible.

## Design obligations created now

Even while implementing only Homology DB, the foundation must:

- distinguish conceptual objects, concrete models, maps, and relation assertions;
- use immutable public IDs and content hashes;
- treat coefficient systems and conventions as explicit data;
- keep chain-level artifacts and ordered bases when computations produce them;
- allow assertions to cite other assertions and computation runs;
- preserve conflicts and corrections instead of overwriting them;
- publish versioned schemas and reproducible snapshots;
- offer efficient structured queries and bulk access;
- make every LLM-facing answer reducible to a structured query plus sourced records;
- avoid baking the first computation engine’s internal data structures into canonical storage.

## Current implementation scope

Current work is strictly the database foundation:

- the homology query contract;
- canonical encodings;
- PostgreSQL assertion history and current read projections;
- a small adversarial corpus;
- provenance and snapshots;
- machine-readable APIs and exports;
- computation adapters only as data producers.

Specifically excluded for now:

- spectral-sequence page/differential schemas;
- Serre or Adams computation algorithms;
- an LLM agent or vector-search layer;
- constraint propagation or automated differential inference;
- a polished research notebook or operating-system UI.

These exclusions prevent the future vision from destabilizing the first useful artifact.

## Research questions to carry forward

### Serre

- Which fibration models and local coefficient systems can be exchanged reliably?
- What chain-level data must be retained to reproduce transgressions and multiplicative structure?
- How should naturality and comparison-map evidence be represented?
- How should partial pages, unresolved differentials, and extension ambiguity be published?

### Adams

- Which Adams variants and conventions share a core representation?
- How are chart classes identified across published computations and software packages?
- How should products, operations, hidden extensions, and convergence claims be distinguished?
- What is the boundary between raw algebraic computation, spectral-sequence inference, and stable-stem identification?

### LLM access

- Which structured query language is expressive enough for mathematical example retrieval?
- How are missing data and completeness boundaries exposed so absence is not misread as vanishing?
- What compact context bundles allow an LLM to reason without losing provenance or conventions?
- How will every answer expose the exact records and query that produced it?

## Guardrail

Every future feature must strengthen the shared data substrate rather than creating a new isolated chart, notebook, database dump, or convention silo.
