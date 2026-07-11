# Current assertion projection contract v1

Status: normative for Homology DB `0.0.1` planning and implementation.

This contract defines how immutable Homology assertions and append-only
editorial history produce the snapshot-bound Current projection consumed by
[homology pattern v1](homology-pattern-v1.md). It does not choose a database,
an organizational review hierarchy, or a source-reliability ranking.

## Non-negotiable boundary

The system has three independent axes:

1. a **Knowledge state** describes the content of one mathematical assertion;
2. an **Admission decision** says that the assertion is eligible to participate
   in a published snapshot;
3. the **Current projection** reports what the admitted active assertions imply
   for one fully qualified Homology slot.

`unknown`, `not_computed`, and `not_applicable` are Knowledge states. They are
not editorial statuses. Conversely, unpublished, superseded, and retracted are
editorial dispositions and are not claims that a Homology group is unknown or
zero.

Assertion presence alone never admits it. A newer timestamp, a preferred
source, a successful computation, or a stronger-looking Knowledge state never
selects it. Those facts may inform an editor or a versioned admission policy,
but they do not alter the reducer described here.

## Selection key

The selection key for an atomic Homology assertion is exactly one Homology
slot:

```text
(subject_kind, subject_id, theory_id, coefficient_system_id,
 convention_id, reduced, degree)
```

The subject kind is tagged. A Model slot and a Conceptual-space slot never
share a selection key even when a reviewed `model_of` assertion relates their
subjects. All axes use canonical versioned identifiers; no default is supplied
during projection.

Supersession and Conflict sets are confined to one complete selection key.
A correction that changes any axis is a cross-slot correction: it retracts the
old assertion and admits a fresh assertion in the new slot, but it is not a
Homology supersession edge. The fresh assertion must independently satisfy the
complete admission and derivation policy for its new slot. In particular,
changing Model subject to Conceptual-space subject requires the Promotion rule
below, and changing coefficients or conventions requires a registered
inference rather than editorial rekeying.

## Immutable assertion boundary

A Homology assertion contains immutable claim material:

- assertion ID and assertion-schema version;
- the complete Homology slot;
- Knowledge state and its state-specific canonical Claim payload, including
  every value-scope or completeness semantic;
- derivation kind;
- immutable evidence and provenance references;
- immutable dependency references for derived or promoted assertions.

It does not contain `is_current`, a mutable review/publication status, a
validity interval, retraction state, Conflict-set status, or a canonical
`supersedes` field. Those are editorial-history concerns. If an API expands
`supersedes` beside an assertion, it is a projection of the canonical Editorial
event and never a second writable authority.

Every assertion is evidence-bearing. The required evidence shape depends on
derivation kind. In particular, computation evidence names exact input and
output hashes, algorithm and implementation versions, parameters, exit state,
and retained logs; literature evidence uses a structured reference and a
pinpoint when the source provides one.

### State-specific payloads

Every Knowledge state has a versioned typed payload:

| Knowledge state | Required semantic payload | Forbidden shortcut |
| --- | --- | --- |
| `exact` | Coefficient-appropriate canonical value and explicit value scope; `complete_group` is required to prove v1 mathematical predicates | Display text as the only value |
| `bounded` | A registered bound schema and all operands/scope | An untyped note |
| `conjectural` | A registered conjecture schema and proposed content/scope | Treating the proposal as exact |
| `unknown` | Explicit scope and reason code, with no mathematical value | SQL null or bare absence |
| `not_computed` | Qualifying computation scope/status, with no mathematical value | Failed or absent run inferred from missing rows |
| `not_applicable` | Applicability-rule reference and scope, with no mathematical value | A generic error string |

The state schemas may grow by version. The reducer does not reason that two
different bounded or conjectural payloads are compatible, nor that one entails
another.

## Claim fingerprint

`claim_fingerprint_v1` is the SHA-256 of a version-tagged canonical encoding of:

```text
(complete selection key, Knowledge state, canonical Claim payload)
```

It excludes source, derivation kind, citation, computation run, contributor,
editorial actor, wall-clock times, and display notation. Those fields explain
and corroborate a claim; they do not change its semantic identity.

Two assertions corroborate one another only when this fingerprint is bytewise
equal. Canonical equality is deliberately narrower than mathematical
compatibility:

- two independently computed canonical copies of `Z/6` have one fingerprint;
- exact zero and absence do not;
- the same displayed group under different coefficients or conventions does
  not;
- an exact claim and a compatible-looking bound do not;
- two state assertions with different typed scopes do not.

The project does not perform theorem proving, bound intersection, UCT, or
source reconciliation while computing this fingerprint.

## Editorial ledger

Editorial events are immutable and form the sole lifecycle authority. Every
selection-affecting event contains:

- stable event ID and event-schema version;
- one unique immutable total ledger position, with optional additional causal
  predecessor references;
- a canonically encoded unordered set of typed effects, each carrying its own
  kind and exact target IDs or content-addressed enumerated target manifest;
- actor, recorded time, reason, and evidence references;
- authorization-policy and accepted authorization-decision references;
- the expected global ledger revision.

Recorded time is audit metadata, not replay order. Database insertion order,
UUID implementation details, source date, and locale never determine an
effect. Replaying an event ID with identical canonical bytes is idempotent;
reusing it with different bytes is an integrity error. Wildcard targets such as
“all matching assertions” are forbidden.

One Editorial event is one ledger-positioned atomic change set containing one
or more typed effects. Effects have no independent positions or replay order:
the builder validates all of them against the pre-event state plus fresh records
declared by that event, computes one joint post-state, and rejects contradictory
effects. For serialization and digests only, effects are sorted bytewise by
`(kind, canonical target-manifest digest, canonical effect bytes)`; this order
does not change their joint semantics. The expected global ledger revision
makes concurrent or stale events unambiguous. This permits a correction to
admit successors and retire
predecessors, or a conflict extension to admit and add a fresh member, without
exposing a partial intermediate state. All effects append or none do.

The organizational authorization rules are not fixed here. Human review,
dual review, or admission by a validated owned-computation policy may all be
configured later, but the accepted decision and policy version must be pinned
in the Snapshot.

### Admission and activity

An assertion begins unadmitted. Exactly one effective Admission decision makes
it projection-eligible. That decision may be a `publish_assertion` effect or the
admission effect of a correction or supersession Editorial event.

For v1, retirement is terminal:

```text
active(assertion, snapshot) :=
    assertion is a snapshot member
    and has exactly one valid Admission decision in the snapshot
    and is not the predecessor of an effective supersession event
    and is not the target of an effective retraction event
```

Mandatory dependency validity is checked after this explicit-lifecycle fold.
An active derived or promoted assertion with an invalid dependency makes the
Snapshot invalid; it is never silently removed from `active` to manufacture
absence.

Withdrawing a successor never resurrects its predecessor. If an earlier claim
is endorsed again, the system appends and admits a fresh assertion, usually
with the same Claim fingerprint and an audit link to the history.

Unadmitted assertions may be retained for review and history, but they do not
cause `unresolved_selection`. An admitted `unknown`, `not_computed`, or
`not_applicable` assertion is active exactly like an admitted exact assertion.

### Minimum lifecycle effects

| Effect kind | Required preconditions | Selection effect |
| --- | --- | --- |
| `publish_assertion` | Schema-valid unadmitted assertion; evidence and dependencies resolve; exact scope authorized | Admits the assertion |
| `supersede_assertions` | One or more fresh successors, one or more active predecessors, one complete selection key, acyclic edges, authorized decision | Atomically admits every successor and terminally retires the predecessors |
| `correct_assertions` | Supersession preconditions plus a defect classification and correction evidence | Same lifecycle effect as supersession, with correction semantics recorded |
| `correct_assertion_scope` | Active old assertion and fresh assertion have different keys; exact old/new targets are named; the fresh assertion passes the new slot's full derivation/admission policy | Atomically retracts the old assertion and admits the new one; creates an audit link but no cross-slot supersession edge |
| `retract_assertion` | Active target, reason and evidence, exact scope authorized | Terminally retires the assertion without asserting its negation |
| `declare_conflict` | Valid active same-slot member set and registered incompatibility evidence | Opens a Conflict set and blocks selection |
| `extend_conflict` | One open set; resulting member set remains maximal and valid; fresh members are already active or admitted in the same Editorial event | Appends members without rewriting the declaration |
| `resolve_conflict` | One open set and explicit disposition of every incompatible active claim class | Closes the set; assertion lifecycle effects are explicit in the same Editorial event |
| `record_review` / `annotate_assertion` | Existing explicitly named target IDs and authorized audit effect | Adds evidence only; cannot change lifecycle or selection |

The canonical supersession relation lives in the event ledger. It must be
same-slot, irreflexive, acyclic, and duplicate-free. `fresh` means a
schema-valid Snapshot-member assertion with no earlier Admission or lifecycle
effect; `active` has the definition above. One Editorial event may admit multiple
forked successors of the active predecessor. If their Claim fingerprints differ,
the projection is honestly unresolved until a later Editorial event. A later
genealogical note about an already retired predecessor has no second retirement
effect and is not a supersession edge.

A malformed or unauthorized event appends no partial effects. The physical
transaction mechanism is deferred, but the observable operation is atomic.

## Conflict sets

Conflict is declared, never guessed. Multiple unequal active claims without a
Conflict set produce `unresolved_selection`, not `conflicting`.

For one Snapshot and Homology slot, v1 permits at most one effective open
Conflict set. Its effective member set is a subset of the complete active set
and must:

- contain at least two active assertions in exactly that slot;
- contain at least two distinct Claim fingerprints;
- cite a registered incompatibility rule and evidence;
- contain no retracted, superseded, unadmitted, or dangling member;
- contain every active assertion whose Claim fingerprint participates in a
  checked incompatibility edge, while permitting nonconflicting active claims
  such as explicit `unknown` to remain outside the set.

Canonical unequal exact group values have a registered v1 incompatibility
rule. Exact beside `unknown`, `not_computed`, or a different scoped bound is not
by itself a mathematical contradiction and cannot use that rule. General
incompatibility reasoning for bounded and conjectural claims is deferred.

Conflict status is reconstructed from declare, extend, and resolve events; no
mutable `status` field is authoritative. Adding or retiring a member requires
an atomic extension or resolution so a tagged Snapshot never contains a stale
or partial open set. Closing a set does not select a winner: the accompanying
lifecycle events must leave zero or one active Claim-fingerprint class, or the
result remains `unresolved_selection`.

## Deterministic reducer

For each selection key in a valid Snapshot, `current_projection_v1` performs:

```text
history := every snapshot-member assertion with this complete key
active := canonically sort the active admitted subset by assertion ID
open_conflicts := effective open Conflict sets for this key

if active is empty:
    absent
else if there is one valid open_conflict:
    conflicting(conflict member assertion IDs, conflict_set_id)
else:
    classes := partition active by claim_fingerprint_v1
    if classes has exactly one member:
        selected(
            selected_assertion_id = bytewise-minimum assertion ID,
            supporting_assertion_ids = every other active ID in sorted order,
            selected Knowledge state and canonical payload
        )
    else:
        unresolved_selection(all active assertion IDs in sorted order)
```

Validation has already rejected every malformed open Conflict set, including a
set with fewer than two members and multiple, stale, or partial open sets.
Having no open Conflict set is valid.

The bytewise-minimum assertion ID is only a versioned deterministic carrier
for a semantically homogeneous class. It expresses no source priority or
evidence judgment. All other members remain first-class Supporting assertions.
V1 has no event that hides nonidentical active claims behind a manual winner;
an editor resolves them by explicit retraction, correction, or supersession.

### Projection outcomes

The normative tagged outcomes consumed by pattern v1 are:

```text
selected(selected_assertion_id, supporting_assertion_ids,
         knowledge_state, value-or-no-value)
absent
unresolved_selection(assertion_ids)
conflicting(assertion_ids, conflict_set_id)
```

Every stored projection record additionally carries:

- Snapshot ID and `current_projection_v1` policy ID;
- complete selection key;
- stable outcome reason code;
- Claim fingerprint when selected;
- all active assertion IDs, including nonconflicting active assertions outside
  an open Conflict set;
- projection-record digest;
- per-assertion origin and derivation classification for the selected assertion
  and every Supporting assertion;
- admission, lifecycle, conflict, and dependency references needed to explain
  the result.

Stable v1 reasons include:

| Outcome | Reason |
| --- | --- |
| `selected` | `single_active_assertion` or `corroborating_active_assertions` |
| `absent` | `no_admitted_assertion` or `all_admitted_assertions_retired` |
| `unresolved_selection` | `multiple_active_claim_fingerprints` |
| `conflicting` | `open_declared_conflict` |

Both absence reasons have the same mathematical outcome. Absence carries no
selected assertion ID and proves no Homology value. History APIs may expose
retired or unadmitted IDs separately.

## Model-to-space promotion

Projection never traverses a `model_of` relation at query time. Promotion
creates a new immutable Homology assertion whose subject is the Conceptual
space and whose derivation kind is `model_promotion`.

For `0.0.1`, a promotable Homology claim must come from a Model slot whose
Current projection selects one exact-complete Claim-fingerprint class. The
promoted assertion must pin:

- one active source Model Homology assertion in that selected class, whether it
  is the deterministic carrier or a Supporting assertion;
- the selected source Claim fingerprint and canonical group digest;
- the admitted, active, reviewed `model_of` assertion ID and named equivalence
  level under a Snapshot-pinned relationship-admission policy;
- a versioned invariant-preservation rule accepting that relation kind for
  ordinary Homology;
- the source validation artifacts and versioned promotion-policy reference;
- all source and promotion evidence.

Theory, coefficient system, convention, reducedness, degree, and canonical
group digest are copied exactly. Changing an axis is a separately registered
inference, not promotion. Homotopy equivalence and stronger registered
relations preserve ordinary Homology group isomorphism, but promotion does not
transport chosen bases, cycles, representatives, chain artifacts, geometric
dimension, or model presentation data.

V1 does not promote bounded, conjectural, incomplete-exact, `unknown`,
`not_computed`, or `not_applicable` Model assertions. In particular, failure to
compute on one Model says nothing about whether the Conceptual space has been
computed through another Model.

The pinned source assertion must remain active, and its Model slot must continue
to select the same Claim fingerprint in the same Snapshot. A newly admitted
lower-ID corroborator may change the deterministic carrier without invalidating
the promotion. The `model_of` dependency must remain admitted, active, reviewed,
and valid under the pinned relationship-admission policy; this contract does
not invent selected/unresolved/conflicting outcomes for relationship assertions.
If a source assertion or relationship dependency is later retracted or
superseded, or the source Model projection ceases to select that fingerprint, a
later Snapshot must explicitly retire or correct the promoted target. An
admitted nonretired promotion with an invalid dependency aborts Snapshot
publication; there is no silent cascading withdrawal or mutation.

Multiple models produce distinct promoted assertions. Equal target Claim
fingerprints corroborate. Unequal target fingerprints produce unresolved
selection or an explicitly declared Conceptual-space Conflict. A Model and a
Conceptual-space assertion can never belong to one Conflict set.

An unpromoted Model result remains queryable only in the Model tier. It neither
fills nor conflicts with a Conceptual-space slot.

## Completeness and vanishing assertions

Completeness-region projections use the same admission, activity,
fingerprinting, supersession, conflict, and representative-selection kernel,
with their own fully qualified region key and typed claim payload.

A Conceptual-space exact-coverage or vanishing claim is a new explicit
Completeness assertion. A Model's dimension does not silently become a
Conceptual-space dimension or zero tail. The promoted assertion pins one active
source Model Completeness assertion from its selected Claim-fingerprint class
(or a registered derivation whose output is that assertion), the source class
fingerprint, an admitted active reviewed `model_of` assertion, and the
registered preservation/proof rule. It copies slot-family axes, region shape
and bounds, claim kind, and proof-rule semantics exactly except for the tagged
subject. Representative-carrier changes within the same source fingerprint do
not invalidate it.

The consistency rules in pattern v1 remain mandatory. Selected exact coverage
must contain selected exact complete slots. Selected vanishing may corroborate
selected exact `complete_group` zero or decide a bare-absent slot; it cannot
coexist with selected nonzero, nonexact, or incomplete-exact slot evidence. A
detected inconsistency is reconciled through lifecycle/conflict history or
invalidates the Snapshot; precedence is forbidden.

## Snapshot and materialized read model

A Snapshot pins the exact membership and versions of:

- assertion, evidence, dependency, immutable Conflict-set header, and
  Editorial-event records;
- event, authorization, claim-fingerprint, incompatibility, promotion,
  preservation, and Current-projection policies;
- all canonical encodings and schema versions used in digests.

Later records do not affect an older Snapshot. The canonical builder validates
all references and policies, folds the event ledger, validates promotion and
conflict graphs, and then computes projections. It never consults a mutable
“latest” row.

`declare_conflict` mints the immutable Conflict-set header containing identity,
rule, and declaration evidence. Effective members and open/closed status come
only from the ledger's declare, extend, and resolve effects; the header contains
no competing mutable member or status authority.

The Current projection is a rebuildable read model, never a second source of
truth. For efficient queries, implementations may materialize one row for each
touched `(snapshot, selection key)` plus stable child rows for Supporting
assertions and exact integral primary decompositions. A requested untouched
slot yields derived `absent`; the database need not materialize infinitely many
absence rows.

The materialized form must support the pattern contract without joining the
full history. It must still dereference every selected/supporting assertion,
evidence record, promotion dependency, correction chain, and Conflict set in
the same Snapshot.

The read model also materializes analogous snapshot-bound Completeness
projection rows. Each carries its full slot-family key, claim coordinates,
region kind and endpoints, outcome, selected/Supporting/Conflict IDs, and
proof-rule reference, so interval/ray applicability and documented unions are
evaluated from the projection rather than the Editorial ledger.

Canonical exports sort records and child IDs by specified bytewise keys. Full
rebuilds, repeated rebuilds, and incremental rebuilds from the same Snapshot
input must produce byte-identical projection rows, a matching projection
SHA-256, and the same selected-assertion digest. Physical input row order is an
adversarial test variable.

## Integrity errors versus honest unresolved data

The following are Snapshot-integrity errors and abort publication:

- malformed state payloads, noncanonical values, missing evidence, invalid
  slots, dangling references, or reused IDs with different bytes;
- duplicate total ledger positions, causal cycles, targets that do not exist at
  their event position unless introduced by that same Editorial event,
  a stale/forked global ledger revision, or ambiguous event order;
- duplicate, unauthorized, or scope-invalid Admission decisions, or an
  assertion treated as active without exactly one valid Admission decision;
- self, duplicate, cross-slot, dangling, or cyclic supersession edges;
- an assertion field and Editorial event presented as competing lifecycle
  authorities;
- an open Conflict set with fewer than two members, or multiple, stale, partial,
  same-fingerprint-only, or otherwise invalid open Conflict sets;
- an active promoted assertion with an inactive or missing pinned assertion, an
  invalid relationship dependency, or a source Model/Completeness projection
  that is unresolved, conflicting, or no longer selects the pinned fingerprint;
- a cyclic derivation or promotion dependency graph;
- inconsistent exact primary derivations or selected
  vanishing/exact-nonzero evidence;
- an incomplete exact-coverage region;
- nondeterministic replay or mismatched rebuild digests.

The following are valid mathematical/editorial outcomes, not corruption:

- no admitted active assertion: `absent`;
- one admitted `unknown`, `not_computed`, or `not_applicable` claim: selected
  with that exact Knowledge state;
- multiple active Claim fingerprints without a declared incompatibility:
  `unresolved_selection`;
- a valid declared incompatibility: `conflicting`;
- multiple active assertions with one fingerprint: one deterministic selected
  carrier plus Supporting assertions.

## Evidence returned to an LLM tool

A result explanation names the Snapshot, projection policy and record digest,
selection key, outcome/reason, selected ID, Supporting IDs, Claim fingerprint,
Knowledge state, and evidence references. Unresolved results expose every
active assertion ID and fingerprint; conflicts expose the Conflict-set ID,
exact member IDs, all active IDs, incompatibility rule, and
declaration/resolution history.

For the selected assertion and every Supporting assertion, the explanation
exposes origin and derivation independently. Whenever any participating
assertion is promoted, it additionally exposes the concrete source and target
slots, source Model assertion and Claim fingerprint, `model_of` assertion and
equivalence level, preservation rule, validation/Admission decision, and
evidence. A direct minimum-ID carrier therefore cannot hide a promoted
supporter's Model lineage. Structured fields are authoritative; generated
prose is only a presentation.

Zero query results therefore means no proven matching candidates in that
Snapshot and tier. It does not mean that no matching space exists or that an
unpromoted Model computation was silently searched.

## Mandatory adversarial fixtures

The implementation and release tests must include at least these cases:

1. no history and all-history-retired both project to `absent`, with different
   audit reasons and no selected assertion ID;
2. exact zero remains distinct from absence;
3. a sole admitted assertion in each of the six Knowledge states projects to
   `selected` without conflating state and lifecycle;
4. two equal exact assertions from different sources select the bytewise-smallest
   representative and retain the other as support;
5. equal display values with different Knowledge states, scopes, or
   completeness semantics produce distinct fingerprints and unresolved
   selection;
6. exact beside `unknown` or `not_computed` is unresolved, not a Conflict;
7. unequal exact claims without a Conflict declaration are unresolved and no
   source/reliability priority wins;
8. the same incompatible exact pair under one valid maximal Conflict set is
   `conflicting` with no selected value, even when an active nonconflicting
   `unknown` remains outside the set but appears in the projection record's
   all-active IDs;
9. a third active member in an incompatible Claim class requires extending the
   open set; a second, stale, or partial open set invalidates the Snapshot;
10. a correction chain across Snapshots selects the then-active successor while
    every predecessor remains byte-identical and addressable;
11. forked correction successors with unequal fingerprints are unresolved
    until an explicit lifecycle or conflict event;
12. withdrawing the sole active assertion produces absence and never
    synthesizes `unknown` or revives its predecessor;
13. self, dangling, duplicate, cross-slot, and cyclic supersession attempts are
    rejected;
14. a wrong-degree, coefficient, convention, subject, or reducedness correction
    uses cross-slot correction rather than supersession;
15. equal or inverted wall-clock times and shuffled database rows cannot change
    projection bytes or digests;
16. an identical event retry is idempotent, while identical ID with changed
    bytes, a stale revision, wildcard target, or unauthorized scope fails
    atomically;
17. an unpromoted exact Model match is visible in the Model tier and absent in
    the curated tier;
18. promotion rejects an unreviewed/insufficient `model_of` relation, axis
    change, incomplete source, nonexact state, or unresolved/conflicting Model
    projection;
19. two valid promotions agreeing at the Conceptual-space slot corroborate;
    two disagreeing promotions yield unresolved selection and then conflict
    only after declaration;
20. a promoted assertion agreeing or disagreeing with a direct literature
    assertion follows the same fingerprint/conflict rules;
21. a source correction leaves the old Snapshot unchanged and requires an
    explicit target promotion correction in the later Snapshot;
22. an active promotion whose source or relation dependency is inactive makes
    the later Snapshot invalid;
23. Model dimension alone creates no Conceptual-space zero tail, while an
    explicit evidence-bearing vanishing promotion may do so;
24. complete rebuild and incremental rebuild over the synthetic G9 tier produce
    byte-identical projections and selected-ID digests.
25. admitting a lower-ID same-fingerprint Model corroborator may change the
    selected carrier but does not invalidate a promotion pinned to another
    still-active member of that unchanged selected Claim class.
26. selected vanishing beside selected incomplete-exact zero is reconciled or
    rejected rather than treated as corroborating complete zero.
27. cross-slot correction cannot rekey Model evidence onto a Conceptual space
    or change coefficient/convention axes without the registered promotion or
    inference policy for the fresh assertion.

## Deliberately deferred

V1 does not decide organizational roles, dual-review thresholds, public draft
visibility, automatic admission rules for ticket 08 computations, general
bounded/conjectural incompatibility proofs, cross-coefficient inference,
dynamic promotion, or a database layout. Each later policy must be versioned
and Snapshot-pinned; none may weaken the outcomes or provenance boundary above.
