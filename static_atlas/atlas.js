(async () => {
  "use strict";

  const presentation = window.HomologyAtlasPresentation;
  if (!presentation) {
    throw new Error("Homology Atlas presentation helpers did not load.");
  }
  const {
    coefficientDisplay,
    coefficientTex,
    cohomologyCoveragePresentation,
    coverageFor,
    coveragePresentation: pureCoveragePresentation,
    firstRecorded,
    groupPresentation,
    monomialTex,
    basisLabelTex,
    parseTex,
    relationTex,
  } = presentation;
  const dataStore = window.HomologyAtlasDataStore;
  const atlas = await dataStore.loadAtlas();
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
  const textbookGroups = [
    { title: "First examples", note: "Points, components, and spheres", ids: ["point", "sphere:0", "sphere:1", "sphere:2", "sphere:3", "sphere:4"] },
    { title: "Surfaces", note: "Products and a change of coefficients", ids: ["torus:2", "klein_bottle"] },
    { title: "Real projective spaces", note: "See what changes over a field", ids: ["real_projective_space:2", "real_projective_space:3", "real_projective_space:4"] },
    { title: "Same groups, different rings", note: "A cup product tells the difference", ids: ["complex_projective_space:2", "sphere_wedge:2:4"] },
  ];
  const classicalDescriptions = Object.freeze({
    point: "A space consisting of a single point. Every contractible space has the same ordinary homology and cohomology ring.",
    "sphere:0": "Two distinct points with the discrete topology. Its two components make degree zero different from that of a connected space.",
    "sphere:1": "The circle: the points at distance one from the origin in the plane.",
    "sphere:2": "The usual two-dimensional sphere, the boundary of a solid ball in three-dimensional Euclidean space.",
    "sphere:3": "The unit sphere in four-dimensional Euclidean space, with one cell in dimensions zero and three.",
    "sphere:4": "The unit sphere in five-dimensional Euclidean space, with one cell in dimensions zero and four.",
    "torus:2": "The product of two circles, or a square with each pair of opposite edges identified in the same direction. It is an orientable closed surface.",
    klein_bottle: "A square with one pair of opposite edges identified in the same direction and the other pair in opposite directions. It is a nonorientable closed surface.",
    "real_projective_space:2": "The space of lines through the origin in three-dimensional real space, equivalently the two-sphere with antipodal points identified.",
    "real_projective_space:3": "The space of lines through the origin in four-dimensional real space, equivalently the three-sphere with antipodal points identified.",
    "real_projective_space:4": "The space of lines through the origin in five-dimensional real space, equivalently the four-sphere with antipodal points identified.",
    "complex_projective_space:2": "The space of complex lines through the origin in complex three-dimensional space. It has one cell in real dimensions zero, two, and four.",
    "sphere_wedge:2:4": "A two-sphere and a four-sphere joined at one chosen point. Its additive groups agree with those of the complex projective plane; its cup products do not.",
  });
  const classicalFamilyDescriptions = Object.freeze({
    point: "The one-point space is the starting example for ordinary homology and cohomology.",
    sphere: "Unit spheres in Euclidean space, from the disconnected zero-sphere to higher-dimensional examples.",
    wedge: "Join pointed spaces at their chosen basepoints. Wedges give simple examples where cup products carry information beyond additive groups.",
    surface: "Every closed surface is a connected sum of tori or of projective planes. Orientability decides whether any torsion appears; the genus decides how many degree-one classes there are.",
    prism_polyhedral_3manifold: "Quotients of the 3-sphere by binary dihedral and binary polyhedral groups. The other spherical quotients \u2014 lens spaces, RP\u00b3, S\u00b3 and the Poincar\u00e9 sphere \u2014 are recorded in their own families.",
    flat_3manifold: "All ten closed flat 3-manifolds: six orientable, four not. Whether the top homology is Z or zero is exactly whether the quotient is orientable.",
    nil_3manifold: "Circle bundles over the torus with nonzero Euler number. That number appears directly as the order of the torsion class in first homology.",
    h2xr_3manifold: "A closed hyperbolic surface times a circle. K\u00fcnneth predicts every group here from the surface factor.",
    hyperbolic_3manifold: "Closed hyperbolic 3-manifolds of small volume. Volume determines the manifold; homology does not, and several of these share it.",
    connected_sum_3manifold: "Reducible 3-manifolds. By Kneser\u2013Milnor each has a unique prime decomposition, and every entry links to the summands it is built from.",
    four_manifold: "In dimension four the cup product on the middle degree is the intersection form. It is the only thing separating CP\u00b2 # CP\u00b2 from S\u00b2 \u00d7 S\u00b2, which have identical homology.",
    five_manifold: "Two products and the Wu manifold SU(3)/SO(3), the standard non-spin example in dimension five.",
    combinatorial_complex: "Complexes built from combinatorics rather than geometry. Their torsion is large and arbitrary rather than structural \u2014 one of these has Z/32 in its first homology.",
    s2xr_3manifold: "The four closed 3-manifolds built on S\u00b2 \u00d7 R. Two are sphere bundles over the circle, one is a product, one is a connected sum, and the list is complete.",
    real_projective_space: "Real lines through the origin, or spheres with antipodal points identified. Each has one cell in every dimension up to its dimension.",
    hopf_projective_plane: "The complex, quaternionic, and octonionic projective planes each have three cells, with different attaching maps.",
  });

  const spacesById = new Map(conceptualSpaces.map((space) => [space.id, space]));
  const spacesBySlug = new Map(
    conceptualSpaces.map((space) => [space.slug, space]),
  );
  const familiesById = new Map(sections.map((section) => [section.id, section]));
  const definitionsById = new Map(
    definitions.map((definition) => [definition.id, definition]),
  );
  const state = {
    route: { kind: "home" },
    queriesByScope: new Map(),
    homologyViewBySpace: new Map(),
  };

  const siteBrand = document.getElementById("site-brand");
  const requestSpace = document.getElementById("request-space");
  const themeMenu = document.getElementById("theme-menu");
  const themeSummary = themeMenu.querySelector(":scope > summary");
  const themeCurrent = themeMenu.querySelector(".theme-current");
  const themeInputs = [
    ...themeMenu.querySelectorAll('input[name="theme-preference"]'),
  ];
  const navHome = document.getElementById("nav-home");
  const navSpaces = document.getElementById("nav-spaces");
  const atlasDocument = document.getElementById("atlas-document");
  const actionStatus = document.getElementById("action-status");

  let knowlInstance = 0;
  let lastWorkbenchHash = "#home";
  const workbenchStorageKey = "homology-atlas-workbench-v1";
  function validWorkbenchHash(hash) {
    if (hash === "#home") return true;
    if (typeof hash !== "string" || !hash.startsWith("#")) return false;
    const route = parseRoute(hash);
    return route.kind === "workbench"
      && ["sphere", "real_projective_space", "complex_projective_space"].includes(route.family)
      && /^\d+$/.test(route.n) && /^\d+$/.test(route.start);
  }
  try {
    const remembered = sessionStorage.getItem(workbenchStorageKey);
    if (validWorkbenchHash(remembered)) lastWorkbenchHash = remembered;
  } catch (_error) { /* Session storage is optional for local-file viewing. */ }
  navHome.href = lastWorkbenchHash;
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
        catalog_search: space.catalog_search,
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
    const spoken = String(fallback ?? "").trim() || "Mathematical expression";
    math.setAttribute("aria-label", spoken);
    math.setAttribute("role", "math");
    const visual = element("span", "math-visual");
    visual.setAttribute("aria-hidden", "true");
    math.append(visual);

    function appendNodes(target, nodes) {
      nodes.forEach((node) => {
        if (node.type === "text") {
          target.append(document.createTextNode(node.value));
          return;
        }
        if (node.type === "sup" || node.type === "sub") {
          const script = element(node.type);
          appendNodes(script, node.children);
          target.append(script);
          return;
        }
        if (node.type === "group") {
          const wrapper = element(
            "span",
            node.command === "widetilde"
              ? "tex-widetilde"
              : `tex-${node.command}`,
          );
          appendNodes(wrapper, node.children);
          target.append(wrapper);
        }
      });
    }

    const parsed = parseTex(tex);
    if (parsed) {
      appendNodes(visual, parsed);
    } else {
      visual.replaceChildren(document.createTextNode(spoken));
      math.classList.add("math-fallback");
    }
    return math;
  }

  window.HomologyAtlasMath = Object.freeze({ renderTex });
  window.dispatchEvent(new Event("homology-atlas-renderer-ready"));

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
      [
        ...asArray(space.homology).map((row) => row.coefficient_ring),
        ...asArray(space.cohomology).map((record) => record.coefficient),
      ],
    );
    const core = space.classical_core || asArray(space.cohomology).length > 0;
    if (core) ["Q", "F2", "F3", "F5", "F7", "Z"].forEach((item) => recorded.add(item));
    const order = core ? ["Q", "F2", "F3", "F5", "F7", "Z"] : supportedCoefficients;
    return [...new Set([...order.filter((item) => recorded.has(item)), ...recorded])];
  }

  function homologyViewFor(space) {
    if (!state.homologyViewBySpace.has(space.id)) {
      const coefficients = availableCoefficients(space);
      const core = space.classical_core || asArray(space.cohomology).length > 0;
      const coefficient = core && coefficients.includes("Q") ? "Q"
        : coefficients.includes("Z") ? "Z" : coefficients[0] ?? "Z";
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
    const view = homologyViewFor(space);
    url.hash = `space=${encodeURIComponent(space.slug)}?${new URLSearchParams({coefficient:view.coefficient,reduced:view.reduced ? "1" : "0"})}`;
    return url.href;
  }

  function rememberSpaceView(space) {
    if (state.route.kind === "space" && state.route.space.id === space.id) {
      window.history.replaceState(null, "", permalinkFor(space));
    }
  }

  function serializedSpaceRecord(space) {
    return JSON.stringify({
      ...space,
      export_context: {
        atlas_schema_version: snapshot.schema_version,
        snapshot_id: snapshot.snapshot_id,
        source_commit: snapshot.source_commit,
        source_inputs_sha256: snapshot.source_inputs_sha256,
        source_database_sha256: snapshot.source_database_sha256,
        classical: atlas.classical,
      },
    }, null, 2);
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
    const symbol = {"Q":"\\mathbb{Q}","Z":"\\mathbb{Z}","F_p":"\\mathbb{F}_{p}"}[label ?? definition.term];
    if (symbol) trigger.replaceChildren(renderTex(symbol,label ?? definition.term,"math-inline"));
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
      (() => { const content=element("span"); if(window.HomologyWorkbench) window.HomologyWorkbench.mathText(content,` ${definition.body} `,renderTex); else content.textContent=` ${definition.body} `; return content; })(),
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
      scopeKey === "spaces" || scopeKey === "home"
        ? "Try “torus”, “RP²”, or “CP²”"
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
      element("p", "page-kicker", "A classical topology reference"),
      element("h1", "page-title", "Spaces, groups, and cup products."),
      element(
        "p",
        "home-intro page-lede",
        "Look up a familiar space. Compare coefficients, understand its cohomology ring, and follow the mathematics back to a source.",
      ),
    );
    hero.append(heroCopy);
    const examples = element("section", "textbook-examples home-section");
    const heading = element("div", "section-heading");
    heading.append(element("h2", "", "Start with these spaces"));
    const allSpaces = element("a", "text-link", `Browse all ${conceptualSpaces.length} spaces →`);
    allSpaces.href = "#spaces";
    heading.append(allSpaces);
    const groups = element("div", "textbook-groups");
    textbookGroups.forEach((group) => {
      const entries = group.ids.map((id) => spacesById.get(id)).filter(Boolean);
      if (!entries.length) return;
      const card = element("div", "textbook-group");
      card.append(element("h3", "", group.title), element("p", "", group.note));
      const links = element("ul", "textbook-links");
      entries.forEach((space) => {
        const item = element("li");
        const link = element("a", "textbook-space-link");
        link.href = `#space=${encodeURIComponent(space.slug)}`;
        link.setAttribute("aria-label", space.name.plain);
        link.append(mathName(space, "math-inline"));
        if (space.id === "point" || space.id === "klein_bottle") {
          link.append(document.createTextNode(` ${space.name.plain}`));
        }
        item.append(link);
        links.append(item);
      });
      card.append(links);
      groups.append(card);
    });
    const coreCount = conceptualSpaces.filter((space) => Number(space.cohomology_record_count ?? asArray(space.cohomology).length) > 0).length;
    examples.append(heading, groups,
      element("p", "classical-coverage-note", coreCount
        ? `Cohomology rings over ℚ, 𝔽₂, 𝔽₃, 𝔽₅, and 𝔽₇ are recorded for ${coreCount} textbook spaces. Integral homology remains available. Human mathematical review is pending.`
        : "Explore the existing homology collection. Cohomology-ring coverage is not recorded in this snapshot."));
    view.append(hero, buildSpaceSearch(conceptualSpaces, "home", "Find a space", { showAllOnEmpty: false }), examples);
    return view;
  }

  function teachingParagraph(text, className = "") {
    const node = element("p", className);
    window.HomologyWorkbench.mathText(node, text || "", renderTex);
    return node;
  }

  function buildTeachingView(route) {
    const catalog = atlas.teaching || {};
    const view = element("article", "route-view teaching-view");
    const comparisons = asArray(catalog.comparisons);
    const comparison = comparisons.find(item => item.id === route.id);
    if (route.kind === "comparison") {
      if (!comparison) return buildNotFoundView({requested:window.location.hash});
      const back=element("a", "teaching-entry-link", "← Textbook map");back.href="#textbook";
      view.append(back, element("p", "page-kicker", "Guided comparison"), element("h1", "page-title", comparison.title), teachingParagraph(comparison.introduction));
      const steps=element("ol", "teaching-steps");
      asArray(comparison.steps).forEach(step=>{const item=element("li");item.append(teachingParagraph(step.text));if(String(step.href).startsWith("#")){const go=element("a", "", "Open this example →");go.href=step.href;item.append(go);}steps.append(item);});
      view.append(steps, element("h2", "", "What to take away"), teachingParagraph(comparison.takeaway));
      const sources=element("ul", "citation-list");asArray(comparison.sources).forEach(ref=>sources.append(renderCitation(ref)));view.append(element("h2", "", "Sources"),sources,element("p", "table-note", "Teaching notes · human review pending. Follow each result’s own coverage and review labels."));return view;
    }
    view.append(element("h1", "page-title", catalog.title || "Textbook map"),teachingParagraph(catalog.scope_note || "A selected inventory, not every example in the book."));
    const guided=element("section", "teaching-guided");guided.append(element("h2", "", "Three ways to read the examples"));
    comparisons.forEach(item=>{const a=element("a", "teaching-comparison-link", item.title);a.href="#comparison="+encodeURIComponent(item.id);guided.append(a);});view.append(guided);
    const filters=element("div", "teaching-filters");const searchLabel=element("label", "wb-field", "Find a textbook example");const search=element("input");search.type="search";searchLabel.append(search);
    const chapterLabel=element("label", "wb-field", "Chapter or topic");const chapter=element("select");const all=element("option", "", "All chapters and topics");all.value="";chapter.append(all);
    [...new Set(asArray(catalog.entries).map(item=>item.chapter))].filter(Boolean).forEach(value=>{const option=element("option", "", value);option.value=value;chapter.append(option);});chapterLabel.append(chapter);filters.append(searchLabel,chapterLabel);view.append(filters);
    const count=element("p", "table-note");count.setAttribute("role","status");const results=element("div", "teaching-inventory");view.append(count,results);
    function draw(){results.replaceChildren();let number=0;asArray(catalog.entries).forEach(entry=>{const space=spacesById.get(entry.space_id);if(!space)return;const text=[space.name.plain,entry.chapter,entry.introduction,entry.locator,entry.coverage?.label].join(" ").toLowerCase();if((chapter.value&&chapter.value!==entry.chapter)||!text.includes(search.value.toLowerCase()))return;number++;const card=element("article", "teaching-example");card.dataset.spaceId=space.id;const title=element("h2");const a=element("a");a.href="#space="+encodeURIComponent(space.slug);a.append(mathName(space,"math-inline"));title.append(a);card.append(element("p", "page-kicker",entry.chapter),title,teachingParagraph(entry.introduction),element("p", "teaching-coverage",entry.coverage?.label || entry.coverage_note || "Coverage: see the space record."));if(entry.coverage?.label&&entry.coverage_note)card.append(teachingParagraph(entry.coverage_note,"table-note"));const details=element("details", "teaching-source");details.append(element("summary", "", "Reading and sources"),teachingParagraph(entry.teaching_point));const sources=element("ul","citation-list");asArray(entry.sources).forEach(ref=>sources.append(renderCitation(ref)));details.append(sources);card.append(details);results.append(card);});count.textContent=`${number} of ${asArray(catalog.entries).length} retained examples. Selected inventory; not an exhaustive textbook index.`;if(!number)results.append(element("p","","No examples match. Try another topic or clear the search."));}
    search.addEventListener("input",draw);chapter.addEventListener("change",draw);draw();return view;
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
        `${conceptualSpaces.length} spaces in ${sections.length} families`,
        "Search the collection or browse by family. The textbook core includes cohomology rings; every space retains its existing homology and sources.",
      ),
    );
    const teachingLink = element("a", "teaching-entry-link", "Textbook map and guided comparisons →");
    teachingLink.href = "#textbook"; view.append(teachingLink);

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
    const familyIntroduction = classicalFamilyDescriptions[section.id] ?? section.summary;
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

  function buildCoefficientControls(space, cohomology, homology) {
    const controls = element(
      "div",
      "coefficient-controls shared-coefficient-controls",
    );
    const view = homologyViewFor(space);
    const coefficientFieldset = element(
      "fieldset",
      "space-coefficients segmented-fieldset segmented-control-group",
    );
    coefficientFieldset.append(element("legend", "", "Coefficients for both theories"));
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
        renderTex(coefficientTex(coefficient), coefficientDisplay(coefficient), "math-inline"),
      );
      coefficientOptions.append(option);
    });
    coefficientFieldset.append(coefficientOptions);
    const help = element("p", "control-help");
    help.append(buildKnowl("coefficient-field", "What do coefficients change?"));
    controls.append(coefficientFieldset, help);
    controls.addEventListener("change", (event) => {
      if (!(event.target instanceof HTMLInputElement)
        || event.target.name !== `coefficient-${space.slug}`) return;
      const current = homologyViewFor(space);
      current.coefficient = event.target.value;
      renderCohomology(space, cohomology);
      renderHomology(space, homology);
      rememberSpaceView(space);
      announce(`${space.name.plain}: cohomology and homology with ${coefficientDisplay(current.coefficient)} coefficients.`);
    });
    return controls;
  }

  function buildHomologyControls(space, host) {
    const controls = element("div", "homology-controls local-homology-controls");
    const view = homologyViewFor(space);
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
      document.createTextNode(" · Applies to homology only."),
    );
    conventionFieldset.append(conventionHelp);

    controls.addEventListener("change", (event) => {
      if (!(event.target instanceof HTMLInputElement)) return;
      const current = homologyViewFor(space);
      if (event.target.name === `convention-${space.slug}`) {
        current.reduced = event.target.value === "true";
      }
      renderHomology(space, host);
      rememberSpaceView(space);
      announce(
        `${space.name.plain}: ${current.reduced ? "reduced" : "unreduced"} homology with ${coefficientDisplay(current.coefficient)} coefficients.`,
      );
    });
    controls.append(conventionFieldset);
    return controls;
  }

  function renderCohomology(space, host) {
    const dynamic = host.querySelector(".cohomology-dynamic");
    const coefficient = homologyViewFor(space).coefficient;
    const records = asArray(space.cohomology)
      .filter((record) => record.coefficient === coefficient);
    // A slot can carry more than one record: a sourced ring and an independently
    // computed one corroborate each other and are never merged. A cited text takes
    // precedence over a machine computation wherever one exists, so the displayed
    // ring and its table come from the literature record when there is one. The
    // others are named rather than hidden.
    const record = records.find((item) => item.provenance?.kind === "literature")
      ?? records.find((item) => item.presentation?.tex)
      ?? records[0]
      ?? null;
    const corroborating = records.filter((item) => item !== record);
    const hasRing = Boolean(record?.knowledge_state === "exact" && Array.isArray(record.groups) && record.algebra);
    host.classList.toggle("cohomology-unrecorded", !hasRing);
    host.closest(".space-theory-results")?.classList.toggle("has-cohomology-ring", hasRing);
    const content = element("div", "cohomology-rendered");
    if (!hasRing) {
      content.append(
        element("p", "cohomology-missing", `Cohomology is not recorded with ${coefficientDisplay(coefficient)} coefficients. This does not mean it is zero.`),
      );
      dynamic.replaceChildren(content);
      return;
    }

    const algebra = record.algebra ?? {};
    const formula = element("div", "ring-presentation");
    formula.append(
      renderTex(`H^{*}(${space.name.tex};${coefficientTex(coefficient)})`,
        `Ordinary cohomology ring of ${space.name.plain} with ${coefficientDisplay(coefficient)} coefficients`, "cohomology-formula"),
    );
    if (record.presentation?.tex) {
      formula.append(renderTex(`\\cong ${record.presentation.tex}`,
        `is isomorphic to ${record.presentation.plain}`, "ring-formula"));
    }
    content.append(formula,
      element("p", "ring-convention", "Ordinary, unreduced cohomology · multiplication is the cup product · unit 1 in degree 0"));
    if (record.provenance?.kind === "external_engine_computation") {
      content.append(element("p", "ring-provenance cohomology-imported",
        `Computed by ${record.provenance.engine ?? "an external system"} from a pinned simplicial model, and imported. Not independently verified here and not human-reviewed.`));
    }
    if (corroborating.length) {
      const kinds = corroborating.map((item) => item.provenance?.kind === "external_engine_computation"
        ? "an independent machine computation" : "a literature source");
      content.append(element("p", "ring-corroboration",
        `Also recorded by ${[...new Set(kinds)].join(" and ")}, agreeing on the additive groups.`));
    }

    const definitionsLine = element("p", "ring-definitions");
    definitionsLine.append(buildKnowl("cup-product", "Cup product"), document.createTextNode(" · "),
      buildKnowl("generator-degree", "Generator degree"), document.createTextNode(" · "),
      buildKnowl("ring-relation", "Relations"));
    content.append(definitionsLine);

    const structure = element("dl", "ring-structure");
    if (algebra.kind === "graded_structure_constants") {
      structure.append(element("dt", "", "Presentation"));
      structure.append(element("dd", "ring-generators",
        "Recorded as an additive basis with its full cup-product table. No generators-and-relations presentation is claimed."));
    } else {
    structure.append(element("dt", "", "Generators"));
    const generators = element("dd", "ring-generators");
    if (!asArray(algebra.generators).length) {
      generators.textContent = "The unit 1 alone; no additional generators.";
    } else {
      asArray(algebra.generators).forEach((generator, index) => {
        if (index) generators.append(document.createTextNode("; "));
        generators.append(renderTex(generator.id, generator.id, "math-inline"),
          document.createTextNode(` in degree ${generator.degree}`));
      });
    }
    structure.append(generators, element("dt", "", "Relations"));
    const relations = element("dd", "ring-relations");
    if (!asArray(algebra.relations).length) {
      relations.textContent = "No additional relations.";
    } else {
      asArray(algebra.relations).forEach((relation, index) => {
        if (index) relations.append(document.createTextNode("; "));
        const tex = relationTex(relation);
        relations.append(renderTex(tex, tex.replaceAll("^{", " to the power ").replaceAll("}", ""), "math-inline"));
      });
    }
    structure.append(relations);
    }
    content.append(structure);
    const notes = element("div", "ring-meaning");
    asArray(record.presentation?.notes).forEach((note) => notes.append(element("p", "", note)));
    content.append(notes, element("h3", "cohomology-groups-heading", "Groups by degree"));

    const tableWrap = element("div", "homology-table-wrap cohomology-table-wrap");
    const table = element("table", "homology-table cohomology-table");
    table.append(element("caption", "visually-hidden", `Cohomology groups and a vector-space basis for ${space.name.plain} over ${coefficientDisplay(coefficient)}`));
    const head = element("thead");
    const header = element("tr");
    ["Degree", "Group", "Basis"].forEach((label) => {
      const cell = element("th", "", label);
      cell.scope = "col";
      header.append(cell);
    });
    head.append(header);
    const body = element("tbody");
    record.groups.forEach((group) => {
      const row = element("tr");
      const degree = element("th", "degree-cell");
      degree.scope = "row";
      degree.append(renderTex(`H^{${group.degree}}`, `Cohomology degree ${group.degree}`, "math-inline"));
      const groupCell = element("td", "group-cell");
      const value = groupPresentation({ coefficient_ring: coefficient, knowledge_state: "exact", group: { state: "exact", ...group } });
      groupCell.append(value.exact ? renderTex(value.tex, value.plain, "group-math") : document.createTextNode(value.plain));
      const basisCell = element("td", "cohomology-basis");
      const basis = asArray(algebra.basis).filter((item) => item.degree === group.degree);
      const summands = Number.isInteger(group.dimension)
        ? group.dimension
        : (group.free_rank ?? 0) + asArray(group.torsion_orders).length;
      if (summands === 0) {
        basisCell.textContent = "—";
      } else if (basis.length !== summands) {
        basisCell.textContent = "Not recorded";
      } else {
        basis.forEach((item, index) => {
          if (index) basisCell.append(document.createTextNode(", "));
          basisCell.append(renderTex(basisLabelTex(item), item.id, "math-inline"));
        });
      }
      row.append(degree, groupCell, basisCell);
      body.append(row);
    });
    table.append(head, body);
    tableWrap.append(table);
    const coverage = cohomologyCoveragePresentation(record);
    content.append(tableWrap, element("p", "cohomology-coverage table-note", `${coverage.label}. ${coverage.detail}`));
    const products = element("details", "wb-products classical-products");
    products.append(element("summary", "", "Cup-product table"));
    const complete = algebra.multiplication?.complete === true;
    products.append(element("p", "wb-muted", complete ? "Multiplication: complete for all additive basis pairs." : "Multiplication: not recorded completely. Missing products are not zero."));
    const basis = asArray(algebra.basis);
    const basisById = new Map(basis.map(item => [item.id,item]));
    const basisTex = basisLabelTex;
    const list = element("ul", "wb-generator-list");
    basis.forEach(item => {const row=element("li");row.append(renderTex(basisTex(item),item.id,"math-inline"),document.createTextNode(` · degree ${item.degree}`));list.append(row);});
    products.append(list);
    const wrap = element("div", "wb-table-scroll");wrap.tabIndex=0;wrap.setAttribute("role","region");wrap.setAttribute("aria-label","Cup-product table");
    const productTable=element("table","wb-multiplication");const productHead=element("thead");const productHeader=element("tr");productHeader.append(element("th","","∪"));
    basis.forEach(item=>{const cell=element("th");cell.scope="col";cell.append(renderTex(basisTex(item),item.id,"math-inline"));productHeader.append(cell);});productHead.append(productHeader);
    const productBody=element("tbody");basis.forEach(left=>{const row=element("tr");const title=element("th");title.scope="row";title.append(renderTex(basisTex(left),left.id,"math-inline"));row.append(title);basis.forEach(right=>{
      const recorded=asArray(algebra.products).find(product=>product.left===left.id&&product.right===right.id);
      let tex;
      if(left.id===algebra.unit)tex=basisTex(right);else if(right.id===algebra.unit)tex=basisTex(left);
      else if(recorded)tex=recorded.result.map(term=>`${term.coefficient===1?"":term.coefficient===-1?"-":term.coefficient}${basisTex(basisById.get(term.basis))}`).join("+").replaceAll("+-","-") || "0";
      else if(complete&&algebra.multiplication.omitted_products==="zero")tex="0";
      const cell=element("td");cell.append(tex===undefined?document.createTextNode("Not recorded"):renderTex(tex,tex,"math-inline"));row.append(cell);
    });productBody.append(row);});productTable.append(productHead,productBody);wrap.append(productTable);products.append(wrap);content.append(products);

    const sources = element("div", "cohomology-sources");
    sources.append(element("h3", "", "Sources & review"));
    const citations = element("ul", "citation-list");
    asArray(record.sources).forEach((reference) => {
      const catalog = { ...(atlas.classical?.sources ?? {}), ...(atlas.computed_rings?.sources ?? {}) };
      const source = Array.isArray(catalog)
        ? catalog.find((item) => item.id === reference.source_id || item.source_id === reference.source_id)
        : catalog?.[reference.source_id];
      citations.append(renderCitation({ ...source, ...reference, year: source?.publication_year ?? source?.year }));
    });
    if (!citations.children.length) citations.append(element("li", "", "Source not recorded."));
    // Say how this particular record was established. Calling a machine
    // computation literature-based is a false claim about its evidence, and the
    // two differ in what is still unverified: a citation has not been re-derived
    // here, an import has not been checked to be the cup product of its model.
    const reviewNote = record.provenance?.kind === "external_engine_computation"
      ? "Machine-computed from a pinned simplicial model · imported, not verified here · human mathematical review pending."
      : "Literature-based presentation · human mathematical review pending.";
    sources.append(citations, element("p", "human-review-note", reviewNote));
    if (record.provenance?.derivation) {
      const derivation = detailsBlock("How this record is supported");
      derivation.content.append(element("p", "", record.provenance.derivation));
      sources.append(derivation.details);
    }
    content.append(sources);
    dynamic.replaceChildren(content);
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
    if (view.coefficient === "Q" && rows.length) {
      const note = element("p", "table-note rational-homology-note",
        "Rational homology is derived from integral homology by extension of scalars. ");
      const source = atlas.classical?.rational_homology_derivation;
      const link = outboundLink(source?.locator ?? "Source", source?.source_url,
        "Source for rational homology by extension of scalars");
      if (link) note.append(link);
      content.append(note);
    }
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
      rows.forEach((row, index) => {
        const tableRow = element("tr");
        if (index >= 9) { tableRow.hidden = true; tableRow.classList.add("additional-homology-degree"); }
        const degree = element("th", "degree-cell");
        degree.scope = "row";
        degree.setAttribute("headers", degreeHeader.id);
        degree.append(
          renderTex(`${view.reduced ? "\\widetilde{H}" : "H"}_{${row.degree}}`, `${view.reduced ? "Reduced h" : "H"}omology degree ${row.degree}`),
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
    if (rows.length > 9) {
      const scope = element("p", "table-note degree-display-note", `Showing the first 9 of ${rows.length} recorded degrees. This is a display limit, not a coverage limit.`);
      const expand = element("button", "text-button show-recorded-degrees", "Show all recorded degrees");
      expand.type = "button"; expand.setAttribute("aria-expanded", "false");
      expand.addEventListener("click", () => {
        const open = expand.getAttribute("aria-expanded") !== "true";
        body.querySelectorAll(".additional-homology-degree").forEach(row => { row.hidden = !open; });
        expand.setAttribute("aria-expanded", String(open));
        expand.textContent = open ? "Show first 9 recorded degrees" : "Show all recorded degrees";
        scope.textContent = open ? `Showing all ${rows.length} recorded degrees. Coverage is stated above.` : `Showing the first 9 of ${rows.length} recorded degrees. This is a display limit, not a coverage limit.`;
      });
      content.append(scope, expand);
    }
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

  // A computed ring is only as identified as the model it was computed on, so the
  // technical block shows that model too: its size, its pinned hash, and the
  // constructor that produced it. Where the constructor does not reproduce its
  // own vertex labelling, the facets are the identity and that is said plainly.
  function renderSimplicialModels(space, content) {
    const models = asArray(atlas.computed_rings?.models)
      .filter((model) => model.space_id === space.id);
    if (!models.length) return;
    content.append(element("h4", "", "Simplicial models used for computed rings"));
    models.forEach((model) => {
      const list = element("dl", "record-fields");
      const rows = [
        ["Model", model.model_id],
        ["Kind", model.kind],
        ["Size", `${model.vertices} vertices · ${model.facets} facets · f-vector (${asArray(model.f_vector).join(", ")})`],
        ["Constructed by", `${String(model.generator_version ?? "").startsWith(model.generator)
          ? model.generator_version
          : `${model.generator} ${model.generator_version}`} · ${model.constructor}`],
        ["Computed by", `${model.engine} ${model.engine_version}`],
        ["Facets SHA-256", model.facets_sha256],
        ["Artifact", model.artifact_path],
        ["Artifact SHA-256", model.artifact_sha256],
        ["Labelling", model.reproducible_labelling
          ? "The constructor reproduces this vertex labelling."
          : "The constructor does not reproduce this vertex labelling between runs; the checked-in facets are the model of record."],
      ];
      rows.forEach(([label, value]) => {
        if (!value) return;
        list.append(element("dt", "", label), element("dd", "", String(value)));
      });
      content.append(list);
    });
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

  function supportingCitations(space) {
    const references = evidenceRecords(space).flatMap(record => citationRecords(record));
    const seen = new Set();
    return references.filter(reference => {
      if (!reference || typeof reference !== "object" || !String(reference.role ?? "").split("_").includes("homology")) return false;
      const key = JSON.stringify([reference.url, reference.title, reference.locator, reference.role]);
      if (seen.has(key)) return false;
      seen.add(key); return true;
    });
  }

  // The cohomology section shows the sources for whichever coefficient is
  // selected. This is the whole set for the space, so a reader looking at
  // "Sources and details" does not have to change coefficient to find them.
  function cohomologyCitations(space) {
    const catalog = { ...(atlas.classical?.sources ?? {}), ...(atlas.computed_rings?.sources ?? {}) };
    const groups = new Map();
    asArray(space.cohomology).forEach((record) => {
      asArray(record.sources).forEach((reference) => {
        const source = catalog?.[reference.source_id];
        const merged = { ...source, ...reference, year: source?.publication_year ?? source?.year };
        const key = JSON.stringify([merged.url, merged.title, merged.role]);
        const group = groups.get(key);
        if (group) {
          if (!group.locators.includes(merged.locator)) group.locators.push(merged.locator);
        } else {
          groups.set(key, { reference: merged, locators: [merged.locator] });
        }
      });
    });
    // One source cited once per coefficient would otherwise repeat six times over,
    // identical but for the tail of the locator. Fold those into a single line.
    return Array.from(groups.values()).map(({ reference, locators }) => ({
      ...reference,
      locator: locators.length > 1 ? foldLocators(locators) : locators[0],
    }));
  }

  function foldLocators(locators) {
    let prefix = locators[0];
    locators.forEach((locator) => {
      while (prefix && !String(locator).startsWith(prefix)) prefix = prefix.slice(0, -1);
    });
    if (prefix.length < 4) return locators.join("; ");
    const tails = locators.map((locator) => String(locator).slice(prefix.length)).filter(Boolean);
    return tails.length ? `${prefix}${tails.join(", ")}` : prefix;
  }

  function buildProvenanceSummary(space) {
    const citation = supportingCitations(space)[0];
    const summary = element("aside", "provenance-summary");
    summary.setAttribute("aria-label", "Provenance");
    if (!citation) {
      summary.append(element("p", "", "A supporting homology source is not recorded."));
      return summary;
    }
    const title = citationTitle(citation);
    summary.append(element("span", "provenance-label", "Homology source"),
      outboundLink(title + " ↗", citation.url, "Open supporting homology source: " + title) ?? element("strong", "", title));
    if (citation.locator) summary.append(element("span", "provenance-locator", citation.locator));
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
      teachingParagraph(atlas.teaching?.entries?.find(entry => entry.space_id === space.id)?.introduction ?? classicalDescriptions[space.id] ?? space.summary, "space-summary"),
    );
    const feedback = outboundLink(
      "Correct or improve ↗",
      spaceFeedbackUrl(space),
      `Give feedback on ${space.name.plain}`,
    );
    if (feedback) {
      feedback.classList.add("context-feedback-link");
    }
    let reviewToggle = null;
    header.append(titleCopy);
    const actions = element("div", "space-actions permalink-actions");
    const copyLink = element("button", "text-button", "Copy link");
    copyLink.type = "button";
    copyLink.addEventListener("click", () => copyText(permalinkFor(space), copyLink));
    const headerDownload = element("button", "text-button", "Download space JSON");
    headerDownload.type = "button"; headerDownload.addEventListener("click", () => downloadRecord(space));
    actions.append(copyLink, headerDownload);
    header.append(actions);
    if (reviewModeEnabled) {
      reviewToggle = element(
        "button",
        "text-button review-toggle",
        "Review details",
      );
      reviewToggle.type = "button";
      reviewToggle.setAttribute("aria-pressed", "false");
      actions.append(reviewToggle);
    }
    view.append(header);

    const metadata = element("dl", "space-metadata");
    const dimension = spaceDimension(space);
    const dimensionLabel = isInfiniteFiniteType(space)
      ? "Infinite dimensional · finite type"
      : (dimension ?? "Not recorded");
    const titleFacts = element("p", "space-title-facts");
    titleFacts.append(element("span", "space-dimension", `Dimension: ${dimensionLabel}`));
    const reviewPending = evidenceRecords(space).some(record => record.release_status === "development_corpus_not_externally_reviewed")
      || asArray(space.cohomology).some(record => record.provenance?.review_state === "human_review_pending");
    titleFacts.append(document.createTextNode(" · "), element("span", "space-review-state", reviewPending ? "Human review pending" : "Human review not recorded"));
    titleCopy.append(titleFacts);
    const teaching = atlas.teaching?.entries?.find(entry => entry.space_id === space.id);
    if (teaching) {
      const readerNote = element("details", "space-teaching-note");
      readerNote.append(element("summary", "", "What to notice"), teachingParagraph(teaching.teaching_point));
      const sources = element("ul", "citation-list"); asArray(teaching.sources).forEach(ref => sources.append(renderCitation(ref)));
      readerNote.append(sources); titleCopy.append(readerNote);
      const map = element("a", "teaching-entry-link", "Place this example in the textbook map →"); map.href="#textbook"; titleCopy.append(map);
    }
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
    const cohomology = element("section", "cohomology-section space-section");
    const cohomologyHeading = element("div", "section-heading space-section-heading");
    cohomologyHeading.append(element("h2", "", "Cohomology"),
      buildKnowl("ordinary-cohomology", "Definition"));
    cohomology.append(cohomologyHeading, element("div", "cohomology-dynamic"));
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
    const results = element("div", "space-theory-results");
    results.append(homology, cohomology);
    view.append(buildCoefficientControls(space, cohomology, homology), results);
    renderCohomology(space, cohomology);
    renderHomology(space, homology);
    homology.append(buildProvenanceSummary(space));

    if (space.id === "complex_projective_space:2" || space.id === "sphere_wedge:2:4") {
      const otherId = space.id === "complex_projective_space:2"
        ? "sphere_wedge:2:4" : "complex_projective_space:2";
      const other = spacesById.get(otherId);
      if (other) {
        const comparison = element("aside", "ring-comparison space-section");
        comparison.setAttribute("aria-label", "Why ring structure matters");
        comparison.append(element("h2", "", "Why ring structure matters"));
        const explanation = element("p");
        explanation.append(
          document.createTextNode("Over each displayed field, the complex projective plane and "),
          renderTex("S^{2}\\vee S^{4}", "the wedge of a two-sphere and a four-sphere", "math-inline"),
          document.createTextNode(" have one-dimensional cohomology in degrees 0, 2, and 4. In the projective plane, the square of a degree-2 generator is nonzero. In the wedge, every product of positive-degree classes is zero. The groups agree; the rings distinguish the spaces."),
        );
        const link = element("a", "text-link related-example-link");
        link.href = `#space=${encodeURIComponent(other.slug)}`;
        link.append(document.createTextNode("Compare with "), mathName(other, "math-inline"), document.createTextNode(" →"));
        comparison.append(explanation, link);
        view.append(comparison);
      }
    }

    const records = element(
      "section",
      "record-details entry-details evidence-details space-section",
    );
    records.append(element("h2", "", "Sources and details"));
    const readableSources = element("section", "space-readable-sources");
    readableSources.append(element("h3", "", "Supporting homology sources"));
    const citations = supportingCitations(space);
    const citationList = element("ul", "citation-list");
    citations.forEach(reference => citationList.append(renderCitation(reference)));
    readableSources.append(citations.length ? citationList : element("p", "", "Supporting homology sources are not recorded."));
    records.append(readableSources);
    const ringCitations = cohomologyCitations(space);
    if (ringCitations.length) {
      const ringSources = element("section", "space-readable-sources");
      ringSources.append(element("h3", "", "Supporting cohomology sources"));
      const ringList = element("ul", "citation-list");
      ringCitations.forEach((reference) => ringList.append(renderCitation(reference)));
      ringSources.append(ringList);
      records.append(ringSources);
    }
    const modelBlock = detailsBlock("Technical model and evidence records");
    const modelDefinition = element("p", "detail-definition");
    modelDefinition.append(buildKnowl("model", "What is a Model?"));
    modelBlock.content.append(modelDefinition, metadata);
    renderModels(space, modelBlock.content);
    renderSimplicialModels(space, modelBlock.content);
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
    if (feedback) view.append(feedback);
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
    if (hash === "#textbook") return {kind:"textbook"};
    if (hash.startsWith("#comparison=")) { try { return {kind:"comparison",id:decodeURIComponent(hash.slice(12))}; } catch { return {kind:"not-found",requested:hash}; } }
    if (hash === "#about") return { kind: "about" };
    const workbenchRoute = window.HomologyWorkbench?.route(hash);
    if (workbenchRoute) return workbenchRoute;
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
        const [encodedSlug, query = ""] = spaceMatch[1].split("?", 2);
        const slug = decodeURIComponent(encodedSlug);
        const space = spacesBySlug.get(slug);
        if (!space) return { kind: "not-found", requested: hash };
        const params = new URLSearchParams(query);
        const viewState = {};
        if (availableCoefficients(space).includes(params.get("coefficient"))) viewState.coefficient = params.get("coefficient");
        if (["0", "1"].includes(params.get("reduced"))) viewState.reduced = params.get("reduced") === "1";
        const legacy = window.HomologyWorkbench?.legacy(space);
        if (legacy) return {...legacy, ...(viewState.reduced !== undefined ? {reduced:viewState.reduced} : {})};
        return { kind: "space", space, viewState };
      } catch (_error) {
        return { kind: "not-found", requested: hash };
      }
    }
    return { kind: "not-found", requested: hash };
  }

  function routeTitle(route) {
    if (["textbook", "comparison"].includes(route.kind)) return "Textbook examples · Homology Atlas";
    if (route.kind === "about") return "About · Homology Atlas";
    if (route.kind === "workbench") return "Family workbench · Homology Atlas";
    if (route.kind === "glossary") return "Glossary · Homology Atlas";
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
    document.querySelectorAll(".primary-nav a, #nav-spectra").forEach(link => link.removeAttribute("aria-current"));
    const current = { home: "nav-home", workbench: "nav-home", spaces: "nav-spaces", family: "nav-spaces", space: "nav-spaces", glossary: "nav-glossary", about: "nav-about" }[route.kind];
    document.getElementById(current)?.setAttribute("aria-current", ["family", "space"].includes(route.kind) ? "location" : "page");
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

  let routeRevision = 0;
  async function renderRoute({ initial = false } = {}) {
    const revision = ++routeRevision;
    const route = parseRoute();
    if (route.kind === "space") {
      const loading = element("article", "route-view loading-view");
      loading.setAttribute("aria-busy", "true");
      loading.append(
        element("p", "page-kicker", "Loading one atlas record"),
        element("h1", "page-title", route.space.name?.plain ?? "Loading space…"),
        element("p", "page-lede", "Loading homology, cohomology, and provenance…"),
      );
      atlasDocument.replaceChildren(loading);
      try {
        await dataStore.loadSpace(route.space);
      } catch (_error) {
        if (revision !== routeRevision) return;
        const failed = element("article", "route-view load-error-view");
        failed.setAttribute("role", "alert");
        failed.append(
          element("h1", "page-title", "This record could not be loaded"),
          element("p", "page-lede", "The atlas could not retrieve this space. No missing information has been interpreted as zero."),
        );
        const actions = element("div", "hero-actions");
        const retry = element("button", "primary-action", "Retry");
        retry.type = "button";
        retry.addEventListener("click", () => renderRoute());
        const all = element("a", "secondary-action", "Return to all spaces");
        all.href = "#spaces";
        actions.append(retry, all);
        failed.append(actions);
        atlasDocument.replaceChildren(failed);
        document.title = "Record unavailable · Homology Atlas";
        if (!initial) window.requestAnimationFrame(focusRouteHeading);
        return;
      }
      if (revision !== routeRevision) return;
    }
    state.route = route;
    if (route.kind === "space") Object.assign(homologyViewFor(route.space), route.viewState || {});
    if (["home", "workbench"].includes(route.kind) && validWorkbenchHash(window.location.hash || "#home")) {
      lastWorkbenchHash = window.location.hash || "#home";
      navHome.href = lastWorkbenchHash;
      try { sessionStorage.setItem(workbenchStorageKey, lastWorkbenchHash); } catch (_error) { /* Optional persistence. */ }
    }
    let view;
    if (["home", "workbench", "glossary"].includes(route.kind) && window.HomologyWorkbench) {
      view = window.HomologyWorkbench.create({atlas, renderTex, copyText, downloadRecord}, route);
    }
    else if (route.kind === "home") view = buildHomeView();
    else if (route.kind === "about") view = buildAboutView();
    else if (["textbook", "comparison"].includes(route.kind)) view = buildTeachingView(route);
    else if (route.kind === "spaces") view = buildSpacesView();
    else if (route.kind === "family") view = buildFamilyView(route.section);
    else if (route.kind === "space") view = buildSpaceView(route.space);
    else view = buildNotFoundView(route);

    atlasDocument.replaceChildren(view);
    document.title = routeTitle(route);
    updateNavigationCurrent(route);
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

  function buildSnapshotDetail() {
    const snapshotDetail = element("div", "snapshot-detail");
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
      ["Stable spectra", snapshot.conceptual_spectrum_count],
      ["Models", snapshot.model_count],
      ["Evidence records", snapshot.evidence_count],
      ["Source commit", snapshot.source_commit],
    ].forEach(([term, value]) => appendDefinition(facts, term, value));
    snapshotDetail.append(summary, facts);
    if (Number(snapshot.conceptual_spectrum_count) > 0) {
      const foundations = element("p", "snapshot-foundations-note");
      foundations.append(
        document.createTextNode(
          "The stable-spectrum area currently uses the language of the stable homotopy category, written ",
        ),
        renderTex("\\mathrm{Sp}", "S p", "math-inline"),
        document.createTextNode(
          ". Its long-term infinity-categorical foundations and notation remain an editorial work in progress; this presentation note does not alter the imported operations' review status.",
        ),
      );
      snapshotDetail.append(foundations);
    }
    return snapshotDetail;
  }

  function buildAboutView() {
    const view = element("article", "route-view about-view");
    const textbook = element("a", "teaching-entry-link", "Textbook map and guided comparisons →"); textbook.href="#textbook"; view.append(textbook);
    view.append(element("p", "page-kicker", "A reference, with its workings visible"), element("h1", "page-title", "About Homology Atlas"));
    view.append(element("p", "page-lede", "Explore ordinary homology and cohomology rings of familiar spaces, compare coefficients, and follow each result back to its sources."));
    view.append(element("h2", "", "What is covered"), element("p", "", "The family workbench evaluates sourced rules for spheres, real projective spaces, and complex projective spaces at every finite nonnegative dimension parameter. Its degree window limits the display, not the mathematical coverage."));
    view.append(element("p", "", "All spaces retains the earlier catalogue. Coverage and coefficient availability vary by record; missing information is labelled, never treated as zero. Stable spectra remain a separate, secondary resource."));
    view.append(element("h2", "", "Review and provenance"), element("p", "", "Coverage, automated checks, agent review, and human review are distinct. A completeness label is not a human sign-off. Human reviews bind an exact rule version and scope, and changes require fresh review."));
    const rules = atlas.family_rules?.rules || [];
    const list = element("ul", "about-review-list");
    rules.forEach(rule => {
      const label = rule.human_review_state === "human_reviewed" ? "Human reviewed" : rule.human_review_state === "human_concern" ? "Human concern recorded" : "Human review pending";
      const scopedLabel = rule.scoped_review_state === "scoped_human_concern" ? " · Concern recorded in a narrower scope" : asArray(rule.scoped_human_reviews).length ? " · Narrow-scope reviews recorded" : "";
      const item = element("li", "", `${rule.name || humanize(rule.family)}: ${label}${scopedLabel}`);
      if (scopedLabel) { const details = element("a", "", " — inspect exact review scopes"); details.href = "#workbench?" + new URLSearchParams({family:rule.family,n:"2",start:"0"}); item.append(details); }
      list.append(item);
    });
    if (!rules.length) list.append(element("li", "", "Family human-review state not recorded."));
    view.append(list, element("p", "", "Use “Review this result” on the workbench to choose your exact scope and copy a review packet or open the public GitHub form. A maintainer validates submissions before publishing them as mathematical review."));
    const back = element("a", "", "Return to your workbench →"); back.href = lastWorkbenchHash; view.append(back);
    const request = element("a", "about-request-link", "Request a space ↗");
    request.href = requestSpaceUrl(); request.target = "_blank"; request.rel = "noopener noreferrer";
    view.append(element("h2", "", "Contribute an example"), request);
    view.append(element("h2", "", "Snapshot details"), buildSnapshotDetail());
    const offlinePath = atlas._bundle_manifest?.offline_artifact?.path;
    if (offlinePath) {
      const offline = element("a", "secondary-resource-link", "Download the complete offline atlas ↓");
      offline.href = offlinePath;
      offline.download = "";
      view.append(offline);
    }
    if (Number(snapshot.conceptual_spectrum_count) > 0) { const spectra = element("a", "secondary-resource-link", "Stable spectra preview →"); spectra.href = "#spectra"; view.append(spectra); }
    return view;
  }

  function configureUtilities() {
    requestSpace.href = requestSpaceUrl();
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
    document.addEventListener("click", (event) => {
      if (themeMenu.open && !themeMenu.contains(event.target)) {
        themeMenu.open = false;
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (themeMenu.open) {
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
  configureUtilities();
  renderRoute({ initial: isInitialRoute });
  isInitialRoute = false;
})().catch(() => {
  const host = document.getElementById("atlas-document");
  const view = document.createElement("article");
  view.className = "route-view load-error-view";
  view.setAttribute("role", "alert");
  const heading = document.createElement("h1");
  heading.className = "page-title";
  heading.textContent = "The atlas could not be loaded";
  const note = document.createElement("p");
  note.className = "page-lede";
  note.textContent = "Its catalogue is temporarily unavailable. No missing information has been interpreted as zero.";
  const retry = document.createElement("button");
  retry.className = "primary-action";
  retry.type = "button";
  retry.textContent = "Retry";
  retry.addEventListener("click", () => window.location.reload());
  view.append(heading, note, retry);
  host?.replaceChildren(view);
});
