from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from homology_db.steenrod import (
    IncompleteModuleError,
    ModuleValidationError,
    UnsupportedExportError,
    export_bruner,
    export_manifest,
    export_sseq,
    export_sseqcpp,
    load_cw49_corpus,
    validate_module,
)


def sum_fixture_module() -> dict:
    return {
        "schema_version": "homology-db.steenrod-module/1",
        "spectrum_id": "sum_fixture",
        "module_type": "finite_basis",
        "coefficient_field": "F2",
        "reduced": True,
        "category": "stable",
        "grading_convention": "cohomological",
        "suspension_shift": 0,
        "basis_version": "test:sum_fixture",
        "basis": [
            {"basis_id": "b0", "name": "x0", "degree": 0, "ordinal": 0},
            {"basis_id": "b1a", "name": "x1_0", "degree": 1, "ordinal": 0},
            {"basis_id": "b1b", "name": "x1_1", "degree": 1, "ordinal": 1},
        ],
        "actions": [
            {
                "source_basis_id": "b0",
                "square_degree": 1,
                "knowledge_state": "exact",
                "target_basis_ids": ["b1a", "b1b"],
            }
        ],
        "completeness": {
            "knowledge_state": "exact",
            "slots": [{"source_basis_id": "b0", "square_degree": 1}],
        },
        "source_snapshot": "test",
        "source_locator": "test:sum_fixture",
        "evidence": {
            "evidence_kind": "imported_source",
            "source_snapshot": "test",
            "source_locator": "test:sum_fixture",
            "review_state": "imported_unreviewed",
        },
        "review_state": "imported_unreviewed",
    }


class SteenrodCorpusTests(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("BRUNER_NEWCONSISTENCY"),
        "set BRUNER_NEWCONSISTENCY to Bruner Ext 1.9.5's checker",
    )
    def test_all_bruner_exports_pass_the_pinned_real_consistency_checker(self) -> None:
        checker = os.environ["BRUNER_NEWCONSISTENCY"]
        spectra = [
            spectrum
            for spectrum in load_cw49_corpus()["spectra"]
            if spectrum["module"]["module_type"] == "finite_basis"
        ]
        self.assertEqual(len(spectra), 48)
        for spectrum in spectra:
            spectrum_id = spectrum["spectrum_id"]
            with (
                self.subTest(spectrum_id=spectrum_id),
                tempfile.TemporaryDirectory() as directory,
            ):
                Path(directory, "Def").write_text(
                    export_bruner(spectrum), encoding="utf-8"
                )
                checked = subprocess.run(
                    [checker], cwd=directory, check=False, capture_output=True, text=True
                )
                self.assertEqual(
                    checked.returncode,
                    0,
                    f"{checked.stdout}\n{checked.stderr}",
                )

    @unittest.skipUnless(
        os.environ.get("SSEQCPP_ADAMS"),
        "set SSEQCPP_ADAMS to the pinned SSeqCpp Adams executable",
    )
    def test_sseqcpp_fragments_pass_the_pinned_real_parser(self) -> None:
        executable = os.environ["SSEQCPP_ADAMS"]
        records = [
            spectrum
            for spectrum in load_cw49_corpus()["spectra"]
            if spectrum["module"]["module_type"] == "finite_basis"
        ]
        records.append(sum_fixture_module())
        self.assertEqual(len(records), 49)
        for record in records:
            spectrum_id = record["spectrum_id"]
            payload = export_sseqcpp(record)
            module = record.get("module", record)
            top_degree = max(element["degree"] for element in module["basis"])
            with (
                self.subTest(spectrum_id=spectrum_id),
                tempfile.TemporaryDirectory() as directory,
            ):
                Path(directory, "Adams.json").write_text(
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                    encoding="utf-8",
                )
                checked = subprocess.run(
                    [executable, "cellstructure", spectrum_id, str(top_degree)],
                    cwd=directory,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    checked.returncode,
                    0,
                    f"{checked.stdout}\n{checked.stderr}",
                )

    @unittest.skipUnless(
        os.environ.get("SSEQ_PARSER"),
        "set SSEQ_PARSER to a pinned SpectralSequences/sseq parser helper",
    )
    def test_sseq_exports_pass_the_pinned_real_parser(self) -> None:
        parser = os.environ["SSEQ_PARSER"]
        # The pinned ext-rs parser is killed by its own degree-256 Adem-algebra
        # expansion for these three records on the validation host. Their JSON
        # remains deterministic and schema-identical to the records exercised
        # here; retain the exact limitation instead of treating a SIGKILL as a
        # successful consumer parse.
        parser_resource_limits = {"Fphi", "RP1_256", "RP3_256"}
        records = [
            spectrum
            for spectrum in load_cw49_corpus()["spectra"]
            if spectrum["spectrum_id"] not in parser_resource_limits
        ]
        records.append(sum_fixture_module())
        self.assertEqual(len(records), 47)
        for record in records:
            spectrum_id = record["spectrum_id"]
            with (
                self.subTest(spectrum_id=spectrum_id),
                tempfile.TemporaryDirectory() as directory,
            ):
                payload_path = Path(directory, f"{spectrum_id}.json")
                payload_path.write_text(
                    json.dumps(
                        export_sseq(record),
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    encoding="utf-8",
                )
                checked = subprocess.run(
                    [parser, str(payload_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    checked.returncode,
                    0,
                    f"{checked.stdout}\n{checked.stderr}",
                )

    def test_sseqcpp_minimal_generator_degrees_match_every_pinned_source_record(
        self,
    ) -> None:
        upstream_path = (
            Path(__file__).resolve().parent.parent
            / "corpus"
            / "steenrod-cw49-v1"
            / "upstream-adams.json"
        )
        source_definitions = json.loads(upstream_path.read_text(encoding="utf-8"))[
            "CW_complexes"
        ]
        spectra = {
            spectrum["spectrum_id"]: spectrum
            for spectrum in load_cw49_corpus()["spectra"]
        }

        self.assertEqual(len(source_definitions), 41)
        for spectrum_id, definition in source_definitions.items():
            with self.subTest(spectrum_id=spectrum_id):
                exported = export_sseqcpp(spectra[spectrum_id])
                self.assertEqual(
                    exported["CW_complexes"][spectrum_id]["cells_gen"],
                    definition["cells_gen"],
                )

    def test_module_cli_lists_exports_and_reports_typed_unsupported(self) -> None:
        listed = subprocess.run(
            [sys.executable, "-m", "homology_db.steenrod", "list"],
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(listed.stdout)
        self.assertEqual(summary["spectrum_count"], 49)
        self.assertEqual(summary["finite_module_count"], 48)
        package_listed = subprocess.run(
            [sys.executable, "-m", "homology_db", "steenrod", "list"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(package_listed.stdout), summary)

        exported = subprocess.run(
            [
                sys.executable,
                "-m",
                "homology_db.steenrod",
                "export",
                "Ceta",
                "--format",
                "sseq",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(exported.stdout)["actions"], ["Sq2 x0 = x2"])
        manifest = subprocess.run(
            [
                sys.executable,
                "-m",
                "homology_db.steenrod",
                "manifest",
                "Ceta",
                "--format",
                "sseq",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            json.loads(manifest.stdout)["payload_sha256"],
            hashlib.sha256(exported.stdout.encode("utf-8")).hexdigest(),
        )

        unsupported = subprocess.run(
            [
                sys.executable,
                "-m",
                "homology_db.steenrod",
                "export",
                "tmf",
                "--format",
                "bruner",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(unsupported.returncode, 2)
        self.assertEqual(
            json.loads(unsupported.stderr),
            {
                "status": "unsupported",
                "format": "bruner",
                "reason": "infinite_profile",
                "spectrum_id": "tmf",
            },
        )

    def test_cli_export_bytes_are_independent_of_python_hash_seed(self) -> None:
        for format_name in ("sseq", "sseqcpp", "bruner"):
            outputs = []
            for seed in ("1", "8675309"):
                environment = os.environ.copy()
                environment["PYTHONHASHSEED"] = seed
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "homology_db.steenrod",
                        "export",
                        "C2_C2",
                        "--format",
                        format_name,
                    ],
                    check=True,
                    capture_output=True,
                    env=environment,
                )
                outputs.append(completed.stdout)
            with self.subTest(format_name=format_name):
                self.assertEqual(outputs[0], outputs[1])

    def test_complete_cw49_corpus_is_pinned_unreviewed_and_deterministic(self) -> None:
        corpus_path = (
            Path(__file__).resolve().parent.parent
            / "corpus"
            / "steenrod-cw49-v1"
            / "corpus.json"
        )
        persisted = json.loads(corpus_path.read_text(encoding="utf-8"))
        first = load_cw49_corpus()
        second = load_cw49_corpus()

        self.assertEqual(persisted, first)
        self.assertEqual(first, second)
        self.assertEqual(len(first["spectra"]), 49)
        self.assertEqual(first["source"]["normalization_state"], "complete")
        self.assertEqual(
            sum(
                spectrum["module"]["module_type"] == "finite_basis"
                for spectrum in first["spectra"]
            ),
            48,
        )
        self.assertTrue(
            all(
                spectrum["review_state"] == "imported_unreviewed"
                and spectrum["source_decode_state"] == "complete"
                and spectrum["module"]["review_state"] == "imported_unreviewed"
                and spectrum["module"]["reduced"] is True
                and spectrum["module"]["evidence"]["evidence_kind"]
                == "imported_source"
                and len(spectrum["module"]["content_sha256"]) == 64
                for spectrum in first["spectra"]
            )
        )
        self.assertEqual(
            first["source"]["module_source"],
            {
                "archive_filename": "programs.rar",
                "archive_bytes": 4180266,
                "archive_md5": "554d12d6dc6aa61b94a7b9fe85c73f04",
                "archive_sha256": (
                    "dca24f896dd3eb296e6cbe32e2fcdd57"
                    "77056a026674454c6a0ac08b9e1fe73e"
                ),
                "path": "programs/Adams.json",
                "bytes": 24455,
                "sha256": (
                    "5a4adf1561832a762b7d3a504f8f2603"
                    "793855733f549d17d5a9668f6c7935bc"
                ),
                "normalized_subset_path": "upstream-adams.json",
                "normalized_subset_sha256": (
                    "53e7c69f0642a04d2c990c23638ab0ae"
                    "5f72899c30d05faa2655cd3ac55d2576"
                ),
            },
        )
        self.assertEqual(first["source"]["dataset_license"], "CC-BY-4.0")
        self.assertEqual(
            first["source"]["source_code"],
            {
                "archive_filename": "source code.zip",
                "archive_bytes": 5051993,
                "archive_md5": "66ce3684e92676604f8368191e35d5b3",
                "archive_sha256": (
                    "dd784541626f4d693c35f3ca84d4a67e"
                    "83758ac463aabe58ab6c9cc92be22a15"
                ),
                "zip_comment_commit": "087753ebaa0b351f565d18279442cf05c9ab3c50",
                "license_path": "SSeqCpp-master/LICENSE",
                "license_spdx": "Apache-2.0",
            },
        )
        self.assertNotIn("license", first["source"])
        self.assertEqual(
            first["source"]["fallback"],
            {
                "role": "historical_cross_check_only",
                "repository": "https://github.com/WayneLin92/SSeqCpp",
                "commit": "fdf7e372da28ff1ac59794807d5468b6c7cf12e1",
                "path": "scripts/Adams.json",
                "sha256": "86c27d67e8c726c83138cc4134c563cffdd38f8e00d1891bff6fcb3a5bce6c44",
                "known_ordering_differences": [
                    "C2_C2",
                    "Ceta_Ceta",
                    "Cnu_Cnu",
                    "Csigma_Csigma",
                ],
            },
        )

    def test_loader_rejects_drift_from_the_pinned_normalization(self) -> None:
        corpus_directory = (
            Path(__file__).resolve().parent.parent
            / "corpus"
            / "steenrod-cw49-v1"
        )
        corpus = json.loads(
            (corpus_directory / "corpus.json").read_text(encoding="utf-8")
        )
        corpus["spectra"][0]["slug"] = "silently-drifted"

        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            corpus_path = directory_path / "corpus.json"
            corpus_path.write_text(json.dumps(corpus), encoding="utf-8")
            (directory_path / "upstream-adams.json").write_bytes(
                (corpus_directory / "upstream-adams.json").read_bytes()
            )
            with self.assertRaisesRegex(ModuleValidationError, "normalization"):
                load_cw49_corpus(corpus_path)

    def test_s0_tracer_loads_validates_and_exports_all_three_formats(self) -> None:
        corpus = load_cw49_corpus()
        self.assertEqual(corpus["schema_version"], "homology-db.steenrod-corpus/1")
        s0 = next(
            spectrum
            for spectrum in corpus["spectra"]
            if spectrum["spectrum_id"] == "S0"
        )

        self.assertIsNone(validate_module(s0["module"]))
        self.assertEqual(
            export_sseq(s0),
            {
                "p": 2,
                "type": "finite dimensional module",
                "gens": {"x0": 0},
                "actions": [],
            },
        )
        self.assertEqual(
            export_sseqcpp(s0),
            {
                "CW_complexes": {
                    "S0": {
                        "cells": [0],
                        "cells_gen": [0],
                        "operations": [],
                    }
                }
            },
        )
        self.assertEqual(export_bruner(s0), "1\n0\n")
        self.assertEqual(
            export_manifest(s0, "sseq", export_sseq(s0)),
            {
                "schema_version": "homology-db.steenrod-export-manifest/1",
                "spectrum_id": "S0",
                "basis_version": "cw49-v126.3:S0",
                "suspension_shift": 0,
                "source_snapshot": "zenodo:14875701:v126.3.cw49",
                "adapter_version": "homology-db.steenrod/1",
                "format": "sseq",
                "payload_sha256": (
                    "0c0f2f362114f52cc6a907914db66e8b"
                    "5a358b15207fe8017064e71a398d5630"
                ),
            },
        )
        with self.assertRaisesRegex(ModuleValidationError, "export format"):
            export_manifest(s0, "unknown", {})

    def test_all_forty_eight_finite_modules_export_deterministically(self) -> None:
        finite = [
            spectrum
            for spectrum in load_cw49_corpus()["spectra"]
            if spectrum["module"]["module_type"] == "finite_basis"
        ]

        self.assertEqual(len(finite), 48)
        for spectrum in finite:
            with self.subTest(spectrum_id=spectrum["spectrum_id"]):
                sseq = export_sseq(spectrum)
                sseqcpp = export_sseqcpp(spectrum)
                bruner = export_bruner(spectrum)
                self.assertEqual(sseq, export_sseq(spectrum))
                self.assertEqual(sseqcpp, export_sseqcpp(spectrum))
                self.assertEqual(bruner, export_bruner(spectrum))
                self.assertEqual(
                    len(export_manifest(spectrum, "bruner", bruner)["payload_sha256"]),
                    64,
                )

    def test_export_requires_an_exact_image_for_every_finite_support_slot(self) -> None:
        ceta = {
            "schema_version": "homology-db.steenrod-module/1",
            "spectrum_id": "Ceta",
            "module_type": "finite_basis",
            "coefficient_field": "F2",
            "reduced": True,
            "category": "stable",
            "grading_convention": "cohomological",
            "suspension_shift": 0,
            "basis_version": "test:Ceta",
            "basis": [
                {"basis_id": "b0", "name": "x0", "degree": 0, "ordinal": 0},
                {"basis_id": "b2", "name": "x2", "degree": 2, "ordinal": 0},
            ],
            "actions": [
                {
                    "source_basis_id": "b0",
                    "square_degree": 2,
                    "knowledge_state": "exact",
                    "target_basis_ids": ["b2"],
                }
            ],
            "completeness": {
                "knowledge_state": "exact",
                "slots": [
                    {"source_basis_id": "b0", "square_degree": 2},
                ],
            },
            "source_snapshot": "test",
            "source_locator": "test:Ceta",
            "evidence": {
                "evidence_kind": "imported_source",
                "source_snapshot": "test",
                "source_locator": "test:Ceta",
                "review_state": "imported_unreviewed",
            },
            "review_state": "imported_unreviewed",
        }

        self.assertIsNone(validate_module(ceta))
        for exporter in (export_sseq, export_sseqcpp, export_bruner):
            with self.subTest(exporter=exporter.__name__):
                with self.assertRaisesRegex(IncompleteModuleError, "exact image"):
                    exporter(ceta)
        with self.assertRaisesRegex(IncompleteModuleError, "exact image"):
            export_manifest(ceta, "sseq", {"not": "a downloadable module"})

        ceta["actions"].insert(
            0,
            {
                "source_basis_id": "b0",
                "square_degree": 1,
                "knowledge_state": "exact",
                "target_basis_ids": [],
            },
        )
        ceta["completeness"]["slots"].insert(
            0, {"source_basis_id": "b0", "square_degree": 1}
        )
        self.assertEqual(export_sseq(ceta)["actions"], ["Sq2 x0 = x2"])

    def test_validation_rejects_a_stale_canonical_content_hash(self) -> None:
        s0 = deepcopy(load_cw49_corpus()["spectra"][0]["module"])
        s0["basis_version"] = "silently-mutated"

        with self.assertRaisesRegex(ModuleValidationError, "content_sha256"):
            validate_module(s0)

    def test_validation_requires_manifest_provenance_to_match_evidence(self) -> None:
        canonical = deepcopy(load_cw49_corpus()["spectra"][0]["module"])
        cases = (
            ("spectrum_id", None, "spectrum_id"),
            ("basis_version", "", "basis_version"),
            ("source_snapshot", None, "source_snapshot"),
            ("source_locator", "", "source_locator"),
            ("suspension_shift", "0", "suspension_shift"),
        )
        for field_name, replacement, message in cases:
            malformed = deepcopy(canonical)
            malformed.pop("content_sha256")
            if replacement is None:
                malformed.pop(field_name)
            else:
                malformed[field_name] = replacement
            with self.subTest(field_name=field_name), self.assertRaisesRegex(
                ModuleValidationError, message
            ):
                validate_module(malformed)

        mismatched = deepcopy(canonical)
        mismatched.pop("content_sha256")
        mismatched["evidence"]["source_snapshot"] = "different-source"
        with self.assertRaisesRegex(ModuleValidationError, "source evidence"):
            validate_module(mismatched)

    def test_acceptance_metadata_does_not_change_mathematical_content_hash(self) -> None:
        imported = deepcopy(load_cw49_corpus()["spectra"][0]["module"])
        accepted = deepcopy(imported)
        accepted["review_state"] = "accepted"
        accepted["evidence"]["review_state"] = "accepted"
        accepted["review"] = {
            "reviewer": "Dan Isaksen",
            "verdict": "accept",
        }

        self.assertEqual(accepted["content_sha256"], imported["content_sha256"])
        self.assertIsNone(validate_module(accepted))

    def test_validation_rejects_malformed_profile_order_and_subject_drift(self) -> None:
        spectra = {
            spectrum["spectrum_id"]: spectrum
            for spectrum in load_cw49_corpus()["spectra"]
        }

        malformed_profile = deepcopy(spectra["tmf"]["module"])
        malformed_profile.pop("content_sha256")
        malformed_profile["basis"] = [
            {"basis_id": "tmf:b0", "name": "x0", "degree": 0, "ordinal": 0}
        ]
        with self.assertRaisesRegex(ModuleValidationError, "profile module"):
            validate_module(malformed_profile)

        malformed_order = deepcopy(spectra["C2_C2"]["module"])
        malformed_order.pop("content_sha256")
        malformed_order["basis"][2]["ordinal"] = 2
        with self.assertRaisesRegex(ModuleValidationError, "ordinal"):
            validate_module(malformed_order)

        mismatched_subject = deepcopy(spectra["Ceta"])
        mismatched_subject["spectrum_id"] = "not-Ceta"
        with self.assertRaisesRegex(ModuleValidationError, "subject"):
            export_sseq(mismatched_subject)

    def test_validation_rejects_booleans_in_integer_basis_and_action_fields(self) -> None:
        canonical = next(
            spectrum["module"]
            for spectrum in load_cw49_corpus()["spectra"]
            if spectrum["spectrum_id"] == "C2"
        )
        mutations = (
            ("basis degree", lambda module: module["basis"][0].update(degree=True)),
            ("basis ordinal", lambda module: module["basis"][0].update(ordinal=False)),
            (
                "action degree",
                lambda module: module["actions"][0].update(square_degree=True),
            ),
            (
                "completeness degree",
                lambda module: module["completeness"]["slots"][0].update(
                    square_degree=True
                ),
            ),
        )
        for label, mutate in mutations:
            malformed = deepcopy(canonical)
            malformed.pop("content_sha256")
            mutate(malformed)
            with self.subTest(label=label), self.assertRaisesRegex(
                ModuleValidationError, "integer|square_degree"
            ):
                validate_module(malformed)

    def test_validation_rejects_an_adem_inconsistent_generator_action(self) -> None:
        module = {
            "schema_version": "homology-db.steenrod-module/1",
            "spectrum_id": "bad",
            "module_type": "finite_basis",
            "coefficient_field": "F2",
            "reduced": True,
            "category": "stable",
            "grading_convention": "cohomological",
            "suspension_shift": 0,
            "basis_version": "test:bad",
            "basis": [
                {"basis_id": "b0", "name": "x0", "degree": 0, "ordinal": 0},
                {"basis_id": "b1", "name": "x1", "degree": 1, "ordinal": 0},
                {"basis_id": "b2", "name": "x2", "degree": 2, "ordinal": 0},
            ],
            "actions": [
                {
                    "source_basis_id": "b0",
                    "square_degree": 1,
                    "knowledge_state": "exact",
                    "target_basis_ids": ["b1"],
                },
                {
                    "source_basis_id": "b0",
                    "square_degree": 2,
                    "knowledge_state": "exact",
                    "target_basis_ids": [],
                },
                {
                    "source_basis_id": "b1",
                    "square_degree": 1,
                    "knowledge_state": "exact",
                    "target_basis_ids": ["b2"],
                },
            ],
            "completeness": {
                "knowledge_state": "exact",
                "slots": [
                    {"source_basis_id": "b0", "square_degree": 1},
                    {"source_basis_id": "b0", "square_degree": 2},
                    {"source_basis_id": "b1", "square_degree": 1},
                ],
            },
            "source_snapshot": "test",
            "source_locator": "test:bad",
            "evidence": {
                "evidence_kind": "imported_source",
                "source_snapshot": "test",
                "source_locator": "test:bad",
                "review_state": "imported_unreviewed",
            },
            "review_state": "imported_unreviewed",
        }

        with self.assertRaisesRegex(ModuleValidationError, "Adem"):
            validate_module(module)

    def test_unstable_modules_enforce_the_instability_condition(self) -> None:
        ceta = next(
            spectrum["module"]
            for spectrum in load_cw49_corpus()["spectra"]
            if spectrum["spectrum_id"] == "Ceta"
        )
        unstable = deepcopy(ceta)
        unstable.pop("content_sha256")
        unstable["category"] = "unstable"

        with self.assertRaisesRegex(ModuleValidationError, "instability"):
            validate_module(unstable)

    def test_tmf_is_an_infinite_profile_with_typed_bruner_refusal(self) -> None:
        tmf = next(
            spectrum
            for spectrum in load_cw49_corpus()["spectra"]
            if spectrum["spectrum_id"] == "tmf"
        )

        self.assertEqual(
            tmf["module"]["profile"]["basis"],
            "milnor",
        )
        self.assertEqual(
            export_sseq(tmf),
            {
                "p": 2,
                "type": "finite dimensional module",
                "algebra": ["milnor"],
                "profile": {"truncated": True, "p_part": [3, 2, 1]},
                "gens": {"x0": 0},
                "actions": [],
            },
        )
        with self.assertRaises(UnsupportedExportError) as raised:
            export_sseqcpp(tmf)
        self.assertEqual(raised.exception.format_name, "sseqcpp")
        self.assertEqual(raised.exception.reason, "infinite_profile")
        with self.assertRaises(UnsupportedExportError) as raised:
            export_bruner(tmf)
        self.assertEqual(raised.exception.format_name, "bruner")
        self.assertEqual(raised.exception.reason, "infinite_profile")

    def test_sseqcpp_preserves_repeated_degrees_and_minimal_generators(self) -> None:
        spectra = {
            spectrum["spectrum_id"]: spectrum
            for spectrum in load_cw49_corpus()["spectra"]
        }
        for spectrum_id, middle_degree in {
            "C2_C2": 1,
            "Ceta_Ceta": 2,
            "Cnu_Cnu": 4,
            "Csigma_Csigma": 8,
        }.items():
            with self.subTest(spectrum_id=spectrum_id):
                self.assertEqual(
                    export_sseqcpp(spectra[spectrum_id]),
                    {
                        "CW_complexes": {
                            spectrum_id: {
                                "cells": [
                                    0,
                                    middle_degree,
                                    middle_degree,
                                    2 * middle_degree,
                                ],
                                "cells_gen": [0, middle_degree],
                                "operations": [
                                    [0, [middle_degree, 1]],
                                    [0, 2 * middle_degree],
                                    [[middle_degree, 0], 2 * middle_degree],
                                ],
                            }
                        }
                    }
                )
        self.assertEqual(
            export_sseq(spectra["C2_C2"])["actions"],
            [
                "Sq1 x0 = x1_1",
                "Sq2 x0 = x2",
                "Sq1 x1_0 = x2",
            ],
        )

    def test_sum_valued_action_round_trips_through_every_finite_export(self) -> None:
        module = sum_fixture_module()

        self.assertEqual(
            export_sseq(module)["actions"], ["Sq1 x0 = x1_0 + x1_1"]
        )
        self.assertEqual(
            export_sseqcpp(module),
            {
                "CW_complexes": {
                    "sum_fixture": {
                        "cells": [0, 1, 1],
                        "cells_gen": [0, 1],
                        "operations": [[0, [1, 0, 1]]],
                    }
                }
            },
        )
        self.assertEqual(export_bruner(module), "3\n0 1 1\n0 1 2 1 2\n")

    def test_bruner_emits_generator_and_adem_derived_composite_squares(self) -> None:
        spectra = {
            spectrum["spectrum_id"]: spectrum
            for spectrum in load_cw49_corpus()["spectra"]
        }

        self.assertEqual(export_bruner(spectra["Ceta"]), "2\n0 2\n0 2 1 1\n")
        joker_lines = export_bruner(spectra["Joker"]).splitlines()
        self.assertIn("0 1 1 1", joker_lines)
        self.assertIn("0 2 1 2", joker_lines)
        self.assertIn("1 3 1 4", joker_lines)
        self.assertIn("3 1 1 4", joker_lines)


if __name__ == "__main__":
    unittest.main()
