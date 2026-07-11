Type: research
Status: resolved
Claimed by: /root
Claimed at: 2026-07-11T11:28:33Z
Resolved at: 2026-07-11T11:51:32Z
Blocked by:

# Survey scalable finite-model corpora

## Question

What artifact shapes, actual counts, identifiers, metadata, attribution, update mechanisms, reconstructibility, torsion coverage, and independent validation data are available from Sage, HAP, simpcomp, and other plausible sources for a large `0.0.1` model corpus?

## Answer

Pin the Stellar v6 Zenodo archive as the leading bulk-source candidate and use
live polyDB as a structured cross-check of the same Lutz lineage, not as a
second independent corpus. Stellar contains hundreds of thousands of explicit
triangulations with a DOI, file checksums, and homology/type sidecars. simpcomp
adds 648 engine-native but reconstructible named/transitive artifacts. Sage is
a deterministic generator and external homology oracle, not a stored corpus.
HAP supplies only a handful of literal ordinary-space triangulations plus
useful recipes and regular-CW semantics; it is a differential oracle, not a
source of scale. Regina is a large future generalized-triangulation source but
does not enter `0.0.1` until the model boundary admits it or a validated
conversion.

The finite-simplicial floor is feasible. The 400-model regular-CW floor remains
conditional on ticket 04: a disjoint selection of triangulations can be
exported as reconstructible face/incidence artifacts only if that representation
is accepted as a counted Model. A source artifact counts once, even when
multiple normalized representations exist. Cross-source Lutz duplicates must
be identified and retain all provenance without inflating counts.

Every selected source record keeps its upstream pin, original bytes/hash,
record locator, attribution, decoder/transformation version, normalized
bytes/hash, and validation runs. Upstream homology remains a separately
attributed assertion; owned parse-to-chain, `d^2 = 0`, and integral homology are
mandatory before a model counts.

## Evidence

- [Finite-model corpus survey](../../../docs/research/finite-model-corpus-survey.md)
  records direct source/file/API counts, immutable pins, artifact shapes,
  torsion coverage, update paths, attribution facts, source overlap, validation
  roles, and explicit unknowns.
- Three independent source audits covered Sage, HAP, and simpcomp/other corpora;
  the integrated report was then checked source-by-source. The Sage review
  returned no corrections; the simpcomp/other review corrected the Stellar pin
  to v6 and reconfirmed all polyDB/simpcomp counts.
- `git diff --check` passes for the integrated research checkpoint.
