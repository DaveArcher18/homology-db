Type: prototype
Status: resolved
Claimed by: /root
Claimed at: 2026-07-11T11:03:01Z
Resolved at: 2026-07-11T11:22:27Z
Blocked by:

# Prototype the smallest honest constellation

## Question

Can one neutral executable fixture represent the empty space, point, sphere family instances, two models of `S²`, `RP²`, the Hopf-fibration context, an unidentified model, and corrected/conflicting assertions without hiding conventions or collapsing absent data into zero—and which domain distinctions does that force?

## Answer

Yes. One small neutral constellation can represent the cases, but only if it
does **not** collapse them into one nullable “space” record. The executable
fixture is retained at commit `0ebf896` on the throwaway
`prototype/honest-constellation` branch under
`prototypes/honest_constellation/`; it is a design probe, not the physical schema.

The fixture forces these distinctions for the later interchange contract:

1. **Identity is layered.** Conceptual spaces, concrete finite models, immutable
   model artifacts, and parameterized family membership are separate records.
   Two reviewed `model_of` assertions connect different simplicial and CW
   models to `S²`; the unattached model has no `model_of` assertion and appears
   only when the model tier is requested.
2. **A homology slot is fully qualified.** Its key contains tagged subject kind
   and ID, theory, coefficient system, a versioned homology convention,
   reduced/unreduced choice, and an integer degree. The convention is
   dereferenceable and declares augmented grading, including
   `H̃_{-1}(∅; Z) = Z`; the empty model correspondingly declares dimension
   `-1`. `S⁰` separately exercises disconnected and reduced degree-zero data.
3. **Claims and query resolution are different axes.** An atomic homology
   assertion states knowledge state, derivation, evidence, and completeness.
   Exact zero carries the canonical group `{free_rank: 0,
   torsion_invariant_factors: []}`. `not_computed` is an evidenced assertion;
   absence is a derived lookup outcome with no value and no assertion ID.
   The fixture does not invent an `unknown` claim for these elementary finite
   cases merely to fill a state bucket.
4. **History is append-only and slot-safe.** A correction appends the standard
   `H_1(RP²; Z) = Z/2` assertion, a same-slot supersession edge, and an editorial
   event while leaving the deliberately bad historical zero assertion
   unchanged and addressable. Cross-slot, forward, duplicate, and self
   supersession are rejected by the prototype boundary.
5. **Conflict is explicit, not guessed.** An open conflict set names two
   incompatible retained exact assertions on the unattached model. It produces
   a current projection with no selected value and preserved assertion/evidence
   references. Merely placing `unknown` or `not_computed` beside exact data does
   not manufacture a mathematical conflict; it produces unresolved selection.
6. **Negative queries use evidence trits.** Required or forbidden prime-torsion
   constraints return `proven_true`, `proven_false`, or `unresolved`. Exact
   complete zero can prove a forbidden condition; absent, not-computed,
   unresolved-selection, and conflict cannot. Conflict results retain their
   conflict-set reference.
7. **Map identity and fibration context are distinct.** The Hopf projection is
   identity-only map metadata with explicit domain, codomain, and unspecified
   basedness. One evidence-bearing n-ary fibration-context assertion binds that
   map to total space `S³`, base `S²`, and typical fiber type `S¹`. Its
   capability flag explicitly says that computational map data and a chosen
   fiber inclusion are not present; general map support remains out of scope.

This resolves the record distinctions without choosing SQL tables, a service
language, Sage integration, production schemas, snapshot persistence, or a
general theory of maps and fibrations.

## Evidence

- `python3 prototypes/honest_constellation/app.py --script` executes the
  correction and conflict transitions and passes all 22 semantic observations.
- `python3 prototypes/honest_constellation/app.py` opens the one-screen
  interactive state viewer.
