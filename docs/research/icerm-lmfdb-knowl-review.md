# ICERM/LMFDB lessons for Homology DB: knowls, labels, trust, and usability

Date: 2026-07-12
Status: source-backed product research; not a schema decision, corpus admission,
or release claim

## Result

Gabriel Ong's reference is David Roe's 24 June 2026 ICERM talk, **Building
mathematical databases**, given during *Machine Computation in Homotopy
Theory*. Roe explicitly presents the LMFDB as a source of design choices for
people building databases in algebraic topology. The
[ICERM program page](https://icerm.brown.edu/program/topical_workshop/tw-26-mch?item=11160)
identifies the speaker, event, and purpose; ICERM hosts the
[talk recording](https://icerm.brown.edu/video_archive/4709) and
[Roe's slides](https://app.icerm.brown.edu/assets/604/11160/11160_6242_Roe_062420261115_Slides.pdf).

The immediately useful idea is correctly called a **Knowl** (plural:
**knowls**), not “knowles,” “knolwles,” or “nulls.” It is not merely a generic
dropdown. In the LMFDB it is a stable, reusable piece of mathematical
exposition that a user opens inline without leaving the current object or
search page. Knowls can themselves contain links to more knowls. This gives a
reader a tunable amount of explanation while leaving the main presentation
compact.

Homology DB should account for that idea before freezing its production
schema, but should not confuse a definition with assertion evidence. The
named-atlas review gate should add a versioned, reviewed **knowledge-entry
seam** and stable term identifiers, then expose references to selected entries
in the existing four-operation envelopes. The browser interaction itself,
general online editing, and mathematical graphics belong to the later UI and
hosting tier.

This split is an inference and recommendation for this project, not a claim
that Roe prescribed this exact architecture.

## Source boundary and access notes

This review uses only:

- the ICERM-owned event page, recording, presenter slides, and the recording's
  caption track;
- the official LMFDB website and knowledge database; and
- the official LMFDB source repository, pinned here to revision
  [`cbcdaee01f1a698eb44a011b8f4290e294a5a7a1`](https://github.com/LMFDB/lmfdb/tree/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1).

The Panopto player identifies an available caption track. It is useful for
locating spoken claims, but it is not a polished verbatim transcript: most
notably, it repeatedly renders “knowls” as “nulls.” Roe's slide headed
“Features” spells **Knowls**, and the official LMFDB site and code use the same
term, so this note silently corrects that transcription error. Timestamps below
refer to the 47:03 recording. No separately edited transcript was linked from
the ICERM event page. The slide deck was available and was checked against the
caption track.

## Direct findings from Roe's talk

The statements in this section are claims made in the talk or its slides, not
Homology DB design decisions.

### An object database needs layered ways in

At **3:44–8:40**, Roe demonstrates a three-part pattern:

1. a browse page for readers who may know little about the topic;
2. a structured search form for readers who know what they seek, including
   valid-input examples, advanced fields, customizable columns, sorting,
   random results, and downloads; and
3. a dedicated home page that presents one object in a human-readable form.

The browse layer supports exploration, while search supports activities such
as looking for counterexamples. Object pages can then show deeper, type-specific
information. This division is also an explicit official LMFDB guideline:
objects get permanent home pages, each object class gets browse-and-search,
and both experts and non-experts are intended audiences
([official README, lines 25–46](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/README.md#L25-L46)).

### Knowls make explanation local and progressive

At **4:49–5:14**, Roe clicks the term “nilpotency class.” Its definition opens
on the same page; he says the mechanism is recursive and then closes it again.
At **6:14–6:20**, he notes that search fields have knowls explaining their
meaning, alongside examples of valid input. At **24:23–25:09**, he explains
that knowls are editable online: a mathematician can contribute prose without
using Git or editing code. He connects them to serving both experts and
learners by making the amount of exposition adjustable.

Roe's slide summary is precise: “Knowls – often used for defining terms,
expand on the same page. Editable online.”

The implementation verifies the interaction. A click is attached to an
element carrying a knowl identifier; the client toggles an existing expansion
or fetches and inserts the rendered entry next to the triggering content
([`lmfdb.js`, lines 102–140 and 225–298](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/lmfdb/static/lmfdb.js#L102-L140)).
Knowls have standalone pages and identifiers as well: the official
[identifier guidance](https://www.lmfdb.org/knowledge/show/doc.knowl.identifier)
says the identifier is used to create links, and the
[knowledge index](https://www.lmfdb.org/knowledge/) searches IDs,
descriptions, hashtags, and full text.

### Knowls are editorial objects, not untracked tooltips

The LMFDB's public knowl pages display authors, review status, last editor,
referrers, edit history, and diffs. A concrete
[reviewed knowl](https://www.lmfdb.org/knowledge/show/cmf.level) demonstrates
that public presentation. An official
[beta naming-conventions knowl](https://www.lmfdb.org/knowledge/show/doc.knowl.naming_conventions)
demonstrates that unfinished status is visible rather than silently presented
as reviewed content.

The pinned source gives the underlying mechanics:

- saving inserts a new timestamped version while accumulating non-minor
  authorship, links, and defined terms
  ([`knowl.py`, lines 295–326](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/lmfdb/knowledge/knowl.py#L295-L326));
- histories retain timestamp, author, content, and status
  ([`knowl.py`, lines 328–349](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/lmfdb/knowledge/knowl.py#L328-L349));
- review records the reviewer and review time for a specific entry version
  ([`knowl.py`, lines 418–420](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/lmfdb/knowledge/knowl.py#L418-L420)); and
- the reviewer screen shows referrers and a diff from the previously reviewed
  content before an entry is marked reviewed
  ([review template, lines 25–61](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/lmfdb/knowledge/templates/knowl-review-recent.html#L25-L61)).

This does **not** mean LMFDB knowls are assertion-level proof objects. They are
editorial mathematical exposition with their own attribution and review
lifecycle.

### Completeness, source, and reliability are first-class user information

At **4:36–4:42** and **12:15–13:18**, Roe contrasts a complete bounded search
with a search for which LMFDB cannot claim completeness. He stresses that an
empty result is useful only when the user can tell whether the search range is
complete. At **25:09–26:28**, he summarizes the three trust surfaces:

- state the regimes in which the collection is complete;
- link each page to where the data came from, including contributor credit;
  and
- describe consistency checks, mathematical checks, known limitations, and
  why users should trust the data.

The official LMFDB object-page guideline likewise requires the properties box
to link to completeness, source, and reliability knowls and asks pages to name
the entities that produced their data
([official README, lines 25–37](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/README.md#L25-L37)).

At **30:29–30:48**, Roe adds that conditional correctness or completeness
should state the condition explicitly, producing a claim of the form “correct
if [named assumption].” This is directly compatible with Homology DB's rule
that unsupported and bounded outcomes remain explicit.

### Prefer stored, checkable results to hidden query-time computation

At **16:42–18:02**, Roe says that early LMFDB pages did more computation on
the fly, but the project has tried to move toward precomputing and storing
results. His reliability reason is concrete: a bug in a software version may
remain invisible in live computation until a user notices, whereas stored data
can be subjected to consistency checks. He also notes practical limits: some
single-object computations are slow, and one cannot search across properties
that have not been computed for the collection.

At **28:02–30:48**, he gives two continuing reasons for mathematical databases
in an AI setting: expensive computations can be done once and reused, and
stored data can be searched. He mentions LMFDB's MCP server as a way for LLMs
to interact with mathematical data, then points toward certificates and
formal checking as future trust mechanisms.

This supports, but did not originate, Homology DB's existing decisions to
materialize family specializations during Snapshot construction, prohibit
query-time formula evaluation, and give every displayed group an immutable
assertion/dependency chain.

### Labels should persist and convey useful mathematics without pretending to
be identity proofs

At **27:11–27:56**, Roe recommends persistent identifiers. LMFDB tries to make
labels encode a few useful invariants—such as degree or group order—so an
expert can learn something from the citation. He also emphasizes a spectrum:
for some object classes the label can recover the object; for others it is
partly descriptive or merely enumerative. The right choice depends on the
object class.

The official guideline is slightly more conservative: labels should be
mathematically meaningful, human-readable, concise, and translate reasonably
directly to permanent URLs
([official README, lines 31–35](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/README.md#L31-L35)).

For Homology DB this argues for separate, permanent machine identifiers and
carefully designed display labels. It does not justify deriving conceptual
identity from label coincidence.

### Graphics should encode mathematics and explain their encoding

At **10:44–11:51**, Roe answers a question about an abstract-group picture.
The disks represent conjugacy classes; disk area and radial position encode
properties, and color records prime-divisor information. He points to a
“Picture description” under “Learn more” that explains how the visualization
is generated. Current official
[abstract-group pages](https://www.lmfdb.org/Groups/Abstract/100.12) exhibit
the same pattern: a properties panel and related objects, downloads, source,
completeness, reliability, labeling, and picture-description links.

The lesson is not “add decorative pictures.” It is that a graphic earns its
place when it gives a repeatable encoding of mathematical structure and comes
with an accessible explanation of that encoding.

### Match infrastructure to scale and maturity

At **15:13–18:02**, Roe describes three visible website maturities:
production, beta for preliminary sections, and alpha for unfinished work that
carries warnings. The LMFDB uses a Flask frontend with templates over
PostgreSQL. The talk puts its hosting cost at roughly USD 1,000 per month and
describes a multi-terabyte dataset.

In the MathBases half, especially **32:08–39:37**, Roe contrasts that heavy
system with a small-data option: static files in GitHub, browser-side search,
and free hosting can be appropriate when the data and search needs are small.
He recommends adapting a working template over starting from nothing, while
noting that an LMFDB-derived template is still planned work. Therefore the
talk does not provide a ready production template that Homology DB can simply
adopt today.

At **44:04–45:45**, Roe candidly describes a provenance limitation: LMFDB's
frontend is on GitHub, but data-generation code is scattered and not always
easy to find. His ideal for new projects is a repository plus explicit input
whose execution generates the data, tempered by the cost of rerunning
hundreds of CPU-years after a bug. Homology DB should preserve its stronger
source-artifact, run, environment, log, and deterministic-Snapshot goals
rather than copying this limitation.

## Recommendations for `named-atlas-review-v1`

These are project-specific inferences from the sources above. They are the
parts that should affect the current review gate.

### 1. Reserve a first-class knowledge-entry seam in the production schema

Add a small editorial subsystem alongside, but not inside, assertion evidence:

- `knowledge_entry`: stable namespaced identifier, entry kind, and canonical
  term or subject relation;
- `knowledge_revision`: immutable content, format version, author/editor,
  creation time, citations, and content hash;
- `knowledge_review`: reviewer, verdict/status, time, note, and the exact
  revision reviewed;
- `knowledge_link`: typed links to other knowledge entries, Conceptual spaces,
  families, Models, assertions, and public-operation fields; and
- `snapshot_knowledge_selection`: the exact reviewed revision selected into a
  Snapshot.

Renames should create aliases or redirects, not rewrite references or merge
Conceptual spaces. Corrections should create new revisions. The Current
projection may select a reviewed revision; history remains available.

This is deliberately parallel to the assertion system. A definition may cite
a textbook and explain notation, but its presence must never count as evidence
for a Homology group, Model identity, implication edge, or completeness claim.

### 2. Add stable definition references to the four-operation contract

Do not add an unscoped fifth mathematical operation. Instead, version the
existing response envelopes so fields and resolved terms can carry
`knowledge_refs`, each containing at least:

- knowledge-entry ID and selected revision ID;
- title and short display text;
- review status;
- content hash; and
- a flag distinguishing `exposition` from `assertion_evidence` (for knowl-like
  entries this must be `exposition`).

`resolve_subject` should return definitions for the resolved family and its
typed parameters. `read_homology` should reference definitions of coefficient,
reduced/unreduced, degree, and group-notation fields where needed.
`query_examples` should expose definitions for query predicates and typed
coverage outcomes. `expand_evidence` should continue expanding evidence—not
silently reinterpret a knowledge entry as evidence—but may report linked
knowledge-entry metadata separately.

Every reference must resolve within the same Snapshot. Missing exposition is
not a mathematical zero or a failed assertion; use a distinct typed editorial
gap if it must be reported.

### 3. Ship a small reviewed glossary with the atlas, not a mass of AI prose

Before reviewer invitation, select reviewed entries for the terms the fixed QA
actually exposes, including:

- Conceptual space, family, family instance, identity assertion, Model, Model
  qualification, assertion, evidence, dependency, Snapshot, and Current;
- integral Homology, reduced Homology, coefficient field, degree, free rank,
  torsion summand, completeness, `not_computed`,
  `outside_materialized_range`, and `model_not_qualified`; and
- the projective-space family parameters and the notation used in their
  displayed groups.

Each entry needs a responsible author/editor, sources where appropriate, a
review verdict, and one selected revision. AI may draft entries, but no
generated entry should become reviewed merely because it is fluent or
mathematically familiar.

### 4. Make bounded completeness visible wherever a user can infer absence

The named atlas already plans `outside_materialized_range` above (n=12) and
`model_not_qualified` where no admitted Model exists. Preserve those outcomes
in search summaries and subject pages/envelopes. An empty `query_examples`
result must state the selected Snapshot and the predicate's coverage regime;
it must not visually resemble a proof that no mathematical example exists.

### 5. Freeze identifier policy before corpus materialization

Use permanent opaque or namespaced IDs as references. Treat human-facing
labels such as `CP^2`, `RP^3`, or `L(2,1)` as display labels and aliases backed
by identity assertions. Let labels carry readable mathematical content where
that remains stable, but do not encode mutable review state, Model choice, or
unproved identity into them. Explicit identity assertions—not matching
labels—connect `CP^1` with `S^2` and the other selected identities.

### 6. Keep the reproducible-computation and provenance gate stronger than
the LMFDB example

Retain the planned source hashes, exact pinpoints, Model-artifact hashes,
algorithm/environment records, logs, assertion dependencies, and deterministic
Snapshot rebuilds. Add a release audit that follows every displayed Homology
assertion back to either cited literature or an owned run and follows every
expository entry back to its selected reviewed revision. These are two
different paths and should be tested separately.

### 7. Record maturity without inviting premature reliance

Continue to freeze `local-preview-60` as a regression fixture and label
`named-atlas-review-v1` explicitly as a review candidate. If a hosted test is
later exposed, show Snapshot/schema version and maturity on every response or
page. Do not borrow “production,” “beta,” and “alpha” labels without defining
their local acceptance meaning.

## Recommendations for later UI and hosting

These items should be designed for now only where a schema seam is necessary;
they need not block the database-connected named-atlas review unless a later
ticket moves UI into scope.

1. **Implement actual inline knowls.** A linked term should open and close an
   adjacent panel without losing the user's place. Nested knowledge links
   should work. The panel should show selected revision, review state, and a
   permalink to the full entry.

2. **Separate browse, search, and object pages.** A novice should be able to
   browse named families and constructions; an expert should have structured
   search; every materialized Conceptual space should have a permanent object
   page with concise invariants, typed coverage, related objects, and expanded
   provenance.

3. **Make definitions contributable without weakening review.** A web editor
   can eventually lower the barrier for mathematicians who do not use Git, but
   it needs authentication, edit conflicts, immutable revisions, preview,
   citation fields, review assignment, diffing, and rollback-by-new-revision.
   Until then, repository-reviewed Markdown or structured fixtures are safer.

4. **Expose trust next to the claim.** Put completeness, source, reliability,
   Model status, and typed gaps in the object-page summary rather than hiding
   them in an administrative screen. Knowls can explain those terms, but the
   actual assertion/evidence identifiers must remain visible.

5. **Wrap the same four operations for agents.** A future MCP server is a good
   transport for AI clients, but it should call the immutable, read-only four-
   operation contract. Roe's mention of direct SQL is not a reason to give
   agents unrestricted database access or introduce a hidden inference layer.

6. **Defer graphics until one has a mathematical encoding.** Candidate later
   graphics include a degree-by-coefficient Homology barcode, Model-comparison
   view, or cited-implication/dependency graph. Require a written encoding,
   accessible text description, provenance for displayed values, deterministic
   rendering, and a test showing that equal Homology is not presented as
   equivalence. Decorative space illustrations do not satisfy this criterion.

7. **Choose hosting after measuring the candidate.** The talk supports a
   spectrum from static GitHub-hosted data to Flask/PostgreSQL at multi-terabyte
   scale. Measure Snapshot size, query needs, concurrent review load, and
   rebuild workflow before selecting a physical deployment. Keep the planned
   SQLite/PostgreSQL benchmark authoritative.

## Consequences for the human-reviewable implication graph

Knowls and the proposed implication graph solve different problems:

- a **knowl-like knowledge entry** explains a term, convention, object family,
  or UI field at the reader's chosen depth;
- an **assertion node** states a reviewable mathematical or provenance claim;
  and
- an **implication/dependency edge** records why one assertion supports or
  specializes to another, with cited hypotheses and evidence.

They should link to each other but remain typed. For example, a knowl may
explain the universal coefficient theorem; a derived field-coefficient
Homology assertion still needs a concrete immutable dependency edge from the
integral assertion and the exact theorem citation. Reviewing the prose is not
the same verdict as reviewing that specialization edge.

This separation preserves the project's central philosophy: AI can help build
a cited graph that is efficient for expert review, while uncertainty,
correction history, and provenance remain visible rather than being smoothed
away by the interface.

## Source-role summary

| Source | Supports | Does not support |
| --- | --- | --- |
| [ICERM event page](https://icerm.brown.edu/program/topical_workshop/tw-26-mch?item=11160), [recording](https://icerm.brown.edu/video_archive/4709), and [Roe slides](https://app.icerm.brown.edu/assets/604/11160/11160_6242_Roe_062420261115_Slides.pdf) | Speaker, date, stated aims, demonstrated UI, design rationale, architecture and scale discussion, MathBases contrast | A turnkey LMFDB template; Homology DB schema acceptance; proof that LMFDB's choices transfer unchanged |
| [Official LMFDB README](https://github.com/LMFDB/lmfdb/blob/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/README.md#L22-L46) | Object pages, meaningful labels and URLs, properties/trust links, browse/search, expert/novice audience | Homology-specific identity, provenance, or completeness semantics |
| [Official LMFDB knowledge index](https://www.lmfdb.org/knowledge/) and example knowls | Actual term, stable IDs, authorship, visible beta/reviewed state, history/diffs, cross-references | Assertion-level mathematical evidence or immutable Snapshot selection |
| [Pinned LMFDB knowl source](https://github.com/LMFDB/lmfdb/tree/cbcdaee01f1a698eb44a011b8f4290e294a5a7a1/lmfdb/knowledge) | Inline rendering, revision storage, author accumulation, review metadata, diffs and referrers | A requirement to copy LMFDB's implementation or grant public editing immediately |
