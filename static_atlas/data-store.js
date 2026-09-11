(() => {
  "use strict";

  const node = document.getElementById("atlas-data");
  const bootstrap = JSON.parse(node.textContent);
  const sharded = bootstrap?.mode === "sharded";
  const cache = new Map();
  let atlasPromise;
  let manifest;

  async function digest(value) {
    if (!window.crypto?.subtle) return null;
    const bytes = new TextEncoder().encode(value);
    const result = await window.crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(result)].map((item) => item.toString(16).padStart(2, "0")).join("");
  }

  async function fetchDocument(path, expectedKind) {
    if (!cache.has(path)) {
      cache.set(path, (async () => {
        const separator = path.includes("?") ? "&" : "?";
        const response = await fetch(`${path}${separator}v=${encodeURIComponent(bootstrap.bundle_id)}`);
        if (!response.ok) throw new Error(`HTTP ${response.status} while loading ${path}`);
        const raw = await response.text();
        const documentValue = JSON.parse(raw);
        if (documentValue.schema_version !== "homology-db.static-bundle-document/1") {
          throw new Error(`Unsupported atlas document schema for ${path}`);
        }
        if (documentValue.bundle_id !== bootstrap.bundle_id) {
          throw new Error(`Atlas release mismatch for ${path}`);
        }
        if (documentValue.document_kind !== expectedKind) {
          throw new Error(`Unexpected atlas document kind for ${path}`);
        }
        if (manifest) {
          const entry = manifest.files.find((item) => item.path === path);
          if (!entry || entry.document_kind !== expectedKind) {
            throw new Error(`Atlas manifest does not inventory ${path}`);
          }
          const actualDigest = await digest(raw);
          if (entry.bytes !== new TextEncoder().encode(raw).byteLength || (actualDigest && entry.sha256 !== actualDigest)) {
            throw new Error(`Atlas file integrity check failed for ${path}`);
          }
          if (documentValue.snapshot_id !== manifest.snapshot_id) {
            throw new Error(`Atlas Snapshot mismatch for ${path}`);
          }
        }
        return documentValue.payload;
      })());
    }
    try {
      return await cache.get(path);
    } catch (error) {
      cache.delete(path);
      throw error;
    }
  }

  async function loadAtlas() {
    if (!sharded) return bootstrap;
    if (!atlasPromise) {
      atlasPromise = (async () => {
        const manifestResponse = await fetch(`${bootstrap.manifest_path}?v=${encodeURIComponent(bootstrap.bundle_id)}`);
        if (!manifestResponse.ok) throw new Error(`HTTP ${manifestResponse.status} while loading atlas manifest`);
        manifest = await manifestResponse.json();
        if (manifest.schema_version !== "homology-db.static-atlas-bundle/1" || manifest.bundle_id !== bootstrap.bundle_id) {
          throw new Error("Atlas manifest does not match the application shell");
        }
        const [catalog, definitions, familyRules, teaching, classical] = await Promise.all([
          fetchDocument("data/catalog.json", "catalog"),
          fetchDocument("data/shared/definitions.json", "definitions"),
          fetchDocument("data/shared/family-rules.json", "family_rules"),
          fetchDocument("data/shared/teaching.json", "teaching"),
          fetchDocument("data/shared/classical.json", "classical"),
        ]);
        return {
          ...catalog,
          definitions,
          family_rules: familyRules,
          teaching,
          classical,
          _bundle_manifest: manifest,
        };
      })();
    }
    return atlasPromise;
  }

  async function loadSubject(record, kind) {
    if (!sharded || record?._loaded) return record;
    if (!record?._document_path) throw new Error("This atlas record has no document path");
    const payload = await fetchDocument(record._document_path, kind);
    const expected = kind === "space" ? record.id : (record.spectrum_id ?? record.id);
    const actual = kind === "space" ? payload.id : (payload.spectrum_id ?? payload.id);
    if (actual !== expected) throw new Error("Loaded atlas record has the wrong stable identity");
    Object.keys(record).forEach((key) => delete record[key]);
    Object.assign(record, payload, { _loaded: true });
    return record;
  }

  window.HomologyAtlasDataStore = Object.freeze({
    sharded,
    loadAtlas,
    loadSpace: (record) => loadSubject(record, "space"),
    loadSpectrum: (record) => loadSubject(record, "spectrum"),
  });
})();
