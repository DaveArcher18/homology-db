Type: task
Status: resolved
Claimed by: /root/steenrod_atlas
Claimed at: 2026-08-05T15:58:08Z
Blocked by: 01

# Normalize cw49 and implement exporters

Build the canonical corpus, validators, deterministic exports, manifests, and
public CLI for the complete cw49 set.

## Answer

The pinned cw49 corpus now contains exactly 49 Conceptual spectra: 48 complete
finite-basis modules and the `tmf` Steenrod profile. The canonical
`homology-db.steenrod-module/1` records preserve stable basis order, exact
sparse `Sq^(2^k)` images, explicit zeroes, source evidence, review state, and
content hashes. Validators enforce grading, unique terms, completeness, Adem
relations, and unstable-only instability.

Deterministic Python and CLI adapters emit pinned sseq JSON, SSeqCpp
`Adams.json` fragments, and full nonzero Bruner closure. All adapters reject
incomplete finite modules; Bruner returns typed `infinite_profile` unsupported
for `tmf`. The corpus has 942 basis elements and 5,780 generator-action slots,
of which 2,503 are nonzero and 3,277 are exact zeroes. Fixture exports passed
the pinned real Bruner 1.9.5, sseq, and SSeqCpp consumers.

## Comments

- Resolved by `/root/steenrod_atlas` on 2026-08-05 after the complete corpus,
  deterministic round trips, and all three real-consumer checks passed.
