#!/usr/bin/env python3
"""Materialize a written-accepted cw49 review into an AtlasSchema v5 database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from homology_db.steenrod_snapshot import materialize_steenrod_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--review-packet", type=Path, required=True)
    parser.add_argument("--coverage-report", type=Path, required=True)
    parser.add_argument("--acceptance-record", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = materialize_steenrod_snapshot(
        args.database.resolve(),
        args.review_packet.resolve(),
        args.coverage_report.resolve(),
        args.acceptance_record.resolve(),
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
