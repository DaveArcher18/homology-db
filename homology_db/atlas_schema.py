"""Versioned SQLite schema prototype for the named atlas.

This module is deliberately separate from :mod:`homology_db.preview`.  The
preview remains a frozen regression fixture; these migrations exercise the
production domain boundaries before a physical database is selected.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


SCHEMA_VERSION = "homology-db.atlas-schema/3"
MIGRATION_DIRECTORY = Path(__file__).with_name("migrations")


def _migration_files() -> list[Path]:
    return sorted(MIGRATION_DIRECTORY.glob("[0-9][0-9][0-9][0-9]_*.sql"))


class AtlasSchema:
    """Build and migrate the executable production-schema prototype."""

    @staticmethod
    def migrate(path: Path) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            for migration_path in _migration_files():
                version = int(migration_path.name.split("_", 1)[0])
                sql = migration_path.read_text(encoding="utf-8")
                migration_hash = hashlib.sha256(sql.encode("utf-8")).hexdigest()
                if version > 1:
                    existing = connection.execute(
                        "SELECT sha256 FROM schema_migration WHERE version = ?", (version,)
                    ).fetchone()
                    if existing:
                        if existing[0] != migration_hash:
                            raise ValueError(f"migration {version} hash changed")
                        continue
                elif connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'schema_migration'"
                ).fetchone():
                    existing = connection.execute(
                        "SELECT sha256 FROM schema_migration WHERE version = 1"
                    ).fetchone()
                    if existing:
                        if existing[0] != migration_hash:
                            raise ValueError("migration 1 hash changed")
                        continue
                connection.executescript(sql)
                connection.execute(
                    "INSERT INTO schema_migration(version, name, sha256) VALUES (?, ?, ?)",
                    (version, migration_path.name, migration_hash),
                )
                connection.commit()
            applied = connection.execute("SELECT MAX(version) FROM schema_migration").fetchone()[0]
        return f"homology-db.atlas-schema/{applied}"

    @staticmethod
    def build(path: Path) -> str:
        if path.exists():
            path.unlink()
        return AtlasSchema.migrate(path)

    @staticmethod
    def build_model_workload(path: Path, model_count: int, *, reverse: bool) -> dict[str, object]:
        """Build a deterministic logical workload in a chosen insertion order."""
        if model_count < 0:
            raise ValueError("model_count must be nonnegative")
        AtlasSchema.build(path)
        indices = list(range(model_count))
        if reverse:
            indices.reverse()
        with sqlite3.connect(path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            for index in indices:
                model_id = f"model:{index:04d}"
                model_record_hash = hashlib.sha256(
                    f"model|{model_id}|candidate|{index % 13}".encode("utf-8")
                ).hexdigest()
                connection.execute(
                    "INSERT INTO model VALUES (?, ?, ?, 'candidate', ?)",
                    (model_id, "finite_simplicial" if index % 2 == 0 else "finite_regular_cw",
                     index % 13, model_record_hash),
                )
                content_hash = hashlib.sha256(f"artifact|{model_id}".encode("utf-8")).hexdigest()
                artifact_record_hash = hashlib.sha256(
                    f"model-artifact|{model_id}|{content_hash}".encode("utf-8")
                ).hexdigest()
                connection.execute(
                    "INSERT INTO model_artifact VALUES (?, ?, NULL, ?, ?, ?)",
                    (f"model-artifact:{index:04d}", model_id, "prototype/json",
                     content_hash, artifact_record_hash),
                )
            connection.commit()
            connection.row_factory = sqlite3.Row
            models = [
                dict(row) for row in connection.execute(
                    "SELECT * FROM model ORDER BY model_id"
                )
            ]
            artifacts = [
                dict(row) for row in connection.execute(
                    "SELECT * FROM model_artifact ORDER BY model_artifact_id"
                )
            ]
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"SQLite integrity failure: {integrity}")
        canonical_bytes = json.dumps(
            {"models": models, "model_artifacts": artifacts},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return {
            "model_count": len(models),
            "model_artifact_count": len(artifacts),
            "first_model_id": models[0]["model_id"] if models else None,
            "last_model_id": models[-1]["model_id"] if models else None,
            "canonical_sha256": hashlib.sha256(canonical_bytes).hexdigest(),
            "canonical_bytes": canonical_bytes,
        }
