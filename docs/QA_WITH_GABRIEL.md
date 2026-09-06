# David + Gabriel: first QA session

Status: live and ready for human QA, 2026-09-06. Source 63116513; release 5bf19f8.
All 211 tests completed successfully (3 optional skips), with independent
mathematical, workflow and integration reviews. Deterministic rebuild and four
Chrome browser suites pass both locally and on the live site. Codex in-app checks
were unavailable while the Mac was locked; those are not claimed as passed.
This checklist invites human QA; it is not a record of acceptance.

Start with the [textbook map](https://davearcher18.github.io/homology-db/#textbook).
The selected map covers all 42 retained spaces; 27 still have no encoded
cohomology ring and remain explicitly labelled. It is not an exhaustive textbook
inventory. The original 13-space ring core is preserved, with HP²/OP² added as a
separate sourced five-field extension.

Publication: [Pages run 34039872067](https://github.com/DaveArcher18/homology-db/actions/runs/34039872067)
succeeded. The live 5,386,015-byte file matches SHA-256
80f2adaa588657c8cf33c8450f8ae7ad037d3bdb46671fdbaf0239de0f89d974 exactly.

Allow about 15 minutes. David can concentrate on reading and navigation; Gabriel
can concentrate on the stated mathematical examples. Either can flag either kind
of problem. No need to audit the whole database in one sitting.

## 1. Can you find what you need?

Start at the [workbench](https://davearcher18.github.io/homology-db/). Find the
textbook map, search for a projective plane, and return to its result. Try one
example on a phone or narrow window. Tell us where you had to guess what to do.

## 2. Does the comparison teach the intended distinction?

Follow the guided comparison of CP² with S² ∨ S⁴. Over Q, both have one-dimensional
cohomology in degrees 0, 2 and 4, but the degree-two generator squares nontrivially
in CP² and trivially in the wedge. Can you find both the claim and its source
without digging through technical records?

## 3. Can you distinguish coefficients and theories?

Open RP². Over Z, inspect H₁ = Z/2 and H¹ = 0, then H₂ = 0 and H² = Z/2.
Compare with F₂. Switch reduced homology on: degree-zero homology changes, but
the ordinary cohomology ring and its unit must not change. Are the labels clear?

## 4. Check the new projective-plane collection

Inspect HP² and OP² over Q and F₂. The new records assert k[u]/(u³), with |u|=4
and |u|=8 respectively. Check the nonzero additive degrees, u², the vanishing of
u³, and the cited Hatcher passages (p. 222 and §4.B p. 427). These field results
are deductions from the sourced integral rings, not new machine computations.

## 5. Is an honest gap actually obvious?

Open a Moore or lens space without recorded cohomology. The site must say
“not recorded,” not suggest its cohomology is zero. In a bounded homology entry,
distinguish the visible degree window from the stated mathematical coverage.

## 6. Try the review handoff

For RP², prepare a review covering only n=2, F₂, degrees 0–2, cohomology and
multiplication. Check the copied packet or prefilled GitHub form: exact rule
version/hash, parameters, coefficients, degrees, components and sources must
travel with it. Do not choose whole-rule acceptance unless you actually reviewed
the whole rule. Copying/opening the form does not submit it.

For legacy individual records such as HP²/OP², use their existing correction
form and include the downloaded space JSON/snapshot and coefficient; a family
review is not the correct target for those records.

## What to send back

One short note per finding is enough:

    Page link:
    Mathematical issue or usability issue:
    Coefficient / dimension / degree / rule or record identity:
    What I expected:
    What I saw:
    Evidence or suggested correction:
    Exact scope I checked (if giving a mathematical verdict):

“Looks good” is useful product feedback, but will not be silently converted into
mathematical acceptance. Named mathematical reviews are published only after
maintainer validation, with their actual scope and history preserved.
