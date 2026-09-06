# Independent navigation repair review

Reviewer: `/root/family_engine`, agent. Scope: approved navigation repair relative
to `7cf1a00`; source and test review, not a human mathematical review.

## Findings

1. **Mobile request-space link lost.** Removing the old drawer also removes its
   Request a space link, while the surviving header `.request-link` remains
   `display:none` below 45rem. No equivalent request URL is exposed by All spaces,
   About or footer. Restore a visible request link in About/footer and cover
   320px and 700px in interaction checks.
2. **About refresh loses return state.** `lastWorkbenchHash` is initialized to
   `#home` in memory. Workbench → About → reload → Workbench consequently loses
   n/degree/family; the new test returns through browser Back before testing the
   Workbench link, which reconstructs state and masks this path. Preserve the
   return state across refresh if the intended contract includes this path,
   and test the direct return after About reload.

## Confirmed by inspection

- Native select exposes three stable option values; Explore still applies
  family/n/degree together. Mathematical generation and download code unchanged.
- Family engine, family metadata, review validator and review registry have no
  diff against `7cf1a00`; review hashes and mathematics are not altered by the
  navigation repair.
- Legacy space/family and spectrum route parsers remain intact. Route changes
  retain heading focus and hash-based browser history.
- About includes purpose, coverage caveats, distinct provenance/human review
  states, snapshot details and secondary spectra navigation.
- Primary aria-current state is cleared by spectrum navigation, and the
  footer spectrum link marks page/location appropriately. The About spectrum
  link is an ordinary content link; it does not create duplicate current items.
- Old drawer elements, backdrop, trap and inert handlers are removed. Form
  layout wraps before its former overflow range; widths around both breakpoints
  are explicitly included in the new browser suite.
- New tests cover native keyboard selection, 33 selected-family applications,
  About visibility/focus, reload/history and breakpoint resizing. `selectOption`
  verifies selection/application but does not itself exercise an open native
  menu; root's Codex mouse interaction is complementary evidence.

## Verification limits

My attempted separate Chrome probe was sandbox-aborted at launch, before any
page inspection. Root is running Chrome and Codex checks; this report does not
misrepresent those as independently executed here. Mathematical diff check was
executed and showed no changes in the four source/review files listed above.

## Final correction review

Both findings are resolved in the frozen candidate:

- About now contains a dedicated, unhidden `about-request-link` using the same
  request-space URL as the header, with `noopener noreferrer` for the new tab.
  The browser regression explicitly checks its visibility at every tested width.
- A validated, same-page workbench hash is retained in session storage and
  restored on startup. The guard allows only supported families and nonnegative
  integer parameters, not external navigation URLs. Storage failures degrade
  safely to the default workbench. The regression now tests the direct
  About → reload → Workbench return before invoking browser Back.
- Root identified an additional inherited two-column-grid navigation-label
  defect in Codex visual inspection. Navigation links now use an intrinsic
  inline-flex layout; the regression checks each label's own overflow as well
  as document/viewport bounds.

Final source SHA-256 values:

- `static_atlas/atlas.js`: `177a63c2b29d56ccd9b0159915ffbe65c32a40af78c4f7fb51da0742f5d43a44`
- `static_atlas/atlas.css`: `8909050e3e866ab6f3b1389a1ce74e07ac94c5be2f8a6a3050f4d8d1f7ea6886`
- `static_atlas/index.template.html`: `f450c3d1e32c546b9af1a05cbbaaea9fdf2a2aea1f4c3496df0a430583fa14f0`
- `static_atlas/workbench.js`: `791b7c6b3a811cb98a12db49d372d6d60c7f159382fa997e9d556b7a75000e82`
- `scripts/verify_navigation_browser.cjs`: `41b94a0ba28fcba9fc6ddfdbfb985e493fd3d0f680e4e59de91fb5c47af36d1f`

The four mathematical/review files were rechecked against `7cf1a00` with no
diff. `node --check static_atlas/atlas.js` and `git diff --check` pass. Root
reports the corrected browser regression passing 11 widths and 33 selections,
keyboard and history/reload checks; that execution remains root's evidence,
not a claim of independent browser execution here.

The final test-only strengthening was inspected after this source freeze. It
asserts that changing the picker/parameters does not navigate before Explore,
checks native select keyboard typeahead for all three families, and exercises
actual Chrome page zoom at 125% and 200%. Zoom settings are changed only in an
isolated temporary persistent profile, closed in `finally`, not in the user's
browser profile. A viewport-width assertion verifies that zoom really applies,
followed by control visibility/bounds and document overflow checks on workbench
and About. Root reports both zoom levels and the full matrix passing. All four
UI source hashes above remain unchanged; this test strengthening does not
reopen the implementation review.

Final status: **no remaining identified blocker within the navigation review
scope**. This acceptance is exact-source-bound and does not replace the final
artifact rebuild, full-suite, publication or live verification. Only this
report was edited by this review.
