#!/usr/bin/env python3
"""Verify accepted releases or explicitly enabled public review previews."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from homology_db.steenrod import CW49_SPECTRUM_IDS
from scripts.export_static_atlas import (
    build_current_database,
    build_spectrum_read_model,
    build_steenrod_review_packet,
    export_atlas,
    materialize_accepted_steenrod_database,
    render_atlas,
    render_steenrod_coverage_report,
    source_commit,
    source_inputs_sha256,
    validate_steenrod_acceptance_record,
)


ATLAS_DATA = re.compile(
    r'<script id="atlas-data" type="application/json">(.*?)</script>', re.DOTALL
)
REQUIRED_REVIEWER = "Dan Isaksen"
MAX_ATLAS_BYTES = 5 * 1024 * 1024


def _slug_from_id(stable_id: str) -> str:
    slug = "".join(character if character.isalnum() else "-" for character in stable_id)
    return "-".join(part for part in slug.casefold().split("-") if part)


CW49_IDENTITY_PROJECTION = frozenset(
    (spectrum_id, _slug_from_id(spectrum_id)) for spectrum_id in CW49_SPECTRUM_IDS
)


class ReleaseGateError(ValueError):
    """The embedded spectrum release is not eligible for publication."""


def _without_review_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_review_metadata(item)
            for key, item in value.items()
            if key not in {"review", "review_state"}
        }
    if isinstance(value, list):
        return [_without_review_metadata(item) for item in value]
    return value


def candidate_sha256(spectra: list[dict[str, Any]]) -> str:
    payload = json.dumps(
        _without_review_metadata(spectra),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _with_review_state(value: Any, review_state: str) -> Any:
    if isinstance(value, dict):
        return {
            key: (
                review_state
                if key == "review_state"
                else _with_review_state(item, review_state)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_with_review_state(item, review_state) for item in value]
    return value


def _candidate_atlas_from_accepted(atlas: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(atlas)
    snapshot = candidate["snapshot"]
    snapshot.pop("spectrum_acceptance", None)
    snapshot.pop("spectrum_snapshot", None)
    snapshot.pop("spectrum_database_hash_kind", None)
    snapshot.pop("spectrum_database_sha256", None)
    snapshot.pop("spectrum_materialization", None)
    snapshot["spectrum_review_candidate"] = True
    snapshot["spectrum_release_status"] = "imported_unreviewed_review_candidate"
    snapshot["spectrum_source"] = _with_review_state(
        snapshot["spectrum_source"],
        "imported_unreviewed",
    )
    candidate["conceptual_spectra"] = _with_review_state(
        candidate["conceptual_spectra"],
        "imported_unreviewed",
    )
    return candidate


def load_atlas(path: Path) -> dict[str, Any]:
    match = ATLAS_DATA.search(path.read_text(encoding="utf-8"))
    if match is None:
        raise ReleaseGateError("atlas does not contain the embedded atlas-data payload")
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ReleaseGateError("embedded atlas-data payload must be an object")
    return value


def validate_spectra(
    spectra: list[dict[str, Any]],
    *,
    expected_review_state: str = "accepted",
) -> tuple[int, int]:
    if len(spectra) != 49:
        raise ReleaseGateError(
            f"a stable-spectrum release requires exactly 49 spectra, found {len(spectra)}"
        )
    if any(not isinstance(item, dict) for item in spectra):
        raise ReleaseGateError("every spectrum must be an object")
    identifiers = [item.get("spectrum_id") for item in spectra]
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise ReleaseGateError("every spectrum requires a stable spectrum_id")
    if len(set(identifiers)) != len(identifiers):
        raise ReleaseGateError("stable-spectrum release contains duplicate spectrum IDs")
    identity_projection = {
        (spectrum.get("spectrum_id"), spectrum.get("slug")) for spectrum in spectra
    }
    if identity_projection != CW49_IDENTITY_PROJECTION:
        raise ReleaseGateError(
            "stable-spectrum release does not match the exact cw49 spectrum identity projection"
        )

    finite_count = 0
    profile_count = 0
    for spectrum in spectra:
        if spectrum.get("source_decode_state") != "complete":
            raise ReleaseGateError(
                f"spectrum {spectrum['spectrum_id']} is not completely decoded"
            )
        if spectrum.get("review_state") != expected_review_state:
            raise ReleaseGateError(
                f"spectrum {spectrum['spectrum_id']} does not have review state "
                f"{expected_review_state}"
            )
        module = spectrum.get("module")
        if not isinstance(module, dict):
            raise ReleaseGateError(f"spectrum {spectrum['spectrum_id']} has no module")
        if module.get("review_state") != expected_review_state:
            raise ReleaseGateError(
                f"module for {spectrum['spectrum_id']} does not have review state "
                f"{expected_review_state}"
            )
        evidence = module.get("evidence")
        if not isinstance(evidence, dict) or evidence.get(
            "review_state"
        ) != "imported_unreviewed":
            raise ReleaseGateError(
                f"import evidence for {spectrum['spectrum_id']} must remain "
                "imported_unreviewed"
            )
        content_hash = module.get("content_sha256")
        if not isinstance(content_hash, str) or re.fullmatch(r"[0-9a-f]{64}", content_hash) is None:
            raise ReleaseGateError(
                f"module for {spectrum['spectrum_id']} has no canonical content hash"
            )
        module_type = module.get("module_type")
        if module_type == "finite_basis":
            finite_count += 1
            completeness = module.get("completeness")
            if not isinstance(completeness, dict) or completeness.get(
                "knowledge_state"
            ) != "exact":
                raise ReleaseGateError(
                    f"finite module for {spectrum['spectrum_id']} is incomplete"
                )
        elif module_type == "profile":
            profile_count += 1
            if spectrum["spectrum_id"] != "tmf":
                raise ReleaseGateError("tmf must be the only profile module")
        else:
            raise ReleaseGateError(
                f"module for {spectrum['spectrum_id']} has unsupported module_type"
            )
    if (finite_count, profile_count) != (48, 1):
        raise ReleaseGateError(
            "cw49 release requires 48 finite modules and one tmf profile module"
        )
    return finite_count, profile_count


def verify_deterministic_rebuild(atlas_path: Path, review_path: Path) -> str:
    """Require two fresh accepted builds to equal each other and the artifact."""

    try:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            output_paths: list[Path] = []
            for ordinal in range(2):
                database_path = directory / f"homology-db-{ordinal}.sqlite3"
                output_path = directory / f"atlas-{ordinal}.html"
                build_current_database(database_path)
                export_atlas(
                    database_path,
                    output_path,
                    steenrod_acceptance_record_path=review_path,
                )
                output_paths.append(output_path)
            first_bytes = output_paths[0].read_bytes()
            second_bytes = output_paths[1].read_bytes()
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        raise ReleaseGateError(
            f"canonical accepted rebuild failed: {error}"
        ) from error

    if first_bytes != second_bytes:
        raise ReleaseGateError(
            "canonical accepted rebuild is non-deterministic across fresh databases"
        )
    if atlas_path.read_bytes() != first_bytes:
        raise ReleaseGateError(
            "published atlas does not match the canonical accepted rebuild"
        )
    return hashlib.sha256(first_bytes).hexdigest()


def verify_deterministic_preview_rebuild(atlas_path: Path) -> str:
    """Require two fresh preview builds to equal each other and the artifact."""

    try:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            output_paths: list[Path] = []
            for ordinal in range(2):
                database_path = directory / f"homology-db-{ordinal}.sqlite3"
                output_path = directory / f"atlas-{ordinal}.html"
                build_current_database(database_path)
                export_atlas(
                    database_path,
                    output_path,
                    steenrod_review_candidate=True,
                    allow_public_review_preview=True,
                )
                output_paths.append(output_path)
            first_bytes = output_paths[0].read_bytes()
            second_bytes = output_paths[1].read_bytes()
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        raise ReleaseGateError(
            f"canonical public preview rebuild failed: {error}"
        ) from error

    if first_bytes != second_bytes:
        raise ReleaseGateError(
            "canonical public preview rebuild is non-deterministic across fresh databases"
        )
    if atlas_path.read_bytes() != first_bytes:
        raise ReleaseGateError(
            "published atlas does not match the canonical public preview rebuild"
        )
    return hashlib.sha256(first_bytes).hexdigest()


def verify_spectrum_materialization(
    snapshot: dict[str, Any],
    packet: dict[str, Any],
    coverage_report: str,
    review_path: Path,
) -> dict[str, Any]:
    if snapshot.get("spectrum_database_hash_kind") != "homology-db.sqlite-logical/2":
        raise ReleaseGateError(
            "accepted release requires the canonical materialized spectrum database"
        )
    spectrum_database_sha256 = snapshot.get("spectrum_database_sha256")
    if re.fullmatch(r"[0-9a-f]{64}", str(spectrum_database_sha256 or "")) is None:
        raise ReleaseGateError(
            "accepted release requires a valid materialized spectrum database SHA-256"
        )
    embedded = snapshot.get("spectrum_materialization")
    if not isinstance(embedded, dict):
        raise ReleaseGateError(
            "accepted release requires its materialized spectrum database summary"
        )
    try:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "steenrod-cw49-v1.sqlite3"
            actual = materialize_accepted_steenrod_database(
                database_path,
                packet,
                coverage_report,
                review_path,
            )
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        raise ReleaseGateError(
            f"could not rebuild the materialized spectrum database: {error}"
        ) from error
    if embedded != actual:
        raise ReleaseGateError(
            "embedded materialized spectrum database summary does not match a fresh build"
        )
    if (
        actual.get("logical_database_hash_kind")
        != snapshot["spectrum_database_hash_kind"]
        or actual.get("logical_database_sha256") != spectrum_database_sha256
    ):
        raise ReleaseGateError(
            "materialized spectrum database identity does not match its fresh build"
        )
    return actual


def verify(
    atlas_path: Path,
    review_path: Path | None,
    *,
    verify_rebuild: bool = False,
    allow_public_review_preview: bool = False,
) -> dict[str, Any]:
    atlas_bytes = atlas_path.stat().st_size
    if atlas_bytes > MAX_ATLAS_BYTES:
        raise ReleaseGateError(
            f"atlas is {atlas_bytes} bytes; the release limit is 5 MiB"
        )
    atlas = load_atlas(atlas_path)
    if "conceptual_spectra" not in atlas:
        return {"state": "legacy_space_only", "conceptual_spectrum_count": 0}
    spectra = atlas["conceptual_spectra"]
    if not isinstance(spectra, list):
        raise ReleaseGateError("conceptual_spectra must be a list")
    if not spectra:
        snapshot = atlas.get("snapshot")
        if (
            not isinstance(snapshot, dict)
            or snapshot.get("conceptual_spectrum_count") != 0
            or snapshot.get("spectrum_release_status") != "withheld_pending_review"
        ):
            raise ReleaseGateError(
                "an empty conceptual_spectra list must be explicitly withheld by its Snapshot"
            )
        return {"state": "withheld_space_only", "conceptual_spectrum_count": 0}
    snapshot = atlas.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ReleaseGateError("stable-spectrum release requires Snapshot metadata")
    spectrum_source = snapshot.get("spectrum_source")
    if not isinstance(spectrum_source, dict) or spectrum_source.get(
        "normalization_state"
    ) != "complete":
        raise ReleaseGateError("stable-spectrum source normalization is incomplete")
    if snapshot.get("source_database_hash_kind") != "homology-db.sqlite-logical/1":
        raise ReleaseGateError(
            "stable-spectrum release requires the canonical logical database hash"
        )
    if re.fullmatch(r"[0-9a-f]{64}", str(snapshot.get("source_database_sha256", ""))) is None:
        raise ReleaseGateError(
            "stable-spectrum release requires a valid logical database SHA-256"
        )
    public_preview = snapshot.get("spectrum_release_status") == "public_review_preview"
    if public_preview and not allow_public_review_preview:
        raise ReleaseGateError(
            "public review preview is not enabled for this deployment"
        )
    expected_review_state = "imported_unreviewed" if public_preview else "accepted"
    finite_count, profile_count = validate_spectra(
        spectra,
        expected_review_state=expected_review_state,
    )
    if snapshot.get("conceptual_spectrum_count") != 49:
        raise ReleaseGateError("stable-spectrum Snapshot must project exactly 49 spectra")
    if spectrum_source.get("review_state") != "imported_unreviewed":
        raise ReleaseGateError(
            "stable-spectrum import evidence must remain imported_unreviewed"
        )

    source_inputs_hash = snapshot.get("source_inputs_sha256")
    if re.fullmatch(r"[0-9a-f]{64}", str(source_inputs_hash or "")) is None:
        raise ReleaseGateError("stable-spectrum release requires a valid source-input SHA-256")
    current_source_inputs_hash = source_inputs_sha256()
    if source_inputs_hash != current_source_inputs_hash:
        raise ReleaseGateError("stable-spectrum release is bound to stale source inputs")
    embedded_source_commit = snapshot.get("source_commit")
    if re.fullmatch(r"[0-9a-f]{40}", str(embedded_source_commit or "")) is None:
        raise ReleaseGateError("stable-spectrum release requires a valid source commit")
    if embedded_source_commit != source_commit():
        raise ReleaseGateError("stable-spectrum release is bound to a stale source commit")

    try:
        canonical_spectra, canonical_source = build_spectrum_read_model()
    except ValueError as error:
        raise ReleaseGateError(
            f"could not reconstruct the pinned cw49 projection: {error}"
        ) from error
    expected_hash = candidate_sha256(canonical_spectra)
    actual_hash = candidate_sha256(spectra)
    if actual_hash != expected_hash:
        raise ReleaseGateError(
            "stable-spectrum release does not match the exact pinned cw49 projection"
        )
    if _without_review_metadata(spectrum_source) != _without_review_metadata(
        canonical_source
    ):
        raise ReleaseGateError(
            "stable-spectrum release does not match the exact pinned cw49 source projection"
        )

    if public_preview:
        if snapshot.get("spectrum_review_candidate") is not True:
            raise ReleaseGateError(
                "public review preview must retain review-candidate Snapshot metadata"
            )
        if review_path is not None:
            raise ReleaseGateError(
                "public review preview must not claim an acceptance record"
            )
        forbidden_metadata = {
            "spectrum_acceptance",
            "spectrum_snapshot",
            "spectrum_database_hash_kind",
            "spectrum_database_sha256",
            "spectrum_materialization",
        }
        embedded_forbidden = sorted(forbidden_metadata.intersection(snapshot))
        if embedded_forbidden:
            raise ReleaseGateError(
                "public review preview must not embed acceptance or finalization "
                "metadata: " + ", ".join(embedded_forbidden)
            )
        summary = {
            "state": "public_review_preview",
            "conceptual_spectrum_count": len(spectra),
            "finite_module_count": finite_count,
            "profile_module_count": profile_count,
            "candidate_sha256": actual_hash,
            "atlas_bytes": atlas_bytes,
        }
        if verify_rebuild:
            summary.update(
                {
                    "deterministic_rebuild_verified": True,
                    "canonical_atlas_sha256": verify_deterministic_preview_rebuild(
                        atlas_path
                    ),
                }
            )
        return summary

    if snapshot.get("spectrum_release_status") != "accepted_finalized" or snapshot.get(
        "spectrum_review_candidate"
    ) is not False:
        raise ReleaseGateError(
            "stable-spectrum release requires an accepted finalized spectrum Snapshot"
        )

    if review_path is None or not review_path.is_file():
        raise ReleaseGateError(
            "stable-spectrum release requires Dan Isaksen's review record"
        )
    review_bytes = review_path.read_bytes()
    review = json.loads(review_bytes)
    candidate_atlas = _candidate_atlas_from_accepted(atlas)
    candidate_html = render_atlas(candidate_atlas)
    packet = build_steenrod_review_packet(candidate_atlas, candidate_html)
    coverage_report = render_steenrod_coverage_report(packet)
    try:
        bindings = validate_steenrod_acceptance_record(
            review,
            packet,
            coverage_report,
        )
    except ValueError as error:
        raise ReleaseGateError(str(error)) from error

    acceptance_record_sha256 = hashlib.sha256(review_bytes).hexdigest()
    expected_acceptance = {
        "schema_version": review["schema_version"],
        "record_sha256": acceptance_record_sha256,
        "reviewer": review["reviewer"],
        "verdict": review["verdict"],
        "reviewed_at": review["reviewed_at"],
        "evidence": review["evidence"],
        "editorial_actor": review["editorial_actor"],
        "bindings": bindings,
    }
    if snapshot.get("spectrum_acceptance") != expected_acceptance:
        raise ReleaseGateError(
            "embedded spectrum acceptance does not match the supplied record"
        )
    projection = packet["release_projection"]
    expected_snapshot = {
        **projection["spectrum_snapshot"],
        "finalized_at": review["reviewed_at"],
        "assertion_reviews": projection["assertion_reviews"],
        "editorial_admissions": projection["editorial_admissions"],
    }
    if snapshot.get("spectrum_snapshot") != expected_snapshot:
        raise ReleaseGateError(
            "finalized spectrum Snapshot does not match the reviewed release manifests"
        )
    materialization = verify_spectrum_materialization(
        snapshot,
        packet,
        coverage_report,
        review_path,
    )
    summary = {
        "state": "reviewed_cw49",
        "conceptual_spectrum_count": len(spectra),
        "finite_module_count": finite_count,
        "profile_module_count": profile_count,
        "candidate_sha256": actual_hash,
        "reviewer": REQUIRED_REVIEWER,
        "spectrum_snapshot_id": expected_snapshot["snapshot_id"],
        "spectrum_snapshot_sha256": expected_snapshot["manifest_sha256"],
        "assertion_review_count": expected_snapshot["assertion_reviews"]["count"],
        "editorial_admission_count": expected_snapshot["editorial_admissions"][
            "count"
        ],
        "atlas_bytes": atlas_bytes,
        "spectrum_database_hash_kind": materialization[
            "logical_database_hash_kind"
        ],
        "spectrum_database_sha256": materialization["logical_database_sha256"],
    }
    if verify_rebuild:
        if review_path is None:
            raise AssertionError("accepted rebuild lacks its review record")
        summary.update(
            {
                "deterministic_rebuild_verified": True,
                "canonical_atlas_sha256": verify_deterministic_rebuild(
                    atlas_path,
                    review_path,
                ),
            }
        )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument(
        "--allow-public-review-preview",
        action="store_true",
        help=(
            "allow an exact imported-unreviewed cw49 preview that remains visibly "
            "awaiting review and carries no acceptance record"
        ),
    )
    parser.add_argument(
        "--verify-rebuild",
        action="store_true",
        help=(
            "for an accepted corpus, rebuild twice from fresh logical databases "
            "and require the checked artifact to match exactly"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = verify(
            args.atlas.resolve(),
            args.review.resolve() if args.review else None,
            verify_rebuild=args.verify_rebuild,
            allow_public_review_preview=args.allow_public_review_preview,
        )
    except (OSError, json.JSONDecodeError, ReleaseGateError) as error:
        print(f"release gate failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
