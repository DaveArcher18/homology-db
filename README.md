# Homology DB

Homology DB is a searchable, citable, provenance-rich atlas of Conceptual
spaces and computations, inspired by the LMFDB. It is under active
construction; the current public atlas is a focused chromatic gateway built
from 42 named CW spaces.

## Browse the atlas

**Live atlas:** [davearcher18.github.io/homology-db](https://davearcher18.github.io/homology-db/)

Open [`dist/atlas.html`](dist/atlas.html) directly in a browser. It is a single
self-contained, offline file: search all 42 spaces, follow stable
Conceptual-space links, switch coefficient systems and reduced/unreduced
choices, filter the corpus, and open CW models, citations, computation sketches,
recorded runs, or raw JSON in review mode.

The corpus includes Moore spaces with prime-power torsion, projective and lens
spaces, low-rank compact Lie groups, Schubert spaces, classifying spaces,
`BU(2)`, and the universal rank-two complex Thom space. Ten infinite
finite-type models are materialized through degree 24 and never presented as
vanishing above that bound. This is ordinary Homology: the atlas explains the
chromatic connection but does not claim to compute chromatic type or Morava
K-theory.

Rebuild the current `chromatic-gateway-42` Snapshot deterministically with:

```bash
python3 scripts/export_static_atlas.py --snapshot current --output dist/atlas.html
```

The [static atlas read-model note](docs/static-atlas-read-model.md) records the
schema mapping, measured database and HTML sizes, and validation boundaries.
Pushes of the checked-in artifact to `main` are deployed by
[`deploy-atlas-pages.yml`](.github/workflows/deploy-atlas-pages.yml).
Every space and family has a correction/computation-feedback link, and the
toolbar links to a structured request-a-space form. Browsing is account-free;
submitting those GitHub Issue Forms requires a GitHub account.

## Try it now

No installation or network access is required beyond Python 3.10 or newer:

```bash
python3 -m homology_db chromatic demo
```

The command builds a disposable SQLite snapshot and walks through a Moore
space, a 3-primary lens space, a Hopf-attached projective plane, and the model
and citation behind an answer. It finishes in under a second on the development
machine. The unprefixed `python3 -m homology_db ...` commands remain the frozen
60-space regression fixture so its 2026-07-12 adversarial audit stays replayable.

For a guided Codex session, say:

> Read `docs/TEST_DRIVE.md`, run the Homology DB test drive, and guide me
> through three questions of my choice. Show the evidence behind each answer.

External mathematical review is currently **on hold**. The
[retained reviewer handoff](docs/EXTERNAL_REVIEW.md) documents the frozen
60-space regression fixture; it is not a review claim for this newer corpus.

The four public tools also accept stable JSON for agent use. See
[the local test-drive guide](docs/TEST_DRIVE.md) for copy-paste examples,
limitations, and the automated checks. The current atlas is still a development
corpus, not the qualified `0.0.1` release. It makes model identity, parameterized
torsion computations, bounded coverage, and source provenance tangible while
the full release process remains in progress.

Its two confirmed downstream consumers are future spectral-sequence computation engines and LLM tools that retrieve useful examples from partial homological descriptions. The purpose is to reduce routine lookup and reconstruction work so algebraic topologists can spend more time on mathematical judgment and discovery.

The long-term direction is an AI-powered research harness or operating system for stable homotopy theorists. The intended sequence is Homology DB first, Serre spectral-sequence support second, and Adams spectral-sequence support after that. Querying known spectral sequences with LLMs and forcing new computations are later research programs, not current implementation scope.

The project intends to reimplement the relevant mathematical capabilities under a coherent architecture. Existing systems are references, attributed sources, datasets, and differential-test oracles rather than intended permanent runtime foundations. Licensing is deliberately deferred and is not a current architecture decision.

The current recommendation is to begin with a deliberately narrow vertical slice:

- spaces and their finite simplicial or CW models;
- ordinary integral homology in explicit degrees;
- relationships between spaces, models, and constructions;
- reproducible computation records with sources, software versions, and reliability states;
- a Conceptual-space page, browse/search experience, downloads, and a versioned JSON API.

The identity model and pilot corpus selection contract are now fixed. The
current implementation frontier is owned chain computation, followed by
measured persistence/query design and the release pipeline.

## Start here

1. [Project brief](docs/planning/00-project-brief.md)
2. [Domain model](docs/planning/01-domain-model.md)
3. [First implementation tasks](docs/planning/03-first-tasks.md)
4. [Long-term vision and scope boundary](docs/planning/04-long-term-vision.md)
5. [Compute-platform strategy](docs/planning/05-compute-platform-strategy.md)
6. [Working agreements and decision state](docs/planning/06-working-agreements.md)
7. [Reimplementation doctrine](docs/planning/07-reimplementation-doctrine.md)
8. [Roadmap](docs/planning/02-roadmap.md)
9. [Candidate data sources](docs/research/data-source-landscape.md)
10. [Spectral-sequence prior art](docs/research/spectral-sequence-prior-art.md)
11. [Pinned LMFDB documentation](docs/upstream/lmfdb/UPSTREAM.md)
12. [Local test drive](docs/TEST_DRIVE.md)
13. [Chromatic gateway 42 corpus contract](docs/contracts/chromatic-gateway-42.md)
14. [Next steps](docs/NEXT_STEPS.md)
15. [Prepared database-connected review run](docs/REVIEW_AGENT_RUN.md)
16. [External reviewer handoff — on hold](docs/EXTERNAL_REVIEW.md)
17. [Append-only review process](docs/REVIEW_PROCESS.md)
18. [Common-example source review](docs/research/common-examples-review.md)
19. [ICERM/LMFDB knowl and usability review](docs/research/icerm-lmfdb-knowl-review.md)
20. [Topology-agent question benchmark](docs/research/topology-agent-question-benchmark.md)
21. [Atlas schema prototype contract](docs/contracts/atlas-schema-prototype-v1.md)
22. [Four-minute development-preview Loom plan](docs/LOOM_WALKTHROUGH.md)
23. [Open-this-first Loom recording workspace](LOOM_START_HERE.md)

## Working position

Build an independent prototype that adopts LMFDB's information architecture and editorial discipline. Do not fork the LMFDB application until there is a decision to pursue an official LMFDB section and the LMFDB developers have been consulted. This keeps the first experiment small and avoids prematurely inheriting its Sage/Flask deployment stack and runtime type model.
