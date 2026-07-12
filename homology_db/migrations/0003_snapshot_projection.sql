PRAGMA foreign_keys = ON;

CREATE TABLE snapshot(
    snapshot_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    selection_policy_id TEXT NOT NULL,
    selection_policy_sha256 TEXT NOT NULL,
    canonical_manifest_sha256 TEXT NOT NULL,
    current_projection_sha256 TEXT NOT NULL,
    finalized_at TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE snapshot_record(
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    record_kind TEXT NOT NULL,
    record_id TEXT NOT NULL,
    record_sha256 TEXT NOT NULL,
    PRIMARY KEY(snapshot_id, record_kind, record_id)
);
CREATE INDEX snapshot_record_lookup_idx ON snapshot_record(snapshot_id, record_kind, record_id);

CREATE TABLE snapshot_knowledge_selection(
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    knowledge_entry_id TEXT NOT NULL REFERENCES knowledge_entry(knowledge_entry_id),
    knowledge_revision_id TEXT NOT NULL REFERENCES knowledge_revision(knowledge_revision_id),
    knowledge_review_id TEXT NOT NULL REFERENCES knowledge_review(knowledge_review_id),
    PRIMARY KEY(snapshot_id, knowledge_entry_id),
    UNIQUE(snapshot_id, knowledge_revision_id)
);

CREATE TRIGGER snapshot_knowledge_selection_validate
BEFORE INSERT ON snapshot_knowledge_selection
WHEN NOT EXISTS (
    SELECT 1
    FROM knowledge_revision revision
    JOIN knowledge_review review
      ON review.knowledge_revision_id = revision.knowledge_revision_id
    WHERE revision.knowledge_revision_id = NEW.knowledge_revision_id
      AND revision.knowledge_entry_id = NEW.knowledge_entry_id
      AND review.knowledge_review_id = NEW.knowledge_review_id
      AND review.verdict = 'accept'
)
BEGIN
    SELECT RAISE(ABORT, 'invalid_snapshot_knowledge_selection');
END;

CREATE TABLE current_homology(
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    slot_key TEXT NOT NULL,
    projection_outcome TEXT NOT NULL CHECK(projection_outcome IN (
        'selected', 'unresolved_selection', 'conflicting', 'absent'
    )),
    selected_assertion_id TEXT REFERENCES assertion(assertion_id),
    conflict_set_id TEXT REFERENCES conflict_set(conflict_set_id),
    projection_sha256 TEXT NOT NULL,
    PRIMARY KEY(snapshot_id, slot_key),
    CHECK(
        (projection_outcome = 'selected' AND selected_assertion_id IS NOT NULL AND conflict_set_id IS NULL)
        OR (projection_outcome = 'conflicting' AND selected_assertion_id IS NULL AND conflict_set_id IS NOT NULL)
        OR (projection_outcome IN ('unresolved_selection', 'absent') AND selected_assertion_id IS NULL AND conflict_set_id IS NULL)
    )
);
CREATE INDEX current_homology_lookup_idx ON current_homology(snapshot_id, slot_key, projection_outcome);

CREATE TRIGGER current_homology_selected_closure
BEFORE INSERT ON current_homology
WHEN NEW.projection_outcome = 'selected' AND NOT (
    EXISTS (
        SELECT 1
        FROM assertion selected
        JOIN homology_assertion homology USING(assertion_id)
        JOIN snapshot_record member
          ON member.record_id = selected.assertion_id
         AND member.record_kind = 'assertion'
         AND member.record_sha256 = selected.record_sha256
        WHERE selected.assertion_id = NEW.selected_assertion_id
          AND selected.assertion_kind = 'homology'
          AND selected.slot_key = NEW.slot_key
          AND member.snapshot_id = NEW.snapshot_id
          AND (
              selected.knowledge_state <> 'exact'
              OR EXISTS (SELECT 1 FROM integer_group WHERE assertion_id = selected.assertion_id)
              OR EXISTS (SELECT 1 FROM field_dimension WHERE assertion_id = selected.assertion_id)
          )
    )
    AND EXISTS (
        SELECT 1
        FROM assertion_evidence link
        JOIN evidence item USING(evidence_id)
        JOIN snapshot_record member
          ON member.record_kind = 'evidence'
         AND member.record_id = item.evidence_id
         AND member.record_sha256 = item.record_sha256
        WHERE link.assertion_id = NEW.selected_assertion_id
          AND member.snapshot_id = NEW.snapshot_id
          AND (
              (item.evidence_kind = 'literature' AND EXISTS (
                  SELECT 1 FROM literature_evidence WHERE evidence_id = item.evidence_id
              ))
              OR (item.evidence_kind = 'computation' AND EXISTS (
                  SELECT 1 FROM computation_evidence WHERE evidence_id = item.evidence_id
              ))
              OR (item.evidence_kind = 'derivation' AND EXISTS (
                  SELECT 1 FROM derivation_evidence WHERE evidence_id = item.evidence_id
              ))
          )
    )
    AND EXISTS (
        SELECT 1
        FROM assertion_review review
        JOIN snapshot_record member
          ON member.record_kind = 'assertion_review'
         AND member.record_id = review.assertion_review_id
         AND member.record_sha256 = review.record_sha256
        WHERE review.assertion_id = NEW.selected_assertion_id
          AND review.verdict = 'accept'
          AND member.snapshot_id = NEW.snapshot_id
    )
    AND EXISTS (
        SELECT 1
        FROM editorial_event_effect effect
        JOIN editorial_event event USING(event_id)
        JOIN snapshot_record member
          ON member.record_kind = 'editorial_event'
         AND member.record_id = event.event_id
         AND member.record_sha256 = event.record_sha256
        WHERE effect.assertion_id = NEW.selected_assertion_id
          AND effect.effect_kind = 'admit'
          AND event.event_kind = 'admit'
          AND member.snapshot_id = NEW.snapshot_id
    )
)
BEGIN
    SELECT RAISE(ABORT, 'selected_assertion_not_grounded_in_snapshot');
END;

CREATE TRIGGER snapshot_no_update BEFORE UPDATE ON snapshot
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot'); END;
CREATE TRIGGER snapshot_no_delete BEFORE DELETE ON snapshot
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot'); END;
CREATE TRIGGER snapshot_record_no_update BEFORE UPDATE ON snapshot_record
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot_record'); END;
CREATE TRIGGER snapshot_record_no_delete BEFORE DELETE ON snapshot_record
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot_record'); END;
CREATE TRIGGER snapshot_knowledge_selection_no_update BEFORE UPDATE ON snapshot_knowledge_selection
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot_knowledge_selection'); END;
CREATE TRIGGER snapshot_knowledge_selection_no_delete BEFORE DELETE ON snapshot_knowledge_selection
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot_knowledge_selection'); END;
CREATE TRIGGER current_homology_no_update BEFORE UPDATE ON current_homology
BEGIN SELECT RAISE(ABORT, 'immutable_current_homology'); END;
CREATE TRIGGER current_homology_no_delete BEFORE DELETE ON current_homology
BEGIN SELECT RAISE(ABORT, 'immutable_current_homology'); END;

CREATE TABLE current_completeness(
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    subject_kind TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    assertion_id TEXT NOT NULL REFERENCES completeness_assertion(assertion_id),
    projection_sha256 TEXT NOT NULL,
    PRIMARY KEY(snapshot_id, subject_kind, subject_id, assertion_id)
);

CREATE TABLE supporting_assertion(
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    selected_assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    supporting_assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    PRIMARY KEY(snapshot_id, selected_assertion_id, supporting_assertion_id),
    CHECK(selected_assertion_id <> supporting_assertion_id)
);

CREATE TABLE canonical_export(
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    export_kind TEXT NOT NULL CHECK(export_kind IN ('snapshot_manifest', 'current_projection')),
    media_type TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    byte_length INTEGER NOT NULL CHECK(byte_length >= 0),
    PRIMARY KEY(snapshot_id, export_kind)
);
