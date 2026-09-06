/* Exact-artifact UI regression. NODE_PATH may point to bundled Playwright. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const path = require('node:path');

async function main() {
  const target=process.argv[2] || 'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.goto(base);
    await page.locator('.workbench-view').waitFor();
    const atlas=await page.locator('#atlas-data').evaluate(n=>JSON.parse(n.textContent));
    assert.equal(atlas.family_rules.rules.length,3);
    let views=0;
    for(const family of ['sphere','real_projective_space','complex_projective_space']) {
      for(const n of ['0','1','2','3','4','13','100000000000000000001']) {
        await page.goto(base+'#workbench?'+new URLSearchParams({family,n,start:'0'}));
        await page.locator('.workbench-view').waitFor();
        await page.waitForFunction(({family,n})=>document.querySelector('.workbench-view')?.dataset.family===family && document.querySelectorAll('.wb-controls input')[0]?.value===n,{family,n});
        assert.equal(await page.locator('.wb-groups').count(),7);
        assert.equal(await page.locator('.wb-groups tbody tr').count(),63);
        assert.match(await page.locator('.wb-review-state').innerText(),/Human review pending/);
        assert.deepEqual(await page.locator('.workbench-view .math-fallback').allTextContents(),[],`${family}/${n}`);
        views++;
      }
    }
    await page.goto(base+'#workbench?family=real_projective_space&n=4&start=0');
    await page.locator('.wb-provenance > summary').click();
    await page.getByRole('button',{name:'Review this result',exact:true}).click();
    const reviewLink=page.getByRole('link',{name:'Open public GitHub review form'});
    const reviewURL=new URL(await reviewLink.getAttribute('href'));
    assert.equal(reviewURL.searchParams.get('template'),'family-review.yml');
    assert.match(reviewURL.searchParams.get('rule-hash'),/^[a-f0-9]{64}$/);
    assert.equal(reviewURL.searchParams.get('rule-id'),'ordinary-real_projective_space');
    assert.ok(reviewURL.href.length<3000);
    const before=await page.locator('.wb-groups tbody tr td:last-child').allTextContents();
    await page.getByLabel('Reduced homology only').check();
    await page.waitForURL(/reduced=1/);
    await page.waitForFunction(()=>document.querySelector('.wb-groups thead').textContent.includes('Reduced'));
    assert.deepEqual(await page.locator('.wb-groups tbody tr td:last-child').allTextContents(),before);
    await page.getByLabel('Dimension parameter n').fill('25');
    await page.getByLabel('First displayed degree').fill('24');
    await page.getByLabel('First displayed degree').press('Enter');
    await page.waitForURL(/n=25.*start=24/);
    assert.match(page.url(),/n=25/);
    assert.match(page.url(),/start=24/);
    await page.reload();
    assert.equal(await page.getByLabel('First displayed degree').inputValue(),'24');
    const productPanel=page.locator('.wb-products').first();
    await productPanel.locator('summary').click();
    await productPanel.getByLabel('First generator index (0-based)').fill('1');
    await productPanel.getByRole('button',{name:'Show generators'}).click();
    assert.equal(await productPanel.locator('.wb-multiplication tbody tr').count(),12);
    assert.match(await productPanel.innerText(),/window|cropped/i);
    await page.locator('.wb-provenance > summary').click();
    const downloadEvent=page.waitForEvent('download');
    await page.getByRole('button',{name:'Download family JSON',exact:true}).click();
    const download=await downloadEvent;
    const payload=JSON.parse(require('node:fs').readFileSync(await download.path(),'utf8'));
    assert.equal(payload.result_convention,'ordinary_unreduced');
    assert.equal(payload.displayed_homology_convention,'reduced');
    assert.equal(payload.rule.content_sha256,reviewURL.searchParams.get('rule-hash'));
    assert.equal(payload.results.length,7);
    assert.ok(Array.isArray(payload.review_history));
    await page.goto(base+'#glossary');
    assert.equal(await page.locator('.glossary-card').count(),12);
    await page.getByLabel('Find a definition').fill('exterior');
    assert.ok(await page.locator('.glossary-card').count()>=1);
    assert.match(await page.locator('.glossary-results').innerText(),/Exterior/);
    assert.equal(await page.locator('.glossary-view .math-fallback').count(),0);
    await page.goto(base+'#space=klein-bottle');
    await page.locator('input[name="coefficient-klein-bottle"][value="F2"]').locator('..').click();
    await page.locator('.cohomology-rendered').getByText('Cup-product table',{exact:true}).click();
    assert.ok((await page.locator('.cohomology-rendered').innerText()).includes('Multiplication'));
    for(const space of atlas.conceptual_spaces) {
      await page.goto(base+'#space='+space.slug);
      assert.equal(await page.locator('.workbench-view,.space-page').count(),1,space.id);
    }
    for(const spectrum of atlas.conceptual_spectra) {
      await page.goto(base+'#spectrum='+spectrum.slug);
      assert.equal(await page.locator('.spectrum-view').getAttribute('data-spectrum-id'),spectrum.id);
    }
    for(const width of [1440,390,320]) {
      await page.setViewportSize({width,height:900});
      for(const hash of ['#home','#spaces','#space=klein-bottle','#space=complex-projective-space-2','#glossary','#spectra','#spectrum=ceta']) {
        await page.goto(base+hash);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${width} ${hash}`);
      }
      await page.goto(base+'#home');
      await page.screenshot({path:`/tmp/homology-family-${width}.png`,fullPage:true});
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,familyViews:views,legacySpaces:atlas.conceptual_spaces.length,spectra:atlas.conceptual_spectra.length,responsiveCases:21,consoleErrors:errors}));
  } finally {await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
