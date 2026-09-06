# F-01 — Textbook reference ready for human QA

Status: implemented, independently verified and live, 2026-09-06. Human QA and
mathematical acceptance pending. Release5bf19f8; docs/QA_WITH_GABRIEL.md.

## Outcome

David and Gabriel can inspect a coherent textbook reference, follow short
explanations/comparisons, and submit a bounded mathematical review with precise
scope and source identity. A concise QA packet guides their first session.

## Relevant context

Read ../research.md, ../prd.md and ../grounding.md. Existing static product,
provenance and review-state boundaries remain authoritative. This feature
explicitly adds narrow review scope without relaxing maintainer validation.

## UX and UI

- Provide a sourced chapter/example-indexed Hatcher teaching/coverage map,
  explicitly labelled as a selected inventory, not every example in the book.
  Account for all 42 retained spaces, identifying the 13-space ring core and
  general-family redirects. Show missing coverage honestly.
- Give named spaces concise, sourced reader-facing introductions. Provide a
  small set of guided comparisons about coefficient dependence and ring versus
  additive information. Use existing routes, typesetting and inline exposition.
- Make the map and examples discoverable without cluttering the workbench.
  Improve mobile/keyboard reading; preserve current coefficient/form semantics.
- Allow a review of an exact family instance or narrower coefficient/degree/
  theory scope. Show its scope and verdict separately from whole-rule review.
- Explain public GitHub submission/maintainer validation; provide a concise
  copyable review packet when account-based submission is inconvenient.

## Functional

- Keep all 42 space and 49 spectrum routes, share state and downloads.
- Source-qualify one small useful next collection from existing spaces. Add
  mathematical records only when exact primary-source evidence and independent
  review support them; document selected/deferred entries and reasons. Do not
  silently manufacture coverage to meet a count.
- Review records remain version/hash-bound, append-only, with explicit human
  author and maintainer validation. Narrow acceptance never means entire rule
  accepted. Stale review cannot approve a changed rule; concern scope is visible.
- Preserve legacy review-document compatibility or provide an explicit tested
  additive version path. No fabricated reviews in production data.
- Static build and downloads remain deterministic. No runtime backend/network
  dependency beyond links and existing static delivery.

## Out of scope

No settings agent, backend, purchases, outreach, exhaustive Hatcher inventory,
general computation engine, broad spectrum expansion or claimed human acceptance.

## Proof plan

Source-check all new exposition/claims with exact primary-source locators;
independently inspect any new mathematics. Test review scope validation, stale
hashes, partial acceptance, concerns, history and old records. Check rendered
teaching links, math/knowls, missing coverage, keyboard/mobile and review packets.
Retain all existing Python, deterministic and browser regression suites. Freeze
an exact candidate and run independent feature verification. Publish under the
existing authorization, verify live bytes/interactions and provide a short QA
journey for David/Gabriel. Any inaccessible in-app check remains explicitly noted.
