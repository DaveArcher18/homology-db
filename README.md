# Homology DB

Homology DB is a searchable, citable, provenance-rich atlas of Conceptual
spaces and computations, inspired by the LMFDB. It is under active
construction; a local preview is available now.

## Browse the atlas

Open [`dist/atlas.html`](dist/atlas.html) directly in a browser. It is a single
self-contained, offline file: search all 60 spaces, follow stable Conceptual-space links,
switch coefficient systems and reduced/unreduced choices, filter the corpus, and
open provenance or raw JSON in review mode.

The atlas is a human-facing view of `local-preview-60`, not the held
`named-atlas-review-v1` release candidate. Its visible “local preview” status is
intentional. Rebuild it deterministically with:

```bash
python3 scripts/export_static_atlas.py --snapshot current --output dist/atlas.html
```

The [static atlas read-model note](docs/static-atlas-read-model.md) records the
schema mapping, measured database and HTML sizes, and validation boundaries.

## Try it now

No installation or network access is required beyond Python 3.10 or newer:

```bash
python3 -m homology_db demo
```

The command builds a disposable SQLite snapshot of 60 common manifolds and
walks through the Klein bottle, `RP^4` over `F_2`, a 5-primary example search,
and the evidence record behind an answer. It finishes in under a second on the
development machine.

For a guided Codex session, say:

> Read `docs/TEST_DRIVE.md`, run the Homology DB test drive, and guide me
> through three questions of my choice. Show the evidence behind each answer.

External mathematical review is currently **on hold**. Do not send the
60-subject preview to Gabriel Ong, Dan Isaksen, or another reviewer as the
proposed atlas. The [retained reviewer handoff](docs/EXTERNAL_REVIEW.md)
documents the frozen regression fixture, but it will not become active again
until `named-atlas-review-v1` passes its schema, named-corpus, provenance, and
adversarial QA gates.

The four public tools also accept stable JSON for agent use. See
[the local test-drive guide](docs/TEST_DRIVE.md) for copy-paste examples,
limitations, and the automated checks. This preview is not the qualified
`0.0.1` release; its purpose is to make the interface and mathematics tangible
while the full source-qualified corpus is built.

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
13. [Next steps](docs/NEXT_STEPS.md)
14. [Prepared database-connected review run](docs/REVIEW_AGENT_RUN.md)
15. [External reviewer handoff — on hold](docs/EXTERNAL_REVIEW.md)
16. [Append-only review process](docs/REVIEW_PROCESS.md)
17. [Common-example source review](docs/research/common-examples-review.md)
18. [ICERM/LMFDB knowl and usability review](docs/research/icerm-lmfdb-knowl-review.md)
19. [Topology-agent question benchmark](docs/research/topology-agent-question-benchmark.md)
20. [Atlas schema prototype contract](docs/contracts/atlas-schema-prototype-v1.md)
21. [Four-minute development-preview Loom plan](docs/LOOM_WALKTHROUGH.md)
22. [Open-this-first Loom recording workspace](LOOM_START_HERE.md)

## Working position

Build an independent prototype that adopts LMFDB's information architecture and editorial discipline. Do not fork the LMFDB application until there is a decision to pursue an official LMFDB section and the LMFDB developers have been consulted. This keeps the first experiment small and avoids prematurely inheriting its Sage/Flask deployment stack and runtime type model.
