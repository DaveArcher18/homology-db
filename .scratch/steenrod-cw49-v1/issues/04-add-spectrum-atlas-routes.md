Type: task
Status: resolved
Claimed by: /root/steenrod_review
Claimed at: 2026-08-05T15:58:08Z
Blocked by: 02, 03

# Add spectrum atlas routes

Extend the static payload and UI with spectrum browse/detail routes, operation
tables, review state, provenance, and deterministic downloads.

## Answer

The static payload now keeps `conceptual_spaces` and `conceptual_spectra`
separate. Review builds expose `#spectra` and `#spectrum=<slug>`, alias-aware
search, stable-category and review badges, source provenance, structured
feedback links, and build-time downloads for each supported adapter. Existing
space routes and behavior remain unchanged.

Finite spectrum pages lead with the ordered basis/action table and distinguish
nonzero, exact zero, unknown, and review state. `tmf` renders its infinite
profile and the typed Bruner limitation. Exact-artifact browser QA passed at
desktop, 390-pixel, and 320-pixel widths, including keyboard search, long
routes, `tmf`, malformed routes, internal table scrolling, and zero console
warnings or page-level overflow.

## Comments

- Resolved by `/root/steenrod_review` on 2026-08-05 after route, download,
  accessibility, responsive-layout, and malformed-data contracts passed.
