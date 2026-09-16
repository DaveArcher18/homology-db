# Pages computed-provenance repair — 2026-09-16

## Incident

Production release `1bc827d339996b82db3ed78ba6ca6856864a3fc8`
retained complete computed-ring provenance in `dist/atlas.html`, but the Pages
partition omitted the top-level `computed_rings` object. The sharded loader
therefore had no computed source catalogue or computed simplicial-model
descriptions. Bare `source_id`, role and locator values reached the renderer,
whose truthful last-resort label is `Untitled source`.

This was a production-bundle defect, not corruption of the canonical ring
records. The offline artifact remained complete.

## Reproduced scope

- 194 provenance-eligible spaces remain the complete shipped product.
- 187 spaces carry 1,309 imported ring records; the other seven retain their
  explicitly withheld ring state.
- All 187 imported-ring space pages were affected in the sharded build.
- The aggregate cohomology-source section rendered 690 `Untitled source`
  entries: 58 pages with three and 129 pages with four.
- Flat 3-manifold G2 lost the readable identities of `cohomology-tables`,
  OSCAR, the Manifold Page and *f-vectors of 3-manifolds*.
- The 11 checked-in computed simplicial-model descriptions were unavailable to
  the production renderer.
- No former legacy-only space was present; `cayley_plane:2` remained absent.

## Repair

Source commit: `a44a43f` (`Preserve computed provenance in Pages bundle`).

- `scripts/build_static_bundle.py` emits one shared
  `data/shared/computed-rings.json` document.
- `static_atlas/data-store.js` verifies and reloads that document as
  `atlas.computed_rings`.
- `tests/test_static_bundle.py` asserts exact shared-object preservation,
  resolution and readable metadata for every shipped cohomology source ID,
  Gabriel/OSCAR/external-source attribution, 11 computed models, and the
  194/187/7 product boundary without legacy-only spaces.
- `scripts/verify_pages_provenance_browser.cjs` exercises the generated
  sharded site through the production loader, including G2 citations, HTTPS
  links, a checked-in computed model, corpus boundaries and browser errors.

## Verification

- Focused bundle tests: 2 passed.
- Complete unittest partition: 238 tests assigned exactly once across eight
  module-preserving shards (30/30/30/30/30/30/29/29); all passed. Three
  existing optional external-consumer tests skipped with their documented
  environment requirements.
- Deterministic release gate passed with
  `deterministic_rebuild_verified=true`.
- Rebuilt `dist/atlas.html`: 20,154,412 bytes; SHA-256
  `6cd3763a6b882ce3e6b58e0d4495c33021835fecdf9761fab27b02715d600b17`.
- Exact Pages bundle: 249 documents, including one 101,928-byte
  `computed_rings` document; bundle ID
  `bundle-9e4a2610d4f51dbb9beabdb641141bd011efb770e2c8a0c323ead2e55fbab988`.
- Headless Chrome passed the provenance browser contract: G2 rendered all four
  named, linked sources; the 11-model catalogue reloaded and a computed model
  rendered; 194/187/7 remained exact; no legacy-only space appeared; no console
  or page errors occurred.

The older broad `verify_space_reading_browser.cjs` currently asserts seven
finite-field workbench cards on every formula-rendered page. It fails with five
on the same 13 pages in both pre-repair production and the repaired bundle, so
that pre-existing oracle mismatch is not attributed to this incident repair.

These checks are mechanical deployment-candidate evidence. Human product and
mathematical acceptance remain open.
