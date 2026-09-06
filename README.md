# Homology Atlas · Homology DB

A small, source-first reference for the homology and cohomology of spaces.
Browse familiar examples, compare coefficients, and see what cup products
tell you beyond the additive groups.

**[Explore the atlas](https://davearcher18.github.io/homology-db/)** ·
[Textbook trail](https://davearcher18.github.io/homology-db/#textbook) ·
[Contribute](CONTRIBUTING.md) · [Try the QA walkthrough](docs/QA_WITH_GABRIEL.md)

This is a hobby project in active development. Students, mathematicians,
developers, and curious readers are welcome. You do not need to write code—or
review a whole family—to help.

## What can I explore?

- **Families:** spheres, real projective spaces, and complex projective spaces
  for any finite nonnegative dimension parameter.
- **Coefficients:** ℤ and ℚ, followed by 𝔽₂, 𝔽₃, 𝔽₅, 𝔽₇, and 𝔽₁₁ in the
  family workbench. Compare homology and cohomology degree by degree.
- **Rings:** generators, degrees, relations, and expandable cup-product tables.
- **A selected textbook trail:** all 42 retained spaces, sourced introductions,
  three guided comparisons, and clearly labelled coverage gaps.
- **Explanations:** a glossary and expandable inline definitions.
- **Evidence:** citations, derivations, versioned rules, and JSON downloads.

Start with **CP² versus S² ∨ S⁴**: their additive groups agree over a field, but
their cup products differ. Then try **RP² over ℤ, ℚ, and 𝔽₂**.

The original thirteen-space ring core is retained, with HP² and OP² added as a
separate five-field extension. Coverage varies outside the three general
families; 27 retained spaces do not yet have encoded cohomology rings. Ten
infinite finite-type entries have stored homology only through degree 24.

A separate [stable-spectrum preview](https://davearcher18.github.io/homology-db/#spectra)
preserves the existing 49-spectrum collection. It is secondary to the
ordinary-space atlas.

## What should I trust?

**Human mathematical review is pending.** Automated checks and agent review
help catch errors; neither is human mathematical acceptance.

- Missing or unrecorded information never means zero.
- A short display window is different from limited mathematical knowledge.
- A review applies only to its stated rule version, parameters, coefficients,
  degrees, and components.
- Sources and review history stay attached to the results.

Found something questionable? Use **Review this result** on a family page or
**Correct or improve** on an individual space. A small, precise correction is
very useful. See [how mathematical review works](docs/reviews/FAMILY_REVIEW_GUIDE.md).

## Run it locally

To browse, download or clone the repository and open
[`dist/atlas.html`](dist/atlas.html). The atlas is a self-contained static file:
no account, server, package install, or network is needed to read it. External
sources and GitHub feedback links need a connection.

For the Python tools, use **Python 3.11 or newer**, from the repository root.
No third-party Python packages are needed for the core demo and tests.

```sh
git clone https://github.com/DaveArcher18/homology-db.git
cd homology-db
python3 -m homology_db chromatic demo
python3 -m unittest discover -s tests
```

The full suite takes a few minutes. Some optional external-consumer checks may
be skipped when their tools are unavailable.

See [development and build instructions](docs/DEVELOPMENT.md) for rebuilding the
atlas, running browser checks, and preserving release provenance. There is no
`pip install` step or published package to install.

## Help improve it

Good first contributions include:

- explaining where a page or control was confusing;
- fixing a typo or improving a source locator;
- reviewing one example over one coefficient ring;
- adding a focused regression test;
- proposing a sourced example that is missing.

[Open an issue](https://github.com/DaveArcher18/homology-db/issues/new/choose)
or read [CONTRIBUTING.md](CONTRIBUTING.md). Please be kind, patient, and specific.
This is maintained as a side project, so response times vary.

## Find your way around

| Path | What lives here |
| --- | --- |
| `homology_db/` | Mathematical records, family rules, validation, and Python tools |
| `static_atlas/` | Static page templates, JavaScript, and CSS |
| `corpus/` | Pinned data and provenance |
| `tests/` | Python regression tests |
| `scripts/` | Export, validation, and browser checks |
| `dist/atlas.html` | The built, offline atlas published to GitHub Pages |
| `docs/` | Contributor references, source research, and review guidance |

The [documentation index](docs/README.md) separates current guides from
historical design notes. Internal planning files are not prerequisites for
contributing.

## License and acknowledgements

Original code and accompanying original documentation are **[MIT licensed](LICENSE)**.
Fork, modify, and use them commercially; keep the copyright and license notice.
See [licensing and third-party attribution](docs/LICENSING.md) for material with
separate terms, including imported datasets and upstream reference documents.

The project is inspired by the LMFDB's reference-oriented approach. Mathematical
sources are credited with individual records. Retained LMFDB reference documents
and the stable-spectrum data have their own recorded provenance and licensing;
they are not silently relicensed by this project.
