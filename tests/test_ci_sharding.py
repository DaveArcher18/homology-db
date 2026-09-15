from __future__ import annotations

import unittest

from scripts.run_unittest_shard import build_plan, discover_tests, verify_partition


class CiShardingTest(unittest.TestCase):
    def test_six_shards_cover_exactly_the_discovered_suite(self) -> None:
        discovered = discover_tests()
        plan = build_plan(discovered, 6)
        verify_partition(discovered, plan)

        discovered_ids = {test.id() for test in discovered}
        assigned_ids = {test_id for shard in plan.test_ids for test_id in shard}
        self.assertEqual(assigned_ids, discovered_ids)
        self.assertEqual(sum(len(shard) for shard in plan.test_ids), len(discovered_ids))

    def test_plan_is_deterministic_and_preserves_modules(self) -> None:
        discovered = discover_tests()
        first = build_plan(discovered, 6)
        second = build_plan(discovered, 6)
        self.assertEqual(first, second)

        module_shards: dict[str, set[int]] = {}
        tests_by_id = {test.id(): test for test in discovered}
        for shard_index, test_ids in enumerate(first.test_ids):
            for test_id in test_ids:
                module = tests_by_id[test_id].__class__.__module__
                module_shards.setdefault(module, set()).add(shard_index)
        self.assertTrue(all(len(shards) == 1 for shards in module_shards.values()))


if __name__ == "__main__":
    unittest.main()
