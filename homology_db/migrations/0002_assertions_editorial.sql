PRAGMA foreign_keys = ON;

CREATE TABLE assertion(
    assertion_id TEXT PRIMARY KEY,
    assertion_kind TEXT NOT NULL,
    subject_kind TEXT NOT NULL CHECK(subject_kind IN ('conceptual_space', 'model', 'family', 'map')),
    subject_id TEXT NOT NULL,
    slot_key TEXT NOT NULL,
    knowledge_state TEXT NOT NULL CHECK(knowledge_state IN (
        'exact', 'bounded', 'conjectural', 'unknown', 'not_computed', 'not_applicable'
    )),
    claim_fingerprint TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);
CREATE INDEX assertion_slot_idx ON assertion(subject_kind, subject_id, slot_key, claim_fingerprint);

CREATE TABLE homology_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES assertion(assertion_id),
    theory TEXT NOT NULL,
    coefficient_system TEXT NOT NULL,
    convention_id TEXT NOT NULL,
    reduced INTEGER NOT NULL CHECK(reduced IN (0, 1)),
    degree INTEGER NOT NULL,
    derivation_kind TEXT NOT NULL CHECK(derivation_kind IN (
        'literature', 'owned_computation', 'derived_specialization', 'promotion'
    ))
);
CREATE INDEX homology_slot_idx ON homology_assertion(
    theory, coefficient_system, convention_id, reduced, degree, assertion_id
);

CREATE TABLE completeness_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES assertion(assertion_id),
    region_json TEXT NOT NULL,
    completeness_kind TEXT NOT NULL CHECK(completeness_kind IN (
        'exact_coverage', 'vanishing', 'materialized_family_range', 'model_coverage'
    ))
);

CREATE TABLE family_theorem_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES assertion(assertion_id),
    family_id TEXT NOT NULL REFERENCES family_definition(family_id),
    parameter_domain_json TEXT NOT NULL,
    formula_json TEXT NOT NULL
);

CREATE TABLE model_relation_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES assertion(assertion_id),
    source_model_id TEXT NOT NULL REFERENCES model(model_id),
    target_kind TEXT NOT NULL CHECK(target_kind IN ('model', 'conceptual_space')),
    target_id TEXT NOT NULL,
    relation_kind TEXT NOT NULL,
    equivalence_level TEXT NOT NULL
);

CREATE TABLE model_coverage_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES assertion(assertion_id),
    space_id TEXT NOT NULL REFERENCES conceptual_space(space_id),
    coverage_state TEXT NOT NULL CHECK(coverage_state IN (
        'qualified', 'model_not_qualified', 'unresolved'
    )),
    model_id TEXT REFERENCES model(model_id)
);

CREATE TABLE integer_group(
    assertion_id TEXT PRIMARY KEY REFERENCES homology_assertion(assertion_id),
    free_rank INTEGER NOT NULL CHECK(free_rank >= 0)
);

CREATE TABLE invariant_factor(
    assertion_id TEXT NOT NULL REFERENCES integer_group(assertion_id),
    position INTEGER NOT NULL CHECK(position >= 0),
    order_text TEXT NOT NULL CHECK(length(order_text) > 0),
    PRIMARY KEY(assertion_id, position)
);

CREATE TABLE field_dimension(
    assertion_id TEXT PRIMARY KEY REFERENCES homology_assertion(assertion_id),
    characteristic INTEGER NOT NULL CHECK(characteristic > 1),
    dimension INTEGER NOT NULL CHECK(dimension >= 0)
);

CREATE TRIGGER integer_group_requires_exact_assertion
BEFORE INSERT ON integer_group
WHEN NOT EXISTS (
    SELECT 1 FROM assertion
    WHERE assertion_id = NEW.assertion_id AND knowledge_state = 'exact'
)
BEGIN
    SELECT RAISE(ABORT, 'group_value_requires_exact_assertion');
END;

CREATE TRIGGER field_dimension_requires_exact_assertion
BEFORE INSERT ON field_dimension
WHEN NOT EXISTS (
    SELECT 1 FROM assertion
    WHERE assertion_id = NEW.assertion_id AND knowledge_state = 'exact'
)
BEGIN
    SELECT RAISE(ABORT, 'group_value_requires_exact_assertion');
END;

CREATE TABLE primary_summand(
    assertion_id TEXT NOT NULL REFERENCES integer_group(assertion_id),
    prime INTEGER NOT NULL CHECK(prime > 1),
    exponent INTEGER NOT NULL CHECK(exponent > 0),
    multiplicity INTEGER NOT NULL CHECK(multiplicity > 0),
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(assertion_id, prime, exponent, position)
);
CREATE INDEX primary_summand_query_idx ON primary_summand(prime, exponent, multiplicity, assertion_id);

CREATE TABLE evidence(
    evidence_id TEXT PRIMARY KEY,
    evidence_kind TEXT NOT NULL CHECK(evidence_kind IN ('literature', 'computation', 'derivation')),
    record_sha256 TEXT NOT NULL
);

CREATE TABLE literature_evidence(
    evidence_id TEXT PRIMARY KEY REFERENCES evidence(evidence_id),
    reference_id TEXT NOT NULL REFERENCES "reference"(reference_id),
    pinpoint TEXT NOT NULL
);

CREATE TABLE computation_evidence(
    evidence_id TEXT PRIMARY KEY REFERENCES evidence(evidence_id),
    run_id TEXT NOT NULL REFERENCES computation_run(run_id)
);

CREATE TABLE derivation_evidence(
    evidence_id TEXT PRIMARY KEY REFERENCES evidence(evidence_id),
    rule_id TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    rule_source_sha256 TEXT NOT NULL
);

CREATE TABLE assertion_evidence(
    assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
    role TEXT NOT NULL CHECK(role IN ('supports', 'computes', 'derives')),
    PRIMARY KEY(assertion_id, evidence_id, role)
);

CREATE TABLE assertion_dependency(
    dependency_id TEXT PRIMARY KEY,
    source_assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    target_assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    relation_kind TEXT NOT NULL CHECK(relation_kind IN (
        'implication', 'specialization', 'promotion', 'corroboration'
    )),
    hypotheses_json TEXT NOT NULL,
    review_id TEXT NOT NULL,
    record_sha256 TEXT NOT NULL,
    CHECK(source_assertion_id <> target_assertion_id)
);

CREATE TABLE assertion_review(
    assertion_review_id TEXT PRIMARY KEY,
    assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    reviewer TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('accept', 'reject', 'needs_evidence')),
    reviewed_at TEXT NOT NULL,
    note TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE editorial_event(
    event_id TEXT PRIMARY KEY,
    event_kind TEXT NOT NULL CHECK(event_kind IN (
        'admit', 'supersede', 'retract', 'declare_conflict', 'resolve_conflict'
    )),
    actor TEXT NOT NULL,
    reason TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    expected_revision INTEGER NOT NULL CHECK(expected_revision >= 0),
    record_sha256 TEXT NOT NULL
);

CREATE TABLE editorial_event_effect(
    event_id TEXT NOT NULL REFERENCES editorial_event(event_id),
    assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    effect_kind TEXT NOT NULL CHECK(effect_kind IN ('admit', 'retire', 'conflict_add', 'conflict_remove')),
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(event_id, position)
);

CREATE TABLE conflict_set(
    conflict_set_id TEXT PRIMARY KEY,
    slot_key TEXT NOT NULL,
    declared_event_id TEXT NOT NULL REFERENCES editorial_event(event_id),
    resolved_event_id TEXT REFERENCES editorial_event(event_id),
    record_sha256 TEXT NOT NULL
);

CREATE TABLE conflict_member(
    conflict_set_id TEXT NOT NULL REFERENCES conflict_set(conflict_set_id),
    assertion_id TEXT NOT NULL REFERENCES assertion(assertion_id),
    PRIMARY KEY(conflict_set_id, assertion_id)
);

CREATE TRIGGER assertion_no_update BEFORE UPDATE ON assertion
BEGIN SELECT RAISE(ABORT, 'immutable_assertion'); END;
CREATE TRIGGER assertion_no_delete BEFORE DELETE ON assertion
BEGIN SELECT RAISE(ABORT, 'immutable_assertion'); END;
CREATE TRIGGER evidence_no_update BEFORE UPDATE ON evidence
BEGIN SELECT RAISE(ABORT, 'immutable_evidence'); END;
CREATE TRIGGER evidence_no_delete BEFORE DELETE ON evidence
BEGIN SELECT RAISE(ABORT, 'immutable_evidence'); END;
CREATE TRIGGER knowledge_revision_no_update BEFORE UPDATE ON knowledge_revision
BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_revision'); END;
CREATE TRIGGER knowledge_revision_no_delete BEFORE DELETE ON knowledge_revision
BEGIN SELECT RAISE(ABORT, 'immutable_knowledge_revision'); END;
