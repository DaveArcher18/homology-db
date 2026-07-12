Type: prototype
Status: open
Claimed by:
Claimed at:
Blocked by: 01

# Decide finite-simplicial-set admission

## Question

Does a canonical finite-simplicial-set encoding with checked simplicial
identities, normalized chains, maps and basepoints, deterministic hashes, and
fixed size budgets preserve reconstructibility strongly enough to extend the
accepted Model boundary for compact `RP^n`, `CP^0..4`, and construction Models?

## Acceptance criteria

- The prototype enforces dimension at most 12 and at most 50,000
  nondegenerate simplices or cells per constructed Model.
- The ADR accepts or rejects finite simplicial sets only after measuring
  canonical serialization, simplicial-identity validation, normalized chains,
  maps and basepoints, deterministic hashes, and source-version pinning.
