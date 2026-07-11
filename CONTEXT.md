# Homology DB

Homology DB is a queryable, provenance-rich corpus of topological spaces, concrete models, and homology assertions intended for mathematical example retrieval and future computation systems.

## Language

**Conceptual space**:
A named, citable mathematical space or homotopy type that may have multiple concrete models.
_Avoid_: Object, canonical model

**Model**:
A concrete finite presentation of a space, such as a finite simplicial complex or CW complex. A model may remain unidentified.
_Avoid_: Space representation, raw space

**Curated corpus**:
Reviewed conceptual spaces returned by default as meaningful examples.
_Avoid_: Main database, clean data

**Model corpus**:
Concrete models that remain queryable even when unnamed, duplicated, or not attached to a conceptual space.
_Avoid_: Raw database, junk drawer

**Model assertion**:
A sourced claim that a model presents a particular conceptual space at an explicitly stated equivalence level.
_Avoid_: Model link, deduplication

**Homology assertion**:
A sourced or reproducibly computed claim about a subject’s homology for an explicit coefficient system, convention, and degree.
_Avoid_: Homology value, fact

**Knowledge state**:
The mathematical status of an assertion, distinguishing exact, bounded, conjectural, conflicting, unknown, not computed, and not applicable.
_Avoid_: Null state, missing value

**Coefficient system**:
The coefficient ring or field and associated parameters under which a homology assertion is interpreted.
_Avoid_: Coefficients when the context is ambiguous

**Computation run**:
The reproducibility record connecting exact inputs, algorithms, software versions, parameters, logs, and outputs.
_Avoid_: Job, calculation

**Current projection**:
A rebuildable query view selecting the published assertion for each subject, coefficient system, convention, and degree while retaining assertion history.
_Avoid_: Truth table, current facts

**Homology pattern**:
A structured set of required, forbidden, exact, or unknown homology constraints over specified degrees and coefficient systems.
_Avoid_: Similarity prompt, embedding query

**Example query**:
A structured request for conceptual spaces or models satisfying a homology pattern and optional corpus constraints.
_Avoid_: Semantic search when the matching semantics are exact

**Snapshot**:
An immutable, citable release view of records and selected assertions.
_Avoid_: Backup, latest data
