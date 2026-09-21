# Canonical Space Page review slice

Base: `origin/main` at `698cd8720d3b4d46334dedb7efbbd241dfad5a51`.
This is a local review candidate, not a deployment or human acceptance.

## Renderer diagnosis

The public atlas is a self-contained export. `scripts/export_static_atlas.py`
projects database homology, model, evidence and citation records, then joins
separately sourced and computed cohomology records into JSON. `atlas.js`
selects a route, then `buildSpaceView` constructs the space article in the
browser. Family rules have their own `#workbench` route; recorded members now
route to `#space=...` following PR #14. The public page has one builder for
recorded spaces, but several data-dependent structures: no cohomology ring,
literature and computation records, a large generators-and-relations display,
and family-specific explanatory text. The older builder also special-cases the
CP²/wedge comparison. Its side-by-side theory layout and open ring details
become substantially different reading experiences depending on record size.

This review slice uses the same `buildCanonicalSpaceView` for seven records:
the point, S⁰, RP⁴, torus, K3, connected sum of 19 copies of S²×S¹ (40 basis
elements), and genus-26 orientable surface (computed ring withheld). The other recorded
spaces retain the deployed page pending review. That temporary gate is the
only route to a different primary page structure in the candidate; it must be
removed as part of an approved corpus-wide rollout.

## Common page data contract

The page adapter `canonicalSpaceData(space, coefficient)` returns:

| Field | Meaning |
| --- | --- |
| `space` | Identity, notation, aliases, summary, family, properties and existing raw record. |
| `coefficient` | One explicitly selected coefficient ring. |
| `homology` | Ordinary unreduced rows for that coefficient, with exact/nonexact group state and row provenance unchanged. |
| `cohomology` | One selected record for the coefficient. Literature takes display precedence; it never replaces independent computation records. `null` is missing, not zero. |
| `corroborating` | Other records for the same slot, kept separate. |
| `degrees` | Sorted union of actually recorded homology and cohomology degrees. A missing cell is labelled “Not recorded.” |
| `computedRingState` | `recorded`, `withheld`, or `not_recorded`; this never alters separately sourced cohomology. |

The shared template then renders identity, aligned invariants, a coefficient
comparison on request, a compact ring summary, and source/confidence. Basis,
products, models, evidence and raw JSON are disclosures. The large K3 and
connected-sum records use the same hierarchy; their large presentations are
never silently truncated or promoted above the invariants. Computed provenance
remains distinct from literature provenance and human mathematical review.

This follows the [LMFDB development guide](https://github.com/LMFDB/lmfdb/blob/main/Development.md)
principle that each object has a durable home page reached through browse and
search, and its [object-page style guide](https://github.com/LMFDB/lmfdb/blob/main/StyleGuide.md)
ordering from identifying information through standard invariants to deeper
technical material. The local
[atlas UI research](atlas-ui-ux-redesign-2026-07-23.md) supports a continuous
article, typographic hierarchy and progressive disclosure. These are
architectural references, not a visual-style prescription.

## Remaining truth limits

- Withheld computed rings remain withheld. S⁰ also has separately sourced ring
  information, and the page states both facts.
- A space may have homology but no recorded cohomology for the selected
  coefficient. The aligned cell says “Not recorded,” never `0`.
- A computation may supply a complete product table without a compact ring
  presentation. The page describes the basis and table rather than inventing a
  quotient formula.
- A recorded presentation may include imported claims about generation and
  relation completeness. The detailed record keeps that qualification.
- The browser screenshot and visual acceptance gate remains outstanding until
  the local preview can be opened in an authorized browser surface.
