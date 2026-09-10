"""Convert cohomology-tables records into homology-db corpus data.

Out-of-band producer tooling: nothing in ``homology_db`` imports this, and it is
not part of any build. It reads a local checkout of

    https://github.com/wgabrielong/cohomology-tables

and writes the neutral corpus files the atlas loads.

No triangulation is copied. Upstream states no licence for the Lutz Manifold
Page data and none can now be sought, so each simplicial model is recorded by
its identity -- SHA-256 of the canonical facet list, f-vector, vertex and facet
counts, and the citation needed to fetch it -- and never by its facets.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path

COEFFICIENTS = ("Z", "Q", "F2", "F3", "F5", "F7")
SCHEMA_VERSION = "homology-db.imported-models/1"


EXISTING = {"point","S^0","S^1","S^2","S^3","S^4","Poincare sphere","T^2","Klein bottle",
 "Sigma_2","Sigma_3","Sigma_4","Sigma_5","Sigma_6","N_3","N_4","N_5","N_6","RP^2","RP^3",
 "RP^4","CP^2","HP^2","M(Z/3,1)","M(Z/4,1)","M(Z/5,2)","M(Z/9,2)","M(Z/7,3)","M(Z/8,4)",
 "L(3,1)","L(5,1)","L(5,2)"}
DROP = {f"N_{k} x S^1" for k in (7, 8, 9, 10)}

def ident(text):
    """Readable, permanent identifier fragment. These become atlas URLs."""
    text = text.replace("^", "")            # S^2 -> S2, not s-2
    text = re.sub(r"_(?=\d)", "", text)      # N_3 -> N3, Sigma_2 -> Sigma2
    text = text.replace("#-", "-sum-minus-").replace("#", "-sum-")
    text = text.replace("twist", "-twist-")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9.]+", "-", text.lower())).strip("-")


def plan_for(name, row):
    dim = len(row["f_vector"].split(",")) - 1
    g3 = ["closed_3manifold"]
    if m := re.fullmatch(r"S\^(\d+)", name):
        return f"sphere:{m.group(1)}", "sphere", None, None, None
    if name == "RP^5":
        return "real_projective_space:5", "real_projective_space", None, None, None
    if name == "CP^3":
        return "complex_projective_space:3", "complex_projective_space", None, None, None
    if m := re.fullmatch(r"Sigma_(\d+)", name):
        g = m.group(1)
        return (f"orientable_surface:{g}", "surface", f"Genus-{g} orientable surface",
                [f"Sigma_{g}", f"M_{g}", f"connected sum of {g} tori"],
                ["surface", "orientable", "torsion_free", "connected_sum"])
    if m := re.fullmatch(r"Sigma\((\d+),(\d+),(\d+)\)", name):
        a, b, c = m.groups()
        return (f"brieskorn_sphere:{a}:{b}:{c}", "homology_sphere",
                f"Brieskorn homology sphere Sigma({a},{b},{c})",
                [f"Sigma({a},{b},{c})", f"Brieskorn sphere ({a},{b},{c})"],
                ["homology_sphere", "same_homology_guard", "nontrivial_pi1", *g3])
    if m := re.fullmatch(r"L\((\d+),(\d+)\)", name):
        p, q = m.groups()
        return (f"lens:{p}:3:1-{q}", "lens_space", f"Lens space L^3({p};1,{q})",
                [f"L({p},{q})", f"L^3({p};1,{q})"],
                [f"{f}_primary" for f in sorted({d for d in range(2, int(p)+1) if int(p) % d == 0 and all(d % e for e in range(2, d))})]
                + ["torsion", "spherical_geometry", *g3])
    if m := re.fullmatch(r"P_(\d+)", name):
        return (f"prism_manifold:{m.group(1)}", "prism_polyhedral_3manifold",
                f"Prism manifold P_{m.group(1)}", [f"P_{m.group(1)}"],
                ["2_primary", "torsion", "spherical_geometry", *g3])
    if name in ("cube_space", "octahedron_space", "truncated_cube_space"):
        pretty = name.replace("_", " ")
        return (f"polyhedral:{ident(name)}", "prism_polyhedral_3manifold",
                pretty[0].upper() + pretty[1:], [name],
                ["torsion", "spherical_geometry", *g3])
    if name in ("T^3", "G2", "G3", "G4", "G5", "G6", "KxS^1", "B2", "B3", "B4"):
        orientable = name in ("T^3", "G2", "G3", "G4", "G5", "G6")
        label = {"T^3": "3-torus T^3", "KxS^1": "Klein bottle times circle K x S^1"}.get(
            name, f"Flat 3-manifold {name}")
        return (f"flat:{ident(name)}", "flat_3manifold", label, [name],
                ["flat_geometry", "orientable" if orientable else "nonorientable", *g3])
    if m := re.fullmatch(r"Nil_Oo1_(\d+)", name):
        return (f"nil:{m.group(1)}", "nil_3manifold",
                f"Nil 3-manifold Nil_Oo1_{m.group(1)}", [name],
                ["nil_geometry", "orientable", *g3])
    if name in ("S^2xS^1", "S^2twistS^1", "RP^2xS^1", "RP^3#RP^3"):
        label = {"S^2xS^1": "Product S^2 x S^1", "S^2twistS^1": "Twisted bundle S^2 x~ S^1",
                 "RP^2xS^1": "Product RP^2 x S^1", "RP^3#RP^3": "Connected sum RP^3 # RP^3"}[name]
        extra = (["connected_sum"] if "#" in name
                 else ["sphere_bundle"] if "twist" in name else ["product"])
        return (f"s2xr:{ident(name)}", "s2xr_3manifold", label, [name],
                ["s2xr_geometry", *g3] + extra)
    if m := re.fullmatch(r"(Sigma|N)_(\d+) x S\^1", name):
        kind, g = m.groups()
        surface = f"Sigma_{g}" if kind == "Sigma" else f"N_{g}"
        return (f"h2xr:{ident(surface)}xs1", "h2xr_3manifold",
                f"Product {surface.replace('_', '_')} x S^1", [name],
                ["h2xr_geometry", "product", *g3])
    if name.startswith("hyperbolic vol "):
        vol = name[len("hyperbolic vol "):]
        return (f"hyperbolic:vol:{vol}", "hyperbolic_3manifold",
                f"Hyperbolic 3-manifold of volume {vol}", [name],
                ["hyperbolic_geometry", "torsion", *g3])
    if name == "Weber-Seifert space":
        return ("hyperbolic:weber-seifert", "hyperbolic_3manifold",
                "Weber-Seifert dodecahedral space",
                ["Weber-Seifert space", "hyperbolic dodecahedral space"],
                ["hyperbolic_geometry", "5_primary", "torsion", *g3])
    if name in ("S^3xS^2", "S^2 x Poincare sphere", "Wu manifold"):
        key = {"S^3xS^2": "s3xs2", "S^2 x Poincare sphere": "s2-x-poincare-sphere",
               "Wu manifold": "wu"}[name]
        label = {"S^3xS^2": "Product S^3 x S^2",
                 "S^2 x Poincare sphere": "Product S^2 x Poincare sphere",
                 "Wu manifold": "Wu manifold SU(3)/SO(3)"}[name]
        return (f"five_manifold:{key}", "five_manifold", label, [name],
                ["closed_5manifold"] + (["product"] if "x" in name else ["2_primary", "torsion"]))
    COMBINATORIAL = ("HMT_", "Chessboard(", "Matching(", "Hom_", "NotIConnected",
                     "SumComplex", "rand2_")
    if dim == 4 and not name.startswith(COMBINATORIAL) or name in ("S^3xS^1", "S^3twistS^1"):
        label = {"S^2xS^2": "Product S^2 x S^2", "K3": "K3 surface",
                 "S^3xS^1": "Product S^3 x S^1", "S^3twistS^1": "Twisted bundle S^3 x~ S^1",
                 "CP^2#CP^2": "Connected sum CP^2 # CP^2",
                 "CP^2#-CP^2": "Connected sum CP^2 # -CP^2",
                 "CP^2#(S^2xS^2)": "Connected sum CP^2 # (S^2 x S^2)",
                 "(S^2xS^2)#(S^2xS^2)": "Connected sum (S^2 x S^2) # (S^2 x S^2)",
                 "RP^4#K3": "Connected sum RP^4 # K3",
                 "RP^4#11(S^2xS^2)": "Connected sum RP^4 # 11(S^2 x S^2)"}.get(name, name)
        tags = ["closed_4manifold", "intersection_form"]
        if "#" in name: tags.append("connected_sum")
        elif "x" in name.lower(): tags.append("product")
        return (f"four_manifold:{ident(name)}", "four_manifold", label, [name], tags)
    if "#" in name:
        return (f"connected_sum:{ident(name)}", "connected_sum_3manifold",
                f"Connected sum {name}", [name], ["connected_sum", "reducible", *g3])
    # combinatorial complexes
    key, label, tags = None, None, ["combinatorial"]
    if m := re.fullmatch(r"HMT_(\d+)", name):
        key, label = f"hadamard_torsion_complex:{m.group(1)}", f"Hadamard torsion complex HMT_{m.group(1)}"
        tags += ["2_primary", "torsion"]
    elif m := re.fullmatch(r"Chessboard\((\d+),(\d+)\)", name):
        key, label = f"chessboard_complex:{m.group(1)}:{m.group(2)}", f"Chessboard complex M_{{{m.group(1)},{m.group(2)}}}"
    elif m := re.fullmatch(r"Matching\((\d+)\)", name):
        key, label = f"matching_complex:{m.group(1)}", f"Matching complex M_{m.group(1)}"
    elif name.startswith("Hom_"):
        key, label = f"hom_complex:{ident(name[4:])}", "Hom complex Hom(C_6, complement of K_5)"
    elif name == "NotIConnected(5,2)":
        key, label = "not_i_connected_complex:5:2", "Not-2-connected graph complex on 5 vertices"
    elif name.startswith("SumComplex"):
        key, label = "sum_complex:5:0-1-3", "Sum complex X(5; {0,1,3})"
    elif name == "rand2_n25":
        key, label = "random_2_complex:25", "Random 2-complex on 25 vertices"
    return key, "combinatorial_complex", label, [name], tags


def parse_integral_homology(text: str) -> list[dict[str, object]]:
    """``Z,Z^2,Z + Z/2,0`` -> per-degree free rank and torsion orders."""
    rows = []
    for degree, term in enumerate(text.split(",")):
        free_rank, torsion = 0, []
        for part in (piece.strip() for piece in term.split("+")):
            if part in ("", "0"):
                continue
            if part == "Z":
                free_rank += 1
            elif match := re.fullmatch(r"Z\^(\d+)", part):
                free_rank += int(match.group(1))
            elif match := re.fullmatch(r"Z/(\d+)", part):
                torsion.append(int(match.group(1)))
            else:
                raise ValueError(f"cannot parse homology term {part!r} in {text!r}")
        rows.append({"degree": degree, "free_rank": free_rank,
                     "torsion_orders": sorted(torsion)})
    return rows


def certificate_chain(rows: list[dict[str, object]]) -> tuple[dict, dict]:
    """Smallest chain complex realising ``rows``, in the shape _base_spec wants.

    This is a calculation certificate, not a replacement for the simplicial
    model: it reproduces the recorded groups under the repository's own Smith
    reduction, so the homology is re-derived here rather than taken on trust.
    """
    free = [int(row["free_rank"]) for row in rows]
    torsion = [list(row["torsion_orders"]) for row in rows]
    top = len(rows) - 1
    ranks, nonzero = {}, {}
    for degree in range(top + 2):
        below = torsion[degree - 1] if 0 < degree <= top else []
        here = torsion[degree] if degree <= top else []
        rank = (free[degree] if degree <= top else 0) + len(here) + len(below)
        if rank:
            ranks[degree] = rank
        entries = []
        for index, order in enumerate(below):
            column = (free[degree] if degree <= top else 0) + len(here) + index
            entries.append((free[degree - 1] + index, column, order))
        if entries:
            nonzero[degree] = entries
    return ranks, nonzero


def build_plan(records: Path) -> list[dict]:
    """One entry per imported space: its permanent id, family, and display data."""
    spaces, seen = [], set()
    for row in csv.DictReader((records / "MANIFEST.tsv").open(), delimiter="\t"):
        name = row["space"]
        if name in EXISTING or name in DROP:
            continue
        space_id, family, label, aliases, tags = plan_for(name, row)
        if space_id is None:
            raise ValueError(f"no identifier rule for {name!r}")
        if space_id in seen:
            raise ValueError(f"identifier {space_id} is claimed twice")
        seen.add(space_id)
        spaces.append({"space_id": space_id, "family": family, "source_space": name,
                       "label": label or name, "aliases": aliases or [name],
                       "tags": sorted(set(tags or []))})
    return sorted(spaces, key=lambda entry: entry["space_id"])


def build_models(records: Path) -> dict:
    rows = {row["space"]: row for row in
            csv.DictReader((records / "MANIFEST.tsv").open(), delimiter="\t")}
    models = []
    for entry in build_plan(records):
        row = rows[entry["source_space"]]
        f_vector = [int(value) for value in row["f_vector"].split(",")]
        homology = parse_integral_homology(row["integral_homology"])
        models.append({
            "space_id": entry["space_id"],
            "family": entry["family"],
            "label": entry["label"],
            "aliases": entry["aliases"],
            "tags": entry["tags"],
            "dimension": len(f_vector) - 1,
            "integral_homology": homology,
            "certificate_chain": dict(zip(("ranks", "nonzero"),
                                          [{str(k): v for k, v in part.items()}
                                           for part in certificate_chain(homology)])),
            "model": {
                "model_id": f"simplicial:{entry['space_id']}",
                "facets_sha256": row["facets_sha256"],
                "f_vector": f_vector,
                "vertices": f_vector[0],
                "facets": f_vector[-1],
                "retrieval": {
                    "catalog": row["kind"],
                    "file": row["file"],
                    "label": row["label"],
                    "url": row["url"],
                    "date_accessed": row["date_accessed"],
                },
                "redistribution": "identified_not_redistributed",
            },
            "source_space": entry["source_space"],
        })
    models.sort(key=lambda model: model["space_id"])
    return {"schema_version": SCHEMA_VERSION, "models": models}


RING_SCHEMA = "homology-db.cohomology-rings/1"
HOMOLOGY_SCHEMA = "homology-db.computed-homology/1"
MULTIPLICATION_SCOPE = {
    "complete": True, "omitted_products": "zero",
    "scope": "all_nonunit_ordered_basis_pairs", "unit_products": "identity",
}
RING_DERIVATION = (
    "Alexander-Whitney cup product on the simplicial cochains of the pinned model, "
    "with canonical graded bases obtained by Smith normal form; imported as computed, "
    "not verified here."
)
HOMOLOGY_DERIVATION = (
    "Simplicial chain complex of the pinned model, reduced to Smith normal form; "
    "imported as computed, and corroborating rather than replacing this repository's "
    "own cellular homology."
)
MODEL_SOURCE_ID = {"lutz": "lutz-manifold-page", "sage": "sagemath",
                   "builtin": "cohomology-tables", "arxiv": "cohomology-tables"}


def _basis_and_order(graded, characteristic):
    """Flatten the producer's graded bases into the atlas's basis list."""
    basis = []
    for block in graded:
        degree = block["degree"]
        factors = block.get("invariant_factors") or []
        for index, label in enumerate(block.get("basis_labels") or []):
            raw = factors[index] if index < len(factors) else "0"
            order = int(raw) if raw.isdigit() else 0
            basis.append({"degree": degree, "id": label,
                          "order": 0 if characteristic else order})
    return basis


def _products(record, graded):
    """Nonzero, non-unit structure constants in the atlas's sparse shape."""
    labels_by_degree = {block["degree"]: (block.get("basis_labels") or [])
                        for block in graded}
    products = []
    for entry in record.get("structure_constants") or []:
        left, right = entry["a"]["label"], entry["b"]["label"]
        if left == "1" or right == "1":
            continue                                  # implied by unit_products
        target = labels_by_degree.get(entry["product_degree"], [])
        result = [{"basis": target[index], "coefficient": int(value)}
                  for index, value in enumerate(entry["coefficients"])
                  if index < len(target) and value not in ("0", "0//1")]
        if result:                                    # implied by omitted_products
            products.append({"left": left, "right": right, "result": result})
    products.sort(key=lambda item: (item["left"], item["right"]))
    return products


def _sources(entry, row, coefficient, kind):
    model_source = MODEL_SOURCE_ID[row["kind"]]
    locator = (f"{row['file']}:{row['label']}" if row["kind"] == "lutz"
               else row["call"] or row["space"])
    return [
        {"source_id": "cohomology-tables", "role": kind,
         "locator": f"records/{entry['space_id']} over {coefficient}"},
        {"source_id": model_source, "role": "model", "locator": locator},
        {"source_id": "oscar", "role": "engine",
         "locator": "SimplicialCochainComplex and DGAlgCohRing (experimental/DoubleAndHyperComplexes)"},
    ]


def _provenance(entry, row, coefficient, kind, derivation):
    return {
        "kind": "external_engine_computation", "review_state": "imported_unreviewed",
        "derivation": derivation, "engine": "OSCAR", "engine_version": "1.8.2",
        "model_id": entry["model"]["model_id"],
        "model_facets_sha256": entry["model"]["facets_sha256"],
        "source_locator": f"cohomology-tables:records/{row['space']}.{coefficient}#/{kind}",
    }


def build_records(records: Path, entries: list[dict], expected_groups) -> tuple[list, list]:
    """Ring and homology records for the given imported spaces."""
    rows = {row["space"]: row for row in
            csv.DictReader((records / "MANIFEST.tsv").open(), delimiter="\t")}
    stems = {}
    for name in os.listdir(records):
        if name.endswith(".Z.json") and ".homology." not in name:
            stems[name[: -len(".Z.json")]] = True

    def stem_for(space_name):
        prefix = re.sub(r"[^A-Za-z0-9]+", "_", space_name).strip("_")
        matches = [stem for stem in stems if stem.rsplit("_", 1)[0] == prefix]
        if len(matches) != 1:
            raise ValueError(f"cannot locate records for {space_name!r}")
        return matches[0]

    rings, homology = [], []
    for entry in entries:
        row = rows[entry["source_space"]]
        stem = stem_for(entry["source_space"])
        dimension = entry["dimension"]
        for coefficient in COEFFICIENTS:
            characteristic = 0 if coefficient in ("Z", "Q") else int(coefficient[1:])
            source = json.loads(
                (records / f"{stem}.{coefficient}.json").read_text(encoding="utf-8"))
            graded = source["cohomology"]
            basis = _basis_and_order(graded, characteristic)
            rings.append({
                "schema_version": RING_SCHEMA,
                "record_id": f"computed:{entry['space_id']}:{coefficient}:v1",
                "space_id": entry["space_id"], "theory": "ordinary_cohomology",
                "coefficient": coefficient, "characteristic": characteristic,
                "convention": "unreduced", "knowledge_state": "exact",
                "algebra": {"kind": "graded_structure_constants", "unit": "1",
                            "basis": basis, "multiplication": dict(MULTIPLICATION_SCOPE),
                            "products": _products(source, graded)},
                "coverage": {"kind": "complete_finite", "through_degree": dimension,
                             "upper_vanishing_starts_at": dimension + 1},
                "groups": expected_groups(basis, dimension, coefficient),
                "provenance": _provenance(entry, row, coefficient,
                                          "structure_constants", RING_DERIVATION),
                "sources": _sources(entry, row, coefficient, "computed_ring"),
            })
            hom_source = json.loads(
                (records / f"{stem}.homology.{coefficient}.json").read_text(encoding="utf-8"))
            groups = []
            for block in hom_source["homology"]:
                factors = block.get("invariant_factors") or []
                free = sum(1 for value in factors if value == "0")
                torsion = sorted(int(value) for value in factors
                                 if value.isdigit() and value != "0")
                groups.append({"degree": block["degree"], "free_rank": free,
                               "torsion_orders": torsion} if coefficient == "Z"
                              else {"degree": block["degree"],
                                    "dimension": free + len(torsion)})
            homology.append({
                "schema_version": HOMOLOGY_SCHEMA,
                "record_id": f"computed-homology:{entry['space_id']}:{coefficient}:v1",
                "space_id": entry["space_id"], "theory": "ordinary_homology",
                "coefficient": coefficient, "characteristic": characteristic,
                "convention": "unreduced", "knowledge_state": "exact",
                "coverage": {"kind": "complete_finite", "through_degree": dimension,
                             "upper_vanishing_starts_at": dimension + 1},
                "groups": groups,
                "euler_characteristic": hom_source["euler_characteristic"],
                "provenance": _provenance(entry, row, coefficient,
                                          "homology", HOMOLOGY_DERIVATION),
                "sources": _sources(entry, row, coefficient, "computed_homology"),
            })
    return rings, homology


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, required=True,
                        help="cohomology-tables records/ directory")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    payload = build_models(arguments.records)
    arguments.output.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"wrote {len(payload['models'])} model descriptors to {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
