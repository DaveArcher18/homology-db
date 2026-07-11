# Working agreements and decision state

## Method

Proceed gently: constrain the problem through representative examples until the necessary abstractions become clear.

The project should not mistake an attractive architecture diagram for a mathematical data model. Definitions, tables, interfaces, and platform choices remain hypotheses until they survive real objects, conflicting conventions, source data, and downstream queries.

Practical rules:

- accumulate a small but structurally diverse corpus before generalizing;
- prefer reversible experiments to framework commitments;
- require concrete counterexamples when splitting or merging concepts;
- derive indexes from observed query workloads;
- derive interchange records from actual cross-engine translations;
- keep source artifacts unchanged so normalization can be revisited;
- distinguish a direction, a working hypothesis, and a frozen decision in documentation;
- freeze a contract only when fixtures, queries, round trips, and attribution all agree;
- allow different capabilities to settle on different computational backends;
- do not let the distant research-harness vision force speculative tables into Homology DB.

## Current directions

These guide exploration but are not detailed commitments:

- build a unified, attributed mathematical data system;
- focus implementation on Homology DB now;
- design with Serre as the first future spectral-sequence consumer and Adams after it;
- make structured example retrieval a first-class downstream use;
- retain enough chain-level and provenance data for future computation;
- consolidate or reimplement capabilities behind a shared semantic boundary.
- reimplement the relevant high-level mathematical capabilities rather than making existing systems the permanent substrate.

## Accepted provisional policy

### Two-tier corpus

Use two distinguishable layers if the fixtures support them:

1. curated conceptual spaces, returned by default as named and citable examples;
2. raw computational models, searchable explicitly even when unnamed or unidentified.

A raw model is connected to a conceptual space through a sourced `model_of` assertion. Neither tier silently deduplicates the other.

This policy remains open to revision if family objects, equivalent presentations, or unidentified models reveal a better decomposition.

## Open working hypotheses

- Sage may be the first broad computation backend.
- Sage may be a bootstrap and reference backend rather than a lasting dependency.
- Canonical records should not be Sage runtime objects.
- PostgreSQL may hold assertion history and query projections.
- Engine-native artifacts may live in content-addressed storage.

None of these is frozen. The Sage comparison spike and real data fixtures will determine them. Licensing is intentionally not being decided now.

## First constellation of examples

Instead of designing the whole universe, model a small connected constellation:

- a point and the empty space, to expose conventions;
- `S¹`, `S²`, and `S³` as instances of a family;
- two distinct finite models of `S²`, to test the two tiers;
- `RP²`, to expose integral torsion and coefficient changes;
- the Hopf fibration `S¹ → S³ → S²`, to expose maps and the future Serre boundary;
- one deliberately unidentified finite complex;
- one conflicting or corrected result assertion.

For each example, record only what can be defended from a source or reproducible computation. Let the difficulty of expressing these records reveal the next distinction.

## Next freeze point

Do not freeze the physical schema yet. The next legitimate decision point comes after the constellation can be represented in a neutral interchange draft and used to answer the initial homology/example queries without hiding conventions or provenance.
