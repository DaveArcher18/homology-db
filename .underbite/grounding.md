# Current technical grounding

Historical F-01 baseline `e33e830`: static self-contained `dist/atlas.html`, built with
scripts/export_static_atlas.py. Rendering lives in static_atlas/atlas.js,
workbench.js and atlas.css. 42 retained space routes, 3 general formula families,
49 secondary spectrum routes. 13-space five-field ring core in
homology_db/classical.py; source rules in homology_db/families.py and mirrored
static_atlas/families.js. Source-bound deterministic artifact gate must be kept.

Review register homology_db/family_reviews.py currently accepts whole-rule
reviews only, stores none, binds exact rule/version/hash, and requires named
human plus maintainer validation. Narrow review must remain narrower than
whole-rule acceptance and cannot turn the whole-rule badge green.

At that baseline, checks comprised 189 Python tests (3 optional skips) and browser scripts for family,
navigation and space reading. Source freeze before full-suite/rebuild is required
because fixture evidence binds source hashes. Existing untracked Steenrod
artifacts/feedback belong to the user and must remain untouched.

## Static delivery scaling, 2026-09-11

The live post-PR-4 baseline is merge `f6dab91`: 42 spaces, three formula
families, 49 secondary spectra, a 5,387,491-byte self-contained HTML artifact,
and 212 passing Python tests with three optional skips. The exporter already
constructs and validates one complete structured read model before rendering.

The frontend's scaling bottleneck is delivery, not canonical mathematics:
`static_atlas/atlas.js` synchronously parses `#atlas-data`, creates global maps
of every space/section/definition, and renders routes from that object. Space
records are already self-contained enough to partition; stable IDs/slugs,
coverage, Models, Evidence, citations, computations, relationships, review
state, downloads, and source/Snapshot bindings already exist.

The credible route is a deterministic static bundle: a small catalogue, shared
catalogs, and one complete JSON document per space/spectrum, loaded through a
small client data store. Keep a separately generated self-contained HTML file
for `file://` offline use, where neighbouring JSON fetches are unreliable. No
runtime database is required. The exact interface and migration constraints are
recorded in `docs/architecture/static-data-bundle-v1.md` and Feature F-02.

The hard traps are mixed cached releases, treating fetch failure as absent
mathematics, breaking hash routes/history, and invalidating deterministic
source-bound release identity. Bundle/manifest/subject IDs, versioned request
URLs, explicit loading/error states, reconstruction tests, and dual artifact
parity address those traps. Hosting and the larger computed corpus remain
separate later decisions.
