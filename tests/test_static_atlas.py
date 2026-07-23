import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from homology_db.chromatic import ChromaticDatabase


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPORTER = REPOSITORY_ROOT / "scripts" / "export_static_atlas.py"


class StaticAtlasTest(unittest.TestCase):
    def test_pages_actions_are_pinned_to_full_commit_shas(self) -> None:
        workflow = (
            REPOSITORY_ROOT / ".github" / "workflows" / "deploy-atlas-pages.yml"
        ).read_text(encoding="utf-8")
        action_revisions = re.findall(r"^\s*uses:\s+[^@\s]+@([^\s]+)", workflow, re.MULTILINE)
        self.assertEqual(len(action_revisions), 4)
        self.assertTrue(
            all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in action_revisions)
        )

    def test_exporter_generates_complete_self_contained_atlas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            snapshot_id = ChromaticDatabase.build(database_path)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            build_summary = json.loads(completed.stdout)
            self.assertEqual(build_summary["relation_count"], 11)
            self.assertGreater(build_summary["source_database_bytes"], 0)
            html = output_path.read_text(encoding="utf-8")
            embedded = re.search(
                r'<script id="atlas-data" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            self.assertIsNotNone(embedded)
            atlas = json.loads(embedded.group(1))
            self.assertEqual(atlas["snapshot"]["snapshot_id"], snapshot_id)
            self.assertEqual(atlas["snapshot"]["schema_version"], "homology-db.static-atlas/3")
            self.assertEqual(
                atlas["snapshot"]["source_revision_inputs"],
                [
                    "corpus/chromatic-v1/manifest.json",
                    "corpus/chromatic-v1/poincare-sphere-facets.json",
                    "homology_db/__init__.py",
                    "homology_db/chromatic.py",
                    "homology_db/preview.py",
                    "scripts/export_static_atlas.py",
                    "static_atlas/atlas.css",
                    "static_atlas/atlas.js",
                    "static_atlas/index.template.html",
                    "static_atlas/presentation.js",
                ],
            )
            self.assertRegex(
                atlas["snapshot"]["source_inputs_sha256"], r"^[0-9a-f]{64}$"
            )
            self.assertIn(atlas["snapshot"]["source_tree_state"], {"clean", "dirty"})
            self.assertEqual(
                atlas["snapshot"]["source_inputs_dirty"],
                atlas["snapshot"]["source_tree_state"] == "dirty",
            )
            self.assertEqual(atlas["snapshot"]["conceptual_space_count"], 42)
            self.assertEqual(atlas["snapshot"]["relation_count"], 11)
            self.assertEqual(len(atlas["conceptual_spaces"]), 42)
            self.assertEqual(len({item["id"] for item in atlas["conceptual_spaces"]}), 42)
            self.assertTrue(
                all(
                    isinstance(item["name"]["tex"], str)
                    and bool(item["name"]["tex"].strip())
                    for item in atlas["conceptual_spaces"]
                )
            )
            names_by_id = {
                item["id"]: item["name"]["tex"]
                for item in atlas["conceptual_spaces"]
            }
            self.assertEqual(
                names_by_id["classifying_space:elementary_abelian:2:2"],
                r"B(C_{2}^{2})",
            )
            self.assertEqual(
                names_by_id["moore:9:2"],
                r"M(\mathbb{Z}/9,2)",
            )
            self.assertEqual(
                names_by_id["universal_complex_thom:2"],
                r"\operatorname{Th}(\gamma_{2}\to BU(2))",
            )
            definitions = atlas["definitions"]
            self.assertEqual(
                set(definitions[0]),
                {
                    "id",
                    "revision",
                    "selected_for_snapshot_id",
                    "term",
                    "body",
                    "scope",
                    "assertion_evidence",
                },
            )
            self.assertEqual(
                len({definition["id"] for definition in definitions}),
                len(definitions),
            )
            self.assertTrue(
                all(
                    definition["scope"] == "exposition"
                    and definition["assertion_evidence"] is False
                    and definition["revision"] == 1
                    and definition["selected_for_snapshot_id"]
                    == atlas["snapshot"]["snapshot_id"]
                    for definition in definitions
                )
            )
            self.assertIn(
                "ordinary-homology",
                {definition["id"] for definition in definitions},
            )
            self.assertIn("nonorientable surface genus 2", next(
                item["aliases"] for item in atlas["conceptual_spaces"]
                if item["id"] == "klein_bottle"
            ))
            projective_aliases = next(
                item["aliases"]
                for item in atlas["conceptual_spaces"]
                if item["id"] == "real_projective_space:4"
            )
            self.assertIn("RP4", [alias.replace("^", "") for alias in projective_aliases])
            projective_space = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "real_projective_space:4"
            )
            homology_row = projective_space["homology"][0]
            self.assertEqual(homology_row["theory"], "ordinary_homology")
            self.assertIsNone(homology_row["homology_convention"])
            self.assertEqual(
                homology_row["convention_state"], "not_recorded_in_database_schema"
            )
            self.assertNotIn("reliability", homology_row)
            self.assertEqual(
                projective_space["evidence"][0]["reliability"],
                "exact_owned_computation_with_cited_family_cross_check",
            )
            self.assertEqual(len(projective_space["computations"]), 1)
            self.assertTrue(projective_space["models"])
            self.assertEqual(projective_space["data_quality"]["state"], "valid")

            complex_projective_plane = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "complex_projective_space:2"
            )
            self.assertEqual(
                complex_projective_plane["parameters"],
                {"division_algebra": "complex"},
            )
            self.assertIn("hopf_invariant_one", complex_projective_plane["taxonomy"]["tags"])
            self.assertIn("projective planes", complex_projective_plane["summary"])
            self.assertIn("attaching maps", complex_projective_plane["chromatic_relevance"])
            self.assertEqual(
                complex_projective_plane["models"][0]["attaching_map"],
                "Attach e^4 to S^2 by the Hopf map eta.",
            )
            self.assertTrue(complex_projective_plane["evidence"][0]["citations"])
            self.assertEqual(
                complex_projective_plane["relations"],
                [
                    {
                        "detail": "The standard three-cell CW model is the 4-skeleton of the projective filtration of CP^infinity.",
                        "evidence_ids": [
                            "chromatic:evidence:complex_projective_space:2"
                        ],
                        "id": "relation:cp2:finite-skeleton:cp-infinity",
                        "source_id": "complex_projective_space:2",
                        "target_id": "complex_projective_space:infinity",
                        "type": "finite_skeleton_of",
                    }
                ],
            )
            self.assertTrue(all(
                citation["url"].startswith("https://")
                for evidence in complex_projective_plane["evidence"]
                for citation in evidence["citations"]
            ))

            cyclic_classifying_space = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "classifying_space:cyclic:3"
            )
            self.assertIsNone(next(
                property_["value"]
                for property_ in cyclic_classifying_space["properties"]
                if property_["key"] == "dimension"
            ))
            self.assertTrue(cyclic_classifying_space["infinite_finite_type"])
            self.assertEqual(
                cyclic_classifying_space["homology_coverage"]["kind"],
                "bounded_through_degree",
            )
            self.assertEqual(
                cyclic_classifying_space["homology_coverage"]["computed_through_degree"],
                24,
            )
            self.assertIsNone(
                cyclic_classifying_space["homology_coverage"]["upper_vanishing_starts_at"]
            )
            self.assertEqual(
                sum(
                    item["homology_coverage"]["kind"] == "complete_finite_cw"
                    for item in atlas["conceptual_spaces"]
                ),
                32,
            )
            self.assertEqual(
                sum(
                    item["homology_coverage"]["kind"] == "bounded_through_degree"
                    for item in atlas["conceptual_spaces"]
                ),
                10,
            )
            elementary_abelian_rank_three = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "classifying_space:elementary_abelian:2:3"
            )
            largest_repeated_sum = next(
                row
                for row in elementary_abelian_rank_three["homology"]
                if row["coefficient_ring"] == "Z"
                and row["reduced"] is False
                and row["degree"] == 24
            )
            self.assertEqual(
                largest_repeated_sum["group"]["torsion_orders"],
                [2] * 168,
            )
            presentation_check = subprocess.run(
                [
                    "node",
                    "-e",
                    r"""
const fs = require("fs");
const presentation = require("./static_atlas/presentation.js");
const atlas = JSON.parse(fs.readFileSync(0, "utf8"));
const coverageCounts = {
  "coverage-exhaustive": 0,
  "coverage-bounded": 0,
  "coverage-neutral": 0,
};
let malformedExactGroups = 0;
for (const space of atlas.conceptual_spaces) {
  const rows = space.homology.filter(
    (row) => row.coefficient_ring === "Z" && row.reduced === false
  );
  const coverage = presentation.coveragePresentation(
    space, rows, atlas.snapshot
  );
  coverageCounts[coverage.className] += 1;
  malformedExactGroups += rows.filter(
    (row) => row.group.state === "exact"
      && !presentation.groupPresentation(row).exact
  ).length;
}
const elementary = atlas.conceptual_spaces.find(
  (space) => space.id === "classifying_space:elementary_abelian:2:3"
);
const largest = elementary.homology.find(
  (row) => row.coefficient_ring === "Z"
    && row.reduced === false
    && row.degree === 24
);
console.log(JSON.stringify({
  unsupportedNames: atlas.conceptual_spaces
    .filter((space) => !presentation.isSupportedTex(space.name.tex))
    .map((space) => space.id),
  coverageCounts,
  malformedExactGroups,
  largestDisplay: presentation.groupPresentation(largest).tex,
}));
""",
                ],
                cwd=REPOSITORY_ROOT,
                input=json.dumps(atlas),
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                presentation_check.returncode,
                0,
                presentation_check.stderr,
            )
            presentation_result = json.loads(presentation_check.stdout)
            self.assertEqual(presentation_result["unsupportedNames"], [])
            self.assertEqual(
                presentation_result["coverageCounts"],
                {
                    "coverage-exhaustive": 32,
                    "coverage-bounded": 10,
                    "coverage-neutral": 0,
                },
            )
            self.assertEqual(presentation_result["malformedExactGroups"], 0)
            self.assertEqual(
                presentation_result["largestDisplay"],
                r"(\mathbb{Z}/2\mathbb{Z})^{\oplus 168}",
            )

            poincare_sphere = next(
                item
                for item in atlas["conceptual_spaces"]
                if item["id"] == "poincare_homology_sphere:3"
            )
            self.assertEqual(poincare_sphere["computations"], [])
            self.assertEqual(
                poincare_sphere["models"][0]["artifact_path"],
                "corpus/chromatic-v1/poincare-sphere-facets.json",
            )
            self.assertRegex(
                poincare_sphere["models"][0]["artifact_sha256"],
                r"^[0-9a-f]{64}$",
            )
            self.assertEqual(
                poincare_sphere["evidence"][0]["kind"],
                "official_model_and_cited_computation",
            )
            self.assertNotIn("<script src=", html)
            self.assertNotRegex(html, r'<link[^>]+rel=["\']stylesheet["\']')
            self.assertNotRegex(html, r"url\(\s*[\"']?https?://")

    def test_generated_atlas_exposes_routed_home_family_and_space_views(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            html = output_path.read_text(encoding="utf-8")
            for required_route_contract in (
                'id="site-brand"',
                'id="nav-home"',
                'id="nav-spaces"',
                'id="family-toggle"',
                'id="about-toggle"',
                'id="atlas-index"',
                'id="atlas-document"',
                "function parseRoute",
                "function renderRoute",
                "function buildHomeView",
                "function buildSpacesView",
                "function buildFamilyView",
                "function buildSpaceView",
                'hash === "#atlas-document"',
                'kind: "not-found"',
                "buildBreadcrumbs",
                "buildSpaceSearch",
                "Search all spaces",
                "Search this family",
                'href = `#family-${section.id}`',
                'href = `#space=${encodeURIComponent(space.slug)}`',
                "document.title",
                'setAttribute("aria-current"',
            ):
                self.assertIn(required_route_contract, html)
            for required_space_contract in (
                "homologyViewBySpace",
                "buildHomologyControls",
                "space-coefficients",
                "`coefficient-${space.slug}`",
                "`convention-${space.slug}`",
                "renderHomology",
                "renderTex",
                "space.name?.tex",
                "groupPresentation",
                "torsion_orders",
                r"\\oplus",
                "coveragePresentation",
                "coverage-exhaustive",
                "coverage-bounded",
                "buildKnowl",
                "knowl-panel",
                'setAttribute("aria-expanded"',
                'buildKnowl("reduced-homology"',
                'buildKnowl("direct-sum-notation"',
                'buildKnowl("finite-cw-space"',
                'buildKnowl("model"',
                "Copy link",
                "Review details",
                "homology-row-review",
                "Knowledge state",
                "Assertion",
                "Copy JSON",
                "Download JSON",
                "Computation runs",
                "Data quality",
                "Source locator",
                "Model & sources",
                "Classification & record",
                "serializedSpaceRecord",
                "JSON.stringify(space, null, 2)",
            ):
                self.assertIn(required_space_contract, html)
            self.assertNotIn("item.rank === best", html)
            self.assertIn('event.key === "ArrowDown"', html)
            self.assertIn('event.key === "ArrowUp"', html)
            self.assertIn('event.key === "j"', html)
            self.assertIn('event.key === "k"', html)
            for removed_global_control in (
                'id="atlas-search"',
                'id="coefficient-switcher"',
                'id="reduced-filter"',
                'id="reliability-filter"',
                'id="filter-disclosure"',
                'id="review-toggle"',
            ):
                self.assertNotIn(removed_global_control, html)

    def test_generated_atlas_supports_accessible_navigation_knowls_and_themes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            html = output_path.read_text(encoding="utf-8")
            for theme_contract in (
                '<meta name="color-scheme" content="light dark">',
                'id="theme-menu"',
                'name="theme-preference"',
                'value="system"',
                'value="light"',
                'value="dark"',
                "homology-atlas-theme-v1",
                "prefers-color-scheme: dark",
                'window.addEventListener("storage"',
            ):
                self.assertIn(theme_contract, html)
            for accessibility_contract in (
                'id="index-close"',
                'id="index-backdrop"',
                'class="index-backdrop" aria-hidden="true"',
                'aria-controls="snapshot-about"',
                "backgroundInertTargets",
                "trapIndexFocus",
                "getClientRects",
                'atlasIndex.setAttribute("aria-modal"',
                'setAttribute("inert", "")',
                "focusRouteHeading",
                "search-label-text",
                'searchMark.setAttribute("aria-hidden", "true")',
                'plainName.setAttribute("aria-hidden", "true")',
                'atlasIndex.addEventListener("click"',
                "if (!open && snapshotAbout.open)",
                "snapshotAbout.open = false",
                'buildKnowl("ordinary-homology", "Definition")',
                'buildKnowl("model", "What is a Model?")',
                'summary.setAttribute("aria-label", "Provenance")',
                'role", "region"',
                '"aria-labelledby"',
                "definition.assertion_evidence",
                "themeSummary.focus()",
                "source_database_sha256",
                'setAttribute("headers"',
            ):
                self.assertIn(accessibility_contract, html)

    def test_generated_atlas_limits_the_public_surface_to_finished_features(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            html = output_path.read_text(encoding="utf-8")
            for simplified_contract in (
                "const reviewModeEnabled = false",
                "Reviewer-only renderers stay in source for later wiring",
                "const familySearchThreshold = 8",
                "if (members.length > familySearchThreshold)",
                "showAllOnEmpty: false",
                "const visibleMatches =",
                "view.append(hero, familySection)",
                "item.append(main)",
                "if (relations.length) records.append(relationBlock.details)",
                "if (qualityIssueCount) records.append(qualityBlock.details)",
                "if (reviewModeEnabled)",
                "route-view h1[tabindex=\"-1\"]:focus",
            ):
                self.assertIn(simplified_contract, html)
            self.assertNotIn(
                'window.location.search).get("review")',
                html,
            )
            for removed_public_chrome in (
                'id="family-outline"',
                "view.append(feedbackBand)",
                "home-stats snapshot-stats",
                "atlas-principles home-section",
                "snapshot-scope home-section",
                '"space-result-summary"',
            ):
                self.assertNotIn(removed_public_chrome, html)

    def test_presentation_contracts_execute_as_pure_javascript(self) -> None:
        script = r"""
const presentation = require("./static_atlas/presentation.js");
const repeated = presentation.groupPresentation({
  coefficient_ring: "Z",
  knowledge_state: "exact",
  group: {
    state: "exact",
    plain: "unused",
    free_rank: 0,
    torsion_orders: Array(168).fill(2),
  },
});
const malformed = presentation.groupPresentation({
  coefficient_ring: "Z",
  knowledge_state: "exact",
  group: { state: "exact", plain: "0" },
});
const nonexact = presentation.groupPresentation({
  coefficient_ring: "Z",
  knowledge_state: "not_computed",
  group: { state: "not_computed", plain: "not computed" },
});
const completeSpace = {
  homology_coverage: {
    kind: "complete_finite_cw",
    computed_through_degree: 1,
    upper_vanishing_starts_at: 2,
  },
};
const exactRows = [0, 1].map((degree) => ({
  degree,
  coefficient_ring: "Z",
  knowledge_state: "exact",
  group: {
    state: "exact",
    plain: "Z",
    free_rank: 1,
    torsion_orders: [],
  },
}));
const incompleteRows = structuredClone(exactRows);
incompleteRows[1] = {
  degree: 1,
  coefficient_ring: "Z",
  knowledge_state: "not_computed",
  group: { state: "not_computed", plain: "not computed" },
};
const missingUpper = structuredClone(completeSpace);
missingUpper.homology_coverage.upper_vanishing_starts_at = null;
const boundedSpace = {
  homology_coverage: {
    kind: "bounded_through_degree",
    computed_through_degree: 24,
    upper_vanishing_starts_at: null,
  },
};
console.log(JSON.stringify({
  repeated,
  malformed,
  nonexact,
  exhaustive: presentation.coveragePresentation(
    completeSpace, exactRows, { materialized_through_degree: 24 }
  ),
  incomplete: presentation.coveragePresentation(
    completeSpace, incompleteRows, { materialized_through_degree: 24 }
  ),
  missingUpper: presentation.coveragePresentation(
    missingUpper, exactRows, { materialized_through_degree: 24 }
  ),
  bounded: presentation.coveragePresentation(
    boundedSpace, incompleteRows, { materialized_through_degree: 24 }
  ),
  supportedTex: presentation.isSupportedTex(
    String.raw`\operatorname{Th}(\gamma_{2}\to BU(2))`
  ),
  unsafeTex: presentation.isSupportedTex(String.raw`\href{x}{y}`),
}));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(
            result["repeated"]["tex"],
            r"(\mathbb{Z}/2\mathbb{Z})^{\oplus 168}",
        )
        self.assertTrue(result["repeated"]["exact"])
        self.assertFalse(result["malformed"]["exact"])
        self.assertEqual(result["nonexact"]["plain"], "not computed")
        self.assertEqual(
            result["exhaustive"]["className"],
            "coverage-exhaustive",
        )
        self.assertEqual(
            result["incomplete"]["className"],
            "coverage-neutral",
        )
        self.assertEqual(
            result["missingUpper"]["className"],
            "coverage-neutral",
        )
        self.assertEqual(result["bounded"]["className"], "coverage-bounded")
        self.assertIn("Recorded through degree 24", result["bounded"]["detail"])
        self.assertTrue(result["supportedTex"])
        self.assertFalse(result["unsafeTex"])

    def test_export_is_deterministic_for_one_database_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            first_output = directory / "first.html"
            second_output = directory / "second.html"
            ChromaticDatabase.build(database_path)

            for output_path in (first_output, second_output):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(EXPORTER),
                        "--database",
                        str(database_path),
                        "--output",
                        str(output_path),
                    ],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

            self.assertEqual(first_output.read_bytes(), second_output.read_bytes())

    def test_current_snapshot_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            first_output = directory / "first.html"
            second_output = directory / "second.html"

            for output_path in (first_output, second_output):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(EXPORTER),
                        "--snapshot",
                        "current",
                        "--output",
                        str(output_path),
                    ],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

            self.assertEqual(first_output.read_bytes(), second_output.read_bytes())

    def test_checked_in_artifact_matches_the_current_source_build(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "atlas.html"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--snapshot",
                    "current",
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                (REPOSITORY_ROOT / "dist" / "atlas.html").read_bytes(),
                output_path.read_bytes(),
            )

    def test_nonexact_homology_state_is_not_exported_as_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    """
                    UPDATE homology
                    SET knowledge_state = 'not_computed', free_rank = 0, torsion_json = '[]'
                    WHERE space_id = 'sphere:1'
                      AND coefficient = 'Z'
                      AND reduced = 0
                      AND degree = 1
                    """
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            html = output_path.read_text(encoding="utf-8")
            embedded = re.search(
                r'<script id="atlas-data" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            atlas = json.loads(embedded.group(1))
            sphere = next(item for item in atlas["conceptual_spaces"] if item["id"] == "sphere:1")
            row = next(
                group for group in sphere["homology"]
                if group["coefficient_ring"] == "Z"
                and group["reduced"] is False
                and group["degree"] == 1
            )
            self.assertEqual(row["group"]["state"], "not_computed")
            self.assertEqual(row["group"]["plain"], "not computed")
            self.assertNotEqual(row["group"]["plain"], "0")
            self.assertIn("Coverage incomplete", html)
            self.assertIn(
                "groupPresentation(row).exact",
                html,
            )

    def test_export_fails_when_homology_evidence_integrity_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute("PRAGMA foreign_keys = OFF")
                connection.execute(
                    "DELETE FROM evidence WHERE evidence_id = ?",
                    ("chromatic:evidence:sphere:1",),
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("foreign-key failure", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_fails_when_model_and_evidence_inputs_disagree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    "UPDATE model SET chain_sha256 = ? WHERE space_id = 'sphere:1'",
                    ("0" * 64,),
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Model/Evidence input mismatch", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_rejects_relation_evidence_from_another_space(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    """
                    UPDATE space_relation
                    SET evidence_id = 'chromatic:evidence:complex_projective_space:infinity'
                    WHERE relation_id = 'relation:cp2:finite-skeleton:cp-infinity'
                    """
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("references unresolved Evidence", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_rejects_non_https_citation_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    "UPDATE reference SET url = 'http://example.test/source' "
                    "WHERE reference_id = 'hatcher-at'"
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("non-HTTPS source URL", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_export_fails_with_a_precise_malformed_record_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            database_path = directory / "chromatic.sqlite3"
            output_path = directory / "atlas.html"
            ChromaticDatabase.build(database_path)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    "UPDATE space SET label = '' WHERE space_id = 'sphere:1'"
                )
                connection.commit()

            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("malformed Conceptual-space records", completed.stderr)
            self.assertIn("label", completed.stderr)
            self.assertFalse(output_path.exists())

            review_completed = subprocess.run(
                [
                    sys.executable,
                    str(EXPORTER),
                    "--database",
                    str(database_path),
                    "--output",
                    str(output_path),
                    "--allow-malformed-for-review",
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(review_completed.returncode, 0, review_completed.stderr)
            html = output_path.read_text(encoding="utf-8")
            embedded = re.search(
                r'<script id="atlas-data" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            atlas = json.loads(embedded.group(1))
            malformed_space = next(
                item for item in atlas["conceptual_spaces"] if item["id"] == "sphere:1"
            )
            self.assertEqual(malformed_space["data_quality"]["state"], "malformed")
            self.assertEqual(
                malformed_space["data_quality"]["missing_required_fields"], ["label"]
            )


if __name__ == "__main__":
    unittest.main()
