(function exposePresentation(root, factory) {
  "use strict";

  const presentation = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = presentation;
  }
  if (root) root.HomologyAtlasPresentation = presentation;
}(typeof globalThis === "object" ? globalThis : this, () => {
  "use strict";

  const simpleTexCommands = Object.freeze({
    infinity: "∞",
    infty: "∞",
    gamma: "γ",
    Sigma: "Σ",
    vee: "∨",
    to: "→",
    oplus: "⊕",
    ast: "∗",
    ldots: "…",
  });
  const blackboardCharacters = Object.freeze({
    Z: "ℤ",
    R: "ℝ",
    C: "ℂ",
    H: "ℍ",
    O: "𝕆",
    F: "𝔽",
  });
  const texGroupCommands = new Set([
    "mathbb",
    "mathrm",
    "operatorname",
    "widetilde",
  ]);
  const supportedTexCommands = new Set([
    ...Object.keys(simpleTexCommands),
    ...texGroupCommands,
  ]);

  function firstRecorded(...values) {
    return values.find(
      (value) => value !== undefined && value !== null && value !== "",
    );
  }

  function coefficientDisplay(coefficient) {
    if (coefficient === "Z") return "ℤ";
    const fieldMatch = String(coefficient).match(/^F(\d+)$/);
    return fieldMatch ? `𝔽${fieldMatch[1]}` : String(coefficient);
  }

  function coefficientTex(coefficient) {
    if (coefficient === "Z") return "\\mathbb{Z}";
    const fieldMatch = String(coefficient).match(/^F(\d+)$/);
    return fieldMatch
      ? `\\mathbb{F}_{${fieldMatch[1]}}`
      : String(coefficient);
  }

  function incompleteExactGroup(kind) {
    return {
      exact: false,
      plain: `Exact ${kind} data is incomplete in this snapshot.`,
      tex: "",
    };
  }

  function groupPresentation(row) {
    const group = row?.group ?? {};
    if (group.state !== row?.knowledge_state) {
      return incompleteExactGroup("group-state");
    }
    if (group.state !== "exact") {
      return {
        exact: false,
        plain: group.plain ?? String(group.state ?? "not recorded"),
        tex: "",
      };
    }

    if (row.coefficient_ring === "Z") {
      if (
        !Number.isInteger(group.free_rank)
        || group.free_rank < 0
        || !Array.isArray(group.torsion_orders)
        || group.torsion_orders.some(
          (order) => !Number.isInteger(order) || order < 2,
        )
      ) {
        return incompleteExactGroup("integral-group");
      }
      const terms = [];
      const spokenTerms = [];
      if (group.free_rank === 1) {
        terms.push("\\mathbb{Z}");
        spokenTerms.push("the integers");
      } else if (group.free_rank > 1) {
        terms.push(`\\mathbb{Z}^{\\oplus ${group.free_rank}}`);
        spokenTerms.push(`${group.free_rank} copies of the integers`);
      }

      const counts = new Map();
      group.torsion_orders.forEach((order) => {
        const key = String(order);
        counts.set(key, (counts.get(key) ?? 0) + 1);
      });
      counts.forEach((count, order) => {
        const cyclic = `\\mathbb{Z}/${order}\\mathbb{Z}`;
        if (count === 1) {
          terms.push(cyclic);
          spokenTerms.push(`integers modulo ${order}`);
        } else {
          terms.push(`(${cyclic})^{\\oplus ${count}}`);
          spokenTerms.push(`${count} copies of the integers modulo ${order}`);
        }
      });
      return {
        exact: true,
        tex: terms.length ? terms.join("\\oplus ") : "0",
        plain: terms.length ? spokenTerms.join(" direct sum ") : "zero",
      };
    }

    if (!Number.isInteger(group.dimension) || group.dimension < 0) {
      return incompleteExactGroup("field-vector-space");
    }
    if (group.dimension === 0) {
      return { exact: true, tex: "0", plain: "zero" };
    }
    const field = coefficientTex(row.coefficient_ring);
    return {
      exact: true,
      tex:
        group.dimension === 1
          ? field
          : `${field}^{\\oplus ${group.dimension}}`,
      plain:
        group.dimension === 1
          ? coefficientDisplay(row.coefficient_ring)
          : `${group.dimension} copies of ${coefficientDisplay(row.coefficient_ring)}`,
    };
  }

  function coverageFor(space) {
    const coverage = firstRecorded(space?.homology_coverage, space?.coverage);
    return coverage && typeof coverage === "object" ? coverage : {};
  }

  function coveragePresentation(space, rows, snapshot = {}) {
    const coverage = coverageFor(space);
    const through = firstRecorded(
      coverage.computed_through_degree,
      coverage.materialized_through_degree,
      snapshot.materialized_through_degree,
    );
    if (coverage.kind === "bounded_through_degree") {
      return {
        className: "coverage-bounded",
        label:
          through === undefined
            ? "Bounded record"
            : `Bounded · recorded through degree ${through}`,
        detail:
          through === undefined
            ? "No claim is made outside the recorded range."
            : `Recorded through degree ${through}; no claim is made above it.`,
      };
    }
    if (coverage.kind === "complete_finite_cw") {
      const expectedThrough = Number(through);
      const rowsByDegree = new Map(
        rows.map((row) => [Number(row.degree), row]),
      );
      const exactThrough =
        Number.isInteger(expectedThrough)
        && expectedThrough >= 0
        && Array.from(
          { length: expectedThrough + 1 },
          (_item, degree) => {
            const row = rowsByDegree.get(degree);
            return (
              row?.knowledge_state === "exact"
              && row.group?.state === "exact"
              && groupPresentation(row).exact
            );
          },
        ).every(Boolean);
      const vanishing = coverage.upper_vanishing_starts_at;
      const hasExplicitVanishing =
        Number.isInteger(vanishing) && vanishing > expectedThrough;
      if (exactThrough && hasExplicitVanishing) {
        return {
          className: "coverage-exhaustive",
          label: "Exhaustive · all degrees",
          detail: `Exact through degree ${expectedThrough}; groups vanish from degree ${vanishing}.`,
        };
      }
      return {
        className: "coverage-neutral",
        label: "Coverage incomplete",
        detail:
          "Finite coverage metadata is recorded, but the selected rows or explicit upper-vanishing bound are incomplete; no exhaustive claim is shown.",
      };
    }
    return {
      className: "coverage-neutral",
      label: "Coverage not classified",
      detail: coverage.detail ?? "No coverage classification is recorded.",
    };
  }

  function isSupportedTex(value) {
    const source = String(value ?? "");
    if (
      !source
      || source.length > 500
      || /\\(?:href|html|include|input|write|def|newcommand|style)/i.test(
        source,
      )
    ) {
      return false;
    }
    let braceDepth = 0;
    for (const character of source) {
      if (character === "{") braceDepth += 1;
      if (character === "}") braceDepth -= 1;
      if (braceDepth < 0) return false;
    }
    if (braceDepth !== 0) return false;
    return [...source.matchAll(/\\([A-Za-z]+)/g)].every((match) =>
      supportedTexCommands.has(match[1]),
    );
  }

  return Object.freeze({
    blackboardCharacters,
    coefficientDisplay,
    coefficientTex,
    coverageFor,
    coveragePresentation,
    firstRecorded,
    groupPresentation,
    isSupportedTex,
    simpleTexCommands,
    texGroupCommands,
  });
}));
