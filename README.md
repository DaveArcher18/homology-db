# Homology DB

Homology DB is a planning-stage project for a searchable, citable, provenance-rich atlas of algebraic-topological objects and computations, inspired by the LMFDB.

Its two confirmed downstream consumers are future spectral-sequence computation engines and LLM tools that retrieve useful examples from partial homological descriptions. The purpose is to reduce routine lookup and reconstruction work so algebraic topologists can spend more time on mathematical judgment and discovery.

The long-term direction is an AI-powered research harness or operating system for stable homotopy theorists. The intended sequence is Homology DB first, Serre spectral-sequence support second, and Adams spectral-sequence support after that. Querying known spectral sequences with LLMs and forcing new computations are later research programs, not current implementation scope.

The project intends to reimplement the relevant mathematical capabilities under a coherent architecture. Existing systems are references, attributed sources, datasets, and differential-test oracles rather than intended permanent runtime foundations. Licensing is deliberately deferred and is not a current architecture decision.

The current recommendation is to begin with a deliberately narrow vertical slice:

- spaces and their finite simplicial or CW models;
- ordinary integral homology in explicit degrees;
- relationships between spaces, models, and constructions;
- reproducible computation records with sources, software versions, and reliability states;
- an object page, browse/search experience, downloads, and a versioned JSON API.

This is not yet an application scaffold. The first milestone is agreement on the mathematical identity model and the pilot corpus.

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

## Working position

Build an independent prototype that adopts LMFDB's information architecture and editorial discipline. Do not fork the LMFDB application until there is a decision to pursue an official LMFDB section and the LMFDB developers have been consulted. This keeps the first experiment small and avoids prematurely inheriting its Sage/Flask deployment stack and runtime object model.
