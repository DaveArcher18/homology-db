#!/usr/bin/env python3
"""Run one deterministic, module-preserving shard of the unittest suite."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_SHARD_COUNT = 6
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


def flatten_suite(suite: unittest.TestSuite) -> list[unittest.TestCase]:
    tests: list[unittest.TestCase] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            tests.extend(flatten_suite(item))
        else:
            tests.append(item)
    return tests


def discover_tests() -> list[unittest.TestCase]:
    return flatten_suite(unittest.defaultTestLoader.discover("tests"))


def module_name(test: unittest.TestCase) -> str:
    return test.__class__.__module__


@dataclass(frozen=True)
class ShardPlan:
    modules: tuple[tuple[str, ...], ...]
    test_ids: tuple[tuple[str, ...], ...]

    def summary(self) -> dict[str, object]:
        return {
            "discovered_test_count": sum(len(ids) for ids in self.test_ids),
            "shards": [
                {
                    "index": index,
                    "module_count": len(self.modules[index]),
                    "test_count": len(self.test_ids[index]),
                    "modules": list(self.modules[index]),
                }
                for index in range(len(self.modules))
            ],
        }


def build_plan(tests: Iterable[unittest.TestCase], shard_count: int) -> ShardPlan:
    if shard_count < 1:
        raise ValueError("shard_count must be positive")

    by_module: dict[str, list[unittest.TestCase]] = {}
    for test in tests:
        by_module.setdefault(module_name(test), []).append(test)

    shard_modules: list[list[str]] = [[] for _ in range(shard_count)]
    shard_sizes = [0] * shard_count
    module_to_shard: dict[str, int] = {}
    for name, module_tests in sorted(
        by_module.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        shard_index = min(range(shard_count), key=lambda index: (shard_sizes[index], index))
        shard_modules[shard_index].append(name)
        shard_sizes[shard_index] += len(module_tests)
        module_to_shard[name] = shard_index

    shard_ids: list[list[str]] = [[] for _ in range(shard_count)]
    for test in tests:
        shard_ids[module_to_shard[module_name(test)]].append(test.id())

    return ShardPlan(
        modules=tuple(tuple(names) for names in shard_modules),
        test_ids=tuple(tuple(ids) for ids in shard_ids),
    )


def verify_partition(tests: list[unittest.TestCase], plan: ShardPlan) -> None:
    discovered = [test.id() for test in tests]
    assigned = [test_id for shard in plan.test_ids for test_id in shard]
    duplicates = sorted(test_id for test_id, count in Counter(assigned).items() if count != 1)
    if duplicates:
        raise ValueError(f"test ids are not assigned exactly once: {duplicates}")
    if Counter(assigned) != Counter(discovered):
        missing = sorted((Counter(discovered) - Counter(assigned)).elements())
        extra = sorted((Counter(assigned) - Counter(discovered)).elements())
        raise ValueError(f"shards do not cover discovery: missing={missing}, extra={extra}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard-count", type=int, default=DEFAULT_SHARD_COUNT)
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--verify-partition", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    tests = discover_tests()
    plan = build_plan(tests, arguments.shard_count)
    verify_partition(tests, plan)
    print(json.dumps(plan.summary(), indent=2, sort_keys=True), flush=True)

    if arguments.verify_partition:
        return 0
    if arguments.shard_index is None:
        raise SystemExit("--shard-index is required unless --verify-partition is used")
    if not 0 <= arguments.shard_index < arguments.shard_count:
        raise SystemExit("--shard-index must be within the configured shard count")

    selected_ids = set(plan.test_ids[arguments.shard_index])
    selected = [test for test in tests if test.id() in selected_ids]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
