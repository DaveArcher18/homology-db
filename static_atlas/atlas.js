(() => {
  "use strict";

  const atlas = JSON.parse(document.getElementById("atlas-data").textContent);
  const coefficientLabels = Object.freeze({
    Z: "ℤ",
    F2: "𝔽₂",
    F3: "𝔽₃",
    F5: "𝔽₅",
    F7: "𝔽₇",
  });
  const spacesById = new Map(atlas.conceptual_spaces.map((space) => [space.id, space]));
  const entriesById = new Map();
  const sectionsById = new Map();
  const selectionTimers = new Map();
  const state = {
    query: "",
    coefficient: "Z",
    reduced: false,
    family: "",
    dimension: "",
    torsion: false,
    review: false,
    visible: [],
    selectedId: null,
  };

  const searchInput = document.getElementById("atlas-search");
  const coefficientFilter = document.getElementById("coefficient-filter");
  const reducedFilter = document.getElementById("reduced-filter");
  const familyFilter = document.getElementById("family-filter");
  const dimensionFilter = document.getElementById("dimension-filter");
  const torsionFilter = document.getElementById("torsion-filter");
  const reviewToggle = document.getElementById("review-toggle");
  const aboutToggle = document.getElementById("about-toggle");
  const clearFilters = document.getElementById("clear-filters");
  const indexToggle = document.getElementById("index-toggle");
  const atlasIndex = document.getElementById("atlas-index");
  const sectionIndex = document.getElementById("section-index");
  const spaceIndex = document.getElementById("space-index");
  const atlasDocument = document.getElementById("atlas-document");
  const snapshotAbout = document.getElementById("snapshot-about");
  const resultStatus = document.getElementById("result-status");

  function element(tagName, className, text) {
    const node = document.createElement(tagName);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function appendDefinition(list, term, description) {
    list.append(element("dt", "", term), element("dd", "", description ?? "—"));
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
    return normalizedSearchSource(value)
      .split(/\s+/)
      .filter(Boolean);
  }

  function searchValues(space) {
    const relatedNames = space.relations
      .map((relation) => spacesById.get(relation.target_id)?.name.plain)
      .filter(Boolean);
    return [
      space.name.plain,
      ...space.aliases,
      space.id,
      space.slug,
      space.taxonomy.family,
      ...space.taxonomy.tags,
      ...relatedNames,
    ];
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
    return coefficientLabels[coefficient] ?? coefficient;
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
    return coefficientDisplay(fieldGroup[1])
      + (fieldGroup[2] ? superscript(fieldGroup[2]) : "");
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
    const summary = element("summary");
    summary.append(element("span", "", title), element("span", "review-label", String(count)));
    const content = element("div", "detail-content");
    details.append(summary, content);
    return { details, content };
  }

  function renderHomology(space, entry) {
    const heading = entry.querySelector(".homology-heading h3");
    const convention = entry.querySelector(".homology-convention");
    const tableBody = entry.querySelector(".homology-table tbody");
    const rows = space.homology.filter((row) =>
      row.coefficient_ring === state.coefficient && row.reduced === state.reduced
    );
    heading.textContent = `H${state.reduced ? "̃" : ""}ₙ(${space.name.plain}; ${coefficientDisplay(state.coefficient)})`;
    convention.textContent = `ordinary homology · ${state.reduced ? "reduced" : "unreduced"} · convention not recorded · ${rows[0]?.value_scope?.replaceAll("_", " ") ?? "no recorded scope"}`;
    convention.title = rows[0]?.convention_state?.replaceAll("_", " ")
      ?? "No convention identity recorded";
    tableBody.replaceChildren();
    rows.forEach((row) => {
      const tableRow = element("tr");
      const degree = element("td", "", `H${subscript(row.degree)}`);
      const group = element("td", row.group.state === "exact" ? "" : "state-nonexact", groupDisplay(row));
      const knowledge = element("td", "state-cell review-only", row.knowledge_state);
      const assertion = element("td", "assertion-cell review-only", row.assertion_id);
      tableRow.append(degree, group, knowledge, assertion);
      tableBody.append(tableRow);
    });
  }

  function buildEntry(space) {
    const entry = element("article", "atlas-entry");
    entry.id = `space-${space.slug}`;
    entry.dataset.spaceId = space.id;

    const header = element("header", "entry-header");
    const titleBlock = element("div");
    titleBlock.append(
      element("p", "entry-kicker", space.taxonomy.family.replaceAll("_", " ")),
      element("h2", "entry-title", space.name.plain),
    );
    const actions = element("div", "permalink-actions");
    const permalink = element("a", "permalink", "# permalink");
    permalink.href = `#space=${encodeURIComponent(space.slug)}`;
    const copyLink = element("button", "copy-link-button", "Copy link");
    copyLink.type = "button";
    copyLink.addEventListener("click", () => copyText(permalinkFor(space), copyLink));
    actions.append(permalink, copyLink);
    header.append(titleBlock, actions);

    const meta = element("p", "entry-meta");
    if (space.aliases.length) meta.append(element("span", "", `Aliases: ${space.aliases.join(", ")}`));
    const dimension = space.properties.find((property) => property.key === "dimension")?.value;
    meta.append(
      element("span", "", `dimension ${dimension ?? "not recorded"}`),
      element("span", "review-only", space.id),
      element("span", "review-only", space.kind),
    );

    const homology = element("section", "homology-block");
    const homologyHeading = element("div", "homology-heading");
    homologyHeading.append(element("h3"), element("span", "homology-convention"));
    const table = element("table", "homology-table");
    const caption = element("caption", "visually-hidden", `Homology groups for ${space.name.plain}`);
    const tableHead = element("thead");
    const headerRow = element("tr");
    ["Degree", "Group", "State", "Assertion ID"].forEach((label, index) => {
      headerRow.append(element("th", index > 1 ? "review-only" : "", label));
    });
    tableHead.append(headerRow);
    table.append(caption, tableHead, element("tbody"));
    homology.append(homologyHeading, table);

    const evidenceSummary = element("p", "evidence-summary");
    const reliability = space.evidence[0]?.reliability ?? "reliability not recorded";
    const evidenceKind = space.evidence[0]?.kind?.replaceAll("_", " ")
      ?? "source not recorded";
    evidenceSummary.append(
      element("strong", "", "Evidence"),
      element("span", "", evidenceKind),
      element("span", "", `${space.evidence.length} evidence record${space.evidence.length === 1 ? "" : "s"}`),
      element("span", "", `${space.computations.length} Computation run${space.computations.length === 1 ? "" : "s"}`),
      element("span", "", reliability),
      element("span", "review-only review-warning", atlas.snapshot.release_status.replaceAll("_", " ")),
    );

    const details = element("div", "entry-details");
    const modelBlock = detailsBlock("Models & constructions", space.models.length);
    modelBlock.content.append(element("p", "empty-state", "No qualified Model records are attached in this preview snapshot."));

    const relationBlock = detailsBlock("Relationships", space.relations.length, true);
    relationBlock.content.append(element("p", "empty-state", "No relationship records are present in the local preview schema."));

    const evidenceBlock = detailsBlock("Evidence", space.evidence.length, true);
    space.evidence.forEach((record) => {
      const list = element("dl", "record-list");
      appendDefinition(list, "Evidence ID", record.id);
      appendDefinition(list, "Kind", record.kind);
      appendDefinition(list, "Reliability", record.reliability ?? "Not recorded in preview schema");
      appendDefinition(list, "Release status", record.release_status);
      appendDefinition(list, "Source locator", record.locator ?? "Not recorded in preview schema");
      appendDefinition(list, "Algorithm", record.algorithm_id);
      appendDefinition(list, "Input SHA-256", record.chain_sha256);
      appendDefinition(list, "Representatives", record.representatives_state);
      appendDefinition(list, "Induced maps", record.induced_maps_state);
      appendDefinition(list, "Citation", record.citation ?? "No literature citation in this preview record");
      evidenceBlock.content.append(list);
    });

    const computationBlock = detailsBlock("Computation runs", space.computations.length, true);
    if (!space.computations.length) {
      computationBlock.content.append(element(
        "p",
        "empty-state",
        "No Computation run record exists in the preview schema. The evidence record above preserves only the algorithm ID, input hash, and capability states.",
      ));
    }

    const qualityIssueCount = space.data_quality.missing_required_fields.length
      + space.data_quality.malformed_fields.length;
    const qualityBlock = detailsBlock("Data quality", qualityIssueCount, true);
    const qualityList = element("dl", "record-list");
    appendDefinition(qualityList, "Exporter state", space.data_quality.state);
    appendDefinition(
      qualityList,
      "Missing required fields",
      space.data_quality.missing_required_fields.join(", ") || "None",
    );
    appendDefinition(
      qualityList,
      "Malformed fields",
      space.data_quality.malformed_fields.join(", ") || "None",
    );
    qualityBlock.content.append(qualityList);

    const rawBlock = detailsBlock("Raw record", 1, true);
    const rawActions = element("div", "raw-actions");
    const copyJson = element("button", "copy-button", "Copy JSON");
    copyJson.type = "button";
    copyJson.addEventListener("click", () => copyText(JSON.stringify(space.raw, null, 2), copyJson));
    const downloadJson = element("button", "download-button", "Download JSON");
    downloadJson.type = "button";
    downloadJson.addEventListener("click", () => downloadRecord(space));
    const report = element("a", "download-button", "Report data issue ↗");
    const issueTitle = encodeURIComponent(`Atlas data: ${space.id}`);
    const issueBody = encodeURIComponent(`Conceptual space: ${space.id}\nSnapshot: ${atlas.snapshot.snapshot_id}\nSource SHA-256: ${atlas.snapshot.source_database_sha256}\n\nDescribe the issue:`);
    report.href = `https://github.com/DaveArcher18/homology-db/issues/new?title=${issueTitle}&body=${issueBody}`;
    report.target = "_blank";
    report.rel = "noopener noreferrer";
    rawActions.append(copyJson, downloadJson, report);
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
    entry.append(header, meta, homology, evidenceSummary, details);
    renderHomology(space, entry);
    return entry;
  }

  function buildAtlas() {
    atlas.sections.forEach((section) => {
      const sectionNode = element("section", "atlas-section");
      sectionNode.id = `family-${section.id}`;
      sectionNode.dataset.sectionId = section.id;
      const heading = element("h2", "section-heading");
      heading.append(element("span", "section-kicker", "Family"));
      heading.append(document.createTextNode(section.label));
      heading.append(element("span", "section-count", String(section.conceptual_space_ids.length)));
      sectionNode.append(heading);
      section.conceptual_space_ids.forEach((id) => {
        const space = spacesById.get(id);
        const entry = buildEntry(space);
        entriesById.set(id, entry);
        sectionNode.append(entry);
      });
      sectionsById.set(section.id, sectionNode);
      atlasDocument.append(sectionNode);
    });

    atlas.snapshot.supported_coefficients.forEach((coefficient) => {
      const option = element("option", "", coefficientDisplay(coefficient));
      option.value = coefficient;
      coefficientFilter.append(option);
    });
    coefficientFilter.value = state.coefficient;

    const families = [...atlas.sections].sort((left, right) => left.label.localeCompare(right.label));
    families.forEach((section) => {
      const option = element("option", "", section.label);
      option.value = section.id;
      familyFilter.append(option);
    });
    const dimensions = [...new Set(atlas.conceptual_spaces.map((space) =>
      space.properties.find((property) => property.key === "dimension")?.value
    ).filter((value) => value !== undefined))].sort((left, right) => left - right);
    dimensions.forEach((dimension) => {
      const option = element("option", "", String(dimension));
      option.value = String(dimension);
      dimensionFilter.append(option);
    });

    document.getElementById("conceptual-space-count").textContent = String(atlas.snapshot.conceptual_space_count);
    document.getElementById("snapshot-name").textContent = atlas.snapshot.snapshot_id.replace("preview-", "preview · ").slice(0, 26);
    const generatedAt = document.getElementById("generated-at");
    generatedAt.dateTime = atlas.snapshot.generated_at;
    generatedAt.textContent = atlas.snapshot.generated_at.replace("T", " ").replace("Z", " UTC");
    const snapshotDetail = document.getElementById("snapshot-detail");
    const detailList = element("dl");
    appendDefinition(detailList, "Snapshot ID", atlas.snapshot.snapshot_id);
    appendDefinition(detailList, "Read model", atlas.snapshot.schema_version);
    appendDefinition(detailList, "Generated", atlas.snapshot.generated_at);
    appendDefinition(detailList, "Database bytes", atlas.snapshot.source_database_bytes.toLocaleString());
    appendDefinition(detailList, "Database SHA-256", atlas.snapshot.source_database_sha256);
    appendDefinition(detailList, "Source commit", atlas.snapshot.source_commit);
    appendDefinition(detailList, "Release state", atlas.snapshot.release_status);
    snapshotDetail.append(detailList);
  }

  function hasIntegralTorsion(space) {
    return space.homology.some((row) =>
      row.coefficient_ring === "Z" && !row.reduced && row.group.state === "exact" && row.group.torsion_orders?.length
    );
  }

  function spaceDimension(space) {
    return space.properties.find((property) => property.key === "dimension")?.value;
  }

  function renderIndex(visibleWithRank) {
    const counts = new Map(atlas.sections.map((section) => [section.id, 0]));
    visibleWithRank.forEach(({ space }) => counts.set(space.taxonomy.family, counts.get(space.taxonomy.family) + 1));
    sectionIndex.replaceChildren();
    atlas.sections.forEach((section) => {
      const button = element("button", "index-link");
      button.type = "button";
      button.disabled = counts.get(section.id) === 0;
      button.append(element("span", "", section.label), element("span", "", String(counts.get(section.id))));
      button.addEventListener("click", () => {
        sectionsById.get(section.id).scrollIntoView({ block: "start" });
        closeIndex();
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
        link.addEventListener("click", closeIndex);
        item.append(link);
        spaceIndex.append(item);
      });
  }

  function updateAtlas() {
    const visibleWithRank = atlas.conceptual_spaces.map((space) => ({
      space,
      rank: searchRank(space, state.query),
    })).filter(({ space, rank }) => {
      if (!Number.isFinite(rank)) return false;
      if (state.family && space.taxonomy.family !== state.family) return false;
      if (state.dimension !== "" && String(spaceDimension(space)) !== state.dimension) return false;
      if (state.torsion && !hasIntegralTorsion(space)) return false;
      return true;
    });
    state.visible = visibleWithRank
      .slice()
      .sort((left, right) => left.rank - right.rank || left.space.name.plain.localeCompare(right.space.name.plain))
      .map(({ space }) => space.id);

    const visibleIds = new Set(state.visible);
    entriesById.forEach((entry, id) => {
      entry.hidden = !visibleIds.has(id);
      renderHomology(spacesById.get(id), entry);
    });
    atlas.sections.forEach((section) => {
      const visibleCount = section.conceptual_space_ids.filter((id) => visibleIds.has(id)).length;
      const sectionNode = sectionsById.get(section.id);
      sectionNode.hidden = visibleCount === 0;
      sectionNode.querySelector(".section-count").textContent = String(visibleCount);
    });
    document.querySelectorAll("details[data-review-detail]").forEach((details) => {
      details.open = state.review && !details.closest("article").hidden;
    });
    resultStatus.textContent = `${state.visible.length} of ${atlas.snapshot.conceptual_space_count}`;
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
    return atlas.conceptual_spaces.find((space) => space.slug === slug) ?? null;
  }

  function handleHash() {
    const space = spaceFromHash();
    if (!space) return;
    if (entriesById.get(space.id)?.hidden) {
      searchInput.value = "";
      familyFilter.value = "";
      dimensionFilter.value = "";
      torsionFilter.checked = false;
      state.query = state.family = state.dimension = "";
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

  function moveSelection(direction) {
    if (!state.visible.length) return;
    const currentIndex = state.visible.indexOf(state.selectedId);
    const nextIndex = currentIndex < 0
      ? (direction > 0 ? 0 : state.visible.length - 1)
      : Math.max(0, Math.min(state.visible.length - 1, currentIndex + direction));
    navigateTo(state.visible[nextIndex]);
  }

  function closeIndex() {
    atlasIndex.classList.remove("is-open");
    indexToggle.setAttribute("aria-expanded", "false");
  }

  function clearAllFilters() {
    searchInput.value = "";
    coefficientFilter.value = "Z";
    reducedFilter.checked = false;
    familyFilter.value = "";
    dimensionFilter.value = "";
    torsionFilter.checked = false;
    Object.assign(state, { query: "", coefficient: "Z", reduced: false, family: "", dimension: "", torsion: false });
    updateAtlas();
    searchInput.focus();
  }

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
  torsionFilter.addEventListener("change", () => { state.torsion = torsionFilter.checked; updateAtlas(); });
  clearFilters.addEventListener("click", clearAllFilters);
  indexToggle.addEventListener("click", () => {
    const open = !atlasIndex.classList.contains("is-open");
    atlasIndex.classList.toggle("is-open", open);
    indexToggle.setAttribute("aria-expanded", String(open));
  });
  aboutToggle.addEventListener("click", () => {
    snapshotAbout.open = !snapshotAbout.open;
    aboutToggle.setAttribute("aria-expanded", String(snapshotAbout.open));
    if (window.matchMedia("(max-width: 58rem)").matches) {
      atlasIndex.classList.add("is-open");
      indexToggle.setAttribute("aria-expanded", "true");
    }
    if (snapshotAbout.open) snapshotAbout.scrollIntoView({ block: "nearest" });
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
  document.addEventListener("keydown", (event) => {
    const interactive = event.target.matches("input, select, textarea, button, a, summary");
    if (event.key === "/" && !interactive) {
      event.preventDefault();
      searchInput.focus();
      return;
    }
    if (event.key === "Escape") {
      if (atlasIndex.classList.contains("is-open")) closeIndex();
      else if (searchInput.value) {
        searchInput.value = "";
        state.query = "";
        updateAtlas();
      }
      return;
    }
    if (!interactive && (event.key === "j" || event.key === "ArrowDown")) {
      event.preventDefault();
      moveSelection(1);
    }
    if (!interactive && (event.key === "k" || event.key === "ArrowUp")) {
      event.preventDefault();
      moveSelection(-1);
    }
  });

  buildAtlas();
  updateAtlas();
  handleHash();
})();
