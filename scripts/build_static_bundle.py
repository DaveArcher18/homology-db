#!/usr/bin/env python3
"""Partition a validated self-contained atlas into a deterministic static site."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any


ATLAS_DATA = re.compile(
    r'(<script id="atlas-data" type="application/json">)(.*?)(</script>)',
    re.DOTALL,
)
DOCUMENT_SCHEMA = "homology-db.static-bundle-document/1"
BUNDLE_SCHEMA = "homology-db.static-atlas-bundle/1"
SAFE_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HEAVY_SPACE_KEYS = {
    "citations", "cohomology", "computations", "evidence", "homology",
    "models", "raw", "responses",
}
HEAVY_SPECTRUM_KEYS = {"module", "downloads", "provenance"}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_atlas(path: Path) -> tuple[str, dict[str, Any]]:
    html = path.read_text(encoding="utf-8")
    match = ATLAS_DATA.search(html)
    if match is None:
        raise ValueError("atlas has no embedded atlas-data document")
    atlas = json.loads(match.group(2))
    if not isinstance(atlas, dict) or not isinstance(atlas.get("snapshot"), dict):
        raise ValueError("embedded atlas data is not a complete read model")
    return html, atlas


def _catalog_space(space: dict[str, Any]) -> dict[str, Any]:
    result = {key: value for key, value in space.items() if key not in HEAVY_SPACE_KEYS}
    result["cohomology_record_count"] = len(space.get("cohomology", []))
    result["cohomology_coverage"] = [
        {
            "coefficient": record.get("coefficient"),
            "knowledge_state": record.get("knowledge_state"),
            "coverage": record.get("coverage"),
            "multiplication": record.get("algebra", {}).get("multiplication"),
            "human_review_state": record.get("provenance", {}).get("review_state"),
        }
        for record in space.get("cohomology", [])
    ]
    result["catalog_search"] = json.dumps(
        {
            "citations": space.get("citations", []),
            "models": space.get("models", []),
            "evidence": space.get("evidence", []),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    result["_document_path"] = f"data/spaces/{space['slug']}.json"
    return result


def _catalog_spectrum(spectrum: dict[str, Any]) -> dict[str, Any]:
    result = {
        key: value for key, value in spectrum.items() if key not in HEAVY_SPECTRUM_KEYS
    }
    result["_document_path"] = f"data/spectra/{spectrum['slug']}.json"
    return result


def partition(atlas: dict[str, Any]) -> dict[str, tuple[str, Any]]:
    spaces = atlas.get("conceptual_spaces", [])
    spectra = atlas.get("conceptual_spectra", [])
    for subject in [*spaces, *spectra]:
        slug = subject.get("slug")
        if not isinstance(slug, str) or SAFE_SLUG.fullmatch(slug) is None:
            raise ValueError(f"unsafe or missing subject slug: {slug!r}")
    documents: dict[str, tuple[str, Any]] = {
        "data/catalog.json": (
            "catalog",
            {
                "snapshot": atlas["snapshot"],
                "sections": atlas.get("sections", []),
                "conceptual_spaces": [_catalog_space(item) for item in spaces],
                "conceptual_spectra": [_catalog_spectrum(item) for item in spectra],
            },
        ),
        "data/shared/definitions.json": ("definitions", atlas.get("definitions", [])),
        "data/shared/family-rules.json": ("family_rules", atlas.get("family_rules", {})),
        "data/shared/teaching.json": ("teaching", atlas.get("teaching", {})),
        "data/shared/classical.json": ("classical", atlas.get("classical", {})),
    }
    for space in spaces:
        documents[f"data/spaces/{space['slug']}.json"] = ("space", space)
    for spectrum in spectra:
        documents[f"data/spectra/{spectrum['slug']}.json"] = ("spectrum", spectrum)
    return documents


def build_bundle(atlas_path: Path, output_directory: Path) -> dict[str, Any]:
    html, atlas = read_atlas(atlas_path)
    documents = partition(atlas)
    snapshot = atlas["snapshot"]
    payloads = {
        path: canonical_bytes(payload) for path, (_kind, payload) in documents.items()
    }
    aggregate = canonical_bytes([
        {"path": path, "payload_sha256": sha256(payloads[path]), "payload_bytes": len(payloads[path])}
        for path in sorted(documents)
    ])
    bundle_id = f"bundle-{sha256(aggregate)}"
    encoded: dict[str, bytes] = {}
    for path, (kind, payload) in documents.items():
        encoded[path] = canonical_bytes({
            "schema_version": DOCUMENT_SCHEMA,
            "bundle_id": bundle_id,
            "snapshot_id": snapshot.get("snapshot_id"),
            "source_commit": snapshot.get("source_commit"),
            "document_kind": kind,
            "payload": payload,
            "payload_sha256": sha256(payloads[path]),
        })

    bootstrap = {
        "mode": "sharded",
        "schema_version": BUNDLE_SCHEMA,
        "bundle_id": bundle_id,
        "manifest_path": "data/manifest.json",
    }
    safe_bootstrap = json.dumps(bootstrap, sort_keys=True, separators=(",", ":"))
    shell = ATLAS_DATA.sub(r"\1" + safe_bootstrap + r"\3", html, count=1).encode("utf-8")
    offline_name = f"homology-atlas-{bundle_id.removeprefix('bundle-')[:12]}.html"
    offline_path = f"downloads/{offline_name}"
    offline = html.encode("utf-8")
    inventory = [
        {
            "path": path,
            "media_type": "application/json",
            "bytes": len(encoded[path]),
            "sha256": sha256(encoded[path]),
            "document_kind": documents[path][0],
            **(
                {"subject_id": documents[path][1].get("id")}
                if documents[path][0] == "space"
                else {"subject_id": documents[path][1].get("spectrum_id", documents[path][1].get("id"))}
                if documents[path][0] == "spectrum"
                else {}
            ),
        }
        for path in sorted(encoded)
    ]
    manifest = {
        "schema_version": BUNDLE_SCHEMA,
        "bundle_id": bundle_id,
        "snapshot_id": snapshot.get("snapshot_id"),
        "source_commit": snapshot.get("source_commit"),
        "source_inputs_sha256": snapshot.get("source_inputs_sha256"),
        "release_status": snapshot.get("release_status"),
        "read_model_version": snapshot.get("schema_version"),
        "supported_coefficients": snapshot.get("supported_coefficients", []),
        "counts": {
            "spaces": len(atlas.get("conceptual_spaces", [])),
            "spectra": len(atlas.get("conceptual_spectra", [])),
            "documents": len(encoded),
        },
        "files": inventory,
        "shell": {"path": "index.html", "bytes": len(shell), "sha256": sha256(shell)},
        "offline_artifact": {"path": offline_path, "bytes": len(offline), "sha256": sha256(offline)},
        "aggregate_payload_sha256": sha256(aggregate),
    }
    manifest_bytes = canonical_bytes(manifest)

    output_directory.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output_directory.parent) as temporary:
        candidate = Path(temporary) / "site"
        candidate.mkdir()
        (candidate / "index.html").write_bytes(shell)
        for path, value in encoded.items():
            target = candidate / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
        manifest_target = candidate / "data" / "manifest.json"
        manifest_target.parent.mkdir(parents=True, exist_ok=True)
        manifest_target.write_bytes(manifest_bytes)
        offline_target = candidate / offline_path
        offline_target.parent.mkdir(parents=True, exist_ok=True)
        offline_target.write_bytes(offline)
        (candidate / ".nojekyll").touch()
        if output_directory.exists():
            shutil.rmtree(output_directory)
        candidate.rename(output_directory)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_bundle(args.atlas.resolve(), args.output.resolve())
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
