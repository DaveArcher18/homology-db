# Machine-readable external reviews

This directory is reserved for review records that unlock a named release
gate. A record is added only after the named human reviewer has evaluated the
exact candidate and supplied a verdict; development work never manufactures
one.

## Open feedback preview

An explicitly authorized public preview may carry the exact 49-spectrum
candidate before acceptance. It must use `--allow-public-review-preview` in
both the exporter and Pages gate, retain `spectrum_review_candidate = true`,
label every spectrum and module `imported_unreviewed`, preserve import evidence
as `imported_unreviewed`, and carry no acceptance record. The preview gate
still validates the pinned identities, complete finite modules, content and
source hashes, 5 MiB limit, and two byte-identical fresh rebuilds.

This mode exists for informal inspection and GitHub feedback. It does not
finalize the spectrum Snapshot, materialize assertion reviews or editorial
admissions, or weaken the accepted-release contract below.

The cw49 gate expects `steenrod-cw49-v1-dan.json` with this shape. Development
may generate the candidate packet and coverage report, but it does not generate
this acceptance record or populate any of its verdict fields:

```json
{
  "schema_version": "homology-db.steenrod-acceptance/1",
  "reviewer": "Dan Isaksen",
  "verdict": "accept",
  "reviewed_at": "<RFC 3339 timestamp>",
  "evidence": {
    "kind": "written_acceptance",
    "locator": "<retained email, notes, or other review locator>",
    "sha256": "<SHA-256 of the retained evidence>"
  },
  "editorial_actor": "<person recording the admission>",
  "bindings": {
    "candidate_sha256": "<from the review packet>",
    "spectrum_source_sha256": "<from the review packet build block>",
    "source_commit": "<40-character source commit>",
    "source_inputs_sha256": "<from the review packet build block>",
    "source_database_hash_kind": "homology-db.sqlite-logical/1",
    "source_database_sha256": "<from the review packet build block>",
    "review_packet_sha256": "<SHA-256 of the exact review packet bytes>",
    "coverage_report_sha256": "<SHA-256 of the exact coverage report bytes>",
    "spectrum_snapshot_id": "<from release_projection.spectrum_snapshot>",
    "spectrum_snapshot_manifest_sha256": "<from release_projection.spectrum_snapshot>",
    "spectrum_count": 49,
    "assertion_review_count": 5828,
    "assertion_review_manifest_sha256": "<from release_projection.assertion_reviews>",
    "editorial_admission_count": 5829,
    "editorial_admission_manifest_sha256": "<from release_projection.editorial_admissions>",
    "tmf_profile_module_content_sha256": "<from release_projection.editorial_admissions>"
  }
}
```

The candidate hash is computed from the canonical embedded
`conceptual_spectra` payload after `review` and `review_state` fields are
removed. The 5,828 assertion-review targets comprise 5,780 finite Steenrod
action assertions and 48 finite completeness assertions. The 5,829 admission
targets add the immutable `tmf` profile module to those assertions. Migration
0005 provides the typed append-only module Editorial effect needed to
materialize that last admission.

After the record has been supplied, the accepted local artifact is built with
`--steenrod-acceptance-record`. The exporter reconstructs the unreviewed
candidate, verifies every binding, overlays only review metadata, preserves all
canonical module content hashes, materializes the reviews and Editorial
admissions in a separate AtlasSchema v5 ledger, and records the finalized
spectrum Snapshot. The existing `source_database_*` fields continue to identify
the 42-space Chromatic database. Accepted artifacts additionally carry
`spectrum_database_hash_kind` (`homology-db.sqlite-logical/2`),
`spectrum_database_sha256`, and the deterministic `spectrum_materialization`
summary for that stable ledger. The v2 identity excludes only the physical
build timestamp `schema_migration.applied_at`.

The Pages gate independently rematerializes the ledger, validates both database
identities, rebuilds the accepted atlas twice from fresh databases, and requires
the checked artifact to match those canonical bytes. Until this succeeds, a
public preview may remain available for feedback, but it is never described as
the reviewed or finalized release.
