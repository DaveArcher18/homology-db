# Homology pattern query contract v1

Status: normative design contract for Homology DB `0.0.1`.

This contract defines structured example lookup. It consumes a snapshot-bound
Current projection; it does not choose assertions, promote Model results to
Conceptual spaces, parse natural language, or infer mathematics from missing
data.

## Normalized request

The normalized form is a nonempty conjunction of `slot_clause` nodes and
require-only `exact_signature_clause` nodes. It contains no implicit slot
defaults, nested Boolean expressions, similarity score, or relevance ranking.

```json
{
  "schema_version": "homology-db.example-query/1",
  "snapshot_id": "snapshot:0.0.1",
  "subject_tier": "curated",
  "include_unresolved": false,
  "pattern": {
    "operator": "all",
    "clauses": [
      {
        "node_kind": "slot_clause",
        "id": "h1_has_2_torsion",
        "polarity": "require",
        "slot": {
          "subject": {
            "binding": "candidate",
            "kind": "conceptual_space"
          },
          "theory_id": "ordinary_homology",
          "coefficient_system_id": "Z",
          "convention_id": "augmented_singular_v1",
          "reduced": false,
          "degree": 1
        },
        "predicate": {
          "kind": "has_primary_torsion",
          "prime": 2
        }
      }
    ]
  },
  "order": {"key": "public_id", "direction": "asc"},
  "page": {"limit": 50, "cursor": null}
}
```

Normalization expands all accepted request sugar into this form, sorts clauses
by caller-supplied unique `id`, uses canonical JSON key ordering, resolves the
snapshot, and returns the normalized request. The semantic query SHA-256 covers
the schema version, snapshot, tier, unresolved policy, pattern, and order but
excludes the `page` object. Clause IDs are part of the hash so explanations can
preserve caller correlation. A cursor is bound to the snapshot, semantic query
hash, and stable order; it cannot hash itself.

`subject_tier` is exactly one of:

- `curated`: reviewed Conceptual spaces only; this is the request default but
  is always explicit after normalization;
- `model`: released Models, including unidentified or unpromoted Models.

The tiers never form an implicit union. A Model assertion cannot fill a
Conceptual-space Homology slot during lookup; promotion must already exist as
an evidence-bearing assertion in the snapshot.

Every `slot_clause` has one Candidate-bound slot selector containing subject
kind, theory, coefficient system, Homology convention, reducedness, and integer
degree. It instantiates to one concrete fully qualified Homology slot per
candidate. A negative degree is valid only when the named convention admits it.

## Clause structure

Only `require` and `forbid` are ordinary clause polarities. “Exact,” “unknown,” and
torsion describe predicates or evidence; “partial” describes a pattern that
mentions only some slots. Omitted slots impose no condition and are never read
as zero, unknown, or absent.

The v1 mathematical predicate union is:

| Predicate | Meaning and type restriction |
|---|---|
| `group_equals` | Equality with a canonical complete group: an invariant-factor finitely generated abelian group over `Z`, or a vector-space dimension over `F_p` |
| `free_rank_compare` | Compare the free rank of an exact integral group; this is the integral Betti number and is never inferred from field dimensions |
| `field_dimension_compare` | Compare the exact vector-space dimension over the slot's prime field; never infer it from integral data in the read path |
| `has_primary_torsion` | The exact integral group has a nonempty primary part for prime `p` |
| `primary_summand` | The exact integral group contains `Z/(p^e)` with exact or minimum multiplicity at that exact exponent |
| `primary_decomposition_equals` | Equality of the complete finite map `e -> multiplicity` for one prime, ignoring free rank and other primes |
| `primary_exponent_equals` | The nontrivial `p`-primary subgroup has exponent `p^e`; request field `exponent_e` means `e`, not its total order |

The v1 snapshot-metadata predicate union is:

| Predicate | Meaning |
|---|---|
| `selected_knowledge_state_is` | The Current projection selected an atomic assertion with exactly one of `exact`, `bounded`, `conjectural`, `unknown`, `not_computed`, or `not_applicable` |
| `projection_outcome_is` | The Current projection outcome is exactly `selected`, `absent`, `unresolved_selection`, or `conflicting` |

Snapshot-metadata predicates are require-only in v1. Their forbidden complement
would be easy to misread—for example, forbidding explicit `unknown` would also
accept bare absence—and is not needed by G6.

The primary predicates are integral-only and require a prime. `Z/(p^e)` means a
cyclic primary direct summand at exactly exponent `e`; it is not divisibility of
the torsion order, p-rank, or total p-adic valuation. Multiplicity must be
positive. An empty exact p-primary decomposition means no p-torsion and is
provable only from an exact complete group with a verified complete primary
derivation.

Normalized predicate payloads use these shapes:

```jsonc
{"kind":"free_rank_compare","op":"eq|gte|lte","value":0}
{"kind":"field_dimension_compare","op":"eq|gte|lte","value":0}
{"kind":"group_equals","value":{"schema_version":"homology-db.fgag/1","free_rank":0,"torsion_invariant_factors":[]}}
{"kind":"primary_summand","prime":2,"exponent_e":3,
 "multiplicity":{"op":"eq|gte","value":2}}
{"kind":"primary_decomposition_equals","prime":2,
 "summands":[{"exponent_e":1,"multiplicity":1},
             {"exponent_e":3,"multiplicity":2}]}
{"kind":"primary_exponent_equals","prime":2,"exponent_e":3}
{"kind":"selected_knowledge_state_is","state":"unknown"}
{"kind":"projection_outcome_is","outcome":"conflicting"}
```

Primary-decomposition summands are sorted by strictly increasing `exponent_e`
and have unique positive exponents and multiplicities. Multiplicity zero is
expressed by forbidding a summand or by an exact empty primary decomposition.
For an exact complete group with trivial p-primary part,
`primary_exponent_equals` is `proven_false`, not undefined.

`group_equals` and signature entries carry one versioned canonical value:

```jsonc
{"schema_version":"homology-db.fgag/1","free_rank":1,
 "torsion_invariant_factors":["2","12"]}
{"schema_version":"homology-db.prime-vector-space/1","prime":3,
 "dimension":4}
```

A prime-vector-space value's embedded prime must equal the prime named by the
slot's coefficient system.

Torsion invariant factors are canonical positive decimal strings so values
beyond JSON's exact numeric range remain stable. V1 request integers use these
finite schema limits: prime `2..2147483647`, `exponent_e` `1..65535`, and rank,
dimension, or multiplicity `0..2147483647` subject to the stricter positive
multiplicity rule. Validation cost and integer precision are therefore bounded.

## Current projection input

For one instantiated slot, pattern evaluation consumes one tagged Current
projection outcome:

```text
selected(selected_assertion_id, supporting_assertion_ids,
         knowledge_state, value-or-no-value)
absent
unresolved_selection(assertion_ids)
conflicting(assertion_ids, conflict_set_id)
```

It may additionally dereference:

- the selected canonical group value;
- for integral torsion predicates, a verified-complete primary derivation and
  profile with its derivation ID;
- applicable snapshot-bound Completeness-region projections and their evidence
  or conflict references.

Ticket 06 defines how this projection is selected. Pattern evaluation never
looks through an unresolved selection or conflict to manufacture a weaker
mathematical consensus, even if all members appear to agree on the requested
predicate.

## Evidence trits

A mathematical predicate at a slot has one evidence trit:

- `proven_true`;
- `proven_false`;
- `unresolved` with a stable reason code and evidence references.

V1 has two registered mathematical proof sources:

1. a selected exact complete canonical group;
2. an applicable published vanishing/completeness assertion with a versioned
   rule that entails the exact zero group at the requested slot or region.

Bounded and conjectural assertions do not decide v1 mathematical predicates.
They remain queryable as knowledge states and may support future versioned
proof rules. Explicit `unknown`, `not_computed`, `not_applicable`, bare absence,
unresolved selection, conflict, or insufficient coverage yield `unresolved` for
mathematical predicates.

A Completeness-region projection has the same selected, unresolved-selection,
or conflicting discipline as a Homology slot. V1 regions use one fully
qualified slot family and inclusive `closed_interval(min,max)`,
`lower_ray(max)`, or `upper_ray(min)` shapes within the named convention's
degree domain. `exact_coverage` is permitted only on a finite closed interval
and requires every covered slot to project to selected exact complete data.
`vanishing` is permitted on intervals or rays, and every selected vanishing
claim names a registered `proof_rule_id`. Selected regions may be unioned only
when their slot-family and claim coordinates agree, using this documented
interval/ray coverage algebra. Outside `[a,b]` is covered by
`lower_ray(a-1)` and `upper_ray(b+1)` after intersecting the convention domain.

A completeness assertion is evidence; absence is not. An exact-coverage region
containing an absent, nonexact, unresolved-selection, conflicting, or
incomplete slot; an inconsistent primary derivation; an unsupported state; or
simultaneously selected exact nonzero group and applicable vanishing claim is a
snapshot-integrity error. A detected but unresolved disagreement is represented
by an explicit conflict and is a hard unresolved fence. The evaluator never
chooses precedence or infers zero.

A selected vanishing rule derives the canonical exact zero group and, for an
integral slot, a verified empty primary profile. It may corroborate a selected
exact zero or decide a bare-absent slot. If the slot instead selects `unknown`,
`not_computed`, `not_applicable`, `bounded`, or `conjectural`, snapshot building
must reconcile them into supersession, unresolved selection, or conflict; if
both remain independently selected, the snapshot has an integrity error.

Snapshot-metadata predicates are exact two-valued comparisons. In particular,
`selected_knowledge_state_is: unknown` is true only for a selected explicit
`unknown` assertion and false for `not_computed`, `absent`, insufficient coverage,
`unresolved_selection`, `conflicting`, and every other selected state.

Metadata comparisons emit `proven_true` or `proven_false` in the same predicate
trit field used by mathematical clauses; they never emit `unresolved`.

## Polarity and whole-pattern outcome

The predicate trit and clause polarity produce a clause verdict:

| Predicate trit | `require` | `forbid` |
|---|---|---|
| `proven_true` | `satisfied` | `violated` |
| `proven_false` | `violated` | `satisfied` |
| `unresolved` | `unresolved` | `unresolved` |

`forbid` is evidence-backed negation, never a SQL anti-join over missing child
rows.

The conjunction classifies each candidate:

| Clause verdicts | Candidate classification |
|---|---|
| every clause `satisfied` | `proven_match` |
| at least one `violated` | `proven_nonmatch` |
| no `violated` clause and at least one `unresolved` | `unresolved_candidate` |

A candidate with one violated and one unresolved clause is a proven nonmatch.

`include_unresolved` changes result presentation only:

- `false`: return proven matches and report unresolved counts;
- `true`: return proven matches and unresolved candidates in structurally
  separate arrays;
- never mix, jointly rank, or call unresolved candidates examples that match.

## Exact signatures and regional completeness

An `exact_signature_clause` is the one normalized macro exception to the
single-slot shape. It is require-only in v1 and denotes the exact `Z`-coefficient
Homology signature over contiguous integer degrees. It contains one
Candidate-bound slot family, exactly one explicit group—including explicit
zero—for every degree in the range, and one mandatory outside policy:

```json
{
  "node_kind": "exact_signature_clause",
  "id": "integral_signature_0_2",
  "polarity": "require",
  "predicate": {
    "kind": "exact_signature",
    "slot_family": {
      "subject": {"binding": "candidate", "kind": "conceptual_space"},
      "theory_id": "ordinary_homology",
      "coefficient_system_id": "Z",
      "convention_id": "augmented_singular_v1",
      "reduced": false
    },
    "degree_range": {"min": 0, "max": 2},
    "groups": [
      {"degree": 0, "value": {"schema_version": "homology-db.fgag/1", "free_rank": 1, "torsion_invariant_factors": []}},
      {"degree": 1, "value": {"schema_version": "homology-db.fgag/1", "free_rank": 0, "torsion_invariant_factors": []}},
      {"degree": 2, "value": {"schema_version": "homology-db.fgag/1", "free_rank": 0, "torsion_invariant_factors": ["2"]}}
    ],
    "outside_range": "ignore"
  }
}
```

- `ignore`: compare only the listed range and warn that other degrees were not
  constrained;
- `require_vanish_under_published_completeness`: also require evidence proving
  vanishing in every degree outside the range in the named convention's domain.

A known nonzero group outside the range proves the latter predicate false.
Complete cited vanishing proves it true. Missing or partial regional evidence
is unresolved. A finite table, a Model dimension, or absent rows do not by
themselves establish vanishing; a published Completeness region must make that
claim. The explanation expands stable subchecks for every degree and the
outside region using IDs `<macro-id>/degree/<n>` and `<macro-id>/outside`, and
cites group and completeness evidence separately. The macro's subcheck trits
are conjoined before its single require polarity is applied.

## Validation

Validation is all-or-nothing. Invalid requests return a versioned error with a
stable code, JSON path, and clause ID; no clause is silently dropped and no
partial result is returned.

```json
{
  "schema_version": "homology-db.error/1",
  "error": {
    "code": "invalid_query",
    "issues": [
      {
        "path": "/pattern/clauses/0/predicate/prime",
        "clause_id": "h1_has_2_torsion",
        "code": "not_prime",
        "message": "prime must be prime"
      }
    ]
  }
}
```

`normalized_query`, match arrays, and partial data are absent from this error
response. A detected snapshot-integrity failure aborts the entire query with
stable top-level code `snapshot_integrity_error` and also fails release
verification; the service never skips the affected candidate.

V1 request-complexity limits are part of the schema:

| Quantity | Limit |
|---|---:|
| UTF-8 request body | 1 MiB |
| normalized pattern nodes | 64 |
| clause or macro ID | 128 ASCII characters |
| degree integer | signed 32-bit, then restricted by convention |
| exact-signature degree span | 256 degrees |
| primary-decomposition summands | 1,024 |
| invariant factors in one FGAG value | 1,024 |
| decimal digits in one invariant factor | 4,096 |
| canonical FGAG payload | 256 KiB |
| page limit | 500; default 50 |

Limit failures use stable issue codes such as `request_too_large`,
`too_many_pattern_nodes`, `signature_span_too_large`, or
`group_value_too_large` before expensive factoring, compilation, or lookup.

V1 rejects at least:

- unsupported schema or snapshot, empty clause list, duplicate clause ID, or
  cursor/query/snapshot mismatch;
- unknown theory, coefficient system, or convention; tier/subject-kind
  mismatch; convention-invalid degree;
- p-primary predicates on a field slot, field dimension over `Z`, free rank
  over a field, nonprime `p`, nonpositive exponent/multiplicity, or a
  noncanonical group encoding;
- forbidden snapshot-metadata predicates or a forbidden exact-signature macro;
- incomplete/noncontiguous exact signatures or a missing outside policy;
- directly contradictory normalized nodes, including require and forbid of one
  atom in the same fully qualified slot, two unequal required exact groups in
  one slot, two unequal required exact p-primary profiles for one slot and
  prime, two distinct required projection outcomes for one slot, or required
  outside vanishing together with required nonzero data in that outside region;
- page limits outside the documented bounds.

The validator need not solve every arithmetic implication. Unrecognized but
valid-looking contradictions may evaluate to zero matches; clauses are never
silently simplified or discarded.

No arbitrary Boolean trees, wildcard/unbounded degree inference, cross-degree
arithmetic, UCT inference, bound-theorem proving, cross-tier union, similarity
score, or natural-language interpretation exists in v1. Clients can issue and
combine multiple snapshot-bound queries explicitly.

## Evidence envelope

Every response contains `release.version`, `release.snapshot_id`,
`release.manifest_sha256`, the normalized request, semantic query hash,
`semantics.query_semantics_id`, subject tier, and unresolved policy. Every
`evidence_ref` dereferences inside that snapshot to a citation, immutable
artifact, Computation run, or review/correction record.

Coverage identifies the complete candidate universe and reports counts that
sum:

- eligible subjects examined;
- proven matches;
- unresolved candidates;
- proven nonmatches;
- unresolved reasons and warnings.

Zero results means zero proven matches in this snapshot and tier, never global
nonexistence.

Coverage totals describe the whole eligible universe, not the current page.
They are computed or retrieved once per `(snapshot_id, semantic_query_sha256)`
and reused unchanged across cursor pages so first-page latency does not require
reclassification on every page.

Use separate `proven_matches` and `unresolved_candidates` arrays. Each result
contains its subject identity, overall classification, and one explanation per
clause with:

- clause ID, predicate trit, clause verdict, and stable reason code;
- for ordinary clauses, the complete concrete Homology slot;
- for signature macros, every deterministic observation/subcheck and its
  concrete slot or Completeness region;
- projection outcome and selected knowledge state when one exists;
- selected and supporting assertion IDs;
- general evidence, Homology, completeness, Conflict-set, and proof-rule
  references;
- a canonical value only when value-bearing;
- Model references and warnings.

Optional prose may summarize these fields, but structured reason codes and
references are authoritative. Absence has no assertion ID. Conflict has member
assertion IDs and a Conflict-set reference but no selected assertion.

Pagination uses one logical stream of returned subjects in the normalized
`public_id` order. One `limit` applies across that stream; the response splits
the page into the two structural arrays, and each item carries its zero-based
`page_ordinal` so the page order can be reconstructed without mixing the
semantic result classes. The opaque next cursor carries the last public ID and
binds the semantic query hash, snapshot, and order. The response page block
gives `limit`, per-array counts on this page, and `next_cursor`.

## Mandatory adversarial fixtures

The implementation test matrix includes:

1. exact zero, bare absence, explicit unknown, and not-computed at the same slot
   coordinates on distinct subjects or snapshots;
2. `Z/4` versus `Z/2 ⊕ Z/2`;
3. `Z/2 ⊕ Z/4` and `Z/2 ⊕ Z/8`, with explicit expected results for exact
   exponent multiplicity, p-rank, and maximum exponent;
4. `Z/6`, whose 2- and 3-primary parts share one invariant factor;
5. a Moore-space coefficient example showing field dimension is not
   same-degree integral torsion evidence;
6. reduced versus unreduced `H_0(S^0)`;
7. conflicting torsion/torsion-free assertions, for which require and forbid
   are both unresolved and retain the Conflict-set reference;
8. unresolved selection containing exact and unknown assertions, which does
   not match explicit unknown;
9. bounded/conjectural assertions that do not decide v1 mathematical clauses;
10. exact signatures with explicit zero, omitted slots, and both outside
    policies with and without sufficient completeness evidence;
11. deliberately corrupt/incomplete primary rows that fail snapshot validation;
12. an unpromoted matching Model whose putative Conceptual space does not
    inherit the match;
13. conjunctions yielding all three candidate classifications, including a
    violated-plus-unresolved proven nonmatch;
14. nonprime and coefficient-incompatible predicates that fail validation;
15. cursor pages whose public-ID stream contains both proven and unresolved
    results, preserving page ordinals, semantic query hash, and universe-wide
    coverage totals.
