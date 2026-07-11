#!/usr/bin/env python3
"""Verify the auditable arithmetic and disjointness in the 0.0.1 manifest spec."""

from __future__ import annotations

import json
from math import gcd
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "corpus" / "v0.0.1" / "manifest-spec.json"


def inclusive_count(bounds: list[int]) -> int:
    if len(bounds) != 2 or bounds[0] > bounds[1]:
        raise AssertionError(f"invalid inclusive range: {bounds}")
    return bounds[1] - bounds[0] + 1


def prime_factors(value: int) -> set[int]:
    factors: set[int] = set()
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors.add(divisor)
            value //= divisor
        divisor += 1
    if value > 1:
        factors.add(value)
    return factors


def has_nonlinear_primary_part(value: int) -> bool:
    """Whether Z/value has a Z/(p^e), e >= 2, primary summand."""
    for prime in prime_factors(value):
        remaining = value
        exponent = 0
        while remaining % prime == 0:
            exponent += 1
            remaining //= prime
        if exponent >= 2:
            return True
    return False


def lens_canonical_q(p: int, q: int) -> int:
    inverse = pow(q, -1, p)
    return min(q % p, (-q) % p, inverse, (-inverse) % p)


def moore_parameters(family: dict[str, Any]) -> set[tuple[int, int]]:
    parameters = family["parameter"]
    grid = parameters["cartesian_m_n"]
    grid_values = {(m, n) for m in grid["m_values"] for n in grid["n_values"]}
    excluded = {tuple(item) for item in parameters.get("excluded_values", [])}
    additional = {tuple(item) for item in parameters.get("additional_values", [])}
    if not excluded <= grid_values:
        raise AssertionError("Moore exclusions are not members of the grid")
    retained = grid_values - excluded
    if retained & additional:
        raise AssertionError("Moore additional values duplicate the retained grid")
    if (2, 1) not in excluded or (2, 1) in retained | additional:
        raise AssertionError("M(Z/2,1) must be excluded as the RP2 identity")
    return retained | additional


def derive_torsion(families: dict[str, dict[str, Any]]) -> dict[str, Any]:
    pairs: set[tuple[str, int]] = set()
    primary_pairs: dict[str, set[tuple[str, int]]] = {
        str(prime): set() for prime in (2, 3, 5, 7)
    }
    torsion_spaces: set[str] = set()
    prime_power_spaces: set[str] = set()
    multiplicity_spaces: set[str] = set()

    def add(space: str, degree: int, order: int, multiplicity: int = 1) -> None:
        pair = (space, degree)
        pairs.add(pair)
        torsion_spaces.add(space)
        for prime in prime_factors(order):
            if str(prime) in primary_pairs:
                primary_pairs[str(prime)].add(pair)
        if has_nonlinear_primary_part(order):
            prime_power_spaces.add(space)
        if multiplicity >= 2:
            multiplicity_spaces.add(space)

    for m, n in moore_parameters(families["moore_spaces"]):
        add(f"moore:{m}:{n}", n, m)

    bouquets = families["mixed_moore_bouquets"]
    ranks = bouquets["parameter"]["free_circle_rank"]["range_inclusive"]
    repeated_ranks = set(bouquets["definition"]["extra_multiplicity"]["for_free_circle_rank"])
    for rank in range(ranks[0], ranks[1] + 1):
        for order, degree in bouquets["definition"]["summands"]:
            add(
                f"mixed_moore_bouquet:{rank}",
                degree,
                order,
                2 if rank in repeated_ranks and (order, degree) == (2, 2) else 1,
            )

    nonorientable = families["closed_nonorientable_surfaces"]
    genus_bounds = nonorientable["parameter"]["genus"]["range_inclusive"]
    for genus in range(genus_bounds[0], genus_bounds[1] + 1):
        add(f"nonorientable_surface:{genus}", 1, 2)

    for dimension in families["real_projective_spaces"]["parameter"]["dimension"]["values"]:
        for degree in range(1, dimension, 2):
            add(f"real_projective_space:{dimension}", degree, 2)

    lens_pairs = families["lens_spaces_3d"]["parameter"]["p_q_pairs"]["values"]
    for p, q in lens_pairs:
        add(f"lens:{p}:{q}", 1, p)

    return {
        "distinct_space_degree_pairs_floor": len(pairs),
        "distinct_spaces_floor": len(torsion_spaces),
        "p_primary_pair_floors": {
            prime: len(primary_pairs[prime]) for prime in primary_pairs
        },
        "prime_power_spaces_floor": len(prime_power_spaces),
        "primary_multiplicity_spaces_floor": len(multiplicity_spaces),
        "positive_degree_other_than_one_pairs_floor": sum(
            degree != 1 for _, degree in pairs
        ),
    }


def parameter_count(family: dict[str, Any]) -> int:
    if "instances" in family:
        return len(family["instances"])

    parameters = family["parameter"]
    if "p_q_pairs" in parameters:
        pairs = parameters["p_q_pairs"]["values"]
        if len({tuple(pair) for pair in pairs}) != len(pairs):
            raise AssertionError("lens-space parameter pairs are not unique")
        if any(p < 2 or q < 1 or q >= p or gcd(p, q) != 1 for p, q in pairs):
            raise AssertionError("invalid lens-space parameter pair")
        canonical_pairs = {(p, lens_canonical_q(p, q)) for p, q in pairs}
        if len(canonical_pairs) != len(pairs):
            raise AssertionError("lens spaces duplicate an unoriented homeomorphism class")
        if any(q != lens_canonical_q(p, q) for p, q in pairs):
            raise AssertionError("lens-space q is not in canonical unoriented form")
        return len(pairs)

    if "dimension_pairs" in parameters:
        pairs = parameters["dimension_pairs"]["values"]
        if len({tuple(pair) for pair in pairs}) != len(pairs):
            raise AssertionError(f"duplicate dimension pair in {family['id']}")
        if family["id"] == "sphere_products" and any(a > b for a, b in pairs):
            raise AssertionError("sphere-product factors must satisfy a <= b")
        return len(pairs)

    if "surface_kinds" in parameters:
        return len(parameters["surface_kinds"]) * inclusive_count(
            parameters["genus"]["range_inclusive"]
        )

    if "cartesian_m_n" in parameters:
        return len(moore_parameters(family))

    variable_counts: list[int] = []
    for value in parameters.values():
        if not isinstance(value, dict):
            continue
        if "range_inclusive" in value:
            variable_counts.append(inclusive_count(value["range_inclusive"]))
        elif "values" in value:
            variable_counts.append(len(value["values"]))
    if not variable_counts:
        raise AssertionError(f"cannot expand family {family['id']}")

    count = 1
    for item in variable_counts:
        count *= item
    return count


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data["status"] != "selection_contract_not_release_evidence":
        raise AssertionError("planning spec must not claim release qualification")

    families = data["curated_space_plan"]["family_rollups"]
    family_ids = [family["id"] for family in families]
    if len(family_ids) != len(set(family_ids)):
        raise AssertionError("family rollup IDs must be unique")

    for family in families:
        expanded = parameter_count(family)
        if expanded != family["count"]:
            raise AssertionError(
                f"{family['id']} declares {family['count']} but expands to {expanded}"
            )

    curated_count = sum(family["count"] for family in families)
    qa_common_count = sum(family["qa_common_manifold_count"] for family in families)
    expected_curated = data["curated_space_plan"]["expected_count"]
    expected_qa_common = data["curated_space_plan"]["expected_common_manifold_count"]
    if curated_count != expected_curated:
        raise AssertionError((curated_count, expected_curated))
    if qa_common_count != expected_qa_common:
        raise AssertionError((qa_common_count, expected_qa_common))
    if max(family["count"] for family in families) * 4 > curated_count:
        raise AssertionError("one family exceeds the 25 percent cap")
    if len(families) < 12:
        raise AssertionError("fewer than twelve family rollups")
    families_by_id = {family["id"]: family for family in families}

    exceptional = next(f for f in families if f["id"] == "exceptional_spaces")
    empty = exceptional["empty_space_semantics"]
    required_coefficients = ["Z", "F2", "F3", "F5", "F7"]
    if empty["model_dimension"] != -1:
        raise AssertionError("empty Model dimension must be -1")
    if empty["explicit_unreduced_h0_zero_coefficients"] != required_coefficients:
        raise AssertionError("empty unreduced H0 zero grid is incomplete")
    if empty["explicit_reduced_h0_zero_coefficients"] != required_coefficients:
        raise AssertionError("empty reduced H0 zero grid is incomplete")
    if empty["reduced_h_minus_1"] != "coefficient_module":
        raise AssertionError("empty reduced H_-1 convention is not explicit")

    model_plan = data["model_plan"]
    bulk = model_plan["bulk_stellar"]
    multi = model_plan["multipresentation_models"]
    dimensions = bulk["dimensions"]
    if len(dimensions) != len(set(dimensions)) or dimensions != [2, 3]:
        raise AssertionError("bulk dimensions must be the distinct fixed 2/3 strata")
    format_plans = bulk["per_dimension"]
    reserves: dict[str, set[int]] = {}
    for format_name, format_plan in format_plans.items():
        bounds = format_plan["reserve_rank_interval"]
        quota = format_plan["qualifying_quota"]
        if inclusive_count(bounds) < quota:
            raise AssertionError(f"{format_name} reserve cannot fill its quota")
        reserves[format_name] = set(range(bounds[0], bounds[1] + 1))
    if reserves["finite_simplicial"] & reserves["finite_regular_cw"]:
        raise AssertionError("bulk format reserves overlap")
    derived_bulk_simplicial = len(dimensions) * format_plans["finite_simplicial"]["qualifying_quota"]
    derived_bulk_cw = len(dimensions) * format_plans["finite_regular_cw"]["qualifying_quota"]
    if derived_bulk_simplicial != bulk["counted_simplicial"]:
        raise AssertionError("simplicial bulk total does not derive from strata")
    if derived_bulk_cw != bulk["counted_regular_cw_simplicial_face_poset"]:
        raise AssertionError("regular-CW bulk total does not derive from strata")
    if bulk["dedupe"] != "dimension_colored_incidence_graph_presentation_isomorphism/1":
        raise AssertionError("bulk presentation-isomorphism rule is not fixed")
    required_exclusions = {
        "presentation_isomorphic_to_counted_model",
        "lossless_reencoding_of_counted_model",
        "duplicate_derivation_root_outside_multipresentation_cohort",
    }
    if not required_exclusions <= set(model_plan["counting_exclusions"]):
        raise AssertionError("model counting exclusions do not protect cohort disjointness")
    if model_plan["curated_primary_models"]["count"] != curated_count:
        raise AssertionError("curated primary-model count does not match curated spaces")
    computed_simplicial = (
        bulk["counted_simplicial"]
        + model_plan["curated_primary_models"]["count"]
        + multi["same_format_simplicial_count"]
    )
    computed_cw = (
        bulk["counted_regular_cw_simplicial_face_poset"]
        + multi["cross_format_genuinely_nonsimplicial_count"]
    )
    if computed_simplicial != model_plan["expected_finite_simplicial"]:
        raise AssertionError((computed_simplicial, model_plan["expected_finite_simplicial"]))
    if computed_cw != model_plan["expected_finite_regular_cw"]:
        raise AssertionError((computed_cw, model_plan["expected_finite_regular_cw"]))
    if computed_simplicial + computed_cw != model_plan["expected_counted_total"]:
        raise AssertionError("model bucket totals do not reconcile")
    if min(computed_simplicial, computed_cw) < 400:
        raise AssertionError("a model format floor is below G2")

    same_format = multi["same_format_spaces"]
    cross_format = multi["cross_format_spaces"]
    if len(same_format) != len(set(same_format)):
        raise AssertionError("same-format cohort contains duplicate space keys")
    if len(cross_format) != len(set(cross_format)):
        raise AssertionError("cross-format cohort contains duplicate space keys")
    if len(same_format) != multi["same_format_simplicial_count"]:
        raise AssertionError("same-format multipresentation count mismatch")
    if len(cross_format) != multi["cross_format_genuinely_nonsimplicial_count"]:
        raise AssertionError("cross-format multipresentation count mismatch")
    if set(same_format) & set(cross_format):
        raise AssertionError("multipresentation cohorts overlap")
    if len(set(same_format + cross_format)) != multi["additional_count"]:
        raise AssertionError("multipresentation space count mismatch")

    torsion = data["predicted_torsion_acceptance"]
    derived_torsion = derive_torsion(families_by_id)
    for field, derived_value in derived_torsion.items():
        if torsion[field] != derived_value:
            raise AssertionError(
                f"torsion {field} declares {torsion[field]!r}, derives {derived_value!r}"
            )
    if derived_torsion["distinct_space_degree_pairs_floor"] < 100:
        raise AssertionError("G3 pair floor not met")
    if derived_torsion["distinct_spaces_floor"] < 40:
        raise AssertionError("G3 space floor not met")
    required_prime_pairs = {"2": 40, "3": 25, "5": 15, "7": 10}
    for prime, floor in required_prime_pairs.items():
        if derived_torsion["p_primary_pair_floors"][prime] < floor:
            raise AssertionError(f"G3 p={prime} floor not met")
    if derived_torsion["prime_power_spaces_floor"] < 8:
        raise AssertionError("G3 prime-power floor not met")
    if derived_torsion["primary_multiplicity_spaces_floor"] < 5:
        raise AssertionError("G3 multiplicity floor not met")
    if derived_torsion["positive_degree_other_than_one_pairs_floor"] < 10:
        raise AssertionError("G3 higher-degree floor not met")

    grid = data["mathematical_grid_plan"]
    if grid["coefficient_system_ids"] != required_coefficients:
        raise AssertionError("G4 coefficient grid is not the required five-system grid")
    required_grid_values = {
        "theory_id": "ordinary_homology",
        "convention_id": "augmented_singular_v1",
        "required_projection_outcome": "selected",
        "required_knowledge_state": "exact",
        "required_value_scope": "complete_group",
    }
    for field, expected in required_grid_values.items():
        if grid[field] != expected:
            raise AssertionError(f"G4 {field} must be {expected}")
    full_grid_keys = grid["full_reduced_grid_space_keys"]
    if len(full_grid_keys) != len(set(full_grid_keys)):
        raise AssertionError("G4 full-reduced cohort contains duplicate space keys")
    if len(full_grid_keys) != grid["full_reduced_grid_space_count"] or len(full_grid_keys) < 25:
        raise AssertionError("G4 full-reduced cohort count mismatch")
    expected_grid_keys = {"empty_space", "point"}
    expected_grid_keys |= {f"sphere:{degree}" for degree in range(13)}
    expected_grid_keys |= {f"orientable_surface:{genus}" for genus in range(2, 7)}
    expected_grid_keys |= {f"nonorientable_surface:{genus}" for genus in range(2, 7)}
    if set(full_grid_keys) != expected_grid_keys:
        raise AssertionError("G4 full-reduced cohort does not match its exact expansion")
    required_grid_flags = {
        "explicit_reduced_h0_for_every_curated_space",
        "expected_minus_selected_must_be_empty",
        "field_groups_computed_from_owned_chains",
    }
    if not all(grid[field] is True for field in required_grid_flags):
        raise AssertionError("G4 exactness/completeness flags are not all enabled")
    if grid["read_time_uct_forbidden"] is not True:
        raise AssertionError("read-time UCT must remain forbidden")

    adversarial = data["adversarial_plan"]
    expected_case_counts = {
        "unknown": 10,
        "not_computed": 10,
        "not_applicable": 3,
        "bounded_or_conjectural": 5,
        "correction": 5,
        "conflict": 3,
    }
    if {key: case["count"] for key, case in adversarial["cases"].items()} != expected_case_counts:
        raise AssertionError("G5 case counts differ from the fixed adversarial plan")
    not_applicable = adversarial["cases"]["not_applicable"]
    if len(not_applicable["slot_degrees"]) != not_applicable["count"]:
        raise AssertionError("G5 not-applicable slots do not expand to three cases")
    if not_applicable["convention_id"] == grid["convention_id"]:
        raise AssertionError("G5 not-applicable fixtures collide with the G4 convention")
    if not_applicable["applicability_rule_id"] != "reduced_homology_nonempty_subject_required/1":
        raise AssertionError("G5 not-applicable rule is not a valid separate convention")
    if adversarial["generated_slots_must_have_zero_intersection_with_g4"] is not True:
        raise AssertionError("G5/G4 slot disjointness is not required")
    generated_patterns: list[str] = [adversarial["fixture_subject_pattern"]]
    for case in adversarial["cases"].values():
        generated_patterns.extend(
            value for key, value in case.items()
            if key.endswith("_id_pattern") and isinstance(value, str)
        )
    if len(generated_patterns) != len(set(generated_patterns)):
        raise AssertionError("G5 generated ID namespaces overlap")
    if set(adversarial["mandatory_fixture_models"]) != {"empty_space", "sphere:0", "point"}:
        raise AssertionError("G5 mandatory exceptional fixtures changed")

    validation = data["independent_validation_cohort"]
    derived_validation_count = 0
    explicit_validation_keys: list[str] = []
    for component in validation["selection_components"]:
        if component["kind"] == "all_models_of_multipresentation_cohort":
            expected = component["space_count"] * component["models_per_space"]
        elif "space_keys" in component:
            expected = len(component["space_keys"])
            explicit_validation_keys.extend(component["space_keys"])
        elif "strata" in component:
            expected = len(component["strata"])
        else:
            raise AssertionError("unknown independent-validation selection component")
        if expected != component["model_count"]:
            raise AssertionError("independent-validation component count mismatch")
        derived_validation_count += expected
    if derived_validation_count != validation["expected_model_count"] or derived_validation_count != 66:
        raise AssertionError("independent-validation cohort does not derive to 66 Models")
    if len(explicit_validation_keys) != len(set(explicit_validation_keys)):
        raise AssertionError("explicit independent-validation Models overlap")
    if set(explicit_validation_keys) & set(same_format + cross_format):
        raise AssertionError("explicit validation extras overlap the all-presentation cohort")
    required_validation_coverage = {
        "both_format_classes", "p2", "p3", "p5", "p7", "prime_power",
        "multiplicity", "degree_gt_1", "empty", "disconnected", "each_source_lineage",
    }
    if set(validation["must_cover"]) != required_validation_coverage:
        raise AssertionError("independent-validation coverage changed")
    if not validation["generator_and_oracle_must_be_independent"]:
        raise AssertionError("independent validation does not require an independent oracle")
    if not validation["release_ledger_must_name_exact_model_and_result_refs"]:
        raise AssertionError("independent validation lacks exact release-ledger references")

    qa = data["qa_cohort"]
    if sum(qa["prompt_categories"].values()) != qa["expected_prompt_count"]:
        raise AssertionError("QA prompt categories do not total the expected suite")
    if qa["pinned_acceptance_space_count"] < 50:
        raise AssertionError("QA cohort is too small")
    if qa["family_rollup_count"] < 8:
        raise AssertionError("QA cohort is too narrow")

    locks = data["source_locks"]
    lock_ids = [lock["id"] for lock in locks]
    if len(lock_ids) != len(set(lock_ids)):
        raise AssertionError("source-lock IDs must be unique")
    if bulk["source_lock"] not in lock_ids:
        raise AssertionError("bulk source lock does not resolve")
    locks_by_id = {lock["id"]: lock for lock in locks}
    stellar = locks_by_id["stellar-v6-zenodo-17495553"]
    if len(stellar["files"]) != 6 or sum(item["bytes"] for item in stellar["files"]) != 117167618:
        raise AssertionError("Stellar source lock is not the exact six-file pin")
    if any(len(item["sha256"]) != 64 for item in stellar["files"]):
        raise AssertionError("Stellar source file lacks a SHA-256")
    simpcomp = locks_by_id["simpcomp-aff7cf2"]
    lens_keys = {f"lens:{p}:{q}" for p, q in families_by_id["lens_spaces_3d"]["parameter"]["p_q_pairs"]["values"]}
    if {item["space_key"] for item in simpcomp["artifacts"]} != lens_keys:
        raise AssertionError("simpcomp artifacts do not exactly cover the lens manifest")
    if len({item["path"] for item in simpcomp["artifacts"]}) != 13:
        raise AssertionError("simpcomp lens artifact paths are not unique")
    if any(len(item["sha256"]) != 64 for item in simpcomp["artifacts"]):
        raise AssertionError("simpcomp artifact lacks a SHA-256")

    required_ledger_fields = {
        "source": {"source_lock_id", "immutable_pin", "retrieved_at", "raw_sha256", "attribution", "license_facts"},
        "model_artifact": {"model_id", "artifact_id", "counted_bucket", "schema_version", "decoder_version", "neutral_sha256", "derivation_root_id", "ordered_cells", "regularity_witness_id", "distinctness_evidence_id", "qualification_state"},
        "computation": {"run_id", "input_sha256", "chain_sha256", "output_sha256", "log_sha256", "ordered_basis_manifest", "boundary_matrix_hashes", "algorithm_id", "implementation_version", "library_versions", "parameters", "environment_lock", "exit_status", "deterministic_rerun_digest"},
        "homology_assertion": {"assertion_id", "subject_id", "theory_id", "coefficient_system_id", "degree", "reduced", "convention_id", "knowledge_state", "typed_payload", "value_scope", "completeness_id", "derivation_id", "evidence_refs", "admission_event_id", "current_projection_outcome"},
        "model_of": {"model_of_assertion_id", "model_id", "space_id", "equivalence_kind", "review_event_id", "admission_event_id", "preservation_rule_id", "evidence_refs"},
        "snapshot": {"snapshot_id", "membership_digest", "event_log_digest", "projection_digest", "manifest_digest", "export_digest"},
    }
    ledger = data["release_ledger_required_fields"]
    for section, fields in required_ledger_fields.items():
        if not fields <= set(ledger[section]):
            raise AssertionError(f"release ledger {section} omits mandatory fields")

    summary = {
        "curated_spaces": curated_count,
        "common_manifolds": qa_common_count,
        "family_rollups": len(families),
        "finite_simplicial_models": computed_simplicial,
        "finite_regular_cw_models": computed_cw,
        "counted_models": computed_simplicial + computed_cw,
        "predicted_torsion_pairs": derived_torsion["distinct_space_degree_pairs_floor"],
        "qa_prompts": qa["expected_prompt_count"]
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
