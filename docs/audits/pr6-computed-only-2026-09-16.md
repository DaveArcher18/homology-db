# PR #6 computed-only product verification — 2026-09-16

Product authority supersedes the earlier combined-corpus retention decision.
The shipped ordinary-space atlas contains only spaces selected by
`has_gabriel_imported_computational_model_provenance`; the broader disposable
source ledger is not a product-retention mechanism.

## Candidate

- Verified artifact commit: `1a4ac83d3bbfc91dbcda619f84da83045cc9f17b`
- `dist/atlas.html`: 20,154,207 bytes
- SHA-256: `2b691d2f9fdc22968a19b43854937d10a2fc711ab9a5b7e0f423eb0cd7c9c8bb`

## Corpus invariants

- 194 shipped spaces; every one satisfies the provenance rule.
- 187 spaces carry 1,309 imported ring records.
- Seven provenance-eligible spaces retain computed homology with imported ring
  output withheld: `connected_sum:s2-twist-s1-sum-20`,
  `connected_sum:s2xs1-sum-20`, `hadamard_torsion_complex:32`,
  `hom_complex:c6-compl-k5-small`, `orientable_surface:26`,
  `random_2_complex:25`, and `sphere:0`.
- `M(Z/11,2)` and F11 remain present.
- Former legacy-only identifier `cayley_plane:2` is absent from the embedded
  corpus, catalogue, and static bundle documents.
- The 49-spectrum secondary corpus is unchanged.

## Automated verification

- `python3 scripts/run_unittest_shard.py --shard-count 8 --verify-partition`:
  238 discovered tests assigned exactly once as 30/30/30/30/30/30/29/29.
- All eight shards passed; the complete union is 238 tests. Three optional
  pinned external-consumer tests were discovered, executed, and reported as
  their existing environment-dependent skips.
- `python3 scripts/verify_steenrod_release.py --atlas dist/atlas.html
  --allow-public-review-preview --verify-rebuild`: passed with
  `deterministic_rebuild_verified=true` and canonical SHA-256 above.

## Exact-artifact browser smoke

Headless Google Chrome through Playwright exercised the checked artifact at
1440 px and 390 px. It verified the 194-space catalogue; `M(Z/11,2)` with F11;
the short integral torus presentation; the long K3 fallback presentation;
truthful withheld-ring messaging for `orientable_surface:26`; absence of
`cayley_plane:2`; no horizontal overflow on the exercised pages; and no console
or page runtime errors.

This is bounded smoke evidence, not human mathematical acceptance. Gabriel's
explicit faithful-representation and publication confirmation remains open.
