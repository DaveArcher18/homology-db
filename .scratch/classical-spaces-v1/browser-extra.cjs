const assert = require("node:assert/strict");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");
const fs = require("node:fs");

async function main() {
  const base = pathToFileURL(process.argv[2] || "/tmp/homology-classical-candidate.html").href;
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(base);
    const data = await page.locator("#atlas-data").evaluate((node) => JSON.parse(node.textContent));
    assert.equal(await page.locator(".textbook-space-link").count(), 13);
    assert.equal(await page.locator(".primary-nav #nav-spectra").count(), 0);
    const search = page.locator("#search-home");
    await search.fill("CP²");
    await search.press("ArrowDown");
    assert.match(await page.evaluate(() => document.activeElement.getAttribute("href")), /complex-projective-space-2/);
    await page.keyboard.press("Enter");
    await page.waitForURL("**#space=complex-projective-space-2");
    await page.locator(".cohomology-table").waitFor();
    const cup = page.locator(".cohomology-section").getByRole("button", { name: "Cup product", exact: true });
    assert.equal(await cup.getAttribute("aria-expanded"), "false");
    await cup.click();
    assert.equal(await cup.getAttribute("aria-expanded"), "true");
    const panel = page.locator(`#${await cup.getAttribute("aria-controls")}`);
    assert.equal(await panel.isVisible(), true);
    await cup.press("Enter");
    assert.equal(await panel.isVisible(), false);
    await page.locator('input[name="coefficient-complex-projective-space-2"]:checked').focus();
    await page.keyboard.press("ArrowRight");
    assert.equal(await page.locator('input[name="coefficient-complex-projective-space-2"]:checked').inputValue(), "F2");

    await page.locator('input[name="coefficient-complex-projective-space-2"][value="F3"]').locator("..").click();
    await page.locator(".related-example-link").click();
    await page.waitForURL("**#space=sphere-wedge-2-4");
    assert.equal(await page.locator('input[name="coefficient-sphere-wedge-2-4"]:checked').inputValue(), "Q");
    await page.locator('input[name="coefficient-sphere-wedge-2-4"][value="F2"]').locator("..").click();
    await page.goBack();
    await page.locator('input[name="coefficient-complex-projective-space-2"]').first().waitFor();
    assert.equal(await page.locator('input[name="coefficient-complex-projective-space-2"]:checked').inputValue(), "F3");
    await page.goForward();
    await page.locator('input[name="coefficient-sphere-wedge-2-4"]').first().waitFor();
    assert.equal(await page.locator('input[name="coefficient-sphere-wedge-2-4"]:checked').inputValue(), "F2");

    let fieldViews = 0;
    for (const space of data.conceptual_spaces.filter((item) => item.classical_core)) {
      await page.goto(`${base}#space=${space.slug}`);
      for (const coefficient of data.classical.coefficients) {
        await page.locator(`input[name="coefficient-${space.slug}"][value="${coefficient}"]`).locator("..").click();
        assert.equal(await page.locator(`input[name="coefficient-${space.slug}"]:checked`).inputValue(), coefficient);
        assert.equal(await page.locator(".cohomology-section .math-fallback").count(), 0, `${space.id}/${coefficient}`);
        assert.equal(await page.locator(".cohomology-section .citation-list a").count(), 1);
        fieldViews += 1;
      }
    }
    const noncore = data.conceptual_spaces.find((item) => !item.classical_core);
    await page.goto(`${base}#space=${noncore.slug}`);
    assert.equal(await page.locator(`input[name="coefficient-${noncore.slug}"]:checked`).inputValue(), "Z");
    assert.match(await page.locator(".cohomology-missing").innerText(), /Not recorded/);
    assert.ok(await page.locator(".homology-table tbody tr").count() > 0);

    await page.locator("#snapshot-about > summary").click();
    assert.equal(await page.locator("#nav-spectra").isVisible(), true);
    await page.locator("#nav-spectra").click();
    await page.locator(".spectra-view").waitFor();
    assert.match(await page.locator(".spectra-view").innerText(), /review/i);

    await page.goto(`${base}#home`);
    if (await page.locator("#snapshot-about").getAttribute("open") !== null) await page.locator("#snapshot-about > summary").click();
    await page.locator("#search-home").fill("");
    await page.locator("#search-home").blur();
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: "/tmp/homology-classical-home-extra.png", fullPage: true, animations: "disabled" });
    await page.goto(`${base}#space=complex-projective-space-2`);
    await page.locator('input[name="coefficient-complex-projective-space-2"][value="Q"]').locator("..").click();
    await page.locator(".record-details").getByText("Model & sources", { exact: true }).click();
    const pendingDownload = page.waitForEvent("download");
    await page.getByRole("button", { name: "Download space JSON", exact: true }).click();
    const download = await pendingDownload;
    await download.saveAs("/tmp/homology-classical-cp2.json");
    const record = JSON.parse(fs.readFileSync("/tmp/homology-classical-cp2.json", "utf8"));
    assert.equal(record.id, "complex_projective_space:2");
    assert.equal(record.cohomology.length, 5);
    assert.equal(record.export_context.atlas_schema_version, "homology-db.static-atlas/4");
    assert.ok(record.export_context.source_inputs_sha256);
    assert.ok(record.export_context.classical.sources.hatcher2002.url);
    assert.ok(record.export_context.classical.rational_homology_derivation.source_url);
    await page.locator(".record-details").getByText("Model & sources", { exact: true }).click();
    await page.evaluate(() => { document.activeElement.blur(); window.scrollTo(0, 0); });
    await page.screenshot({ path: "/tmp/homology-classical-cp2-extra.png", fullPage: true, animations: "disabled" });
    await page.setViewportSize({ width: 320, height: 720 });
    await page.screenshot({ path: "/tmp/homology-classical-mobile-extra.png", fullPage: true, animations: "disabled" });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ keyboard_search: "passed", knowl_keyboard: "passed", coefficient_keyboard: "passed", history_and_state: "passed", field_tex_and_sources: fieldViews, noncore: "passed", secondary_spectra: "passed", downloaded_json_context: "passed", errors }));
  } finally {
    await browser.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
