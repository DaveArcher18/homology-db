# Gabriel computed-rings staging audit — 2026-09-11

## Decision

The computed-ring corpus is staged for maintainer QA on
`staging/gabriel-computed-rings`. It has not been merged into `main`, pushed,
or published. The contributor branch was not merged wholesale because it also
replays obsolete application and deployment history; only the corpus-related
commits were replayed onto current `origin/main`.

## Exact inputs

- Contributor repository: `wgabrielong/homology-db`
- Contributor branch: `cohomology-tables-families`
- Audited contributor commit: `1262076fcf32545f33196939f2ca63d0bce00ed5`
- Upstream computation identified by the corpus manifest:
  `wgabrielong/cohomology-tables@5ae5870b3aa67d89f29d14f850e38186dd231898`
- Recorded engine: OSCAR 1.8.2 on Julia 1.12.7
- Data license: CC0-1.0; software license: GPL-3.0-or-later

## Staged scope

- 1,116 cohomology records for 186 spaces.
- Six records per represented space: Z, Q, F2, F3, F5, and F7.
- Every imported record remains labelled `imported_unreviewed`.
- The combined staged atlas contains 212 conceptual spaces, 12,668 homology
  rows, 640 citations, 66 computations, 212 evidence records, and 100
  relations.
- Eleven redistributable triangulations are checked in. Other models are
  pinned by identifiers and hashes rather than silently copied.
- Seven spaces retain explicit withheld/incomplete ring output where the
  producer's basis or schema limits prevent a faithful record. Missing output
  is not presented as a zero ring.

## Integration repairs

- Reinstated the complex-projective family handler and the CP3 teaching entry.
- Kept the public site sharded; the catalogue is about 716 KiB rather than
  embedding full evidence and models in the shell.
- Raised only the optional single-file offline snapshot limit to 24 MiB. This
  does not reinstate the rejected monolithic public-page approach.
- Made navigation QA wait for asynchronous workbench rendering.
- Added safe presentation support for `\\cdots`, `\\mathbin`, and escaped
  connected-sum notation.
- Allowed an untouched production artifact to remain deliberately stale on a
  feature branch while requiring the release gate to reject it.

## Verification evidence

- Focused mathematical and integration suite: 39 tests passed.
- Full Python suite: 229 tests run; 228 passed, 3 skipped, and one stale
  test-fixture failure was repaired. The repaired boundary test then passed.
- Responsive navigation QA passed at 320, 390, 640, 641, 700, 768, 900, 960,
  961, 1024, and 1440 px.
- Textbook and review-flow QA passed for all 212 teaching entries.
- Exhaustive browser reading QA passed for 212 spaces, 1,177 coefficient views,
  12 disclosures, four responsive widths, history/reload, keyboard scrolling,
  source focus, and dark mode, with no browser errors.
- A deterministic space-only export produced 217 documents. The release-gated
  review-candidate build preserved the 49 secondary spectra and produced 266
  documents in total: 212 spaces, 49 spectra, and shared/catalogue documents.

## Remaining gate

The records are suitable for product QA, not mathematical acceptance. Cup
products were imported from the pinned computation and were not independently
recomputed by this repository. Human review remains pending and must stay
visibly independent of automated checks. Before release, rebuild from the
final clean commit, run the entire suite once more, inspect the generated
artifact, and explicitly decide whether to publish this corpus.
