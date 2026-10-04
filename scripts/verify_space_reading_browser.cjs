/* Table-first reading and coefficient-qualified ring contract. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const path = require('node:path');

(async () => {
  const target = process.argv[2] || 'dist/atlas.html';
  const base = /^https?:/.test(target) ? target : pathToFileURL(path.resolve(target)).href;
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const errors = [];
  try {
    const page = await browser.newPage({viewport: {width: 1100, height: 900}, reducedMotion: 'reduce'});
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    await page.goto(base);
    const catalogue = await page.evaluate(async () => {
      const atlas = await window.HomologyAtlasDataStore.loadAtlas();
      await Promise.all(atlas.conceptual_spaces.map(space => window.HomologyAtlasDataStore.loadSpace(space)));
      return {
        historicalScope: atlas.snapshot.scope_note,
        spaces: atlas.conceptual_spaces.map(space => ({
          id: space.id,
          slug: space.slug,
          cohomology: (space.cohomology || []).map(record => ({
            coefficient: record.coefficient,
            provenance: record.provenance?.kind,
            presentation: record.presentation,
            generators: record.algebra?.generators || [],
            basisCount: record.algebra?.basis?.length || 0,
          })),
        })),
      };
    });
    const {spaces} = catalogue;
    const bySlug = new Map(spaces.map(space => [space.slug, space]));
    assert.equal(spaces.length, 194);

    async function openSpace(slug) {
      const space = bySlug.get(slug);
      assert.ok(space, `Retained route ${slug}`);
      await page.goto(base + '#space=' + slug);
      await page.locator(`.canonical-space-page[data-space-id="${space.id}"]`).waitFor();
      return space;
    }

    function preferredRecord(space, coefficient) {
      const records = space.cohomology.filter(record => record.coefficient === coefficient);
      return records.find(record => record.provenance === 'literature')
        || records.find(record => record.presentation?.tex)
        || records[0];
    }

    async function assertVisibleRing(space, coefficient) {
      const record = preferredRecord(space, coefficient);
      assert.ok(record, `${space.id}: ${coefficient} record exists`);
      const formula = page.locator('.canonical-ring-formula');
      assert.ok(await formula.isVisible(), `${space.id}: ring formula visible without disclosure`);
      assert.equal(await formula.evaluate(node => node.closest('details') === null), true);
      if (record.presentation?.tex) {
        assert.ok((await formula.locator('[data-tex]').evaluateAll(nodes => nodes.map(node => node.dataset.tex)))
          .includes('\\cong ' + record.presentation.tex), `${space.id}: original ${coefficient} presentation preserved`);
      }
      if (record.generators.length) {
        const degrees = page.locator('.canonical-generator-degrees');
        assert.ok(await degrees.isVisible(), `${space.id}: generator degrees visible`);
        assert.equal(await degrees.evaluate(node => node.closest('details') === null), true);
        const text = await degrees.innerText();
        for (const generator of record.generators) {
          assert.match(text, new RegExp(`\\b${generator.degree}\\b`), `${space.id}: degree ${generator.degree}`);
        }
      }
      return record;
    }

    async function openProducts(record) {
      const products = page.locator('.canonical-ring details.classical-products');
      assert.equal(await products.count(), 1, 'One nearby cup-product disclosure');
      assert.equal(await products.locator('details').count(), 0, 'No nested disclosure before the product table');
      await products.locator('summary').click();
      await products.locator('table.wb-multiplication').waitFor();
      assert.equal(await products.locator('table.wb-multiplication > tbody > tr').count(), record.basisCount);
      assert.equal(await page.locator('.canonical-ring table.wb-multiplication').count(), 1);
    }

    for (const space of spaces) {
      await openSpace(space.slug);
      assert.equal(await page.locator('.canonical-theory-table').count(), 2, space.id);
      assert.equal(await page.locator('.canonical-theory-table table').count(), 2, space.id);
      assert.equal(await page.locator('section.canonical-ring > h2').innerText(), 'Cohomology ring', space.id);
      assert.equal(await page.locator('.canonical-detail').count(), 1, space.id);
      assert.equal(await page.locator('.canonical-detail[open]').count(), 0, space.id);
      assert.equal(await page.locator('.canonical-invariants > .detail-section[open]').count(), 0, space.id);
      assert.equal(await page.locator('.canonical-ring table.wb-multiplication').count(), 0,
        `${space.id}: product tables are lazy`);
    }

    for (const [slug, coefficient] of [
      ['point', 'Q'], ['real-projective-space-2', 'F2'], ['klein-bottle', 'F2'],
      ['four-manifold-k3', 'Z'], ['orientable-surface-26', 'Q'],
    ]) {
      await openSpace(slug);
      await page.locator('.canonical-select').first().selectOption(coefficient);
      assert.match(page.url(), new RegExp('coefficient=' + coefficient));
      await page.locator('.canonical-invariants > .detail-section > summary').click();
      await page.locator('.canonical-provenance > summary').click();
      assert.equal(await page.locator('.canonical-detail[open]').count(), 1);
      assert.equal(await page.locator('.canonical-invariants > .detail-section[open]').count(), 1);
    }

    // Source formulas, degrees and tables must follow the selected coefficient together.
    const lens = await openSpace('lens-5-3-1-2');
    const lensBasisSizes = [];
    for (const coefficient of ['F5', 'F2', 'Z']) {
      await page.locator('.canonical-select').first().selectOption(coefficient);
      const record = await assertVisibleRing(lens, coefficient);
      const convention = page.locator('.canonical-ring-content .ring-algebra-convention');
      assert.ok(await convention.isVisible(), `${coefficient}: algebra convention is visible`);
      const conventionText = await convention.innerText();
      assert.match(conventionText, /graded.commutative/i);
      if (coefficient === 'F5') {
        assert.match(conventionText, /odd.degree/i);
        assert.match(conventionText, /zero|vanish/i);
      } else if (coefficient === 'F2') {
        assert.match(conventionText, /characteristic\s*2/i);
        assert.match(conventionText, /not|do not|does not/i);
      } else {
        assert.equal(await convention.locator('[data-tex="2x^2=0"]').count(), 1,
          'Integral odd squares are constrained by 2x² = 0');
        assert.match(conventionText, /not|do not|does not/i);
      }
      assert.equal(await page.locator('.canonical-ring table.wb-multiplication').count(), 0,
        `${coefficient}: switching discards the old product table`);
      await openProducts(record);
      lensBasisSizes.push(record.basisCount);
      await page.getByText('Generators, relations & full record', {exact: true}).click();
      await page.locator('.canonical-ring .cohomology-rendered').waitFor();
      assert.equal(await page.locator('.canonical-ring details.classical-products').count(), 1,
        `${coefficient}: full record does not duplicate the product disclosure`);
      assert.equal(await page.locator('.canonical-ring table.wb-multiplication').count(), 1,
        `${coefficient}: full record does not duplicate the product table`);
      assert.ok(await page.locator('.canonical-ring .cohomology-sources .citation-list > li').count());
    }
    assert.ok(new Set(lensBasisSizes).size > 1, 'The coefficient-switch check exercises distinct basis sizes');

    const cp2 = await openSpace('complex-projective-space-2');
    await page.locator('.canonical-select').first().selectOption('Q');
    await assertVisibleRing(cp2, 'Q');
    await page.getByText('Why ring structure matters', {exact: true}).click();
    assert.match(await page.locator('.canonical-ring').innerText(), /cup products differ/);
    await page.locator('.canonical-provenance > summary').click();
    assert.ok(await page.locator('.canonical-provenance .citation-list > li').count() > 3);
    assert.equal(await page.getByText('What to notice', {exact: true}).count(), 1);

    const k3 = await openSpace('four-manifold-k3');
    await page.locator('.canonical-select').first().selectOption('Z');
    await openProducts(await assertVisibleRing(k3, 'Z'));
    assert.equal(await page.locator('.canonical-ring .cohomology-rendered').count(), 0,
      'K3 product table is reachable without its long full record');

    const zeroSphere = await openSpace('sphere-0');
    await page.locator('.canonical-select').first().selectOption('Q');
    await assertVisibleRing(zeroSphere, 'Q');
    assert.match(await page.locator('.canonical-ring').innerText(), /computed ring output is withheld/);
    assert.match(await page.locator('.canonical-ring').innerText(), /literature-based ring information remains available/);
    assert.equal(await page.locator('.canonical-theory-table').nth(1)
      .locator('tbody tr').first().locator('[role="math"]').getAttribute('data-tex'), '\\mathbb{Q}^{\\oplus 2}');

    await openSpace('orientable-surface-26');
    await page.locator('.canonical-select').first().selectOption('Q');
    assert.match(await page.locator('.canonical-ring').innerText(), /No cohomology ring is recorded/);
    assert.match(await page.locator('.canonical-ring').innerText(), /not a zero-ring assertion/);
    assert.equal(await page.locator('.canonical-ring details.classical-products').count(), 0);
    assert.match(await page.locator('.canonical-theory-table').nth(1).innerText(), /Not recorded/);

    await openSpace('real-projective-space-2');
    await page.locator('.canonical-select').first().selectOption('Z');
    await page.locator('.canonical-compare').click();
    await page.locator('.canonical-compare-label select').selectOption('F2');
    async function groupTex(theoryIndex, degree, coefficientIndex) {
      const row = page.locator('.canonical-theory-table').nth(theoryIndex).locator('tbody tr')
        .filter({has: page.locator('th.canonical-degree', {hasText: new RegExp(`^${degree}$`)})});
      return row.locator('td').nth(coefficientIndex).locator('[role="math"]').getAttribute('data-tex');
    }
    assert.equal(await groupTex(0, 1, 0), '\\mathbb{Z}/2\\mathbb{Z}', 'RP2 integral H1 has torsion');
    assert.equal(await groupTex(1, 1, 0), '0', 'RP2 integral H^1 is zero');
    assert.equal(await groupTex(0, 2, 0), '0', 'RP2 integral H2 is zero');
    assert.equal(await groupTex(1, 2, 0), '\\mathbb{Z}/2\\mathbb{Z}', 'RP2 integral H^2 has torsion');
    assert.equal(await groupTex(0, 1, 1), '\\mathbb{F}_{2}');
    assert.equal(await groupTex(1, 1, 1), '\\mathbb{F}_{2}');
    for (const width of [320, 390, 700, 1100]) {
      await page.setViewportSize({width, height: 900});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, `${width}px`);
    }

    await page.goto(base + '#family-lens_space');
    await page.locator('.family-members-section').waitFor();
    const familyLinks = page.locator('.family-members-section .space-result-link');
    const lensOrder = await familyLinks.evaluateAll(links => links.map(link => link.getAttribute('href')));
    assert.deepEqual(lensOrder, [
      'lens-3-3-1-1', 'lens-4-3-1-1', 'lens-5-3-1-1', 'lens-5-3-1-2', 'lens-6-3-1-1',
      'lens-7-3-1-1', 'lens-7-3-1-2', 'lens-8-3-1-1', 'lens-8-3-1-3', 'lens-9-3-1-1',
      'lens-9-3-1-2', 'lens-10-3-1-1', 'lens-10-3-1-3',
    ].map(slug => '#space=' + slug));
    assert.equal(await page.locator('.family-members-section .family-inline-link').count(), 0);
    await page.locator('#search-family-lens_space').fill('L(5,2)');
    assert.equal(await familyLinks.count(), 1, 'Existing exact alias search stays available');
    assert.equal(await familyLinks.first().getAttribute('href'), '#space=lens-5-3-1-2');
    await page.locator('#search-family-lens_space').fill('');
    assert.deepEqual(await familyLinks.evaluateAll(links => links.map(link => link.getAttribute('href'))), lensOrder,
      'Clearing family search restores natural order');

    await page.goto(base + '#about');
    await page.locator('.about-view').waitFor();
    const aboutText = await page.locator('.about-view').innerText();
    assert.match(aboutText, /194\s+(?:recorded\s+)?(?:named\s+)?spaces/i);
    assert.doesNotMatch(aboutText, /Fifty-one named CW spaces/i, 'Historical scope is not the current scope');
    if (catalogue.historicalScope) {
      const historical = page.locator('.about-view details').filter({hasText: catalogue.historicalScope});
      assert.equal(await historical.count(), 1, 'Original snapshot scope remains available');
      assert.equal(await historical.getAttribute('open'), null, 'Historical scope starts collapsed');
      assert.match(await historical.locator('summary').innerText(), /historical|original/i);
    }

    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ok: true, spaces: spaces.length, tableFirst: spaces.length,
      ringConventions: ['F5', 'F2', 'Z'], coefficientRefresh: true, missingAndWithheld: true,
      rp2Comparison: true, naturalFamilyOrder: true, aboutScope: true,
      disclosures: true, widths: [320, 390, 700, 1100], errors}));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
