/* Entry-point and canonical-space routing regression. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');

(async()=>{
  const target=process.argv[2]||'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const output=process.argv[3]||'/tmp';
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.goto(base);
    await page.locator('.home-view').waitFor();
    assert.equal(await page.locator('main h1').innerText(),'Homology Atlas');
    assert.equal(await page.locator('#nav-home').innerText(),'Home');
    assert.equal(await page.locator('#nav-spaces').innerText(),'Spaces');
    assert.deepEqual(await page.locator('.primary-nav a').allTextContents(),['Home','Spaces','Glossary','About']);
    assert.match(await page.locator('.home-view').innerText(),/homology and cohomology[\s\S]*Compare coefficients[\s\S]*computations, references, and review provenance[\s\S]*194 computed-space records[\s\S]*withheld/i);
    const primaryBrowse=page.locator('main a.primary-action',{hasText:'Browse spaces'});
    assert.equal(await primaryBrowse.getAttribute('href'),'#spaces');
    await page.screenshot({path:path.join(output,'homology-atlas-home.png'),fullPage:true,animations:'disabled'});

    await primaryBrowse.click();
    await page.locator('.spaces-view').waitFor();
    assert.match(await page.locator('.page-header').innerText(),/194 spaces/i);
    await page.screenshot({path:path.join(output,'homology-atlas-spaces.png'),fullPage:true,animations:'disabled'});

    const atlas=await page.evaluate(()=>window.HomologyAtlasDataStore.loadAtlas());
    assert.equal(atlas.conceptual_spaces.length,194);
    const ids=['sphere:0','real_projective_space:4','complex_projective_space:2','torus:2','four_manifold:k3'];
    for(const id of ids){
      const space=atlas.conceptual_spaces.find(item=>item.id===id);
      assert.ok(space,id);
      const route=base+'#space='+space.slug;
      await page.goto(route);
      await page.locator(`.canonical-space-page[data-space-id="${id}"]`).waitFor();
      assert.equal(await page.locator('.workbench-view').count(),0,id);
      await page.reload();
      await page.locator(`.canonical-space-page[data-space-id="${id}"]`).waitFor();
      assert.equal(page.url(),route,id);
    }
    await page.goto(base+'#space=sphere-0');
    await page.locator('.canonical-ring > summary').click();
    const s0=await page.locator('.canonical-ring').innerText();
    assert.match(s0,/imported computed ring output[\s\S]*withheld[\s\S]*does not mean the ring is zero/i);
    assert.match(s0,/separately sourced literature-based ring information[\s\S]*not presented as a computed result/i);
    await page.screenshot({path:path.join(output,'homology-atlas-s0.png'),fullPage:true,animations:'disabled'});
    await page.goto(base+'#space=real-projective-space-4');
    await page.locator('.space-page').waitFor();
    await page.screenshot({path:path.join(output,'homology-atlas-rp4.png'),fullPage:true,animations:'disabled'});

    await page.locator('#site-brand').click();
    await page.locator('.home-view').waitFor();
    assert.match(page.url(),/#home$/);
    await page.goto(base+'#workbench?family=real_projective_space&n=4&start=0');
    await page.locator('.workbench-view').waitFor();
    assert.equal(await page.locator('#nav-home').getAttribute('aria-current'),null);
    await page.locator('#nav-home').click();
    await page.locator('.home-view').waitFor();
    assert.match(page.url(),/#home$/);

    for(const width of [1440,390,320]){
      await page.setViewportSize({width,height:900});
      for(const hash of ['#home','#spaces','#space=sphere-0','#space=real-projective-space-4']){
        await page.goto(base+hash);
        await page.locator('.route-view').waitFor();
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${width} ${hash}`);
      }
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,spaces:194,canonicalRoutes:ids.length,reloads:ids.length,widths:[1440,390,320],errors,screenshots:['homology-atlas-home.png','homology-atlas-spaces.png','homology-atlas-s0.png','homology-atlas-rp4.png']},null,2));
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
