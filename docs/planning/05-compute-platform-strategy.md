# Compute-platform strategy

Status: exploratory. Reimplementation is the direction; language and low-level libraries remain open. Licensing is deferred.

## Working hypothesis

Explore **SageMath as a bootstrap and reference backend**, while building the canonical semantic model, database, interchange schemas, and eventual owned implementations independently of Sage objects.

The system boundary should be:

```text
canonical versioned input
        ↓
isolated compute adapter
        ↓
Sage / Rust / OSCAR / GAP / other engine
        ↓
canonical versioned output + run manifest
```

No compute engine writes database tables directly. No pickle, Sage object, GAP workspace, Julia serialization, or engine-specific save file is canonical data. Engine-native artifacts may be retained by hash for reproduction.

If the concrete examples support it, Sage can help us establish correct behavior and fixtures without becoming the permanent implementation substrate.

## Why Sage is the leading starting point

The current Sage distribution provides:

- [chain complexes, morphisms, homotopies, homology, and induced maps](https://doc.sagemath.org/html/en/reference/homology/index.html);
- [simplicial complexes, simplicial sets, cubical and filtered complexes](https://doc.sagemath.org/html/en/reference/topology/index.html);
- normalized chain complexes from [simplicial sets](https://doc.sagemath.org/html/en/reference/topology/sage/topology/simplicial_set.html);
- [sparse integer matrices and Smith normal form](https://doc.sagemath.org/html/en/reference/matrices/sage/matrix/matrix_integer_sparse.html);
- [the Steenrod algebra at all primes and multiple bases](https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/steenrod/steenrod_algebra.html);
- [finitely presented graded Steenrod modules](https://doc.sagemath.org/html/en/thematic_tutorials/steenrod_algebra_modules.html);
- the existing [Kenzo interface](https://doc.sagemath.org/html/en/reference/interfaces/sage/interfaces/kenzo.html).

Python is a productive orchestration language and makes database/API integration straightforward. Sage also already integrates optimized systems such as FLINT, GAP, and other specialist packages.

## Why Sage must not define the canonical model

### Serialization and identity

Runtime Sage parents, categories, bases, and wrapped Kenzo objects are useful computation structures but are not durable cross-language identifiers. Canonical records need explicit coefficient rings, gradings, ordered bases, sparse maps, conventions, and schema versions.

### Service isolation

The query/API service should remain small, deterministic, and independently deployable. Sage computation belongs in isolated workers or reproducible jobs, never inside latency-sensitive web requests.

### Performance uncertainty

Sage supplies sparse representations and optimized routines, but performance is operation- and coefficient-dependent. Its own sparse-matrix documentation notes that some generic operations convert to dense form. Large Ext and propagation workloads have already motivated specialist Rust and C++ systems. Benchmark the exact workloads rather than declaring Sage either fast enough or untenable in general.

### Licensing is deferred

The project is not selecting its licensing posture during data-model and algorithm exploration. Continue recording upstream licenses and attribution so later distribution decisions have accurate inputs, but do not use licensing to prematurely constrain the architecture.

## Alternatives

| Option | Strengths | Gaps for this project | Recommended role |
|---|---|---|---|
| SageMath/Python | Broadest relevant topology coverage; Steenrod algebra/modules; Kenzo; mature exact algebra | Heavy runtime, engine-specific object model, performance must be profiled | Bootstrap, reference, and differential-test backend |
| Rust native core | Control, performance, safe services, good fit with ext-rs/SpectralSequences work | Much of general topology and integral homological algebra would need implementation | Candidate for owned performance-critical kernels |
| Julia/OSCAR | Modern language; [chain complexes and module maps](https://docs.oscar-system.org/stable/CommutativeAlgebra/ModulesOverMultivariateRings/complexes/); [simplicial integral homology](https://docs.oscar-system.org/stable/Combinatorics/simplicialcomplexes/); strong computational algebra | Less ready-made algebraic-topology and Steenrod infrastructure for our path | Serious comparison backend and possible future kernel |
| GAP/HAP/homalg | Strong group homology, filtered complexes, LHS, categorical homological algebra | GAP-native runtime model and persistence; not a complete general Serre/Adams platform | Independent adapters and verification |
| Macaulay2 | Strong filtered complexes, modules, page maps, algebraic workflows | Not a general topology/fibration compiler; executable serialization is system-specific | Filtered-complex comparator |
| Pure Python without Sage | Simple deployment and familiar orchestration | Rebuilding exact algebra immediately; likely poor high-end performance without native kernels | API/schema tooling only, not primary mathematics kernel |

The mature architecture may still be hybrid, but the project should own its high-level mathematical capabilities. Sage and other systems can remain optional reference adapters; native kernels can be introduced where the emerging model and workloads make their interfaces obvious.

## Unified implementation policy

For every studied or reimplemented capability, record:

- capability and mathematical specification;
- originating papers and algorithms;
- upstream software/project and contributors;
- source and data licenses separately;
- how the new specification relates to upstream behavior and published algorithms;
- upstream version/commit and test-vector version;
- known convention differences;
- differential comparison results;
- performance and correctness limitations.

Attribution must be both human-readable and machine-queryable. A result generated by our implementation should still cite the algorithm, source dataset, and comparison corpus that support it.

Do not rewrite mature low-level arithmetic or systems infrastructure merely to claim unification. Reimplement the algebraic-topology capability when owning its semantics, state, correctness, interoperability, and evolution makes the overall system clearer.

## Sage tenability spike

Before committing the compute platform, implement the same canonical fixtures through Sage and at least one alternative backend.

### Workloads

1. Construct and round-trip finite simplicial and cellular chain complexes with ordered bases.
2. Compute integral homology and transformation data for sparse boundary matrices of increasing size.
3. Compute homology over several prime fields, including odd primes.
4. Transport maps through homology while retaining basis-coordinate maps.
5. Exercise Steenrod-algebra arithmetic and basis changes at primes 2 and 3.
6. Construct filtered complexes required by a future Serre adapter.
7. Start isolated workers repeatedly and measure cold start, memory, concurrency, and artifact size.
8. Reproduce selected published or hand-checked fixtures and compare exact canonical outputs.

### Compare

- correctness and convention clarity;
- exact output and transformation data available;
- runtime and peak memory by workload size;
- sparse-to-dense failure points;
- deterministic behavior and reproducibility;
- installation/container complexity;
- adapter code complexity;
- ability to cancel, resume, and capture logs;
- contributor accessibility and operational complexity.

### Exit decision

Choose one of:

- Sage remains a useful bootstrap/reference backend;
- an owned implementation is ready to replace Sage for the capability;
- another system supplies better differential tests or low-level kernels;
- the capability needs further specification before implementation.

The decision may differ by capability. A single canonical data model does not require a single numerical or algebraic backend.
