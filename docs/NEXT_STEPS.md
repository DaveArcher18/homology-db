# Next steps from the local Homology DB preview

Date: 2026-07-11

Status: Wayfinder execution handoff after the first usable local preview

## Where we are

The repository now has three distinct layers that should not be conflated:

1. the resolved mathematical and editorial contracts;
2. the exact `0.0.1` corpus selection plan—174 curated spaces and a target of
   1,159 qualified finite Models; and
3. a testable 60-common-manifold local preview over the four public QA tools.

The preview is valuable because it makes the human and agent interface
concrete. It does not make the planned corpus counts achieved release facts.

## Wayfinder route

Work should proceed in the issue tracker’s dependency order. Each linked issue
owns its decision; this document only shows the route and the observable exit
from each stage.

### 1. Finish [Prototype the owned cellular-homology boundary](../.scratch/homology-db-v0-0-1/issues/08-prototype-owned-homology.md)

Replace the preview's determinantal-minor Smith routine with a measured,
version-pinned implementation that handles general sparse chain complexes and
retains the basis transformations needed for representatives and induced maps.
Benchmark a clean SageMath 10.9 environment against direct FLINT/python-flint
and any other credible exact-integer adapter. The current machine's `sage`
launcher points to a missing SageMath 9.6 application; that installation fault
is evidence to repair, not an argument against Sage.

Exit: worked complexes with adjacent nonzero boundaries, torsion, explicit
cycles, a nonidentity induced map, deterministic reruns, and an independent
oracle all agree through the computation interface.

### 2. Resolve [Benchmark assertion-to-query architectures](../.scratch/homology-db-v0-0-1/issues/09-benchmark-query-architectures.md)

Materialize the Current projection and primary-summand indexes at realistic
scale. Compare SQLite and PostgreSQL from the actual torsion, partial-pattern,
batch, provenance-expansion, and export workload; PostgreSQL is a candidate,
not a foregone conclusion.

Exit: checked-in data generator, query corpus, query plans, cold/warm timings,
storage figures, and one justified physical design that meets the observable
latency targets.

### 3. Resolve [Prototype the LLM lookup evidence bundle](../.scratch/homology-db-v0-0-1/issues/10-prototype-llm-evidence-bundle.md)

Turn the preview envelopes into a compact, versioned tool contract with exact
claim-to-assertion grounding, completeness warnings, conflict and unresolved
states, pagination, and evidence expansion. Keep model-native tool selection
outside the structured query semantics.

Exit: an agent can answer a representative mixed set without SQL, filesystem,
network, embeddings, or a custom natural-language parser, and every stated
group is mechanically grounded.

### 4. Resolve [Specify ingestion, snapshot, and release boundary](../.scratch/homology-db-v0-0-1/issues/11-specify-release-boundary.md)

Implement the idempotent route from pinned Source artifacts through neutral
Models, owned computation runs, immutable assertions and events, Current
projection, Snapshot, export, changelog, and test log. Materialize and qualify
the curated slice before attempting the entire Stellar reserve.

Exit: a clean checkout rebuilds byte-identical release artifacts from pinned
inputs and retains every rejection, correction, and conflict without mutation.

### 5. Resolve [Prove common-manifold QA through the public tools](../.scratch/homology-db-v0-0-1/issues/12-prove-common-manifold-qa.md)

Run the frozen 100-prompt suite with a fresh tool-constrained agent against one
release Snapshot, retain the transcript and tool calls, then replay the
grounding evaluator deterministically.

Exit: 100/100 semantic correctness, zero unsupported mathematical claims, and
every group claim tied to a selected assertion in the one Snapshot.

## UX requirements carried through every stage

- One obvious first command from a clean checkout.
- Human-readable summaries and stable machine JSON come from the same module.
- Mathematical zero, absence, unsupported input, unknown, not-computed,
  conflict, and unresolved selection remain visibly different.
- Subject resolution explains ambiguity and offers bounded suggestions.
- Query results explain why they match and expose assertion/evidence IDs
  without forcing the caller to understand storage.
- Expensive provenance is expandable, not dumped into every response.
- Errors state what the caller can do next.
- A Codex user can control and inspect all progress from this chat and the
  repository; no hidden standalone worker is required.

## Deferred after `0.0.1`

The general research agent, vector or embedding retrieval, Web UI, CW
rendering, official LMFDB integration, Serre and Adams schemas, known spectral
sequence querying, and forced spectral-sequence computation remain later maps.
The current data model must leave seams for them without pretending to have
implemented them.
