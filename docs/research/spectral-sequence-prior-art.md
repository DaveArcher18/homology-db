# Spectral-sequence prior art

Research date: 2026-07-11.

Scope: computational Serre/Leray–Serre and Adams systems, reusable datasets, general spectral-sequence packages, visualization/interchange attempts, and the implications for a shared database. This review prioritizes project documentation, source repositories, datasets, and papers produced by the projects themselves.

## Executive conclusion

There are several powerful computation systems and substantial published datasets, but no stable shared semantic interchange across them.

- **Kenzo** is the strongest general computational Serre lineage surveyed.
- **SSeqCpp** is the strongest database-oriented Adams predecessor surveyed.
- **htpy** is a live 2026 experiment closest to the long-term integrated computation/deduction vision.
- **SeqSee** is the clearest cross-project visualization interchange, but intentionally does not preserve full mathematical semantics.
- Bruner, ext-rs, SSeqCpp, Isaksen–Wang–Xu, and related releases preserve valuable computation-grade data in mutually different bases and formats.

The project must not create another calculator-specific format. Its durable boundary should be:

```text
engine-native source artifacts
        ↓ versioned adapters
canonical semantic assertions
        ↓ deterministic projection
query-optimized PostgreSQL
        ↓
APIs / LLM tools / visualizers / computation engines
```

## Serre and general filtered-complex systems

### Kenzo and effective homology

The [Kenzo spectral-sequence extension](https://arxiv.org/abs/cs/0602064) computes Serre and Eilenberg–Moore page groups and differential maps for arbitrary pages, detects convergence, and determines the resulting filtration on target homology. Its Serre construction uses a simplicial group fiber, a 1-reduced simplicial base, and twisting data; effective-homology equivalences replace potentially infinite chain complexes with finite effective ones.

The current [Sage/Kenzo interface](https://doc.sagemath.org/html/en/reference/interfaces/sage/interfaces/kenzo.html) exposes page terms, tables, differential morphisms, and differential matrices. It wraps live ECL/Lisp objects rather than defining a neutral persisted representation. Sage warns that its Serre interface assumes simple connectivity and may give incorrect results outside that assumption. The optional [Sage Kenzo package](https://doc.sagemath.org/html/en/reference/spkg/kenzo.html) and the portable [Kenzo repository](https://github.com/gheber/kenzo) are GPL-licensed.

Database lesson: use Sage/Kenzo as a future adapter, not as the canonical schema. A matrix is portable only when its source, target, coefficient ring, page convention, and ordered bases are identified.

### Higher Serre spectral systems

The [Kenzo spectral-systems work](https://arxiv.org/abs/1912.04848) generalizes effective computation to towers of fibrations and produces groups and differentials for higher-dimensional indexing systems. The related [external modules](https://github.com/ana-romero/Kenzo-external-modules) had no visible repository license or published release at review time.

Database lesson: a future indexing model should be versioned and extensible rather than assuming every sequence is indexed only by two integers. No external-module code or data should be reused before its license is clarified.

### Macaulay2 `SpectralSequences`

[Macaulay2 SpectralSequences](https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/SpectralSequences/html/index.html), version 2.02 dated 2026-03-09, represents filtered complexes, page modules, page maps, bases, edge maps, page-to-page homology identifications, and associated/filtered homology. Its [Hopf-fibration example](https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/SpectralSequences/html/___Computing_spthe_sp__Serre_sp__Spectral_sp__Sequence_spassociated_spto_spa_sp__Hopf_sp__Fibration.html) manually constructs a simplicial model and inverse-image filtration before invoking the general engine.

It is therefore a strong filtered-complex comparator, not a general fibration-to-Serre compiler. Generic [Macaulay2 serialization](https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/Serialization/html/_serialize.html) recreates executable system objects and is unsuitable as canonical interchange. Macaulay2 is GPL-licensed.

Database lesson: preserve the conceptual separation between filtered input complex, page, page map, basis, edge map, convergence, and target filtration.

### GAP HAP

[HAP](https://github.com/gap-packages/hap) 1.76 was released on 2026-07-08 and declares GPL-2.0-or-later in its package metadata. It supports filtered chain complexes and includes a specialized [Lyndon–Hochschild–Serre computation](https://gap-packages.github.io/hap/doc/chap2_mj.html) for finite 2-groups and normal subgroups. Its filtered complexes rely on compatible preferred bases. Documented HAP persistence does not provide a neutral spectral-sequence interchange.

Database lesson: HAP is a future independent group-cohomology adapter, but LHS group spectral sequences must be identified separately from topological Leray–Serre sequences.

### GAP `homalg`

The [homalg project](https://homalg-project.github.io/homalg_project/homalg/doc/chap0.html) provides a general categorical model for exact couples, filtered complexes, bicomplexes, pages, embeddings into total objects, and stability. Its emphasis is computable homological algebra rather than constructing a Serre sequence from a topological fibration.

Database lesson: spectral sequence and construction mechanism are separate entities. A durable database should use simpler immutable records rather than reproduce a computation system’s runtime category hierarchy.

## Adams and stable-homotopy systems

### Bruner–Rognes Ext data

The [Bruner–Rognes dataset and paper](https://arxiv.org/abs/2109.13117) provide a minimal resolution of the mod-2 Steenrod algebra in a substantial range, together with chain maps representing every cocycle and `Sq^0`. The data is CC-BY-4.0 and organized for Bruner’s `ext` workflow.

Database lesson: computation-grade chain data and maps are more valuable than chart dots alone, but engine directory layout is not interchange.

### ext-rs / Spectral Sequences Project

The [ext-rs code in the Spectral Sequences Project](https://github.com/SpectralSequences/sseq/tree/master/ext) computes Ext over finite fields and supports odd primes, secondary-Steenrod differentials, Massey products, and unstable calculations. The monorepo is MIT/Apache-2.0 licensed and documents native module/save formats.

Database lesson: retain engine-native saves as immutable artifacts and extract versioned semantic assertions through adapters.

### SSeqCpp

[SSeqCpp](https://github.com/WayneLin92/SSeqCpp) uses SQLite for resolutions, products, spectral-sequence pages, maps, cofiber sequences, differentials, extensions, and proof logs; JSON describes categories of spectra and maps. It is designed for resumable computation and propagation across maps and cofiber sequences. The code is Apache-2.0.

The related [Kervaire computation dataset](https://zenodo.org/records/14475507) publishes SQLite/CSV data and large explicit derivation logs for spectra, maps, differentials, and extensions. This is the closest surveyed predecessor to a database plus computation-forcing substrate.

Database lesson: proof dependencies, maps, cofiber sequences, propagation steps, and contradictions are data. The canonical layer should preserve them as assertions and evidence without adopting SSeqCpp’s SQLite schema wholesale.

### Published Adams datasets

- [Steenrod-algebra cohomology through total degree 261](https://zenodo.org/records/7786290) is available as SQLite, CSV, PDF, and an interactive chart under CC-BY-4.0.
- [Secondary-Steenrod data](https://zenodo.org/records/5898461) includes differentials, products, Massey products, minimal-resolution data, and a basis-change file to Bruner’s basis under CC-BY-4.0.
- [Classical and motivic chart data](https://zenodo.org/records/6987157) and [algebraic-Novikov/`Cτ` data](https://zenodo.org/records/6987227) include per-page CSV data, differentials, and extensions under CC-BY-4.0.
- The [stable-stems computation](https://arxiv.org/abs/2001.04511) retains explicitly enumerated uncertainties rather than presenting every blank region as known vanishing.

Database lesson: a class label is not a cross-dataset identity. Store basis versions and basis-change linear maps. Record bounded completeness regions and uncertainty explicitly.

### Automated differential propagation

The [automated Adams `d_2` work](https://arxiv.org/abs/2210.15169) propagated more than 95% of differentials in its range from two seed differentials and multiplicative structure and detected an error in an earlier computation. It did not impose every possible constraint—such as `d² = 0`—when doing so caused prohibitive non-affine search growth.

Database lesson: a forcing engine needs an explicit dependency graph and named inference rules. “Machine-derived” does not mean exhaustive or formally verified.

### htpy

[htpy](https://htpy.app/about/) is a live experimental system that combines Ext and Gröbner-based spectral-sequence machinery with an archive/playground, differential propagation, contradiction testing, motivic and algebraic-Novikov computations, and cross-validation. Its [archive](https://htpy.app/archive/results) exposes multiple Adams-related theories, primes, and finite-complex computations.

This project is unusually close to the long-term research-harness vision and should be studied before designing any Adams module. Its documentation describes it as open source, but an exact code/data license was not verified during this review.

Database lesson: collaborate or interoperate rather than duplicate. First determine its canonical identifiers, schemas, persistence boundary, inference log model, API/export, governance, and licensing.

## Interchange, visualization, and formalization

### SeqSee

[SeqSee](https://arxiv.org/abs/2501.18429) and its [MIT-licensed repository](https://github.com/JoeyBF/SeqSee) define JSON headers, nodes, edges, styles, and pages for spectral-sequence visualization. The project explicitly notes that ext-rs, Bruner, and SSeqCpp use fundamentally different formats. SeqSee deliberately stores enough semantics for visualization rather than computation, so each source still needs a converter.

Database lesson: visualization is a projection, not canonical truth. Chart nodes and arrows cannot replace graded modules, bases, linear maps, assertions, and evidence.

### General software and formal libraries

The active Rust [SpectralSequences/sseq](https://github.com/SpectralSequences/sseq) monorepo includes finite-field Adams computation and a history/action model for assertions, products, differentials, permanent cycles, and propagation. Lean’s [mathlib](https://github.com/leanprover-community/mathlib4) supplies proof-level categorical spectral-sequence constructions, but it is not a computation database or interchange format.

Database lesson: semantic data, engine artifacts, visualization state, and formal proof objects are distinct layers. A future formal certificate may support an assertion without replacing its query representation.

## Shared data-model lessons

Any future spectral-sequence module will need:

- construction type and variant;
- homological/cohomological variance;
- coefficient ring, local/coefficient system, and actions;
- grading coordinates, page-origin convention, axes, and differential bidegree;
- convergence target, filtration, and bounded validity/completeness region;
- page terms as graded modules with explicit basis versions;
- sparse linear combinations over declared coefficient rings;
- differentials as linear maps between identified source and target terms;
- products, operations, extensions, maps, comparison maps, and cofiber/fibration structure;
- basis-change maps between datasets;
- assertion status, evidence, dependencies, citations, computation runs, and supersession;
- unresolved differentials and extension problems as positive records, not blank cells;
- content-addressed large matrices, resolutions, logs, and certificates outside ordinary SQL rows.

The forcing-engine requirement adds one non-negotiable rule: every derived claim must record the input assertions and inference rule that produced it. Proof logs produced by current software are valuable derivations, but should not be called formal certificates unless checked in an identified proof system.

## Implications for Homology DB now

Build only the shared foundations:

- durable IDs for spaces, models, future spectra, maps, coefficient systems, and conventions;
- versioned model and chain-complex artifacts with ordered bases;
- append-only assertions, corrections, conflicts, and scoped completeness claims;
- computation runs, source artifacts, licenses, citations, and content hashes;
- deterministic snapshots, bulk exports, and versioned interchange;
- query projections that never treat absent data as mathematical zero.

Do not yet add speculative Serre or Adams tables. Before the Serre module begins, define a neutral fibration/map representation, local coefficient/action model, filtered chain artifact, and Kenzo adapter contract. Before the Adams module begins, conduct a dedicated interoperability review with htpy, SSeqCpp, ext-rs, SeqSee, and the published CC-BY datasets.
