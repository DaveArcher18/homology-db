# Candidate data-source landscape

This is a discovery inventory, not permission to ingest. Every source needs a version, license, attribution, and redistribution review before data enters a release.

## LMFDB

- [Source repository](https://github.com/LMFDB/lmfdb)
- [Developer guide](https://github.com/LMFDB/lmfdb/blob/main/Development.md)
- [Style guide](https://github.com/LMFDB/lmfdb/blob/main/StyleGuide.md)
- [PostgreSQL FAQ](https://github.com/LMFDB/lmfdb/blob/main/Postgres_FAQ.md)
- [Public API](https://www.lmfdb.org/api/)
- [Project paper](https://arxiv.org/abs/1511.04289)

Relevant lessons:

- The web application uses Python, Flask blueprints, Jinja templates, SageMath, PostgreSQL, and the psycodict abstraction.
- Search tables use typed columns and indexes, while large non-search fields may live in extra tables.
- The current public API is intentionally basic, capped and URL-query based; a new project should version its API and design bulk snapshots separately.
- The upstream application is GPLv2+.
- LMFDB asks prospective contributors to consult its developers before adding top-level object families or committing to labels.

Use: product/editorial reference now; possible application upstream later.

## SageMath topology and homology

- [Topology reference](https://doc.sagemath.org/html/en/reference/topology/index.html)
- [Chain complexes and homology](https://doc.sagemath.org/html/en/reference/homology/index.html)

The current documentation covers finite simplicial, delta, cubical, and filtered complexes; simplicial sets; chain complexes; homology/cohomology; algebraic topological models; and induced maps on homology.

Use: preferred first computation adapter and source of small generated examples. Treat Sage's catalog names as external identifiers, not automatically as Homology DB identities.

## HAP for GAP

- [HAP manual](https://gap-packages.github.io/hap/doc/chap0_mj.html)
- [Regular CW-complex chapter](https://gap-packages.github.io/hap/doc/chap30_mj.html)

HAP is a homological algebra and algebraic topology package. Its documented capabilities include regular CW complexes, cellular chain complexes, fundamental groups, group cohomology, covering spaces, knots, and related computations.

Use: independent validation backend and possible import/export format investigation. Check exact package and example-data licenses before redistribution.

## simpcomp for GAP

- [Project](https://simpcomp-team.github.io/simpcomp/)
- [Library and I/O](https://simpcomp-team.github.io/simpcomp/doc/chap13.html)

simpcomp includes a library of triangulated manifolds and pseudomanifolds and computes properties including face data, automorphism groups, (co)homology, and intersection forms. Its library documentation describes external naming conventions and import/export mechanisms.

Use: strongest candidate for a pilot corpus with multiple finite simplicial models. Do not import the global library until its data licenses, upstream attributions, stable identifiers, and canonicalization behavior have been audited.

## KnotInfo and LinkInfo

- [About and acknowledgments](https://knotinfo.org/homelinks/about.html)
- [Downloads](https://knotinfo.math.indiana.edu/homelinks/database_download.php)

KnotInfo is a mature example of searchable objects, many invariants, references per invariant, contributor credit, unknown values, and downloadable data.

Use: product and editorial comparison; not part of the recommended first corpus. It demonstrates why values, references, conventions, and uncertainty must be modeled together.

## Stable homotopy groups

- [Isaksen–Wang–Xu computation](https://arxiv.org/abs/2001.04247)

This is an important later test domain because results are interconnected, computational, prime-specific, and may include unresolved extensions. It should not be the first object family unless the project has a stable-homotopy editor and an agreed notation/provenance model.

## Source qualification checklist

Before importing any dataset, record:

1. upstream owner and canonical URL;
2. exact release, commit, or retrieval date;
3. code license and data license separately;
4. redistribution, modification, and attribution terms;
5. published references and required citation text;
6. external labels and whether they are stable;
7. file format and convention documentation;
8. completeness boundary;
9. known errors, corrections, and update process;
10. contributor credits at dataset and record level;
11. checksums of original artifacts;
12. importer, normalization, and validation versions.
