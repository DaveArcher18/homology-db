# Homology DB

Homology DB is a queryable, provenance-rich corpus of topological spaces, concrete models, and homology assertions intended for mathematical example retrieval and future computation systems.

## Language

**Conceptual space**:
A named, citable mathematical space or homotopy type that may have multiple concrete models.
_Avoid_: Object, canonical model

**Model**:
A concrete finite presentation of a space, such as a finite simplicial complex or CW complex. A model may remain unidentified.
_Avoid_: Space representation, raw space

**Model artifact**:
An immutable, versioned encoding of exactly one Model. Multiple artifacts belong to the same Model only through recorded identity evidence; byte-distinct artifacts are never silently merged.
_Avoid_: Model file, engine object

**Source artifact**:
Immutable upstream content retained exactly as received, which may encode zero, one, or many Models. Decoding creates Model artifacts with provenance; the Source artifact never itself counts as a Model.
_Avoid_: Raw model, canonical input

**Derived artifact**:
An immutable computation output made from a Model, such as a based chain complex, boundary matrices, or rendering. It is never reclassified; an admitted topological output instead creates a new Model and Model artifact with a derivation relation.
_Avoid_: Derived model, equivalent copy

**Finite simplicial Model**:
A Model whose finite abstract simplicial presentation determines its geometric realization. Distinct subdivisions remain distinct Models, and a `subdivision_of` assertion records rather than collapses their relation.
_Avoid_: Triangulated space when only a presentation is meant

**Cell-closure poset**:
The cells of a finite cell presentation ordered by inclusion of their closures, excluding any artificial bottom element used by a combinatorial encoding.
_Avoid_: Incidence matrix, face adjacency

**Finite regular-CW Model**:
A Model whose topology is carried by the Cell-closure poset of a finite regular CW complex. Its order complex is the agreed reconstruction and is homeomorphic to the represented realization.
_Avoid_: Incidence complex, arbitrary CW data

**Regularity witness**:
Corrigible evidence that a Cell-closure poset is realizable by a finite regular CW complex, supplied by an owned preserving construction or a checked certificate rather than incidence signs or `d^2 = 0`.
_Avoid_: Regular flag, trusted label

**Family instance assertion**:
An evidence-bearing claim that a conceptual space is the instance of a parameterized mathematical family at specified parameter values.
_Avoid_: Family tag, generated duplicate

**Curated corpus**:
Reviewed conceptual spaces returned by default as meaningful examples.
_Avoid_: Main database, clean data

**Model corpus**:
Concrete models that remain queryable even when unnamed, duplicated, or not attached to a conceptual space.
_Avoid_: Raw database, junk drawer

**Model assertion**:
A sourced claim that a model presents a particular conceptual space at an explicitly stated equivalence level.
_Avoid_: Model link, deduplication

**Model relation assertion**:
An evidence-bearing claim between Models with a named relation kind, such as directed subdivision or an equivalence claim at the presentation-isomorphism, PL-homeomorphism, homeomorphism, or homotopy-equivalence level. It never collapses Model identities.
_Avoid_: Duplicate, same model, automatic merge

**Homology assertion**:
A sourced or reproducibly computed claim about a subject’s homology for an explicit coefficient system, convention, and degree.
_Avoid_: Homology value, fact

**Knowledge state**:
The mathematical status of an atomic assertion, distinguishing exact, bounded, conjectural, unknown, not computed, and not applicable. A current projection may additionally expose a derived conflicting outcome that references the incompatible assertions.
_Avoid_: Null state, missing value

**Homology convention**:
A versioned definition of grading, augmentation, and reduced/unreduced semantics under which homology is interpreted, including exceptional empty-space behavior.
_Avoid_: Reduced flag when the convention is otherwise implicit

**Homology slot**:
The fully qualified location of a possible homology claim: tagged subject, theory, coefficient system, homology convention, reduced/unreduced choice, and integer degree.
_Avoid_: Degree cell, nullable homology column

**Coefficient system**:
The coefficient ring or field and associated parameters under which a homology assertion is interpreted.
_Avoid_: Coefficients when the context is ambiguous

**Computation run**:
The reproducibility record connecting exact inputs, algorithms, software versions, parameters, logs, and outputs.
_Avoid_: Job, calculation

**Current projection**:
A rebuildable query view that selects a published assertion or exposes unresolved selection/conflict for each homology slot while retaining assertion history. Absence is a lookup outcome, not a stored assertion.
_Avoid_: Truth table, current facts

**Editorial event**:
An append-only record explaining a correction, supersession, retraction, or conflict-resolution action with actor, time, reason, and affected assertion IDs.
_Avoid_: In-place edit, validity overwrite

**Conflict set**:
An explicit group of incompatible retained assertions for one homology slot. An open conflict set prevents the current projection from selecting a mathematical value.
_Avoid_: Conflicting value, source-priority winner

**Unresolved selection**:
A current-projection outcome in which multiple active assertions share a homology slot but no versioned selection or conflict decision applies. It is not an atomic knowledge state and carries no selected value.
_Avoid_: Implicit tie-break, inferred conflict

**Mathematical map declaration**:
A stable map identity with explicit domain, codomain, basedness, evidence, and a capability statement describing whether computational map data is actually present.
_Avoid_: Arrow label, implicit relationship

**Structured context assertion**:
An evidence-bearing n-ary claim binding mathematical subjects or maps in named roles, such as a fibration context with total space, base, projection, and typical fiber type.
_Avoid_: Unbound pairwise tags, diagram inferred from names

**Homology pattern**:
A structured set of required, forbidden, exact, or unknown homology constraints over specified degrees and coefficient systems.
_Avoid_: Similarity prompt, embedding query

**Example query**:
A structured request for conceptual spaces or models satisfying a homology pattern and optional corpus constraints.
_Avoid_: Semantic search when the matching semantics are exact

**Snapshot**:
An immutable, citable release view of records and selected assertions.
_Avoid_: Backup, latest data
