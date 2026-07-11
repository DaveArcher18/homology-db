Type: task
Status: open
Claimed by:
Claimed at:
Blocked by: 07, 08, 09, 10, 11

# Prove common-manifold QA through the public tools

## Question

Can a bounded tool-constrained agent answer the frozen 100-prompt suite about the homology of 60 common manifolds with 100/100 semantic correctness, zero unsupported claims, and every group claim grounded in selected assertion IDs from one immutable release snapshot?

## Fixed acceptance boundary

The release pins one `common-manifold-qa-v1` cohort from the corpus manifest. Its 60 distinct subjects are exactly:

- spheres of dimensions 1 through 8 (8);
- orientable surfaces of genera 2 through 9 (8);
- nonorientable surfaces of genera 2 through 9 (8);
- tori of dimensions 2 through 5 (4);
- real projective spaces of dimensions 2, 4, 5, and 6 (4);
- the first 12 lens-space pairs in manifest order (12);
- the first 8 sphere-product pairs in manifest order (8);
- disks of dimensions 1 through 4 (4); and
- orientable-surface-circle products of genera 2 through 5 (4).

The checked-in prompt manifest contains exactly 100 independently evaluated cases:

| Category | Cases | Required coverage |
|---|---:|---|
| Integral lookup | 60 | One basic unreduced integral-homology question for every cohort subject. |
| Coefficient or reduced | 8 | Explicit finite-field or reduced-homology questions, including degree-zero convention checks. |
| Structured example query | 12 | Exact-group, Betti-rank, prime-primary, primary-summand, partial-pattern, and exact-signature retrieval. |
| Comparison or provenance | 8 | Comparisons grounded in returned groups and evidence expansions, including source/computation history. |
| Safety | 12 | Two cases each for ambiguous/not-found identity, explicit unknown/not-computed, absent data, conflict/correction, unresolved forbidden constraints, and bounded/not-applicable data. |

No prompt or subject may be silently replaced after the release-candidate run begins. Prompt text, expected semantic facts, cohort IDs, category membership, and ordering are content-addressed release inputs.

## Agent capability boundary

The agent receives only its pinned system instructions, one case's prompt, the four tool schemas below, and tool responses from the selected snapshot:

- `resolve_subject` resolves public IDs or aliases and exposes ambiguity or not-found outcomes;
- `read_homology` reads selected evidence-bearing homology slots for one resolved subject;
- `query_examples` submits the versioned structured pattern language and returns proven matches separately from unresolved candidates; and
- `expand_evidence` dereferences returned assertion and evidence IDs within the same snapshot.

The agent has no SQL or database connection, filesystem access, network or browsing access, release exports, answer key, gold labels, embeddings, vector index, semantic search, or custom prompt parser. Model-native tool selection is the only permitted natural-language interpretation. Every tool call is bound to the run's one immutable `snapshot_id`; cross-snapshot data is rejected.

The final response uses a versioned structured answer envelope containing human-readable text plus an exhaustive claim list. Every mathematical group claim names its subject, fully qualified Homology slot, canonical group value, selected assertion ID, and snapshot ID.

## Pass condition

The gate passes only when one declared, noninteractive run policy satisfies all of the following:

1. all 100/100 prompt cases pass every expected semantic fact; partial credit does not pass;
2. every stated homology group is exactly supported by a selected Current assertion ID from the run's single snapshot;
3. the complete transcript contains zero unsupported mathematical claims, where an unsupported claim is any factual mathematical statement not entailed by cited snapshot-bound tool records or by a versioned deterministic presentation rule over their returned values; group claims still require selected Current assertion IDs;
4. ambiguous, absent, unknown, not-computed, bounded, not-applicable, conflicting, and unresolved outcomes remain explicit and are never converted to zero, exactness, or a proven forbidden condition;
5. there is no per-case human intervention, selective retry, hidden retrieval channel, or access to the expected answers; and
6. the release retains the model/runtime identifier and settings, system-prompt hash, tool-schema hashes, prompt-manifest hash, ordered tool traces, final answers, evaluator version/report, and claim-to-assertion grounding audit.

A clean checkout need not recontact an external model provider to reproduce stochastic text. It MUST verify every retained artifact hash and deterministically replay the evaluator over the frozen transcript; the live release-candidate run itself remains mandatory evidence for this gate.
