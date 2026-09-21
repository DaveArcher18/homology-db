/* Table-first reading contract for every recorded space. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');

(async()=>{
  const target=process.argv[2]||'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  try {
    const page=await browser.newPage({viewport:{width:1100,height:900},reducedMotion:'reduce'});
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.goto(base);
    const spaces=await page.evaluate(async()=>{
      const atlas=await window.HomologyAtlasDataStore.loadAtlas();
      await Promise.all(atlas.conceptual_spaces.map(space=>window.HomologyAtlasDataStore.loadSpace(space)));
      return atlas.conceptual_spaces.map(space=>({id:space.id,slug:space.slug}));
    });
    assert.equal(spaces.length,194);
    for(const space of spaces){
      await page.goto(base+'#space='+space.slug);
      const view=page.locator('.canonical-space-page');
      await view.waitFor();
      assert.equal(await view.getAttribute('data-space-id'),space.id);
      assert.equal(await page.locator('.canonical-theory-table').count(),2,space.id);
      assert.equal(await page.locator('.canonical-theory-table table').count(),2,space.id);
      assert.equal(await page.locator('.canonical-detail').count(),2,space.id);
      assert.equal(await page.locator('.canonical-detail[open]').count(),0,space.id);
      assert.equal(await page.locator('.canonical-invariants > .detail-section[open]').count(),0,space.id);
    }
    for(const [slug,coefficient] of [
      ['point','Q'],['real-projective-space-2','F2'],['klein-bottle','F2'],
      ['four-manifold-k3','Z'],['orientable-surface-26','Q'],
    ]){
      await page.goto(base+'#space='+slug);
      await page.locator('.canonical-space-page').waitFor();
      await page.locator('.canonical-select').first().selectOption(coefficient);
      assert.match(page.url(),new RegExp('coefficient='+coefficient));
      await page.locator('.canonical-invariants > .detail-section > summary').click();
      await page.locator('.canonical-ring > summary').click();
      await page.locator('.canonical-provenance > summary').click();
      assert.equal(await page.locator('.canonical-detail[open]').count(),2);
      assert.equal(await page.locator('.canonical-invariants > .detail-section[open]').count(),1);
    }
    await page.goto(base+'#space=real-projective-space-2');
    for(const width of [320,390,700,1100]){
      await page.setViewportSize({width,height:900});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${width}px`);
    }
    await page.goto(base+'#space=complex-projective-space-2');
    await page.locator('.canonical-ring > summary').click();
    await page.getByText('Why ring structure matters',{exact:true}).click();
    assert.match(await page.locator('.canonical-ring').innerText(),/cup products differ/);
    await page.locator('.canonical-provenance > summary').click();
    assert.ok(await page.locator('.canonical-provenance .citation-list > li').count()>3);
    assert.equal(await page.getByText('What to notice',{exact:true}).count(),1);
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,spaces:spaces.length,tableFirst:spaces.length,disclosures:true,widths:[320,390,700,1100],errors}));
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
