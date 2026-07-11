# Project brief

## North star

A mathematician should be able to find a space, inspect known invariants and models, understand exactly where every claim came from, reproduce machine computations, follow relationships to nearby objects, and cite a permanent page or data record.

The project is an atlas, not merely a calculator and not merely a table of Betti numbers.

## Confirmed downstream consumers

### Spectral-sequence computation engines

Homology DB should provide reliable upstream objects and invariants to future spectral-sequence software. A group isomorphism type alone is generally insufficient for this role. The project must retain concrete models and be able to attach computation-ready chain complexes, basis conventions, boundary maps, filtrations, maps, and representative cycles when the chosen spectral-sequence workflow requires them.

The first intended spectral-sequence consumer is Serre/Leray–Serre; Adams follows later. This means the shared identity layer must eventually represent actual maps and fibrations—not merely loosely typed related-object links—and must be able to attach coefficient systems, actions, filtrations, chain-level representatives, and conventions. Adams will later add spectra, graded algebra/module/comodule structures, operations, and extension data.

Do not implement either spectral-sequence domain in the Homology DB milestone, and do not invent one universal spectral-sequence table. Preserve room for versioned domain modules sharing the same mathematical objects, maps, assertions, sources, computation runs, and snapshots.

### LLM example retrieval

An LLM tool should be able to translate requests such as “find examples of spaces with homology like this” into a documented structured query and return sourced, machine-readable candidates.

“Like this” must become explicit constraints rather than an opaque embedding score. Initial similarity dimensions should include:

- coefficient system and reduced/unreduced convention;
- degree window;
- exact, required, forbidden, or unknown groups by degree;
- Betti-number patterns;
- torsion primes, exponents, and multiplicities;
- space/model class and construction constraints;
- completeness and reliability requirements.

Every match should explain which constraints it satisfied, expose unknown fields, and link to the supporting assertions and models. Semantic/vector retrieval may later help interpret natural language, but it must not replace the structured mathematical query or its explanation.

## What to copy from LMFDB

LMFDB's most valuable contribution is its product contract:

- every mathematical object has a permanent home page and label;
- every object class has novice-friendly browsing and expert search;
- technical terms have short, context-independent knowledge entries ("knowls");
- object pages expose related objects, downloads, and provenance;
- source, completeness, and reliability are visible rather than buried;
- data and code snippets are intended to be reusable.

Its [developer guide](https://github.com/LMFDB/lmfdb/blob/main/Development.md) also recommends iterating with both experts and nonexperts and consulting existing developers before introducing top-level identifiers or labels. The [style guide](https://github.com/LMFDB/lmfdb/blob/main/StyleGuide.md) makes source, completeness, reliability, and label documentation standard parts of every object family.

## First scope decision

"Algebraic topology" is too broad to be a first database boundary. There are three credible starting wedges:

| Wedge | First-class object | Strength | Main risk |
|---|---|---|---|
| Spaces and ordinary homology | Space plus finite model | Broadly understandable, computable with existing tools, and extensible | Identity and equivalence of spaces are subtle |
| Stable stems and spectral sequences | Spectrum, class, and differential | High research value and relationship density | Specialized notation, disputed extensions, and difficult curation |
| Knots/manifolds and invariants | Knot or triangulated manifold | Existing corpora and mature search questions | Overlaps established projects such as KnotInfo and simpcomp |

### Recommendation

Start with **spaces and ordinary integral homology**, using finite simplicial and CW presentations. This is a foundation on which the other wedges can later sit, and Sage, HAP, and simpcomp provide realistic computation and import paths.

The first release should answer:

1. What is this space?
2. Which concrete models represent it?
3. What are its homology groups in each known degree and coefficient system?
4. Was each value proved in a reference, computed by software, or inferred from another certified result?
5. Which spaces and constructions are related to it?
6. Can I download the model, result, and reproduction recipe?

## MVP boundaries

### In scope

- named spaces and small parameterized families;
- finite simplicial and regular CW models;
- versioned chain-complex artifacts derived from those models, including boundary matrices and basis conventions where available;
- ordinary homology over the integers and finite fields;
- degree-by-degree group decomposition;
- basic metadata: dimension, connectivity when known, compactness, orientability where applicable, Euler characteristic, and cell/face counts;
- relationships such as model-of, homotopy-equivalent-to, homeomorphic-to, suspension-of, wedge-of, product-of, covering-of, and boundary-of;
- references, contributors, software/version/environment, input hashes, and result status;
- browse, search, object pages, downloads, and a read-only versioned API;
- computation-ready and LLM-tool-friendly bundles with explicit schemas and snapshot identifiers;
- concise knowledge entries for terminology and conventions.

### Explicitly out of scope for the first release

- classification of arbitrary spaces or recognition of arbitrary equivalent presentations;
- user-submitted untrusted computation;
- generalized (co)homology theories;
- full cohomology rings and operations;
- homotopy groups and spectral-sequence charts;
- a proof assistant or a claim that every computed result is formally verified;
- replacing Sage, HAP, simpcomp, KnotInfo, or other specialist databases.

## Pilot corpus

Use a small corpus designed to stress the data model, not impress by row count:

- points and spheres in several dimensions;
- orientable and nonorientable closed surfaces;
- tori and products of spheres;
- real and complex projective spaces in bounded dimensions;
- lens spaces;
- wedges, suspensions, cones, and selected mapping cones;
- two or more distinct finite models of several of the same spaces;
- a handful of examples with torsion and a handful with an intentionally unknown field.

A useful first acceptance target is 30–50 conceptual spaces, 50–100 concrete models, and independently checked homology results. The exact count is less important than covering identity, torsion, provenance, conflicting evidence, and multiple presentations.

## Success criteria for the vertical slice

- A stable URL resolves for every conceptual space and every model.
- Search can filter by dimension, model type, Euler characteristic, Betti number, torsion prime, and result status.
- Every displayed invariant has a source or a reproducible computation record.
- "Unknown", "not computed", "not applicable", "conjectural", "bound", and "exact" are distinct states.
- Two independent backends agree on a selected validation subset, or disagreements are displayed and retained.
- A full database export and a per-object JSON download are documented.
- A nonexpert can browse from examples without knowing a label, while an expert can formulate a precise query.

## Independent project or LMFDB contribution?

Begin independently but stay structurally compatible with LMFDB ideas.

Pursue an actual LMFDB blueprint only if all of the following become true:

- the desired outcome is an official section of lmfdb.org;
- LMFDB maintainers support the mathematical scope and labeling scheme;
- the project accepts the existing Sage/Python, Flask/Jinja, PostgreSQL/psycodict stack;
- contributors accept the upstream GPLv2+ license and review process;
- data ownership, hosting, and editorial maintenance have named owners.

Until then, copying information architecture is safer than copying application code.

## Decisions for the first planning meeting

1. **Audience:** research mathematicians first, students first, or equal priority?
2. **Identity:** are conceptual homotopy types the main objects, or are finite presentations the main objects?
3. **Pilot:** is the recommended spaces-and-homology wedge acceptable?
4. **Authority:** may a reproducible computation be published as exact without a literature citation, and under what validation rule?
5. **Destination:** independent public project, eventual LMFDB proposal, or undecided?
6. **Editorial ownership:** who can approve labels, equivalence assertions, and disputed results?

The second question is the most consequential. This plan recommends conceptual spaces as the public objects and finite presentations as separately addressable models.

### Current answer on identity

Use a provisional two-tier corpus:

- curated conceptual spaces are the default citable and LLM-facing examples;
- raw computational models remain separately searchable, including models whose homotopy type is unknown;
- attaching a model to a conceptual space requires a sourced assertion.

This policy is accepted only insofar as concrete fixtures show that the data layers remain coherent. It is not a reason to freeze the full schema early.
