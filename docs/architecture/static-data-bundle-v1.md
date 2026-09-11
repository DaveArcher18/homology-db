# Static data bundle v1

Status: accepted design; not yet implemented

This contract replaces the growing JSON payload embedded in `dist/atlas.html`
with deterministic static files. It changes delivery, not mathematical meaning,
review state, or the canonical Python/SQLite build inputs.

## Goals

- Load catalogue-scale metadata once and one complete space record on demand.
- Preserve stable hash routes, provenance, downloads, coverage, and explicit
  absence semantics.
- Remain deployable as ordinary files on GitHub Pages or any static/object host.
- Retain a complete, self-contained offline artifact as a separate download.
- Bind every file to one exact Snapshot and source revision.

No database service, account system, submission API, or computation service is
part of this contract.

## Published layout

```text
dist/
  atlas.html                         application shell
  data/
    manifest.json                    exact bundle inventory and root binding
    catalog.json                     navigation and search metadata
    shared/
      definitions.json
      family-rules.json
      teaching.json
      classical.json                 shared source/catalog metadata only
    spaces/
      <existing-unique-slug>.json    one complete conceptual-space page
    spectra/
      <existing-unique-slug>.json    one complete secondary spectrum page
  downloads/
    homology-atlas-<bundle-id>.html  self-contained offline snapshot
```

The deployed root continues to copy `dist/atlas.html` to `index.html`. Existing
routes such as `#space=klein-bottle`, family routes, glossary, textbook routes,
and spectrum routes do not change. Paths are relative so a future host move does
not change the read model.

## Common envelope

Every non-manifest JSON document uses canonical UTF-8 JSON with sorted keys,
compact separators, and one trailing newline. It has this envelope:

```json
{
  "schema_version": "homology-db.static-bundle-document/1",
  "bundle_id": "bundle-<content-derived lowercase hex>",
  "snapshot_id": "<existing Snapshot ID>",
  "source_commit": "<40 lowercase hex characters>",
  "document_kind": "catalog",
  "payload": {},
  "payload_sha256": "<canonical payload hash>"
}
```

`document_kind` is one of `catalog`, `definitions`, `family_rules`, `teaching`,
`classical`, `space`, or `spectrum`. The payload hash covers only canonical
`payload` bytes, avoiding a self-referential document hash. The manifest records
the SHA-256 and byte length of each complete file.

The `bundle_id` is derived from the sorted sequence of `(path, sha256, bytes)`
for all non-manifest documents plus the existing Snapshot and source-input
identity. The manifest records that sequence and its own schema version; the
HTML shell embeds the expected bundle ID and manifest path. No timestamp or
host-specific absolute path participates in identity.

## Manifest

`data/manifest.json` uses
`homology-db.static-atlas-bundle/1` and contains:

- bundle, Snapshot, source commit, source-input hash, and release state;
- read-model and family-rule schema versions;
- supported coefficients and conventions;
- counts by document kind;
- an exact sorted file inventory with path, media type, byte length, SHA-256,
  document kind, and stable subject ID where applicable;
- the offline artifact path, byte length, and SHA-256;
- the aggregate content hash from which `bundle_id` is derived.

The manifest never upgrades mathematical completeness or review state. Those
remain properties of the records it inventories.

## Catalogue

`catalog.json` contains only what navigation, search, routing, and result-card
summaries require:

- existing section records and ordered membership;
- for each space: stable ID, slug, plain/TeX name, aliases, summary, taxonomy,
  parameters, tags, finite-type/dimension/component metadata, and compact
  homology/cohomology/multiplication coverage summaries;
- for each spectrum: stable ID, slug, display name, summary, and review state;
- the path of each subject document.

It contains no homology rows, multiplication tables, raw evidence responses, or
download payloads. A catalogue coverage badge is a projection of a validated
subject document and is checked against it during the build.

## Space documents

A `space` payload is the current conceptual-space read-model record without
loss: homology rows and coverage, cohomology assertions, ring presentations and
products, Models, Evidence, citations, computations, relationships, raw
responses, data-quality diagnostics, and review/provenance state. Related-space
links refer to stable IDs/slugs and do not duplicate the target record.

Two assertions with different provenance remain separate. Imported computation
does not replace a literature record, and corroboration does not imply human
review. An empty cohomology list means no ring is recorded; it never means the
zero ring. Omitted multiplication entries mean zero only when the record's
explicit complete multiplication scope says so.

The existing “Download JSON” action serializes the loaded envelope and payload,
so a download remains useful and provenance-bound without another request.

## Shared documents and family evaluation

Definitions, reviewed family rules, teaching content, and classical source
metadata remain exact source-bound documents. They load only on routes that need
them and may be cached in memory. General family evaluation remains local and
deterministic; this split does not turn it into a network computation.

The `classical` shared document contains catalogue/source metadata. Individual
ring records live with their space, preventing a global ring table from becoming
the new monolith.

## Loader behaviour

The application shell contains only a tiny bootstrap record with expected
bundle ID, manifest path, and schema version. A data-store module:

1. loads and validates the manifest and catalogue;
2. indexes stable IDs and slugs from the catalogue;
3. loads a subject document only when its route is opened;
4. memoizes successful in-flight/completed loads for the page session;
5. checks schema, bundle, Snapshot, subject identity, and manifest file entry;
6. discards and reports a mismatched document instead of combining releases.

Requests append `?v=<bundle-id>` so a new shell does not reuse an older cached
document. A route renders a labelled loading state. Network/file failure renders
“This record could not be loaded” with Retry and Return to all spaces actions;
it must not render empty tables or “zero”. Unknown slugs remain “Page not found”.
Back/Forward navigation and copied hashes wait for the same loader path and move
focus to the resulting heading or error message.

The build validates complete-file hashes. Where Web Crypto is available, the
runtime may additionally verify downloaded bytes; lack of runtime hashing does
not weaken the build/release gate.

## Offline and compatibility

Browsers commonly block `fetch()` from neighbouring files under `file://`.
Therefore `dist/atlas.html` is the hosted sharded shell, while the generated
file under `dist/downloads/` preserves the current self-contained behaviour for
offline use. Both artifacts are generated from the same read model and manifest
and must expose the same routes and mathematical records.

Legacy space/family/spectrum hashes are acceptance fixtures. Existing JSON
download schema versions remain readable; the new envelope is additive. The
release does not redirect or rename stable subject IDs or slugs.

## Build and release invariants

- Build into a temporary directory, validate it completely, then replace the
  generated bundle so partial output is never published.
- Rebuild twice and require byte-identical manifests, JSON documents, shell, and
  offline artifact.
- Require every manifest file to exist with matching bytes/hash and reject
  unlisted generated data files.
- Require catalogue membership to equal the exact set of subject documents and
  require catalogue coverage projections to match those documents.
- Validate the existing full read model before partitioning and validate each
  reconstructed subject/shared projection afterward.
- Keep source-commit, source-input, Snapshot, review, and provenance gates.
- Never fetch third-party mathematics at page-view time; published records are
  exact files in the reviewed bundle.

## Migration sequence

1. Add a deterministic partitioner and bundle validator while keeping the
   current all-in-one artifact as the oracle.
2. Add the loader behind the existing routes and prove parity on the current 42
   spaces and 49 spectra.
3. Publish both sharded and offline artifacts and run local/live browser parity,
   caching, failure, history, keyboard, mobile, download, and legacy-route tests.
4. Only after parity, import the larger computed corpus through the same bundle
   interface.

The first implementation does not ingest Gabriel's larger branch, add Regina,
change hosting provider, or introduce a server database.
