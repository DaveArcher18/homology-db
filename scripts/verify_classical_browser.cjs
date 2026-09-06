/* Run with Playwright installed (or NODE_PATH pointing to a bundled runtime). */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const { pathToFileURL } = require("node:url");
const path = require("node:path");

async function main() {
  const target = process.argv[2] || path.resolve("dist/atlas.html");
  const base = /^https?:/.test(target) ? target : pathToFileURL(path.resolve(target)).href;
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
    const errors = [];
    const choose = async (selector) => {
      const input = page.locator(selector);
      await input.locator("..").click();
      assert.equal(await input.isChecked(), true);
    };
    page.on("pageerror", error => errors.push(error.message));
    page.on("console", message => {
      if (message.type() === "error") errors.push(message.text());
    });
    await page.goto(base);
    const atlas = await page.locator("#atlas-data").evaluate(node => JSON.parse(node.textContent));
    assert.equal(atlas.classical.record_count, 65);
    const core = atlas.conceptual_spaces.filter(space => space.classical_core);
    assert.equal(core.length, 13);
    await page.screenshot({ path: "/tmp/homology-classical-home.png", fullPage: true, animations: "disabled" });

    for (const space of core) {
      await page.goto(`${base}#space=${space.slug}`);
      await page.locator(".cohomology-rendered").waitFor();
      assert.equal(await page.locator(`input[name="coefficient-${space.slug}"]:checked`).inputValue(), "Q");
      for (const coefficient of atlas.classical.coefficients) {
        await choose(`input[name="coefficient-${space.slug}"][value="${coefficient}"]`);
        assert.equal(await page.locator(".cohomology-missing").count(), 0, `${space.id}/${coefficient}`);
        const rows = await page.locator(".cohomology-table tbody tr").count();
        const record = space.cohomology.find(item => item.coefficient === coefficient);
        assert.equal(rows, record.groups.length);
        assert.ok((await page.locator(".cohomology-sources").innerText()).includes("human mathematical review pending"));
        const before = await page.locator(".cohomology-rendered").innerText();
        await choose(`input[name="convention-${space.slug}"][value="true"]`);
        assert.equal(await page.locator(".cohomology-rendered").innerText(), before);
        await choose(`input[name="convention-${space.slug}"][value="false"]`);
      }
      await choose(`input[name="coefficient-${space.slug}"][value="Z"]`);
      assert.match(await page.locator(".cohomology-missing").innerText(), /Not recorded/);
      assert.ok(await page.locator(".homology-dynamic tbody tr").count() > 0);
    }

    for (const space of atlas.conceptual_spaces) {
      await page.goto(`${base}#space=${space.slug}`);
      assert.equal(await page.locator(".space-page").getAttribute("data-space-id"), space.id);
    }
    for (const spectrum of atlas.conceptual_spectra) {
      await page.goto(`${base}#spectrum=${spectrum.slug}`);
      assert.equal(await page.locator(".spectrum-view").getAttribute("data-spectrum-id"), spectrum.id);
    }

    for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }, { width: 320, height: 720 }]) {
      await page.setViewportSize(viewport);
      for (const hash of ["#home", "#spaces", "#space=complex-projective-space-2", "#space=sphere-0", "#space=klein-bottle", "#spectra", "#spectrum=ceta"]) {
        await page.goto(`${base}${hash}`);
        await page.locator(".route-view").waitFor();
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
        assert.equal(overflow, false, `${viewport.width}px ${hash}`);
      }
    }
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(`${base}#space=complex-projective-space-2`);
    await choose('input[value="F2"][name^="coefficient-"]');
    await page.screenshot({ path: "/tmp/homology-classical-cp2.png", fullPage: true, animations: "disabled" });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: "/tmp/homology-classical-mobile.png", fullPage: true, animations: "disabled" });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ spaces: core.length, field_views: 65, integral_missing_views: 13,
      reduced_isolation: 65, space_routes: atlas.conceptual_spaces.length,
      spectrum_routes: atlas.conceptual_spectra.length, responsive_routes: 21, errors, screenshots: [
        "/tmp/homology-classical-home.png", "/tmp/homology-classical-cp2.png", "/tmp/homology-classical-mobile.png"
      ] }, null, 2));
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
