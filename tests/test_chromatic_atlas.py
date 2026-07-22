from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from homology_db.chromatic import (
    ChromaticDatabase,
    ChromaticTools,
    _integral_rows,
    load_manifest,
)
from homology_db.preview import digest


class ChromaticAtlasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.database_path = Path(self.temporary_directory.name) / "chromatic.sqlite3"
        self.snapshot_id = ChromaticDatabase.build(self.database_path)
        self.tools = ChromaticTools(self.database_path)
        self.addCleanup(self.tools.close)

    def test_builds_the_curated_forty_two_space_snapshot_deterministically(self) -> None:
        summary = self.tools.corpus_summary()
        self.assertEqual(summary["subject_count"], 42)
        self.assertEqual(
            summary["family_counts"],
            {
                "compact_lie_group": 2,
                "cyclic_classifying_space": 3,
                "elementary_abelian_classifying_space": 3,
                "homology_sphere": 1,
                "hopf_projective_plane": 3,
                "infinite_projective_space": 2,
                "lens_space": 4,
                "moore_space": 6,
                "point": 1,
                "real_projective_space": 3,
                "schubert_space": 2,
                "sphere": 5,
                "stunted_projective_space": 2,
                "surface": 2,
                "thom_space": 1,
                "unitary_classifying_space": 1,
                "wedge": 1,
            },
        )
        second_path = Path(self.temporary_directory.name) / "second.sqlite3"
        self.assertEqual(ChromaticDatabase.build(second_path), self.snapshot_id)
        self.assertEqual(self.database_path.read_bytes(), second_path.read_bytes())

    def test_cited_integral_rows_require_an_explicit_group_in_every_degree(
        self,
    ) -> None:
        with self.assertRaisesRegex(ValueError, "explicit groups for every degree"):
            _integral_rows(2, {0: (1, []), 2: (1, [])})
        cited_rows = _integral_rows(0, {0: (1, [])})
        self.assertIsNone(
            cited_rows[0]["smith_diagonal_of_incoming_boundary"]
        )
        self.assertEqual(cited_rows[0]["smith_diagonal_state"], "not_computed")

    def test_parameterized_torsion_computations_include_uct_tor_classes(self) -> None:
        integral = self.tools.read_homology("M(Z/9,2)", coefficient="Z")
        self.assertEqual(integral["outcome"], "selected")
        self.assertEqual(integral["subject"]["parameters"], {"m": 9, "n": 2})
        self.assertEqual(integral["groups"][2]["value"]["display"], "Z/9")

        mod_three = self.tools.read_homology("M(Z/9,2)", coefficient="F3")
        self.assertEqual(
            [
                (group["degree"], group["value"]["dimension"])
                for group in mod_three["groups"]
                if group["value"]["dimension"]
            ],
            [(0, 1), (2, 1), (3, 1)],
        )

        elementary = self.tools.read_homology("B(C_2^3)", coefficient="F2")
        self.assertEqual(elementary["groups"][2]["value"]["dimension"], 6)

        klein_mod_two = self.tools.read_homology("Klein bottle", coefficient="F2")
        self.assertEqual(
            [row["value"]["dimension"] for row in klein_mod_two["groups"]],
            [1, 2, 1],
        )

    def test_coverage_distinguishes_finite_models_from_bounded_finite_type_data(
        self,
    ) -> None:
        finite = self.tools.read_homology("RP^4")
        self.assertEqual(finite["coverage"]["kind"], "complete_finite_cw")
        self.assertEqual(finite["coverage"]["computed_through_degree"], 4)
        self.assertEqual(finite["coverage"]["upper_vanishing_starts_at"], 5)

        finite_type = self.tools.read_homology("BC_3")
        self.assertTrue(finite_type["subject"]["infinite_finite_type"])
        self.assertIsNone(finite_type["subject"]["dimension"])
        self.assertEqual(
            finite_type["coverage"]["kind"], "bounded_through_degree"
        )
        self.assertEqual(finite_type["coverage"]["computed_through_degree"], 24)
        self.assertIsNone(finite_type["coverage"]["upper_vanishing_starts_at"])
        self.assertEqual(finite_type["groups"][-1]["degree"], 24)

    def test_models_preserve_attaching_data_and_literature_only_evidence(self) -> None:
        projective = self.tools.read_homology("CP^2")
        wedge = self.tools.read_homology("sphere_wedge:2:4")
        projective_evidence = self.tools.expand_evidence(
            [projective["groups"][0]["evidence_id"]]
        )["evidence"][0]
        wedge_evidence = self.tools.expand_evidence(
            [wedge["groups"][0]["evidence_id"]]
        )["evidence"][0]
        self.assertNotEqual(
            projective_evidence["model"]["model_id"],
            wedge_evidence["model"]["model_id"],
        )
        self.assertIn("eta", projective_evidence["model"]["attaching_map"])
        self.assertNotEqual(
            projective_evidence["model"]["attaching_map"],
            wedge_evidence["model"]["attaching_map"],
        )

        poincare = self.tools.read_homology("Poincare homology 3-sphere")
        expanded = self.tools.expand_evidence(
            [poincare["groups"][0]["evidence_id"]]
        )
        self.assertEqual(expanded["outcome"], "complete")
        evidence = expanded["evidence"][0]
        self.assertIn("cited_computation", evidence["evidence_kind"])
        self.assertIsNone(evidence["computation"])
        self.assertEqual(evidence["model"]["status"], "qualified")
        self.assertTrue(evidence["model"]["artifact_path"].endswith("facets.json"))
        self.assertTrue(evidence["references"])

    def test_query_filters_are_exact_and_coefficient_typed(self) -> None:
        invalid = self.tools.query_examples(
            {"coefficient": "F3", "free_rank_at_least": 1}
        )
        self.assertEqual(invalid["outcome"], "invalid_pattern")

        results = self.tools.query_examples(
            {
                "coefficient": "Z",
                "torsion_prime": 7,
                "degree": 3,
                "limit": 100,
            }
        )
        self.assertEqual(results["outcome"], "proven_matches")
        self.assertIn("moore:7:3", {row["space_id"] for row in results["matches"]})
        self.assertTrue(
            all(row["knowledge_state"] == "exact" for row in results["matches"])
        )

    def test_database_integrity_models_and_sources_cover_every_space(self) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM space").fetchone()[0], 42)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM model").fetchone()[0], 42)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM evidence").fetchone()[0], 42)
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM space_relation").fetchone()[0],
                11,
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT target_space_id
                    FROM space_relation
                    WHERE source_space_id = 'complex_projective_space:2'
                      AND relation_type = 'finite_skeleton_of'
                    """
                ).fetchone()[0],
                "complex_projective_space:infinity",
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM space WHERE infinite_finite_type = 1"
                ).fetchone()[0],
                10,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM model WHERE status != 'qualified'"
                ).fetchone()[0],
                0,
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(DISTINCT space_id) FROM homology
                    WHERE coefficient = 'Z' AND reduced = 0
                      AND torsion_json != '[]'
                    """
                ).fetchone()[0],
                21,
            )
            self.assertEqual(
                {
                    row[0]
                    for row in connection.execute(
                        "SELECT DISTINCT prime FROM primary_summand"
                    )
                },
                {2, 3, 5, 7},
            )
            self.assertEqual(
                connection.execute(
                    "SELECT MAX(exponent) FROM primary_summand WHERE prime = 2"
                ).fetchone()[0],
                3,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT MAX(exponent) FROM primary_summand WHERE prime = 3"
                ).fetchone()[0],
                2,
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM evidence e
                    WHERE NOT EXISTS (
                        SELECT 1 FROM evidence_reference er
                        WHERE er.evidence_id = e.evidence_id
                    )
                    """
                ).fetchone()[0],
                0,
            )
            self.assertTrue(
                all(
                    row[0].startswith("https://")
                    for row in connection.execute("SELECT url FROM reference")
                )
            )
            for row in connection.execute(
                "SELECT evidence_id, chain_json, chain_sha256 FROM evidence"
            ):
                self.assertEqual(
                    digest(json.loads(row["chain_json"])),
                    row["chain_sha256"],
                    row["evidence_id"],
                )
            artifact = connection.execute(
                """
                SELECT artifact_path, artifact_sha256
                FROM model WHERE space_id = 'poincare_homology_sphere:3'
                """
            ).fetchone()
            artifact_path = Path(__file__).resolve().parents[1] / artifact["artifact_path"]
            self.assertTrue(artifact_path.is_file())
            self.assertEqual(
                hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
                artifact["artifact_sha256"],
            )
            self.assertEqual(
                artifact["artifact_sha256"],
                load_manifest()["artifacts"][0]["sha256"],
            )

    def test_same_homology_guards_remain_distinct_conceptual_spaces(self) -> None:
        def signature(subject: str) -> list[tuple[int, str]]:
            return [
                (row["degree"], row["value"]["display"])
                for row in self.tools.read_homology(subject)["groups"]
            ]

        self.assertEqual(signature("CP^2"), signature("sphere_wedge:2:4"))
        self.assertEqual(
            signature("Poincare homology 3-sphere"), signature("sphere:3")
        )
        self.assertEqual(
            signature("L^3(5;1,1)"), signature("L^3(5;1,2)")
        )
        left = self.tools.expand_evidence(
            [self.tools.read_homology("L^3(5;1,1)")["groups"][0]["evidence_id"]]
        )["evidence"][0]
        right = self.tools.expand_evidence(
            [self.tools.read_homology("L^3(5;1,2)")["groups"][0]["evidence_id"]]
        )["evidence"][0]
        self.assertNotEqual(left["space_id"], right["space_id"])
        self.assertNotEqual(
            left["model"]["attaching_map"], right["model"]["attaching_map"]
        )
        self.assertEqual(
            self.tools.resolve_subject("SO(3)")["candidates"][0]["space_id"],
            "real_projective_space:3",
        )

    def test_reduced_h_zero_respects_components(self) -> None:
        sphere_zero = self.tools.read_homology("S^0", reduced=True)
        self.assertEqual(sphere_zero["subject"]["connected_components"], 2)
        self.assertEqual(sphere_zero["groups"][0]["value"]["free_rank"], 1)
        point = self.tools.read_homology("point", reduced=True)
        self.assertEqual(point["groups"][0]["value"]["display"], "0")

    def test_chromatic_cli_prefix_routes_to_the_current_product(self) -> None:
        cli_database = Path(self.temporary_directory.name) / "cli.sqlite3"
        request = json.dumps(
            {
                "tool": "read_homology",
                "arguments": {"subject": "M(Z/9,2)", "coefficient": "Z"},
            }
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "homology_db",
                "chromatic",
                "--db",
                str(cli_database),
                "tool",
                request,
            ],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        response = json.loads(completed.stdout)
        self.assertEqual(response["outcome"], "selected")
        self.assertEqual(response["groups"][2]["value"]["display"], "Z/9")


if __name__ == "__main__":
    unittest.main()
