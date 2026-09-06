# Independent reading-page review

Reviewer: `/root/family_engine` (agent). Read-only audit of the legacy page,
family workbench and CSS changes. No mathematical acceptance is implied.

## Findings communicated to the primary agent

1. **Source shortcut can hide keyboard focus behind the sticky header.**
   `source.scrollIntoView({block:'start'})` followed by focus with preventScroll
   respects only `.wb-provenance {scroll-margin-top:1rem}`, smaller than the
   sticky site header. Use a header-aware margin and test the summary's bounds
   after clicking Sources & derivation.
2. **Citation role matching is too broad.** `role.includes('homology')` also
   accepts `cohomology`/`cohomology_only`. Current 42-record data contains no such
   misleading role, so the present sources are selected correctly. Use exact
   role-token matching or an explicit supported-role set and a negative fixture.
3. **Printed display note becomes inaccurate.** Print CSS reveals all recorded
   rows while leaving the note "Showing the first 9". Hide the screen-only
   display note in print or provide print-specific truthful copy.

## Confirmed invariants

- All 42 space records were inspected in the preceding bounded audit. Current
  source-role inventory includes model_and_homology, homology and
  model_homology_and_identity, with contextual/identity-only roles now excluded.
- Missing ring results still explicitly say not recorded and not zero. Exact
  zero cells retain the same rendering/data paths.
- Coverage uses the existing source-qualified helpers. Human-review status is
  separately exposed near the title and never inferred from completeness.
- Reduced homology labels now include the tilde per row. The cohomology ring
  remains ordinary/unreduced. No coefficient/group/multiplication algorithm changed.
- Additional homology rows stay present in the DOM and can be revealed using a
  native button with aria-expanded; the first-nine note distinguishes display
  scope from coverage. Changing coefficients regenerates the appropriate rows.
- Legacy links without queries remain valid. Valid coefficient and reduced
  query values hydrate the view; copied links serialize them, and replaceState
  persists a changed selection without adding route-history noise. Family
  aliases still route to the comparison workbench, where coefficients are all
  visible and only reduced state needs forwarding.
- All-degree rules and cup products remain native details controls; collapsing
  them does not remove their contents. Rule identity moved to a nested
  disclosure, not out of the export/review binding. Review/download controls
  are moved rather than recreated; their existing bound URLs/payloads remain.
- No diff under homology_db, static_atlas/families.js or docs/reviews: imported
  mathematical records and review authority are unchanged.
- Both changed JavaScript files pass node syntax checks; git diff --check passes.

## Verification boundary

Root owns the all-42 screenshot/browser matrix. This report is source and
data-state inspection, not an independent browser run. It requests the three
small corrections above before final source-bound disposition. Only this
report was edited by the reviewer.

## Final re-review

All three findings are resolved:

- Supporting citations match the exact `homology` underscore-delimited role
  token, excluding `cohomology` and contextual/identity-only roles.
- Source scrolling uses `calc(var(--header-height) + 1rem)`; the new browser
  assertion verifies focused summary placement below the actual header bottom.
- Print hides the screen-only degree-display note and reveals all additional
  rows with `display:table-row !important`, overriding hidden-state rules.

The new five-card finite-field strip has an explicitly named keyboard-focusable
scroll region, visible scrolling instructions and print stacking. All seven
coefficient panels still use the same evaluator, records, coverage and
unreduced/reduced separation. Typeset legacy coefficient labels retain the
coefficient radio values and text alternatives. No further blocking defect was
identified by this source audit.

The dedicated browser test was inspected: it enumerates all embedded spaces,
checks every available legacy coefficient, missing-ring language, first-nine
and expanded/print row visibility, copy/reload/back state, reduced math labels,
finite-field keyboard scroll, source focus and dark theme. Root reports it
passing 42 spaces, 169 legacy coefficient views and four widths, together with
the existing family and 11-width/zoom navigation suites. These browser runs
are root's execution evidence, not independently executed by this reviewer.
JavaScript syntax and diff checks were independently rerun successfully.

Exact reviewed SHA-256 values:

- `static_atlas/atlas.js`: `005503ba9484b2ee20abcfba8336abd920ccf51a3757f38c0fe1562a0265b296`
- `static_atlas/workbench.js`: `66e55aefee52d50c39674cf8627148ac587c9d144babfc7ea78a8685796cd81f`
- `static_atlas/atlas.css`: `478dad6dcb2a6193cc7ac512deabe549abb351d2378559f72997ee7376e25e8a`
- `scripts/verify_space_reading_browser.cjs`: `bbdfa7492b0a3700c5e64859a3b9996dfdac77f8a0fdd7bdea0a32fc44dd3053`

Mathematical source/evaluator and review files were rechecked with no diff.
Final disposition: **no remaining identified blocker within this review scope**.
This does not replace deterministic artifact, full-suite or live-release checks.
