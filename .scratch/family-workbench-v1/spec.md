# Family-first workbench — approved implementation contract

David explicitly approved implementation, independent verification, commit,
push/merge and publication to existing GitHub Pages on 2026-09-06. No purchases
or outreach. This is the next cycle, not an acceptance of earlier mathematics.

## UX and behaviour

Replace the primary navigation with a searchable family picker, finite
nonnegative dimension control, and results. RP^n, CP^n and S^n have sourced
all-n/all-degree rules. Display Z separately, Q separately, and F2/F3/F5/F7/F11
together; compare ordinary unreduced homology and cohomology degree by degree.
Initially show 0–8, allow arbitrary-degree windows, and always show general
formulas. Any reduced homology choice does not change the cohomology ring.
Preserve other spaces, spectra as secondary, downloads and existing links.

Keep semantic mathematical typesetting including inside knowls. Add searchable,
linkable glossary for basic rings, polynomial/quotient/exterior rings, grading,
generators, relations, cup products, torsion and reduced conventions. Lambda
here denotes exterior algebra, not specialist lambda-ring operations.

Expandable cup-product matrices include the unit, named homogeneous additive
generators, degrees, and integral torsion orders. Full matrices for <=12
generators; larger ones use a labelled selectable window and the general rule.
Homology, cohomology and multiplication completeness are separate from display
limits and human-review state. Missing data never means zero.

## Provenance and review

Version/hash-bind general rules, derivations, citations and exact review scope.
Human review pending until a named, maintainer-validated review covers that exact
rule. Preserve append-only reviews and invalidate coverage for changed rules.
One-click prefilled GitHub family review form, human submits accept/reject/
needs-evidence. Gabriel's screenshot feedback (typeset knowls, multiplication
tables, exhaustiveness labels) is product feedback only, not math acceptance.

## Implementation and proof

Static hosting, versioned family interface with parameter/degree evaluation,
products/coverage/source/review metadata; do not enumerate unbounded families.
Retain legacy snapshot and stable-spectrum gate. Split package if needed.
Primary-source qualification; independent math and implementation review;
boundary, parity, torsion, all coefficients, large dimension/degree tests;
browser mobile/keyboard/knowl/state/download/legacy-route checks. Commit frozen
source, deterministically export, run release gate, publish and verify live.

## Not in scope

New topology families beyond the three named ones; specialist lambda operations;
outreach, paid services, or manufactured human review.
