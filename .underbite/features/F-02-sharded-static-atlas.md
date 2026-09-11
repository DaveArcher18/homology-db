# F-02 — Sharded static atlas delivery

Status: specified; implementation not started

## Outcome

The public atlas loads a small catalogue and only the selected space/spectrum
record while preserving the current routes, mathematical display, provenance,
review state, downloads, and a separate self-contained offline snapshot. The
same files work on GitHub Pages and a future static/object host.

## Relevant context

The student-facing product remains a static reference. Gabriel's larger corpus
demonstrates that embedding all records in one HTML file no longer scales. The
current Python exporter already produces one validated structured read model;
`static_atlas/atlas.js` currently synchronously indexes its embedded global
`atlas` object. The accepted data contract is
`docs/architecture/static-data-bundle-v1.md`.

## UX and UI

- Preserve all visible navigation, space/family/textbook/glossary/about/spectrum
  routes and current page hierarchy.
- Show a brief labelled loading state when a subject document is requested.
- On load failure or cross-bundle mismatch, show an honest recoverable error
  with Retry and Return to all spaces. Never substitute an empty or zero result.
- Preserve copied links, refresh, Back/Forward, focus movement, keyboard use,
  mobile layouts, theme, coefficient state, and existing review links.
- Keep “Download JSON” for one loaded subject and provide a clearly labelled
  complete offline snapshot download.

## Functional

- Generate the exact v1 layout, envelopes, manifest, hashes, catalogue, subject
  and shared documents defined by the accepted contract.
- Load catalogue data once and subject data on demand; memoize successful loads.
- Reject unsupported schema, wrong Snapshot/bundle/subject identity, missing
  manifest entries, and mismatched records without conflating failure and
  mathematical absence.
- Keep family formula evaluation in the browser and keep all review/provenance
  bindings exact and independent.
- Produce deterministic sharded and self-contained artifacts from one validated
  read model. Deploy complete generated output atomically through the existing
  Pages workflow.
- Preserve compatibility with all current stable IDs, slugs, hash routes, and
  per-record download meaning.

## Out of scope

No Gabriel 200-space import, Regina ingestion, Supabase/database backend,
accounts, server API, computation service, new mathematics, mathematical review
promotion, UI redesign, or hosting-provider migration.

## Proof plan

- Unit-test canonical envelopes, aggregate/file hashes, deterministic ordering,
  path safety, catalogue/subject parity, cross-bundle rejection, absence versus
  failure, and atomic build replacement.
- Reconstruct and validate the current complete read model from the partitioned
  output; compare all 42 spaces, 49 spectra, shared catalogs, and downloads with
  the all-in-one oracle.
- Run two clean byte-identical builds and the existing source/Snapshot release
  gates on the exact candidate.
- Browser-test every legacy route plus loading, retry, missing file, mismatched
  bundle, copied state, refresh, Back/Forward, keyboard, mobile, zoom, and the
  complete offline artifact.
- After deployment, require live manifest/document hashes and the shell/offline
  artifact to match the committed bundle, then repeat representative live routes.
