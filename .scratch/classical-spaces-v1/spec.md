# Classical spaces reference — next iteration

Status: implemented and independently reviewed; final release verification pending

## Purpose and accepted direction

Serve students working at Hatcher level: find a familiar space, read ordinary
homology and cohomology, understand its cup products, and locate the source.
David selected both theories with rings central, a small textbook core, and
fields first while retaining integral homology on 2026-09-06.
The meeting with Gabriel and Dan supports usefulness before new computation
infrastructure; neither participant has committed to implementation or review
dates. This scope supersedes the old brief's exclusion of cohomology rings for
this iteration only.

## Starter corpus

Use these 13 existing conceptual spaces, retaining their IDs and URLs:

| Entries | Role in the reference |
| --- | --- |
| Point; S⁰, S¹, S², S³, S⁴ | Basic examples; disconnected versus connected degree zero |
| Torus T²; Klein bottle | Familiar surfaces, products, and coefficient dependence |
| RP², RP³, RP⁴ | Projective examples and characteristic dependence |
| CP²; S² ∨ S⁴ | A paired explanation of why additive groups do not determine a ring |

The torus supplies the initial product example; arbitrary product construction
is deferred. Keep all other existing space pages searchable with their existing
homology. Label cohomology coverage explicitly; do not imply all 42 entries have
new ring data. Broader Hatcher extraction, new spaces, infinite-family ring
coverage, operations, spectral sequences, and computation engines are deferred.

## Page and navigation design

Home: a short student-facing purpose, prominent existing search, and a compact
"Start with these spaces" group. Keep access to the complete Spaces directory.
Remove chromatic motivation from default home, family, and space copy. Preserve
the spectrum preview and its existing routes under a secondary About/resource
link, retaining its review labels.

Space-page reading order:

```text
CP² — Complex projective plane
Short classical definition                 Copy link

Coefficients:  Q  F₂  F₃  F₅  F₇  Z

Cohomology
  Ring presentation
  Named generators and their degrees
  Relations / meaning of the cup products
  Degree-by-degree groups
  Source and coverage

Homology
  Degree-by-degree groups
  Reduced/unreduced control local to this section
  Source and coverage

Why ring structure matters [related example, where curated]
Definition links · Model & sources · Correct or improve
```

Default to Q on the 13 starter pages and preserve Z as the default on existing
homology-only pages. One coefficient choice controls both theories on a page;
unavailable theory/coefficient data is explicitly "Not recorded", never silently
replaced by another coefficient. Preserve choices per space as the app already
does. Cohomology rings use ordinary unreduced cohomology with a unit; the existing
reduced-homology control cannot change ring conventions. Display degree zero
correctly for S⁰ rather than assuming connectedness.

Reuse semantic TeX, current responsive layout, and inline definition controls.
Define cohomology, cup product, generator degree, relation, and coefficient field.
No general nested-knowl framework, comparison application, or new UI framework
is required. The paired examples use explanatory text and reciprocal links.

## Data and implementation boundaries

Require sourced Q, F₂, F₃, F₅, and F₇ cohomology groups and rings for all 13
starter spaces. Retain existing integral homology. Add integral cohomology rings
only where the same qualified source supplies an explicit presentation; these
are optional coverage, not an iteration completion requirement.

Before coding mathematical records, qualify each family/coefficient formula
against a primary text with an exact section/example/page locator. Existing
citations for homology or cell structures do not automatically support rings.
Record basis and generator conventions, grading, characteristic-sensitive signs,
and complete versus bounded scope. The plan contains no approved ring formulas.

Add versioned cohomology records keyed by existing space identity and coefficient,
containing additive degree data, structured homogeneous generators and relations,
unit convention, coverage, source locators, and provenance/review state. Render
TeX from these records; do not store display text as the sole ring representation.
Keep sourced ring claims distinct from derived additive checks. Boundary matrices
alone do not provide cup products. Do not claim formal verification or reconstruct
integral rings from field results.

Extend the current static exporter/read model and per-space JSON additively;
preserve existing homology CLI responses, identifiers, and old snapshots. Bump
the atlas read-model version for the new capability and test older optional-field
handling. Keep deterministic single-file delivery and the existing release size
limit. No backend replacement or general symbolic algebra engine is in scope.

## Acceptance and delivery order

1. Qualify sources and freeze exact record shape, presentations, and conventions.
2. Implement the full CP² / S² ∨ S⁴ page pair with Q and F₂ first, including
   sources, definitions, additive rows, and missing-data behavior.
3. Extend the same path to all 13 spaces and five required fields; simplify home
   and family copy and keep existing routes available.
4. Verify and prepare a local review candidate with a short reviewer checklist.

Tests must cover generator/relationship grading and source resolution; the
CP²/wedge distinction; torus products and odd-characteristic signs; real
projective and Klein bottle coefficient changes; S⁰ degree-zero multiplication;
agreement of field additive dimensions with independently derived homology
dimensions; missing versus zero; and unchanged noncore/stable routes. These
checks establish consistency, not independent proof of all source mathematics.

Browser acceptance: find a space by name or notation, switch coefficients, read
the ring and its generator degrees, open a definition and source, follow the
paired example, and return using browser history. Exercise keyboard navigation
and narrow screens. Rebuild twice and compare bytes; run the existing regression
suite and current artifact-size checks.

Prepare three review tasks: compare CP² with the wedge, inspect an RP example
over F₂ and Q, and look up a familiar surface. Capture mathematical feedback
separately from usability feedback. Dan/Gabriel review remains pending until
actually received. A proper domain and public announcement follow review;
the autonomous run may publish on the existing Pages site after primary-source
qualification, automated checks, and independent agent review. User explicitly
authorized commits, push/merge and deployment. Human review remains pending and
is not a publication blocker; unresolved mathematics may be marked as a gap while
verified coverage ships. No purchases or messages to others are authorized.
