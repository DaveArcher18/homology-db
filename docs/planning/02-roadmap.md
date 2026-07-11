# Roadmap

The roadmap is organized around decision gates and testable artifacts. Do not begin with a polished frontend or a bulk import.

## Gate 0: agree on the charter

Deliverables:

- answer the six decisions in the [project brief](00-project-brief.md);
- name one mathematical editor and one technical owner;
- select 30–50 pilot spaces and at least two independent computational backends for a validation subset;
- decide whether the public object is a conceptual space, a presentation, or both (this plan recommends both, with conceptual spaces primary);
- write a one-page result authority and correction policy;
- decide whether eventual LMFDB integration is a goal.

Exit test: the same example—such as two triangulations of the real projective plane—can be entered without anyone disagreeing about which records represent the space, the models, the equivalence assertion, and the computation.

## Phase 1: executable data contract

Deliverables:

- JSON Schemas for spaces, models, relationships, homology results, references, and computation runs;
- a version-controlled downstream query workload with expected result shapes;
- canonical encoding for finitely generated abelian groups;
- label/redirect rules;
- five hand-curated examples with valid and deliberately invalid fixtures;
- schema validators and round-trip tests;
- a policy for unknown, conflicting, corrected, and superseded data.
- a PostgreSQL schema spike with a rebuildable current-homology projection;
- synthetic scale fixtures, representative indexes, query plans, and baseline timings.

Exit test: every fixture validates deterministically, invalid mathematical states are rejected, rendered values round-trip to the canonical representation, and the priority query workload meets its documented baseline without parsing display strings or invariant JSON.

## Phase 2: provenance-first ingestion

Deliverables:

- one Sage adapter and one independent HAP or simpcomp adapter;
- content hashing and immutable source artifacts;
- repeatable import commands;
- run manifests containing software versions and parameters;
- comparison reports for the validation subset;
- licensing and attribution records for every imported corpus.

Exit test: a clean environment can regenerate the selected results, and any disagreement becomes a retained conflict record rather than an overwritten value.

## Phase 3: thin public vertical slice

Deliverables:

- productionized PostgreSQL migrations based on the Phase 1 spike;
- server-rendered browse/search page;
- permanent space and model pages;
- source/completeness/reliability/labels panels;
- related-object links;
- per-object JSON and model downloads;
- `/api/v1` read endpoints with pagination and field selection;
- a random-object entry point for exploration.

Exit test: five representative user questions can be answered from the UI and API without direct SQL.

Suggested questions:

1. Find connected spaces in the pilot with 2-torsion in second homology.
2. Show all models known for a chosen space.
3. Reproduce the homology result for a selected model.
4. Distinguish an unknown result from a result computed to be trivial.
5. Follow a construction relationship from a product or suspension to its inputs.

## Phase 4: editorial workflow and release

Deliverables:

- draft/review/publish permissions;
- append-only review and correction history;
- contributor credit and citation export;
- knowledge-entry editing and review;
- full data export with a versioned snapshot identifier;
- backup/restore drill;
- accessibility, performance, and security checks;
- public statement of scope and completeness.

Exit test: an editor can correct a result without destroying the old assertion, publish a new snapshot, and produce a citation for both the page and the data release.

## Technical baseline

Use this only after Gate 0:

- Python for importers and compute integration because Sage is Python-based;
- PostgreSQL for metadata, assertions, normalized search projections, and review state;
- content-addressed object storage for models and run artifacts;
- a simple server-rendered web application with progressive enhancement;
- a versioned JSON API generated from the same service layer as the UI;
- isolated workers or containers for computation—never computation inside web requests;
- deterministic fixtures and property-based validation for group encodings and state transitions.

Framework selection is deliberately deferred. A short prototype should compare a modern Python framework with extending LMFDB's Flask/Jinja conventions. Data contracts and editorial rules should survive either choice.

## Risks to settle early

| Risk | Early control |
|---|---|
| One space has many presentations and names | Separate conceptual objects, models, and aliases |
| Equality/equivalence is uncomputable in general | Store typed, sourced assertions; never infer universal deduplication |
| Computed values silently become "facts" | Explicit promotion and review policy |
| Different packages use different conventions | Store convention parameters and knowledge entries with each invariant |
| Bulk imports carry incompatible licenses | Complete a source-by-source rights review before ingestion |
| Schema becomes a JSON dumping ground | Normalize common search projections and version invariant payload schemas |
| Project expands into all of topology | Require a new object-family proposal and editor for every expansion |
| A beautiful UI hides weak data | Make provenance, completeness, reliability, and unknown states visible |

## Later expansions

Add only after the first release is maintained successfully:

- cohomology rings, cup products, and operations;
- maps and induced maps on homology;
- fundamental groups and presentations;
- persistent homology modules;
- spectra and generalized cohomology theories;
- stable and unstable homotopy groups;
- spectral-sequence pages and extension problems;
- proof-assistant certificates;
- user-submitted computation jobs.

Each should reuse the assertion, provenance, relationship, review, and snapshot machinery rather than becoming a special-purpose table.
