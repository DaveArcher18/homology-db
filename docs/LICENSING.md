# Licensing and attribution

## Original project material

The original Homology DB code and accompanying original documentation are
licensed under the [MIT License](../LICENSE). You may fork, modify, redistribute,
and use them commercially, including in closed-source projects, provided you
retain the copyright and license notice. Contributions back are welcome but
not required.

This license does not replace the separate licenses on third-party documents,
imported datasets, or other material identified below or by its own notices.

## Material with separate provenance

- **Pinned LMFDB reference documents:** retained under their upstream GPLv2-or-later
  notice. See [the upstream license](upstream/lmfdb/LICENSE) and
  [pinned revision and attribution](upstream/lmfdb/UPSTREAM.md). They are planning
  references, not a statement that this project is the LMFDB application.
- **Stable-spectrum import:** the source record in
  [the corpus](../corpus/steenrod-cw49-v1/corpus.json) identifies the Zenodo
  deposit, its recorded CC-BY-4.0 dataset license, normalization, and hashes.
  The related software has separately recorded licensing. See the
  [interoperability/source note](research/steenrod-module-interoperability-2026-08-05.md).
- **Computed cohomology rings:** the manifest in
  [the corpus](../corpus/computed-rings-v1/manifest.json) records the producing
  repository, its commit, and its two licenses separately: the software is
  GPL-3.0-or-later (OSCAR is), while the generated ring records it publishes are
  CC0-1.0. The records imported here are the CC0 ones.
- **Checked-in triangulations:** the facet lists under
  [the corpus](../corpus/computed-rings-v1/triangulations/) are output of the named
  SageMath constructors, retained as mathematical data so each imported ring is
  bound to an exact model. Sage itself is GPL-2.0-or-later and none of its source
  is included here; no license is asserted over the facet lists. They are checked
  in rather than referenced by recipe because `SurfaceOfGenus` does not reproduce
  its vertex labelling between processes, so a recipe alone would not identify the
  model. This follows the existing precedent of
  [the Poincare sphere artifact](../corpus/chromatic-v1/poincare-sphere-facets.json),
  and like that precedent it is a recorded fact rather than a settled rights
  determination.
- **Mathematical references:** citations identify the evidence for a result;
  they do not grant permission to redistribute a cited book or paper.

This attribution guide is not a completed repository-wide
rights audit. Keep upstream notices intact and check new code, data, or copied
text individually before adding it.
