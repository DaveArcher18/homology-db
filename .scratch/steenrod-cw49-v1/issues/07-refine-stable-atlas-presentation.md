Type: task
Status: resolved
Claimed by: /root (interactive chat)
Claimed at: 2026-08-09T08:25:07Z
Blocked by:

# Refine the stable atlas presentation

Implement the confirmed two-round Converge context in
`.scratch/steenrod-presentation-feedback-v1/shared-context.md` without changing
the mathematical corpus or review state.

## Acceptance

- Keep Home spaces-first and friendly. Add one compact “what's new” banner
  describing Steenrod-operation tables, their imported/unreviewed feedback
  state, and one secondary link to the stable index.
- Render all semantic mathematics on spectrum routes through the existing safe,
  dependency-free TeX path: spectrum names, coefficients, basis elements,
  Steenrod operators, sums, and profile notation.
- Use curated TeX names only where the imported identifier has an obvious
  interpretation. Preserve the raw identifier as the display fallback for
  unresolved names.
- Keep exact cw49 identifiers searchable and reproducible. Show them in detail
  metadata, downloads, manifests, and provenance, not as browse-list subtitles.
- Say “stable homotopy category” before introducing `Sp`. Put a concise
  provisional-foundations disclaimer on the spectra landing page and a fuller
  note in About; do not repeat it on every object page.
- Preserve all 42 existing space routes, all 49 spectrum routes, the one-file
  size cap, deterministic rebuilds, exact-zero/unknown semantics, and every
  `imported_unreviewed` state.
- Test the source contract, exact generated artifact, keyboard and responsive
  behavior, safe TeX fallbacks, and deployment gate before publishing.

## Answer

The public-review atlas now keeps Home centered on the existing 42 spaces and
introduces the stable update through one compact secondary banner. Stable
routes use the shared safe TeX renderer for spectrum names, coefficients,
basis elements, Steenrod operations, sums, profiles, and `Sp`; 19 obvious
names receive curated mathematical presentation, while the remaining 30 keep
their exact cw49 identifiers as the visible fallback. Detail routes preserve
the raw ID in metadata, search, provenance, and downloads.

The spectra landing page introduces the stable homotopy category before
`Sp` and carries the concise provisional-foundations note; About carries the
fuller explanation. Every imported claim remains `imported_unreviewed`, and
the accepted-release path is unchanged.

## Comments

- The user confirmed the reconciled context and authorized proceeding on
  2026-08-09. The two raw packets remain local beside the shared-context brief.
- Fixed-point specification and standards re-reviews report no remaining
  actionable defect. Desktop QA covered all 49 spectrum routes and all 42
  existing space routes; 390-pixel and keyboard checks covered reflow, exact-ID
  search, focus movement, table-local scrolling, and semantic/spoken math.
- The exact 5,084,430-byte artifact is byte-identical to a second clean export,
  has SHA-256 `0233958c69beeac7c75540d7bcd0d0ee11cc6e425e30a9100f7012783e4ecb7d`,
  passes the deterministic preview release gate, and passes all 154 local
  tests with three documented optional external-consumer tests skipped.
- PR [#2](https://github.com/DaveArcher18/homology-db/pull/2) was merged with
  source ancestry preserved. Pages run
  [31305860160](https://github.com/DaveArcher18/homology-db/actions/runs/31305860160)
  passed, and the public HTTP body at
  <https://davearcher18.github.io/homology-db/> is byte-identical to the
  reviewed artifact. Live Home, spectra, and `Ceta` route checks passed.
