(() => {
  "use strict";

  const presentation = window.HomologyAtlasPresentation;
  if (!presentation) {
    throw new Error("Homology Atlas presentation helpers did not load.");
  }
  const {
    blackboardCharacters,
    coefficientDisplay,
    coefficientTex,
    coverageFor,
    coveragePresentation: pureCoveragePresentation,
    firstRecorded,
    groupPresentation,
    isSupportedTex,
    simpleTexCommands,
    texGroupCommands,
  } = presentation;
  const atlas = JSON.parse(document.getElementById("atlas-data").textContent);
  const snapshot = atlas.snapshot ?? {};
  const conceptualSpaces = Array.isArray(atlas.conceptual_spaces)
    ? atlas.conceptual_spaces
    : [];
  const sections = Array.isArray(atlas.sections) ? atlas.sections : [];
  const definitions = Array.isArray(atlas.definitions) ? atlas.definitions : [];
  const supportedCoefficients =
    Array.isArray(snapshot.supported_coefficients)
    && snapshot.supported_coefficients.length
      ? snapshot.supported_coefficients
      : ["Z"];

  const issueEndpoint = "https://github.com/DaveArcher18/homology-db/issues/new";
  const themeStorageKey = "homology-atlas-theme-v1";
  // Reviewer-only renderers stay in source for later wiring, but unfinished
  // controls and record diagnostics are not addressable in the public build.
  const reviewModeEnabled = false;
  const familySearchThreshold = 8;
  const themeLabels = Object.freeze({
    system: "System",
    light: "Light",
    dark: "Dark",
  });

  const spacesById = new Map(conceptualSpaces.map((space) => [space.id, space]));
  const spacesBySlug = new Map(
    conceptualSpaces.map((space) => [space.slug, space]),
  );
  const familiesById = new Map(sections.map((section) => [section.id, section]));
  const definitionsById = new Map(
    definitions.map((definition) => [definition.id, definition]),
  );
  const familyNavigationLinks = new Map();
  const state = {
    route: { kind: "home" },
    queriesByScope: new Map(),
    homologyViewBySpace: new Map(),
  };

  const siteBrand = document.getElementById("site-brand");
  const requestSpace = document.getElementById("request-space");
  const requestSpaceIndex = document.getElementById("request-space-index");
  const aboutToggle = document.getElementById("about-toggle");
  const themeMenu = document.getElementById("theme-menu");
  const themeSummary = themeMenu.querySelector(":scope > summary");
  const themeCurrent = themeMenu.querySelector(".theme-current");
  const themeInputs = [
    ...themeMenu.querySelectorAll('input[name="theme-preference"]'),
  ];
  const familyToggle = document.getElementById("family-toggle");
  const indexClose = document.getElementById("index-close");
  const indexBackdrop = document.getElementById("index-backdrop");
  const atlasIndex = document.getElementById("atlas-index");
  const familyOutline = document.getElementById("family-outline");
  const navHome = document.getElementById("nav-home");
  const navSpaces = document.getElementById("nav-spaces");
  const snapshotAbout = document.getElementById("snapshot-about");
  const snapshotDetail = document.getElementById("snapshot-detail");
  const atlasDocument = document.getElementById("atlas-document");
  const actionStatus = document.getElementById("action-status");
  const narrowIndexMedia = window.matchMedia("(max-width: 60rem)");
  const backgroundInertTargets = [
    siteBrand,
    requestSpace,
    aboutToggle,
    themeMenu,
    atlasDocument,
    document.querySelector(".site-footer"),
  ].filter(Boolean);

  let knowlInstance = 0;
  let indexReturnFocus = familyToggle;
  let isInitialRoute = true;

  function element(tagName, className = "", text) {
    const node = document.createElement(tagName);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function humanize(value) {
    return String(value ?? "not recorded").replaceAll("_", " ");
  }

  function displayValue(value) {
    if (value === undefined || value === null || value === "") {
      return "Not recorded";
    }
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (Array.isArray(value)) {
      return value.length ? value.map(displayValue).join(", ") : "None";
    }
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  }

  function appendDefinition(list, term, description) {
    list.append(
      element("dt", "", term),
      element("dd", "", displayValue(description)),
    );
  }

  function appendRecordedDefinition(list, term, description) {
    if (
      description === undefined
      || description === null
      || description === ""
      || (Array.isArray(description) && !description.length)
    ) {
      return;
    }
    appendDefinition(list, term, description);
  }

  function propertyValue(space, key) {
    return asArray(space.properties).find((item) => item.key === key)?.value;
  }

  function spaceDimension(space) {
    return firstRecorded(space.dimension, propertyValue(space, "dimension"));
  }

  function isInfiniteFiniteType(space) {
    return Boolean(
      firstRecorded(
        space.infinite_finite_type,
        space.raw?.subject?.infinite_finite_type,
        false,
      ),
    );
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
      if (computation?.computation_id || computation?.id) {
        records.push(computation);
      }
    });
    const seen = new Set();
    return records.filter((record) => {
      const identity =
        record.computation_id ?? record.id ?? JSON.stringify(record);
      if (seen.has(identity)) return false;
      seen.add(identity);
      return true;
    });
  }

  function citationRecords(record) {
    const references = asArray(record?.references);
    return references.length ? references : asArray(record?.citations);
  }

  function normalizedThemePreference(value) {
    return value === "light" || value === "dark" ? value : "system";
  }

  function storedThemePreference() {
    const bootPreference = normalizedThemePreference(
      document.documentElement.dataset.theme,
    );
    if (bootPreference !== "system") return bootPreference;
    try {
      return normalizedThemePreference(
        window.localStorage.getItem(themeStorageKey),
      );
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
    themeInputs.forEach((input) => {
      input.checked = input.value === preference;
    });
    themeCurrent.textContent = themeLabels[preference];
    themeSummary.setAttribute(
      "aria-label",
      `Theme: ${themeLabels[preference]}`,
    );
    if (!persist) return;
    try {
      if (preference === "system") {
        window.localStorage.removeItem(themeStorageKey);
      } else {
        window.localStorage.setItem(themeStorageKey, preference);
      }
    } catch (_error) {
      // Theme storage is optional for the self-contained file.
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
      .replace(/\\(?:mathbb|mathrm|operatorname)/g, "")
      .replace(/[\\{}_^.,;:()[\]/\-]+/g, " ")
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

  function searchValues(space) {
    const family = familiesById.get(space.taxonomy?.family);
    const relatedNames = asArray(space.relations)
      .map((relation) => spacesById.get(relation.target_id)?.name?.plain)
      .filter(Boolean);
    return [
      space.name?.plain,
      space.name?.tex,
      ...asArray(space.aliases),
      space.id,
      space.slug,
      family?.id,
      family?.label,
      family?.summary,
      family?.chromatic_relevance,
      ...asArray(space.taxonomy?.tags),
      ...relatedNames,
      ...searchTextValues({
        summary: space.summary,
        relevance: space.chromatic_relevance,
        parameters: space.parameters,
        properties: space.properties,
        models: modelRecords(space),
        evidence: evidenceRecords(space),
      }),
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
    if (
      queryTokens.length
      && queryTokens.every((token) => joined.includes(token))
    ) {
      return 2;
    }
    if (compactValues.some((value) => value.includes(compactQuery))) return 3;
    return Number.POSITIVE_INFINITY;
  }

  function renderTex(tex, fallback, className = "math-display") {
    const math = element("span", className);
    math.dataset.tex = String(tex ?? "");
    math.setAttribute("aria-label", fallback);
    const visual = element("span", "math-visual");
    visual.setAttribute("aria-hidden", "true");
    math.append(visual);

    function grouped(source, start) {
      if (source[start] !== "{") throw new Error("Expected TeX group");
      let depth = 0;
      for (let index = start; index < source.length; index += 1) {
        if (source[index] === "{") depth += 1;
        if (source[index] === "}") {
          depth -= 1;
          if (depth === 0) {
            return {
              content: source.slice(start + 1, index),
              end: index + 1,
            };
          }
        }
      }
      throw new Error("Unclosed TeX group");
    }

    function appendSequence(target, source) {
      let index = 0;
      while (index < source.length) {
        const character = source[index];
        if (character === "\\") {
          const commandMatch = source.slice(index + 1).match(/^[A-Za-z]+/);
          if (!commandMatch) throw new Error("Malformed TeX command");
          const command = commandMatch[0];
          index += command.length + 1;
          if (simpleTexCommands[command]) {
            target.append(document.createTextNode(simpleTexCommands[command]));
            continue;
          }
          if (!texGroupCommands.has(command)) {
            throw new Error(`Unsupported TeX command: ${command}`);
          }
          const group = grouped(source, index);
          index = group.end;
          if (command === "mathbb") {
            const converted = [...group.content]
              .map((item) => blackboardCharacters[item] ?? item)
              .join("");
            target.append(document.createTextNode(converted));
            continue;
          }
          const wrapper = element(
            "span",
            command === "widetilde" ? "tex-widetilde" : `tex-${command}`,
          );
          appendSequence(wrapper, group.content);
          target.append(wrapper);
          continue;
        }
        if (character === "^" || character === "_") {
          const script = character === "^" ? element("sup") : element("sub");
          index += 1;
          if (source[index] === "{") {
            const group = grouped(source, index);
            appendSequence(script, group.content);
            index = group.end;
          } else {
            if (index >= source.length) throw new Error("Missing TeX script");
            script.textContent = source[index];
            index += 1;
          }
          target.append(script);
          continue;
        }
        if (character === "{") {
          const group = grouped(source, index);
          appendSequence(target, group.content);
          index = group.end;
          continue;
        }
        if (character === "}") throw new Error("Unexpected TeX brace");
        target.append(document.createTextNode(character));
        index += 1;
      }
    }

    try {
      const source = String(tex ?? "");
      if (!isSupportedTex(source)) {
        throw new Error("Unsafe or empty TeX");
      }
      appendSequence(visual, source);
    } catch (_error) {
      visual.replaceChildren(document.createTextNode(fallback));
      math.classList.add("math-fallback");
    }
    return math;
  }

  function mathName(space, className = "math-display") {
    return renderTex(
      space.name?.tex,
      space.name?.plain ?? space.id,
      className,
    );
  }

  function coveragePresentation(space, rows) {
    return pureCoveragePresentation(space, rows, snapshot);
  }

  function buildCoverageBadge(space, rows, { withDefinitions = false } = {}) {
    const presentation = coveragePresentation(space, rows);
    const wrapper = element(
      "div",
      `coverage-summary ${presentation.className}`,
    );
    wrapper.append(
      element(
        "span",
        `coverage-badge ${presentation.className}`,
        presentation.label,
      ),
      element("p", "coverage-detail", presentation.detail),
    );
    if (withDefinitions) {
      const definitionsLine = element("p", "coverage-definitions");
      definitionsLine.append(buildKnowl("coverage", "Coverage definition"));
      if (coverageFor(space).kind === "complete_finite_cw") {
        definitionsLine.append(
          document.createTextNode(" · "),
          buildKnowl("finite-cw-space", "Finite CW space"),
        );
      }
      wrapper.append(definitionsLine);
    }
    return wrapper;
  }

  function availableCoefficients(space) {
    const recorded = new Set(
      asArray(space.homology).map((row) => row.coefficient_ring),
    );
    const ordered = supportedCoefficients.filter((item) => recorded.has(item));
    return ordered.length ? ordered : [...recorded];
  }

  function homologyViewFor(space) {
    if (!state.homologyViewBySpace.has(space.id)) {
      const coefficients = availableCoefficients(space);
      const coefficient = coefficients.includes("Z")
        ? "Z"
        : coefficients[0] ?? "Z";
      state.homologyViewBySpace.set(space.id, {
        coefficient,
        reduced: false,
      });
    }
    return state.homologyViewBySpace.get(space.id);
  }

  function homologyRows(space, view = homologyViewFor(space)) {
    return asArray(space.homology).filter(
      (row) =>
        row.coefficient_ring === view.coefficient
        && row.reduced === view.reduced,
    );
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
    const safeHref = safeHttpsUrl(href);
    if (!safeHref) return null;
    const link = element("a", "external-link", label);
    link.href = safeHref;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    if (accessibleContext) {
      link.setAttribute(
        "aria-label",
        `${accessibleContext} (opens in a new tab)`,
      );
    }
    return link;
  }

  function snapshotReference() {
    return firstRecorded(
      snapshot.snapshot_id,
      snapshot.snapshot_name,
      "unknown-snapshot",
    );
  }

  function snapshotIssueReference() {
    const hash = firstRecorded(
      snapshot.source_database_sha256,
      snapshot.source_inputs_sha256,
    );
    return hash
      ? `${snapshotReference()} | sha256:${hash}`
      : snapshotReference();
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
      `[Space feedback] ${space.name?.plain ?? space.id} | ${space.id} | ${snapshotIssueReference()}`,
    );
  }

  function familyFeedbackUrl(section) {
    return issueUrl(
      "family-feedback.yml",
      `[Family feedback] ${section.label} | ${section.id} | ${snapshotIssueReference()}`,
    );
  }

  function requestSpaceUrl() {
    return issueUrl(
      "space-request.yml",
      `[Space request] ${snapshotIssueReference()}`,
    );
  }

  function permalinkFor(space) {
    const url = new URL(window.location.href);
    url.hash = `space=${encodeURIComponent(space.slug)}`;
    return url.href;
  }

  function serializedSpaceRecord(space) {
    return JSON.stringify(space, null, 2);
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
    window.setTimeout(() => {
      button.textContent = previous;
    }, 1400);
  }

  function downloadRecord(space) {
    const blob = new Blob([serializedSpaceRecord(space)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${space.slug}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function buildKnowl(definitionId, label) {
    const definition = definitionsById.get(definitionId);
    if (!definition) return document.createTextNode(label ?? humanize(definitionId));
    knowlInstance += 1;
    const instance = `knowl-${definition.id}-${knowlInstance}`;
    const trigger = element(
      "button",
      "knowl-trigger knowl-button",
      label ?? definition.term,
    );
    trigger.type = "button";
    trigger.id = `${instance}-trigger`;
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-controls", `${instance}-panel`);
    const panel = element("span", "knowl-panel");
    panel.id = `${instance}-panel`;
    panel.hidden = true;
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-labelledby", trigger.id);
    panel.append(
      element("strong", "knowl-term", definition.term),
      document.createTextNode(` ${definition.body} `),
      element(
        "span",
        "knowl-status",
        definition.assertion_evidence
          ? "Assertion evidence"
          : (
            `Definition ${definition.id} r${definition.revision}`
            + ` · selected for Snapshot ${definition.selected_for_snapshot_id}`
            + " · exposition, not assertion evidence"
          ),
      ),
    );
    trigger.addEventListener("click", () => {
      const expanded = trigger.getAttribute("aria-expanded") === "true";
      trigger.setAttribute("aria-expanded", String(!expanded));
      panel.hidden = expanded;
    });
    const wrapper = element("span", "knowl");
    wrapper.append(trigger, panel);
    return wrapper;
  }

  function buildBreadcrumbs(items) {
    const nav = element("nav", "breadcrumbs");
    nav.setAttribute("aria-label", "Breadcrumb");
    const list = element("ol");
    items.forEach((item, index) => {
      const listItem = element("li");
      if (item.href && index < items.length - 1) {
        const link = element("a", "", item.label);
        link.href = item.href;
        listItem.append(link);
      } else {
        const current = element("span", "", item.label);
        if (index === items.length - 1) {
          current.setAttribute("aria-current", "page");
        }
        listItem.append(current);
      }
      list.append(listItem);
    });
    nav.append(list);
    return nav;
  }

  function pageHeader(title, eyebrow, description) {
    const header = element("header", "page-header");
    if (eyebrow) header.append(element("p", "page-kicker", eyebrow));
    header.append(element("h1", "page-title", title));
    if (description) header.append(element("p", "page-lede", description));
    return header;
  }

  function familyFor(space) {
    return familiesById.get(space.taxonomy?.family);
  }

  function memberMeta(space) {
    const dimension = spaceDimension(space);
    if (isInfiniteFiniteType(space)) return "Infinite dimensional · finite type";
    return dimension === undefined || dimension === null
      ? "Dimension not recorded"
      : `Dimension ${dimension}`;
  }

  function buildSpaceResultItem(space, { showFamily = true } = {}) {
    const family = familyFor(space);
    const item = element("li", "space-result space-list-item");
    const main = element("div", "space-list-main");
    const primary = element("a", "space-result-link");
    primary.href = `#space=${encodeURIComponent(space.slug)}`;
    primary.append(mathName(space, "space-result-math"));
    const plainName = element("span", "space-result-plain", space.name?.plain);
    plainName.setAttribute("aria-hidden", "true");
    primary.append(plainName);
    const meta = element("p", "space-result-meta");
    if (family && showFamily) {
      const familyLink = element("a", "family-inline-link", family.label);
      familyLink.href = `#family-${family.id}`;
      meta.append(familyLink, document.createTextNode(" · "));
    }
    meta.append(document.createTextNode(memberMeta(space)));
    main.append(primary, meta);
    item.append(main);
    return item;
  }

  function rankedSpaces(spaces, query) {
    const ranked = spaces
      .map((space) => ({ space, rank: searchRank(space, query) }))
      .filter((item) => Number.isFinite(item.rank));
    if (!query.trim()) {
      return ranked
        .map((item) => item.space)
        .sort((left, right) =>
          left.name.plain.localeCompare(right.name.plain),
        );
    }
    return ranked
      .sort(
        (left, right) =>
          left.rank - right.rank
          || left.space.name.plain.localeCompare(right.space.name.plain),
      )
      .map((item) => item.space);
  }

  function buildSpaceSearch(
    spaces,
    scopeKey,
    label,
    { showAllOnEmpty = true } = {},
  ) {
    const section = element("section", "space-search-section");
    const form = element("form", "space-search directory-tools");
    form.setAttribute("role", "search");
    const inputId = `search-${scopeKey}`;
    const statusId = `search-status-${scopeKey}`;
    const inputLabel = element("label", "search-label search-control");
    inputLabel.htmlFor = inputId;
    inputLabel.append(element("span", "search-label-text", label));
    const searchWrap = element("span", "route-search-wrap search-wrap");
    const input = element("input");
    input.id = inputId;
    input.type = "search";
    input.autocomplete = "off";
    input.placeholder =
      scopeKey === "spaces"
        ? "Try “sphere”, “torsion”, or “B(C₂)”"
        : "Search names, parameters, and aliases";
    input.value = state.queriesByScope.get(scopeKey) ?? "";
    input.setAttribute("aria-describedby", statusId);
    const searchMark = element("span", "route-search-mark search-mark");
    searchMark.setAttribute("aria-hidden", "true");
    searchWrap.append(searchMark, input);
    inputLabel.append(searchWrap);
    const status = element("output", "search-status directory-status");
    status.id = statusId;
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const results = element("ol", "space-results space-list");

    function renderResults() {
      const query = input.value;
      state.queriesByScope.set(scopeKey, query);
      const matches = rankedSpaces(spaces, query);
      const visibleMatches =
        (query.trim() || showAllOnEmpty) ? matches : [];
      results.replaceChildren();
      visibleMatches.forEach((space) =>
        results.append(buildSpaceResultItem(space)),
      );
      status.textContent = query.trim()
        ? `${matches.length} match${matches.length === 1 ? "" : "es"}`
        : (
          showAllOnEmpty
            ? `${matches.length} space${matches.length === 1 ? "" : "s"}`
            : `Search ${matches.length} spaces by name, family, or alias.`
        );
      if (query.trim() && !matches.length) {
        results.append(
          element(
            "li",
            "empty-state",
            "No spaces match this search. Try a family name, alias, or parameter.",
          ),
        );
      }
    }

    form.addEventListener("submit", (event) => event.preventDefault());
    input.addEventListener("input", renderResults);
    input.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && input.value) {
        input.value = "";
        renderResults();
        return;
      }
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        const links = [...results.querySelectorAll(".space-result-link")];
        if (!links.length) return;
        event.preventDefault();
        const target = event.key === "ArrowDown" ? links[0] : links.at(-1);
        target.focus();
      }
    });
    results.addEventListener("keydown", (event) => {
      const activeLink = event.target.closest(".space-result-link");
      if (!activeLink) return;
      const previous = event.key === "ArrowUp" || event.key === "k";
      const next = event.key === "ArrowDown" || event.key === "j";
      if (!previous && !next) return;
      const links = [...results.querySelectorAll(".space-result-link")];
      const current = links.indexOf(activeLink);
      if (current < 0) return;
      event.preventDefault();
      const target = previous
        ? links[Math.max(0, current - 1)]
        : links[Math.min(links.length - 1, current + 1)];
      target.focus();
    });
    form.append(inputLabel, status);
    section.append(form, results);
    renderResults();
    return section;
  }

  function buildFamilyDirectory(limit = sections.length) {
    const list = element("ol", "family-directory");
    sections.slice(0, limit).forEach((section) => {
      const item = element("li", "family-directory-item");
      const heading = element("div", "family-directory-heading");
      const link = element("a", "family-directory-link", section.label);
      link.href = `#family-${section.id}`;
      heading.append(
        link,
        element(
          "span",
          "family-count",
          `${asArray(section.conceptual_space_ids).length}`,
        ),
      );
      item.append(heading);
      list.append(item);
    });
    return list;
  }

  function buildHomeView() {
    const view = element("article", "route-view home-view");
    const hero = element("section", "home-hero");
    const heroCopy = element("div", "home-hero-copy");
    heroCopy.append(
      element("p", "page-kicker", "An atlas of computed examples"),
      element("h1", "page-title", "Homology, space by space"),
      element(
        "p",
        "home-intro page-lede",
        "Browse ordinary homology, concrete models, and provenance for a focused collection of familiar spaces.",
      ),
    );
    const actions = element("div", "hero-actions");
    const explore = element("a", "primary-action", "Explore spaces");
    explore.href = "#spaces";
    actions.append(explore);
    heroCopy.append(actions);
    hero.append(heroCopy);

    const familySection = element("section", "home-families home-section");
    const familyHeading = element("div", "section-heading");
    familyHeading.append(
      element("div", "", ""),
    );
    familyHeading.firstElementChild.append(
      element("p", "section-kicker", "Start with a family"),
      element("h2", "", "Browse familiar families"),
    );
    const allFamilies = element("a", "text-link", "See every family");
    allFamilies.href = "#spaces";
    familyHeading.append(allFamilies);
    familySection.append(familyHeading, buildFamilyDirectory(6));
    view.append(hero, familySection);
    return view;
  }

  function buildSpacesView() {
    const view = element("article", "route-view spaces-view");
    view.append(
      buildBreadcrumbs([
        { label: "Home", href: "#home" },
        { label: "Spaces" },
      ]),
      pageHeader(
        "Spaces",
        `${conceptualSpaces.length} conceptual spaces in ${sections.length} families`,
        "Browse by mathematical family or search the whole snapshot. Each result opens a focused page for one space.",
      ),
    );

    const allSpaces = element("section", "all-spaces-section");
    allSpaces.append(
      element("h2", "", "All spaces"),
      buildSpaceSearch(
        conceptualSpaces,
        "spaces",
        "Search all spaces",
        { showAllOnEmpty: false },
      ),
    );
    const directory = element("section", "directory-section");
    directory.append(
      element("h2", "", "Browse by family"),
      buildFamilyDirectory(),
    );
    view.append(allSpaces, directory);
    return view;
  }

  function buildFamilyView(section) {
    const members = asArray(section.conceptual_space_ids)
      .map((id) => spacesById.get(id))
      .filter(Boolean);
    const view = element("article", "route-view family-view family-page");
    view.append(
      buildBreadcrumbs([
        { label: "Home", href: "#home" },
        { label: "Spaces", href: "#spaces" },
        { label: section.label },
      ]),
    );
    const familyIntroduction = [
      section.summary,
      section.chromatic_relevance ?? section.relevance,
    ].filter(Boolean).join(" ");
    const header = pageHeader(
      section.label,
      `${members.length} space${members.length === 1 ? "" : "s"} in this snapshot`,
      familyIntroduction,
    );
    const feedback = outboundLink(
      "Correct or improve this family ↗",
      familyFeedbackUrl(section),
      `Give feedback on ${section.label}`,
    );
    if (feedback) {
      feedback.classList.add("feedback-action");
      header.append(feedback);
    }
    view.append(header);

    const browse = element("section", "family-members-section home-section");
    browse.append(element("h2", "", `Spaces in ${section.label}`));
    if (members.length > familySearchThreshold) {
      browse.append(
        buildSpaceSearch(
          members,
          `family-${section.id}`,
          "Search this family",
        ),
      );
    } else {
      const memberList = element("ol", "space-results space-list");
      members.forEach((space) =>
        memberList.append(buildSpaceResultItem(space, { showFamily: false })),
      );
      browse.append(memberList);
    }
    view.append(browse);
    return view;
  }

  function buildHomologyControls(space, host) {
    const controls = element(
      "div",
      "homology-controls coefficient-controls local-homology-controls",
    );
    const view = homologyViewFor(space);
    const coefficientFieldset = element(
      "fieldset",
      "space-coefficients segmented-fieldset segmented-control-group",
    );
    coefficientFieldset.append(element("legend", "", "Coefficient ring"));
    const coefficientOptions = element(
      "div",
      "segment-options segmented-control",
    );
    availableCoefficients(space).forEach((coefficient) => {
      const option = element("label", "segment-option");
      const input = element("input");
      input.type = "radio";
      input.name = `coefficient-${space.slug}`;
      input.value = coefficient;
      input.checked = coefficient === view.coefficient;
      option.append(
        input,
        element("span", "", coefficientDisplay(coefficient)),
      );
      coefficientOptions.append(option);
    });
    coefficientFieldset.append(coefficientOptions);

    const conventionFieldset = element(
      "fieldset",
      "space-convention segmented-fieldset segmented-control-group",
    );
    conventionFieldset.append(element("legend", "", "Homology convention"));
    const conventionOptions = element(
      "div",
      "segment-options segmented-control",
    );
    [
      [false, "Unreduced"],
      [true, "Reduced"],
    ].forEach(([reduced, label]) => {
      const option = element("label", "segment-option");
      const input = element("input");
      input.type = "radio";
      input.name = `convention-${space.slug}`;
      input.value = String(reduced);
      input.checked = reduced === view.reduced;
      option.append(input, element("span", "", label));
      conventionOptions.append(option);
    });
    conventionFieldset.append(conventionOptions);
    const conventionHelp = element("p", "control-help");
    conventionHelp.append(
      buildKnowl("reduced-homology", "Reduced versus unreduced"),
    );
    conventionFieldset.append(conventionHelp);

    controls.addEventListener("change", (event) => {
      if (!(event.target instanceof HTMLInputElement)) return;
      const current = homologyViewFor(space);
      if (event.target.name === `coefficient-${space.slug}`) {
        current.coefficient = event.target.value;
      }
      if (event.target.name === `convention-${space.slug}`) {
        current.reduced = event.target.value === "true";
      }
      renderHomology(space, host);
      announce(
        `${space.name.plain}: ${current.reduced ? "reduced" : "unreduced"} homology with ${coefficientDisplay(current.coefficient)} coefficients.`,
      );
    });
    controls.append(coefficientFieldset, conventionFieldset);
    return controls;
  }

  function hasRepeatedSummand(rows) {
    return rows.some((row) => {
      if ((row.group?.free_rank ?? 0) > 1) return true;
      const counts = new Map();
      return asArray(row.group?.torsion_orders).some((order) => {
        const count = (counts.get(order) ?? 0) + 1;
        counts.set(order, count);
        return count > 1;
      });
    });
  }

  function renderHomology(space, host) {
    const dynamic = host.querySelector(".homology-dynamic");
    const view = homologyViewFor(space);
    const rows = homologyRows(space, view);
    const content = element("div", "homology-rendered");
    const formulaTex = `${
      view.reduced ? "\\widetilde{H}" : "H"
    }_{n}(${space.name.tex};${coefficientTex(view.coefficient)})`;
    content.append(
      renderTex(
        formulaTex,
        `${view.reduced ? "Reduced" : "Unreduced"} homology of ${space.name.plain} with ${coefficientDisplay(view.coefficient)} coefficients`,
        "homology-formula",
      ),
    );
    const convention = element(
      "p",
      "homology-convention",
      `Ordinary homology · ${view.reduced ? "reduced" : "unreduced"} · ${coefficientDisplay(view.coefficient)} coefficients`,
    );
    content.append(
      convention,
      buildCoverageBadge(space, rows),
    );
    if (reviewModeEnabled) {
      const conventionNote = element("p", "convention-note review-only");
      conventionNote.append(
        document.createTextNode("Convention metadata: "),
        document.createTextNode(
          humanize(
            rows[0]?.homology_convention
              ?? rows[0]?.convention_state
              ?? snapshot.homology_convention_state,
          ),
        ),
      );
      content.append(conventionNote);
    }
    if (hasRepeatedSummand(rows)) {
      const notation = element("p", "table-note");
      notation.append(
        buildKnowl("direct-sum-notation", "Direct-sum notation"),
      );
      content.append(notation);
    }

    const tableWrap = element("div", "homology-table-wrap");
    const table = element("table", "homology-table");
    const caption = element(
      "caption",
      "visually-hidden",
      `${view.reduced ? "Reduced" : "Unreduced"} ordinary homology groups for ${space.name.plain} with ${coefficientDisplay(view.coefficient)} coefficients`,
    );
    const head = element("thead");
    const headerRow = element("tr");
    const degreeHeader = element("th", "", "Degree");
    degreeHeader.scope = "col";
    degreeHeader.id = `table-${space.slug}-degree`;
    const groupHeader = element("th", "", "Group");
    groupHeader.scope = "col";
    groupHeader.id = `table-${space.slug}-group`;
    headerRow.append(degreeHeader, groupHeader);
    head.append(headerRow);
    const body = element("tbody");
    if (!rows.length) {
      const row = element("tr");
      const cell = element(
        "td",
        "state-nonexact",
        "No values are recorded for this coefficient and convention.",
      );
      cell.colSpan = 2;
      row.append(cell);
      body.append(row);
    } else {
      rows.forEach((row) => {
        const tableRow = element("tr");
        const degree = element("th", "degree-cell");
        degree.scope = "row";
        degree.setAttribute("headers", degreeHeader.id);
        degree.append(
          renderTex(`H_{${row.degree}}`, `Homology degree ${row.degree}`),
        );
        const groupCell = element(
          "td",
          row.group?.state === "exact" ? "group-cell" : "state-nonexact",
        );
        groupCell.setAttribute("headers", groupHeader.id);
        const presentation = groupPresentation(row);
        if (presentation.exact) {
          groupCell.append(
            renderTex(presentation.tex, presentation.plain, "group-math"),
          );
        } else {
          groupCell.textContent = presentation.plain;
        }
        const rowReview = element(
          "dl",
          "homology-row-review review-only",
        );
        appendDefinition(
          rowReview,
          "Knowledge state",
          humanize(row.knowledge_state),
        );
        appendDefinition(rowReview, "Assertion", row.assertion_id);
        appendDefinition(rowReview, "Evidence", row.evidence_ids);
        appendDefinition(rowReview, "Computation", row.computation_ids);
        appendDefinition(
          rowReview,
          "Value scope",
          humanize(row.value_scope),
        );
        groupCell.append(rowReview);
        tableRow.append(degree, groupCell);
        body.append(tableRow);
      });
    }
    table.append(caption, head, body);
    tableWrap.append(table);
    content.append(tableWrap);
    dynamic.replaceChildren(content);
  }

  function detailsBlock(title, count) {
    const details = element("details", "detail-section");
    const summary = element("summary");
    summary.append(element("span", "detail-title", title));
    if (count !== undefined) {
      summary.append(element("span", "detail-count", String(count)));
    }
    const content = element("div", "detail-content");
    details.append(summary, content);
    return { details, content };
  }

  function renderCellDescription(model) {
    const formula = firstRecorded(model.cell_formula, model.cells_formula);
    const degrees = firstRecorded(model.cell_degrees, model.cells);
    const cells = asArray(degrees)
      .map((cell) => {
        if (!cell || typeof cell !== "object") return displayValue(cell);
        const count = firstRecorded(cell.count, cell.rank, 1);
        const degree = firstRecorded(cell.degree, cell.dimension);
        return degree === undefined
          ? displayValue(cell)
          : `${count} cell${count === 1 ? "" : "s"} in degree ${degree}`;
      })
      .join("; ");
    if (formula && cells) return `${formula}; materialized cells: ${cells}`;
    return displayValue(firstRecorded(formula, cells || degrees));
  }

  function renderModels(space, content) {
    const models = modelRecords(space);
    if (!models.length) {
      content.append(
        element(
          "p",
          "empty-state",
          "No qualified Model record is attached to this snapshot.",
        ),
      );
      return;
    }
    models.forEach((model) => {
      const card = element("section", "record-section");
      card.append(
        element(
          "h3",
          "record-title",
          firstRecorded(model.name, model.model_id, model.id, "CW model"),
        ),
      );
      const list = element("dl", "record-list");
      appendDefinition(list, "Model ID", firstRecorded(model.model_id, model.id));
      appendDefinition(list, "Kind", humanize(model.kind));
      appendDefinition(list, "Status", humanize(model.status));
      appendDefinition(list, "Construction", model.construction);
      appendDefinition(list, "Cells", renderCellDescription(model));
      appendRecordedDefinition(list, "Attaching map", model.attaching_map);
      appendRecordedDefinition(list, "Cellular boundary", model.boundary_formula);
      appendRecordedDefinition(
        list,
        "Scope",
        firstRecorded(model.model_scope, model.scope),
      );
      appendRecordedDefinition(
        list,
        "Checked artifact",
        firstRecorded(model.artifact_path, model.artifact),
      );
      appendRecordedDefinition(list, "Artifact SHA-256", model.artifact_sha256);
      appendRecordedDefinition(
        list,
        "Cellular-chain SHA-256",
        firstRecorded(model.input_sha256, model.chain_sha256),
      );
      card.append(list);
      content.append(card);
    });
  }

  function citationTitle(reference) {
    if (typeof reference === "string") return reference;
    if (!reference || typeof reference !== "object") return "Untitled source";
    const authors = Array.isArray(reference.authors)
      ? reference.authors.join(", ")
      : reference.authors;
    return [authors, reference.title, reference.year]
      .filter(Boolean)
      .join(". ");
  }

  function renderCitation(reference) {
    const item = element("li", "citation-item");
    const record =
      reference && typeof reference === "object" ? reference : {};
    const title =
      citationTitle(reference)
      || firstRecorded(
        record.citation,
        record.reference_id,
        "Untitled source",
      );
    const link = outboundLink(
      `${title} ↗`,
      record.url,
      `Open source: ${title}`,
    );
    item.append(link ?? element("span", "", title));
    const context = [
      record.source_kind && humanize(record.source_kind),
      record.role && humanize(record.role),
      record.locator,
    ]
      .filter(Boolean)
      .join(" · ");
    if (context) item.append(element("span", "citation-context", context));
    return item;
  }

  function renderEvidence(space, content) {
    const records = evidenceRecords(space);
    if (!records.length) {
      content.append(
        element(
          "p",
          "empty-state",
          "No Evidence record is attached to this snapshot.",
        ),
      );
      return;
    }
    records.forEach((record) => {
      const card = element("section", "record-section");
      card.append(
        element(
          "h3",
          "record-title",
          firstRecorded(record.id, record.evidence_id, "Evidence record"),
        ),
      );
      const list = element("dl", "record-list");
      appendDefinition(list, "Kind", humanize(record.kind));
      appendDefinition(list, "Reliability", humanize(record.reliability));
      appendDefinition(
        list,
        "Release status",
        humanize(record.release_status ?? snapshot.release_status),
      );
      appendDefinition(list, "Source locator", record.locator);
      appendDefinition(list, "Algorithm", record.algorithm_id);
      appendDefinition(
        list,
        "Input SHA-256",
        firstRecorded(record.chain_sha256, record.input_sha256),
      );
      appendDefinition(
        list,
        "Representatives",
        humanize(record.representatives_state),
      );
      appendDefinition(
        list,
        "Induced maps",
        humanize(record.induced_maps_state),
      );
      card.append(list);
      const sketch = firstRecorded(
        record.computation_sketch,
        record.sketch,
      );
      if (sketch) {
        const sketchBlock = element("div", "computation-sketch");
        sketchBlock.append(
          element("h4", "", "Computation sketch"),
          element("p", "", sketch),
          element(
            "p",
            "sketch-note",
            "A mathematical sketch is evidence context; it is not itself a recorded software run.",
          ),
        );
        card.append(sketchBlock);
      }
      const references = citationRecords(record);
      if (references.length) {
        const citationHeading = element(
          "h4",
          "citation-heading",
          "Sources and locators",
        );
        const citations = element("ul", "citation-list");
        references.forEach((reference) =>
          citations.append(renderCitation(reference)),
        );
        card.append(citationHeading, citations);
      }
      content.append(card);
    });
  }

  function renderComputations(space, content) {
    const computations = computationRecords(space);
    if (!computations.length) {
      content.append(
        element(
          "p",
          "empty-state",
          "No recorded Computation run is attached. Computation sketches, when present, remain under Evidence.",
        ),
      );
      return;
    }
    computations.forEach((record) => {
      const card = element("section", "record-section");
      card.append(
        element(
          "h3",
          "record-title",
          firstRecorded(
            record.computation_id,
            record.id,
            "Recorded computation",
          ),
        ),
      );
      const list = element("dl", "record-list");
      appendDefinition(list, "Status", humanize(record.status));
      appendDefinition(list, "Algorithm", record.algorithm_id);
      appendDefinition(list, "Parameters", record.parameters);
      appendDefinition(list, "Output scope", record.output_scope);
      appendDefinition(
        list,
        "Input SHA-256",
        firstRecorded(record.input_sha256, record.chain_sha256),
      );
      card.append(list);
      content.append(card);
    });
  }

  function renderRelations(space, content) {
    const relations = asArray(space.relations);
    if (!relations.length) {
      content.append(
        element(
          "p",
          "empty-state",
          "No relationship records are attached to this snapshot.",
        ),
      );
      return;
    }
    const list = element("ul", "relation-list");
    relations.forEach((relation) => {
      const item = element("li");
      const target = spacesById.get(relation.target_id);
      item.append(
        element("span", "relation-kind", humanize(relation.type)),
        document.createTextNode(" "),
      );
      if (target) {
        const link = element("a");
        link.href = `#space=${encodeURIComponent(target.slug)}`;
        link.append(mathName(target, "relation-math"));
        item.append(link);
      } else {
        item.append(
          document.createTextNode(relation.target_id ?? "unresolved target"),
        );
      }
      if (relation.detail) {
        item.append(element("p", "relation-context", relation.detail));
      }
      list.append(item);
    });
    content.append(list);
  }

  function buildProvenanceSummary(space) {
    const evidence = evidenceRecords(space);
    const firstEvidence = evidence[0];
    const firstCitation = citationRecords(firstEvidence)[0];
    const sourceTitle =
      typeof firstCitation === "string"
        ? firstCitation
        : firstRecorded(
          firstCitation?.title,
          firstEvidence?.citation,
          "Source not recorded",
        );
    const summary = element("aside", "provenance-summary");
    summary.setAttribute("aria-label", "Provenance");
    const copy = element("div");
    const source =
      outboundLink(
        `${sourceTitle} ↗`,
        typeof firstCitation === "object" ? firstCitation?.url : null,
        `Open source: ${sourceTitle}`,
      )
      ?? element("strong", "", sourceTitle);
    copy.append(
      element("span", "provenance-label", "Source"),
      source,
      element(
        "span",
        "provenance-reliability",
        humanize(firstEvidence?.reliability ?? "reliability not recorded"),
      ),
    );
    summary.append(copy);
    return summary;
  }

  function buildClassificationBlock(space) {
    const block = detailsBlock("Classification & record", 1);
    block.details.classList.add("classification-disclosure");
    const list = element("dl", "record-list classification-record-list");
    appendDefinition(list, "Stable ID", space.id);
    appendDefinition(list, "Family", familyFor(space)?.label);
    appendDefinition(list, "Parameters", space.parameters);
    appendDefinition(
      list,
      "Tags",
      asArray(space.taxonomy?.tags).map(humanize),
    );
    appendDefinition(list, "Kind", space.kind);
    appendDefinition(list, "Data quality", space.data_quality?.state);
    appendDefinition(
      list,
      "Missing required fields",
      asArray(space.data_quality?.missing_required_fields),
    );
    block.content.append(list);
    const rawActions = element("div", "raw-actions");
    const copyJson = element("button", "text-button", "Copy JSON");
    copyJson.type = "button";
    copyJson.addEventListener("click", () =>
      copyText(serializedSpaceRecord(space), copyJson),
    );
    const downloadJson = element("button", "text-button", "Download JSON");
    downloadJson.type = "button";
    downloadJson.addEventListener("click", () => downloadRecord(space));
    rawActions.append(copyJson, downloadJson);
    const rawPre = element("pre", "raw-record");
    rawPre.setAttribute(
      "aria-label",
      `Raw JSON record for ${space.name.plain}`,
    );
    block.details.addEventListener("toggle", () => {
      if (block.details.open && !rawPre.textContent) {
        rawPre.textContent = serializedSpaceRecord(space);
      }
    });
    block.content.append(rawActions, rawPre);
    return block.details;
  }

  function buildSpaceView(space) {
    const family = familyFor(space);
    const view = element("article", "route-view space-view space-page");
    view.dataset.spaceId = space.id;
    view.append(
      buildBreadcrumbs([
        { label: "Home", href: "#home" },
        { label: "Spaces", href: "#spaces" },
        {
          label: family?.label ?? "Family",
          href: family ? `#family-${family.id}` : "#spaces",
        },
        { label: space.name.plain },
      ]),
    );

    const header = element("header", "space-header");
    const titleCopy = element("div", "space-title-copy");
    const heading = element("h1", "space-title");
    heading.append(mathName(space, "space-title-math"));
    titleCopy.append(
      heading,
      element("p", "space-plain-name", space.name.plain),
      element("p", "space-summary", space.summary),
    );
    const feedback = outboundLink(
      "Correct or improve ↗",
      spaceFeedbackUrl(space),
      `Give feedback on ${space.name.plain}`,
    );
    if (feedback) {
      feedback.classList.add("context-feedback-link");
      titleCopy.append(feedback);
    }
    let reviewToggle = null;
    header.append(titleCopy);
    if (reviewModeEnabled) {
      const actions = element("div", "space-actions permalink-actions");
      const copyLink = element("button", "text-button", "Copy link");
      copyLink.type = "button";
      copyLink.addEventListener("click", () =>
        copyText(permalinkFor(space), copyLink),
      );
      reviewToggle = element(
        "button",
        "text-button review-toggle",
        "Review details",
      );
      reviewToggle.type = "button";
      reviewToggle.setAttribute("aria-pressed", "false");
      actions.append(copyLink, reviewToggle);
      header.append(actions);
    }
    view.append(header);

    const metadata = element("dl", "space-metadata");
    const dimension = spaceDimension(space);
    const dimensionLabel = isInfiniteFiniteType(space)
      ? "Infinite dimensional · finite type"
      : (dimension ?? "Not recorded");
    const metadataItems = [
      ["Dimension", dimensionLabel],
      ["Aliases", asArray(space.aliases).join(", ") || "None recorded"],
    ];
    metadataItems.forEach(([term, description]) => {
      const item = element("div");
      item.append(
        element("dt", "", term),
        element("dd", "", description),
      );
      metadata.append(item);
    });
    view.append(metadata);

    const homology = element(
      "section",
      "homology-section space-section",
    );
    const homologyHeading = element(
      "div",
      "section-heading homology-section-heading space-section-heading",
    );
    const headingCopy = element("div");
    headingCopy.append(
      element("p", "section-kicker", "Computed invariant"),
      element("h2", "", "Homology"),
    );
    homologyHeading.append(
      headingCopy,
      buildKnowl("ordinary-homology", "Definition"),
    );
    homology.append(
      homologyHeading,
      buildHomologyControls(space, homology),
      element("div", "homology-dynamic"),
    );
    view.append(homology);
    renderHomology(space, homology);

    view.append(buildProvenanceSummary(space));
    const records = element(
      "section",
      "record-details entry-details evidence-details space-section",
    );
    records.append(element("h2", "", "Further details"));
    const modelBlock = detailsBlock("Model & sources");
    const modelDefinition = element("p", "detail-definition");
    modelDefinition.append(buildKnowl("model", "What is a Model?"));
    modelBlock.content.append(modelDefinition);
    renderModels(space, modelBlock.content);
    renderEvidence(space, modelBlock.content);
    records.append(modelBlock.details);

    const relations = asArray(space.relations);
    const relationBlock = detailsBlock("Relationships", relations.length);
    renderRelations(space, relationBlock.content);
    if (relations.length) records.append(relationBlock.details);

    if (reviewModeEnabled) {
      const reviewNote = element(
        "p",
        "review-mode-note review-only",
        "Review details include exact row states and IDs, computation metadata, data-quality fields, and the full atlas record.",
      );
      records.insertBefore(reviewNote, records.children[1] ?? null);
      const computations = computationRecords(space);
      const computationBlock = detailsBlock(
        "Computation runs",
        computations.length,
      );
      renderComputations(space, computationBlock.content);
      if (computations.length) records.append(computationBlock.details);

      const missingFields =
        asArray(space.data_quality?.missing_required_fields);
      const malformedFields = asArray(space.data_quality?.malformed_fields);
      const qualityIssueCount = missingFields.length + malformedFields.length;
      const qualityBlock = detailsBlock("Data quality", qualityIssueCount);
      const qualityList = element("dl", "record-list");
      appendDefinition(
        qualityList,
        "Exporter state",
        space.data_quality?.state,
      );
      appendRecordedDefinition(
        qualityList,
        "Missing required fields",
        missingFields,
      );
      appendRecordedDefinition(
        qualityList,
        "Malformed fields",
        malformedFields,
      );
      qualityBlock.content.append(qualityList);
      if (qualityIssueCount) records.append(qualityBlock.details);
      records.append(buildClassificationBlock(space));
    }
    view.append(records);
    reviewToggle?.addEventListener("click", () => {
      const enabled = reviewToggle.getAttribute("aria-pressed") !== "true";
      reviewToggle.setAttribute("aria-pressed", String(enabled));
      reviewToggle.textContent = enabled ? "Hide review details" : "Review details";
      view.classList.toggle("review-mode", enabled);
      records.querySelectorAll(":scope > details").forEach((details) => {
        details.open = enabled;
      });
      announce(
        enabled
          ? `Review details opened for ${space.name.plain}.`
          : `Review details closed for ${space.name.plain}.`,
      );
    });
    return view;
  }

  function buildNotFoundView(route) {
    const view = element("article", "route-view not-found-view");
    view.append(
      buildBreadcrumbs([
        { label: "Home", href: "#home" },
        { label: "Page not found" },
      ]),
      pageHeader(
        "Page not found",
        "Unknown atlas address",
        `The atlas does not contain a page for “${route.requested ?? window.location.hash}”.`,
      ),
    );
    const actions = element("div", "hero-actions");
    const home = element("a", "primary-action", "Go home");
    home.href = "#home";
    const spaces = element("a", "secondary-action", "Browse spaces");
    spaces.href = "#spaces";
    actions.append(home, spaces);
    view.append(actions);
    return view;
  }

  function parseRoute(hash = window.location.hash) {
    if (!hash || hash === "#" || hash === "#home") {
      return { kind: "home" };
    }
    if (hash === "#spaces" || hash === "#atlas-document") {
      return { kind: "spaces" };
    }
    const familyMatch = hash.match(/^#family-(.+)$/);
    if (familyMatch) {
      try {
        const id = decodeURIComponent(familyMatch[1]);
        const section = familiesById.get(id);
        return section
          ? { kind: "family", section }
          : { kind: "not-found", requested: hash };
      } catch (_error) {
        return { kind: "not-found", requested: hash };
      }
    }
    const spaceMatch = hash.match(/^#space=(.+)$/);
    if (spaceMatch) {
      try {
        const slug = decodeURIComponent(spaceMatch[1]);
        const space = spacesBySlug.get(slug);
        return space
          ? { kind: "space", space }
          : { kind: "not-found", requested: hash };
      } catch (_error) {
        return { kind: "not-found", requested: hash };
      }
    }
    return { kind: "not-found", requested: hash };
  }

  function routeTitle(route) {
    if (route.kind === "home") return "Homology Atlas";
    if (route.kind === "spaces") return "Spaces · Homology Atlas";
    if (route.kind === "family") {
      return `${route.section.label} · Homology Atlas`;
    }
    if (route.kind === "space") {
      return `${route.space.name.plain} · Homology Atlas`;
    }
    return "Page not found · Homology Atlas";
  }

  function updateNavigationCurrent(route) {
    [navHome, navSpaces, ...familyNavigationLinks.values()].forEach((link) => {
      link.removeAttribute("aria-current");
    });
    if (route.kind === "home") {
      navHome.setAttribute("aria-current", "page");
    }
    if (route.kind === "spaces") {
      navSpaces.setAttribute("aria-current", "page");
    }
    if (route.kind === "family") {
      navSpaces.setAttribute("aria-current", "location");
      familyNavigationLinks
        .get(route.section.id)
        ?.setAttribute("aria-current", "page");
    }
    if (route.kind === "space") {
      navSpaces.setAttribute("aria-current", "location");
      familyNavigationLinks
        .get(route.space.taxonomy?.family)
        ?.setAttribute("aria-current", "location");
    }
  }

  function focusRouteHeading() {
    const heading = atlasDocument.querySelector("h1");
    if (!heading) {
      atlasDocument.focus();
      return;
    }
    heading.tabIndex = -1;
    heading.focus({ preventScroll: true });
  }

  function renderRoute({ initial = false } = {}) {
    const route = parseRoute();
    state.route = route;
    let view;
    if (route.kind === "home") view = buildHomeView();
    else if (route.kind === "spaces") view = buildSpacesView();
    else if (route.kind === "family") view = buildFamilyView(route.section);
    else if (route.kind === "space") view = buildSpaceView(route.space);
    else view = buildNotFoundView(route);

    atlasDocument.replaceChildren(view);
    document.title = routeTitle(route);
    updateNavigationCurrent(route);
    closeIndex(false);
    if (!initial) {
      window.scrollTo(0, 0);
      window.requestAnimationFrame(focusRouteHeading);
      announce(
        route.kind === "space"
          ? `${route.space.name.plain} page`
          : `${view.querySelector("h1")?.textContent ?? "Atlas"} page`,
      );
    }
  }

  function buildFamilyNavigation() {
    if (!familyOutline) return;
    familyOutline.replaceChildren();
    const list = element("ol", "family-nav-list");
    sections.forEach((section) => {
      const item = element("li");
      const link = element("a", "family-nav-link");
      link.href = `#family-${section.id}`;
      link.append(
        element("span", "family-nav-label", section.label),
        element(
          "span",
          "family-nav-count",
          String(asArray(section.conceptual_space_ids).length),
        ),
      );
      familyNavigationLinks.set(section.id, link);
      item.append(link);
      list.append(item);
    });
    familyOutline.append(list);
  }

  function buildSnapshotDetail() {
    snapshotDetail.replaceChildren();
    const summary = element(
      "p",
      "",
      snapshot.scope_note ?? "No scope note is recorded.",
    );
    const facts = element("dl", "snapshot-facts");
    [
      ["Snapshot", snapshot.snapshot_name],
      ["Snapshot ID", snapshot.snapshot_id],
      ["Generated", snapshot.generated_at],
      ["Status", humanize(snapshot.release_status)],
      ["Spaces", snapshot.conceptual_space_count],
      ["Models", snapshot.model_count],
      ["Evidence records", snapshot.evidence_count],
      ["Source commit", snapshot.source_commit],
    ].forEach(([term, value]) => appendDefinition(facts, term, value));
    snapshotDetail.append(summary, facts);
  }

  function focusableWithin(container) {
    return [
      ...container.querySelectorAll(
        'a[href], button:not([disabled]), summary, input:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ),
    ].filter((node) => {
      if (node.closest("[hidden]") || node.closest("[inert]")) return false;
      if (!node.getClientRects().length) return false;
      const style = window.getComputedStyle(node);
      return style.visibility !== "hidden" && style.display !== "none";
    });
  }

  function syncIndexAccessibility() {
    const open = atlasIndex.classList.contains("is-open");
    if (!narrowIndexMedia.matches) {
      atlasIndex.classList.remove("is-open");
      atlasIndex.removeAttribute("inert");
      atlasIndex.removeAttribute("aria-hidden");
      atlasIndex.removeAttribute("aria-modal");
      atlasIndex.removeAttribute("role");
      backgroundInertTargets.forEach((target) => {
        target.removeAttribute("inert");
      });
      indexBackdrop.hidden = true;
      document.body.classList.remove("index-open");
      familyToggle.setAttribute("aria-expanded", "false");
      return;
    }
    if (!open && snapshotAbout.open) {
      snapshotAbout.open = false;
      aboutToggle.setAttribute("aria-expanded", "false");
    }
    if (open) {
      atlasIndex.removeAttribute("inert");
    } else {
      atlasIndex.setAttribute("inert", "");
    }
    atlasIndex.setAttribute("aria-hidden", String(!open));
    atlasIndex.setAttribute("role", "dialog");
    atlasIndex.setAttribute("aria-modal", String(open));
    backgroundInertTargets.forEach((target) => {
      if (open) target.setAttribute("inert", "");
      else target.removeAttribute("inert");
    });
    indexBackdrop.hidden = !open;
    document.body.classList.toggle("index-open", open);
    familyToggle.setAttribute("aria-expanded", String(open));
  }

  function openIndex({ returnFocus = familyToggle, focusClose = true } = {}) {
    if (!narrowIndexMedia.matches) return;
    indexReturnFocus = returnFocus;
    atlasIndex.classList.add("is-open");
    syncIndexAccessibility();
    if (focusClose) window.requestAnimationFrame(() => indexClose.focus());
  }

  function closeIndex(returnFocus = false) {
    const wasOpen = atlasIndex.classList.contains("is-open");
    atlasIndex.classList.remove("is-open");
    if (narrowIndexMedia.matches && snapshotAbout.open) {
      snapshotAbout.open = false;
      aboutToggle.setAttribute("aria-expanded", "false");
    }
    syncIndexAccessibility();
    if (
      returnFocus
      && wasOpen
      && narrowIndexMedia.matches
      && indexReturnFocus?.isConnected
    ) {
      indexReturnFocus.focus();
    }
  }

  function trapIndexFocus(event) {
    if (
      event.key !== "Tab"
      || !narrowIndexMedia.matches
      || !atlasIndex.classList.contains("is-open")
    ) {
      return;
    }
    const focusable = focusableWithin(atlasIndex);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (
      event.shiftKey
      && (document.activeElement === first
        || !atlasIndex.contains(document.activeElement))
    ) {
      event.preventDefault();
      last.focus();
    } else if (
      !event.shiftKey
      && (document.activeElement === last
        || !atlasIndex.contains(document.activeElement))
    ) {
      event.preventDefault();
      first.focus();
    }
  }

  function configureUtilities() {
    requestSpace.href = requestSpaceUrl();
    requestSpaceIndex.href = requestSpaceUrl();
    familyToggle.addEventListener("click", () => {
      if (atlasIndex.classList.contains("is-open")) closeIndex(true);
      else openIndex();
    });
    indexClose.addEventListener("click", () => closeIndex(true));
    indexBackdrop.addEventListener("click", () => closeIndex(true));
    atlasIndex.addEventListener("click", (event) => {
      const link = event.target.closest('a[href^="#"]');
      if (!link || !narrowIndexMedia.matches) return;
      const sameRoute = link.hash === window.location.hash;
      closeIndex(false);
      if (sameRoute) window.requestAnimationFrame(focusRouteHeading);
    });
    aboutToggle.addEventListener("click", () => {
      snapshotAbout.open = !snapshotAbout.open;
      aboutToggle.setAttribute(
        "aria-expanded",
        String(snapshotAbout.open),
      );
      if (narrowIndexMedia.matches) {
        openIndex({ returnFocus: aboutToggle, focusClose: false });
      }
      window.requestAnimationFrame(() => {
        snapshotAbout.querySelector("summary")?.focus();
      });
    });
    snapshotAbout.addEventListener("toggle", () => {
      aboutToggle.setAttribute(
        "aria-expanded",
        String(snapshotAbout.open),
      );
    });
    themeMenu.addEventListener("change", (event) => {
      if (!event.target.matches('input[name="theme-preference"]')) return;
      applyThemePreference(event.target.value);
      window.setTimeout(() => {
        themeMenu.open = false;
        themeSummary.focus();
      }, 0);
    });
    window.addEventListener("storage", (event) => {
      if (event.key === themeStorageKey) {
        applyThemePreference(event.newValue, false);
      }
    });
    window.addEventListener("hashchange", () => renderRoute());
    narrowIndexMedia.addEventListener("change", syncIndexAccessibility);
    document.addEventListener("click", (event) => {
      if (themeMenu.open && !themeMenu.contains(event.target)) {
        themeMenu.open = false;
      }
    });
    document.addEventListener("keydown", (event) => {
      trapIndexFocus(event);
      if (event.key !== "Escape") return;
      if (atlasIndex.classList.contains("is-open")) {
        closeIndex(true);
      } else if (themeMenu.open) {
        themeMenu.open = false;
        themeSummary.focus();
      }
    });
    document.querySelector(".skip-link")?.addEventListener("click", (event) => {
      event.preventDefault();
      atlasDocument.focus();
    });
  }

  applyThemePreference(storedThemePreference(), false);
  buildFamilyNavigation();
  buildSnapshotDetail();
  configureUtilities();
  syncIndexAccessibility();
  renderRoute({ initial: isInitialRoute });
  isInitialRoute = false;
})();
