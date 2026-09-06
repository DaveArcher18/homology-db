# Development

Start from the repository root with Python 3.11 or newer. The exporter uses
`datetime.UTC`, so the old Python 3.10 README requirement was insufficient.
The core Python tools use the standard library; no virtual environment or
third-party package installation is required.

## First check

```sh
python3 -m homology_db chromatic demo
python3 -m unittest discover -s tests
```

Use the explicit `chromatic` command for the current ordinary-space corpus.
Unprefixed `python3 -m homology_db ...` commands retain an older regression
fixture; they are not the same dataset as the current atlas.

Run a focused test while developing, for example:

```sh
python3 -m unittest tests.test_families tests.test_family_reviews
```

Optional external-consumer tests can skip when their tools are absent. Read
the test output rather than assuming every consumer was exercised.

## Build the current public-preview atlas

```sh
python3 scripts/export_static_atlas.py \
  --snapshot current \
  --output dist/atlas.html \
  --steenrod-review-candidate \
  --allow-public-review-preview
```

This preserves the secondary stable-spectrum preview and its existing links.
Omitting the two preview flags intentionally builds a spaces-only variant.
The preview flag does not claim human acceptance.

Open `dist/atlas.html` directly in a browser. The HTML includes its data and
assets; no development server is required. Links to sources and GitHub forms
still use the network.

## Browser checks (optional local setup)

The browser scripts require Node.js, Playwright, and Google Chrome. They launch
Chrome through Playwright's `channel: 'chrome'`; having only another Playwright
browser installed is not enough. Use an existing Playwright installation on
Node's module search path. These are separate from the dependency-free Python
checks.

```sh
node scripts/verify_family_browser.cjs dist/atlas.html
node scripts/verify_navigation_browser.cjs dist/atlas.html
node scripts/verify_space_reading_browser.cjs dist/atlas.html
node scripts/verify_textbook_browser.cjs dist/atlas.html
```

The scripts also accept the live atlas URL instead of a file path. They check
navigation, responsive layouts, examples, and review packets without submitting
public reviews. Some scripts save screenshots in the system temporary directory.

## Release provenance

For a release, commit the source inputs first, then build the artifact and run:

```sh
python3 scripts/verify_steenrod_release.py \
  --atlas dist/atlas.html \
  --allow-public-review-preview \
  --verify-rebuild
```

The gate checks source identity and a deterministic rebuild. A local preview
from dirty source is useful during development but is not a verified release.
Commit the artifact separately without changing its source inputs. Rebasing or
squashing source commits can change the embedded identity: rebuild and recheck
afterward, rather than editing the metadata manually.

The [Pages workflow](../.github/workflows/deploy-atlas-pages.yml) validates and
publishes the checked-in artifact on qualifying pushes to `main`. Maintainers
then compare the live file byte-for-byte and run live browser checks. A
documentation-only change does not require rebuilding the unchanged atlas.

## Deeper references

- [Static read-model and build contract](static-atlas-read-model.md)
- [Family review workflow](reviews/FAMILY_REVIEW_GUIDE.md)
- [Stable-spectrum review and release distinctions](reviews/README.md)
- [Command-line test drive](TEST_DRIVE.md)
- [Documentation index](README.md)
