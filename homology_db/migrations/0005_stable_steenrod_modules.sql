PRAGMA foreign_keys = ON;

CREATE TABLE conceptual_spectrum(
    spectrum_id TEXT PRIMARY KEY,
    permanent_label TEXT NOT NULL UNIQUE,
    record_sha256 TEXT NOT NULL
);

CREATE TABLE spectrum_name(
    name_id TEXT PRIMARY KEY,
    spectrum_id TEXT NOT NULL REFERENCES conceptual_spectrum(spectrum_id),
    normalized_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    name_kind TEXT NOT NULL CHECK(name_kind IN ('label', 'alias')),
    identity_assertion_id TEXT,
    record_sha256 TEXT NOT NULL,
    UNIQUE(spectrum_id, normalized_name)
);
CREATE INDEX spectrum_name_lookup_idx ON spectrum_name(normalized_name, spectrum_id);

-- Rebuild the tagged assertion identity without rewriting migration 0002.
-- The v5 runner disables foreign-key rename propagation while this migration
-- runs, so existing assertion subtype references continue to name assertion.
DROP TRIGGER assertion_no_update;
DROP TRIGGER assertion_no_delete;
DROP TRIGGER assertion_subject_must_exist;
ALTER TABLE assertion RENAME TO assertion_v4;
CREATE TABLE assertion(
    assertion_id TEXT PRIMARY KEY,
    assertion_kind TEXT NOT NULL,
    subject_kind TEXT NOT NULL CHECK(subject_kind IN (
        'conceptual_space', 'conceptual_spectrum', 'model', 'family', 'map'
    )),
    subject_id TEXT NOT NULL,
    slot_key TEXT NOT NULL,
    knowledge_state TEXT NOT NULL CHECK(knowledge_state IN (
        'exact', 'bounded', 'conjectural', 'unknown', 'not_computed', 'not_applicable'
    )),
    claim_fingerprint TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL
);
INSERT INTO assertion SELECT * FROM assertion_v4;
DROP TABLE assertion_v4;
CREATE INDEX assertion_slot_idx
ON assertion(subject_kind, subject_id, slot_key, claim_fingerprint);
CREATE INDEX assertion_evidence_assertion_idx
ON assertion_evidence(assertion_id, evidence_id);
CREATE INDEX assertion_review_assertion_idx
ON assertion_review(assertion_id, verdict, assertion_review_id);
CREATE INDEX editorial_event_effect_assertion_idx
ON editorial_event_effect(assertion_id, effect_kind, event_id);

CREATE TRIGGER assertion_subject_must_exist
BEFORE INSERT ON assertion
WHEN
    (NEW.subject_kind = 'conceptual_space' AND NOT EXISTS (
        SELECT 1 FROM conceptual_space WHERE space_id = NEW.subject_id
    ))
    OR (NEW.subject_kind = 'conceptual_spectrum' AND NOT EXISTS (
        SELECT 1 FROM conceptual_spectrum WHERE spectrum_id = NEW.subject_id
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

CREATE TRIGGER assertion_no_update BEFORE UPDATE ON assertion
BEGIN SELECT RAISE(ABORT, 'immutable_assertion'); END;
CREATE TRIGGER assertion_no_delete BEFORE DELETE ON assertion
BEGIN SELECT RAISE(ABORT, 'immutable_assertion'); END;

CREATE TABLE steenrod_module(
    module_id TEXT PRIMARY KEY,
    subject_kind TEXT NOT NULL CHECK(subject_kind IN ('conceptual_spectrum', 'conceptual_space')),
    subject_id TEXT NOT NULL,
    module_kind TEXT NOT NULL CHECK(module_kind IN ('finite_basis', 'profile')),
    module_category TEXT NOT NULL CHECK(module_category IN ('stable', 'unstable')),
    coefficient_prime INTEGER NOT NULL CHECK(coefficient_prime = 2),
    reduced INTEGER NOT NULL CHECK(reduced IN (0, 1)),
    grading_convention TEXT NOT NULL,
    suspension_shift INTEGER NOT NULL,
    format_version TEXT NOT NULL CHECK(format_version = 'homology-db.steenrod-module/1'),
    module_version TEXT NOT NULL,
    basis_version TEXT,
    profile_json TEXT,
    record_sha256 TEXT NOT NULL,
    CHECK(
        (module_kind = 'finite_basis' AND basis_version IS NOT NULL AND profile_json IS NULL)
        OR (module_kind = 'profile' AND basis_version IS NULL AND profile_json IS NOT NULL)
    ),
    CHECK(profile_json IS NULL OR json_valid(profile_json)),
    CHECK(
        (module_category = 'stable' AND subject_kind = 'conceptual_spectrum')
        OR (module_category = 'unstable' AND subject_kind = 'conceptual_space')
    ),
    UNIQUE(subject_kind, subject_id, module_version)
);

CREATE TRIGGER steenrod_module_subject_must_exist
BEFORE INSERT ON steenrod_module
WHEN NOT (
    (NEW.subject_kind = 'conceptual_spectrum' AND EXISTS (
        SELECT 1 FROM conceptual_spectrum WHERE spectrum_id = NEW.subject_id
    ))
    OR (NEW.subject_kind = 'conceptual_space' AND EXISTS (
        SELECT 1 FROM conceptual_space WHERE space_id = NEW.subject_id
    ))
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_module_subject_not_found');
END;

-- Imported-module provenance is both typed and queryable.  The ordinary
-- derivation subtype identifies the normalizer; this subtype retains the
-- exact upstream locator and the normalized module identity it produced.
CREATE TABLE steenrod_import_evidence(
    evidence_id TEXT PRIMARY KEY REFERENCES derivation_evidence(evidence_id),
    source_snapshot TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    normalized_module_sha256 TEXT NOT NULL
);

CREATE TRIGGER steenrod_import_evidence_before_snapshot_use
BEFORE INSERT ON steenrod_import_evidence
WHEN EXISTS (
    SELECT 1 FROM snapshot_record
    WHERE record_kind = 'evidence' AND record_id = NEW.evidence_id
)
BEGIN
    SELECT RAISE(ABORT, 'sealed_snapshot_evidence');
END;

CREATE TABLE steenrod_module_evidence(
    module_id TEXT NOT NULL REFERENCES steenrod_module(module_id),
    evidence_id TEXT NOT NULL REFERENCES steenrod_import_evidence(evidence_id),
    role TEXT NOT NULL CHECK(role IN ('supports', 'derives')),
    PRIMARY KEY(module_id, evidence_id, role)
);

CREATE TRIGGER steenrod_module_evidence_identity_must_match
BEFORE INSERT ON steenrod_module_evidence
WHEN NOT EXISTS (
    SELECT 1
    FROM steenrod_module module
    JOIN evidence item
      ON item.evidence_id = NEW.evidence_id
     AND item.evidence_kind = 'derivation'
    JOIN derivation_evidence derivation USING(evidence_id)
    JOIN steenrod_import_evidence imported USING(evidence_id)
    WHERE module.module_id = NEW.module_id
      AND imported.normalized_module_sha256 = module.record_sha256
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_module_evidence_identity_mismatch');
END;

CREATE TRIGGER steenrod_module_evidence_before_parent_use
BEFORE INSERT ON steenrod_module_evidence
WHEN
    EXISTS (
        SELECT 1 FROM snapshot_record
        WHERE record_kind = 'steenrod_module' AND record_id = NEW.module_id
    )
    OR EXISTS (
        SELECT 1 FROM steenrod_module_editorial_effect
        WHERE module_id = NEW.module_id
    )
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_module_evidence');
END;

CREATE TABLE steenrod_module_editorial_effect(
    event_id TEXT NOT NULL REFERENCES editorial_event(event_id),
    module_id TEXT NOT NULL REFERENCES steenrod_module(module_id),
    effect_kind TEXT NOT NULL CHECK(effect_kind IN ('admit', 'retire')),
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(event_id, module_id),
    UNIQUE(event_id, position)
);

CREATE TRIGGER steenrod_module_editorial_effect_kind_must_match
BEFORE INSERT ON steenrod_module_editorial_effect
WHEN NOT EXISTS (
    SELECT 1
    FROM editorial_event event
    WHERE event.event_id = NEW.event_id
      AND (
          (NEW.effect_kind = 'admit' AND event.event_kind = 'admit')
          OR (
              NEW.effect_kind = 'retire'
              AND event.event_kind IN ('supersede', 'retract')
          )
      )
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_module_editorial_effect_kind_mismatch');
END;

CREATE TRIGGER steenrod_module_editorial_effect_before_snapshot_use
BEFORE INSERT ON steenrod_module_editorial_effect
WHEN EXISTS (
    SELECT 1 FROM snapshot_record
    WHERE record_kind = 'editorial_event' AND record_id = NEW.event_id
)
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_module_editorial_effect');
END;

CREATE TABLE steenrod_basis_element(
    basis_element_id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL REFERENCES steenrod_module(module_id),
    basis_key TEXT NOT NULL,
    display_name TEXT NOT NULL,
    degree INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK(position >= 0),
    degree_ordinal INTEGER NOT NULL CHECK(degree_ordinal >= 0),
    record_sha256 TEXT NOT NULL,
    UNIQUE(module_id, basis_element_id),
    UNIQUE(module_id, basis_key),
    UNIQUE(module_id, position),
    UNIQUE(module_id, degree, degree_ordinal)
);
CREATE INDEX steenrod_basis_degree_idx
ON steenrod_basis_element(module_id, degree, degree_ordinal);

CREATE TRIGGER steenrod_basis_requires_finite_module
BEFORE INSERT ON steenrod_basis_element
WHEN NOT EXISTS (
    SELECT 1 FROM steenrod_module
    WHERE module_id = NEW.module_id AND module_kind = 'finite_basis'
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_basis_requires_finite_module');
END;

CREATE TRIGGER steenrod_basis_canonical_order
BEFORE INSERT ON steenrod_basis_element
WHEN
    NEW.position <> (
        SELECT COUNT(*) FROM steenrod_basis_element
        WHERE module_id = NEW.module_id
    )
    OR NEW.degree_ordinal <> (
        SELECT COUNT(*) FROM steenrod_basis_element
        WHERE module_id = NEW.module_id AND degree = NEW.degree
    )
    OR EXISTS (
        SELECT 1 FROM steenrod_basis_element existing
        WHERE existing.module_id = NEW.module_id
          AND (
              existing.degree > NEW.degree
              OR (
                  existing.degree = NEW.degree
                  AND existing.degree_ordinal >= NEW.degree_ordinal
              )
          )
    )
BEGIN
    SELECT RAISE(ABORT, 'steenrod_basis_not_canonically_ordered');
END;

CREATE TRIGGER steenrod_basis_before_module_use
BEFORE INSERT ON steenrod_basis_element
WHEN
    EXISTS (
        SELECT 1 FROM snapshot_record
        WHERE record_kind = 'steenrod_module' AND record_id = NEW.module_id
    )
    OR EXISTS (
        SELECT 1 FROM steenrod_action_assertion
        WHERE module_id = NEW.module_id
    )
    OR EXISTS (
        SELECT 1 FROM steenrod_action_completeness_assertion
        WHERE module_id = NEW.module_id
    )
    OR EXISTS (
        SELECT 1 FROM steenrod_module_editorial_effect
        WHERE module_id = NEW.module_id
    )
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_module_basis');
END;

CREATE TABLE steenrod_action_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES assertion(assertion_id),
    module_id TEXT NOT NULL,
    source_basis_element_id TEXT NOT NULL,
    operation_degree INTEGER NOT NULL CHECK(
        operation_degree > 0
        AND (operation_degree & (operation_degree - 1)) = 0
    ),
    UNIQUE(assertion_id, module_id),
    FOREIGN KEY(module_id, source_basis_element_id)
        REFERENCES steenrod_basis_element(module_id, basis_element_id)
);
CREATE INDEX steenrod_action_slot_idx
ON steenrod_action_assertion(module_id, source_basis_element_id, operation_degree, assertion_id);

CREATE TRIGGER steenrod_action_assertion_before_parent_use
BEFORE INSERT ON steenrod_action_assertion
WHEN
    EXISTS (
        SELECT 1 FROM assertion_review
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM editorial_event_effect
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM snapshot_record
        WHERE record_kind = 'assertion' AND record_id = NEW.assertion_id
    )
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_action_assertion');
END;

CREATE TRIGGER steenrod_action_assertion_subject_must_match
BEFORE INSERT ON steenrod_action_assertion
WHEN NOT EXISTS (
    SELECT 1
    FROM assertion claim
    JOIN steenrod_module module
      ON module.module_id = NEW.module_id
     AND module.subject_kind = claim.subject_kind
     AND module.subject_id = claim.subject_id
    WHERE claim.assertion_id = NEW.assertion_id
      AND claim.assertion_kind = 'steenrod_action'
      AND claim.slot_key = (
          NEW.module_id || '|' || NEW.source_basis_element_id || '|Sq'
          || CAST(NEW.operation_degree AS TEXT)
      )
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_action_assertion_subject_mismatch');
END;

CREATE TABLE steenrod_action_term(
    assertion_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    target_basis_element_id TEXT NOT NULL,
    position INTEGER NOT NULL CHECK(position >= 0),
    PRIMARY KEY(assertion_id, position),
    UNIQUE(assertion_id, target_basis_element_id),
    FOREIGN KEY(assertion_id, module_id)
        REFERENCES steenrod_action_assertion(assertion_id, module_id),
    FOREIGN KEY(module_id, target_basis_element_id)
        REFERENCES steenrod_basis_element(module_id, basis_element_id)
);

CREATE TRIGGER steenrod_action_term_requires_exact_assertion
BEFORE INSERT ON steenrod_action_term
WHEN NOT EXISTS (
    SELECT 1 FROM assertion
    WHERE assertion_id = NEW.assertion_id AND knowledge_state = 'exact'
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_action_terms_require_exact_assertion');
END;

CREATE TRIGGER steenrod_action_term_order_must_be_canonical
BEFORE INSERT ON steenrod_action_term
WHEN
    NEW.position <> (
        SELECT COUNT(*)
        FROM steenrod_action_term
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1
        FROM steenrod_action_term existing
        JOIN steenrod_basis_element existing_target
          ON existing_target.module_id = existing.module_id
         AND existing_target.basis_element_id = existing.target_basis_element_id
        JOIN steenrod_basis_element new_target
          ON new_target.module_id = NEW.module_id
         AND new_target.basis_element_id = NEW.target_basis_element_id
        WHERE existing.assertion_id = NEW.assertion_id
          AND existing_target.position >= new_target.position
    )
BEGIN
    SELECT RAISE(ABORT, 'steenrod_action_terms_not_canonical');
END;

CREATE TRIGGER steenrod_action_term_before_assertion_use
BEFORE INSERT ON steenrod_action_term
WHEN
    EXISTS (
        SELECT 1 FROM assertion_review
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM editorial_event_effect
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM snapshot_record
        WHERE record_kind = 'assertion' AND record_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM current_steenrod_action
        WHERE selected_assertion_id = NEW.assertion_id
    )
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_action_assertion');
END;

CREATE TRIGGER steenrod_action_term_degree_must_match
BEFORE INSERT ON steenrod_action_term
WHEN EXISTS (
    SELECT 1
    FROM steenrod_action_assertion action
    JOIN steenrod_basis_element source
      ON source.module_id = action.module_id
     AND source.basis_element_id = action.source_basis_element_id
    JOIN steenrod_basis_element target
      ON target.module_id = NEW.module_id
     AND target.basis_element_id = NEW.target_basis_element_id
    WHERE action.assertion_id = NEW.assertion_id
      AND action.module_id = NEW.module_id
      AND target.degree <> source.degree + action.operation_degree
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_action_target_degree_mismatch');
END;

CREATE TRIGGER unstable_steenrod_action_must_vanish
BEFORE INSERT ON steenrod_action_term
WHEN EXISTS (
    SELECT 1
    FROM steenrod_action_assertion action
    JOIN steenrod_module module USING(module_id)
    JOIN steenrod_basis_element source
      ON source.module_id = action.module_id
     AND source.basis_element_id = action.source_basis_element_id
    WHERE action.assertion_id = NEW.assertion_id
      AND module.module_category = 'unstable'
      AND action.operation_degree > source.degree
)
BEGIN
    SELECT RAISE(ABORT, 'unstable_steenrod_action_must_vanish');
END;

DROP TRIGGER completeness_assertion_u;
DROP TRIGGER completeness_assertion_d;
ALTER TABLE completeness_assertion RENAME TO completeness_assertion_v4;
CREATE TABLE completeness_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES assertion(assertion_id),
    region_json TEXT NOT NULL CHECK(json_valid(region_json)),
    completeness_kind TEXT NOT NULL CHECK(completeness_kind IN (
        'exact_coverage', 'vanishing', 'materialized_family_range',
        'model_coverage', 'steenrod_action_coverage'
    ))
);
INSERT INTO completeness_assertion SELECT * FROM completeness_assertion_v4;
DROP TABLE completeness_assertion_v4;
CREATE TRIGGER completeness_assertion_u BEFORE UPDATE ON completeness_assertion
BEGIN SELECT RAISE(ABORT, 'immutable_completeness_assertion'); END;
CREATE TRIGGER completeness_assertion_d BEFORE DELETE ON completeness_assertion
BEGIN SELECT RAISE(ABORT, 'immutable_completeness_assertion'); END;

CREATE TABLE steenrod_action_completeness_assertion(
    assertion_id TEXT PRIMARY KEY REFERENCES completeness_assertion(assertion_id),
    module_id TEXT NOT NULL REFERENCES steenrod_module(module_id),
    source_position_start INTEGER NOT NULL CHECK(source_position_start >= 0),
    source_position_end INTEGER NOT NULL CHECK(source_position_end >= source_position_start),
    maximum_operation_degree INTEGER NOT NULL CHECK(
        maximum_operation_degree > 0
        AND (maximum_operation_degree & (maximum_operation_degree - 1)) = 0
    )
);

CREATE TRIGGER steenrod_completeness_before_parent_use
BEFORE INSERT ON steenrod_action_completeness_assertion
WHEN
    EXISTS (
        SELECT 1 FROM assertion_review
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM editorial_event_effect
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM snapshot_record
        WHERE record_kind = 'assertion' AND record_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM current_completeness
        WHERE assertion_id = NEW.assertion_id
    )
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_completeness_assertion');
END;

CREATE TRIGGER steenrod_completeness_requires_exact_assertion
BEFORE INSERT ON steenrod_action_completeness_assertion
WHEN NOT EXISTS (
    SELECT 1
    FROM assertion claim
    JOIN completeness_assertion completeness USING(assertion_id)
    JOIN steenrod_module module
      ON module.module_id = NEW.module_id
     AND module.subject_kind = claim.subject_kind
     AND module.subject_id = claim.subject_id
    WHERE claim.assertion_id = NEW.assertion_id
      AND claim.assertion_kind = 'steenrod_action_completeness'
      AND claim.knowledge_state = 'exact'
      AND completeness.completeness_kind = 'steenrod_action_coverage'
      AND json_type(completeness.region_json) = 'object'
      AND (
          SELECT COUNT(*) FROM json_each(completeness.region_json)
      ) = 2
      AND json_type(completeness.region_json, '$.basis_positions') = 'array'
      AND json_array_length(
          completeness.region_json, '$.basis_positions'
      ) = 2
      AND json_type(
          completeness.region_json, '$.basis_positions[0]'
      ) = 'integer'
      AND json_extract(
          completeness.region_json, '$.basis_positions[0]'
      ) = NEW.source_position_start
      AND json_type(
          completeness.region_json, '$.basis_positions[1]'
      ) = 'integer'
      AND json_extract(
          completeness.region_json, '$.basis_positions[1]'
      ) = NEW.source_position_end
      AND json_type(
          completeness.region_json, '$.maximum_operation_degree'
      ) = 'integer'
      AND json_extract(
          completeness.region_json, '$.maximum_operation_degree'
      ) = NEW.maximum_operation_degree
      AND module.module_kind = 'finite_basis'
      AND EXISTS (
          SELECT 1 FROM steenrod_basis_element
          WHERE module_id = NEW.module_id
            AND position = NEW.source_position_start
      )
      AND EXISTS (
          SELECT 1 FROM steenrod_basis_element
          WHERE module_id = NEW.module_id
            AND position = NEW.source_position_end
      )
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_completeness_requires_exact_assertion');
END;

CREATE TABLE current_steenrod_action(
    snapshot_id TEXT NOT NULL REFERENCES snapshot(snapshot_id),
    slot_key TEXT NOT NULL,
    module_id TEXT NOT NULL,
    source_basis_element_id TEXT NOT NULL,
    operation_degree INTEGER NOT NULL CHECK(
        operation_degree > 0
        AND (operation_degree & (operation_degree - 1)) = 0
    ),
    projection_outcome TEXT NOT NULL CHECK(projection_outcome IN (
        'selected', 'unresolved_selection', 'conflicting', 'absent'
    )),
    selected_assertion_id TEXT REFERENCES steenrod_action_assertion(assertion_id),
    conflict_set_id TEXT REFERENCES conflict_set(conflict_set_id),
    projection_sha256 TEXT NOT NULL,
    PRIMARY KEY(snapshot_id, slot_key),
    UNIQUE(snapshot_id, module_id, source_basis_element_id, operation_degree),
    FOREIGN KEY(module_id, source_basis_element_id)
        REFERENCES steenrod_basis_element(module_id, basis_element_id),
    CHECK(
        (projection_outcome = 'selected' AND selected_assertion_id IS NOT NULL AND conflict_set_id IS NULL)
        OR (projection_outcome = 'conflicting' AND selected_assertion_id IS NULL AND conflict_set_id IS NOT NULL)
        OR (projection_outcome IN ('unresolved_selection', 'absent') AND selected_assertion_id IS NULL AND conflict_set_id IS NULL)
    )
);
CREATE INDEX current_steenrod_action_lookup_idx
ON current_steenrod_action(snapshot_id, module_id, source_basis_element_id, operation_degree);

CREATE TRIGGER current_steenrod_action_slot_snapshot_closure
BEFORE INSERT ON current_steenrod_action
WHEN
    NEW.slot_key <> (
        NEW.module_id || '|' || NEW.source_basis_element_id || '|Sq'
        || CAST(NEW.operation_degree AS TEXT)
    )
    OR NOT EXISTS (
        SELECT 1
        FROM steenrod_module module
        JOIN steenrod_basis_element source
          ON source.module_id = module.module_id
         AND source.basis_element_id = NEW.source_basis_element_id
        JOIN snapshot_record module_member
          ON module_member.snapshot_id = NEW.snapshot_id
         AND module_member.record_kind = 'steenrod_module'
         AND module_member.record_id = module.module_id
         AND module_member.record_sha256 = module.record_sha256
        JOIN snapshot_record source_member
          ON source_member.snapshot_id = NEW.snapshot_id
         AND source_member.record_kind = 'steenrod_basis_element'
         AND source_member.record_id = source.basis_element_id
         AND source_member.record_sha256 = source.record_sha256
        WHERE module.module_id = NEW.module_id
          AND (
              (
                  module.subject_kind = 'conceptual_spectrum'
                  AND EXISTS (
                      SELECT 1
                      FROM conceptual_spectrum spectrum
                      JOIN snapshot_record subject_member
                        ON subject_member.snapshot_id = NEW.snapshot_id
                       AND subject_member.record_kind = 'conceptual_spectrum'
                       AND subject_member.record_id = spectrum.spectrum_id
                       AND subject_member.record_sha256 = spectrum.record_sha256
                      WHERE spectrum.spectrum_id = module.subject_id
                  )
              )
              OR (
                  module.subject_kind = 'conceptual_space'
                  AND EXISTS (
                      SELECT 1
                      FROM conceptual_space space
                      JOIN snapshot_record subject_member
                        ON subject_member.snapshot_id = NEW.snapshot_id
                       AND subject_member.record_kind = 'conceptual_space'
                       AND subject_member.record_id = space.space_id
                       AND subject_member.record_sha256 = space.record_sha256
                      WHERE space.space_id = module.subject_id
                  )
              )
          )
    )
BEGIN
    SELECT RAISE(ABORT, 'steenrod_action_slot_not_grounded_in_snapshot');
END;

CREATE VIEW snapshot_eligible_steenrod_action AS
SELECT
    claim_member.snapshot_id,
    action.assertion_id,
    action.module_id,
    action.source_basis_element_id,
    action.operation_degree,
    claim.slot_key,
    claim.claim_fingerprint,
    claim.knowledge_state
FROM steenrod_action_assertion action
JOIN assertion claim USING(assertion_id)
JOIN snapshot_record claim_member
  ON claim_member.record_kind = 'assertion'
 AND claim_member.record_id = claim.assertion_id
 AND claim_member.record_sha256 = claim.record_sha256
WHERE claim.assertion_kind = 'steenrod_action'
  AND EXISTS (
      SELECT 1
      FROM assertion_evidence link
      JOIN evidence item USING(evidence_id)
      JOIN snapshot_record member
        ON member.snapshot_id = claim_member.snapshot_id
       AND member.record_kind = 'evidence'
       AND member.record_id = item.evidence_id
       AND member.record_sha256 = item.record_sha256
      WHERE link.assertion_id = claim.assertion_id
        AND (
            (item.evidence_kind = 'literature' AND EXISTS (
                SELECT 1 FROM literature_evidence
                WHERE evidence_id = item.evidence_id
            ))
            OR (item.evidence_kind = 'computation' AND EXISTS (
                SELECT 1 FROM computation_evidence
                WHERE evidence_id = item.evidence_id
            ))
            OR (item.evidence_kind = 'derivation' AND EXISTS (
                SELECT 1 FROM derivation_evidence
                WHERE evidence_id = item.evidence_id
            ))
        )
  )
  AND EXISTS (
      SELECT 1
      FROM assertion_review review
      JOIN snapshot_record member
        ON member.snapshot_id = claim_member.snapshot_id
       AND member.record_kind = 'assertion_review'
       AND member.record_id = review.assertion_review_id
       AND member.record_sha256 = review.record_sha256
      WHERE review.assertion_id = claim.assertion_id
        AND review.verdict = 'accept'
  )
  AND EXISTS (
      SELECT 1
      FROM editorial_event_effect effect
      JOIN editorial_event event USING(event_id)
      JOIN snapshot_record member
        ON member.snapshot_id = claim_member.snapshot_id
       AND member.record_kind = 'editorial_event'
       AND member.record_id = event.event_id
       AND member.record_sha256 = event.record_sha256
      WHERE effect.assertion_id = claim.assertion_id
        AND effect.effect_kind = 'admit'
        AND event.event_kind = 'admit'
  )
  AND NOT EXISTS (
      SELECT 1
      FROM editorial_event_effect effect
      JOIN editorial_event event USING(event_id)
      JOIN snapshot_record member
        ON member.snapshot_id = claim_member.snapshot_id
       AND member.record_kind = 'editorial_event'
       AND member.record_id = event.event_id
       AND member.record_sha256 = event.record_sha256
      WHERE effect.assertion_id = claim.assertion_id
        AND effect.effect_kind = 'retire'
        AND event.event_kind IN ('supersede', 'retract')
  )
  AND NOT EXISTS (
      SELECT 1
      FROM steenrod_action_term term
      JOIN steenrod_basis_element target
        ON target.module_id = term.module_id
       AND target.basis_element_id = term.target_basis_element_id
      WHERE term.assertion_id = claim.assertion_id
        AND NOT EXISTS (
            SELECT 1 FROM snapshot_record member
            WHERE member.snapshot_id = claim_member.snapshot_id
              AND member.record_kind = 'steenrod_basis_element'
              AND member.record_id = target.basis_element_id
              AND member.record_sha256 = target.record_sha256
        )
  );

-- Migration 0004 does not yet expose a deterministic Snapshot projection of
-- the append-only conflict ledger. Rejecting this outcome is safer than
-- accepting a conflict label whose active members cannot be proven closed in
-- the same Snapshot.
CREATE TRIGGER current_steenrod_action_conflict_requires_projected_ledger
BEFORE INSERT ON current_steenrod_action
WHEN NEW.projection_outcome = 'conflicting'
BEGIN
    SELECT RAISE(ABORT, 'steenrod_conflict_projection_not_supported');
END;

CREATE TRIGGER current_steenrod_action_absence_requires_no_candidate
BEFORE INSERT ON current_steenrod_action
WHEN NEW.projection_outcome = 'absent' AND EXISTS (
    SELECT 1
    FROM snapshot_eligible_steenrod_action candidate
    WHERE candidate.snapshot_id = NEW.snapshot_id
      AND candidate.module_id = NEW.module_id
      AND candidate.source_basis_element_id = NEW.source_basis_element_id
      AND candidate.operation_degree = NEW.operation_degree
      AND candidate.slot_key = NEW.slot_key
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_action_candidate_not_absent');
END;

CREATE TRIGGER current_steenrod_action_unresolved_requires_candidate
BEFORE INSERT ON current_steenrod_action
WHEN NEW.projection_outcome = 'unresolved_selection' AND 2 > (
    SELECT COUNT(DISTINCT candidate.claim_fingerprint)
    FROM snapshot_eligible_steenrod_action candidate
    WHERE candidate.snapshot_id = NEW.snapshot_id
      AND candidate.module_id = NEW.module_id
      AND candidate.source_basis_element_id = NEW.source_basis_element_id
      AND candidate.operation_degree = NEW.operation_degree
      AND candidate.slot_key = NEW.slot_key
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_action_candidate_not_found');
END;

CREATE TRIGGER current_steenrod_action_selected_closure
BEFORE INSERT ON current_steenrod_action
WHEN NEW.projection_outcome = 'selected' AND NOT (
    EXISTS (
        SELECT 1
        FROM steenrod_action_assertion action
        JOIN assertion claim USING(assertion_id)
        JOIN steenrod_module module USING(module_id)
        JOIN steenrod_basis_element source
          ON source.module_id = action.module_id
         AND source.basis_element_id = action.source_basis_element_id
        JOIN snapshot_record claim_member
          ON claim_member.snapshot_id = NEW.snapshot_id
         AND claim_member.record_kind = 'assertion'
         AND claim_member.record_id = claim.assertion_id
         AND claim_member.record_sha256 = claim.record_sha256
        JOIN snapshot_record module_member
          ON module_member.snapshot_id = NEW.snapshot_id
         AND module_member.record_kind = 'steenrod_module'
         AND module_member.record_id = module.module_id
         AND module_member.record_sha256 = module.record_sha256
        JOIN snapshot_record source_member
          ON source_member.snapshot_id = NEW.snapshot_id
         AND source_member.record_kind = 'steenrod_basis_element'
         AND source_member.record_id = source.basis_element_id
         AND source_member.record_sha256 = source.record_sha256
        WHERE action.assertion_id = NEW.selected_assertion_id
          AND action.module_id = NEW.module_id
          AND action.source_basis_element_id = NEW.source_basis_element_id
          AND action.operation_degree = NEW.operation_degree
          AND claim.assertion_kind = 'steenrod_action'
          AND claim.slot_key = NEW.slot_key
          AND EXISTS (
              SELECT 1 FROM snapshot_eligible_steenrod_action eligible
              WHERE eligible.snapshot_id = NEW.snapshot_id
                AND eligible.assertion_id = NEW.selected_assertion_id
          )
    )
    AND EXISTS (
        SELECT 1
        FROM steenrod_module module
        JOIN conceptual_spectrum spectrum
          ON module.subject_kind = 'conceptual_spectrum'
         AND spectrum.spectrum_id = module.subject_id
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'conceptual_spectrum'
         AND member.record_id = spectrum.spectrum_id
         AND member.record_sha256 = spectrum.record_sha256
        WHERE module.module_id = NEW.module_id
        UNION ALL
        SELECT 1
        FROM steenrod_module module
        JOIN conceptual_space space
          ON module.subject_kind = 'conceptual_space'
         AND space.space_id = module.subject_id
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'conceptual_space'
         AND member.record_id = space.space_id
         AND member.record_sha256 = space.record_sha256
        WHERE module.module_id = NEW.module_id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM steenrod_action_term term
        JOIN steenrod_basis_element target
          ON target.module_id = term.module_id
         AND target.basis_element_id = term.target_basis_element_id
        WHERE term.assertion_id = NEW.selected_assertion_id
          AND NOT EXISTS (
              SELECT 1 FROM snapshot_record member
              WHERE member.snapshot_id = NEW.snapshot_id
                AND member.record_kind = 'steenrod_basis_element'
                AND member.record_id = target.basis_element_id
                AND member.record_sha256 = target.record_sha256
          )
    )
    AND EXISTS (
        SELECT 1
        FROM assertion_evidence link
        JOIN evidence item USING(evidence_id)
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'evidence'
         AND member.record_id = item.evidence_id
         AND member.record_sha256 = item.record_sha256
        WHERE link.assertion_id = NEW.selected_assertion_id
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
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'assertion_review'
         AND member.record_id = review.assertion_review_id
         AND member.record_sha256 = review.record_sha256
        WHERE review.assertion_id = NEW.selected_assertion_id
          AND review.verdict = 'accept'
    )
    AND EXISTS (
        SELECT 1
        FROM editorial_event_effect effect
        JOIN editorial_event event USING(event_id)
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'editorial_event'
         AND member.record_id = event.event_id
         AND member.record_sha256 = event.record_sha256
        WHERE effect.assertion_id = NEW.selected_assertion_id
          AND effect.effect_kind = 'admit'
          AND event.event_kind = 'admit'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM snapshot_eligible_steenrod_action selected
        JOIN snapshot_eligible_steenrod_action other
          ON other.snapshot_id = selected.snapshot_id
         AND other.module_id = selected.module_id
         AND other.source_basis_element_id = selected.source_basis_element_id
         AND other.operation_degree = selected.operation_degree
         AND other.slot_key = selected.slot_key
         AND other.claim_fingerprint <> selected.claim_fingerprint
        WHERE selected.snapshot_id = NEW.snapshot_id
          AND selected.assertion_id = NEW.selected_assertion_id
    )
)
BEGIN
    SELECT RAISE(ABORT, 'selected_steenrod_action_not_grounded_in_snapshot');
END;

CREATE TRIGGER current_steenrod_action_before_finalize
BEFORE INSERT ON current_steenrod_action
WHEN EXISTS (
    SELECT 1 FROM snapshot
    WHERE snapshot_id = NEW.snapshot_id AND finalized_at IS NOT NULL
)
BEGIN SELECT RAISE(ABORT, 'snapshot_finalized'); END;

CREATE TRIGGER current_steenrod_action_u BEFORE UPDATE ON current_steenrod_action
BEGIN SELECT RAISE(ABORT, 'immutable_current_steenrod_action'); END;
CREATE TRIGGER current_steenrod_action_d BEFORE DELETE ON current_steenrod_action
BEGIN SELECT RAISE(ABORT, 'immutable_current_steenrod_action'); END;

CREATE TRIGGER current_steenrod_completeness_selected_closure
BEFORE INSERT ON current_completeness
WHEN NEW.subject_kind = 'steenrod_module' AND NOT (
    EXISTS (
        SELECT 1
        FROM steenrod_action_completeness_assertion steenrod_completeness
        JOIN completeness_assertion completeness USING(assertion_id)
        JOIN assertion claim USING(assertion_id)
        JOIN steenrod_module module USING(module_id)
        JOIN snapshot_record claim_member
          ON claim_member.snapshot_id = NEW.snapshot_id
         AND claim_member.record_kind = 'assertion'
         AND claim_member.record_id = claim.assertion_id
         AND claim_member.record_sha256 = claim.record_sha256
        JOIN snapshot_record module_member
          ON module_member.snapshot_id = NEW.snapshot_id
         AND module_member.record_kind = 'steenrod_module'
         AND module_member.record_id = module.module_id
         AND module_member.record_sha256 = module.record_sha256
        WHERE steenrod_completeness.assertion_id = NEW.assertion_id
          AND steenrod_completeness.module_id = NEW.subject_id
          AND claim.assertion_kind = 'steenrod_action_completeness'
          AND claim.knowledge_state = 'exact'
          AND completeness.completeness_kind = 'steenrod_action_coverage'
    )
    AND EXISTS (
        SELECT 1
        FROM steenrod_module module
        JOIN conceptual_spectrum spectrum
          ON module.subject_kind = 'conceptual_spectrum'
         AND spectrum.spectrum_id = module.subject_id
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'conceptual_spectrum'
         AND member.record_id = spectrum.spectrum_id
         AND member.record_sha256 = spectrum.record_sha256
        WHERE module.module_id = NEW.subject_id
        UNION ALL
        SELECT 1
        FROM steenrod_module module
        JOIN conceptual_space space
          ON module.subject_kind = 'conceptual_space'
         AND space.space_id = module.subject_id
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'conceptual_space'
         AND member.record_id = space.space_id
         AND member.record_sha256 = space.record_sha256
        WHERE module.module_id = NEW.subject_id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM steenrod_action_completeness_assertion completeness
        JOIN steenrod_basis_element basis
          ON basis.module_id = completeness.module_id
         AND basis.position BETWEEN completeness.source_position_start
                                AND completeness.source_position_end
        WHERE completeness.assertion_id = NEW.assertion_id
          AND NOT EXISTS (
              SELECT 1 FROM snapshot_record member
              WHERE member.snapshot_id = NEW.snapshot_id
                AND member.record_kind = 'steenrod_basis_element'
                AND member.record_id = basis.basis_element_id
                AND member.record_sha256 = basis.record_sha256
          )
    )
    AND NOT EXISTS (
        WITH RECURSIVE operation_power(operation_degree) AS (
            SELECT 1
            UNION ALL
            SELECT operation_degree * 2
            FROM operation_power
            WHERE operation_degree * 2 <= (
                SELECT maximum_operation_degree
                FROM steenrod_action_completeness_assertion
                WHERE assertion_id = NEW.assertion_id
            )
        )
        SELECT 1
        FROM steenrod_action_completeness_assertion completeness
        JOIN steenrod_basis_element source
          ON source.module_id = completeness.module_id
         AND source.position BETWEEN completeness.source_position_start
                                 AND completeness.source_position_end
        JOIN operation_power
        WHERE completeness.assertion_id = NEW.assertion_id
          AND source.degree + operation_power.operation_degree <= (
              SELECT MAX(degree)
              FROM steenrod_basis_element
              WHERE module_id = completeness.module_id
          )
          AND NOT EXISTS (
              SELECT 1
              FROM current_steenrod_action current
              JOIN assertion selected
                ON selected.assertion_id = current.selected_assertion_id
              WHERE current.snapshot_id = NEW.snapshot_id
                AND current.module_id = completeness.module_id
                AND current.source_basis_element_id = source.basis_element_id
                AND current.operation_degree = operation_power.operation_degree
                AND current.projection_outcome = 'selected'
                AND selected.knowledge_state = 'exact'
          )
    )
    AND EXISTS (
        SELECT 1
        FROM assertion_evidence link
        JOIN evidence item USING(evidence_id)
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'evidence'
         AND member.record_id = item.evidence_id
         AND member.record_sha256 = item.record_sha256
        WHERE link.assertion_id = NEW.assertion_id
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
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'assertion_review'
         AND member.record_id = review.assertion_review_id
         AND member.record_sha256 = review.record_sha256
        WHERE review.assertion_id = NEW.assertion_id
          AND review.verdict = 'accept'
    )
    AND EXISTS (
        SELECT 1
        FROM editorial_event_effect effect
        JOIN editorial_event event USING(event_id)
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'editorial_event'
         AND member.record_id = event.event_id
         AND member.record_sha256 = event.record_sha256
        WHERE effect.assertion_id = NEW.assertion_id
          AND effect.effect_kind = 'admit'
          AND event.event_kind = 'admit'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM editorial_event_effect effect
        JOIN editorial_event event USING(event_id)
        JOIN snapshot_record member
          ON member.snapshot_id = NEW.snapshot_id
         AND member.record_kind = 'editorial_event'
         AND member.record_id = event.event_id
         AND member.record_sha256 = event.record_sha256
        WHERE effect.assertion_id = NEW.assertion_id
          AND effect.effect_kind = 'retire'
          AND event.event_kind IN ('supersede', 'retract')
    )
)
BEGIN
    SELECT RAISE(ABORT, 'current_steenrod_completeness_not_grounded_in_snapshot');
END;

DROP TRIGGER knowledge_link_target_must_exist;
CREATE TRIGGER knowledge_link_target_must_exist
BEFORE INSERT ON knowledge_link
WHEN NOT (
    (NEW.target_kind = 'knowledge_entry' AND EXISTS (
        SELECT 1 FROM knowledge_entry WHERE knowledge_entry_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'conceptual_space' AND EXISTS (
        SELECT 1 FROM conceptual_space WHERE space_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'conceptual_spectrum' AND EXISTS (
        SELECT 1 FROM conceptual_spectrum WHERE spectrum_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'steenrod_module' AND EXISTS (
        SELECT 1 FROM steenrod_module WHERE module_id = NEW.target_id
    ))
    OR (NEW.target_kind = 'steenrod_basis_element' AND EXISTS (
        SELECT 1 FROM steenrod_basis_element WHERE basis_element_id = NEW.target_id
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

DROP TRIGGER snapshot_record_must_resolve;
CREATE TRIGGER snapshot_record_must_resolve
BEFORE INSERT ON snapshot_record
WHEN NOT (
    (NEW.record_kind = 'conceptual_space' AND EXISTS (
        SELECT 1 FROM conceptual_space
        WHERE space_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'conceptual_spectrum' AND EXISTS (
        SELECT 1 FROM conceptual_spectrum
        WHERE spectrum_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'spectrum_name' AND EXISTS (
        SELECT 1 FROM spectrum_name
        WHERE name_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'steenrod_module' AND EXISTS (
        SELECT 1 FROM steenrod_module
        WHERE module_id = NEW.record_id AND record_sha256 = NEW.record_sha256
    ))
    OR (NEW.record_kind = 'steenrod_basis_element' AND EXISTS (
        SELECT 1 FROM steenrod_basis_element
        WHERE basis_element_id = NEW.record_id AND record_sha256 = NEW.record_sha256
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

CREATE TRIGGER snapshot_steenrod_module_editorial_event_target_closure
BEFORE INSERT ON snapshot_record
WHEN NEW.record_kind = 'editorial_event' AND EXISTS (
    SELECT 1
    FROM steenrod_module_editorial_effect effect
    JOIN steenrod_module module USING(module_id)
    WHERE effect.event_id = NEW.record_id
      AND (
          NOT EXISTS (
              SELECT 1 FROM snapshot_record member
              WHERE member.snapshot_id = NEW.snapshot_id
                AND member.record_kind = 'steenrod_module'
                AND member.record_id = module.module_id
                AND member.record_sha256 = module.record_sha256
          )
          OR (
              module.subject_kind = 'conceptual_spectrum'
              AND NOT EXISTS (
                  SELECT 1
                  FROM conceptual_spectrum spectrum
                  JOIN snapshot_record member
                    ON member.snapshot_id = NEW.snapshot_id
                   AND member.record_kind = 'conceptual_spectrum'
                   AND member.record_id = spectrum.spectrum_id
                   AND member.record_sha256 = spectrum.record_sha256
                  WHERE spectrum.spectrum_id = module.subject_id
              )
          )
          OR (
              module.subject_kind = 'conceptual_space'
              AND NOT EXISTS (
                  SELECT 1
                  FROM conceptual_space space
                  JOIN snapshot_record member
                    ON member.snapshot_id = NEW.snapshot_id
                   AND member.record_kind = 'conceptual_space'
                   AND member.record_id = space.space_id
                   AND member.record_sha256 = space.record_sha256
                  WHERE space.space_id = module.subject_id
              )
          )
          OR NOT EXISTS (
              SELECT 1
              FROM steenrod_module_evidence link
              JOIN evidence item USING(evidence_id)
              JOIN derivation_evidence derivation USING(evidence_id)
              JOIN steenrod_import_evidence imported USING(evidence_id)
              JOIN snapshot_record evidence_member
                ON evidence_member.snapshot_id = NEW.snapshot_id
               AND evidence_member.record_kind = 'evidence'
               AND evidence_member.record_id = item.evidence_id
               AND evidence_member.record_sha256 = item.record_sha256
              WHERE link.module_id = module.module_id
                AND item.evidence_kind = 'derivation'
                AND imported.normalized_module_sha256 = module.record_sha256
          )
      )
)
BEGIN
    SELECT RAISE(ABORT, 'steenrod_module_editorial_target_not_in_snapshot');
END;

CREATE VIEW snapshot_admitted_steenrod_module AS
SELECT DISTINCT
    event_member.snapshot_id,
    module.module_id,
    admit.event_id AS admission_event_id
FROM steenrod_module_editorial_effect admit
JOIN editorial_event admission_event
  ON admission_event.event_id = admit.event_id
 AND admission_event.event_kind = 'admit'
JOIN steenrod_module module USING(module_id)
JOIN snapshot_record event_member
  ON event_member.record_kind = 'editorial_event'
 AND event_member.record_id = admission_event.event_id
 AND event_member.record_sha256 = admission_event.record_sha256
JOIN snapshot_record module_member
  ON module_member.snapshot_id = event_member.snapshot_id
 AND module_member.record_kind = 'steenrod_module'
 AND module_member.record_id = module.module_id
 AND module_member.record_sha256 = module.record_sha256
WHERE admit.effect_kind = 'admit'
  AND EXISTS (
      SELECT 1
      FROM steenrod_module_evidence link
      JOIN evidence item USING(evidence_id)
      JOIN derivation_evidence derivation USING(evidence_id)
      JOIN steenrod_import_evidence imported USING(evidence_id)
      JOIN snapshot_record evidence_member
        ON evidence_member.snapshot_id = event_member.snapshot_id
       AND evidence_member.record_kind = 'evidence'
       AND evidence_member.record_id = item.evidence_id
       AND evidence_member.record_sha256 = item.record_sha256
      WHERE link.module_id = module.module_id
        AND item.evidence_kind = 'derivation'
        AND imported.normalized_module_sha256 = module.record_sha256
  )
  AND NOT EXISTS (
      SELECT 1
      FROM steenrod_module_editorial_effect retire
      JOIN editorial_event retire_event
        ON retire_event.event_id = retire.event_id
       AND retire_event.event_kind IN ('supersede', 'retract')
      JOIN snapshot_record retire_member
        ON retire_member.snapshot_id = event_member.snapshot_id
       AND retire_member.record_kind = 'editorial_event'
       AND retire_member.record_id = retire_event.event_id
       AND retire_member.record_sha256 = retire_event.record_sha256
      WHERE retire.module_id = module.module_id
        AND retire.effect_kind = 'retire'
  );

CREATE TRIGGER snapshot_evidence_requires_typed_subtype
BEFORE INSERT ON snapshot_record
WHEN NEW.record_kind = 'evidence' AND NOT EXISTS (
    SELECT 1 FROM evidence item
    WHERE item.evidence_id = NEW.record_id
      AND item.record_sha256 = NEW.record_sha256
      AND (
          (item.evidence_kind = 'literature' AND EXISTS (
              SELECT 1 FROM literature_evidence
              WHERE evidence_id = item.evidence_id
          ))
          OR (item.evidence_kind = 'computation' AND EXISTS (
              SELECT 1 FROM computation_evidence
              WHERE evidence_id = item.evidence_id
          ))
          OR (item.evidence_kind = 'derivation' AND EXISTS (
              SELECT 1 FROM derivation_evidence
              WHERE evidence_id = item.evidence_id
          ))
      )
)
BEGIN
    SELECT RAISE(ABORT, 'snapshot_evidence_subtype_missing');
END;

CREATE TRIGGER snapshot_record_before_steenrod_projection
BEFORE INSERT ON snapshot_record
WHEN
    EXISTS (
        SELECT 1 FROM current_steenrod_action
        WHERE snapshot_id = NEW.snapshot_id
    )
    OR EXISTS (
        SELECT 1 FROM current_completeness
        WHERE snapshot_id = NEW.snapshot_id
          AND subject_kind = 'steenrod_module'
    )
BEGIN
    SELECT RAISE(ABORT, 'snapshot_steenrod_projection_started');
END;

CREATE TRIGGER literature_evidence_before_snapshot_use
BEFORE INSERT ON literature_evidence
WHEN EXISTS (
    SELECT 1 FROM snapshot_record
    WHERE record_kind = 'evidence' AND record_id = NEW.evidence_id
)
BEGIN SELECT RAISE(ABORT, 'sealed_snapshot_evidence'); END;

CREATE TRIGGER computation_evidence_before_snapshot_use
BEFORE INSERT ON computation_evidence
WHEN EXISTS (
    SELECT 1 FROM snapshot_record
    WHERE record_kind = 'evidence' AND record_id = NEW.evidence_id
)
BEGIN SELECT RAISE(ABORT, 'sealed_snapshot_evidence'); END;

CREATE TRIGGER derivation_evidence_before_snapshot_use
BEFORE INSERT ON derivation_evidence
WHEN EXISTS (
    SELECT 1 FROM snapshot_record
    WHERE record_kind = 'evidence' AND record_id = NEW.evidence_id
)
BEGIN SELECT RAISE(ABORT, 'sealed_snapshot_evidence'); END;

CREATE TRIGGER steenrod_assertion_evidence_before_parent_use
BEFORE INSERT ON assertion_evidence
WHEN (
    EXISTS (
        SELECT 1 FROM steenrod_action_assertion
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM steenrod_action_completeness_assertion
        WHERE assertion_id = NEW.assertion_id
    )
) AND (
    EXISTS (
        SELECT 1 FROM assertion_review
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM editorial_event_effect
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM snapshot_record
        WHERE record_kind = 'assertion' AND record_id = NEW.assertion_id
    )
)
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_assertion_evidence');
END;

CREATE TRIGGER steenrod_editorial_effect_before_snapshot_use
BEFORE INSERT ON editorial_event_effect
WHEN (
    EXISTS (
        SELECT 1 FROM steenrod_action_assertion
        WHERE assertion_id = NEW.assertion_id
    )
    OR EXISTS (
        SELECT 1 FROM steenrod_action_completeness_assertion
        WHERE assertion_id = NEW.assertion_id
    )
) AND (
    EXISTS (
        SELECT 1 FROM snapshot_record
        WHERE record_kind = 'editorial_event' AND record_id = NEW.event_id
    )
)
BEGIN
    SELECT RAISE(ABORT, 'sealed_steenrod_editorial_effect');
END;

CREATE TRIGGER conceptual_spectrum_u BEFORE UPDATE ON conceptual_spectrum
BEGIN SELECT RAISE(ABORT, 'immutable_conceptual_spectrum'); END;
CREATE TRIGGER conceptual_spectrum_d BEFORE DELETE ON conceptual_spectrum
BEGIN SELECT RAISE(ABORT, 'immutable_conceptual_spectrum'); END;
CREATE TRIGGER spectrum_name_u BEFORE UPDATE ON spectrum_name
BEGIN SELECT RAISE(ABORT, 'immutable_spectrum_name'); END;
CREATE TRIGGER spectrum_name_d BEFORE DELETE ON spectrum_name
BEGIN SELECT RAISE(ABORT, 'immutable_spectrum_name'); END;
CREATE TRIGGER steenrod_module_u BEFORE UPDATE ON steenrod_module
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_module'); END;
CREATE TRIGGER steenrod_module_d BEFORE DELETE ON steenrod_module
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_module'); END;
CREATE TRIGGER steenrod_module_editorial_effect_u
BEFORE UPDATE ON steenrod_module_editorial_effect
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_module_editorial_effect'); END;
CREATE TRIGGER steenrod_module_editorial_effect_d
BEFORE DELETE ON steenrod_module_editorial_effect
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_module_editorial_effect'); END;
CREATE TRIGGER steenrod_import_evidence_u BEFORE UPDATE ON steenrod_import_evidence
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_import_evidence'); END;
CREATE TRIGGER steenrod_import_evidence_d BEFORE DELETE ON steenrod_import_evidence
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_import_evidence'); END;
CREATE TRIGGER steenrod_module_evidence_u BEFORE UPDATE ON steenrod_module_evidence
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_module_evidence'); END;
CREATE TRIGGER steenrod_module_evidence_d BEFORE DELETE ON steenrod_module_evidence
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_module_evidence'); END;
CREATE TRIGGER steenrod_basis_element_u BEFORE UPDATE ON steenrod_basis_element
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_basis_element'); END;
CREATE TRIGGER steenrod_basis_element_d BEFORE DELETE ON steenrod_basis_element
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_basis_element'); END;
CREATE TRIGGER steenrod_action_assertion_u BEFORE UPDATE ON steenrod_action_assertion
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_action_assertion'); END;
CREATE TRIGGER steenrod_action_assertion_d BEFORE DELETE ON steenrod_action_assertion
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_action_assertion'); END;
CREATE TRIGGER steenrod_action_term_u BEFORE UPDATE ON steenrod_action_term
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_action_term'); END;
CREATE TRIGGER steenrod_action_term_d BEFORE DELETE ON steenrod_action_term
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_action_term'); END;
CREATE TRIGGER steenrod_action_completeness_assertion_u
BEFORE UPDATE ON steenrod_action_completeness_assertion
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_action_completeness_assertion'); END;
CREATE TRIGGER steenrod_action_completeness_assertion_d
BEFORE DELETE ON steenrod_action_completeness_assertion
BEGIN SELECT RAISE(ABORT, 'immutable_steenrod_action_completeness_assertion'); END;
