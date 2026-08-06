"""Canonical stable mod-2 Steenrod modules and deterministic adapters.

The canonical records distinguish an exact empty image from an absent action.
External adapters are therefore available only for modules with an exact
completeness assertion covering every action slot in finite support.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping


CORPUS_SCHEMA_VERSION = "homology-db.steenrod-corpus/1"
MODULE_SCHEMA_VERSION = "homology-db.steenrod-module/1"
CORPUS_PATH = (
    Path(__file__).resolve().parent.parent
    / "corpus"
    / "steenrod-cw49-v1"
    / "corpus.json"
)
UPSTREAM_ADAMS_PATH = CORPUS_PATH.with_name("upstream-adams.json")

CW49_SPECTRUM_IDS = (
    "S0",
    "tmf",
    "C2",
    "Ceta",
    "Cnu",
    "Csigma",
    "CW_2_eta",
    "CW_eta_2",
    "CW_eta_nu",
    "CW_nu_eta",
    "CW_sigma_nu",
    "CW_nu_sigma",
    "CW_2_eta_nu",
    "CW_nu_eta_2",
    "CW_sigma_nu_eta",
    "CW_eta_nu_sigma",
    "CW_sigma_nu_eta_2",
    "CW_2_eta_nu_sigma",
    "Csigmasq",
    "C2h4",
    "DC2h4",
    "Ctheta4",
    "C2h5",
    "DC2h5",
    "Ctheta5",
    "C2h6",
    "DC2h6",
    "C2_C2",
    "Ceta_Ceta",
    "Cnu_Cnu",
    "Csigma_Csigma",
    "C2_Ceta",
    "CW_2sigma_sigma",
    "CW_sigma_2sigma",
    "C2sigma",
    "CW_2_V_eta",
    "CW_2_A_eta",
    "Joker",
    "CW_eta_2_eta_Eq_2_nu",
    "CW_eta_2_eta_Eq_nu_2",
    "RP3_6",
    "Fphi",
    "RP1_4",
    "RP1_6",
    "RP1_8",
    "RP1_10",
    "RP1_12",
    "RP1_256",
    "RP3_256",
)

_PROJECTIVE_LIMITS = {
    "RP3_6": (3, 6),
    "RP1_4": (1, 4),
    "RP1_8": (1, 8),
    "RP1_10": (1, 10),
    "RP1_256": (1, 256),
    "RP3_256": (3, 256),
}


class ModuleValidationError(ValueError):
    """A canonical Steenrod-module record violates the public contract."""


class IncompleteModuleError(ModuleValidationError):
    """An export would strengthen an unknown action slot to zero."""


class UnsupportedExportError(ValueError):
    """The requested consumer cannot represent the canonical module."""

    def __init__(self, format_name: str, reason: str) -> None:
        self.format_name = format_name
        self.reason = reason
        super().__init__(f"{format_name} export unsupported: {reason}")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _without_review_metadata(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _without_review_metadata(item)
            for key, item in value.items()
            if key not in {"review", "review_state"}
        }
    if isinstance(value, list):
        return [_without_review_metadata(item) for item in value]
    return value


def _content_sha256(module: Mapping[str, Any]) -> str:
    content = {key: value for key, value in module.items() if key != "content_sha256"}
    immutable_content = _without_review_metadata(content)
    return hashlib.sha256(_canonical_json(immutable_content).encode("utf-8")).hexdigest()


def _basis_for(spectrum_id: str, degrees: list[int]) -> list[dict[str, Any]]:
    multiplicities: dict[int, int] = {}
    for degree in degrees:
        multiplicities[degree] = multiplicities.get(degree, 0) + 1
    ordinals: dict[int, int] = {}
    basis = []
    for index, degree in enumerate(degrees):
        ordinal = ordinals.get(degree, 0)
        ordinals[degree] = ordinal + 1
        suffix = f"_{ordinal}" if multiplicities[degree] > 1 else ""
        basis.append(
            {
                "basis_id": f"{spectrum_id}:b{index}",
                "name": f"x{degree}{suffix}",
                "degree": degree,
                "ordinal": ordinal,
            }
        )
    return basis


def _endpoint_index(endpoint: Any, basis: list[Mapping[str, Any]]) -> int:
    if isinstance(endpoint, int):
        degree, ordinal = endpoint, 0
    elif (
        isinstance(endpoint, list)
        and len(endpoint) == 2
        and all(isinstance(item, int) for item in endpoint)
    ):
        degree, ordinal = endpoint
    else:
        raise ModuleValidationError(f"invalid SSeqCpp source endpoint: {endpoint!r}")
    matches = [
        index
        for index, element in enumerate(basis)
        if element["degree"] == degree and element["ordinal"] == ordinal
    ]
    if len(matches) != 1:
        raise ModuleValidationError(f"unresolved SSeqCpp source endpoint: {endpoint!r}")
    return matches[0]


def _target_indices(endpoint: Any, basis: list[Mapping[str, Any]]) -> list[int]:
    if isinstance(endpoint, int):
        return [_endpoint_index(endpoint, basis)]
    if not isinstance(endpoint, list) or len(endpoint) < 2:
        raise ModuleValidationError(f"invalid SSeqCpp target endpoint: {endpoint!r}")
    degree = endpoint[0]
    if not isinstance(degree, int) or not all(
        isinstance(ordinal, int) for ordinal in endpoint[1:]
    ):
        raise ModuleValidationError(f"invalid SSeqCpp target endpoint: {endpoint!r}")
    return [_endpoint_index([degree, ordinal], basis) for ordinal in endpoint[1:]]


def _required_slots(
    basis: list[Mapping[str, Any]],
) -> list[tuple[str, int]]:
    top_degree = max(element["degree"] for element in basis)
    slots = []
    for element in basis:
        square_degree = 1
        while element["degree"] + square_degree <= top_degree:
            slots.append((element["basis_id"], square_degree))
            square_degree *= 2
    return slots


def _finite_module(
    spectrum_id: str,
    degrees: list[int],
    nonzero_actions: Mapping[tuple[int, int], set[int]],
    *,
    import_encoding: str,
    source_locator: str,
) -> dict[str, Any]:
    basis = _basis_for(spectrum_id, degrees)
    index_by_id = {element["basis_id"]: index for index, element in enumerate(basis)}
    slots = _required_slots(basis)
    actions = []
    for source_id, square_degree in slots:
        source_index = index_by_id[source_id]
        targets = sorted(nonzero_actions.get((source_index, square_degree), set()))
        actions.append(
            {
                "source_basis_id": source_id,
                "square_degree": square_degree,
                "knowledge_state": "exact",
                "target_basis_ids": [basis[index]["basis_id"] for index in targets],
            }
        )
    source_snapshot = "zenodo:14875701:v126.3.cw49"
    module = {
        "schema_version": MODULE_SCHEMA_VERSION,
        "spectrum_id": spectrum_id,
        "module_type": "finite_basis",
        "coefficient_field": "F2",
        "reduced": True,
        "category": "stable",
        "grading_convention": "cohomological",
        "suspension_shift": 0,
        "basis_version": f"cw49-v126.3:{spectrum_id}",
        "basis": basis,
        "actions": actions,
        "completeness": {
            "knowledge_state": "exact",
            "slots": [
                {"source_basis_id": source_id, "square_degree": square_degree}
                for source_id, square_degree in slots
            ],
        },
        "source_snapshot": source_snapshot,
        "source_locator": source_locator,
        "evidence": {
            "evidence_kind": "imported_source",
            "source_snapshot": source_snapshot,
            "source_locator": source_locator,
            "review_state": "imported_unreviewed",
        },
        "import_encoding": import_encoding,
        "review_state": "imported_unreviewed",
    }
    module["content_sha256"] = _content_sha256(module)
    return module


def _module_from_adams_source(
    spectrum_id: str, definition: Mapping[str, Any]
) -> dict[str, Any]:
    if definition.get("free") is True:
        degrees = list(definition["cells_gen"])
        operations: list[Any] = []
        import_encoding = "legacy_free_adams_e2"
    else:
        degrees = list(definition["cells"])
        operations = list(definition["operations"])
        import_encoding = "explicit_cells"
    if not degrees or not all(isinstance(degree, int) for degree in degrees):
        raise ModuleValidationError(f"{spectrum_id} source cells are invalid")
    basis = _basis_for(spectrum_id, degrees)
    nonzero: dict[tuple[int, int], set[int]] = {}
    for operation in operations:
        if not isinstance(operation, list) or len(operation) != 2:
            raise ModuleValidationError(f"{spectrum_id} source operation is invalid")
        source_index = _endpoint_index(operation[0], basis)
        targets = _target_indices(operation[1], basis)
        source_degree = basis[source_index]["degree"]
        target_degrees = {basis[index]["degree"] for index in targets}
        if len(target_degrees) != 1:
            raise ModuleValidationError(f"{spectrum_id} operation mixes target degrees")
        square_degree = next(iter(target_degrees)) - source_degree
        slot = (source_index, square_degree)
        image = nonzero.setdefault(slot, set())
        for target in targets:
            if target in image:
                image.remove(target)
            else:
                image.add(target)
    return _finite_module(
        spectrum_id,
        degrees,
        nonzero,
        import_encoding=import_encoding,
        source_locator=(
            "zenodo:14875701:v126.3.cw49:programs.rar!"
            f"/programs/Adams.json#/CW_complexes/{spectrum_id}"
        ),
    )


def _projective_module(spectrum_id: str, first: int, last: int) -> dict[str, Any]:
    degrees = list(range(first, last + 1))
    nonzero: dict[tuple[int, int], set[int]] = {}
    for source_index, degree in enumerate(degrees):
        square_degree = 1
        while degree + square_degree <= last:
            if square_degree <= degree and not (square_degree & (degree - square_degree)):
                nonzero[(source_index, square_degree)] = {
                    source_index + square_degree
                }
            square_degree *= 2
    return _finite_module(
        spectrum_id,
        degrees,
        nonzero,
        import_encoding="sseqcpp_builtin_projective_formula",
        source_locator=(
            "sseqcpp:23d12c973db2b294a6c00c15bd106e70b0af3fa6:"
            "Adams/complexes.cpp#projective-formula"
        ),
    )


def _fphi_module() -> dict[str, Any]:
    degrees = [0, *range(2, 263)]
    degree_index = {degree: index for index, degree in enumerate(degrees)}
    nonzero: dict[tuple[int, int], set[int]] = {}
    square_degree = 2
    while square_degree <= 256:
        nonzero[(0, square_degree)] = {degree_index[square_degree]}
        square_degree *= 2
    for source_degree in range(2, 263):
        n = source_degree - 1
        square_degree = 1
        while source_degree + square_degree <= 262:
            if square_degree <= n and not (square_degree & (n - square_degree)):
                nonzero[(degree_index[source_degree], square_degree)] = {
                    degree_index[source_degree + square_degree]
                }
            square_degree *= 2
    return _finite_module(
        "Fphi",
        degrees,
        nonzero,
        import_encoding="sseqcpp_builtin_fphi_formula",
        source_locator=(
            "sseqcpp:23d12c973db2b294a6c00c15bd106e70b0af3fa6:"
            "Adams/complexes.cpp#Coh_Fphi"
        ),
    )


def _tmf_module() -> dict[str, Any]:
    source_snapshot = "zenodo:14875701:v126.3.cw49"
    source_locator = (
        "sseqcpp:23d12c973db2b294a6c00c15bd106e70b0af3fa6:"
        "Adams/complexes.cpp#tmf"
    )
    module = {
        "schema_version": MODULE_SCHEMA_VERSION,
        "spectrum_id": "tmf",
        "module_type": "profile",
        "coefficient_field": "F2",
        "reduced": True,
        "category": "stable",
        "grading_convention": "cohomological",
        "suspension_shift": 0,
        "basis_version": "cw49-v126.3:tmf",
        "basis": [],
        "actions": [],
        "profile": {"basis": "milnor", "truncated": True, "p_part": [3, 2, 1]},
        "completeness": {
            "knowledge_state": "exact",
            "scope": "infinite_milnor_profile",
        },
        "source_snapshot": source_snapshot,
        "source_locator": source_locator,
        "evidence": {
            "evidence_kind": "imported_source",
            "source_snapshot": source_snapshot,
            "source_locator": source_locator,
            "review_state": "imported_unreviewed",
        },
        "import_encoding": "sseqcpp_builtin_milnor_profile",
        "review_state": "imported_unreviewed",
    }
    module["content_sha256"] = _content_sha256(module)
    return module


def _display_name(spectrum_id: str) -> dict[str, str]:
    if spectrum_id == "S0":
        return {"plain": "S0", "tex": "S^0"}
    if spectrum_id == "tmf":
        return {"plain": "tmf", "tex": "\\mathrm{tmf}"}
    return {"plain": spectrum_id, "tex": f"\\mathrm{{{spectrum_id}}}"}


def _normalize_cw49_spectra(
    upstream: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    spectra = []
    for spectrum_id in CW49_SPECTRUM_IDS:
        if spectrum_id == "tmf":
            module = _tmf_module()
        elif spectrum_id in _PROJECTIVE_LIMITS:
            module = _projective_module(spectrum_id, *_PROJECTIVE_LIMITS[spectrum_id])
        elif spectrum_id == "Fphi":
            module = _fphi_module()
        elif spectrum_id in upstream:
            module = _module_from_adams_source(spectrum_id, upstream[spectrum_id])
        else:
            raise ModuleValidationError(f"missing cw49 source for {spectrum_id}")
        validate_module(module)
        spectra.append(
            {
                "spectrum_id": spectrum_id,
                "slug": spectrum_id.lower().replace("_", "-"),
                "name": _display_name(spectrum_id),
                "object_kind": (
                    "ring_spectrum"
                    if spectrum_id in {"S0", "tmf"}
                    else "module_spectrum"
                ),
                "source_decode_state": "complete",
                "review_state": "imported_unreviewed",
                "module": module,
            }
        )
    return spectra


def load_cw49_corpus(path: Path | str | None = None) -> dict[str, Any]:
    """Load a fresh copy of the pinned, imported cw49 canonical corpus."""

    corpus_path = Path(path) if path is not None else CORPUS_PATH
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    if corpus.get("schema_version") != CORPUS_SCHEMA_VERSION:
        raise ModuleValidationError("unsupported Steenrod corpus schema_version")
    upstream_path = (
        corpus_path.with_name("upstream-adams.json")
        if path is not None
        else UPSTREAM_ADAMS_PATH
    )
    expected_upstream_sha256 = corpus["source"]["module_source"][
        "normalized_subset_sha256"
    ]
    actual_upstream_sha256 = hashlib.sha256(upstream_path.read_bytes()).hexdigest()
    if actual_upstream_sha256 != expected_upstream_sha256:
        raise ModuleValidationError("normalized upstream Adams source hash mismatch")
    upstream = json.loads(upstream_path.read_text(encoding="utf-8"))["CW_complexes"]
    generated_ids = {"tmf", "Fphi", *_PROJECTIVE_LIMITS}
    expected_upstream_ids = set(CW49_SPECTRUM_IDS) - generated_ids
    if set(upstream) != expected_upstream_ids:
        raise ModuleValidationError("normalized upstream Adams source coverage mismatch")
    spectra = _normalize_cw49_spectra(upstream)
    if corpus.get("spectra") != spectra:
        raise ModuleValidationError(
            "persisted cw49 spectra do not match the pinned normalization"
        )
    return copy.deepcopy(corpus)


def _module_from(record: Mapping[str, Any]) -> Mapping[str, Any]:
    module = record.get("module", record)
    if not isinstance(module, Mapping):
        raise ModuleValidationError("module must be an object")
    return module


def _spectrum_id(record: Mapping[str, Any]) -> str:
    spectrum_id = record.get("spectrum_id")
    if isinstance(spectrum_id, str) and spectrum_id:
        return spectrum_id
    module = _module_from(record)
    module_id = module.get("spectrum_id")
    if isinstance(module_id, str) and module_id:
        return module_id
    raise ModuleValidationError("spectrum_id is required for this export")


_ADEM_VALIDATED_HASHES: set[str] = set()


def validate_module(module: Mapping[str, Any]) -> None:
    """Validate one canonical record without promoting unknown slots to zero."""

    if "content_sha256" in module and module["content_sha256"] != _content_sha256(module):
        raise ModuleValidationError("content_sha256 does not match canonical content")
    if module.get("schema_version") != MODULE_SCHEMA_VERSION:
        raise ModuleValidationError("unsupported Steenrod module schema_version")
    if module.get("coefficient_field") != "F2":
        raise ModuleValidationError("coefficient_field must be F2")
    if not isinstance(module.get("reduced"), bool):
        raise ModuleValidationError("reduced must state the cohomology convention")
    if module.get("category") not in {"stable", "unstable"}:
        raise ModuleValidationError("category must be stable or unstable")
    if module.get("grading_convention") != "cohomological":
        raise ModuleValidationError("grading_convention must be cohomological")
    if module.get("module_type") not in {"finite_basis", "profile"}:
        raise ModuleValidationError("module_type must be finite_basis or profile")
    for field_name in (
        "spectrum_id",
        "basis_version",
        "source_snapshot",
        "source_locator",
    ):
        if not isinstance(module.get(field_name), str) or not module[field_name]:
            raise ModuleValidationError(f"{field_name} must be a nonempty string")
    if not isinstance(module.get("suspension_shift"), int) or isinstance(
        module["suspension_shift"], bool
    ):
        raise ModuleValidationError("suspension_shift must be an integer")
    if module.get("review_state") not in {"imported_unreviewed", "accepted"}:
        raise ModuleValidationError(
            "module review_state must be imported_unreviewed or accepted"
        )
    evidence = module.get("evidence")
    if (
        not isinstance(evidence, Mapping)
        or evidence.get("evidence_kind") != "imported_source"
        or evidence.get("review_state") not in {"imported_unreviewed", "accepted"}
        or not isinstance(evidence.get("source_snapshot"), str)
        or not isinstance(evidence.get("source_locator"), str)
        or evidence.get("source_snapshot") != module["source_snapshot"]
        or evidence.get("source_locator") != module["source_locator"]
    ):
        raise ModuleValidationError("imported module requires typed source evidence")

    if module["module_type"] == "profile":
        profile = module.get("profile")
        if (
            not isinstance(profile, Mapping)
            or profile.get("basis") != "milnor"
            or not isinstance(profile.get("truncated"), bool)
            or not isinstance(profile.get("p_part"), list)
            or not profile["p_part"]
            or not all(
                isinstance(part, int) and not isinstance(part, bool) and part > 0
                for part in profile["p_part"]
            )
        ):
            raise ModuleValidationError("profile module requires Milnor profile metadata")
        if module.get("basis") != [] or module.get("actions") != []:
            raise ModuleValidationError(
                "profile module cannot also contain a finite basis or actions"
            )
        completeness = module.get("completeness")
        if (
            not isinstance(completeness, Mapping)
            or completeness.get("knowledge_state") != "exact"
            or completeness.get("scope") != "infinite_milnor_profile"
        ):
            raise ModuleValidationError(
                "profile module requires exact infinite-profile completeness"
            )
        return

    basis = module.get("basis")
    actions = module.get("actions")
    if not isinstance(basis, list) or not basis:
        raise ModuleValidationError("finite_basis module requires a nonempty basis")
    if not isinstance(actions, list):
        raise ModuleValidationError("actions must be a list")
    basis_ids: set[str] = set()
    basis_names: set[str] = set()
    next_ordinal_by_degree: dict[int, int] = {}
    previous_key: tuple[int, int] | None = None
    for element in basis:
        basis_id = element.get("basis_id")
        name = element.get("name")
        degree = element.get("degree")
        ordinal = element.get("ordinal")
        if not isinstance(basis_id, str) or not basis_id or basis_id in basis_ids:
            raise ModuleValidationError("basis IDs must be nonempty and unique")
        if not isinstance(name, str) or not name or name in basis_names:
            raise ModuleValidationError("basis names must be nonempty and unique")
        if (
            not isinstance(degree, int)
            or isinstance(degree, bool)
            or not isinstance(ordinal, int)
            or isinstance(ordinal, bool)
            or ordinal < 0
        ):
            raise ModuleValidationError("basis degree and ordinal must be integers")
        expected_ordinal = next_ordinal_by_degree.get(degree, 0)
        if ordinal != expected_ordinal:
            raise ModuleValidationError(
                "basis ordinal must be contiguous within each degree"
            )
        next_ordinal_by_degree[degree] = expected_ordinal + 1
        key = (degree, ordinal)
        if previous_key is not None and key <= previous_key:
            raise ModuleValidationError("basis must be ordered by degree and ordinal")
        previous_key = key
        basis_ids.add(basis_id)
        basis_names.add(name)

    action_slots: set[tuple[str, int]] = set()
    degree_by_id = {element["basis_id"]: element["degree"] for element in basis}
    for action in actions:
        source = action.get("source_basis_id")
        square_degree = action.get("square_degree")
        targets = action.get("target_basis_ids")
        slot = (source, square_degree)
        if source not in basis_ids:
            raise ModuleValidationError("action source is not in the basis")
        if (
            not isinstance(square_degree, int)
            or isinstance(square_degree, bool)
            or square_degree <= 0
            or square_degree & (square_degree - 1)
        ):
            raise ModuleValidationError("square_degree must be a positive power of two")
        if action.get("knowledge_state") != "exact":
            raise ModuleValidationError("recorded action images must be exact")
        if slot in action_slots:
            raise ModuleValidationError("action slots must be unique")
        if not isinstance(targets, list) or len(targets) != len(set(targets)):
            raise ModuleValidationError("action targets must be a duplicate-free list")
        for target in targets:
            if target not in basis_ids:
                raise ModuleValidationError("action target is not in the basis")
            if degree_by_id[target] != degree_by_id[source] + square_degree:
                raise ModuleValidationError("action target has the wrong degree")
        if (
            module["category"] == "unstable"
            and square_degree > degree_by_id[source]
            and targets
        ):
            raise ModuleValidationError(
                "instability requires Sq^i(x)=0 when i exceeds degree(x)"
            )
        action_slots.add(slot)

    completeness = module.get("completeness")
    if not isinstance(completeness, Mapping) or completeness.get(
        "knowledge_state"
    ) not in {"exact", "unknown", "not_computed", "bounded"}:
        raise ModuleValidationError("finite module requires typed action completeness")
    raw_slots = completeness.get("slots")
    if not isinstance(raw_slots, list) or not all(
        isinstance(slot, Mapping) for slot in raw_slots
    ):
        raise ModuleValidationError("action completeness slots must be a list")
    for slot in raw_slots:
        source_basis_id = slot.get("source_basis_id")
        square_degree = slot.get("square_degree")
        if source_basis_id not in basis_ids:
            raise ModuleValidationError(
                "action completeness source is not in the basis"
            )
        if (
            not isinstance(square_degree, int)
            or isinstance(square_degree, bool)
            or square_degree <= 0
            or square_degree & (square_degree - 1)
        ):
            raise ModuleValidationError(
                "action completeness square_degree must be a positive power of two"
            )
    covered_slots = {
        (slot.get("source_basis_id"), slot.get("square_degree"))
        for slot in raw_slots
    }
    if len(covered_slots) != len(raw_slots):
        raise ModuleValidationError("action completeness slots must be unique")

    required_slots = set(_required_slots(basis))
    if not covered_slots <= required_slots:
        raise ModuleValidationError("completeness names a slot outside finite support")
    if completeness["knowledge_state"] != "exact" and covered_slots:
        raise ModuleValidationError("only exact completeness may cover action slots")

    is_complete = (
        completeness["knowledge_state"] == "exact"
        and covered_slots == required_slots
        and action_slots == required_slots
    )
    if not is_complete:
        return

    module_hash = module.get("content_sha256")
    if isinstance(module_hash, str) and module_hash in _ADEM_VALIDATED_HASHES:
        return
    operators = _all_square_operators(module)
    span = max(degree_by_id.values()) - min(degree_by_id.values())
    if len(set(degree_by_id.values())) == len(basis):
        compositions: dict[tuple[int, int], int] = {}

        def composition_code(left_degree: int, right_degree: int) -> int:
            key = (left_degree, right_degree)
            if key not in compositions:
                code = 0
                for source_index, intermediates in enumerate(
                    operators[right_degree]
                ):
                    if intermediates:
                        intermediate = intermediates.bit_length() - 1
                        if operators[left_degree][intermediate]:
                            code |= 1 << source_index
                compositions[key] = code
            return compositions[key]

        for left_degree in range(1, span + 1):
            for right_degree in range(1, span + 1):
                if (
                    left_degree >= 2 * right_degree
                    or left_degree + right_degree > span
                ):
                    continue
                lhs_code = composition_code(left_degree, right_degree)
                rhs_code = 0
                for t in range(left_degree // 2 + 1):
                    if math.comb(
                        right_degree - t - 1, left_degree - 2 * t
                    ) % 2:
                        rhs_code ^= composition_code(
                            left_degree + right_degree - t, t
                        )
                if lhs_code != rhs_code:
                    raise ModuleValidationError(
                        f"Adem relation fails for Sq^{left_degree} Sq^{right_degree}"
                    )
        if isinstance(module_hash, str):
            _ADEM_VALIDATED_HASHES.add(module_hash)
        return

    zero = [0] * len(basis)
    for left_degree in range(1, span + 1):
        for right_degree in range(1, span + 1):
            if left_degree >= 2 * right_degree or left_degree + right_degree > span:
                continue
            lhs = _compose_operators(
                operators[left_degree], operators[right_degree]
            )
            rhs = zero
            for t in range(left_degree // 2 + 1):
                if math.comb(right_degree - t - 1, left_degree - 2 * t) % 2:
                    rhs = _xor_operators(
                        rhs,
                        _compose_operators(
                            operators[left_degree + right_degree - t],
                            operators[t],
                        ),
                    )
            if lhs != rhs:
                raise ModuleValidationError(
                    f"Adem relation fails for Sq^{left_degree} Sq^{right_degree}"
                )
    if isinstance(module_hash, str):
        _ADEM_VALIDATED_HASHES.add(module_hash)


def _require_complete(module: Mapping[str, Any]) -> None:
    if module["module_type"] != "finite_basis":
        return
    required_slots = set(_required_slots(module["basis"]))
    action_slots = {
        (action["source_basis_id"], action["square_degree"])
        for action in module["actions"]
    }
    completeness = module["completeness"]
    covered_slots = {
        (slot["source_basis_id"], slot["square_degree"])
        for slot in completeness["slots"]
    }
    if (
        completeness["knowledge_state"] != "exact"
        or covered_slots != required_slots
        or action_slots != required_slots
    ):
        raise IncompleteModuleError(
            "export requires an explicit exact image for every finite-support slot"
        )


def _require_exportable(record: Mapping[str, Any], format_name: str) -> Mapping[str, Any]:
    module = _module_from(record)
    outer_spectrum_id = record.get("spectrum_id")
    if (
        isinstance(outer_spectrum_id, str)
        and outer_spectrum_id
        and outer_spectrum_id != module.get("spectrum_id")
    ):
        raise ModuleValidationError(
            "spectrum record and Steenrod module subject do not match"
        )
    validate_module(module)
    _require_complete(module)
    if module["module_type"] == "profile" and format_name in {
        "bruner",
        "sseqcpp",
    }:
        raise UnsupportedExportError(format_name, "infinite_profile")
    return module


def export_sseq(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return native SpectralSequences/sseq module JSON."""

    module = _require_exportable(record, "sseq")
    if module["module_type"] == "profile":
        return {
            "p": 2,
            "type": "finite dimensional module",
            "algebra": ["milnor"],
            "profile": {
                "truncated": module["profile"]["truncated"],
                "p_part": copy.deepcopy(module["profile"]["p_part"]),
            },
            "gens": {"x0": 0},
            "actions": [],
        }
    name_by_id = {element["basis_id"]: element["name"] for element in module["basis"]}
    degree_by_name = {element["name"]: element["degree"] for element in module["basis"]}
    actions = []
    for action in module["actions"]:
        if not action["target_basis_ids"]:
            continue
        target = " + ".join(name_by_id[item] for item in action["target_basis_ids"])
        actions.append(
            f"Sq{action['square_degree']} {name_by_id[action['source_basis_id']]} = {target}"
        )
    return {
        "p": 2,
        "type": "finite dimensional module",
        "gens": degree_by_name,
        "actions": actions,
    }


def export_sseqcpp(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return a native SSeqCpp ``Adams.json`` fragment."""

    module = _require_exportable(record, "sseqcpp")
    spectrum_id = _spectrum_id(record)
    basis = module["basis"]
    cells = [element["degree"] for element in basis]
    counts: dict[int, int] = {}
    for degree in cells:
        counts[degree] = counts.get(degree, 0) + 1
    basis_by_id = {element["basis_id"]: element for element in basis}

    def endpoint(basis_id: str) -> int | list[int]:
        element = basis_by_id[basis_id]
        if counts[element["degree"]] == 1:
            return element["degree"]
        return [element["degree"], element["ordinal"]]

    operations: list[list[Any]] = []
    incoming_by_degree: dict[int, list[int]] = {}
    for action in module["actions"]:
        target_ids = action["target_basis_ids"]
        if not target_ids:
            continue
        targets = [basis_by_id[target_id] for target_id in target_ids]
        target_degree = targets[0]["degree"]
        if len(targets) == 1 and counts[target_degree] == 1:
            target_endpoint: int | list[int] = target_degree
        else:
            target_endpoint = [
                target_degree,
                *(target["ordinal"] for target in targets),
            ]
        operations.append([endpoint(action["source_basis_id"]), target_endpoint])
        mask = 0
        for target in targets:
            mask ^= 1 << target["ordinal"]
        incoming_by_degree.setdefault(target_degree, []).append(mask)

    cells_gen: list[int] = []
    for degree in sorted(counts):
        pivots: dict[int, int] = {}
        for vector in incoming_by_degree.get(degree, []):
            while vector:
                pivot = vector.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = vector
                    break
                vector ^= pivots[pivot]
        cells_gen.extend([degree] * (counts[degree] - len(pivots)))
    return {
        "CW_complexes": {
            spectrum_id: {
                "cells": cells,
                "cells_gen": cells_gen,
                "operations": operations,
            }
        }
    }


def export_bruner(record: Mapping[str, Any]) -> str:
    """Return a Bruner Ext 1.9.5 module definition."""

    module = _require_exportable(record, "bruner")
    degrees = " ".join(str(element["degree"]) for element in module["basis"])
    lines = [str(len(module["basis"])), degrees]
    operators = _all_square_operators(module)
    top_degree = max(element["degree"] for element in module["basis"])
    for source_index, element in enumerate(module["basis"]):
        for square_degree in range(1, top_degree - element["degree"] + 1):
            image = operators[square_degree][source_index]
            if not image:
                continue
            targets = [
                index for index in range(len(module["basis"])) if image & (1 << index)
            ]
            lines.append(
                " ".join(
                    [
                        str(source_index),
                        str(square_degree),
                        str(len(targets)),
                        *(str(target) for target in targets),
                    ]
                )
            )
    return "\n".join(lines) + "\n"


def _compose_operators(left: list[int], right: list[int]) -> list[int]:
    result = []
    for intermediates in right:
        image = 0
        while intermediates:
            low_bit = intermediates & -intermediates
            index = low_bit.bit_length() - 1
            image ^= left[index]
            intermediates ^= low_bit
        result.append(image)
    return result


def _xor_operators(left: list[int], right: list[int]) -> list[int]:
    return [left_image ^ right_image for left_image, right_image in zip(left, right)]


def _all_square_operators(module: Mapping[str, Any]) -> dict[int, list[int]]:
    """Derive the single-square operators from the power-of-two generators."""

    basis = module["basis"]
    size = len(basis)
    index_by_id = {element["basis_id"]: index for index, element in enumerate(basis)}
    span = max(element["degree"] for element in basis) - min(
        element["degree"] for element in basis
    )
    operators: dict[int, list[int]] = {0: [1 << index for index in range(size)]}
    power = 1
    actions_by_slot = {
        (action["source_basis_id"], action["square_degree"]): action
        for action in module["actions"]
    }
    while power <= span:
        operator = [0] * size
        for source_index, element in enumerate(basis):
            action = actions_by_slot.get((element["basis_id"], power))
            if action is None:
                continue
            for target_id in action["target_basis_ids"]:
                operator[source_index] ^= 1 << index_by_id[target_id]
        operators[power] = operator
        power *= 2

    for square_degree in range(1, span + 1):
        if square_degree & (square_degree - 1) == 0:
            continue
        leading_power = 1 << (square_degree.bit_length() - 1)
        remainder = square_degree - leading_power
        operator = _compose_operators(
            operators[remainder], operators[leading_power]
        )
        for t in range(1, remainder // 2 + 1):
            if math.comb(leading_power - t - 1, remainder - 2 * t) % 2:
                operator = _xor_operators(
                    operator,
                    _compose_operators(
                        operators[square_degree - t], operators[t]
                    ),
                )
        operators[square_degree] = operator
    return operators


def export_manifest(
    record: Mapping[str, Any], format_name: str, payload: str | Mapping[str, Any]
) -> dict[str, Any]:
    """Describe one deterministic external-format payload."""

    if format_name not in {"bruner", "sseq", "sseqcpp"}:
        raise ModuleValidationError(f"unsupported export format: {format_name}")
    module = _require_exportable(record, format_name)
    encoded = (
        payload.encode("utf-8")
        if isinstance(payload, str)
        else _canonical_json(payload).encode("utf-8")
    )
    return {
        "schema_version": "homology-db.steenrod-export-manifest/1",
        "spectrum_id": _spectrum_id(record),
        "basis_version": module["basis_version"],
        "suspension_shift": module["suspension_shift"],
        "source_snapshot": module["source_snapshot"],
        "adapter_version": "homology-db.steenrod/1",
        "format": format_name,
        "payload_sha256": hashlib.sha256(encoded).hexdigest(),
    }


def _render_export_payload(payload: str | Mapping[str, Any]) -> str:
    if isinstance(payload, str):
        return payload
    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list the pinned cw49 spectra")
    validate_parser = commands.add_parser("validate", help="validate canonical records")
    validate_parser.add_argument("spectrum_id", nargs="?")
    show_parser = commands.add_parser("show", help="print one canonical spectrum record")
    show_parser.add_argument("spectrum_id")
    for command in ("export", "manifest"):
        export_parser = commands.add_parser(command)
        export_parser.add_argument("spectrum_id")
        export_parser.add_argument(
            "--format", required=True, choices=("sseq", "sseqcpp", "bruner")
        )
    args = parser.parse_args(argv)
    corpus = load_cw49_corpus()
    by_id = {spectrum["spectrum_id"]: spectrum for spectrum in corpus["spectra"]}

    def record_for(spectrum_id: str) -> dict[str, Any]:
        if spectrum_id not in by_id:
            parser.error(f"unknown cw49 spectrum: {spectrum_id}")
        return by_id[spectrum_id]

    if args.command == "list":
        result = {
            "schema_version": corpus["schema_version"],
            "normalization_state": corpus["source"]["normalization_state"],
            "spectrum_count": len(corpus["spectra"]),
            "finite_module_count": sum(
                spectrum["module"]["module_type"] == "finite_basis"
                for spectrum in corpus["spectra"]
            ),
            "spectra": [
                {
                    "spectrum_id": spectrum["spectrum_id"],
                    "module_type": spectrum["module"]["module_type"],
                    "review_state": spectrum["review_state"],
                }
                for spectrum in corpus["spectra"]
            ],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "show":
        print(
            json.dumps(
                record_for(args.spectrum_id),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "validate":
        records = (
            [record_for(args.spectrum_id)]
            if args.spectrum_id
            else corpus["spectra"]
        )
        for spectrum in records:
            validate_module(spectrum["module"])
        print(
            json.dumps(
                {
                    "status": "ok",
                    "validated_spectrum_count": len(records),
                    "normalization_state": corpus["source"]["normalization_state"],
                },
                sort_keys=True,
            )
        )
        return 0

    record = record_for(args.spectrum_id)
    exporters = {
        "sseq": export_sseq,
        "sseqcpp": export_sseqcpp,
        "bruner": export_bruner,
    }
    try:
        payload = exporters[args.format](record)
    except UnsupportedExportError as error:
        print(
            json.dumps(
                {
                    "status": "unsupported",
                    "format": error.format_name,
                    "reason": error.reason,
                    "spectrum_id": args.spectrum_id,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    rendered_payload = _render_export_payload(payload)
    if args.command == "manifest":
        manifest = export_manifest(record, args.format, rendered_payload)
        sys.stdout.write(_render_export_payload(manifest))
    else:
        sys.stdout.write(rendered_payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
