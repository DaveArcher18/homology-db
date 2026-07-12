CREATE TEMP TABLE migration_v4_conflict_guard(
    value INTEGER CONSTRAINT populated_v3_conflict_requires_editorial_migration
        CHECK(value = 0)
);
INSERT INTO migration_v4_conflict_guard
SELECT 1 FROM conflict_set LIMIT 1;
INSERT INTO migration_v4_conflict_guard
SELECT 1 FROM editorial_event_effect
WHERE effect_kind IN ('conflict_add', 'conflict_remove')
LIMIT 1;
DROP TABLE migration_v4_conflict_guard;

ALTER TABLE model_artifact RENAME TO model_artifact_v3;
CREATE TABLE model_artifact(
    model_artifact_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES model(model_id),
    source_artifact_id TEXT REFERENCES source_artifact(source_artifact_id),
    format TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);
INSERT INTO model_artifact
SELECT * FROM model_artifact_v3;
DROP TABLE model_artifact_v3;
CREATE INDEX model_artifact_content_idx ON model_artifact(content_sha256, model_id);

ALTER TABLE derived_artifact RENAME TO derived_artifact_v3;
CREATE TABLE derived_artifact(
    derived_artifact_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES model(model_id),
    artifact_kind TEXT NOT NULL,
    media_type TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);
INSERT INTO derived_artifact
SELECT * FROM derived_artifact_v3;
DROP TABLE derived_artifact_v3;
CREATE INDEX derived_artifact_content_idx ON derived_artifact(content_sha256, model_id);

-- A Snapshot is built as a draft because its member rows reference the parent.
-- The only permitted update seals it exactly once; child insert triggers then
-- prevent later records from changing the cited view.
ALTER TABLE snapshot RENAME TO snapshot_v3;
CREATE TABLE snapshot(
    snapshot_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    selection_policy_id TEXT NOT NULL,
    selection_policy_sha256 TEXT NOT NULL,
    canonical_manifest_sha256 TEXT,
    current_projection_sha256 TEXT,
    finalized_at TEXT,
    record_sha256 TEXT,
    CHECK(
        (finalized_at IS NULL
         AND canonical_manifest_sha256 IS NULL
         AND current_projection_sha256 IS NULL
         AND record_sha256 IS NULL)
        OR (finalized_at IS NOT NULL
            AND canonical_manifest_sha256 IS NOT NULL
            AND current_projection_sha256 IS NOT NULL
            AND record_sha256 IS NOT NULL)
    )
);
INSERT INTO snapshot
SELECT * FROM snapshot_v3;
DROP TABLE snapshot_v3;

ALTER TABLE editorial_event_effect RENAME TO editorial_event_effect_v3;
CREATE TABLE editorial_event_effect(
    event_id TEXT NOT NULL REFERENCES editorial_event(event_id),
    assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    effect_kind TEXT NOT NULL CHECK(effect_kind IN ('admit', 'retire')),
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(event_id, position)
);
INSERT INTO editorial_event_effect
SELECT event_id, assertion_id, effect_kind, position
FROM editorial_event_effect_v3
WHERE effect_kind IN ('admit', 'retire');
DROP TABLE editorial_event_effect_v3;

ALTER TABLE conflict_set RENAME TO conflict_set_v3;
CREATE TABLE conflict_set(
    conflict_set_id TEXT PRIMARY KEY,
    slot_key TEXT NOT NULL,
    declared_event_id TEXT NOT NULL REFERENCES editorial_event(event_id),
    record_sha256 TEXT NOT NULL
);
INSERT INTO conflict_set(conflict_set_id, slot_key, declared_event_id, record_sha256)
SELECT conflict_set_id, slot_key, declared_event_id, record_sha256
FROM conflict_set_v3;
CREATE TABLE conflict_ledger_effect(
    event_id TEXT NOT NULL REFERENCES editorial_event(event_id),
    conflict_set_id TEXT NOT NULL REFERENCES conflict_set(conflict_set_id),
    assertion_id TEXT REFERENCES assertion(assertion_id),
    effect_kind TEXT NOT NULL CHECK(effect_kind IN ('open', 'add_member', 'remove_member', 'close')),
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(event_id, conflict_set_id, position),
    CHECK(
        (effect_kind IN ('add_member', 'remove_member') AND assertion_id IS NOT NULL)
        OR (effect_kind IN ('open', 'close') AND assertion_id IS NULL)
    )
);
DROP TABLE conflict_member;
DROP TABLE conflict_set_v3;

CREATE TRIGGER assertion_subject_must_exist
BEFORE INSERT ON assertion
WHEN
    (NEW.subject_kind = 'conceptual_space' AND NOT EXISTS (
        SELECT 1 FROM conceptual_space WHERE space_id = NEW.subject_id
    ))
    OR (NEW.subject_kind = 'model' AND NOT EXISTS (
        SELECT 1 FROM model WHERE model_id = NEW.subject_id
    ))
    OR (NEW.subject_kind = 'family' AND NOT EXISTS (
        SELECT 1 FROM family_definition WHERE family_id = NEW.subject_id
    ))
    OR NEW.subject_kind = 'map'
BEGIN
    SELECT RAISE(ABORT, 'assertion_subject_not_found');
END;

CREATE TRIGGER run_input_artifact_must_exist
BEFORE INSERT ON run_input
WHEN NOT (
    (NEW.input_kind = 'source_artifact' AND EXISTS (
        SELECT 1 FROM source_artifact
        WHERE source_artifact_id = NEW.artifact_id
          AND content_sha256 = NEW.content_sha256
    ))
    OR (NEW.input_kind = 'model_artifact' AND EXISTS (
        SELECT 1 FROM model_artifact
        WHERE model_artifact_id = NEW.artifact_id
          AND content_sha256 = NEW.content_sha256
    ))
    OR (NEW.input_kind = 'derived_artifact' AND EXISTS (
        SELECT 1 FROM derived_artifact
        WHERE derived_artifact_id = NEW.artifact_id
          AND content_sha256 = NEW.content_sha256
    ))
)
BEGIN
    SELECT RAISE(ABORT, 'invalid_run_input_artifact');
END;

CREATE TRIGGER knowledge_link_target_must_exist
BEFORE INSERT ON knowledge_link
WHEN NOT (
    (NEW.target_kind = 'knowledge_entry' AND EXISTS (
        SELECT 1 FROM knowledge_entry WHERE knowledge_entry_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'conceptual_space' AND EXISTS (
        SELECT 1 FROM conceptual_space WHERE space_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'family' AND EXISTS (
        SELECT 1 FROM family_definition WHERE family_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'model' AND EXISTS (
        SELECT 1 FROM model WHERE model_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'assertion' AND EXISTS (
        SELECT 1 FROM assertion WHERE assertion_id = NEW.target_id
    ))
)
BEGIN
    SELECT RAISE(ABORT, 'invalid_knowledge_link_target');
END;

CREATE TRIGGER snapshot_record_must_resolve
BEFORE INSERT ON snapshot_record
WHEN NOT (
    (NEW.record_kind = 'conceptual_space' AND EXISTS (
        SELECT 1 FROM conceptual_space
        WHERE space_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'family_definition' AND EXISTS (
        SELECT 1 FROM family_definition
        WHERE family_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'family_instance_expression' AND EXISTS (
        SELECT 1 FROM family_instance_expression
        WHERE instance_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'model' AND EXISTS (
        SELECT 1 FROM model
        WHERE model_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'reference' AND EXISTS (
        SELECT 1 FROM "reference"
        WHERE reference_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'source_artifact' AND EXISTS (
        SELECT 1 FROM source_artifact
        WHERE source_artifact_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'model_artifact' AND EXISTS (
        SELECT 1 FROM model_artifact
        WHERE model_artifact_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'derived_artifact' AND EXISTS (
        SELECT 1 FROM derived_artifact
        WHERE derived_artifact_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'algorithm' AND EXISTS (
        SELECT 1 FROM algorithm
        WHERE algorithm_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'computation_environment' AND EXISTS (
        SELECT 1 FROM computation_environment
        WHERE environment_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'computation_run' AND EXISTS (
        SELECT 1 FROM computation_run
        WHERE run_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'knowledge_entry' AND EXISTS (
        SELECT 1 FROM knowledge_entry
        WHERE knowledge_entry_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'knowledge_revision' AND EXISTS (
        SELECT 1 FROM knowledge_revision
        WHERE knowledge_revision_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'knowledge_review' AND EXISTS (
        SELECT 1 FROM knowledge_review
        WHERE knowledge_review_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'assertion' AND EXISTS (
        SELECT 1 FROM assertion
        WHERE assertion_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'evidence' AND EXISTS (
        SELECT 1 FROM evidence
        WHERE evidence_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'assertion_review' AND EXISTS (
        SELECT 1 FROM assertion_review
        WHERE assertion_review_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'editorial_event' AND EXISTS (
        SELECT 1 FROM editorial_event
        WHERE event_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
)
BEGIN
    SELECT RAISE(ABORT, 'snapshot_record_not_resolved');
END;

CREATE TRIGGER snapshot_record_before_finalize
BEFORE INSERT ON snapshot_record
WHEN EXISTS (
    SELECT 1 FROM snapshot
    WHERE snapshot_id = NEW.snapshot_id AND finalized_at IS NOT NULL
)
BEGIN SELECT RAISE(ABORT, 'snapshot_finalized'); END;

CREATE TRIGGER snapshot_knowledge_selection_before_finalize
BEFORE INSERT ON snapshot_knowledge_selection
WHEN EXISTS (
    SELECT 1 FROM snapshot
    WHERE snapshot_id = NEW.snapshot_id AND finalized_at IS NOT NULL
)
BEGIN SELECT RAISE(ABORT, 'snapshot_finalized'); END;

CREATE TRIGGER current_homology_before_finalize
BEFORE INSERT ON current_homology
WHEN EXISTS (
    SELECT 1 FROM snapshot
    WHERE snapshot_id = NEW.snapshot_id AND finalized_at IS NOT NULL
)
BEGIN SELECT RAISE(ABORT, 'snapshot_finalized'); END;

CREATE TRIGGER current_completeness_before_finalize
BEFORE INSERT ON current_completeness
WHEN EXISTS (
    SELECT 1 FROM snapshot
    WHERE snapshot_id = NEW.snapshot_id AND finalized_at IS NOT NULL
)
BEGIN SELECT RAISE(ABORT, 'snapshot_finalized'); END;

CREATE TRIGGER supporting_assertion_before_finalize
BEFORE INSERT ON supporting_assertion
WHEN EXISTS (
    SELECT 1 FROM snapshot
    WHERE snapshot_id = NEW.snapshot_id AND finalized_at IS NOT NULL
)
BEGIN SELECT RAISE(ABORT, 'snapshot_finalized'); END;

CREATE TRIGGER canonical_export_before_finalize
BEFORE INSERT ON canonical_export
WHEN EXISTS (
    SELECT 1 FROM snapshot
    WHERE snapshot_id = NEW.snapshot_id AND finalized_at IS NOT NULL
)
BEGIN SELECT RAISE(ABORT, 'snapshot_finalized'); END;

CREATE TRIGGER snapshot_finalize_once
BEFORE UPDATE ON snapshot
WHEN OLD.finalized_at IS NOT NULL
  OR NEW.finalized_at IS NULL
  OR NEW.snapshot_id <> OLD.snapshot_id
  OR NEW.schema_version <> OLD.schema_version
  OR NEW.selection_policy_id <> OLD.selection_policy_id
  OR NEW.selection_policy_sha256 <> OLD.selection_policy_sha256
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot'); END;

CREATE TRIGGER snapshot_no_delete BEFORE DELETE ON snapshot
BEGIN SELECT RAISE(ABORT, 'immutable_snapshot'); END;

CREATE TRIGGER conceptual_space_u BEFORE UPDATE ON conceptual_space BEGIN SELECT RAISE(ABORT, 'immutable_conceptual_space'); END;
CREATE TRIGGER conceptual_space_d BEFORE DELETE ON conceptual_space BEGIN SELECT RAISE(ABORT, 'immutable_conceptual_space'); END;
CREATE TRIGGER space_name_u BEFORE UPDATE ON space_name BEGIN SELECT RAISE(ABORT, 'immutable_space_name'); END;
CREATE TRIGGER space_name_d BEFORE DELETE ON space_name BEGIN SELECT RAISE(ABORT, 'immutable_space_name'); END;
CREATE TRIGGER family_definition_u BEFORE UPDATE ON family_definition BEGIN SELECT RAISE(ABORT, 'immutable_family_definition'); END;
CREATE TRIGGER family_definition_d BEFORE DELETE ON family_definition BEGIN SELECT RAISE(ABORT, 'immutable_family_definition'); END;
CREATE TRIGGER family_parameter_definition_u BEFORE UPDATE ON family_parameter_definition BEGIN SELECT RAISE(ABORT, 'immutable_family_parameter_definition'); END;
CREATE TRIGGER family_parameter_definition_d BEFORE DELETE ON family_parameter_definition BEGIN SELECT RAISE(ABORT, 'immutable_family_parameter_definition'); END;
CREATE TRIGGER family_instance_expression_u BEFORE UPDATE ON family_instance_expression BEGIN SELECT RAISE(ABORT, 'immutable_family_instance_expression'); END;
CREATE TRIGGER family_instance_expression_d BEFORE DELETE ON family_instance_expression BEGIN SELECT RAISE(ABORT, 'immutable_family_instance_expression'); END;
CREATE TRIGGER family_instance_parameter_u BEFORE UPDATE ON family_instance_parameter BEGIN SELECT RAISE(ABORT, 'immutable_family_instance_parameter'); END;
CREATE TRIGGER family_instance_parameter_d BEFORE DELETE ON family_instance_parameter BEGIN SELECT RAISE(ABORT, 'immutable_family_instance_parameter'); END;
CREATE TRIGGER model_u BEFORE UPDATE ON model BEGIN SELECT RAISE(ABORT, 'immutable_model'); END;
CREATE TRIGGER model_d BEFORE DELETE ON model BEGIN SELECT RAISE(ABORT, 'immutable_model'); END;
CREATE TRIGGER reference_u BEFORE UPDATE ON "reference" BEGIN SELECT RAISE(ABORT, 'immutable_reference'); END;
CREATE TRIGGER reference_d BEFORE DELETE ON "reference" BEGIN SELECT RAISE(ABORT, 'immutable_reference'); END;
CREATE TRIGGER source_artifact_u BEFORE UPDATE ON source_artifact BEGIN SELECT RAISE(ABORT, 'immutable_source_artifact'); END;
CREATE TRIGGER source_artifact_d BEFORE DELETE ON source_artifact BEGIN SELECT RAISE(ABORT, 'immutable_source_artifact'); END;
CREATE TRIGGER model_artifact_u BEFORE UPDATE ON model_artifact BEGIN SELECT RAISE(ABORT, 'immutable_model_artifact'); END;
CREATE TRIGGER model_artifact_d BEFORE DELETE ON model_artifact BEGIN SELECT RAISE(ABORT, 'immutable_model_artifact'); END;
CREATE TRIGGER derived_artifact_u BEFORE UPDATE ON derived_artifact BEGIN SELECT RAISE(ABORT, 'immutable_derived_artifact'); END;
CREATE TRIGGER derived_artifact_d BEFORE DELETE ON derived_artifact BEGIN SELECT RAISE(ABORT, 'immutable_derived_artifact'); END;
CREATE TRIGGER algorithm_u BEFORE UPDATE ON algorithm BEGIN SELECT RAISE(ABORT, 'immutable_algorithm'); END;
CREATE TRIGGER algorithm_d BEFORE DELETE ON algorithm BEGIN SELECT RAISE(ABORT, 'immutable_algorithm'); END;
CREATE TRIGGER computation_environment_u BEFORE UPDATE ON computation_environment BEGIN SELECT RAISE(ABORT, 'immutable_computation_environment'); END;
CREATE TRIGGER computation_environment_d BEFORE DELETE ON computation_environment BEGIN SELECT RAISE(ABORT, 'immutable_computation_environment'); END;
CREATE TRIGGER computation_run_u BEFORE UPDATE ON computation_run BEGIN SELECT RAISE(ABORT, 'immutable_computation_run'); END;
CREATE TRIGGER computation_run_d BEFORE DELETE ON computation_run BEGIN SELECT RAISE(ABORT, 'immutable_computation_run'); END;
CREATE TRIGGER run_input_u BEFORE UPDATE ON run_input BEGIN SELECT RAISE(ABORT, 'immutable_run_input'); END;
CREATE TRIGGER run_input_d BEFORE DELETE ON run_input BEGIN SELECT RAISE(ABORT, 'immutable_run_input'); END;
CREATE TRIGGER run_output_u BEFORE UPDATE ON run_output BEGIN SELECT RAISE(ABORT, 'immutable_run_output'); END;
CREATE TRIGGER run_output_d BEFORE DELETE ON run_output BEGIN SELECT RAISE(ABORT, 'immutable_run_output'); END;
CREATE TRIGGER run_log_u BEFORE UPDATE ON run_log BEGIN SELECT RAISE(ABORT, 'immutable_run_log'); END;
CREATE TRIGGER run_log_d BEFORE DELETE ON run_log BEGIN SELECT RAISE(ABORT, 'immutable_run_log'); END;
CREATE TRIGGER knowledge_entry_u BEFORE UPDATE ON knowledge_entry BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_entry'); END;
CREATE TRIGGER knowledge_entry_d BEFORE DELETE ON knowledge_entry BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_entry'); END;
CREATE TRIGGER knowledge_review_u BEFORE UPDATE ON knowledge_review BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_review'); END;
CREATE TRIGGER knowledge_review_d BEFORE DELETE ON knowledge_review BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_review'); END;
CREATE TRIGGER knowledge_link_u BEFORE UPDATE ON knowledge_link BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_link'); END;
CREATE TRIGGER knowledge_link_d BEFORE DELETE ON knowledge_link BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_link'); END;

CREATE TRIGGER homology_assertion_u BEFORE UPDATE ON homology_assertion BEGIN SELECT RAISE(ABORT, 'immutable_homology_assertion'); END;
CREATE TRIGGER homology_assertion_d BEFORE DELETE ON homology_assertion BEGIN SELECT RAISE(ABORT, 'immutable_homology_assertion'); END;
CREATE TRIGGER completeness_assertion_u BEFORE UPDATE ON completeness_assertion BEGIN SELECT RAISE(ABORT, 'immutable_completeness_assertion'); END;
CREATE TRIGGER completeness_assertion_d BEFORE DELETE ON completeness_assertion BEGIN SELECT RAISE(ABORT, 'immutable_completeness_assertion'); END;
CREATE TRIGGER family_theorem_assertion_u BEFORE UPDATE ON family_theorem_assertion BEGIN SELECT RAISE(ABORT, 'immutable_family_theorem_assertion'); END;
CREATE TRIGGER family_theorem_assertion_d BEFORE DELETE ON family_theorem_assertion BEGIN SELECT RAISE(ABORT, 'immutable_family_theorem_assertion'); END;
CREATE TRIGGER model_relation_assertion_u BEFORE UPDATE ON model_relation_assertion BEGIN SELECT RAISE(ABORT, 'immutable_model_relation_assertion'); END;
CREATE TRIGGER model_relation_assertion_d BEFORE DELETE ON model_relation_assertion BEGIN SELECT RAISE(ABORT, 'immutable_model_relation_assertion'); END;
CREATE TRIGGER model_coverage_assertion_u BEFORE UPDATE ON model_coverage_assertion BEGIN SELECT RAISE(ABORT, 'immutable_model_coverage_assertion'); END;
CREATE TRIGGER model_coverage_assertion_d BEFORE DELETE ON model_coverage_assertion BEGIN SELECT RAISE(ABORT, 'immutable_model_coverage_assertion'); END;
CREATE TRIGGER integer_group_u BEFORE UPDATE ON integer_group BEGIN SELECT RAISE(ABORT, 'immutable_integer_group'); END;
CREATE TRIGGER integer_group_d BEFORE DELETE ON integer_group BEGIN SELECT RAISE(ABORT, 'immutable_integer_group'); END;
CREATE TRIGGER invariant_factor_u BEFORE UPDATE ON invariant_factor BEGIN SELECT RAISE(ABORT, 'immutable_invariant_factor'); END;
CREATE TRIGGER invariant_factor_d BEFORE DELETE ON invariant_factor BEGIN SELECT RAISE(ABORT, 'immutable_invariant_factor'); END;
CREATE TRIGGER field_dimension_u BEFORE UPDATE ON field_dimension BEGIN SELECT RAISE(ABORT, 'immutable_field_dimension'); END;
CREATE TRIGGER field_dimension_d BEFORE DELETE ON field_dimension BEGIN SELECT RAISE(ABORT, 'immutable_field_dimension'); END;
CREATE TRIGGER primary_summand_u BEFORE UPDATE ON primary_summand BEGIN SELECT RAISE(ABORT, 'immutable_primary_summand'); END;
CREATE TRIGGER primary_summand_d BEFORE DELETE ON primary_summand BEGIN SELECT RAISE(ABORT, 'immutable_primary_summand'); END;
CREATE TRIGGER literature_evidence_u BEFORE UPDATE ON literature_evidence BEGIN SELECT RAISE(ABORT, 'immutable_literature_evidence'); END;
CREATE TRIGGER literature_evidence_d BEFORE DELETE ON literature_evidence BEGIN SELECT RAISE(ABORT, 'immutable_literature_evidence'); END;
CREATE TRIGGER computation_evidence_u BEFORE UPDATE ON computation_evidence BEGIN SELECT RAISE(ABORT, 'immutable_computation_evidence'); END;
CREATE TRIGGER computation_evidence_d BEFORE DELETE ON computation_evidence BEGIN SELECT RAISE(ABORT, 'immutable_computation_evidence'); END;
CREATE TRIGGER derivation_evidence_u BEFORE UPDATE ON derivation_evidence BEGIN SELECT RAISE(ABORT, 'immutable_derivation_evidence'); END;
CREATE TRIGGER derivation_evidence_d BEFORE DELETE ON derivation_evidence BEGIN SELECT RAISE(ABORT, 'immutable_derivation_evidence'); END;
CREATE TRIGGER assertion_evidence_u BEFORE UPDATE ON assertion_evidence BEGIN SELECT RAISE(ABORT, 'immutable_assertion_evidence'); END;
CREATE TRIGGER assertion_evidence_d BEFORE DELETE ON assertion_evidence BEGIN SELECT RAISE(ABORT, 'immutable_assertion_evidence'); END;
CREATE TRIGGER assertion_dependency_u BEFORE UPDATE ON assertion_dependency BEGIN SELECT RAISE(ABORT, 'immutable_assertion_dependency'); END;
CREATE TRIGGER assertion_dependency_d BEFORE DELETE ON assertion_dependency BEGIN SELECT RAISE(ABORT, 'immutable_assertion_dependency'); END;
CREATE TRIGGER assertion_review_u BEFORE UPDATE ON assertion_review BEGIN SELECT RAISE(ABORT, 'immutable_assertion_review'); END;
CREATE TRIGGER assertion_review_d BEFORE DELETE ON assertion_review BEGIN SELECT RAISE(ABORT, 'immutable_assertion_review'); END;
CREATE TRIGGER editorial_event_u BEFORE UPDATE ON editorial_event BEGIN SELECT RAISE(ABORT, 'immutable_editorial_event'); END;
CREATE TRIGGER editorial_event_d BEFORE DELETE ON editorial_event BEGIN SELECT RAISE(ABORT, 'immutable_editorial_event'); END;
CREATE TRIGGER editorial_event_effect_u BEFORE UPDATE ON editorial_event_effect BEGIN SELECT RAISE(ABORT, 'immutable_editorial_event_effect'); END;
CREATE TRIGGER editorial_event_effect_d BEFORE DELETE ON editorial_event_effect BEGIN SELECT RAISE(ABORT, 'immutable_editorial_event_effect'); END;
CREATE TRIGGER conflict_set_u BEFORE UPDATE ON conflict_set BEGIN SELECT RAISE(ABORT, 'immutable_conflict_set'); END;
CREATE TRIGGER conflict_set_d BEFORE DELETE ON conflict_set BEGIN SELECT RAISE(ABORT, 'immutable_conflict_set'); END;
CREATE TRIGGER conflict_ledger_effect_u BEFORE UPDATE ON conflict_ledger_effect BEGIN SELECT RAISE(ABORT, 'immutable_conflict_ledger_effect'); END;
CREATE TRIGGER conflict_ledger_effect_d BEFORE DELETE ON conflict_ledger_effect BEGIN SELECT RAISE(ABORT, 'immutable_conflict_ledger_effect'); END;
CREATE TRIGGER schema_migration_u BEFORE UPDATE ON schema_migration BEGIN SELECT RAISE(ABORT, 'immutable_schema_migration'); END;
CREATE TRIGGER schema_migration_d BEFORE DELETE ON schema_migration BEGIN SELECT RAISE(ABORT, 'immutable_schema_migration'); END;

CREATE TRIGGER current_completeness_u BEFORE UPDATE ON current_completeness BEGIN SELECT RAISE(ABORT, 'immutable_current_completeness'); END;
CREATE TRIGGER current_completeness_d BEFORE DELETE ON current_completeness BEGIN SELECT RAISE(ABORT, 'immutable_current_completeness'); END;
CREATE TRIGGER supporting_assertion_u BEFORE UPDATE ON supporting_assertion BEGIN SELECT RAISE(ABORT, 'immutable_supporting_assertion'); END;
CREATE TRIGGER supporting_assertion_d BEFORE DELETE ON supporting_assertion BEGIN SELECT RAISE(ABORT, 'immutable_supporting_assertion'); END;
CREATE TRIGGER canonical_export_u BEFORE UPDATE ON canonical_export BEGIN SELECT RAISE(ABORT, 'immutable_canonical_export'); END;
CREATE TRIGGER canonical_export_d BEFORE DELETE ON canonical_export BEGIN SELECT RAISE(ABORT, 'immutable_canonical_export'); END;
