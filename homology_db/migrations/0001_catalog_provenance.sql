PRAGMA foreign_keys = ON;

CREATE TABLE schema_migration(
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conceptual_space(
    space_id TEXT PRIMARY KEY,
    permanent_label TEXT NOT NULL UNIQUE,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE space_name(
    name_id TEXT PRIMARY KEY,
    space_id TEXT NOT NULL REFERENCES conceptual_space(space_id),
    normalized_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    name_kind TEXT NOT NULL CHECK(name_kind IN ('label', 'alias', 'family_expression')),
    identity_assertion_id TEXT,
    record_sha256 TEXT NOT NULL,
    UNIQUE(space_id, normalized_name)
);
CREATE INDEX space_name_lookup_idx ON space_name(normalized_name, space_id);

CREATE TABLE family_definition(
    family_id TEXT PRIMARY KEY,
    permanent_label TEXT NOT NULL UNIQUE,
    theorem_assertion_id TEXT,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE family_parameter_definition(
    parameter_id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL REFERENCES family_definition(family_id),
    parameter_name TEXT NOT NULL,
    parameter_type TEXT NOT NULL CHECK(parameter_type IN ('natural', 'integer', 'prime', 'enum')),
    domain_json TEXT NOT NULL,
    position INTEGER NOT NULL CHECK(position >= 0),
    UNIQUE(family_id, parameter_name),
    UNIQUE(family_id, position)
);

CREATE TABLE family_instance_expression(
    instance_id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL REFERENCES family_definition(family_id),
    display_label TEXT NOT NULL,
    denoted_space_id TEXT REFERENCES conceptual_space(space_id),
    denotation_assertion_id TEXT,
    materialization_state TEXT NOT NULL CHECK(materialization_state IN (
        'materialized', 'outside_materialized_range', 'invalid_parameter'
    )),
    record_sha256 TEXT NOT NULL
);

CREATE TABLE family_instance_parameter(
    instance_id TEXT NOT NULL REFERENCES family_instance_expression(instance_id),
    parameter_id TEXT NOT NULL REFERENCES family_parameter_definition(parameter_id),
    value_json TEXT NOT NULL,
    PRIMARY KEY(instance_id, parameter_id)
);

CREATE TABLE model(
    model_id TEXT PRIMARY KEY,
    model_kind TEXT NOT NULL,
    dimension INTEGER CHECK(dimension IS NULL OR dimension >= 0),
    qualification_state TEXT NOT NULL CHECK(qualification_state IN (
        'candidate', 'qualified', 'rejected', 'not_qualified'
    )),
    record_sha256 TEXT NOT NULL
);

CREATE TABLE "reference"(
    reference_id TEXT PRIMARY KEY,
    citation_text TEXT NOT NULL,
    stable_locator TEXT NOT NULL,
    revision TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE source_artifact(
    source_artifact_id TEXT PRIMARY KEY,
    reference_id TEXT REFERENCES "reference"(reference_id),
    media_type TEXT NOT NULL,
    content_sha256 TEXT NOT NULL UNIQUE,
    byte_length INTEGER NOT NULL CHECK(byte_length >= 0),
    record_sha256 TEXT NOT NULL
);

CREATE TABLE model_artifact(
    model_artifact_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES model(model_id),
    source_artifact_id TEXT REFERENCES source_artifact(source_artifact_id),
    format TEXT NOT NULL,
    content_sha256 TEXT NOT NULL UNIQUE,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE derived_artifact(
    derived_artifact_id TEXT PRIMARY KEY,
    model_id TEXT REFERENCES model(model_id),
    artifact_kind TEXT NOT NULL,
    media_type TEXT NOT NULL,
    content_sha256 TEXT NOT NULL UNIQUE,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE algorithm(
    algorithm_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE computation_environment(
    environment_id TEXT PRIMARY KEY,
    environment_json TEXT NOT NULL,
    environment_sha256 TEXT NOT NULL UNIQUE,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE computation_run(
    run_id TEXT PRIMARY KEY,
    algorithm_id TEXT NOT NULL REFERENCES algorithm(algorithm_id),
    environment_id TEXT NOT NULL REFERENCES computation_environment(environment_id),
    started_at TEXT NOT NULL,
    finished_at TEXT,
    exit_state TEXT NOT NULL CHECK(exit_state IN ('running', 'succeeded', 'failed')),
    parameters_json TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE run_input(
    run_id TEXT NOT NULL REFERENCES computation_run(run_id),
    input_kind TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(run_id, input_kind, position)
);

CREATE TABLE run_output(
    run_id TEXT NOT NULL REFERENCES computation_run(run_id),
    derived_artifact_id TEXT NOT NULL REFERENCES derived_artifact(derived_artifact_id),
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(run_id, position)
);

CREATE TABLE run_log(
    run_id TEXT NOT NULL REFERENCES computation_run(run_id),
    stream_name TEXT NOT NULL CHECK(stream_name IN ('stdout', 'stderr', 'structured')),
    content_sha256 TEXT NOT NULL,
    media_type TEXT NOT NULL,
    PRIMARY KEY(run_id, stream_name)
);

CREATE TABLE knowledge_entry(
    knowledge_entry_id TEXT PRIMARY KEY,
    canonical_term TEXT NOT NULL,
    entry_kind TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE knowledge_revision(
    knowledge_revision_id TEXT PRIMARY KEY,
    knowledge_entry_id TEXT NOT NULL REFERENCES knowledge_entry(knowledge_entry_id),
    revision_number INTEGER NOT NULL CHECK(revision_number > 0),
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    format_version TEXT NOT NULL,
    author TEXT NOT NULL,
    created_at TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL,
    UNIQUE(knowledge_entry_id, revision_number),
    UNIQUE(knowledge_entry_id, content_sha256)
);

CREATE TABLE knowledge_review(
    knowledge_review_id TEXT PRIMARY KEY,
    knowledge_revision_id TEXT NOT NULL REFERENCES knowledge_revision(knowledge_revision_id),
    reviewer TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('accept', 'reject', 'needs_evidence')),
    reviewed_at TEXT NOT NULL,
    note TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE knowledge_link(
    knowledge_link_id TEXT PRIMARY KEY,
    from_entry_id TEXT NOT NULL REFERENCES knowledge_entry(knowledge_entry_id),
    target_kind TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_kind TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);
