(() => {
  "use strict";

  const atlas = JSON.parse(document.getElementById("atlas-data").textContent);
  const snapshot = atlas.snapshot ?? {};
  const conceptualSpaces = Array.isArray(atlas.conceptual_spaces) ? atlas.conceptual_spaces : [];
  const sections = Array.isArray(atlas.sections) ? atlas.sections : [];
  const issueEndpoint = "https://github.com/DaveArcher18/homology-db/issues/new";
  const themeStorageKey = "homology-atlas-theme-v1";
  const coefficientLabels = Object.freeze({
    Z: "ℤ",
    F2: "𝔽₂",
    F3: "𝔽₃",
    F5: "𝔽₅",
    F7: "𝔽₇",
  });
  const spacesById = new Map(conceptualSpaces.map((space) => [space.id, space]));
  const entriesById = new Map();
  const sectionsById = new Map();
  const selectionTimers = new Map();
  const narrowIndexMedia = window.matchMedia("(max-width: 58rem)");
  const state = {
    query: "",
    coefficient: "Z",
    reduced: false,
    family: "",
    dimension: "",
    reliability: "",
    torsion: false,
    review: false,
    visible: [],
    selectedId: null,
  };

  const searchInput = document.getElementById("atlas-search");
  const atlasControls = document.getElementById("atlas-controls");
  const coefficientFilter = document.getElementById("coefficient-filter");
  const reducedFilter = document.getElementById("reduced-filter");
  const familyFilter = document.getElementById("family-filter");
  const dimensionFilter = document.getElementById("dimension-filter");
  const reliabilityFilter = document.getElementById("reliability-filter");
  const torsionFilter = document.getElementById("torsion-filter");
  const reviewToggle = document.getElementById("review-toggle");
  const aboutToggle = document.getElementById("about-toggle");
  const themeSelect = document.getElementById("theme-select");
  const clearFilters = document.getElementById("clear-filters");
  const filterDisclosure = document.getElementById("filter-disclosure");
  const activeFilterCount = document.getElementById("active-filter-count");
  const indexToggle = document.getElementById("index-toggle");
  const indexClose = document.getElementById("index-close");
  const indexBackdrop = document.getElementById("index-backdrop");
  const requestSpace = document.getElementById("request-space");
  const atlasIndex = document.getElementById("atlas-index");
  const sectionIndex = document.getElementById("section-index");
  const spaceIndex = document.getElementById("space-index");
  const spaceIndexCount = document.getElementById("space-index-count");
  const spaceIndexDisclosure = document.getElementById("space-index-disclosure");
  const atlasDocument = document.getElementById("atlas-document");
  const snapshotAbout = document.getElementById("snapshot-about");
  const resultStatus = document.getElementById("result-status");
  const actionStatus = document.getElementById("action-status");
  const filterSummary = filterDisclosure.querySelector(":scope > summary");
  const backgroundInertTargets = [
    document.querySelector(".skip-link"),
    document.querySelector(".site-header"),
    document.querySelector(".toolbar"),
    atlasDocument,
    document.querySelector(".site-footer"),
  ].filter(Boolean);
  let indexReturnFocus = indexToggle;

  function element(tagName, className, text) {
    const node = document.createElement(tagName);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function firstRecorded(...values) {
    return values.find((value) => value !== undefined && value !== null && value !== "");
  }

  function humanize(value) {
    return String(value ?? "not recorded").replaceAll("_", " ");
  }

  function displayValue(value) {
    if (value === undefined || value === null || value === "") return "Not recorded";
    if (typeof value === "boolean") return value ? "yes" : "no";
    if (Array.isArray(value)) return value.map(displayValue).join(", ") || "None";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  }

  function appendDefinition(list, term, description) {
    list.append(element("dt", "", term), element("dd", "", displayValue(description)));
  }

  function appendDefinitionNode(list, term, descriptionNode) {
    const description = element("dd");
    description.append(descriptionNode);
    list.append(element("dt", "", term), description);
  }

  function normalizedThemePreference(value) {
    return value === "light" || value === "dark" ? value : "system";
  }

  function storedThemePreference() {
    const bootPreference = normalizedThemePreference(document.documentElement.dataset.theme);
    if (bootPreference !== "system") return bootPreference;
    try {
      return normalizedThemePreference(window.localStorage.getItem(themeStorageKey));
    } catch (_error) {
      return "system";
    }
  }

  function applyThemePreference(value, persist = true) {
    const preference = normalizedThemePreference(value);
    if (preference === "system") {
      delete document.documentElement.dataset.theme;
    } else {
      document.documentElement.dataset.theme = preference;
    }
    themeSelect.value = preference;
    if (!persist) return;
    try {
      if (preference === "system") window.localStorage.removeItem(themeStorageKey);
      else window.localStorage.setItem(themeStorageKey, preference);
    } catch (_error) {
      // The atlas remains usable when storage is unavailable or file URL behavior varies.
    }
  }

  function announce(message) {
    actionStatus.textContent = "";
    window.requestAnimationFrame(() => {
      actionStatus.textContent = message;
    });
  }

  function normalizedSearchSource(value) {
    return String(value ?? "")
      .normalize("NFKD")
      .toLocaleLowerCase()
      .replace(/\\mathbb/g, "")
      .replace(/[\\{}_^.,;:()\[\]\/\-]+/g, " ")
      .replace(/[^a-z0-9\s]+/g, " ")
      .trim();
  }

  function normalize(value) {
    return normalizedSearchSource(value).replace(/\s+/g, "");
  }

  function tokenize(value) {
    return normalizedSearchSource(value).split(/\s+/).filter(Boolean);
  }

  function searchTextValues(value, output = []) {
    if (value === undefined || value === null) return output;
    if (Array.isArray(value)) {
      value.forEach((item) => searchTextValues(item, output));
    } else if (typeof value === "object") {
      Object.values(value).forEach((item) => searchTextValues(item, output));
    } else {
      output.push(String(value));
    }
    return output;
  }

  function modelRecords(space) {
    return asArray(space.models);
  }

  function evidenceRecords(space) {
    return asArray(space.evidence);
  }

  function computationRecords(space) {
    const records = [...asArray(space.computations)];
    evidenceRecords(space).forEach((record) => {
      const computation = record.computation;
      if (computation?.computation_id || computation?.id) records.push(computation);
    });
    const seen = new Set();
    return records.filter((record) => {
      const identity = record.computation_id ?? record.id ?? JSON.stringify(record);
      if (seen.has(identity)) return false;
      seen.add(identity);
      return true;
    });
  }

  function citationRecords(record) {
    const references = asArray(record.references);
    return references.length ? references : asArray(record.citations);
  }

  function searchValues(space) {
    const relatedNames = asArray(space.relations)
      .map((relation) => spacesById.get(relation.target_id)?.name?.plain)
      .filter(Boolean);
    const details = [
      space.summary,
      space.chromatic_relevance,
      space.relevance,
      space.parameters,
      space.properties,
      modelRecords(space).map((model) => ({
        name: model.name,
        kind: model.kind,
        construction: model.construction,
        cells: model.cell_degrees,
        cell_formula: model.cell_formula,
        attaching_map: model.attaching_map,
        boundary_formula: model.boundary_formula,
        scope: model.model_scope,
      })),
      evidenceRecords(space).map((record) => ({
        kind: record.kind,
        sketch: record.computation_sketch,
        citation: record.citation,
        references: citationRecords(record),
      })),
      asArray(space.homology).map((row) => ({
        coefficient: row.coefficient_ring,
        degree: row.degree,
        group: row.group?.plain,
        torsion: row.group?.torsion_orders,
      })),
      computationRecords(space).map((record) => ({
        algorithm: record.algorithm_id,
        parameters: record.parameters,
        scope: record.output_scope,
      })),
    ];
    return [
      space.name?.plain,
      ...asArray(space.aliases),
      space.id,
      space.slug,
      space.taxonomy?.family,
      ...asArray(space.taxonomy?.tags),
      ...relatedNames,
      ...searchTextValues(details),
    ].filter(Boolean);
  }

  function searchRank(space, query) {
    if (!query.trim()) return 0;
    const compactQuery = normalize(query);
    const queryTokens = tokenize(query);
    const values = searchValues(space);
    const compactValues = values.map(normalize);
    if (compactValues.some((value) => value === compactQuery)) return 0;
    if (compactValues.some((value) => value.startsWith(compactQuery))) return 1;
    const joined = normalize(values.join(" "));
    if (queryTokens.length && queryTokens.every((token) => joined.includes(token))) return 2;
    if (compactValues.some((value) => value.includes(compactQuery))) return 3;
    return Number.POSITIVE_INFINITY;
  }

  function coefficientDisplay(coefficient) {
    if (coefficientLabels[coefficient]) return coefficientLabels[coefficient];
    const fieldMatch = String(coefficient).match(/^F(\d+)$/);
    return fieldMatch ? `𝔽${subscript(fieldMatch[1])}` : coefficient;
  }

  function superscript(value) {
    const digits = { "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻" };
    return String(value).split("").map((digit) => digits[digit] ?? digit).join("");
  }

  function subscript(value) {
    const digits = { "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉", "-": "₋" };
    return String(value).split("").map((digit) => digits[digit] ?? digit).join("");
  }

  function groupDisplay(row) {
    if (row.group.state !== "exact") return row.group.plain;
    if (row.coefficient_ring === "Z") {
      return row.group.plain.replaceAll("Z", "ℤ").replaceAll(" + ", " ⊕ ");
    }
    const fieldGroup = row.group.plain.match(/^(F\d+)(?:\^(\d+))?$/);
    if (!fieldGroup) return row.group.plain;
    return coefficientDisplay(fieldGroup[1]) + (fieldGroup[2] ? superscript(fieldGroup[2]) : "");
  }

  function safeHttpsUrl(value) {
    if (typeof value !== "string" || !value) return null;
    try {
      const url = new URL(value);
      return url.protocol === "https:" ? url.href : null;
    } catch (_error) {
      return null;
    }
  }

  function outboundLink(label, href, accessibleContext) {
    const link = element("a", "external-link", label);
    const safeHref = safeHttpsUrl(href);
    if (!safeHref) return null;
    link.href = safeHref;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    if (accessibleContext) link.setAttribute("aria-label", `${accessibleContext} (opens in a new tab)`);
    return link;
  }

  function snapshotReference() {
    return firstRecorded(snapshot.snapshot_id, snapshot.snapshot_name, "unknown-snapshot");
  }

  function issueUrl(template, title) {
    const url = new URL(issueEndpoint);
    url.searchParams.set("template", template);
    url.searchParams.set("title", title);
    return url.href;
  }

  function spaceFeedbackUrl(space) {
    return issueUrl(
      "space-feedback.yml",
      `[Space feedback] ${space.name?.plain ?? space.id} | ${space.id} | ${snapshotReference()}`,
    );
  }

  function familyFeedbackUrl(section) {
    return issueUrl(
      "family-feedback.yml",
      `[Family feedback] ${section.label} | ${section.id} | ${snapshotReference()}`,
    );
  }

  function permalinkFor(space) {
    const url = new URL(window.location.href);
    url.hash = `space=${encodeURIComponent(space.slug)}`;
    return url.href;
  }

  async function copyText(text, button) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (_error) {
      const temporary = document.createElement("textarea");
      temporary.value = text;
      temporary.setAttribute("readonly", "");
      temporary.className = "visually-hidden";
      document.body.append(temporary);
      temporary.select();
      document.execCommand("copy");
      temporary.remove();
    }
    const previous = button.textContent;
    button.textContent = "Copied";
    announce(`${previous} copied to the clipboard.`);
    window.setTimeout(() => { button.textContent = previous; }, 1200);
  }

  function downloadRecord(space) {
    const contents = JSON.stringify(space.raw, null, 2);
    const url = URL.createObjectURL(new Blob([contents], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${space.slug}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function detailsBlock(title, count, reviewDetail = false) {
    const details = element("details");
    if (reviewDetail) details.dataset.reviewDetail = "true";
    const summaryNode = element("summary");
    summaryNode.append(element("h4", "details-heading", title), element("span", "review-label", String(count)));
    const content = element("div", "detail-content");
    details.append(summaryNode, content);
    return { details, content };
  }

  function propertyValue(space, key) {
    return asArray(space.properties).find((property) => property.key === key)?.value;
  }

  function spaceDimension(space) {
    const property = asArray(space.properties).find((item) => item.key === "dimension");
    return property ? property.value : space.dimension;
  }

  function isInfiniteFiniteType(space) {
    return Boolean(space.infinite_finite_type) || (spaceDimension(space) === null && coverageFor(space)?.kind === "bounded_through_degree");
  }

  function coverageFor(space) {
    const directCoverage = firstRecorded(space.homology_coverage, space.coverage);
    if (directCoverage && typeof directCoverage === "object") return directCoverage;
    const rowCoverage = asArray(space.homology).find((row) => row.coverage)?.coverage;
    if (rowCoverage) return rowCoverage;
    return asArray(space.raw?.homology_responses).find((response) => response.coverage)?.coverage ?? null;
  }

  function coverageMessage(space) {
    const coverage = coverageFor(space) ?? {};
    const kind = firstRecorded(coverage.kind, coverage.coverage_kind, coverage.scope);
    const through = firstRecorded(
      coverage.computed_through_degree,
      coverage.materialized_through_degree,
      snapshot.materialized_through_degree,
    );
    const upperVanishing = firstRecorded(coverage.upper_vanishing_starts_at, space.upper_vanishing_starts_at);
    if (kind === "bounded_through_degree" || isInfiniteFiniteType(space)) {
      return through !== undefined
        ? `finite-type CW filtration · computed through degree ${through} · no claim above degree ${through}`
        : "finite-type CW filtration · bounded computation · no upper-vanishing claim";
    }
    if (upperVanishing !== undefined && upperVanishing !== null) {
      return `complete finite CW computation · groups vanish from degree ${upperVanishing}`;
    }
    if (kind) return humanize(kind);
    return asArray(space.homology)[0]?.value_scope?.replaceAll("_", " ") ?? "coverage not recorded";
  }

  function renderHomology(space, entry) {
    const heading = entry.querySelector(".homology-heading h4");
    const convention = entry.querySelector(".homology-convention");
    const coverage = entry.querySelector(".coverage-note");
    const tableBody = entry.querySelector(".homology-table tbody");
    const rows = asArray(space.homology).filter((row) =>
      row.coefficient_ring === state.coefficient && row.reduced === state.reduced
    );
    heading.textContent = `H${state.reduced ? "̃" : ""}ₙ(${space.name.plain}; ${coefficientDisplay(state.coefficient)})`;
    convention.textContent = `ordinary homology · ${state.reduced ? "reduced" : "unreduced"} · ${humanize(rows[0]?.homology_convention ?? rows[0]?.convention_state ?? "convention not recorded")}`;
    convention.title = humanize(rows[0]?.convention_state ?? "No convention identity recorded");
    coverage.textContent = coverageMessage(space);
    coverage.classList.toggle("coverage-bounded", isInfiniteFiniteType(space));
    tableBody.replaceChildren();
    if (!rows.length) {
      const tableRow = element("tr");
      const cell = element("td", "state-nonexact", "No values are recorded for this coefficient and convention.");
      cell.colSpan = 4;
      tableRow.append(cell);
      tableBody.append(tableRow);
      return;
    }
    rows.forEach((row) => {
      const tableRow = element("tr");
      const degree = element("th", "degree-cell", `H${subscript(row.degree)}`);
      degree.scope = "row";
      const group = element("td", row.group.state === "exact" ? "" : "state-nonexact", groupDisplay(row));
      const knowledge = element("td", "state-cell review-only", row.knowledge_state);
      const assertion = element("td", "assertion-cell review-only", row.assertion_id);
      group.setAttribute("headers", `table-${space.slug}-group`);
      knowledge.setAttribute("headers", `table-${space.slug}-state`);
      assertion.setAttribute("headers", `table-${space.slug}-assertion`);
      tableRow.append(degree, group, knowledge, assertion);
      tableBody.append(tableRow);
    });
  }

  function renderCellDescription(model) {
    const formula = firstRecorded(model.cell_formula, model.cells_formula);
    const degrees = firstRecorded(model.cell_degrees, model.cells);
    const cells = asArray(degrees).map((cell) => {
      if (!cell || typeof cell !== "object") return displayValue(cell);
      const count = firstRecorded(cell.count, cell.rank, 1);
      const degree = firstRecorded(cell.degree, cell.dimension);
      return degree === undefined ? displayValue(cell) : `${count} cell${count === 1 ? "" : "s"} in degree ${degree}`;
    }).join("; ");
    if (formula && cells) return `${formula}; materialized cells: ${cells}`;
    return displayValue(firstRecorded(formula, cells || degrees));
  }

  function renderModels(space, content) {
    const models = modelRecords(space);
    if (!models.length) {
      content.append(element("p", "empty-state", "No qualified CW Model record is attached to this snapshot."));
      return;
    }
    models.forEach((model) => {
      const card = element("section", "record-card model-card");
      card.append(element("h5", "record-title", firstRecorded(model.name, model.model_id, model.id, "CW model")));
      const list = element("dl", "record-list");
      appendDefinition(list, "Model ID", firstRecorded(model.model_id, model.id));
      appendDefinition(list, "Kind", humanize(model.kind));
      appendDefinition(list, "Status", humanize(model.status));
      appendDefinition(list, "Construction", model.construction);
      appendDefinition(list, "Cells", renderCellDescription(model));
      appendDefinition(list, "Attaching map", model.attaching_map);
      appendDefinition(list, "Cellular boundary", model.boundary_formula);
      appendDefinition(list, "Scope", firstRecorded(model.model_scope, model.scope));
      appendDefinition(list, "Checked artifact", firstRecorded(model.artifact_path, model.artifact));
      appendDefinition(list, "Artifact SHA-256", model.artifact_sha256);
      appendDefinition(list, "Cellular-chain SHA-256", firstRecorded(model.input_sha256, model.chain_sha256));
      card.append(list);
      content.append(card);
    });
  }

  function citationTitle(reference) {
    if (typeof reference === "string") return reference;
    if (!reference || typeof reference !== "object") return "Untitled source";
    const authors = Array.isArray(reference.authors) ? reference.authors.join(", ") : reference.authors;
    return [authors, reference.title, reference.year].filter(Boolean).join(". ");
  }

  function renderCitation(reference) {
    const item = element("li", "citation-item");
    const record = reference && typeof reference === "object" ? reference : {};
    const title = citationTitle(reference) || firstRecorded(record.citation, record.reference_id, "Untitled source");
    const link = outboundLink(`${title} ↗`, record.url, `Open source: ${title}`);
    item.append(link ?? element("span", "", title));
    const context = [
      record.source_kind && humanize(record.source_kind),
      record.role && humanize(record.role),
      record.locator,
    ].filter(Boolean).join(" · ");
    if (context) item.append(element("span", "citation-context", context));
    return item;
  }

  function renderEvidence(space, content) {
    const records = evidenceRecords(space);
    if (!records.length) {
      content.append(element("p", "empty-state", "No Evidence record is attached to this snapshot."));
      return;
    }
    records.forEach((record) => {
      const card = element("section", "record-card evidence-card");
      card.append(element("h5", "record-title", firstRecorded(record.id, record.evidence_id, "Evidence record")));
      const list = element("dl", "record-list");
      appendDefinition(list, "Kind", humanize(record.kind));
      appendDefinition(list, "Reliability", humanize(record.reliability));
      appendDefinition(list, "Release status", humanize(record.release_status ?? snapshot.release_status));
      appendDefinition(list, "Source locator", record.locator);
      appendDefinition(list, "Algorithm", record.algorithm_id);
      appendDefinition(list, "Input SHA-256", firstRecorded(record.chain_sha256, record.input_sha256));
      appendDefinition(list, "Representatives", humanize(record.representatives_state));
      appendDefinition(list, "Induced maps", humanize(record.induced_maps_state));
      card.append(list);

      const sketch = firstRecorded(record.computation_sketch, record.sketch);
      if (sketch) {
        const sketchBlock = element("div", "computation-sketch");
        sketchBlock.append(
          element("h6", "", "Computation sketch"),
          element("p", "", sketch),
          element("p", "sketch-note", "A mathematical sketch is evidence context; it is not itself a recorded software run."),
        );
        card.append(sketchBlock);
      }

      const references = citationRecords(record);
      if (references.length) {
        const citationHeading = element("h6", "citation-heading", "Sources and locators");
        const citations = element("ul", "citation-list");
        references.forEach((reference) => citations.append(renderCitation(reference)));
        card.append(citationHeading, citations);
      } else if (record.citation) {
        card.append(element("p", "citation-fallback", `Citation: ${record.citation}`));
      }
      content.append(card);
    });
  }

  function renderComputations(space, content) {
    const computations = computationRecords(space);
    if (!computations.length) {
      content.append(element(
        "p",
        "empty-state",
        "No recorded Computation run is attached. Any computation sketch appears under Evidence and is not presented as an executed run.",
      ));
      return;
    }
    computations.forEach((record) => {
      const card = element("section", "record-card computation-card");
      card.append(element("h5", "record-title", firstRecorded(record.computation_id, record.id, "Recorded computation")));
      const list = element("dl", "record-list");
      appendDefinition(list, "Status", humanize(record.status));
      appendDefinition(list, "Algorithm", record.algorithm_id);
      appendDefinition(list, "Parameters", record.parameters);
      appendDefinition(list, "Output scope", record.output_scope);
      appendDefinition(list, "Input SHA-256", firstRecorded(record.input_sha256, record.chain_sha256));
      card.append(list);
      content.append(card);
    });
  }

  function renderRelations(space, content) {
    const relations = asArray(space.relations);
    if (!relations.length) {
      content.append(element("p", "empty-state", "No relationship records are attached to this snapshot."));
      return;
    }
    const list = element("ul", "relation-list");
    relations.forEach((relation) => {
      const target = spacesById.get(relation.target_id);
      const item = element("li");
      item.append(document.createTextNode(
        `${space.name.plain} — ${humanize(relation.type)} → `,
      ));
      if (target) {
        const link = element("a", "", target.name.plain);
        link.href = `#space=${encodeURIComponent(target.slug)}`;
        item.append(link);
      } else {
        item.append(document.createTextNode(relation.target_id ?? "unresolved target"));
      }
      if (relation.detail) {
        item.append(element("span", "relation-context", relation.detail));
      }
      const reviewContext = [
        relation.id,
        ...asArray(relation.evidence_ids),
      ].filter(Boolean).join(" · ");
      if (reviewContext) {
        item.append(element("span", "relation-context review-only", reviewContext));
      }
      list.append(item);
    });
    content.append(list);
  }

  function buildEntry(space) {
    const entry = element("article", "atlas-entry");
    entry.id = `space-${space.slug}`;
    entry.dataset.spaceId = space.id;

    const header = element("header", "entry-header");
    const titleBlock = element("div");
    titleBlock.append(
      element("p", "entry-kicker", humanize(space.taxonomy?.family)),
      element("h3", "entry-title", space.name.plain),
    );
    const actions = element("div", "permalink-actions");
    const permalink = element("a", "permalink", "# permalink");
    permalink.href = `#space=${encodeURIComponent(space.slug)}`;
    const copyLink = element("button", "copy-link-button", "Copy link");
    copyLink.type = "button";
    copyLink.addEventListener("click", () => copyText(permalinkFor(space), copyLink));
    const feedback = outboundLink(
      "Correct or improve ↗",
      spaceFeedbackUrl(space),
      `Give feedback on ${space.name.plain}`,
    );
    actions.append(permalink, copyLink);
    if (feedback) {
      feedback.classList.add("feedback-link");
      actions.append(feedback);
    }
    header.append(titleBlock, actions);

    const meta = element("p", "entry-meta");
    if (asArray(space.aliases).length) meta.append(element("span", "", `Aliases: ${space.aliases.join(", ")}`));
    const dimension = spaceDimension(space);
    const dimensionLabel = isInfiniteFiniteType(space) ? "dimension ∞ · finite type" : `dimension ${dimension ?? "not recorded"}`;
    meta.append(
      element("span", "", dimensionLabel),
      element("span", "review-only", space.id),
      element("span", "review-only", space.kind),
    );

    const introduction = element("div", "entry-introduction");
    const summaryText = firstRecorded(space.summary, "No summary is recorded for this space.");
    introduction.append(element("p", "space-summary", summaryText));
    const relevance = firstRecorded(space.chromatic_relevance, space.relevance);
    if (relevance) {
      const relevanceBlock = element("p", "space-relevance");
      relevanceBlock.append(element("strong", "", "Why it matters. "), document.createTextNode(relevance));
      introduction.append(relevanceBlock);
    }
    const tags = asArray(space.taxonomy?.tags);
    if (tags.length) {
      const tagList = element("ul", "tag-list");
      tagList.setAttribute("aria-label", "Space tags");
      tags.forEach((tag) => tagList.append(element("li", "tag", humanize(tag))));
      introduction.append(tagList);
    }

    const homology = element("section", "homology-block");
    const homologyHeading = element("div", "homology-heading");
    homologyHeading.append(element("h4"), element("span", "homology-convention"));
    const coverage = element("p", "coverage-note");
    const table = element("table", "homology-table");
    const caption = element("caption", "visually-hidden", `Homology groups for ${space.name.plain}`);
    const tableHead = element("thead");
    const headerRow = element("tr");
    const headerIds = ["degree", "group", "state", "assertion"]
      .map((kind) => `table-${space.slug}-${kind}`);
    ["Degree", "Group", "State", "Assertion ID"].forEach((label, index) => {
      const headerCell = element("th", index > 1 ? "review-only" : "", label);
      headerCell.scope = "col";
      headerCell.id = headerIds[index];
      headerRow.append(headerCell);
    });
    tableHead.append(headerRow);
    table.append(caption, tableHead, element("tbody"));
    homology.append(homologyHeading, coverage, table);

    const evidence = evidenceRecords(space);
    const computations = computationRecords(space);
    const evidenceSummary = element("p", "evidence-summary");
    const firstEvidence = evidence[0];
    const firstCitation = citationRecords(firstEvidence ?? {})[0];
    const sourceTitle = typeof firstCitation === "string"
      ? firstCitation
      : firstRecorded(firstCitation?.title, firstEvidence?.citation, "source not recorded");
    const reliability = firstEvidence?.reliability ?? "reliability not recorded";
    const evidenceKind = humanize(firstEvidence?.kind ?? "source not recorded");
    evidenceSummary.append(
      element("strong", "", "Provenance"),
      element("span", "", `Source: ${sourceTitle}`),
      element("span", "", humanize(reliability)),
      element("span", "review-only", evidenceKind),
      element("span", "review-only", `${evidence.length} evidence record${evidence.length === 1 ? "" : "s"}`),
      element("span", "review-only", `${computations.length} recorded computation run${computations.length === 1 ? "" : "s"}`),
      element("span", "review-only review-warning", humanize(snapshot.release_status)),
    );

    const details = element("div", "entry-details");
    const models = modelRecords(space);
    const modelBlock = detailsBlock("Models & constructions", models.length);
    renderModels(space, modelBlock.content);

    const relations = asArray(space.relations);
    const relationBlock = detailsBlock("Relationships", relations.length, true);
    renderRelations(space, relationBlock.content);

    const evidenceBlock = detailsBlock("Evidence, sketches & citations", evidence.length, true);
    renderEvidence(space, evidenceBlock.content);

    const computationBlock = detailsBlock("Computation runs (recorded)", computations.length, true);
    renderComputations(space, computationBlock.content);

    const dataQuality = space.data_quality ?? {};
    const missingFields = asArray(dataQuality.missing_required_fields);
    const malformedFields = asArray(dataQuality.malformed_fields);
    const qualityIssueCount = missingFields.length + malformedFields.length;
    const qualityBlock = detailsBlock("Data quality", qualityIssueCount, true);
    const qualityList = element("dl", "record-list");
    appendDefinition(qualityList, "Exporter state", dataQuality.state);
    appendDefinition(qualityList, "Missing required fields", missingFields.length ? missingFields : "None");
    appendDefinition(qualityList, "Malformed fields", malformedFields.length ? malformedFields : "None");
    qualityBlock.content.append(qualityList);

    const rawBlock = detailsBlock("Raw record", 1, true);
    const rawActions = element("div", "raw-actions");
    const copyJson = element("button", "copy-button", "Copy JSON");
    copyJson.type = "button";
    copyJson.addEventListener("click", () => copyText(JSON.stringify(space.raw, null, 2), copyJson));
    const downloadJson = element("button", "download-button", "Download JSON");
    downloadJson.type = "button";
    downloadJson.addEventListener("click", () => downloadRecord(space));
    const report = outboundLink(
      "Open structured feedback form ↗",
      spaceFeedbackUrl(space),
      `Give feedback on ${space.name.plain}`,
    );
    rawActions.append(copyJson, downloadJson);
    if (report) {
      report.classList.add("download-button");
      rawActions.append(report);
    }
    const rawPre = element("pre");
    rawPre.setAttribute("aria-label", `Raw JSON record for ${space.name.plain}`);
    rawBlock.details.addEventListener("toggle", () => {
      if (rawBlock.details.open && !rawPre.textContent) rawPre.textContent = JSON.stringify(space.raw, null, 2);
    });
    rawBlock.content.append(rawActions, rawPre);

    details.append(
      modelBlock.details,
      relationBlock.details,
      evidenceBlock.details,
      computationBlock.details,
      qualityBlock.details,
      rawBlock.details,
    );
    entry.append(header, meta, introduction, homology, evidenceSummary, details);
    renderHomology(space, entry);
    return entry;
  }

  function buildSectionHeading(section) {
    const heading = element("div", "section-heading");
    const title = element("h2");
    title.append(
      element("span", "section-kicker", "Family"),
      document.createTextNode(section.label),
      element("span", "section-count", String(asArray(section.conceptual_space_ids).length)),
    );
    const feedback = outboundLink(
      "Family feedback ↗",
      familyFeedbackUrl(section),
      `Give feedback on the ${section.label} family`,
    );
    heading.append(title);
    if (feedback) {
      feedback.classList.add("family-feedback-link");
      heading.append(feedback);
    }
    return heading;
  }

  function buildAtlas() {
    sections.forEach((section) => {
      const sectionNode = element("section", "atlas-section");
      sectionNode.id = `family-${section.id}`;
      sectionNode.dataset.sectionId = section.id;
      sectionNode.append(buildSectionHeading(section));
      const summary = firstRecorded(section.summary, section.chromatic_relevance, section.relevance);
      if (summary) sectionNode.append(element("p", "family-summary", summary));
      asArray(section.conceptual_space_ids).forEach((id) => {
        const space = spacesById.get(id);
        if (!space) return;
        const entry = buildEntry(space);
        entriesById.set(id, entry);
        sectionNode.append(entry);
      });
      sectionsById.set(section.id, sectionNode);
      atlasDocument.append(sectionNode);
    });

    asArray(snapshot.supported_coefficients).forEach((coefficient) => {
      const option = element("option", "", coefficientDisplay(coefficient));
      option.value = coefficient;
      coefficientFilter.append(option);
    });
    if (!coefficientFilter.options.length) {
      const option = element("option", "", coefficientDisplay("Z"));
      option.value = "Z";
      coefficientFilter.append(option);
    }
    state.coefficient = coefficientFilter.options[0]?.value ?? "Z";
    coefficientFilter.value = state.coefficient;

    const families = [...sections].sort((left, right) => left.label.localeCompare(right.label));
    families.forEach((section) => {
      const option = element("option", "", section.label);
      option.value = section.id;
      familyFilter.append(option);
    });
    const dimensions = [...new Set(conceptualSpaces.map(spaceDimension).filter(Number.isFinite))]
      .sort((left, right) => left - right);
    dimensions.forEach((dimension) => {
      const option = element("option", "", String(dimension));
      option.value = String(dimension);
      dimensionFilter.append(option);
    });
    if (conceptualSpaces.some(isInfiniteFiniteType)) {
      const option = element("option", "", "∞ / finite type");
      option.value = "finite-type";
      dimensionFilter.append(option);
    }
    const reliabilityStates = [...new Set(
      conceptualSpaces.flatMap((space) => evidenceRecords(space).map((record) => record.reliability))
        .filter((value) => typeof value === "string" && value),
    )].sort((left, right) => humanize(left).localeCompare(humanize(right)));
    reliabilityStates.forEach((reliability) => {
      const option = element("option", "", humanize(reliability));
      option.value = reliability;
      reliabilityFilter.append(option);
    });

    document.getElementById("conceptual-space-count").textContent = String(snapshot.conceptual_space_count ?? conceptualSpaces.length);
    document.getElementById("snapshot-name").textContent = snapshotReference();
    const generatedAt = document.getElementById("generated-at");
    if (snapshot.generated_at) {
      generatedAt.dateTime = snapshot.generated_at;
      generatedAt.textContent = snapshot.generated_at.replace("T", " ").replace("Z", " UTC");
    } else {
      generatedAt.textContent = "not recorded";
    }
    document.getElementById("release-status").textContent = humanize(snapshot.release_status);
    const dek = document.getElementById("snapshot-dek");
    const scopeNote = firstRecorded(snapshot.scope_note, snapshot.scope);
    if (scopeNote) dek.textContent = scopeNote;
    const eyebrow = document.getElementById("atlas-eyebrow");
    eyebrow.textContent = `Homology DB · ${humanize(snapshot.release_status)}`;
    requestSpace.href = issueUrl(
      "space-request.yml",
      `[Space request] requested from ${snapshotReference()}`,
    );
    requestSpace.setAttribute("aria-label", "Request another space (opens in a new tab)");

    const snapshotDetail = document.getElementById("snapshot-detail");
    const detailList = element("dl");
    appendDefinition(detailList, "Snapshot ID", snapshot.snapshot_id);
    appendDefinition(detailList, "Read model", snapshot.schema_version);
    appendDefinition(detailList, "Generated", snapshot.generated_at);
    appendDefinition(detailList, "Materialized through", snapshot.materialized_through_degree);
    appendDefinition(detailList, "Database bytes", Number.isFinite(snapshot.source_database_bytes) ? snapshot.source_database_bytes.toLocaleString() : undefined);
    appendDefinition(detailList, "Database SHA-256", snapshot.source_database_sha256);
    appendDefinition(detailList, "Source commit", snapshot.source_commit);
    appendDefinition(detailList, "Source input SHA-256", snapshot.source_inputs_sha256);
    appendDefinition(detailList, "Source tree", snapshot.source_tree_state);
    appendDefinition(detailList, "Release state", humanize(snapshot.release_status));
    snapshotDetail.append(detailList);
  }

  function hasIntegralTorsion(space) {
    return asArray(space.homology).some((row) =>
      row.coefficient_ring === "Z" && !row.reduced && row.group.state === "exact" && row.group.torsion_orders?.length
    );
  }

  function updateControlSummary() {
    const count = [
      state.family,
      state.dimension,
      state.reliability,
      state.reduced,
      state.torsion,
    ].filter(Boolean).length;
    activeFilterCount.textContent = String(count);
    activeFilterCount.setAttribute(
      "aria-label",
      count === 0 ? "No active filters" : `${count} active filter${count === 1 ? "" : "s"}`,
    );
    const defaultCoefficient = coefficientFilter.options[0]?.value ?? "Z";
    clearFilters.hidden = !(
      state.query
      || state.coefficient !== defaultCoefficient
      || count > 0
    );
  }

  function renderIndex(visibleWithRank) {
    const counts = new Map(sections.map((section) => [section.id, 0]));
    visibleWithRank.forEach(({ space }) => counts.set(space.taxonomy.family, (counts.get(space.taxonomy.family) ?? 0) + 1));
    spaceIndexCount.textContent = String(visibleWithRank.length);
    if (state.query.trim()) spaceIndexDisclosure.open = true;
    sectionIndex.replaceChildren();
    sections.forEach((section) => {
      const button = element("button", "index-link");
      button.type = "button";
      button.disabled = counts.get(section.id) === 0;
      button.append(element("span", "", section.label), element("span", "", String(counts.get(section.id) ?? 0)));
      button.addEventListener("click", () => {
        const destination = sectionsById.get(section.id);
        closeIndex();
        destination?.scrollIntoView({ block: "start" });
        const heading = destination?.querySelector("h2");
        if (heading) {
          heading.tabIndex = -1;
          heading.focus({ preventScroll: true });
        }
      });
      sectionIndex.append(button);
    });

    spaceIndex.replaceChildren();
    visibleWithRank
      .slice()
      .sort((left, right) => left.rank - right.rank || left.space.name.plain.localeCompare(right.space.name.plain))
      .forEach(({ space }) => {
        const item = element("li");
        const link = element("a", "", space.name.plain);
        link.href = `#space=${encodeURIComponent(space.slug)}`;
        if (state.selectedId === space.id) link.setAttribute("aria-current", "true");
        link.addEventListener("click", () => {
          closeIndex();
          window.setTimeout(() => {
            const heading = entriesById.get(space.id)?.querySelector(".entry-title");
            if (heading) {
              heading.tabIndex = -1;
              heading.focus({ preventScroll: true });
            }
          }, 0);
        });
        item.append(link);
        spaceIndex.append(item);
      });
  }

  function updateAtlas() {
    const eligibleWithRank = conceptualSpaces.map((space) => ({
      space,
      rank: searchRank(space, state.query),
    })).filter(({ space, rank }) => {
      if (!Number.isFinite(rank)) return false;
      if (state.family && space.taxonomy.family !== state.family) return false;
      if (state.dimension === "finite-type" && !isInfiniteFiniteType(space)) return false;
      if (state.dimension !== "" && state.dimension !== "finite-type" && String(spaceDimension(space)) !== state.dimension) return false;
      if (state.reliability && !evidenceRecords(space).some((record) => record.reliability === state.reliability)) return false;
      if (state.torsion && !hasIntegralTorsion(space)) return false;
      return true;
    });
    const bestRank = state.query.trim() && eligibleWithRank.length
      ? Math.min(...eligibleWithRank.map(({ rank }) => rank))
      : null;
    const visibleWithRank = bestRank === null
      ? eligibleWithRank
      : eligibleWithRank.filter(({ rank }) => rank === bestRank);
    state.visible = visibleWithRank
      .slice()
      .sort((left, right) => left.rank - right.rank || left.space.name.plain.localeCompare(right.space.name.plain))
      .map(({ space }) => space.id);

    const visibleIds = new Set(state.visible);
    entriesById.forEach((entry, id) => {
      entry.hidden = !visibleIds.has(id);
      renderHomology(spacesById.get(id), entry);
    });
    sections.forEach((section) => {
      const visibleCount = asArray(section.conceptual_space_ids).filter((id) => visibleIds.has(id)).length;
      const sectionNode = sectionsById.get(section.id);
      sectionNode.hidden = visibleCount === 0;
      sectionNode.querySelector(".section-count").textContent = String(visibleCount);
    });
    document.querySelectorAll("details[data-review-detail]").forEach((details) => {
      details.open = state.review && !details.closest("article").hidden;
    });
    resultStatus.textContent = `${state.visible.length} of ${snapshot.conceptual_space_count ?? conceptualSpaces.length}`;
    updateControlSummary();
    renderIndex(visibleWithRank);
  }

  function setSelected(id, shouldScroll = true) {
    selectionTimers.forEach((timer) => window.clearTimeout(timer));
    selectionTimers.clear();
    entriesById.forEach((entry) => entry.classList.remove("is-selected"));
    state.selectedId = id;
    if (!id) return;
    const entry = entriesById.get(id);
    if (entry && !entry.hidden) {
      entry.classList.add("is-selected");
      if (shouldScroll) entry.scrollIntoView({ block: "start" });
      const timer = window.setTimeout(() => entry.classList.remove("is-selected"), 1800);
      selectionTimers.set(id, timer);
    }
    renderIndex(state.visible.map((visibleId) => ({ space: spacesById.get(visibleId), rank: searchRank(spacesById.get(visibleId), state.query) })));
  }

  function spaceFromHash() {
    const match = window.location.hash.match(/^#space=(.+)$/);
    if (!match) return null;
    let slug;
    try { slug = decodeURIComponent(match[1]); } catch (_error) { return null; }
    return conceptualSpaces.find((space) => space.slug === slug) ?? null;
  }

  function handleHash() {
    const space = spaceFromHash();
    if (!space) return;
    if (entriesById.get(space.id)?.hidden) {
      searchInput.value = "";
      familyFilter.value = "";
      dimensionFilter.value = "";
      reliabilityFilter.value = "";
      torsionFilter.checked = false;
      state.query = state.family = state.dimension = state.reliability = "";
      state.torsion = false;
      updateAtlas();
    }
    window.requestAnimationFrame(() => setSelected(space.id));
  }

  function navigateTo(id) {
    const space = spacesById.get(id);
    if (!space) return;
    window.location.hash = `space=${encodeURIComponent(space.slug)}`;
    if (spaceFromHash()?.id === id) setSelected(id);
  }

  function syncIndexAccessibility() {
    if (!narrowIndexMedia.matches) {
      atlasIndex.classList.remove("is-open");
      atlasIndex.inert = false;
      atlasIndex.removeAttribute("aria-hidden");
      atlasIndex.removeAttribute("aria-modal");
      atlasIndex.removeAttribute("role");
      backgroundInertTargets.forEach((target) => { target.inert = false; });
      indexBackdrop.hidden = true;
      document.body.classList.remove("index-open");
      indexToggle.setAttribute("aria-expanded", "false");
      return;
    }
    const open = atlasIndex.classList.contains("is-open");
    atlasIndex.inert = !open;
    atlasIndex.setAttribute("aria-hidden", String(!open));
    atlasIndex.setAttribute("role", "dialog");
    atlasIndex.setAttribute("aria-modal", String(open));
    backgroundInertTargets.forEach((target) => { target.inert = open; });
    indexBackdrop.hidden = !open;
    document.body.classList.toggle("index-open", open);
    indexToggle.setAttribute("aria-expanded", String(open));
  }

  function openIndex({ focusClose = true, returnFocus = indexToggle } = {}) {
    if (!narrowIndexMedia.matches) return;
    indexReturnFocus = returnFocus;
    atlasIndex.classList.add("is-open");
    syncIndexAccessibility();
    if (focusClose) window.requestAnimationFrame(() => indexClose.focus());
  }

  function closeIndex(returnFocus = false) {
    atlasIndex.classList.remove("is-open");
    if (narrowIndexMedia.matches) snapshotAbout.open = false;
    syncIndexAccessibility();
    if (returnFocus && narrowIndexMedia.matches) indexReturnFocus.focus();
  }

  function clearAllFilters() {
    searchInput.value = "";
    coefficientFilter.value = coefficientFilter.options[0]?.value ?? "Z";
    reducedFilter.checked = false;
    familyFilter.value = "";
    dimensionFilter.value = "";
    reliabilityFilter.value = "";
    torsionFilter.checked = false;
    Object.assign(state, {
      query: "",
      coefficient: coefficientFilter.value,
      reduced: false,
      family: "",
      dimension: "",
      reliability: "",
      torsion: false,
    });
    filterDisclosure.open = false;
    updateAtlas();
    searchInput.focus();
  }

  atlasControls.addEventListener("submit", (event) => event.preventDefault());
  searchInput.addEventListener("input", () => { state.query = searchInput.value; updateAtlas(); });
  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && state.visible.length) {
      event.preventDefault();
      navigateTo(state.visible[0]);
    }
  });
  coefficientFilter.addEventListener("change", () => { state.coefficient = coefficientFilter.value; updateAtlas(); });
  reducedFilter.addEventListener("change", () => { state.reduced = reducedFilter.checked; updateAtlas(); });
  familyFilter.addEventListener("change", () => { state.family = familyFilter.value; updateAtlas(); });
  dimensionFilter.addEventListener("change", () => { state.dimension = dimensionFilter.value; updateAtlas(); });
  reliabilityFilter.addEventListener("change", () => { state.reliability = reliabilityFilter.value; updateAtlas(); });
  torsionFilter.addEventListener("change", () => { state.torsion = torsionFilter.checked; updateAtlas(); });
  themeSelect.addEventListener("change", () => applyThemePreference(themeSelect.value));
  clearFilters.addEventListener("click", clearAllFilters);
  indexToggle.addEventListener("click", () => {
    if (atlasIndex.classList.contains("is-open")) closeIndex(true);
    else openIndex();
  });
  indexClose.addEventListener("click", () => closeIndex(true));
  indexBackdrop.addEventListener("click", () => closeIndex(true));
  aboutToggle.addEventListener("click", () => {
    snapshotAbout.open = !snapshotAbout.open;
    aboutToggle.setAttribute("aria-expanded", String(snapshotAbout.open));
    if (narrowIndexMedia.matches) {
      openIndex({ focusClose: false, returnFocus: aboutToggle });
      window.requestAnimationFrame(() => {
        snapshotAbout.scrollIntoView({ block: "nearest" });
        snapshotAbout.querySelector("summary").focus();
      });
    } else if (snapshotAbout.open) {
      snapshotAbout.scrollIntoView({ block: "nearest" });
    }
  });
  snapshotAbout.addEventListener("toggle", () => {
    aboutToggle.setAttribute("aria-expanded", String(snapshotAbout.open));
  });
  reviewToggle.addEventListener("click", () => {
    state.review = !state.review;
    document.body.classList.toggle("review-mode", state.review);
    reviewToggle.setAttribute("aria-pressed", String(state.review));
    reviewToggle.textContent = state.review ? "Hide review details" : "Review details";
    document.querySelectorAll("details[data-review-detail]").forEach((details) => {
      details.open = state.review && !details.closest("article").hidden;
    });
  });
  window.addEventListener("hashchange", handleHash);
  window.addEventListener("storage", (event) => {
    if (event.key === themeStorageKey) applyThemePreference(event.newValue, false);
  });
  narrowIndexMedia.addEventListener("change", syncIndexAccessibility);
  document.addEventListener("click", (event) => {
    if (filterDisclosure.open && !filterDisclosure.contains(event.target)) {
      filterDisclosure.open = false;
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      if (atlasIndex.classList.contains("is-open")) closeIndex(true);
      else if (filterDisclosure.open) {
        filterDisclosure.open = false;
        filterSummary.focus();
      }
      else if (searchInput.value) {
        searchInput.value = "";
        state.query = "";
        updateAtlas();
      }
    }
  });

  applyThemePreference(storedThemePreference(), false);
  syncIndexAccessibility();
  buildAtlas();
  updateAtlas();
  handleHash();
})();
