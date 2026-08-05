# Mod-2 Steenrod-module interoperability for cw49

This note fixes the primary-source boundary used by the `steenrod-cw49-v1`
review candidate. Imported data remains unreviewed until a named mathematical
reviewer accepts the exact candidate hash.

## Canonical mathematical boundary

For a homogeneous ordered basis of mod-2 cohomology, record each generator
operation `Sq^(2^k)` as a sparse mod-2 sum of basis elements in degree shifted
by `2^k`. `Sq^0` is the implicit identity. The generator actions determine
composite squares through the Adem relations when they are consistent.

An empty exact image is a known zero. An absent action is unknown unless an
exact completeness assertion covers that basis/power slot. This is critical
because all three external formats treat omitted actions as zero. Exporters
must reject incomplete finite modules rather than strengthen the data.

For unstable modules, `Sq^i(x)=0` when `i>|x|`; stable spectrum cohomology has
no such instability condition. Cup-square checks require algebra data and are
outside this module-only contract.

## Pinned consumers

### Bruner Ext 1.9.5

The official module format is documented at
<https://rrb.wayne.edu/cohom/modfmt.html> and distributed in
<https://rrb.wayne.edu/papers/ext.1.9.5.tar.gz>. A definition contains the
dimension, a nondecreasing degree list, and rows `g r k g1 ... gk` for every
nonzero `Sq^r(g)`. Bruner therefore requires the exporter to derive and emit
all composite nonzero squares, not only generator powers, and then pass
`newconsistency`.

### SpectralSequences/sseq

The contract is `ext/MODULE-SPEC.md` at commit
`99ddfb6b1cfc2dc1c24fd11fe7c0b16e8f318534` of
<https://github.com/SpectralSequences/sseq>. Finite modules use JSON with
`p: 2`, `type: "finite dimensional module"`, an ordered `gens` mapping, and
nonzero action strings such as `Sq2 x0 = x2 + x2b`. Only generator powers are
required. This repository assumes Dan's word “sseq” names this implementation;
the review packet calls out that assumption for confirmation.

### Wayne Lin SSeqCpp

The custom-complex contract and parser are pinned to commit
`23d12c973db2b294a6c00c15bd106e70b0af3fa6` of
<https://github.com/WayneLin92/SSeqCpp>. `Adams.json` records ordered cell
degrees, a derived minimal-generator degree multiset, and nonzero generator
operations. Repeated degrees use `[degree,index]`; target arrays may name a
sum. The operation power is inferred from the source/target degree difference.

## Pinned cw49 source

The index at <https://waynelin92.github.io/ss/kervaire-49.html>, source commit
`b8b48c89abe8287710cc23b9efa1490388dc132a`, lists 49 stable spectra: ring
spectra `S0` and `tmf`, plus 47 modules. The author-owned archive is Zenodo
record <https://zenodo.org/records/14875701>, DOI
`10.5281/zenodo.14875701`, version `v126.3.cw49`, CC-BY-4.0. Its
`programs.rar` has byte length 4,180,266 and MD5
`554d12d6dc6aa61b94a7b9fe85c73f04`, with independently checked SHA-256
`dca24f896dd3eb296e6cbe32e2fcdd5777056a026674454c6a0ac08b9e1fe73e`;
`source code.zip` has byte length
5,051,993, MD5 `66ce3684e92676604f8368191e35d5b3`, and SHA-256
`dd784541626f4d693c35f3ca84d4a67e83758ac463aabe58ab6c9cc92be22a15`.
Its ZIP comment identifies SSeqCpp revision
`087753ebaa0b351f565d18279442cf05c9ab3c50`; the embedded software license is
Apache-2.0. This is distinct from the Zenodo deposit's CC-BY-4.0 data license;
`programs.rar` does not itself contain a license file.

`programs/Adams.json` defines `S0` and 40 of the listed finite modules. Six
stunted real-projective spectra and `Fphi` are SSeqCpp built-ins. `tmf` is an
infinite Steenrod-profile module rather than a finite basis module.

The four older `free:true` records are `Csigmasq`, `Ctheta4`, `Ctheta5`, and
`C2sigma`. At historical commit
`fdf7e372da28ff1ac59794807d5468b6c7cf12e1`, `main_export_mod` bypasses the
general operation parser for these records and calls `ExportFreeModAdamsE2`
using only `cells_gen`. The normalized finite modules therefore use those
listed degrees as their basis and record every in-support generator action as
an exact zero. This is a decode of the archived optimization, not an
independent mathematical verification.

The authoritative normalization is extracted from that pinned Zenodo
`programs.rar`. Its embedded `programs/Adams.json` is 24,455 bytes with
SHA-256 `5a4adf1561832a762b7d3a504f8f2603793855733f549d17d5a9668f6c7935bc`;
the checked-in normalized cw49 subset has SHA-256
`53e7c69f0642a04d2c990c23638ab0ae5f72899c30d05faa2655cd3ac55d2576`.
The historical `scripts/Adams.json` remains a cross-check only. Its SHA-256 is
`86c27d67e8c726c83138cc4134c563cffdd38f8e00d1891bff6fcb3a5bce6c44`;
it swaps the within-degree basis ordinals in `C2_C2`, `Ceta_Ceta`, `Cnu_Cnu`,
and `Csigma_Csigma`. Those four imports follow the archive's ordered basis,
not the historical fallback.

The generated per-spectrum JavaScript files are Adams-chart output, not raw
Steenrod-module input, and `secondary` fields seed Adams differential data
rather than primary Steenrod operations. Neither is promoted into the
canonical Steenrod action table.

## Consumer verification boundary

The interoperability checks validate encodings, not the imported mathematics.
All 48 finite Bruner exports pass the compiled Ext 1.9.5 `newconsistency`
checker. Representative `sseq` exports, including repeated-degree and
sum-valued actions, pass the pinned commit's real module construction in both
Adem and Milnor bases; the profile-shaped `tmf` export also passes its selected
Milnor parser. Exact SSeqCpp fragments for `S0`, archive-ordered `C2_C2`, and a
repeated-degree sum fixture pass the arm64 `Adams` executable from the pinned
Zenodo programs archive. The profile-shaped `tmf` record is intentionally a
built-in adapter rather than an `Adams.json` fragment; `Adams cellstructure
tmf 20` also succeeds with that archived executable. Large modules remain covered by deterministic
canonical validation rather than by computing their full Ext resolution as a
unit test.
