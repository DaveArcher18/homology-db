Type: research
Status: resolved
Claimed by: /root
Claimed at: 2026-07-11T10:49:51Z
Resolved at: 2026-07-11T11:00:13Z
Blocked by:

# Pin the v0.0.1 observable contract

## Question

Which exact query behaviours, minimum corpus scale and coverage, latency/batch/export bounds, provenance guarantees, and release evidence distinguish a useful Homology DB `0.0.1` from a toy while keeping UI and natural-language interpretation out of scope?

## Answer

The hard observable contract is recorded in [`docs/research/v0.0.1-observable-contract.md`](../../../docs/research/v0.0.1-observable-contract.md).

`0.0.1` must prove eleven release gates rather than merely ship code. The key floors are 100 reviewed conceptual spaces, 1,000 reconstructible models across supported simplicial and CW formats, meaningful cross-prime and higher-degree torsion coverage, twelve public query behaviours, a schema-valid evidence-bearing LLM envelope, append-only correction/snapshot semantics, owned high-level model-to-homology computation for every counted model, measured scale budgets on a deterministic synthetic tier, and a reproducible clean tagged release with manifest, changelog, and test log.

Unknown, absent, not-computed, bounded, and conflicting data never prove zero or a forbidden torsion condition. Synthetic scale data never count toward the mathematical corpus. PostgreSQL, Sage, Rust, and web frameworks remain implementation candidates rather than observable requirements.

The contract was derived from the active objective and repository source documents, reviewed independently for mathematical and systems risks, and its non-sensitive reference-host assumptions were verified locally.

## Comments

### 2026-07-11 scope amendment

By explicit project direction, the release contract now includes a twelfth gate: a bounded tool-constrained QA agent must answer the frozen 100-prompt common-manifold suite through the public API with 100/100 semantic correctness, zero unsupported claims, and assertion-level grounding in one snapshot. This appends to, rather than rewrites, the original eleven-gate answer. It removes only the blanket exclusion of every LLM agent; a general research/product agent, bespoke natural-language parser, embeddings, vector search, and opaque semantic retrieval remain outside `0.0.1`.
