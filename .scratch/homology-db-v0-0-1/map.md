Type: wayfinder:map
Status: active

# Homology DB v0.0.1

## Destination

Deliver and verify a versioned `0.0.1` Homology DB that contains many reconstructible finite CW/simplicial models, answers exact and partial torsion-pattern example queries efficiently, and returns structured provenance-bearing results suitable for an LLM tool to consume.

## Notes

- This map explicitly carries execution through the verified release; it does not stop at a specification.
- Read `AGENTS.md`, `CONTEXT.md`, `WORKSTATE.md`, and `docs/agents/resume-protocol.md` at each session start.
- Use `research`, `prototype`, `grilling`, `domain-modeling`, `codebase-design`, `tdd`, and `code-review` as ticket type and phase require.
- Keep an append-only assertion history, explicit knowledge states, immutable source artifacts, and deterministic snapshots.
- Prefer owned high-level mathematical capabilities; existing systems are attributed references and differential-test oracles.
- Make reversible choices from fixtures and measured workloads rather than freezing the architecture early.
- Maintain scoped commits, `CHANGELOG.md`, and a dated `TESTLOG.md` referenced by the changelog.
- UI and CW-complex rendering are explicitly deferred from this destination.

## Decisions so far

<!-- One context pointer per resolved ticket. The answer lives in the ticket. -->

- [Pin the v0.0.1 observable contract](issues/01-pin-observable-contract.md) — Release requires eleven evidence-backed gates, including 100 curated spaces, 1,000 reconstructible models, torsion-pattern semantics, owned computation, measured queries, and a reproducible tagged snapshot.
- [Prototype the smallest honest constellation](issues/02-prototype-honest-constellation.md) — The executable fixture forces layered space/model/artifact identity, fully qualified homology slots, explicit correction and conflict records, three-valued query evidence, and an identity-only map plus atomic fibration-context seam.
- [Survey scalable finite-model corpora](issues/03-survey-finite-model-corpora.md) — Pin Stellar v6 for bulk triangulations, treat polyDB as an overlapping structured view, use simpcomp/Sage/HAP for named generators and validation, and leave the regular-CW counting boundary explicit for ticket 04.
- [Set the first-release model boundary](issues/04-set-model-boundary.md) — Count only finite abstract-simplicial and witness-certified regular-CW Models, reconstruct CW topology through the Cell-closure-poset order complex, require a paired nonsimplicial slice, and keep unsupported attaching-map and generalized formats as attributed Source artifacts.
- [Define structured homology-pattern semantics](issues/05-define-pattern-semantics.md) — Evaluate one-tier conjunctive patterns with evidence trits, keep explicit unknown distinct from unresolved data, return unresolved candidates separately, and require structured slot-level explanations and completeness evidence.

## Not yet specified

- Implementation tickets and package boundaries after the contracts and corpus are visible.
- Exact runtime language and native-kernel boundaries after the reference slice is measured.
- Canonicalization and duplicate-detection algorithms after real cross-source duplicates are observed.
- Bulk export encoding and snapshot-diff representation after the query and persistence prototypes.
- Deployment, object storage, backups, and operational scale after a local release works.
- Corpus refresh and upstream-change reconciliation after the first immutable corpus manifest.

## Out of scope

- Web UI and CW-complex rendering.
- Natural-language parsing, embeddings, vector search, or an LLM agent.
- Serre or Adams schemas, computation engines, querying, or forcing.
- Cohomology rings, generalized theories, and homotopy groups.
- User submissions and untrusted computation.
- Licensing posture.
- Official LMFDB integration.
