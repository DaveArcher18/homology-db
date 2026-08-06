Type: task
Status: resolved
Claimed by:
Claimed at:
Blocked by:

# Publish the open review preview

Review the full stable-spectrum change, correct any release-facing findings,
and publish the exact imported-unreviewed candidate so informal reviewers can
inspect it and submit feedback. Preserve the separate Dan acceptance path.

## Answer

Published the exact imported-unreviewed cw49 feedback preview at
<https://davearcher18.github.io/homology-db/>. The live body is 5,071,504
bytes and byte-identical to the checked-in artifact at SHA-256
`5562e0cada18cf2fa1c0d0e7a1761272cf7ecdd3bb2c8176a417cc12abb61c29`.
GitHub Pages run `31126911171` completed successfully from `main` commit
`e4a1dfb`.

## Comments

- The user explicitly authorized a public feedback preview on 2026-08-06.
  This changes the publication policy, not the mathematical review state.
- PR <https://github.com/DaveArcher18/homology-db/pull/1> records the reviewed
  implementation. The preview gate reports 49 spectra, 48 finite modules, one
  profile, deterministic rebuild success, and no acceptance metadata.
- The first manual Pages run correctly failed because the shallow checkout
  could not prove the embedded source commit was an ancestor. The workflow now
  checks out full history; regression coverage asserts `fetch-depth: 0`.
- Live route checks confirmed the `Public feedback preview` and
  `Imported · awaiting review` labels, the `tmf` typed unsupported downloads,
  and the public feedback link. Dan's eventual acceptance remains a separate
  finalization event.
