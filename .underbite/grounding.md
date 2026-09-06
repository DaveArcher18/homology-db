# Current technical grounding

Baseline e33e830: static self-contained dist/atlas.html, built with
scripts/export_static_atlas.py. Rendering lives in static_atlas/atlas.js,
workbench.js and atlas.css. 42 retained space routes, 3 general formula families,
49 secondary spectrum routes. 13-space five-field ring core in
homology_db/classical.py; source rules in homology_db/families.py and mirrored
static_atlas/families.js. Source-bound deterministic artifact gate must be kept.

Review register homology_db/family_reviews.py currently accepts whole-rule
reviews only, stores none, binds exact rule/version/hash, and requires named
human plus maintainer validation. Narrow review must remain narrower than
whole-rule acceptance and cannot turn the whole-rule badge green.

Existing checks: 189 Python tests (3 optional skips); browser scripts for family,
navigation and space reading. Source freeze before full-suite/rebuild is required
because fixture evidence binds source hashes. Existing untracked Steenrod
artifacts/feedback belong to the user and must remain untouched.
