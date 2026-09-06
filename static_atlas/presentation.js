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
    eta: "η",
    gamma: "γ",
    nu: "ν",
    sigma: "σ",
    theta: "θ",
    Sigma: "Σ",
    vee: "∨",
    to: "→",
    oplus: "⊕",
    cup: "∪",
    smile: "∪",
    quad: " ",
    leq: "≤",
    lt: "<",
    times: "×",
    cong: "≅",
    neq: "≠",
    Lambda: "Λ",
    ast: "∗",
    ldots: "…",
  });
  const blackboardCharacters = Object.freeze({
    Z: "ℤ",
    Q: "ℚ",
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
    "text",
  ]);
  const supportedTexCommands = new Set([
    ...Object.keys(simpleTexCommands),
    ...texGroupCommands,
  ]);
  const spectrumNames = Object.freeze({
    S0: Object.freeze({ tex: "S^0", spoken: "S zero" }),
    tmf: Object.freeze({ tex: "\\mathrm{tmf}", spoken: "tmf" }),
    C2: Object.freeze({ tex: "C2", spoken: "C 2" }),
    Ceta: Object.freeze({ tex: "C\\eta", spoken: "C eta" }),
    Cnu: Object.freeze({ tex: "C\\nu", spoken: "C nu" }),
    Csigma: Object.freeze({ tex: "C\\sigma", spoken: "C sigma" }),
    Csigmasq: Object.freeze({
      tex: "C\\sigma^{2}",
      spoken: "C sigma squared",
    }),
    Ctheta4: Object.freeze({ tex: "C\\theta_{4}", spoken: "C theta 4" }),
    Ctheta5: Object.freeze({ tex: "C\\theta_{5}", spoken: "C theta 5" }),
    C2sigma: Object.freeze({ tex: "C2\\sigma", spoken: "C 2 sigma" }),
    Joker: Object.freeze({ tex: "\\mathrm{Joker}", spoken: "Joker" }),
    RP3_6: Object.freeze({
      tex: "\\mathbb{R}P^{6}_{3}",
      spoken: "R P 3 through 6",
    }),
    RP1_4: Object.freeze({
      tex: "\\mathbb{R}P^{4}_{1}",
      spoken: "R P 1 through 4",
    }),
    RP1_6: Object.freeze({
      tex: "\\mathbb{R}P^{6}_{1}",
      spoken: "R P 1 through 6",
    }),
    RP1_8: Object.freeze({
      tex: "\\mathbb{R}P^{8}_{1}",
      spoken: "R P 1 through 8",
    }),
    RP1_10: Object.freeze({
      tex: "\\mathbb{R}P^{10}_{1}",
      spoken: "R P 1 through 10",
    }),
    RP1_12: Object.freeze({
      tex: "\\mathbb{R}P^{12}_{1}",
      spoken: "R P 1 through 12",
    }),
    RP1_256: Object.freeze({
      tex: "\\mathbb{R}P^{256}_{1}",
      spoken: "R P 1 through 256",
    }),
    RP3_256: Object.freeze({
      tex: "\\mathbb{R}P^{256}_{3}",
      spoken: "R P 3 through 256",
    }),
  });

  function firstRecorded(...values) {
    return values.find(
      (value) => value !== undefined && value !== null && value !== "",
    );
  }

  function coefficientDisplay(coefficient) {
    if (coefficient === "Z") return "ℤ";
    if (coefficient === "Q") return "ℚ";
    const fieldMatch = String(coefficient).match(/^F(\d+)$/);
    return fieldMatch ? `𝔽${fieldMatch[1]}` : String(coefficient);
  }

  function coefficientTex(coefficient) {
    if (coefficient === "Z") return "\\mathbb{Z}";
    if (coefficient === "Q") return "\\mathbb{Q}";
    const fieldMatch = String(coefficient).match(/^F(\d+)$/);
    return fieldMatch
      ? `\\mathbb{F}_{${fieldMatch[1]}}`
      : String(coefficient);
  }

  function spectrumNamePresentation(spectrumId) {
    const exactId = String(spectrumId ?? "");
    const curated = spectrumNames[exactId];
    return curated
      ? { tex: curated.tex, spoken: curated.spoken }
      : { tex: "", spoken: exactId };
  }

  function spectrumNameTex(spectrumId) {
    return spectrumNamePresentation(spectrumId).tex;
  }

  function basisNamePresentation(basisName) {
    const exactName = String(basisName ?? "");
    const match = exactName.match(/^x(\d+)(?:_(\d+))?$/);
    if (!match) return { tex: "", spoken: exactName };
    return match[2] === undefined
      ? { tex: `x_{${match[1]}}`, spoken: `x sub ${match[1]}` }
      : {
          tex: `x_{${match[1]},${match[2]}}`,
          spoken: `x sub ${match[1]} comma ${match[2]}`,
        };
  }

  function basisNameTex(basisName) {
    return basisNamePresentation(basisName).tex;
  }

  function basisNameSpoken(basisName) {
    return basisNamePresentation(basisName).spoken;
  }

  function basisSumPresentation(basisNames) {
    if (!Array.isArray(basisNames) || !basisNames.length) {
      return { tex: "", spoken: "" };
    }
    const terms = basisNames.map(basisNamePresentation);
    return {
      tex: terms.every((term) => term.tex)
        ? terms.map((term) => term.tex).join(" + ")
        : "",
      spoken: terms.map((term) => term.spoken).join(" plus "),
    };
  }

  function basisSumTex(basisNames) {
    return basisSumPresentation(basisNames).tex;
  }

  function basisSumSpoken(basisNames) {
    return basisSumPresentation(basisNames).spoken;
  }

  function steenrodOperationTex(squareDegree) {
    const degree = Number(squareDegree);
    if (
      !Number.isSafeInteger(degree)
      || degree < 1
      || !Number.isInteger(Math.log2(degree))
    ) {
      return "";
    }
    return `\\operatorname{Sq}^{${degree}}`;
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

  function monomialTex(powers) {
    return Object.entries(powers ?? {})
      .filter(([, power]) => power !== 0)
      .map(([generator, power]) => power === 1
        ? generator : `${generator}^{${power}}`)
      .join(" ") || "1";
  }

  function relationTex(relation) {
    const terms = Array.isArray(relation?.terms) ? relation.terms : [];
    if (!terms.length) return "";
    return terms.map((term, index) => {
      const value = term.coefficient;
      const monomial = monomialTex(term.powers);
      const magnitude = Math.abs(value);
      const coefficient = magnitude === 1 && monomial !== "1"
        ? "" : String(magnitude);
      const sign = value < 0 ? (index ? " - " : "-") : (index ? " + " : "");
      return `${sign}${coefficient}${monomial === "1" ? "" : monomial}`;
    }).join("") + " = 0";
  }

  function cohomologyCoveragePresentation(record) {
    const coverage = record?.coverage ?? {};
    const groups = Array.isArray(record?.groups) ? record.groups : [];
    const through = coverage.through_degree;
    const rowsByDegree = new Map(groups.map((row) => [row.degree, row]));
    const exactThrough = record?.knowledge_state === "exact"
      && Number.isInteger(through) && through >= 0
      && Array.from({ length: through + 1 }, (_, degree) => {
        const row = rowsByDegree.get(degree);
        return Number.isInteger(row?.dimension) && row.dimension >= 0;
      }).every(Boolean);
    if (coverage.kind === "complete_finite" && exactThrough
      && Number.isInteger(coverage.upper_vanishing_starts_at)
      && coverage.upper_vanishing_starts_at === through + 1) {
      return {
        complete: true,
        label: "All degrees",
        detail: `Groups vanish in every degree above ${through}.`,
      };
    }
    return {
      complete: false,
      label: "Recorded degrees only",
      detail: "No vanishing claim is made for unrecorded degrees.",
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

  function parseTex(value) {
    const source = String(value ?? "");
    if (
      !source
      || source.length > 500
      || /[<>&\u0000-\u001f\u007f\u202a-\u202e\u2066-\u2069]/u.test(source)
    ) {
      return null;
    }

    function appendText(nodes, text) {
      if (!text) return;
      const previous = nodes.at(-1);
      if (previous?.type === "text") previous.value += text;
      else nodes.push({ type: "text", value: text });
    }

    function parseSequence(start, grouped) {
      const nodes = [];
      let index = start;
      while (index < source.length) {
        const character = source[index];
        if (character === "}") {
          if (!grouped) throw new Error("Unexpected TeX brace");
          return { nodes, end: index + 1 };
        }
        if (character === "{") {
          const group = parseSequence(index + 1, true);
          nodes.push(...group.nodes);
          index = group.end;
          continue;
        }
        if (character === "\\") {
          if ([",", " ", ";", ":"].includes(source[index + 1])) {
            appendText(nodes, " ");
            index += 2;
            continue;
          }
          const commandMatch = source.slice(index + 1).match(/^[A-Za-z]+/);
          if (!commandMatch) throw new Error("Malformed TeX command");
          const command = commandMatch[0];
          if (!supportedTexCommands.has(command)) {
            throw new Error(`Unsupported TeX command: ${command}`);
          }
          index += command.length + 1;
          if (simpleTexCommands[command]) {
            appendText(nodes, simpleTexCommands[command]);
            continue;
          }
          if (source[index] !== "{") {
            throw new Error(`Missing group for TeX command: ${command}`);
          }
          const group = parseSequence(index + 1, true);
          index = group.end;
          if (command === "mathbb") {
            if (group.nodes.some((node) => node.type !== "text")) {
              throw new Error("mathbb accepts literal characters only");
            }
            const converted = [...group.nodes.map((node) => node.value).join("")]
              .map((item) => blackboardCharacters[item] ?? item)
              .join("");
            appendText(nodes, converted);
          } else {
            nodes.push({ type: "group", command, children: group.nodes });
          }
          continue;
        }
        if (character === "^" || character === "_") {
          index += 1;
          if (index >= source.length) throw new Error("Missing TeX script");
          let children;
          if (source[index] === "{") {
            const group = parseSequence(index + 1, true);
            children = group.nodes;
            index = group.end;
          } else {
            if (/[\\^_}]/.test(source[index])) {
              throw new Error("Malformed TeX script");
            }
            children = [{ type: "text", value: source[index] }];
            index += 1;
          }
          nodes.push({
            type: character === "^" ? "sup" : "sub",
            children,
          });
          continue;
        }
        appendText(nodes, character);
        index += 1;
      }
      if (grouped) throw new Error("Unclosed TeX group");
      return { nodes, end: index };
    }

    try {
      return parseSequence(0, false).nodes;
    } catch (_error) {
      return null;
    }
  }

  function isSupportedTex(value) {
    return parseTex(value) !== null;
  }

  return Object.freeze({
    blackboardCharacters,
    basisNamePresentation,
    basisNameSpoken,
    basisNameTex,
    basisSumPresentation,
    basisSumSpoken,
    basisSumTex,
    coefficientDisplay,
    coefficientTex,
    cohomologyCoveragePresentation,
    coverageFor,
    coveragePresentation,
    firstRecorded,
    groupPresentation,
    isSupportedTex,
    monomialTex,
    parseTex,
    relationTex,
    simpleTexCommands,
    spectrumNamePresentation,
    spectrumNameTex,
    steenrodOperationTex,
    texGroupCommands,
  });
}));
