# Homology Atlas UI/UX redesign research

Date: 2026-07-23

Status: implementation-oriented synthesis of primary standards and official
design-system guidance. This is not a substitute for task-based testing with
topologists and other intended users.

## Recommendation in one sentence

Make the atlas a quiet **catalogue plus continuous reading surface**: a compact
header, one prominent search field, a compact family/index column, and one
sectioned mathematical document. Keep ordinary Homology, coverage, and a short
provenance summary visible; put advanced filters and specialist review records
behind clearly labelled disclosures. Use cool-neutral light and dark palettes,
selected through a persistent `System / Light / Dark` preference.

This is an atlas-specific synthesis. A compact master-detail presentation was
considered, but the product PRD's continuous-scroll, browser-find, print, and
all-record rendering requirements are stronger constraints. The implementation
therefore keeps every filtered record in one anchored document and obtains the
same calmness through lower chrome, a narrower reading measure, compact index,
and progressive disclosures. It directly addresses the current page's two main
problems: every element competes for attention, and too many bordered
controls/tags/details create visual “box soup.”

## Family-browser iteration

Direct review of the 42-space snapshot exposed a second structural problem:
17 mathematical families were flattened into one jump list, while a separate
family select and alphabetical space list gave “family” three conflicting
meanings. Parameterized members such as spheres, Moore spaces, lens spaces,
classifying spaces, and projective filtrations consequently looked unrelated.

The revised interaction model treats the family as the atlas's primary
navigation unit:

- one persistent family outline replaces the jump list, family select, and
  separate visible-space list;
- native disclosures reveal each family's narrative, chromatic relevance,
  members in curated order, and explicit parameters/dimensions;
- fragment links navigate, while a separately labelled “Show only this
  family” button filters, so those actions are never overloaded;
- family chapters repeat the member outline before their full records, making
  a parameterized family legible in the reading surface as well as the menu;
- search updates visible/total counts and opens matching families without
  deleting zero-result families from the conceptual map; and
- the family outline is built once and updated in place, preserving keyboard
  focus and assistive-technology position.

This iteration also replaces the remaining native-looking control stack with a
single command bar, coefficient radio group, compact refinement sheet, and
three-state theme menu. At narrow widths, the same family outline becomes a
focus-contained, full-height sheet rather than a different information
architecture.

## Evidence that should govern the redesign

### Structure before decoration

- Use a single logical heading hierarchy and let spacing, type scale, and
  section rules carry most of the hierarchy. GOV.UK advises consistent
  `h1`/`h2`/`h3` structure, while WCAG requires visual relationships such as
  headings, lists, labels, and tables to be programmatically available
  ([GOV.UK headings](https://design-system.service.gov.uk/styles/headings/);
  [WCAG 1.3.1](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html)).
- A card is a modular summary/entry point within a collection, not simply
  “content with a border.” USWDS explicitly says not to use card styling for
  every bordered piece of content
  ([USWDS card guidance](https://designsystem.digital.gov/components/card/)).
  Therefore the selected space should be one continuous article, not a stack
  of nested cards.
- An index is useful on long, structured pages. USWDS recommends in-page
  navigation when content spans at least several viewport heights, provided
  the page has a heading structure
  ([USWDS in-page navigation](https://designsystem.digital.gov/components/in-page-navigation/)).
  In this atlas, the compact space/family result list serves that orientation
  role while the selected article stays readable.
- Running prose should not stretch across the full wide desktop canvas.
  USWDS recommends roughly 45–90 characters per line and about 66 for long
  reading
  ([USWDS typography](https://designsystem.digital.gov/components/typography/)).

### Progressive disclosure, not hidden essentials

- Native `<details>/<summary>` is a widely available disclosure primitive
  ([MDN `<details>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details)).
  GOV.UK recommends it for information only some users need, and explicitly
  warns against hiding information most users need
  ([GOV.UK details](https://design-system.service.gov.uk/components/details/)).
- For this product, **never hide**: space name and aliases, family/dimension,
  coefficient choice, ordinary/reduced convention, coverage or truncation,
  homology groups, reliability wording, and a short source/evidence summary.
- It is appropriate to disclose: advanced filters, full models and
  constructions, relationship records, citation locators and sketches,
  computation-run metadata, data-quality diagnostics, and raw JSON.
- “Review details” may expand all specialist disclosures, but it should not
  add a second competing visual mode or turn the main table into an
  unreadably wide grid.

### Search and filtering

- Search should remain the dominant control. USWDS recommends a visible,
  labelled search box, at least about 27 characters wide, preserving the
  entered terms
  ([USWDS search](https://designsystem.digital.gov/components/search/)).
- Keep exact name/alias matches ahead of broad metadata matches. Filter the
  continuous document to the best-ranked matching records and update the
  compact space index. Do not render full records as “result cards.”
- Keep only **Search**, **Coefficients**, **Filters (n)**, and **Theme** in the
  primary bar. Put family, dimension, reliability, torsion, and reduced-state
  refinements in one labelled Filters disclosure. The summary must expose the
  active count, and a nearby “Clear filters” action must restore all results.
- Update the visible result count in a `role="status"` live region without
  moving focus. W3C provides this exact pattern for search results, and a
  status is intentionally polite rather than interruptive
  ([W3C search-result status example](https://www.w3.org/WAI/WCAG21/working-examples/aria-role-status-searchresults/);
  [MDN status role](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/status_role)).
- Preserve the selected space in the URL. As a later enhancement, serialize
  meaningful search/filter state into query parameters so a filtered view can
  be shared; do not put visual theme preference in a shareable URL.

### Homology table readability

- Keep a real `<table>` with a concise `<caption>`, `<th scope="col">`, and
  `<td>` cells. WAI notes that captions identify tables and header associations
  preserve row/column context for assistive technology
  ([WAI tables tutorial](https://www.w3.org/WAI/tutorials/tables/);
  [WAI caption guidance](https://www.w3.org/WAI/tutorials/tables/caption-summary/)).
- Default view: two columns, **Degree** and **Group**. Make Degree narrow and
  right-aligned; give Group the remaining width. Use tabular numerals and a
  math-friendly font for values. GOV.UK recommends right alignment for
  comparable numeric columns
  ([GOV.UK table](https://design-system.service.gov.uk/components/table/)).
- Use a borderless table with subtle row separators or alternating row tone,
  not a box around every cell. USWDS identifies borderless tables as suitable
  for text-heavy data and striping as an aid for tracking across rows
  ([USWDS table](https://designsystem.digital.gov/components/table/)).
- In Review mode on wide screens, State and Assertion ID may be columns. On
  narrow screens, render those values as labelled secondary lines within each
  row instead of forcing four columns. If a genuinely two-dimensional future
  table must scroll, wrap it in a keyboard-focusable scroll region and test it
  with screen readers; USWDS documents an outstanding keyboard caveat for
  scrollable tables
  ([USWDS table accessibility tests](https://designsystem.digital.gov/components/table/accessibility-tests/)).

### Light/dark theme and user preference

- Set `<meta name="color-scheme" content="light dark">` before styles and
  `color-scheme: light dark` on `:root`. This lets the browser render native
  controls, scrollbars, and other UI consistently
  ([MDN `color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/color-scheme)).
- Default to the operating-system preference with
  `prefers-color-scheme`. Offer an explicit three-state `System / Light /
  Dark` control. MDN defines `prefers-color-scheme` specifically for this user
  preference
  ([MDN `prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-color-scheme)).
- Save only an explicit theme choice in `localStorage`; when choice is
  `System`, remove the override and follow `matchMedia` changes.
  `localStorage` persists across browser sessions, and `matchMedia` can monitor
  preference changes
  ([MDN `localStorage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage);
  [MDN `matchMedia`](https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia)).
  Access storage inside `try/catch` so a blocked storage API does not break the
  atlas.
- Define all colors as semantic custom properties (`--page`, `--surface`,
  `--text`, `--muted`, `--border`, `--accent`, `--warning`, `--focus`) and
  override those tokens, not individual components. USWDS recommends small,
  role-based project palettes and introducing color only after the hierarchy
  works in black and white
  ([USWDS color guidance](https://designsystem.digital.gov/design-tokens/color/overview/)).

#### Recommended starting palette

These are official USWDS system-token values, shifted from the current
beige/teal treatment to cool neutral and restrained indigo. The text ratios
below were checked with the WCAG relative-luminance formula. Final component
states still need automated and manual contrast testing.

| Semantic role | Light | Dark |
| --- | --- | --- |
| Page | `#f7f9fa` | `#151622` |
| Primary surface | `#ffffff` | `#1c1d1f` |
| Selected/subtle surface | `#eef0f9` | `#292d42` |
| Primary text | `#1c1d1f` (15.97:1 on page) | `#f7f9fa` (17.00:1 on page) |
| Secondary text | `#565c65` (6.38:1 on page) | `#c6cace` (10.89:1 on page) |
| Link/accent | `#3f57a6` (6.72:1 on white) | `#94adff` (7.78:1 on surface) |
| Functional control border | `#71767a` | `#71767a` |
| Warning text/accent | `#8a4b08` (6.79:1 on white) | `#fee685` (14.42:1 on page) |
| Focus ring | `#3f57a6` | `#b8c8ff` |

Source token values:
[USWDS system color tokens](https://designsystem.digital.gov/design-tokens/color/system-tokens/).
WCAG requires 4.5:1 for ordinary text, 3:1 for large text, and 3:1 for
meaningful control/state graphics
([WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html);
[WCAG 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast)).
Reliability and warning states must also have explicit text/icon/shape cues;
color alone cannot carry meaning
([WCAG 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)).

## Prioritized atlas decisions

### P0 — required for this redesign

1. **Keep the PRD's continuous document, but quiet its hierarchy.** Retain all
   filtered records, family groupings, browser-find/print behavior, and hash
   deep links; use the compact index for orientation rather than duplicating
   full entries as cards.
2. **Remove nested panel styling.** Use at most three surface levels (page,
   primary, selected/subtle); use whitespace, headings, and single-pixel
   separators before adding borders or shadows. Tags become plain metadata
   text unless they are interactive.
3. **Simplify the primary controls.** Search stays wide; Coefficients remains
   adjacent; advanced filters become one disclosure with an active count;
   Reset appears only when state differs from defaults.
4. **Implement System/Light/Dark end-to-end.** Apply semantic tokens to every
   surface, control, table, link, focus indicator, status, warning, and code
   block. Persist explicit preference and honor live system changes.
5. **Keep the essential scholarly record visible.** Ordinary Homology,
   coverage, reliability text, and concise provenance remain in the reading
   flow. Specialist/raw records use native details.
6. **Make the default homology table two-column and borderless.** Preserve
   captions and scoped headers; adapt Review metadata rather than creating
   horizontal page overflow.

### P0 — accessibility corrections while touching the interaction layer

1. **Remove global single-character shortcuts** (`/`, `j`, `k`) or require a
   modifier and document the shortcuts. WCAG 2.1.4 requires single-character
   shortcuts to be switchable, remappable, or active only when the relevant
   control has focus
   ([WCAG 2.1.4](https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts)).
   Do not capture global Arrow keys; they are expected to scroll the page.
2. **Use native links, buttons, selects, checkboxes, and details** wherever
   possible. Every pointer action must work with a keyboard
   ([WCAG 2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html)).
3. **Keep a clearly visible focus indicator in both themes** and test the
   entire forward and reverse tab order. Sticky content must not cover the
   focused element
   ([WCAG 2.4.7 and 2.4.11](https://www.w3.org/TR/WCAG22/#focus-visible);
   [sticky-header failure](https://www.w3.org/WAI/WCAG22/Techniques/failures/F110)).
4. **Use controls at least 24×24 CSS pixels, preferably about 40–44 pixels for
   primary mobile controls.** WCAG 2.2's AA minimum is 24×24, with limited
   spacing exceptions
   ([WCAG 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)).

### P1 — responsive and refinement work

1. At 320 CSS pixels, show header, search, coefficient, Filters button, result
   status/list, and selected article in one column with no page-level
   horizontal scrolling. WCAG's Reflow criterion uses 320 CSS pixels and warns
   that tall sticky regions can make zoomed content unusable
   ([WCAG 1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)).
2. Prefer an inline mobile result list. If the existing off-canvas index is
   retained as a modal drawer, it needs an accessible name, initial focus,
   contained tab order, visible Close button, Escape handling, and focus return
   to its opener
   ([WAI modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)).
3. Keep the sticky bar to one compact row on desktop. On small screens retain a
   compact sticky search/index surface, keep its filter disclosure dismissible,
   and ensure zoom never strands controls. Preserve one calibrated
   `scroll-margin` offset for deep-linked headings.
4. Retain `prefers-reduced-motion`; drawer and selection transitions should be
   removed when the user requests reduced motion
   ([MDN `prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion)).
5. Use a body line height around 1.5–1.62 and ensure user-applied WCAG text
   spacing does not clip or overlap content
   ([USWDS line height](https://designsystem.digital.gov/design-tokens/typesetting/line-height/);
   [WCAG 1.4.12](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing)).

### P2 — validate after deployment

- Run task-based sessions with intended users: find a named space; find a
  torsion example; change coefficients; judge computation coverage and source;
  submit a correction; copy a deep link; compare light, dark, and system mode.
- Test desktop and 320/390-pixel layouts at 100%, 200%, and 400% zoom; keyboard
  only in both directions; at least one screen reader; reduced motion; system
  theme changes; forced/high-contrast mode; print; and no-storage fallback.
- Record failures by task rather than by taste. Official component guidance
  repeatedly stresses testing components in the context of the actual product,
  not assuming that a component's isolated conformance transfers automatically
  ([USWDS search accessibility tests](https://designsystem.digital.gov/components/search/accessibility-tests/);
  [USWDS table accessibility tests](https://designsystem.digital.gov/components/table/accessibility-tests/)).

## Proposed static-page skeleton

```text
Header: Homology Atlas · scope/status · snapshot metadata · Theme
Search row: [ Find a space …………………… ] [ Coefficients ] [ Filters (0) ]

┌ Family / space index ─────┐  Continuous atlas document
│ 42 visible spaces         │  Family heading + feedback
│ Family                    │    Space name, aliases, dimension
│   Space                   │    Summary + relevance
│   Another space           │    Coverage + reliability + source
│ Another family            │    Ordinary Homology: Degree | Group
│   …                       │    Models, evidence, raw data [disclosures]
└───────────────────────────┘  Next space; next family; …
```

The diagram shows information hierarchy, not visual boxes: the implemented
page should use whitespace and a small number of dividers. The results list and
article are the only major desktop regions.
